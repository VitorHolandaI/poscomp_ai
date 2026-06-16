"""Importa e publica todas as provas POSCOMP encontradas em Provas-POSCOMP.

Usado no build do Docker para deixar o banco/imagens prontos dentro da imagem.
Idempotente: se já houver provas no banco, não faz nada.
"""

from __future__ import annotations

from .db import ROOT_DIR, connect, init_db, utcnow

# Garante que var/images exista antes de importar main (StaticFiles valida o diretório no import).
for _directory in ("uploads", "images", "exports"):
    (ROOT_DIR / "var" / _directory).mkdir(parents=True, exist_ok=True)

from .extraction import DEFAULT_SOURCE_DIR, discover_source_groups  # noqa: E402
from .main import import_group  # noqa: E402


def seed() -> None:
    init_db()
    with connect() as conn:
        existing = conn.execute("SELECT COUNT(*) AS c FROM exams").fetchone()["c"]
    if existing:
        print(f"[seed] já existem {existing} provas, nada a fazer.")
        return

    groups = discover_source_groups(DEFAULT_SOURCE_DIR)
    if not groups:
        print("[seed] nenhuma prova encontrada em", DEFAULT_SOURCE_DIR)
        return

    for group in groups:
        exam_id = import_group(group)
        print(f"[seed] importada {group.title} -> exam_id={exam_id}")

    with connect() as conn:
        conn.execute("UPDATE exams SET status = 'published', updated_at = ?", (utcnow(),))
    print(f"[seed] {len(groups)} provas importadas e publicadas.")


if __name__ == "__main__":
    seed()
