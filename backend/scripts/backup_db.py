"""Back up dev.db to backend/backups/dev-YYYY-MM-DD.db, keeping the 14 newest.

The entire learning history lives in one SQLite file. This uses the SQLite
online backup API rather than shutil.copy: a plain file copy taken while the
server is mid-write can capture a torn page or miss the -wal tail and produce a
backup that only fails when you finally need it. The backup API takes a
transactionally consistent snapshot of a live database, so this is safe to run
with the server up.

Usage:
    python -m scripts.backup_db                 # from backend/
    python scripts/backup_db.py                 # same thing
    python scripts/backup_db.py --keep 30       # keep more generations
    python scripts/backup_db.py --db other.db --out-dir somewhere/
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import date
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = BACKEND_DIR / "dev.db"
DEFAULT_OUT = BACKEND_DIR / "backups"
DEFAULT_KEEP = 14
STEM = "dev-"


def _table_count(conn: sqlite3.Connection, table: str) -> int | None:
    """Row count, or None when the table is absent."""
    try:
        return conn.execute(f"select count(*) from {table}").fetchone()[0]
    except sqlite3.Error:
        return None


def _display(path: Path) -> str:
    """Path relative to backend/ when it is under it, else absolute."""
    try:
        return str(path.relative_to(BACKEND_DIR))
    except ValueError:
        return str(path)


def backup(db_path: Path, out_dir: Path, keep: int = DEFAULT_KEEP) -> Path:
    # Resolve first: a caller passing a relative --out-dir must not blow up on
    # the display line, and sqlite needs a real path either way.
    db_path = db_path.resolve()
    out_dir = out_dir.resolve()
    if not db_path.exists():
        raise SystemExit(f"database not found: {db_path}")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{STEM}{date.today().isoformat()}.db"

    # Read-only on the source so a backup can never be the thing that corrupts
    # the original. Same-day runs overwrite, which is what "one per day" means.
    source = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    try:
        dest = sqlite3.connect(target)
        try:
            source.backup(dest)
        finally:
            dest.close()
    finally:
        source.close()

    print(f"backed up {db_path.name} -> {_display(target)} "
          f"({target.stat().st_size:,} bytes)")

    # Verify the copy actually opens and carries the data, rather than trusting
    # that the write returned without error.
    with sqlite3.connect(f"file:{target.as_posix()}?mode=ro", uri=True) as check:
        integrity = check.execute("pragma integrity_check").fetchone()[0]
        if integrity != "ok":
            raise SystemExit(f"backup failed integrity_check: {integrity}")
        rows = _table_count(check, "daily_plan_items")
    print(f"  integrity_check=ok  daily_plan_items={rows}")

    _prune(out_dir, keep)
    return target


def _prune(out_dir: Path, keep: int) -> None:
    """Keep the newest `keep` dated backups, delete the rest.

    Sorted by filename, which is safe because the name is an ISO date.
    """
    existing = sorted(out_dir.glob(f"{STEM}*.db"))
    stale = existing[:-keep] if keep > 0 else []
    for path in stale:
        path.unlink()
        print(f"  pruned {path.name}")
    print(f"  {len(existing) - len(stale)} backup(s) retained (keep={keep})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--keep", type=int, default=DEFAULT_KEEP)
    args = parser.parse_args(argv)
    backup(args.db, args.out_dir, args.keep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
