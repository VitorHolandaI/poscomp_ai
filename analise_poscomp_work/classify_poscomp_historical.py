from __future__ import annotations

import csv
import json
import os
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path("/home/vitor/git/poscomp_web")
SCRIPT_DIR = Path(__file__).resolve().parent
TAXONOMY_PATH = ROOT / "poscomp_app" / "taxonomy.json"
QUESTIONS_PATH = SCRIPT_DIR / "poscomp_segmented" / "all_questions.jsonl"
OUT_JSONL = SCRIPT_DIR / "poscomp_historical_draft.jsonl"
OUT_CSV = SCRIPT_DIR / "poscomp_historical_draft.csv"
ERR_LOG = SCRIPT_DIR / "poscomp_historical_errors.log"

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:12b")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "10"))
REQUEST_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "180"))
STOP_AT = os.environ.get("STOP_AT", "00:55")
MIN_SECONDS_FOR_NEXT_BATCH = int(os.environ.get("MIN_SECONDS_FOR_NEXT_BATCH", "180"))


def stop_deadline() -> datetime:
    now = datetime.now()
    hour, minute = [int(part) for part in STOP_AT.split(":", 1)]
    deadline = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if deadline <= now - timedelta(hours=12):
        deadline += timedelta(days=1)
    return deadline


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        parsed, _ = decoder.raw_decode(raw)
        return parsed


def taxonomy_for_area(taxonomy: dict, area: str) -> str:
    lines: list[str] = []
    for tema, subs in taxonomy[area]["temas"].items():
        lines.append(f"TEMA: {tema}")
        lines.append("SUBTOPICOS: " + "; ".join(subs))
    return "\n".join(lines)


def schema_for_area(taxonomy: dict, area: str) -> dict:
    temas = list(taxonomy[area]["temas"].keys())
    subs = [sub for topic_subs in taxonomy[area]["temas"].values() for sub in topic_subs]
    return {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer"},
                        "question": {"type": "integer"},
                        "tema": {"type": "string", "enum": temas},
                        "subtopico": {"type": "string", "enum": subs},
                        "resumo": {"type": "string"},
                        "confidence": {"type": "number"},
                        "needs_review": {"type": "boolean"},
                        "note": {"type": "string"},
                    },
                    "required": [
                        "year",
                        "question",
                        "tema",
                        "subtopico",
                        "resumo",
                        "confidence",
                        "needs_review",
                        "note",
                    ],
                },
            }
        },
        "required": ["items"],
    }


def validate_item(taxonomy: dict, area: str, item: dict) -> tuple[bool, str]:
    tema = item.get("tema")
    subtopico = item.get("subtopico")
    if tema not in taxonomy[area]["temas"]:
        return False, f"tema fora da area {area}: {tema!r}"
    if subtopico not in taxonomy[area]["temas"][tema]:
        return False, f"subtopico fora do tema {tema!r}: {subtopico!r}"
    return True, ""


def post_ollama(payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_HOST + "/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def classify_batch(taxonomy: dict, area: str, batch: list[dict]) -> list[dict]:
    questions = []
    for row in batch:
        text = row["text"][:1800]
        questions.append(
            f"ID {row['year']}-{row['question']:02d}\n"
            f"Area original do caderno: {row['area']}\n"
            f"Texto:\n{text}"
        )

    system = (
        "Voce e um auditor de classificacao POSCOMP. Classifique cada questao dentro da AREA informada, "
        "copiando tema e subtopico exatamente da taxonomia. Use o conteudo principal da questao, nao palavras soltas. "
        "Se houver figura/OCR ruim/ambiguidade, escolha o melhor rotulo e marque needs_review=true. "
        "Regras: conjuntos, intervalos e operacoes com conjuntos -> Matematica Discreta; derivada, integral, limite, "
        "continuidade e maximos/minimos -> Calculo; vetores, retas, planos, distancias e angulos -> Geometria Analitica; "
        "matrizes, sistemas lineares, subespacos, bases, autovalores -> Algebra Linear; contagem -> Analise Combinatoria; "
        "chance, probabilidade, media, variancia e correlacao -> Probabilidade e Estatistica; trace de codigo -> Tecnicas "
        "de Programacao; Big-O, recorrencia de algoritmo e crescimento assintotico -> Analise de Algoritmos. "
        "Responda somente JSON. O resumo deve ter no maximo uma frase curta."
    )
    user = (
        f"AREA: {area}\n"
        f"TAXONOMIA DA AREA:\n{taxonomy_for_area(taxonomy, area)}\n\n"
        "QUESTOES:\n" + "\n\n".join(questions)
    )
    payload = {
        "model": MODEL,
        "stream": False,
        "think": False,
        "format": schema_for_area(taxonomy, area),
        "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    data = post_ollama(payload)
    raw = (data.get("message") or {}).get("content") or ""
    parsed = parse_json(raw)
    items = parsed.get("items") or []
    by_key = {(int(item["year"]), int(item["question"])): item for item in items}

    results: list[dict] = []
    for row in batch:
        key = (row["year"], row["question"])
        item = by_key.get(key)
        if not item:
            raise RuntimeError(f"modelo nao retornou item para {key}")
        ok, error = validate_item(taxonomy, area, item)
        if not ok:
            raise RuntimeError(f"{key}: {error}")
        results.append(
            {
                "year": row["year"],
                "question": row["question"],
                "area_original": row["area"],
                "area": area,
                "tema": item["tema"],
                "subtopico": item["subtopico"],
                "resumo": item.get("resumo", ""),
                "confidence": float(item.get("confidence", 0.0)),
                "needs_review": bool(item.get("needs_review", False)),
                "note": item.get("note", ""),
                "model": MODEL,
                "source": "ollama_area_restricted_draft",
            }
        )
    return results


def append_jsonl(rows: list[dict]) -> None:
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def rewrite_csv() -> None:
    rows = read_jsonl(OUT_JSONL)
    fields = [
        "year",
        "question",
        "area_original",
        "area",
        "tema",
        "subtopico",
        "resumo",
        "confidence",
        "needs_review",
        "note",
        "model",
        "source",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (r["year"], r["question"])):
            writer.writerow({field: row.get(field, "") for field in fields})


def main() -> None:
    taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    questions = read_jsonl(QUESTIONS_PATH)
    existing = {(row["year"], row["question"]) for row in read_jsonl(OUT_JSONL)}
    deadline = stop_deadline()

    targets = [
        row
        for row in questions
        if 2002 <= row["year"] <= 2019 and (row["year"], row["question"]) not in existing
    ]
    targets.sort(key=lambda r: (-r["year"], r["question"]))
    print(
        f"starting model={MODEL} batch_size={BATCH_SIZE} pending={len(targets)} "
        f"existing={len(existing)} deadline={deadline:%H:%M:%S}",
        flush=True,
    )

    processed = 0
    i = 0
    while i < len(targets):
        now = datetime.now()
        remaining = (deadline - now).total_seconds()
        if remaining < MIN_SECONDS_FOR_NEXT_BATCH:
            print(f"stopping before next batch; remaining_seconds={remaining:.0f}", flush=True)
            break

        current = targets[i]
        area = current["area"]
        year = current["year"]
        batch = []
        while i < len(targets) and len(batch) < BATCH_SIZE:
            candidate = targets[i]
            if candidate["year"] != year or candidate["area"] != area:
                break
            batch.append(candidate)
            i += 1

        label = f"{year} {area} Q{batch[0]['question']:02d}-Q{batch[-1]['question']:02d}"
        start = time.time()
        print(f"batch start {label} n={len(batch)}", flush=True)
        try:
            rows = classify_batch(taxonomy, area, batch)
        except Exception as exc:
            with ERR_LOG.open("a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} ERROR {label}: {type(exc).__name__}: {exc}\n")
            print(f"batch error {label}: {type(exc).__name__}: {exc}", flush=True)
            # Avoid an infinite loop on a problematic batch; skip only this batch for now.
            continue

        append_jsonl(rows)
        processed += len(rows)
        elapsed = time.time() - start
        review = sum(1 for row in rows if row["needs_review"])
        print(f"batch done {label} seconds={elapsed:.1f} review={review}", flush=True)

    rewrite_csv()
    total = len(read_jsonl(OUT_JSONL))
    print(f"finished processed_now={processed} total_rows={total} csv={OUT_CSV}", flush=True)


if __name__ == "__main__":
    main()
