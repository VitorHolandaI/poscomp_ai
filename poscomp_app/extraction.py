from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import fitz


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_DIR = ROOT_DIR / "Provas-POSCOMP"

ANSWER_VALUES = {"A", "B", "C", "D", "E", "*", "ANULADA"}


@dataclass
class ParsedQuestion:
    number: int
    statement: str
    alternatives: dict[str, str]
    raw_text: str
    page: int | None = None
    source_path: str = ""
    extracted_answer: str = ""
    answer_confidence: float = 0


@dataclass
class ParsedImage:
    question_number: int
    filename: str
    source_page: int
    label: str = ""


@dataclass
class ParsedExam:
    questions: list[ParsedQuestion]
    images: list[ParsedImage] = field(default_factory=list)
    answers: dict[int, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


@dataclass
class SourceGroup:
    year: str
    title: str
    variant: str
    exam_paths: list[Path]
    answer_path: Path | None


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return normalized or "poscomp"


def run_command(args: list[str], timeout: int = 120) -> str:
    completed = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"Command failed: {' '.join(args)}")
    return completed.stdout


def extract_pdf_text(path: Path) -> str:
    return run_command(["pdftotext", "-layout", str(path), "-"])


def ocr_pdf_text(path: Path, *, dpi: int = 300, psm: int = 6) -> str:
    with tempfile.TemporaryDirectory(prefix="poscomp-ocr-") as tmp:
        prefix = Path(tmp) / "page"
        run_command(["pdftocairo", "-png", "-r", str(dpi), str(path), str(prefix)], timeout=240)
        parts: list[str] = []
        for image in sorted(Path(tmp).glob("page-*.png")):
            try:
                parts.append(
                    run_command(
                        ["tesseract", str(image), "stdout", "--psm", str(psm), "-l", "por+eng"],
                        timeout=240,
                    )
                )
            except RuntimeError as exc:
                parts.append(f"\n[OCR_ERROR {image.name}: {exc}]\n")
        return "\n\f\n".join(parts)


def extract_answer_text(path: Path) -> tuple[str, bool]:
    text = extract_pdf_text(path)
    if count_answer_like_pairs(text) >= 50:
        return text, False
    # Gabaritos em imagem/tabela, como 2025, precisam de DPI alto e PSM esparso.
    ocr = ocr_pdf_text(path, dpi=600, psm=11)
    if count_answer_like_pairs(ocr) > count_answer_like_pairs(text):
        return ocr, True
    return text, False


def normalize_answer(value: str) -> str:
    value = value.strip().upper().replace("∗", "*").replace("X", "*")
    if value == "*":
        return "ANULADA"
    return value if value in {"A", "B", "C", "D", "E", "ANULADA"} else ""


def normalize_ocr_number(value: str) -> int | None:
    cleaned = value.translate(str.maketrans({"O": "0", "o": "0", "I": "1", "l": "1", "|": "1"}))
    digits = re.sub(r"\D", "", cleaned)
    if not digits:
        return None
    try:
        number = int(digits[-2:] if len(digits) > 2 else digits)
    except ValueError:
        return None
    return number if 1 <= number <= 90 else None


def count_answer_like_pairs(text: str) -> int:
    return len(parse_answer_key_text(text))


def focus_answer_text(text: str, variant: str) -> str:
    upper = text.upper()
    if "TIPO 2" in upper and re.search(r"TIPO\s*2", variant.upper()):
        index = upper.find("TIPO 2")
        return text[index:]
    if "TIPO 1" in upper and re.search(r"TIPO\s*1", variant.upper()):
        start = upper.find("TIPO 1")
        end = upper.find("TIPO 2", start + 1)
        return text[start:end if end != -1 else None]
    return text


def parse_answer_key_text(text: str, *, variant: str = "") -> dict[int, str]:
    text = focus_answer_text(text, variant)
    text = text.replace("∗", "*").replace("—", "-").replace("–", "-")
    answers: dict[int, str] = {}

    anulada_pattern = re.compile(r"(?<!\w)(\d{1,2})\s*(?:[\.-]?\s*)?(?:QUEST[ÃA]O\s+)?ANULAD[AO]", re.IGNORECASE)
    for raw_number in anulada_pattern.findall(text):
        number = normalize_ocr_number(raw_number)
        if number and 1 <= number <= 70:
            answers[number] = "ANULADA"

    patterns = [
        re.compile(r"(?<!\w)([0OoIl|]{0,2}\d{1,2})\s*-\s*([A-Ea-e*])(?=$|\s|[^A-Za-z0-9])"),
        re.compile(r"(?<!\w)(\d{1,2})\s*[\.)]\s*\(([A-Ea-e*])\)"),
        re.compile(r"(?<!\w)(\d{1,2})\s+([A-Ea-e*])(?=$|\s|[^A-Za-z0-9])"),
        re.compile(r"(?<!\w)(\d{1,2})([A-Ea-e*])(?=$|\s|[^A-Za-z0-9])"),
    ]

    for pattern in patterns:
        for raw_number, raw_answer in pattern.findall(text):
            number = normalize_ocr_number(raw_number)
            answer = normalize_answer(raw_answer)
            if number and 1 <= number <= 70 and answer and number not in answers:
                answers[number] = answer

    if len(answers) < 60:
        answers.update({k: v for k, v in parse_answer_blocks(text).items() if k not in answers})

    return dict(sorted(answers.items()))


def parse_answer_blocks(text: str) -> dict[int, str]:
    tokens = re.findall(r"\b\d{1,2}\b|[A-Ea-e*∗]", text.replace("∗", "*"))
    answers: dict[int, str] = {}
    index = 0
    while index < len(tokens):
        if not tokens[index].isdigit():
            index += 1
            continue
        numbers: list[int] = []
        cursor = index
        expected = int(tokens[cursor])
        while cursor < len(tokens) and tokens[cursor].isdigit() and int(tokens[cursor]) == expected and 1 <= expected <= 70:
            numbers.append(expected)
            cursor += 1
            expected += 1
        if len(numbers) >= 3:
            values: list[str] = []
            value_cursor = cursor
            while value_cursor < len(tokens) and len(values) < len(numbers):
                answer = normalize_answer(tokens[value_cursor])
                if not answer:
                    break
                values.append(answer)
                value_cursor += 1
            if len(values) == len(numbers):
                for number, answer in zip(numbers, values, strict=True):
                    answers.setdefault(number, answer)
                index = value_cursor
                continue
        index += 1
    return answers


def page_texts_for_paths(paths: Iterable[Path]) -> list[tuple[Path, int, str]]:
    pages: list[tuple[Path, int, str]] = []
    for path in paths:
        text = extract_pdf_text(path)
        extracted_pages = text.split("\f")
        if should_ocr_exam_text(text):
            text = ocr_pdf_text(path, dpi=300, psm=6)
            extracted_pages = text.split("\f")
        for index, page in enumerate(extracted_pages, start=1):
            if page.strip():
                pages.append((path, index, page))
    return pages


def should_ocr_exam_text(text: str) -> bool:
    if len(text.strip()) < 1000:
        return True
    markers = len(re.findall(r"QUEST[ÃA]O\s*\d{1,2}|Quest[ãa]o\s*\d{1,2}", text))
    numbered = len(re.findall(r"(?m)^\s*\d{1,2}\s*(?:[\.)-]\s+|[ \t]+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]))\S", text))
    control_chars = sum(1 for char in text[:2000] if ord(char) < 32 and char not in "\n\r\t\f")
    printable = sum(1 for char in text[:2000] if char.isprintable() and not char.isspace())
    odd_controls = control_chars > 20 or (printable > 0 and control_chars / printable > 0.08)
    return markers < 10 and numbered < 20 and odd_controls


def split_questions(pages: list[tuple[Path, int, str]]) -> tuple[list[ParsedQuestion], list[str]]:
    notes: list[str] = []
    full_text = ""
    offsets: list[tuple[int, Path, int]] = []
    for path, page_number, text in pages:
        offsets.append((len(full_text), path, page_number))
        full_text += text + "\n"

    markers = find_question_markers(full_text)
    if len(markers) < 20:
        markers = find_numbered_question_markers(full_text)
    if len(markers) < 20:
        notes.append(f"Baixa confiança: apenas {len(markers)} marcadores de questão detectados.")

    questions: list[ParsedQuestion] = []
    for index, marker in enumerate(markers):
        start = marker["start"]
        end = markers[index + 1]["start"] if index + 1 < len(markers) else len(full_text)
        raw = full_text[start:end].strip()
        if not raw:
            continue
        number = marker["number"]
        statement, alternatives = parse_question_body(raw)
        source_path, page = location_for_offset(offsets, start)
        questions.append(
            ParsedQuestion(
                number=number,
                statement=statement,
                alternatives=alternatives,
                raw_text=raw,
                page=page,
                source_path=str(source_path) if source_path else "",
            )
        )

    deduped: dict[int, ParsedQuestion] = {}
    for question in questions:
        if 1 <= question.number <= 70 and question.number not in deduped:
            deduped[question.number] = question
    return [deduped[number] for number in sorted(deduped)], notes


def find_question_markers(text: str) -> list[dict[str, int]]:
    pattern = re.compile(r"(?im)^\s*[^\w\n]{0,12}\s*QUEST[ÃA]O\s*0?(\d{1,2})\s*[–\-—]?")
    return [{"number": int(match.group(1)), "start": match.start()} for match in pattern.finditer(text)]


def find_numbered_question_markers(text: str) -> list[dict[str, int]]:
    pattern = re.compile(r"(?m)^\s*(\d{1,2})\s*(?:[\.)-]\s+|[ \t]+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]))(?=\S)")
    candidates = [{"number": int(match.group(1)), "start": match.start()} for match in pattern.finditer(text)]
    candidates = [candidate for candidate in candidates if 1 <= candidate["number"] <= 70]
    section_start = first_content_section_start(text)
    if section_start is not None:
        candidates = [candidate for candidate in candidates if candidate["start"] >= section_start]
    if not candidates:
        return []

    best: list[dict[str, int]] = []
    by_number: dict[int, list[list[dict[str, int]]]] = {}
    for candidate in candidates:
        number = candidate["number"]
        chain = [candidate]
        if number > 1:
            previous_chains = by_number.get(number - 1, [])
            previous = max(
                (item for item in previous_chains if item[-1]["start"] < candidate["start"]),
                key=len,
                default=None,
            )
            if previous:
                chain = [*previous, candidate]
        by_number.setdefault(number, []).append(chain)
        if len(chain) > len(best) or (len(chain) == len(best) and chain[-1]["number"] > (best[-1]["number"] if best else 0)):
            best = chain

    if len(best) >= 20:
        return best

    # Alguns cadernos antigos separados por área podem não formar uma sequência perfeita.
    chosen: dict[int, dict[str, int]] = {}
    for candidate in candidates:
        chosen.setdefault(candidate["number"], candidate)
    return [chosen[number] for number in sorted(chosen)]


def first_content_section_start(text: str) -> int | None:
    markers = [
        "MATEMÁTICA",
        "MATEMATICA",
        "QUESTÕES DE MATEM",
        "QUESTOES DE MATEM",
        "PROVA DE MATEM",
    ]
    upper = text.upper()
    indexes = [upper.find(marker) for marker in markers if upper.find(marker) != -1]
    return min(indexes) if indexes else None


def location_for_offset(offsets: list[tuple[int, Path, int]], offset: int) -> tuple[Path | None, int | None]:
    current: tuple[Path | None, int | None] = (None, None)
    for start, _path, page in offsets:
        if start <= offset:
            current = (_path, page)
        else:
            break
    return current


def parse_question_body(raw: str) -> tuple[str, dict[str, str]]:
    body = re.sub(r"(?is)^\s*[^\w\n]{0,20}\s*QUEST[ÃA]O\s*0?\d{1,2}\s*[^\w\n]*\s*", "", raw, count=1)
    body = re.sub(r"(?is)^\s*\d{1,2}\s*[\.)-]\s*", "", body, count=1)
    body = re.sub(r"(?s)^\s*\d{1,2}[ \t]+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ])", "", body, count=1)
    body = clean_common_noise(body)

    alt_pattern = re.compile(r"(?m)^\s*(?:\(?([A-Ea-e])\)?[\.)])\s+(?=\S)")
    matches = list(alt_pattern.finditer(body))
    inline_pattern = re.compile(r"(?i)(?:^|\s)\(([a-e])\)\s+(?=\S)")
    inline_matches = list(inline_pattern.finditer(body))
    if len(matches) < 5 and len(inline_matches) >= 2:
        matches = inline_matches
    alternatives = {letter: "" for letter in "ABCDE"}
    if not matches:
        return normalize_spacing(body), alternatives

    statement = normalize_spacing(body[: matches[0].start()])
    for index, match in enumerate(matches):
        letter = match.group(1).upper()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        alternatives[letter] = normalize_spacing(body[start:end])
    return statement, alternatives


def clean_common_noise(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        upper = stripped.upper()
        if upper.startswith("EXECUÇÃO:") or upper.startswith("EXECUCAO:"):
            continue
        if upper.startswith("EXECUÇÃO") or upper.startswith("EXECUCAO"):
            continue
        if re.match(r"^\d+_[A-Z0-9_ -]*POSCOMP", upper):
            continue
        if re.match(r"^\d+_[A-Z0-9_ -]*EXAME", upper):
            continue
        if "EXAME POSCOMP" in upper and len(upper) <= 80:
            continue
        if "POSCOMP_NS" in upper and len(upper) <= 100:
            continue
        if re.match(r"^\d+\s*/\s*\d+$", stripped):
            continue
        lines.append(line.rstrip())
    return "\n".join(lines)


def normalize_spacing(text: str) -> str:
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    output: list[str] = []
    previous_blank = False
    for line in lines:
        blank = not line
        if blank and previous_blank:
            continue
        output.append(line)
        previous_blank = blank
    return "\n".join(output).strip()


def question_page_candidates(doc: fitz.Document, numbers: Iterable[int]) -> dict[int, list[int]]:
    """Páginas onde o marcador de cada número aparece visualmente (caixa do número
    à esquerda ou número seguido do enunciado). Pode haver falsos (capa/grade de
    gabarito); quem escolhe é o chamador, usando a página do texto como âncora."""
    wanted = set(numbers)
    marker_pattern = re.compile(r"QUEST[ÃA]O\s*0?(\d{1,2})", re.IGNORECASE)
    numbered_pattern = re.compile(r"^\s*(\d{1,2})\s*(?:[\.)-]\s+|[ \t]+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]))")
    standalone_pattern = re.compile(r"^0?(\d{1,2})$")
    candidates: dict[int, set[int]] = {}
    for page_index in range(doc.page_count):
        page = doc[page_index]
        try:
            data = page.get_text("dict")
        except Exception:
            continue
        for block in data.get("blocks", []):
            for line in block.get("lines", []):
                text = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
                if not text:
                    continue
                match = marker_pattern.search(text) or numbered_pattern.match(text)
                number = None
                if match:
                    number = int(match.group(1))
                else:
                    standalone = standalone_pattern.match(text)
                    x0 = float(line.get("bbox", [999, 0, 0, 0])[0])
                    if standalone and x0 < 80:
                        number = int(standalone.group(1))
                if number is None or number not in wanted:
                    continue
                candidates.setdefault(number, set()).add(page_index + 1)
    return {number: sorted(pages) for number, pages in candidates.items()}


def fix_question_pages(questions: list[ParsedQuestion], exam_paths: Iterable[Path]) -> None:
    path_by_resolved = {Path(p).resolve(): Path(p) for p in exam_paths}
    by_source: dict[Path, list[ParsedQuestion]] = {}
    for question in questions:
        if not question.source_path:
            continue
        resolved = Path(question.source_path).resolve()
        if resolved in path_by_resolved:
            by_source.setdefault(resolved, []).append(question)
    for resolved, group in by_source.items():
        try:
            doc = fitz.open(path_by_resolved[resolved])
        except Exception:
            continue
        candidates = question_page_candidates(doc, [question.number for question in group])
        doc.close()
        for question in group:
            options = candidates.get(question.number)
            if not options:
                continue
            # Âncora = página vinda do texto (boa na maioria); escolhe o candidato
            # visual mais próximo, descartando falsos distantes (capa etc).
            hint = question.page or 1
            question.page = min(options, key=lambda page: abs(page - hint))


def extract_images(paths: Iterable[Path], questions: list[ParsedQuestion], image_dir: Path, prefix: str, progress=None) -> list[ParsedImage]:
    original_images = render_question_crops(paths, questions, image_dir, prefix, progress)
    embedded_images = extract_embedded_images(paths, questions, image_dir, prefix)
    return [*original_images, *embedded_images]


def render_question_crops(paths: Iterable[Path], questions: list[ParsedQuestion], image_dir: Path, prefix: str, progress=None) -> list[ParsedImage]:
    image_dir.mkdir(parents=True, exist_ok=True)
    path_set = {Path(path).resolve() for path in paths}
    by_path_page: dict[Path, dict[int, list[int]]] = {}
    for question in questions:
        if not question.page:
            continue
        source_path = Path(question.source_path).resolve() if question.source_path else None
        if not source_path or source_path not in path_set:
            continue
        by_path_page.setdefault(source_path, {}).setdefault(question.page, []).append(question.number)

    images: list[ParsedImage] = []
    saved = 0
    for path in paths:
        resolved = path.resolve()
        valid_by_page = by_path_page.get(resolved, {})
        if not valid_by_page:
            continue
        try:
            doc = fitz.open(path)
        except Exception:
            continue
        positions_by_page = question_positions_for_doc(doc, valid_by_page)
        rendered_numbers: set[int] = set()
        for page_number, positions in sorted(positions_by_page.items()):
            if not positions:
                continue
            page = doc[page_number - 1]
            for index, (question_number, y) in enumerate(positions):
                next_y = positions[index + 1][1] if index + 1 < len(positions) else page.rect.height - 35
                top = max(0, y - 8)
                bottom = min(page.rect.height - 30, next_y - 5)
                if bottom - top < 45:
                    continue
                clip = fitz.Rect(24, top, page.rect.width - 24, bottom)
                try:
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip, alpha=False)
                    saved += 1
                    filename = f"{prefix}_q{question_number:02d}_original_{saved}.png"
                    pix.save(image_dir / filename)
                    images.append(
                        ParsedImage(
                            question_number=question_number,
                            filename=filename,
                            source_page=page_number,
                            label="original",
                        )
                    )
                    rendered_numbers.add(question_number)
                    if progress:
                        progress()
                except Exception:
                    continue
        for page_number, question_numbers in sorted(valid_by_page.items()):
            page = doc[page_number - 1]
            for question_number in question_numbers:
                if question_number in rendered_numbers:
                    continue
                try:
                    clip = fitz.Rect(24, 24, page.rect.width - 24, page.rect.height - 30)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip, alpha=False)
                    saved += 1
                    filename = f"{prefix}_q{question_number:02d}_original_page_{saved}.png"
                    pix.save(image_dir / filename)
                    images.append(
                        ParsedImage(
                            question_number=question_number,
                            filename=filename,
                            source_page=page_number,
                            label="original",
                        )
                    )
                    if progress:
                        progress()
                except Exception:
                    continue
        doc.close()
    return images


def extract_embedded_images(paths: Iterable[Path], questions: list[ParsedQuestion], image_dir: Path, prefix: str) -> list[ParsedImage]:
    image_dir.mkdir(parents=True, exist_ok=True)
    by_page: dict[int, list[int]] = {}
    for question in questions:
        if question.page:
            by_page.setdefault(question.page, []).append(question.number)

    images: list[ParsedImage] = []
    saved = 0
    for path in paths:
        try:
            doc = fitz.open(path)
        except Exception:
            continue
        positions_by_page = question_positions_for_doc(doc, by_page)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            page_number = page_index + 1
            page_area = page.rect.width * page.rect.height
            for image_info in page.get_images(full=True):
                xref = image_info[0]
                rects = page.get_image_rects(xref)
                if not rects:
                    continue
                rect = rects[0]
                question_number = question_for_image(page_number, rect.y0, positions_by_page, by_page)
                if not question_number:
                    continue
                image_area = rect.width * rect.height
                if image_area <= 400 or rect.width < 40 or rect.height < 40 or image_area / page_area > 0.45:
                    continue
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.alpha:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    saved += 1
                    filename = f"{prefix}_q{question_number:02d}_{saved}.png"
                    pix.save(image_dir / filename)
                    images.append(ParsedImage(question_number=question_number, filename=filename, source_page=page_number, label="embedded"))
                except Exception:
                    continue
        doc.close()
    return images


def question_positions_for_doc(doc: fitz.Document, valid_by_page: dict[int, list[int]]) -> dict[int, list[tuple[int, float]]]:
    positions: dict[int, list[tuple[int, float]]] = {}
    marker_pattern = re.compile(r"QUEST[ÃA]O\s*0?(\d{1,2})", re.IGNORECASE)
    numbered_pattern = re.compile(r"^\s*(\d{1,2})\s*(?:[\.)-]\s+|[ \t]+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]))")
    # Número da questão sozinho na linha (caixa preta à esquerda, separado do enunciado).
    standalone_pattern = re.compile(r"^0?(\d{1,2})$")
    for page_index in range(doc.page_count):
        page = doc[page_index]
        valid_numbers = set(valid_by_page.get(page_index + 1, []))
        if not valid_numbers:
            continue
        try:
            data = page.get_text("dict")
        except Exception:
            continue
        page_positions: list[tuple[int, float]] = []
        for block in data.get("blocks", []):
            for line in block.get("lines", []):
                text = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
                if not text:
                    continue
                match = marker_pattern.search(text) or numbered_pattern.match(text)
                number = None
                if match:
                    number = int(match.group(1))
                else:
                    standalone = standalone_pattern.match(text)
                    # Só aceita número isolado se estiver na margem esquerda (a caixa
                    # do número fica à esquerda); evita casar com números soltos do texto.
                    x0 = float(line.get("bbox", [999, 0, 0, 0])[0])
                    if standalone and x0 < 80:
                        number = int(standalone.group(1))
                if number is None or number not in valid_numbers:
                    continue
                page_positions.append((number, float(line.get("bbox", [0, 0, 0, 0])[1])))
        if page_positions:
            deduped: dict[int, float] = {}
            for number, y in sorted(page_positions, key=lambda item: item[1]):
                deduped.setdefault(number, y)
            positions[page_index + 1] = sorted(deduped.items(), key=lambda item: item[1])
    return positions


def question_for_image(
    page_number: int,
    image_y: float,
    positions_by_page: dict[int, list[tuple[int, float]]],
    by_page: dict[int, list[int]],
) -> int | None:
    positions = positions_by_page.get(page_number, [])
    if positions:
        previous = [number for number, y in positions if y <= image_y + 3]
        if previous:
            return previous[-1]
        return positions[0][0]
    return question_for_page(page_number, by_page)


def question_for_page(page_number: int, by_page: dict[int, list[int]]) -> int | None:
    numbers = by_page.get(page_number)
    if numbers:
        return min(numbers)
    previous_pages = [page for page in by_page if page <= page_number]
    if not previous_pages:
        return None
    return max(by_page[max(previous_pages)])


def parse_exam_sources(
    exam_paths: list[Path],
    answer_path: Path | None,
    *,
    year: str,
    variant: str = "",
    image_dir: Path,
    progress=None,
) -> ParsedExam:
    notes: list[str] = []
    pages = page_texts_for_paths(exam_paths)
    questions, split_notes = split_questions(pages)
    notes.extend(split_notes)

    answers: dict[int, str] = {}
    if answer_path:
        answer_text, used_ocr = extract_answer_text(answer_path)
        if used_ocr:
            notes.append("Gabarito extraído por OCR.")
        answers = parse_answer_key_text(answer_text, variant=variant)
        if len(answers) < 60:
            notes.append(f"Baixa confiança no gabarito: {len(answers)} respostas detectadas.")
    else:
        notes.append("Gabarito não informado.")

    for question in questions:
        answer = answers.get(question.number, "")
        question.extracted_answer = answer
        question.answer_confidence = 1.0 if answer else 0.0

    # Corrige a página de cada questão pela posição VISUAL do número no PDF.
    # Mais robusto que o offset no texto concatenado, que pode desalinhar com o
    # layout (ex.: 2014 Q10 caía na pág 4 sendo física da pág 5).
    fix_question_pages(questions, exam_paths)

    image_prefix = slugify(f"{year}-{variant or 'principal'}")
    images = extract_images(exam_paths, questions, image_dir, image_prefix, progress)
    if not images:
        notes.append("Nenhuma imagem embutida associável a questões foi detectada.")

    return ParsedExam(questions=questions, images=images, answers=answers, notes=notes)


def discover_source_groups(root: Path = DEFAULT_SOURCE_DIR, year: str | None = None) -> list[SourceGroup]:
    if not root.exists():
        return []
    year_dirs = [path for path in root.iterdir() if path.is_dir() and path.name.isdigit()]
    if year:
        year_dirs = [path for path in year_dirs if path.name == str(year)]
    groups: list[SourceGroup] = []
    for year_dir in sorted(year_dirs, key=lambda item: item.name):
        pdfs = sorted(year_dir.glob("*.pdf"))
        answer = next((path for path in pdfs if "gabarito" in path.name.lower()), None)
        cadernos = [path for path in pdfs if "caderno" in path.name.lower()]
        unmarked = [path for path in cadernos if "marcado" not in path.name.lower()]
        if unmarked:
            cadernos = unmarked
        if not cadernos:
            continue

        tipo1 = [path for path in cadernos if re.search(r"tipo[_-]?1", path.name.lower())]
        tipo2 = [path for path in cadernos if re.search(r"tipo[_-]?2", path.name.lower())]
        if tipo1 or tipo2:
            for variant, paths in [("Tipo 1", tipo1), ("Tipo 2", tipo2)]:
                if paths:
                    groups.append(SourceGroup(year=year_dir.name, title=f"POSCOMP {year_dir.name} {variant}", variant=variant, exam_paths=paths, answer_path=answer))
            continue

        area_paths = [path for path in cadernos if any(name in path.name.lower() for name in ["matematica", "fundamentos", "tecnologia"])]
        if area_paths:
            order = {"matematica": 0, "fundamentos": 1, "tecnologia": 2}
            area_paths.sort(key=lambda path: next((rank for key, rank in order.items() if key in path.name.lower()), 99))
            groups.append(SourceGroup(year=year_dir.name, title=f"POSCOMP {year_dir.name}", variant="", exam_paths=area_paths, answer_path=answer))
            continue

        groups.append(SourceGroup(year=year_dir.name, title=f"POSCOMP {year_dir.name}", variant="", exam_paths=cadernos[:1], answer_path=answer))
    return groups


def build_export_payload(exam: dict, questions: list[dict], images: list[dict]) -> dict:
    return {
        "schema_version": 1,
        "exam": exam,
        "questions": questions,
        "images": images,
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_extract_zip_member(target_dir: Path, filename: str, data: bytes) -> Path:
    target = (target_dir / filename).resolve()
    if not str(target).startswith(str(target_dir.resolve())):
        raise ValueError(f"Caminho inseguro no pacote: {filename}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def copy_uploaded_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
