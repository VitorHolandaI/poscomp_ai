from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
VAR_DIR = ROOT_DIR / "var"
DB_PATH = VAR_DIR / "poscomp.sqlite3"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect() -> sqlite3.Connection:
    VAR_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT NOT NULL,
                title TEXT NOT NULL,
                variant TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'draft',
                source_kind TEXT NOT NULL DEFAULT 'local',
                source_paths TEXT NOT NULL DEFAULT '[]',
                answer_key_path TEXT NOT NULL DEFAULT '',
                extraction_notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
                number INTEGER NOT NULL,
                page INTEGER,
                statement TEXT NOT NULL DEFAULT '',
                alternative_a TEXT NOT NULL DEFAULT '',
                alternative_b TEXT NOT NULL DEFAULT '',
                alternative_c TEXT NOT NULL DEFAULT '',
                alternative_d TEXT NOT NULL DEFAULT '',
                alternative_e TEXT NOT NULL DEFAULT '',
                extracted_answer TEXT NOT NULL DEFAULT '',
                correct_answer TEXT NOT NULL DEFAULT '',
                answer_confidence REAL NOT NULL DEFAULT 0,
                raw_text TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(exam_id, number)
            );

            CREATE TABLE IF NOT EXISTS question_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                source_page INTEGER,
                label TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS simulados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS simulado_questions (
                simulado_id INTEGER NOT NULL REFERENCES simulados(id) ON DELETE CASCADE,
                position INTEGER NOT NULL,
                question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_questions_exam_number
                ON questions(exam_id, number);
            CREATE INDEX IF NOT EXISTS idx_question_images_question
                ON question_images(question_id);
            CREATE INDEX IF NOT EXISTS idx_simulado_questions_sim
                ON simulado_questions(simulado_id, position);
            """
        )
        _ensure_topic_columns(conn)


def _ensure_topic_columns(conn: sqlite3.Connection) -> None:
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(questions)")}
    columns = [
        ("area", "TEXT NOT NULL DEFAULT ''"),
        ("topic", "TEXT NOT NULL DEFAULT ''"),
        ("subtopic", "TEXT NOT NULL DEFAULT ''"),
        ("topic_confidence", "REAL NOT NULL DEFAULT 0"),
        ("topic_source", "TEXT NOT NULL DEFAULT ''"),
        ("marked_answer", "TEXT NOT NULL DEFAULT ''"),
    ]
    for name, ddl in columns:
        if name not in existing:
            conn.execute(f"ALTER TABLE questions ADD COLUMN {name} {ddl}")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic)")


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def loads(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback
