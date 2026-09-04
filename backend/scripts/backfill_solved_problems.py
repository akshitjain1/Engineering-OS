"""Reconcile problems solved in one topic but still unsolved in another.

Solving a problem now marks it solved on every row that points at the same URL
(service.set_problem_solved). Rows that were already ticked before that existed
never spread, so a problem can still read "Mark solved" under a topic you have
not reached yet even though you solved it weeks ago -- which is the confusion
the change was made to remove, just aged.

Only problems are touched, and only ones already solved somewhere. Nothing is
marked solved that was not solved.

    python scripts/backfill_solved_problems.py            # dry run
    python scripts/backfill_solved_problems.py --apply
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.curriculum import is_lesson_complete  # noqa: E402
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic  # noqa: E402
from app.console import use_utf8  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.learning.service import is_coding_problem  # noqa: E402


def find(db) -> dict[str, list[tuple[str, CurriculumResource]]]:
    """URL -> the unsolved rows for a problem that is solved somewhere else."""
    rows = (
        db.query(CurriculumResource, CurriculumTopic.name)
        .join(CurriculumLesson, CurriculumLesson.id == CurriculumResource.lesson_id)
        .join(CurriculumTopic, CurriculumTopic.id == CurriculumLesson.topic_id)
        .all()
    )
    by_url: dict[str, list[tuple[str, CurriculumResource]]] = defaultdict(list)
    for resource, topic_name in rows:
        if is_coding_problem(resource):
            by_url[resource.url].append((topic_name, resource))

    pending: dict[str, list[tuple[str, CurriculumResource]]] = {}
    for url, entries in by_url.items():
        solved = [n for n, r in entries if is_lesson_complete(r.completion_status)]
        unsolved = [(n, r) for n, r in entries if not is_lesson_complete(r.completion_status)]
        if solved and unsolved:
            pending[url] = unsolved
    return pending


def main(argv: list[str] | None = None) -> int:
    use_utf8()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="write the change (default: dry run)")
    args = parser.parse_args(argv)

    db = SessionLocal()
    try:
        pending = find(db)
        if not pending:
            print("Nothing to reconcile — every solved problem reads solved everywhere.")
            return 0

        count = sum(len(v) for v in pending.values())
        print(f"{len(pending)} problem(s) solved somewhere still read unsolved on "
              f"{count} row(s):\n")
        for url, entries in sorted(pending.items()):
            print(f"  {url}")
            for topic_name, _ in sorted(entries):
                print(f"      still unsolved under: {topic_name}")

        if not args.apply:
            print("\nDry run. Re-run with --apply to write it.")
            return 0

        for entries in pending.values():
            for _, resource in entries:
                resource.completion_status = "completed"
        db.commit()
        print(f"\nMarked {count} row(s) solved.")

        left = find(db)
        print(f"Remaining after the write: {sum(len(v) for v in left.values())}")
        return 0 if not left else 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
