"""Classificação automática de questões por Área → Tema → Subtópico via Ollama.

Os rótulos válidos vêm de ``taxonomy.json`` (Anexo I do edital POSCOMP). O modelo
nunca inventa rótulos: a saída é validada contra a taxonomia e, quando o par
(área, tema) ou o subtópico não bate, o resultado é corrigido/rebaixado em vez de
ser aceito cru.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


TAXONOMY_PATH = Path(__file__).resolve().parent / "taxonomy.json"

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:12b")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "180"))
# Janela de contexto do Ollama. O default do servidor (4096) raspa o teto no pior caso
# (taxonomia ~2.9k tokens + texto + até 3 imagens ≈ 4k); 6144 cobre com folga medida.
OLLAMA_NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX", "6144"))


def _load_taxonomy() -> dict:
    return json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))


_TAXONOMY = _load_taxonomy()
AREAS: list[str] = list(_TAXONOMY.keys())
TEMAS_BY_AREA: dict[str, list[str]] = {area: list(data["temas"].keys()) for area, data in _TAXONOMY.items()}
ALL_TEMAS: list[str] = [tema for temas in TEMAS_BY_AREA.values() for tema in temas]
AREA_BY_TEMA: dict[str, str] = {tema: area for area, temas in TEMAS_BY_AREA.items() for tema in temas}
SUBTOPICS_BY_TEMA: dict[str, list[str]] = {
    tema: list(subs) for data in _TAXONOMY.values() for tema, subs in data["temas"].items()
}


def _taxonomy_text() -> str:
    lines: list[str] = []
    for area, data in _TAXONOMY.items():
        lines.append(f"# ÁREA: {area}")
        for tema, subs in data["temas"].items():
            lines.append(f"  TEMA: {tema}")
            lines.append("    subtópicos: " + "; ".join(subs))
    return "\n".join(lines)


_TAXONOMY_TEXT = _taxonomy_text()

SYSTEM_PROMPT = (
    "Você é um classificador de questões da prova POSCOMP. Receberá uma questão em DUAS partes — "
    "o TEXTO extraído (enunciado e alternativas, que pode conter erros de OCR) e a IMAGEM do recorte "
    "original (que preserva fórmulas, código, tabelas e figuras) — além de uma taxonomia oficial com "
    "Área → Tema → Subtópicos. Use as duas partes em conjunto: combine o texto e a imagem para "
    "entender a questão. Escolha EXATAMENTE um rótulo de cada nível, copiando o texto literal da "
    "taxonomia (sem inventar, sem traduzir, sem abreviar). O tema deve pertencer à área escolhida e o "
    "subtópico ao tema escolhido. Responda apenas com o JSON pedido."
)


@dataclass
class ClassifyResult:
    area: str = ""
    tema: str = ""
    subtopic: str = ""
    confidence: float = 0.0
    note: str = ""
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error and bool(self.tema)


def _output_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "area": {"type": "string", "enum": AREAS},
            "tema": {"type": "string", "enum": ALL_TEMAS},
            "subtopico": {"type": "string"},
        },
        "required": ["area", "tema", "subtopico"],
    }


def question_text(question: dict) -> str:
    parts: list[str] = []
    statement = (question.get("statement") or "").strip()
    if statement:
        parts.append(f"Enunciado:\n{statement}")
    for letter in "ABCDE":
        text = (question.get(f"alternative_{letter.lower()}") or "").strip()
        if text:
            parts.append(f"({letter}) {text}")
    return "\n".join(parts)


def _post(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_HOST + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _validate(parsed: dict) -> ClassifyResult:
    tema = (parsed.get("tema") or "").strip()
    area = (parsed.get("area") or "").strip()
    subtopic = (parsed.get("subtopico") or "").strip()

    if tema not in AREA_BY_TEMA:
        return ClassifyResult(error=f"Tema fora da taxonomia: {tema!r}")

    confidence = 1.0
    notes: list[str] = []
    real_area = AREA_BY_TEMA[tema]
    if area != real_area:
        area = real_area  # confia no tema e corrige a área
        confidence = min(confidence, 0.7)
        notes.append("área corrigida pelo tema")
    if subtopic not in SUBTOPICS_BY_TEMA[tema]:
        subtopic = ""
        confidence = min(confidence, 0.6)
        notes.append("subtópico não reconhecido")
    return ClassifyResult(area=area, tema=tema, subtopic=subtopic, confidence=confidence, note="; ".join(notes))


def _encode_images(image_paths: list[Path] | None) -> list[str]:
    encoded: list[str] = []
    for path in image_paths or []:
        try:
            encoded.append(base64.b64encode(Path(path).read_bytes()).decode("ascii"))
        except OSError:
            continue
    return encoded


def classify_question(question: dict, image_paths: list[Path] | None = None) -> ClassifyResult:
    content = question_text(question)
    images = _encode_images(image_paths)
    if len(content.strip()) < 30 and not images:
        return ClassifyResult(error="Questão sem texto nem imagem para classificar")

    if images and content:
        # Duas partes: texto extraído + imagem do recorte original (anexada em user_message["images"]).
        question_block = (
            f"PARTE 1 — TEXTO EXTRAÍDO (pode ter erros de OCR):\n{content}\n\n"
            "PARTE 2 — IMAGEM: o recorte original da MESMA questão está anexado. "
            "Combine o texto e a imagem para classificar."
        )
    elif images:
        question_block = "PARTE 2 — IMAGEM: o enunciado e as alternativas estão na imagem anexada."
    else:
        question_block = f"TEXTO DA QUESTÃO:\n{content}"
    user_message: dict = {
        "role": "user",
        "content": f"TAXONOMIA:\n{_TAXONOMY_TEXT}\n\nQUESTÃO:\n{question_block}",
    }
    if images:
        user_message["images"] = images

    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "think": False,  # saída estruturada: não precisa de raciocínio longo (deixa rápido/consistente)
        "format": _output_schema(),
        "options": {"temperature": 0, "num_ctx": OLLAMA_NUM_CTX},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            user_message,
        ],
    }
    data = _post("/api/chat", payload)
    raw = (data.get("message") or {}).get("content") or ""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return ClassifyResult(error=f"Resposta do modelo não é JSON: {raw[:200]!r}")
    return _validate(parsed)


def classify_with_retry(question: dict, image_paths: list[Path] | None = None, attempts: int = 2) -> ClassifyResult:
    """Classifica com retry. Erros de validação fazem nova tentativa; erros de rede
    sobem para o chamador decidir parar o lote (e retomar depois)."""
    last = ClassifyResult(error="sem tentativa")
    for _ in range(max(1, attempts)):
        last = classify_question(question, image_paths)
        if last.ok or last.error.startswith("Questão sem texto"):
            return last
    return last
