"""Rebuild a database from the JSON snapshot written by export_db.py.

An export that has never been restored is not a backup, it is a hope. This is
the other half, and `tests/test_db_snapshot.py` runs a full round trip on the
real database so the pair is checked on every test run rather than on the day
you need it.

By default it refuses to write over an existing file, because the moment you
reach for this is the moment you are least able to afford a wrong `--db`.

Usage:
    python scripts/restore_db.py --db restored.db          # new database
    python scripts/restore_db.py --db dev.db --force       # overwrite (careful)
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT = BACKEND_DIR / "data" / "snapshot"


def restore(snapshot_dir: Path, db_path: Path, force: bool = False) -> dict:
    snapshot_dir = snapshot_dir.resolve()
    db_path = db_path.resolve()
    manifest_path = snapshot_dir / "manifest.json"
    schema_path = snapshot_dir / "schema.sql"
    if not manifest_path.exists():
        raise SystemExit(f"no snapshot at {snapshot_dir} (missing manifest.json)")
    if db_path.exists() and not force:
        raise SystemExit(f"{db_path} already exists -- pass --force to overwrite it")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema_path.read_text(encoding="utf-8"))

        # Foreign keys are off by default in SQLite, which is what we want here:
        # tables are loaded in alphabetical order, not dependency order, so a
        # child can legitimately land before its parent. The integrity check at
        # the end is what confirms the finished database is sound.
        written = 0
        for table in sorted(manifest):
            rows = json.loads(
                (snapshot_dir / manifest[table]["dir"] / f"{table}.json").read_text(encoding="utf-8")
            )
            expected = manifest[table]["rows"]
            if len(rows) != expected:
                raise SystemExit(
                    f"{table}: snapshot file has {len(rows)} rows, manifest says {expected}"
                )
            if not rows:
                continue
            cols = list(rows[0])
            placeholders = ", ".join("?" for _ in cols)
            sql = (
                f'insert into "{table}" ({", ".join(chr(34) + c + chr(34) for c in cols)}) '
                f"values ({placeholders})"
            )
            conn.executemany(sql, [[r[c] for c in cols] for r in rows])
            written += len(rows)
        conn.commit()

        integrity = conn.execute("pragma integrity_check").fetchone()[0]
        if integrity != "ok":
            raise SystemExit(f"restored database failed integrity_check: {integrity}")
        # Reported, never fatal. A restore is a faithful copy, so any dangling
        # reference here was already in the source -- and the day you run this
        # is the worst possible day to be told your backup declines to open
        # because a row from months ago points at something deleted since.
        violations = conn.execute("pragma foreign_key_check").fetchall()
    finally:
        conn.close()

    print(f"restored {len(manifest)} tables, {written:,} rows -> {db_path}")
    if violations:
        tables = sorted({v[0] for v in violations})
        print(f"  integrity_check=ok  WARNING: {len(violations)} dangling "
              f"foreign key reference(s) in {', '.join(tables)} (present in the source too)")
    else:
        print("  integrity_check=ok  foreign_key_check=ok")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--force", action="store_true", help="overwrite --db if it exists")
    args = parser.parse_args(argv)
    restore(args.snapshot, args.db, args.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
