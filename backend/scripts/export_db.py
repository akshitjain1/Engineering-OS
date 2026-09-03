"""Dump the whole database to committable JSON under backend/data/snapshot/.

Why this exists
---------------
`dev.db` is gitignored and so is `backups/`, which means pushing this repo to
GitHub backs up none of it. That is a trap: the push looks like a backup, and
the one file that cannot be recreated is the one file it leaves behind.

Nothing here is recoverable from elsewhere. `seed.py` builds a small demo
curriculum only -- it does not reproduce the 449 topics, 1,246 resources or
1,355 questions that were assembled by dozens of one-shot content scripts. Lose
dev.db and you lose both the curriculum and every completion, streak and review
date in it.

So this writes the entire database out as text that git can hold. Committing the
result makes `git push` a real off-machine backup, and `restore_db.py` turns it
back into a working database.

Layout
------
    data/snapshot/schema.sql              CREATE TABLE / CREATE INDEX statements
    data/snapshot/manifest.json           table -> row count, and where each lives
    data/snapshot/curriculum/<table>.json content: rarely changes, large
    data/snapshot/progress/<table>.json   your history: changes daily, small

The split is purely about how git stores them. Curriculum blobs are written
once and left alone, so day-to-day commits only carry the small progress files.

Determinism matters more than it looks: rows are ordered by primary key and
keys are sorted, so a day with no changes produces a byte-identical file and an
empty diff. A diff that is never empty is a diff nobody reads.

Usage:
    python scripts/export_db.py
    python scripts/export_db.py --db backups/dev-2026-09-02.db
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = BACKEND_DIR / "dev.db"
DEFAULT_OUT = BACKEND_DIR / "data" / "snapshot"

#: Tables holding authored content. Big, and only change when a content script
#: runs. Anything not listed is treated as your own history and exported to
#: progress/ -- erring toward the directory that is always written, because the
#: cost of a misfiled table is a noisier diff and the cost of a skipped one is
#: lost data.
CURRICULUM_TABLES = {
    "alembic_version",
    "curriculum_lessons",
    "curriculum_levels",
    "curriculum_modules",
    "curriculum_resources",
    "curriculum_subjects",
    "curriculum_topics",
    "curriculum_tracks",
    "dsa_topics",
    "engineering_projects",
    "lesson_exercises",
    "lesson_questions",
}


def _display(path: Path) -> str:
    """Path relative to backend/ when it is under it, else absolute.

    An --out-dir outside the repo is legitimate (a USB stick, a synced folder),
    and must not blow up on the summary line after the export already succeeded.
    """
    try:
        return str(path.relative_to(BACKEND_DIR))
    except ValueError:
        return str(path)


def _tables(conn: sqlite3.Connection) -> list[str]:
    return [
        r[0]
        for r in conn.execute(
            "select name from sqlite_master where type='table' "
            "and name not like 'sqlite_%' order by name"
        )
    ]


def _order_by(conn: sqlite3.Connection, table: str) -> str:
    """Stable ordering: primary key when there is one, else every column."""
    cols = list(conn.execute(f'pragma table_info("{table}")'))
    pk = [c[1] for c in sorted((c for c in cols if c[5] > 0), key=lambda c: c[5])]
    keys = pk or [c[1] for c in cols]
    return ", ".join(f'"{k}"' for k in keys)


def _rows(conn: sqlite3.Connection, table: str) -> list[dict]:
    conn.row_factory = sqlite3.Row
    cur = conn.execute(f'select * from "{table}" order by {_order_by(conn, table)}')
    return [dict(r) for r in cur]


def _atomic_write(path: Path, text: str) -> None:
    """Write via a temp file and one rename, so a reader never sees half a file.

    This is the backup. A plain write truncates the old contents first, and
    anything reading in that window -- the test that restores the committed
    snapshot, a `git add`, another export -- gets a partial file. A crash in
    that window leaves the truncated file *as* the backup, which is the one
    failure a backup cannot have. os.replace is atomic on Windows and POSIX.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _write(path: Path, payload: object) -> bool:
    """Write only when the bytes differ, so unchanged tables keep their mtime."""
    text = json.dumps(payload, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    _atomic_write(path, text)
    return True


def export(db_path: Path, out_dir: Path) -> dict:
    db_path = db_path.resolve()
    out_dir = out_dir.resolve()
    if not db_path.exists():
        raise SystemExit(f"database not found: {db_path}")

    # Read-only: an export must never be the thing that damages the original.
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    try:
        tables = _tables(conn)

        schema = [
            r[0]
            for r in conn.execute(
                "select sql from sqlite_master where sql is not null "
                "and name not like 'sqlite_%' "
                "order by case type when 'table' then 0 else 1 end, name"
            )
        ]
        schema_text = ";\n\n".join(s.strip() for s in schema) + ";\n"
        schema_path = out_dir / "schema.sql"
        if not schema_path.exists() or schema_path.read_text(encoding="utf-8") != schema_text:
            _atomic_write(schema_path, schema_text)

        manifest: dict[str, dict] = {}
        changed: list[str] = []
        stale = {p for p in out_dir.rglob("*.json") if p.name != "manifest.json"}

        for table in tables:
            where = "curriculum" if table in CURRICULUM_TABLES else "progress"
            rows = _rows(conn, table)
            path = out_dir / where / f"{table}.json"
            stale.discard(path)
            if _write(path, rows):
                changed.append(table)
            manifest[table] = {"rows": len(rows), "dir": where}
    finally:
        conn.close()

    # A table dropped from the schema must not leave a file behind that
    # restore_db.py would happily resurrect.
    for path in sorted(stale):
        path.unlink()
        print(f"  removed {path.relative_to(out_dir)} (table no longer exists)")

    _write(out_dir / "manifest.json", manifest)

    total = sum(m["rows"] for m in manifest.values())
    print(f"exported {len(tables)} tables, {total:,} rows -> {_display(out_dir)}")
    if changed:
        print("  changed: " + ", ".join(changed))
    else:
        print("  no table changed since the last export")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    export(args.db, args.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
