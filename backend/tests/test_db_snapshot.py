"""The database snapshot is only a backup if it restores. So prove it, here.

`dev.db` is gitignored, so pushing the repo backs up none of your history. The
snapshot under `data/snapshot/` is what makes `git push` a real backup, and
these tests are what stop it quietly rotting into a directory of stale JSON
that nobody has ever fed back into a database.

Two things are checked:

* a full export -> restore round trip reproduces every row exactly, on a
  database built from the app's own models rather than a hand-written schema,
  so a new column added tomorrow is covered without touching this file;
* the snapshot committed in the repo is internally consistent -- every table in
  the manifest has a file, with the row count the manifest claims.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.export_db import CURRICULUM_TABLES, export
from scripts.restore_db import restore

BACKEND_DIR = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = BACKEND_DIR / "data" / "snapshot"


def _fingerprint(db_path: Path) -> dict[str, tuple[int, str]]:
    """Every table's row count and a hash of its contents, column order fixed."""
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    try:
        out: dict[str, tuple[int, str]] = {}
        tables = [
            r[0]
            for r in conn.execute(
                "select name from sqlite_master where type='table' "
                "and name not like 'sqlite_%' order by name"
            )
        ]
        for table in tables:
            cols = [r[1] for r in conn.execute(f'pragma table_info("{table}")')]
            order = ", ".join(f'"{c}"' for c in cols)
            statement = f"select {order} from \"{table}\" order by {order}"
            rows = [tuple(r) for r in conn.execute(statement)]
            blob = json.dumps(rows, default=str).encode()
            out[table] = (len(rows), hashlib.sha256(blob).hexdigest())
        return out
    finally:
        conn.close()


@pytest.fixture
def populated_db(tmp_path: Path) -> Path:
    """A database with the app's real schema and rows that stress a JSON trip.

    Built through SQLAlchemy's own metadata so this test tracks the models
    instead of a copy of them.
    """
    from sqlalchemy import create_engine

    from app.db import models  # noqa: F401  -- register tables
    from app.db.session import Base

    db_path = tmp_path / "source.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    engine.dispose()

    # Text, integers, a NULL, a timestamp and a unicode string -- the value
    # shapes a JSON round trip could plausibly mangle.
    conn = sqlite3.connect(db_path)
    conn.execute(
        "insert into curriculum_tracks (slug, name, description, order_index) "
        "values (?, ?, ?, ?)",
        ("dsa", "Data Structures — Algorithms ✓", None, 1),
    )
    conn.execute(
        "insert into user_progress (user_id, topic_id, progress_state, mastery_status, "
        "xp_earned, last_activity_at, streak_days, total_streak_days) "
        "values (?, ?, ?, ?, ?, ?, ?, ?)",
        ("akshit", None, "completed", "mastered", 40, "2026-09-02 19:18:00.123456", 2, 9),
    )
    conn.commit()
    conn.close()
    return db_path


def test_export_then_restore_reproduces_every_row(populated_db: Path, tmp_path: Path) -> None:
    out_dir = tmp_path / "snapshot"
    export(populated_db, out_dir)

    restored = tmp_path / "restored.db"
    restore(out_dir, restored)

    before, after = _fingerprint(populated_db), _fingerprint(restored)
    assert set(before) == set(after), "restore produced a different set of tables"
    differing = [t for t in before if before[t] != after[t]]
    assert not differing, f"tables changed across the round trip: {differing}"


def test_a_dangling_reference_still_restores(populated_db: Path, tmp_path: Path) -> None:
    """The disaster-day case: a backup must not refuse to open.

    Rows outlive the things they point at -- a topic gets retired, a plan item
    is deleted -- and any such reference is already in the source database. If
    restore treated that as fatal it would fail on exactly the day it is needed.
    """
    conn = sqlite3.connect(populated_db)
    conn.execute(
        "insert into user_progress (user_id, topic_id, progress_state, mastery_status, "
        "xp_earned, streak_days, total_streak_days) values (?, ?, ?, ?, ?, ?, ?)",
        ("akshit", 999_999, "completed", "mastered", 10, 1, 1),
    )
    conn.commit()
    conn.close()

    out_dir = tmp_path / "snapshot"
    export(populated_db, out_dir)
    restored = tmp_path / "restored.db"
    restore(out_dir, restored)

    check = sqlite3.connect(f"file:{restored.as_posix()}?mode=ro", uri=True)
    try:
        assert check.execute("select count(*) from user_progress").fetchone()[0] == 2
    finally:
        check.close()


def test_export_is_deterministic(populated_db: Path, tmp_path: Path) -> None:
    """Two exports of an unchanged database must be byte-identical.

    Otherwise every commit carries a diff nobody can read, and a real change
    becomes invisible in the noise.
    """
    a, b = tmp_path / "a", tmp_path / "b"
    export(populated_db, a)
    export(populated_db, b)
    for path in sorted(a.rglob("*")):
        if path.is_file():
            twin = b / path.relative_to(a)
            assert twin.read_bytes() == path.read_bytes(), f"{path.name} differs between exports"


def test_restore_refuses_to_clobber_without_force(populated_db: Path, tmp_path: Path) -> None:
    out_dir = tmp_path / "snapshot"
    export(populated_db, out_dir)
    target = tmp_path / "existing.db"
    target.write_bytes(b"not a database, but not mine to delete either")

    with pytest.raises(SystemExit):
        restore(out_dir, target)
    assert target.read_bytes().startswith(b"not a database")

    restore(out_dir, target, force=True)
    assert _fingerprint(target)["curriculum_tracks"][0] == 1


def test_export_drops_files_for_tables_that_no_longer_exist(
    populated_db: Path, tmp_path: Path
) -> None:
    """A dropped table must not leave a file that restore would resurrect."""
    out_dir = tmp_path / "snapshot"
    export(populated_db, out_dir)
    orphan = out_dir / "progress" / "table_we_dropped.json"
    orphan.write_text("[]", encoding="utf-8")

    export(populated_db, out_dir)
    assert not orphan.exists()


def test_every_table_is_classified(populated_db: Path, tmp_path: Path) -> None:
    """Unlisted tables land in progress/, which is exported daily -- never dropped."""
    manifest = export(populated_db, tmp_path / "snapshot")
    for table, meta in manifest.items():
        expected = "curriculum" if table in CURRICULUM_TABLES else "progress"
        assert meta["dir"] == expected, f"{table} filed under {meta['dir']}"


@pytest.mark.skipif(not SNAPSHOT_DIR.exists(), reason="no snapshot committed yet")
def test_committed_snapshot_is_internally_consistent() -> None:
    """The snapshot in the repo is the actual backup. It must not be half-written."""
    manifest = json.loads((SNAPSHOT_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert manifest, "manifest.json is empty"
    assert (SNAPSHOT_DIR / "schema.sql").read_text(encoding="utf-8").strip(), "schema.sql is empty"

    for table, meta in manifest.items():
        path = SNAPSHOT_DIR / meta["dir"] / f"{table}.json"
        assert path.exists(), f"{table} is in the manifest but has no file"
        rows = json.loads(path.read_text(encoding="utf-8"))
        assert len(rows) == meta["rows"], (
            f"{table}: file has {len(rows)} rows, manifest claims {meta['rows']}"
        )


@pytest.mark.skipif(not SNAPSHOT_DIR.exists(), reason="no snapshot committed yet")
def test_committed_snapshot_actually_restores(tmp_path: Path) -> None:
    """End to end on the real data, not a fixture: this is the disaster drill."""
    restored = tmp_path / "from-repo.db"
    manifest = restore(SNAPSHOT_DIR, restored)

    conn = sqlite3.connect(f"file:{restored.as_posix()}?mode=ro", uri=True)
    try:
        for table, meta in manifest.items():
            count = conn.execute(f'select count(*) from "{table}"').fetchone()[0]
            assert count == meta["rows"], f"{table}: restored {count}, expected {meta['rows']}"
    finally:
        conn.close()


def test_a_crash_mid_export_leaves_the_previous_snapshot_intact(
    populated_db: Path, tmp_path: Path, monkeypatch
) -> None:
    """The snapshot is the backup, so a failed export must not damage it.

    Writing straight to the target truncates the good file first, so a crash in
    that window leaves a half-written file standing in for the backup. Caught
    for real once: an export running while the suite read the snapshot produced
    a JSONDecodeError in test_committed_snapshot_actually_restores.
    """
    from scripts import export_db

    out_dir = tmp_path / "snapshot"
    export(populated_db, out_dir)
    target = out_dir / "curriculum" / "curriculum_tracks.json"
    good = target.read_text(encoding="utf-8")
    assert json.loads(good), "fixture should have written a non-empty table"

    real_write_text = Path.write_text

    def explode(self, data, *args, **kwargs):
        if self.name.endswith(".tmp"):
            raise OSError("disk full, halfway through")
        return real_write_text(self, data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", explode)
    with pytest.raises(OSError):
        export_db._atomic_write(target, "brand new contents")

    assert target.read_text(encoding="utf-8") == good, (
        "a failed write destroyed the snapshot it was replacing"
    )
    assert json.loads(target.read_text(encoding="utf-8")) is not None


def test_export_leaves_no_temp_files_behind(populated_db: Path, tmp_path: Path) -> None:
    out_dir = tmp_path / "snapshot"
    export(populated_db, out_dir)
    assert not list(out_dir.rglob("*.tmp"))


def test_scripts_run_as_modules_from_the_backend_directory() -> None:
    """The launcher invokes these by path. A syntax error must fail the suite,
    not the first morning you open the app."""
    for script in ("export_db.py", "backup_db.py", "restore_db.py"):
        result = subprocess.run(
            [sys.executable, str(BACKEND_DIR / "scripts" / script), "--help"],
            capture_output=True,
            text=True,
            cwd=BACKEND_DIR,
        )
        assert result.returncode == 0, f"{script} --help failed: {result.stderr}"
