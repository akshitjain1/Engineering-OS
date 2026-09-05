"""The publisher runs alone, so it must not assume anything ran before it.

A column was added to day_journals with a migration that runs when the backend
starts. The publisher runs as its own process at *shutdown*, and on the first
evening after the change the backend had not restarted since -- so the column
did not exist, and the publisher died with

    sqlalchemy.exc.OperationalError: no such column: built

before printing a single line. The launcher logged "Publish did not complete
(exit 1)" and the day went unpublished.

"Some other process will have migrated it" is not an assumption a shutdown task
can make. The order is the wrong way round: shutdown comes before the next
startup, always.
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
PUBLISHER = BACKEND / "scripts" / "publish_study_activity.py"


def _database_without_the_column(tmp_path: Path) -> Path:
    """A database as it stands before the migration has ever run."""
    from sqlalchemy import create_engine

    from app.db import models  # noqa: F401  -- register tables
    from app.db.session import Base

    path = tmp_path / "old.db"
    engine = create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(bind=engine)
    engine.dispose()

    conn = sqlite3.connect(path)
    # SQLAlchemy created the current shape; take the column back out so this is
    # genuinely the old schema rather than a description of it.
    cols = [r[1] for r in conn.execute("pragma table_info(day_journals)")]
    if "built" in cols:
        conn.execute("ALTER TABLE day_journals DROP COLUMN built")
    conn.commit()
    remaining = [r[1] for r in conn.execute("pragma table_info(day_journals)")]
    conn.close()
    assert "built" not in remaining, "could not produce a pre-migration database"
    return path


def _run_publisher(db_path: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    return subprocess.run(
        [sys.executable, str(PUBLISHER)],  # dry run: touches no remote
        capture_output=True,
        text=True,
        cwd=BACKEND,
        env=env,
    )


def test_the_old_schema_reproduces_the_crash_without_the_guard(tmp_path):
    """Prove the fixture really is the broken state, not a hopeful one."""
    db_path = _database_without_the_column(tmp_path)
    conn = sqlite3.connect(db_path)
    try:
        try:
            conn.execute("select built from day_journals").fetchall()
        except sqlite3.OperationalError as exc:
            assert "no such column" in str(exc)
        else:
            raise AssertionError("the column is present; the fixture is wrong")
    finally:
        conn.close()


def test_the_publisher_runs_against_a_database_that_predates_the_column(tmp_path):
    """The whole point: it migrates what it needs before reading it."""
    result = _run_publisher(_database_without_the_column(tmp_path))

    assert "no such column" not in result.stderr, result.stderr
    assert result.returncode == 0, f"exit {result.returncode}\n{result.stderr}"


def test_it_adds_the_column_rather_than_working_around_it(tmp_path):
    """Skipping the field would hide the problem and publish nothing."""
    db_path = _database_without_the_column(tmp_path)
    _run_publisher(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cols = [r[1] for r in conn.execute("pragma table_info(day_journals)")]
    finally:
        conn.close()
    assert "built" in cols, "the publisher read around the missing column instead of adding it"
