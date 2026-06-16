from __future__ import annotations

import json
import random
import threading
import zipfile
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import classify
from .db import ROOT_DIR, connect, dumps, init_db, loads, utcnow
from .extraction import (
    DEFAULT_SOURCE_DIR,
    build_export_payload,
    discover_source_groups,
    parse_exam_sources,
    safe_extract_zip_member,
    slugify,
)


app = FastAPI(title="POSCOMP Web")
templates = Jinja2Templates(directory=str(ROOT_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "static")), name="static")
app.mount("/images", StaticFiles(directory=str(ROOT_DIR / "var" / "images")), name="images")


@app.on_event("startup")
def startup() -> None:
    init_db()
    for directory in ["uploads", "images", "exports"]:
        (ROOT_DIR / "var" / directory).mkdir(parents=True, exist_ok=True)


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303)


def get_exam_or_404(exam_id: int) -> dict:
    with connect() as conn:
        row = conn.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Prova não encontrada")
    return dict(row)


def import_group(group, source_kind: str = "local") -> int:
    now = utcnow()
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO exams (year, title, variant, status, source_kind, source_paths, answer_key_path, created_at, updated_at)
            VALUES (?, ?, ?, 'draft', ?, ?, ?, ?, ?)
            """,
            (
                group.year,
                group.title,
                group.variant,
                source_kind,
                dumps([str(path) for path in group.exam_paths]),
                str(group.answer_path or ""),
                now,
                now,
            ),
        )
        exam_id = int(cursor.lastrowid)

    image_dir = ROOT_DIR / "var" / "images" / f"exam_{exam_id}"
    parsed = parse_exam_sources(
        group.exam_paths,
        group.answer_path,
        year=group.year,
        variant=group.variant,
        image_dir=image_dir,
    )

    with connect() as conn:
        conn.execute("DELETE FROM questions WHERE exam_id = ?", (exam_id,))
        for question in parsed.questions:
            conn.execute(
                """
                INSERT INTO questions (
                    exam_id, number, page, statement,
                    alternative_a, alternative_b, alternative_c, alternative_d, alternative_e,
                    extracted_answer, correct_answer, answer_confidence, raw_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exam_id,
                    question.number,
                    question.page,
                    question.statement,
                    question.alternatives.get("A", ""),
                    question.alternatives.get("B", ""),
                    question.alternatives.get("C", ""),
                    question.alternatives.get("D", ""),
                    question.alternatives.get("E", ""),
                    question.extracted_answer,
                    question.extracted_answer,
                    question.answer_confidence,
                    question.raw_text,
                    now,
                    now,
                ),
            )
        rows = conn.execute("SELECT id, number FROM questions WHERE exam_id = ?", (exam_id,)).fetchall()
        question_ids = {int(row["number"]): int(row["id"]) for row in rows}
        for image in parsed.images:
            question_id = question_ids.get(image.question_number)
            if not question_id:
                continue
            conn.execute(
                """
                INSERT INTO question_images (question_id, filename, source_page, label, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (question_id, f"exam_{exam_id}/{image.filename}", image.source_page, image.label, now),
            )
        conn.execute(
            "UPDATE exams SET extraction_notes = ?, updated_at = ? WHERE id = ?",
            ("\n".join(parsed.notes), utcnow(), exam_id),
        )
    return exam_id


@app.get("/", response_class=HTMLResponse)
def public_home(request: Request) -> HTMLResponse:
    with connect() as conn:
        exams = conn.execute(
            """
            SELECT e.*, COUNT(q.id) AS question_count
            FROM exams e
            LEFT JOIN questions q ON q.exam_id = e.id
            WHERE e.status = 'published'
            GROUP BY e.id
            ORDER BY e.year DESC, e.title
            """
        ).fetchall()
        years = [
            row["year"]
            for row in conn.execute(
                "SELECT DISTINCT year FROM exams WHERE status = 'published' ORDER BY year DESC"
            ).fetchall()
        ]
    return templates.TemplateResponse(request, "public/home.html", {"exams": exams, "sim_years": years})


@app.get("/temas", response_class=HTMLResponse)
def public_topics(request: Request) -> HTMLResponse:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT q.area, q.topic, COUNT(*) AS question_count
            FROM questions q
            JOIN exams e ON e.id = q.exam_id
            WHERE e.status = 'published' AND q.topic != ''
            GROUP BY q.area, q.topic
            ORDER BY q.area, question_count DESC, q.topic
            """
        ).fetchall()
    areas: dict[str, list] = {}
    for row in rows:
        areas.setdefault(row["area"] or "Sem área", []).append(row)
    # Áreas ordenadas pelo total de questões (bloco com mais questões primeiro).
    areas = dict(sorted(areas.items(), key=lambda kv: sum(r["question_count"] for r in kv[1]), reverse=True))
    return templates.TemplateResponse(request, "public/topics.html", {"areas": areas})


@app.get("/temas/{topic}", response_class=HTMLResponse)
def public_topic(request: Request, topic: str) -> HTMLResponse:
    with connect() as conn:
        questions = conn.execute(
            """
            SELECT q.number, q.subtopic, e.id AS exam_id, e.title AS exam_title, e.year
            FROM questions q
            JOIN exams e ON e.id = q.exam_id
            WHERE e.status = 'published' AND q.topic = ?
            ORDER BY e.year DESC, e.title, q.number
            """,
            (topic,),
        ).fetchall()
    return templates.TemplateResponse(request, "public/topic.html", {"topic": topic, "questions": questions})


@app.get("/subtemas", response_class=HTMLResponse)
def public_subtopics(request: Request) -> HTMLResponse:
    """Visão de estatística por subtema: quantas questões cada subtópico tem,
    agrupado por área → tema, filtrável por ano. Clicar abre as questões."""
    years = [y for y in request.query_params.getlist("years") if y]
    with connect() as conn:
        all_years = [
            row["year"]
            for row in conn.execute("SELECT DISTINCT year FROM exams WHERE status = 'published' ORDER BY year DESC").fetchall()
        ]
        sql = (
            "SELECT q.area, q.topic, q.subtopic, COUNT(*) AS question_count "
            "FROM questions q JOIN exams e ON e.id = q.exam_id "
            "WHERE e.status = 'published' AND q.subtopic != ''"
        )
        params: list = []
        if years:
            sql += " AND e.year IN (%s)" % ",".join("?" for _ in years)
            params += years
        sql += " GROUP BY q.area, q.topic, q.subtopic ORDER BY q.area, q.topic, question_count DESC, q.subtopic"
        rows = conn.execute(sql, params).fetchall()
    areas: dict[str, dict[str, list]] = {}
    for row in rows:
        areas.setdefault(row["area"] or "Sem área", {}).setdefault(row["topic"] or "Sem tema", []).append(row)
    year_qs = "&".join(f"years={y}" for y in years)
    return templates.TemplateResponse(
        request,
        "public/subtopics.html",
        {"areas": areas, "all_years": all_years, "selected_years": years, "year_qs": year_qs},
    )


@app.get("/subtemas/{subtopic}", response_class=HTMLResponse)
def public_subtopic(request: Request, subtopic: str) -> HTMLResponse:
    years = [y for y in request.query_params.getlist("years") if y]
    with connect() as conn:
        sql = (
            "SELECT q.number, q.topic, q.area, e.id AS exam_id, e.title AS exam_title, e.year "
            "FROM questions q JOIN exams e ON e.id = q.exam_id "
            "WHERE e.status = 'published' AND q.subtopic = ?"
        )
        params: list = [subtopic]
        if years:
            sql += " AND e.year IN (%s)" % ",".join("?" for _ in years)
            params += years
        sql += " ORDER BY e.year DESC, e.title, q.number"
        questions = conn.execute(sql, params).fetchall()
    year_qs = "&".join(f"years={y}" for y in years)
    return templates.TemplateResponse(
        request,
        "public/subtopic.html",
        {"subtopic": subtopic, "questions": questions, "selected_years": years, "year_qs": year_qs},
    )


def _mark_status(marked: str, correct: str) -> str:
    """Estado salvo de uma questão para colorir a grade: 'ok' (acertou),
    'bad' (errou) ou '' (não marcada). Anulada conta como acerto se marcada."""
    if not marked:
        return ""
    if correct == "ANULADA" or marked == correct:
        return "ok"
    return "bad"


def _grid_items(rows) -> list[dict]:
    return [
        {"number": row["number"], "status": _mark_status(row["marked_answer"], row["correct_answer"])}
        for row in rows
    ]


@app.get("/exams/{exam_id}", response_class=HTMLResponse)
def take_exam(request: Request, exam_id: int, q: int = 1, selected: str = "", checked: str = "") -> HTMLResponse:
    exam = get_exam_or_404(exam_id)
    if exam["status"] != "published":
        raise HTTPException(404, "Prova não publicada")
    with connect() as conn:
        grid = conn.execute(
            "SELECT number, marked_answer, correct_answer FROM questions WHERE exam_id = ? ORDER BY number",
            (exam_id,),
        ).fetchall()
        question = conn.execute(
            "SELECT * FROM questions WHERE exam_id = ? AND number = ?", (exam_id, q),
        ).fetchone()
        if not question:
            question = conn.execute(
                "SELECT * FROM questions WHERE exam_id = ? ORDER BY number LIMIT 1", (exam_id,),
            ).fetchone()
        images = []
        if question:
            images = conn.execute("SELECT * FROM question_images WHERE question_id = ? ORDER BY label DESC, id", (question["id"],)).fetchall()
    original_images = [image for image in images if image["label"] == "original"]
    extra_images = [image for image in images if image["label"] != "original"]
    # Sem querystring, mostra o que já está salvo no banco para esta questão.
    saved = question["marked_answer"] if question else ""
    selected = selected or saved
    return templates.TemplateResponse(
        request,
        "public/exam.html",
        {
            "exam": exam,
            "questions": _grid_items(grid),
            "question": question,
            "images": images,
            "original_images": original_images,
            "extra_images": extra_images,
            "selected": selected,
            "checked": checked == "1" or bool(saved),
        },
    )


@app.post("/exams/{exam_id}/answer")
def answer_question(exam_id: int, number: Annotated[int, Form()], selected: Annotated[str, Form()] = "") -> RedirectResponse:
    with connect() as conn:
        conn.execute(
            "UPDATE questions SET marked_answer = ?, updated_at = ? WHERE exam_id = ? AND number = ?",
            (selected.strip().upper(), utcnow(), exam_id, number),
        )
    return redirect(f"/exams/{exam_id}?q={number}&selected={selected}&checked=1")


@app.post("/exams/{exam_id}/clear")
def clear_exam_answers(exam_id: int) -> RedirectResponse:
    with connect() as conn:
        conn.execute("UPDATE questions SET marked_answer = '' WHERE exam_id = ?", (exam_id,))
    return redirect(f"/exams/{exam_id}")


@app.get("/exams/{exam_id}/gabarito")
def exam_answer_key(exam_id: int) -> FileResponse:
    """Serve o PDF do gabarito oficial da prova, para conferência lado a lado."""
    exam = get_exam_or_404(exam_id)
    if exam["status"] != "published":
        raise HTTPException(404, "Prova não publicada")
    path = Path(exam["answer_key_path"] or "")
    if not exam["answer_key_path"] or not path.exists():
        raise HTTPException(404, "Gabarito não disponível")
    return FileResponse(path, media_type="application/pdf", content_disposition_type="inline")


@app.get("/exams/{exam_id}/caderno")
def exam_booklet(exam_id: int) -> FileResponse:
    """Serve o PDF do caderno da prova inline, para o painel lateral mostrar a
    prova inteira (contorna eventuais erros de recorte por questão)."""
    exam = get_exam_or_404(exam_id)
    if exam["status"] != "published":
        raise HTTPException(404, "Prova não publicada")
    paths = [Path(p) for p in loads(exam["source_paths"], []) if p]
    paths = [p for p in paths if p.exists()]
    if not paths:
        raise HTTPException(404, "Caderno não disponível")
    return FileResponse(paths[0], media_type="application/pdf", content_disposition_type="inline")


# Gerador de simulado: replica a proporção do POSCOMP (70 questões → 20/30/20)
# para o total pedido, garantindo um mínimo por área. Sorteia de provas publicadas
# já classificadas, restrito aos anos escolhidos.
AREA_WEIGHTS = {
    "Matemática": 20,
    "Fundamentos da Computação": 30,
    "Tecnologia de Computação": 20,
}


def _area_counts(total: int) -> dict[str, int]:
    """Divide ``total`` entre as 3 áreas na proporção do POSCOMP: cada área recebe
    ``total * peso / 70`` (Matemática 20/70, Fundamentos 30/70, Tecnologia 20/70).
    Arredonda por maior resto para somar exatamente ``total``."""
    areas = list(AREA_WEIGHTS)
    weight_sum = sum(AREA_WEIGHTS.values())  # 70
    raw = {area: total * AREA_WEIGHTS[area] / weight_sum for area in areas}
    counts = {area: int(raw[area]) for area in areas}
    leftover = total - sum(counts.values())
    for area in sorted(areas, key=lambda a: raw[a] - int(raw[a]), reverse=True):
        if leftover <= 0:
            break
        counts[area] += 1
        leftover -= 1
    return counts


def _generate_simulado(total: int, years: list[str]) -> int:
    counts = _area_counts(total)
    picked: list[int] = []
    with connect() as conn:
        year_filter = ""
        params_year: list = []
        if years:
            placeholders = ",".join("?" for _ in years)
            year_filter = f" AND e.year IN ({placeholders})"
            params_year = list(years)
        for area, wanted in counts.items():
            if wanted <= 0:
                continue
            rows = conn.execute(
                "SELECT q.id FROM questions q JOIN exams e ON e.id = q.exam_id "
                "WHERE e.status = 'published' AND q.area = ? "
                "AND q.correct_answer NOT IN ('', 'ANULADA')" + year_filter + " "
                "ORDER BY RANDOM() LIMIT ?",
                [area, *params_year, wanted],
            ).fetchall()
            picked.extend(int(row["id"]) for row in rows)
        if not picked:
            raise HTTPException(400, "Sem questões classificadas suficientes para gerar o simulado.")
        random.shuffle(picked)
        now = utcnow()
        cursor = conn.execute(
            "INSERT INTO simulados (total, created_at) VALUES (?, ?)", (len(picked), now)
        )
        simulado_id = int(cursor.lastrowid)
        for position, question_id in enumerate(picked, start=1):
            conn.execute(
                "INSERT INTO simulado_questions (simulado_id, position, question_id) VALUES (?, ?, ?)",
                (simulado_id, position, question_id),
            )
    return simulado_id


@app.post("/simulado")
def create_simulado(
    total: Annotated[int, Form()] = 10,
    years: Annotated[list[str], Form()] = [],
) -> RedirectResponse:
    simulado_id = _generate_simulado(max(1, total), [y for y in years if y])
    return redirect(f"/simulado/{simulado_id}?q=1")


@app.get("/simulado/{simulado_id}", response_class=HTMLResponse)
def take_simulado(request: Request, simulado_id: int, q: int = 1, selected: str = "", checked: str = "") -> HTMLResponse:
    with connect() as conn:
        sim = conn.execute("SELECT * FROM simulados WHERE id = ?", (simulado_id,)).fetchone()
        if not sim:
            raise HTTPException(404, "Simulado não encontrado")
        positions = conn.execute(
            "SELECT sq.position, q.marked_answer, q.correct_answer "
            "FROM simulado_questions sq JOIN questions q ON q.id = sq.question_id "
            "WHERE sq.simulado_id = ? ORDER BY sq.position",
            (simulado_id,),
        ).fetchall()
        row = conn.execute(
            "SELECT sq.position, q.*, e.year AS exam_year, e.title AS exam_title "
            "FROM simulado_questions sq JOIN questions q ON q.id = sq.question_id "
            "JOIN exams e ON e.id = q.exam_id WHERE sq.simulado_id = ? AND sq.position = ?",
            (simulado_id, q),
        ).fetchone()
        if not row:
            row = conn.execute(
                "SELECT sq.position, q.*, e.year AS exam_year, e.title AS exam_title "
                "FROM simulado_questions sq JOIN questions q ON q.id = sq.question_id "
                "JOIN exams e ON e.id = q.exam_id WHERE sq.simulado_id = ? ORDER BY sq.position LIMIT 1",
                (simulado_id,),
            ).fetchone()
        images = []
        question = None
        origin = ""
        caderno_url = ""
        pdf_page = ""
        if row:
            question = dict(row)
            # Origem: de qual prova/ano e qual o número original da questão.
            origin = f"{row['exam_title']} · Questão {row['number']}"
            caderno_url = f"/exams/{row['exam_id']}/caderno"
            pdf_page = row["page"]
            question["number"] = row["position"]  # grid e navegação usam a posição
            images = conn.execute(
                "SELECT * FROM question_images WHERE question_id = ? ORDER BY label DESC, id", (row["id"],)
            ).fetchall()
    questions = [
        {"number": item["position"], "status": _mark_status(item["marked_answer"], item["correct_answer"])}
        for item in positions
    ]
    original_images = [image for image in images if image["label"] == "original"]
    extra_images = [image for image in images if image["label"] != "original"]
    saved = question["marked_answer"] if question else ""
    selected = selected or saved
    return templates.TemplateResponse(
        request,
        "public/simulado.html",
        {
            "sim": sim,
            "questions": questions,
            "question": question,
            "images": images,
            "original_images": original_images,
            "extra_images": extra_images,
            "selected": selected,
            "checked": checked == "1" or bool(saved),
            "origin": origin,
            "caderno_url": caderno_url,
            "pdf_page": pdf_page,
        },
    )


@app.post("/simulado/{simulado_id}/answer")
def answer_simulado(simulado_id: int, number: Annotated[int, Form()], selected: Annotated[str, Form()] = "") -> RedirectResponse:
    with connect() as conn:
        conn.execute(
            "UPDATE questions SET marked_answer = ?, updated_at = ? WHERE id = ("
            "SELECT question_id FROM simulado_questions WHERE simulado_id = ? AND position = ?)",
            (selected.strip().upper(), utcnow(), simulado_id, number),
        )
    return redirect(f"/simulado/{simulado_id}?q={number}&selected={selected}&checked=1")


@app.post("/simulado/{simulado_id}/clear")
def clear_simulado_answers(simulado_id: int) -> RedirectResponse:
    with connect() as conn:
        conn.execute(
            "UPDATE questions SET marked_answer = '' WHERE id IN ("
            "SELECT question_id FROM simulado_questions WHERE simulado_id = ?)",
            (simulado_id,),
        )
    return redirect(f"/simulado/{simulado_id}")


@app.get("/simulados", response_class=HTMLResponse)
def list_simulados(request: Request) -> HTMLResponse:
    with connect() as conn:
        simulados = conn.execute(
            "SELECT s.id, s.total, s.created_at, COUNT(sq.question_id) AS question_count "
            "FROM simulados s LEFT JOIN simulado_questions sq ON sq.simulado_id = s.id "
            "GROUP BY s.id ORDER BY s.created_at DESC, s.id DESC"
        ).fetchall()
    return templates.TemplateResponse(request, "public/simulados.html", {"simulados": simulados})


@app.post("/simulado/{simulado_id}/delete")
def delete_simulado(simulado_id: int) -> RedirectResponse:
    with connect() as conn:
        conn.execute("DELETE FROM simulado_questions WHERE simulado_id = ?", (simulado_id,))
        conn.execute("DELETE FROM simulados WHERE id = ?", (simulado_id,))
    return redirect("/simulados")


@app.post("/simulados/clear")
def clear_all_simulados() -> RedirectResponse:
    with connect() as conn:
        conn.execute("DELETE FROM simulado_questions")
        conn.execute("DELETE FROM simulados")
    return redirect("/simulados")


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request) -> HTMLResponse:
    with connect() as conn:
        exams = conn.execute(
            """
            SELECT e.*, COUNT(q.id) AS question_count
            FROM exams e
            LEFT JOIN questions q ON q.exam_id = e.id
            GROUP BY e.id
            ORDER BY e.created_at DESC
            """
        ).fetchall()
        totals = conn.execute(
            "SELECT COUNT(*) AS total, SUM(CASE WHEN topic != '' THEN 1 ELSE 0 END) AS classified FROM questions"
        ).fetchone()
    groups = discover_source_groups(DEFAULT_SOURCE_DIR)
    years = sorted({group.year for group in groups}, reverse=True)
    return templates.TemplateResponse(
        request,
        "admin/index.html",
        {
            "exams": exams,
            "years": years,
            "source_dir": DEFAULT_SOURCE_DIR,
            "totals": totals,
            "classifying_all": _is_running(ALL_SCOPE),
            "ollama_host": classify.OLLAMA_HOST,
            "ollama_model": classify.OLLAMA_MODEL,
        },
    )


@app.post("/admin/import-local")
def admin_import_local(year: Annotated[str, Form()] = "") -> RedirectResponse:
    groups = discover_source_groups(DEFAULT_SOURCE_DIR, year.strip() or None)
    if not groups:
        raise HTTPException(400, "Nenhuma prova encontrada para importar")
    last_id = 0
    for group in groups:
        last_id = import_group(group)
    return redirect(f"/admin/exams/{last_id}" if last_id else "/admin")


@app.post("/admin/upload")
async def admin_upload(
    year: Annotated[str, Form()],
    title: Annotated[str, Form()],
    variant: Annotated[str, Form()] = "",
    exam_files: Annotated[list[UploadFile], File()] = [],
    answer_file: Annotated[UploadFile | None, File()] = None,
) -> RedirectResponse:
    upload_dir = ROOT_DIR / "var" / "uploads" / slugify(f"{year}-{title}-{variant}-{utcnow()}")
    upload_dir.mkdir(parents=True, exist_ok=True)
    exam_paths: list[Path] = []
    for upload in exam_files:
        if not upload.filename:
            continue
        destination = upload_dir / Path(upload.filename).name
        destination.write_bytes(await upload.read())
        exam_paths.append(destination)
    answer_path: Path | None = None
    if answer_file and answer_file.filename:
        answer_path = upload_dir / Path(answer_file.filename).name
        answer_path.write_bytes(await answer_file.read())
    if not exam_paths:
        raise HTTPException(400, "Envie ao menos um PDF de prova")

    group = type("UploadGroup", (), {"year": year, "title": title, "variant": variant, "exam_paths": exam_paths, "answer_path": answer_path})
    exam_id = import_group(group, source_kind="upload")
    return redirect(f"/admin/exams/{exam_id}")


@app.get("/admin/exams/{exam_id}", response_class=HTMLResponse)
def admin_exam(request: Request, exam_id: int) -> HTMLResponse:
    exam = get_exam_or_404(exam_id)
    with connect() as conn:
        stats = conn.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN correct_answer != '' THEN 1 ELSE 0 END) AS answered,
                   SUM(CASE WHEN statement != '' THEN 1 ELSE 0 END) AS with_statement,
                   SUM(CASE WHEN topic != '' THEN 1 ELSE 0 END) AS classified
            FROM questions WHERE exam_id = ?
            """,
            (exam_id,),
        ).fetchone()
    return templates.TemplateResponse(
        request,
        "admin/exam.html",
        {
            "exam": exam,
            "stats": stats,
            "classifying": _is_running(exam_id),
            "reextracting": _reextract_state.get(exam_id, {}).get("running", False),
            "ollama_host": classify.OLLAMA_HOST,
            "ollama_model": classify.OLLAMA_MODEL,
        },
    )


# Estado do lote por escopo, para progresso ao vivo e mensagem de erro.
# Chave = exam_id (uma prova) ou ALL_SCOPE (todas). O lote é idempotente:
# só processa questões sem tema e só grava quando topic ainda está vazio.
ALL_SCOPE = 0  # nenhum exame tem id 0 (AUTOINCREMENT começa em 1)
_classify_lock = threading.Lock()
_classify_state: dict[int, dict] = {}


def _is_running(scope: int) -> bool:
    with _classify_lock:
        return _classify_state.get(scope, {}).get("running", False)


def question_image_paths(conn, question_id: int) -> list[Path]:
    """Recortes da questão para classificação multimodal (original primeiro)."""
    rows = conn.execute(
        "SELECT filename FROM question_images WHERE question_id = ? ORDER BY (label = 'original') DESC, id",
        (question_id,),
    ).fetchall()
    paths: list[Path] = []
    for row in rows:
        path = ROOT_DIR / "var" / "images" / row["filename"]
        if path.exists():
            paths.append(path)
    return paths[:3]


def run_classification(scope: int, exam_id: int | None = None, force: bool = False) -> None:
    """Classifica questões uma a uma, salvando cada resultado. Se ``exam_id`` é None,
    varre TODAS as provas. Por padrão só processa questões sem tema; com ``force`` re-escaneia
    também as já classificadas pela IA (mantém as manuais intactas). Roda em background:
    fechar o navegador não interrompe."""
    error = ""
    done = 0
    # No modo força, re-escaneia sem tema + auto, mas preserva o que foi setado à mão.
    where_filter = "topic_source != 'manual'" if force else "topic = ''"
    try:
        with connect() as conn:
            if exam_id is None:
                rows = conn.execute(
                    f"SELECT * FROM questions WHERE {where_filter} ORDER BY exam_id, number"
                ).fetchall()
            else:
                rows = conn.execute(
                    f"SELECT * FROM questions WHERE exam_id = ? AND {where_filter} ORDER BY number",
                    (exam_id,),
                ).fetchall()
            pending = [dict(row) for row in rows]
            images_by_question = {q["id"]: question_image_paths(conn, q["id"]) for q in pending}
        with _classify_lock:
            _classify_state[scope].update(run_total=len(pending), done=0)
        for question in pending:
            try:
                result = classify.classify_with_retry(question, images_by_question.get(question["id"]))
            except Exception as exc:
                # Erro de rede/servidor Ollama: para o lote. O que já foi salvo
                # permanece; clicar o botão de novo retoma de onde parou.
                error = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
                break
            done += 1
            with _classify_lock:
                if scope in _classify_state:
                    _classify_state[scope]["done"] = done
            if not result.ok:
                continue
            with connect() as conn:
                conn.execute(
                    f"""
                    UPDATE questions
                    SET area = ?, topic = ?, subtopic = ?, topic_confidence = ?,
                        topic_source = 'auto', updated_at = ?
                    WHERE id = ? AND {where_filter}
                    """,
                    (result.area, result.tema, result.subtopic, result.confidence, utcnow(), question["id"]),
                )
    finally:
        with _classify_lock:
            _classify_state[scope] = {"running": False, "error": error}


def _start_scope(scope: int, exam_id: int | None, background: BackgroundTasks, force: bool = False) -> bool:
    with _classify_lock:
        if _classify_state.get(scope, {}).get("running"):
            return False
        # Marca como rodando ANTES do redirect, para a página já mostrar progresso.
        _classify_state[scope] = {"running": True, "error": "", "done": 0, "run_total": 0}
    background.add_task(run_classification, scope, exam_id, force)
    return True


@app.post("/admin/exams/{exam_id}/classify")
def admin_classify(exam_id: int, background: BackgroundTasks, force: Annotated[bool, Form()] = False) -> RedirectResponse:
    get_exam_or_404(exam_id)
    _start_scope(exam_id, exam_id, background, force)
    return redirect(f"/admin/exams/{exam_id}")


@app.post("/admin/classify-all")
def admin_classify_all(background: BackgroundTasks, force: Annotated[bool, Form()] = False) -> RedirectResponse:
    _start_scope(ALL_SCOPE, None, background, force)
    return redirect("/admin")


@app.get("/admin/classify-all/status")
def admin_classify_all_status() -> JSONResponse:
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total, SUM(CASE WHEN topic != '' THEN 1 ELSE 0 END) AS classified FROM questions"
        ).fetchone()
    with _classify_lock:
        state = _classify_state.get(ALL_SCOPE, {"running": False, "error": ""})
    return JSONResponse(
        {
            "total": row["total"] or 0,
            "classified": row["classified"] or 0,
            "running": state.get("running", False),
            "error": state.get("error", ""),
            "done": state.get("done", 0),
            "run_total": state.get("run_total", 0),
        }
    )


@app.get("/admin/exams/{exam_id}/classify/status")
def admin_classify_status(exam_id: int) -> JSONResponse:
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total, SUM(CASE WHEN topic != '' THEN 1 ELSE 0 END) AS classified "
            "FROM questions WHERE exam_id = ?",
            (exam_id,),
        ).fetchone()
    with _classify_lock:
        state = _classify_state.get(exam_id, {"running": False, "error": ""})
    return JSONResponse(
        {
            "total": row["total"] or 0,
            "classified": row["classified"] or 0,
            "running": state.get("running", False),
            "error": state.get("error", ""),
            "done": state.get("done", 0),
            "run_total": state.get("run_total", 0),
        }
    )


@app.post("/admin/exams/{exam_id}/questions/{question_id}/classify")
def admin_classify_one(exam_id: int, question_id: int) -> RedirectResponse:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM questions WHERE id = ? AND exam_id = ?", (question_id, exam_id)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Questão não encontrada")
        image_paths = question_image_paths(conn, question_id)
    try:
        result = classify.classify_with_retry(dict(row), image_paths)
    except Exception as exc:
        raise HTTPException(502, f"Erro ao falar com o Ollama em {classify.OLLAMA_HOST}: {exc}")
    if not result.ok:
        raise HTTPException(422, result.error or "Não foi possível classificar a questão")
    with connect() as conn:
        conn.execute(
            """
            UPDATE questions
            SET area = ?, topic = ?, subtopic = ?, topic_confidence = ?, topic_source = 'auto', updated_at = ?
            WHERE id = ?
            """,
            (result.area, result.tema, result.subtopic, result.confidence, utcnow(), question_id),
        )
    return redirect(f"/admin/exams/{exam_id}/questions/{question_id}")


@app.post("/admin/exams/{exam_id}/metadata")
def admin_update_metadata(
    exam_id: int,
    year: Annotated[str, Form()],
    title: Annotated[str, Form()],
    variant: Annotated[str, Form()] = "",
) -> RedirectResponse:
    with connect() as conn:
        conn.execute(
            "UPDATE exams SET year = ?, title = ?, variant = ?, updated_at = ? WHERE id = ?",
            (year, title, variant, utcnow(), exam_id),
        )
    return redirect(f"/admin/exams/{exam_id}")


@app.post("/admin/exams/{exam_id}/publish")
def admin_publish(exam_id: int) -> RedirectResponse:
    with connect() as conn:
        conn.execute("UPDATE exams SET status = 'published', updated_at = ? WHERE id = ?", (utcnow(), exam_id))
    return redirect(f"/admin/exams/{exam_id}")


@app.post("/admin/exams/{exam_id}/unpublish")
def admin_unpublish(exam_id: int) -> RedirectResponse:
    with connect() as conn:
        conn.execute("UPDATE exams SET status = 'draft', updated_at = ? WHERE id = ?", (utcnow(), exam_id))
    return redirect(f"/admin/exams/{exam_id}")


# Estado da re-extração de imagens por prova, para progresso ao vivo (igual ao
# classificador). Roda em background: fechar o navegador não interrompe.
_reextract_lock = threading.Lock()
_reextract_state: dict[int, dict] = {}


def run_reextraction(exam_id: int) -> None:
    """Regenera os recortes/imagens da prova a partir dos PDFs de origem, sem criar
    prova nova nem mexer nos ids das questões (simulados continuam válidos). Aplica
    melhorias de extração a provas já importadas. Preserva imagens enviadas à mão."""
    error = ""
    done = 0
    total = 0
    try:
        exam = get_exam_or_404(exam_id)
        source_paths = [Path(p) for p in loads(exam["source_paths"], []) if p]
        source_paths = [p for p in source_paths if p.exists()]
        if not source_paths:
            error = "Prova sem PDFs de origem disponíveis (ex.: importada de pacote)."
            return
        answer_path = Path(exam["answer_key_path"]) if exam["answer_key_path"] else None
        image_dir = ROOT_DIR / "var" / "images" / f"exam_{exam_id}"
        with connect() as conn:
            total = int(conn.execute("SELECT COUNT(*) AS c FROM questions WHERE exam_id = ?", (exam_id,)).fetchone()["c"])
        with _reextract_lock:
            if exam_id in _reextract_state:
                _reextract_state[exam_id]["total"] = total

        def bump() -> None:
            nonlocal done
            done += 1
            with _reextract_lock:
                if exam_id in _reextract_state:
                    _reextract_state[exam_id]["done"] = done

        # Apaga as imagens automáticas antigas ANTES de gerar as novas: os nomes de
        # arquivo são determinísticos, então deletar depois apagaria os recém-escritos.
        with connect() as conn:
            old = conn.execute(
                "SELECT qi.id, qi.filename FROM question_images qi JOIN questions q ON q.id = qi.question_id "
                "WHERE q.exam_id = ? AND qi.label IN ('original', 'embedded')",
                (exam_id,),
            ).fetchall()
            for row in old:
                path = ROOT_DIR / "var" / "images" / row["filename"]
                if path.exists():
                    path.unlink()
                conn.execute("DELETE FROM question_images WHERE id = ?", (row["id"],))

        parsed = parse_exam_sources(
            source_paths, answer_path, year=exam["year"], variant=exam["variant"],
            image_dir=image_dir, progress=bump,
        )
        now = utcnow()
        with connect() as conn:
            question_ids = {
                int(row["number"]): int(row["id"])
                for row in conn.execute("SELECT id, number FROM questions WHERE exam_id = ?", (exam_id,)).fetchall()
            }
            for image in parsed.images:
                question_id = question_ids.get(image.question_number)
                if not question_id:
                    continue
                conn.execute(
                    "INSERT INTO question_images (question_id, filename, source_page, label, created_at) VALUES (?, ?, ?, ?, ?)",
                    (question_id, f"exam_{exam_id}/{image.filename}", image.source_page, image.label, now),
                )
            conn.execute("UPDATE exams SET updated_at = ? WHERE id = ?", (now, exam_id))
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
    finally:
        with _reextract_lock:
            _reextract_state[exam_id] = {"running": False, "error": error, "done": done, "total": total}


@app.post("/admin/exams/{exam_id}/reextract")
def admin_reextract_images(exam_id: int, background: BackgroundTasks) -> RedirectResponse:
    get_exam_or_404(exam_id)
    with _reextract_lock:
        if _reextract_state.get(exam_id, {}).get("running"):
            return redirect(f"/admin/exams/{exam_id}")
        _reextract_state[exam_id] = {"running": True, "error": "", "done": 0, "total": 0}
    background.add_task(run_reextraction, exam_id)
    return redirect(f"/admin/exams/{exam_id}")


@app.get("/admin/exams/{exam_id}/reextract/status")
def admin_reextract_status(exam_id: int) -> JSONResponse:
    with _reextract_lock:
        state = _reextract_state.get(exam_id, {"running": False, "error": "", "done": 0, "total": 0})
    done = state.get("done", 0)
    total = state.get("total", 0)
    return JSONResponse(
        {
            "running": state.get("running", False),
            "error": state.get("error", ""),
            "done": done,
            "run_total": total,
            "classified": done,
            "total": total,
        }
    )


@app.get("/admin/exams/{exam_id}/answers", response_class=HTMLResponse)
def admin_answers(request: Request, exam_id: int) -> HTMLResponse:
    exam = get_exam_or_404(exam_id)
    with connect() as conn:
        questions = conn.execute("SELECT * FROM questions WHERE exam_id = ? ORDER BY number", (exam_id,)).fetchall()
    return templates.TemplateResponse(request, "admin/answers.html", {"exam": exam, "questions": questions})


@app.post("/admin/exams/{exam_id}/answers")
async def admin_save_answers(request: Request, exam_id: int) -> RedirectResponse:
    form = await request.form()
    now = utcnow()
    with connect() as conn:
        rows = conn.execute("SELECT id, number FROM questions WHERE exam_id = ?", (exam_id,)).fetchall()
        for row in rows:
            value = str(form.get(f"answer_{row['number']}", "")).strip().upper()
            conn.execute("UPDATE questions SET correct_answer = ?, updated_at = ? WHERE id = ?", (value, now, row["id"]))
        conn.execute("UPDATE exams SET updated_at = ? WHERE id = ?", (now, exam_id))
    return redirect(f"/admin/exams/{exam_id}/answers")


@app.get("/admin/exams/{exam_id}/questions", response_class=HTMLResponse)
def admin_questions(request: Request, exam_id: int) -> HTMLResponse:
    exam = get_exam_or_404(exam_id)
    with connect() as conn:
        questions = conn.execute("SELECT * FROM questions WHERE exam_id = ? ORDER BY number", (exam_id,)).fetchall()
    return templates.TemplateResponse(request, "admin/questions.html", {"exam": exam, "questions": questions})


@app.get("/admin/exams/{exam_id}/questions/{question_id}", response_class=HTMLResponse)
def admin_question_edit(request: Request, exam_id: int, question_id: int) -> HTMLResponse:
    exam = get_exam_or_404(exam_id)
    with connect() as conn:
        question = conn.execute("SELECT * FROM questions WHERE id = ? AND exam_id = ?", (question_id, exam_id)).fetchone()
        if not question:
            raise HTTPException(404, "Questão não encontrada")
        images = conn.execute("SELECT * FROM question_images WHERE question_id = ? ORDER BY label DESC, id", (question_id,)).fetchall()
    original_images = [image for image in images if image["label"] == "original"]
    extra_images = [image for image in images if image["label"] != "original"]
    return templates.TemplateResponse(
        request,
        "admin/question_edit.html",
        {
            "exam": exam,
            "question": question,
            "images": images,
            "original_images": original_images,
            "extra_images": extra_images,
            "temas_by_area": classify.TEMAS_BY_AREA,
            "subtopics_by_tema": classify.SUBTOPICS_BY_TEMA,
        },
    )


@app.post("/admin/exams/{exam_id}/questions/{question_id}")
async def admin_question_save(
    exam_id: int,
    question_id: int,
    number: Annotated[int, Form()],
    statement: Annotated[str, Form()],
    alternative_a: Annotated[str, Form()] = "",
    alternative_b: Annotated[str, Form()] = "",
    alternative_c: Annotated[str, Form()] = "",
    alternative_d: Annotated[str, Form()] = "",
    alternative_e: Annotated[str, Form()] = "",
    correct_answer: Annotated[str, Form()] = "",
    area: Annotated[str, Form()] = "",
    topic: Annotated[str, Form()] = "",
    subtopic: Annotated[str, Form()] = "",
    image_file: Annotated[UploadFile | None, File()] = None,
) -> RedirectResponse:
    now = utcnow()
    topic = topic.strip()
    area = classify.AREA_BY_TEMA.get(topic, area.strip()) if topic else ""
    subtopic = subtopic.strip() if topic else ""
    topic_source = "manual" if topic else ""
    with connect() as conn:
        conn.execute(
            """
            UPDATE questions
            SET number = ?, statement = ?, alternative_a = ?, alternative_b = ?, alternative_c = ?,
                alternative_d = ?, alternative_e = ?, correct_answer = ?,
                area = ?, topic = ?, subtopic = ?, topic_source = ?, updated_at = ?
            WHERE id = ? AND exam_id = ?
            """,
            (
                number,
                statement,
                alternative_a,
                alternative_b,
                alternative_c,
                alternative_d,
                alternative_e,
                correct_answer.strip().upper(),
                area,
                topic,
                subtopic,
                topic_source,
                now,
                question_id,
                exam_id,
            ),
        )
        if image_file and image_file.filename:
            image_dir = ROOT_DIR / "var" / "images" / f"exam_{exam_id}"
            image_dir.mkdir(parents=True, exist_ok=True)
            filename = f"manual_q{number:02d}_{Path(image_file.filename).name}"
            destination = image_dir / filename
            destination.write_bytes(await image_file.read())
            conn.execute(
                "INSERT INTO question_images (question_id, filename, source_page, label, created_at) VALUES (?, ?, NULL, 'manual', ?)",
                (question_id, f"exam_{exam_id}/{filename}", now),
            )
        conn.execute("UPDATE exams SET updated_at = ? WHERE id = ?", (now, exam_id))
    return redirect(f"/admin/exams/{exam_id}/questions/{question_id}")


@app.post("/admin/images/{image_id}/delete")
def admin_delete_image(image_id: int) -> RedirectResponse:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT qi.*, q.exam_id
            FROM question_images qi
            JOIN questions q ON q.id = qi.question_id
            WHERE qi.id = ?
            """,
            (image_id,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "Imagem não encontrada")
        conn.execute("DELETE FROM question_images WHERE id = ?", (image_id,))
    path = ROOT_DIR / "var" / "images" / row["filename"]
    if path.exists():
        path.unlink()
    return redirect(f"/admin/exams/{row['exam_id']}/questions/{row['question_id']}")


@app.get("/admin/exams/{exam_id}/export")
def admin_export(exam_id: int) -> FileResponse:
    exam = get_exam_or_404(exam_id)
    with connect() as conn:
        questions = [dict(row) for row in conn.execute("SELECT * FROM questions WHERE exam_id = ? ORDER BY number", (exam_id,)).fetchall()]
        images = [
            dict(row)
            for row in conn.execute(
                """
                SELECT qi.*, q.number AS question_number
                FROM question_images qi
                JOIN questions q ON q.id = qi.question_id
                WHERE q.exam_id = ?
                ORDER BY q.number, qi.id
                """,
                (exam_id,),
            ).fetchall()
        ]
    payload = build_export_payload(exam, questions, images)
    export_dir = ROOT_DIR / "var" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    zip_path = export_dir / f"{slugify(exam['title']) or 'poscomp'}-{exam_id}.zip"
    with NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".json") as tmp:
        json.dump(payload, tmp, ensure_ascii=False, indent=2)
        tmp_path = Path(tmp.name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(tmp_path, "exam.json")
        for image in images:
            image_path = ROOT_DIR / "var" / "images" / image["filename"]
            if image_path.exists():
                archive.write(image_path, f"images/{Path(image['filename']).name}")
    tmp_path.unlink(missing_ok=True)
    return FileResponse(zip_path, filename=zip_path.name, media_type="application/zip")


@app.post("/admin/import-package")
async def admin_import_package(package: Annotated[UploadFile, File()]) -> RedirectResponse:
    if not package.filename:
        raise HTTPException(400, "Envie um pacote .zip")
    data = await package.read()
    with tempfile_zip(data) as zip_path:
        with zipfile.ZipFile(zip_path) as archive:
            try:
                payload = json.loads(archive.read("exam.json").decode("utf-8"))
            except KeyError as exc:
                raise HTTPException(400, "Pacote sem exam.json") from exc

            exam = payload.get("exam", {})
            now = utcnow()
            with connect() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO exams (year, title, variant, status, source_kind, source_paths, answer_key_path, extraction_notes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'package', '[]', '', ?, ?, ?)
                    """,
                    (
                        str(exam.get("year", "")),
                        str(exam.get("title", "Prova importada")),
                        str(exam.get("variant", "")),
                        str(exam.get("status", "draft")),
                        "Importado de pacote exportado.",
                        now,
                        now,
                    ),
                )
                exam_id = int(cursor.lastrowid)
                question_id_by_old: dict[int, int] = {}
                for question in payload.get("questions", []):
                    cursor = conn.execute(
                        """
                        INSERT INTO questions (
                            exam_id, number, page, statement, alternative_a, alternative_b, alternative_c,
                            alternative_d, alternative_e, extracted_answer, correct_answer, answer_confidence,
                            raw_text, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            exam_id,
                            int(question.get("number", 0)),
                            question.get("page"),
                            str(question.get("statement", "")),
                            str(question.get("alternative_a", "")),
                            str(question.get("alternative_b", "")),
                            str(question.get("alternative_c", "")),
                            str(question.get("alternative_d", "")),
                            str(question.get("alternative_e", "")),
                            str(question.get("extracted_answer", "")),
                            str(question.get("correct_answer", "")),
                            float(question.get("answer_confidence", 0) or 0),
                            str(question.get("raw_text", "")),
                            now,
                            now,
                        ),
                    )
                    question_id_by_old[int(question.get("id", 0))] = int(cursor.lastrowid)

                image_dir = ROOT_DIR / "var" / "images" / f"exam_{exam_id}"
                for image in payload.get("images", []):
                    old_filename = Path(str(image.get("filename", ""))).name
                    archive_name = f"images/{old_filename}"
                    if archive_name not in archive.namelist():
                        continue
                    safe_extract_zip_member(image_dir, old_filename, archive.read(archive_name))
                    question_id = question_id_by_old.get(int(image.get("question_id", 0)))
                    if not question_id and image.get("question_number"):
                        row = conn.execute(
                            "SELECT id FROM questions WHERE exam_id = ? AND number = ?",
                            (exam_id, int(image["question_number"])),
                        ).fetchone()
                        question_id = int(row["id"]) if row else 0
                    if question_id:
                        conn.execute(
                            "INSERT INTO question_images (question_id, filename, source_page, label, created_at) VALUES (?, ?, ?, ?, ?)",
                            (question_id, f"exam_{exam_id}/{old_filename}", image.get("source_page"), str(image.get("label", "")), now),
                        )
    return redirect(f"/admin/exams/{exam_id}")


class tempfile_zip:
    def __init__(self, data: bytes):
        self.data = data
        self.path: Path | None = None

    def __enter__(self) -> Path:
        tmp = NamedTemporaryFile(delete=False, suffix=".zip")
        tmp.write(self.data)
        tmp.close()
        self.path = Path(tmp.name)
        return self.path

    def __exit__(self, *_args) -> None:
        if self.path:
            self.path.unlink(missing_ok=True)


def run() -> None:
    uvicorn.run("poscomp_app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
