"""Mark work resources consumed on topics that were finished before the cascade existed.

`complete_topic` now marks a topic's PRIMARY and PRACTICE resources consumed,
because finishing a topic means you did the reading and the problems it sent
you to. Topics finished before that change still show "Not consumed" against
work that is demonstrably done, which is the same inconsistency one day older.

Only resources on topics already recorded as completed are touched, and only
the two roles that make up a topic's work -- the same rule the live code uses,
imported rather than restated so the two cannot drift.

    python scripts/backfill_completed_topic_resources.py            # dry run
    python scripts/backfill_completed_topic_resources.py --apply
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.models import (  # noqa: E402
    CurriculumLesson,
    CurriculumResource,
    CurriculumTopic,
    UserProgress,
)
from app.db.session import SessionLocal  # noqa: E402
from app.learning.service import DEFAULT_USER, TOPIC_WORK_ROLES, is_lesson_complete  # noqa: E402


def find(db, user_id: str) -> list[tuple[CurriculumTopic, CurriculumResource]]:
    completed = {
        row.topic_id
        for row in db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.progress_state == "completed",
            UserProgress.lesson_id.is_(None),
            UserProgress.topic_id.isnot(None),
        )
        .all()
    }
    if not completed:
        return []

    rows = (
        db.query(CurriculumTopic, CurriculumResource)
        .join(CurriculumLesson, CurriculumLesson.topic_id == CurriculumTopic.id)
        .join(CurriculumResource, CurriculumResource.lesson_id == CurriculumLesson.id)
        .filter(CurriculumTopic.id.in_(completed))
        .all()
    )
    return [
        (topic, resource)
        for topic, resource in rows
        if (resource.role or "").upper() in TOPIC_WORK_ROLES
        and getattr(resource, "learner_visible", True) is not False
        and not is_lesson_complete(resource.completion_status)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="write the change (default: dry run)")
    parser.add_argument("--user", default=DEFAULT_USER)
    args = parser.parse_args(argv)

    db = SessionLocal()
    try:
        pending = find(db, args.user)
        if not pending:
            print("Nothing to backfill — every finished topic's work is already consumed.")
            return 0

        print(f"{len(pending)} resource(s) on finished topics still read 'Not consumed':\n")
        for topic, resource in sorted(pending, key=lambda p: p[0].name or ""):
            print(f"  {topic.name:<28} {resource.role:<9} {resource.title}")

        if not args.apply:
            print("\nDry run. Re-run with --apply to write it.")
            return 0

        for _, resource in pending:
            resource.completion_status = "completed"
        db.commit()
        print(f"\nMarked {len(pending)} resource(s) consumed.")

        left = find(db, args.user)
        print(f"Remaining after the write: {len(left)}")
        return 0 if not left else 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
