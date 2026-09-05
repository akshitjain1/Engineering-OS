"""Post today's Engineering OS work into the study-activity repo.

That repo runs a bot at 18:00 UTC which turns `activity.json` into
`logs/<date>.md`, commits it, and then empties `activity.json` again. Filling
it by hand is the part nobody keeps doing, so the log ends up recording the
days you remembered rather than the days you worked -- and the contribution
graph records neither.

Engineering OS already knows exactly what you did. This hands it over.

    { "dsa": [...], "projects": [...], "learning": [...] }

Entries are keyed on the text before the em dash, and writing one replaces any
existing entry with the same key rather than appending. Opening and closing the
app three times in a day therefore leaves three identical-looking runs and one
line per topic, with the newest minute count. Anything in the file that is not
one of ours is left alone.

The working copy is a mirror, never a place to keep local edits: every run
resets it to origin before touching anything, so the bot's nightly reset can
never collide with this.

    python scripts/publish_study_activity.py              # dry run
    python scripts/publish_study_activity.py --apply
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.console import use_utf8  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.learning.streak import local_today  # noqa: E402

REMOTE = "https://github.com/akshitjain1/study-activity.git"
DEFAULT_CLONE = Path(
    os.environ.get("STUDY_ACTIVITY_REPO")
    or Path(os.environ.get("LOCALAPPDATA", Path.home())) / "EngineeringOS" / "study-activity"
)
ACTIVITY_FILE = "activity.json"
#: Kept in the order bot.py renders them. "journal" is ours -- the bot was
#: taught to read it, because a key it does not know would be dropped by the
#: reset it performs after writing the log.
BUCKETS = ("dsa", "projects", "learning", "journal")
SEPARATOR = " — "  # em dash, and the key boundary


def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def summarise_day(db, day: str) -> dict[str, list[str]]:
    """What today's finished blocks amount to, in the shape the bot renders.

    Built from completed plan items, so a block started and abandoned is not
    claimed. Problems are only listed for a topic actually finished today --
    the mapping marks them solved when the topic completes, so listing them for
    an unfinished topic would be reporting work that has not happened.
    """
    rows = db.execute(
        _sql(
            "select i.activity_type, i.title, i.topic_id, i.actual_minutes "
            "from daily_plan_items i "
            "where i.plan_date = :day and i.status = 'done'"
        ),
        {"day": day},
    ).fetchall()

    finished_today = {
        r[0]
        for r in db.execute(
            _sql(
                "select topic_id from user_progress "
                "where progress_state = 'completed' and topic_id is not null "
                "and date(last_activity_at) = :day"
            ),
            {"day": day},
        ).fetchall()
    }

    minutes: dict[int, int] = {}
    names: dict[int, str] = {}
    kinds: dict[int, str] = {}
    projects: list[str] = []

    for activity_type, title, topic_id, actual in rows:
        actual = actual or 0
        if activity_type == "BUILD":
            projects.append(f"{title}{SEPARATOR}{actual} min")
            continue
        if topic_id is None or activity_type not in ("LEARN", "PRACTICE", "DSA"):
            continue
        clean = title.split(": ", 1)[1] if title.startswith(("DSA: ", "Practice: ")) else title
        names.setdefault(topic_id, clean)
        minutes[topic_id] = minutes.get(topic_id, 0) + actual
        # One DSA block is enough to call the topic a DSA topic for the log.
        if activity_type == "DSA":
            kinds[topic_id] = "dsa"
        else:
            kinds.setdefault(topic_id, "learning")

    dsa: list[str] = []
    learning: list[str] = []
    # A problem pinned to two of the day's topics is still one problem solved.
    # Listing it under both would inflate the log, so the first topic keeps it.
    already_listed: set[str] = set()
    for topic_id, total in sorted(minutes.items()):
        entry = f"{names[topic_id]}{SEPARATOR}{total} min"
        if kinds[topic_id] == "dsa":
            if topic_id in finished_today:
                fresh = [p for p in _problems_for(db, topic_id) if p not in already_listed]
                already_listed.update(fresh)
                if fresh:
                    entry += f" (solved: {', '.join(fresh)})"
            dsa.append(entry)
        else:
            learning.append(entry)

    return {
        "dsa": sorted(dsa),
        "projects": sorted(projects) + _built(db, day),
        "learning": sorted(learning),
        "journal": _journal(db, day),
    }


#: The journal prompts, and how each reads as a line in a public daily log.
JOURNAL_FIELDS = (("learned", "Learned"), ("struggled", "Stuck on"), ("tomorrow", "Tomorrow"))


def _journal(db, day: str) -> list[str]:
    """The day's own words, one bullet per prompt.

    Newlines are collapsed: bot.py writes each entry as a single "- " bullet,
    so a multi-line answer would break out of the list and land as loose text
    under it.
    """
    row = db.execute(
        _sql(
            "select learned, struggled, tomorrow from day_journals "
            "where entry_date = :day"
        ),
        {"day": day},
    ).fetchone()
    if row is None:
        return []

    out = []
    for value, label in zip(row, [label for _, label in JOURNAL_FIELDS]):
        text = " ".join((value or "").split())
        if text:
            out.append(f"{label}{SEPARATOR}{text}")
    return out


def _built(db, day: str) -> list[str]:
    """Project or job work, for the log's own "projects" section.

    That section existed from the start and was almost always empty: it was fed
    only by BUILD blocks, which are rare, while the building that actually
    happens on a weekday happens at a job this app never sees. Now the day asks.
    """
    row = db.execute(
        _sql("select built from day_journals where entry_date = :day"),
        {"day": day},
    ).fetchone()
    text = " ".join((row[0] or "").split()) if row else ""
    return [f"Worked on{SEPARATOR}{text}"] if text else []


def _sql(text: str):
    from sqlalchemy import text as sa_text

    return sa_text(text)


def _problems_for(db, topic_id: int) -> list[str]:
    rows = db.execute(
        _sql(
            "select r.title from curriculum_resources r "
            "join curriculum_lessons l on l.id = r.lesson_id "
            "where l.topic_id = :tid and upper(coalesce(r.role,'')) = 'PRACTICE' "
            "and r.completion_status = 'completed' and r.url like '%leetcode.com/problems/%' "
            "order by r.order_index"
        ),
        {"tid": topic_id},
    ).fetchall()
    return [r[0] for r in rows]


def key_of(entry: str) -> str:
    return entry.split(SEPARATOR, 1)[0].strip()


def merge(existing: dict[str, Any], additions: dict[str, list[str]]) -> dict[str, list[str]]:
    """Ours replace ours; anything else in the file is untouched."""
    out: dict[str, list[str]] = {}
    for bucket in BUCKETS:
        current = [str(x) for x in (existing.get(bucket) or [])]
        new_keys = {key_of(e) for e in additions.get(bucket, [])}
        kept = [e for e in current if key_of(e) not in new_keys]
        out[bucket] = kept + additions.get(bucket, [])
    for extra_key, value in existing.items():
        if extra_key not in out:
            out[extra_key] = value
    return out


def ensure_clone(path: Path) -> None:
    if (path / ".git").exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and any(path.iterdir()):
        raise SystemExit(f"{path} exists but is not a git clone; move it aside")
    print(f"cloning {REMOTE} -> {path}")
    result = _run(["git", "clone", "--depth", "1", REMOTE, str(path)])
    if result.returncode != 0:
        raise SystemExit(f"clone failed:\n{result.stderr.strip()}")


def sync_to_origin(path: Path) -> str:
    """Throw away anything local. This copy is a mirror, not a workspace."""
    fetch = _run(["git", "fetch", "origin"], cwd=path)
    if fetch.returncode != 0:
        raise SystemExit(f"fetch failed:\n{fetch.stderr.strip()}")
    branch = (_run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path).stdout or "main").strip()
    reset = _run(["git", "reset", "--hard", f"origin/{branch}"], cwd=path)
    if reset.returncode != 0:
        raise SystemExit(f"reset failed:\n{reset.stderr.strip()}")
    return branch


def main(argv: list[str] | None = None) -> int:
    use_utf8()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="write, commit and push")
    parser.add_argument("--repo", type=Path, default=DEFAULT_CLONE)
    parser.add_argument("--day", help="YYYY-MM-DD (default: today)")
    args = parser.parse_args(argv)

    if not shutil.which("git"):
        print("git is not on PATH; nothing published.")
        return 0

    day = args.day or local_today()
    db = SessionLocal()
    try:
        additions = summarise_day(db, day)
    finally:
        db.close()

    total = sum(len(v) for v in additions.values())
    if total == 0:
        print(f"No finished blocks on {day} - nothing to publish.")
        return 0

    print(f"Engineering OS activity for {day}:")
    for bucket in BUCKETS:
        for entry in additions[bucket]:
            print(f"  {bucket:<9} {entry}")

    if not args.apply:
        print("\nDry run. Re-run with --apply to publish.")
        return 0

    ensure_clone(args.repo)
    branch = sync_to_origin(args.repo)

    target = args.repo / ACTIVITY_FILE
    existing = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    merged = merge(existing, additions)
    text = json.dumps(merged, indent=2, ensure_ascii=False) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") == text:
        print("\nAlready up to date - study-activity has today's work.")
        return 0
    target.write_text(text, encoding="utf-8")

    _run(["git", "add", ACTIVITY_FILE], cwd=args.repo)
    commit = _run(
        ["git", "commit", "-m", f"Study activity from Engineering OS ({day})"], cwd=args.repo
    )
    if commit.returncode != 0 and "nothing to commit" not in (commit.stdout or ""):
        raise SystemExit(f"commit failed:\n{commit.stdout}{commit.stderr}")

    push = _run(["git", "push", "origin", branch], cwd=args.repo)
    if push.returncode != 0:
        raise SystemExit(
            "push failed:\n"
            + (push.stderr or push.stdout).strip()
            + f"\n\nThe change is committed in {args.repo}; push it when you can."
        )
    print(f"\nPublished {total} entr{'y' if total == 1 else 'ies'} to study-activity.")
    print("The bot turns this into logs/<date>.md at 18:00 UTC (23:30 IST).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
