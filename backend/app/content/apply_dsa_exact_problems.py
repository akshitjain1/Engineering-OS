"""Write the verified DSA problem map into curriculum_resources.

Two things happen, and the second matters as much as the first:

* every verified problem becomes its own PRACTICE resource on the topic's
  lesson, carrying the canonical LeetCode title, number and difficulty;

* the NeetCode collection rows that used to serve as the topic's practice
  target are demoted -- `exactness` becomes COLLECTION, which is what they
  always were, and `role` becomes REFERENCE so `pick_resource` stops handing
  them to the DSA block. They are not deleted: a problem set is a perfectly
  good thing to browse, it was only ever wrong as *the* answer to "what am I
  solving today".

Facts come from data/dsa_problem_facts.json, written by verify_dsa_problems.
This module refuses to run if any entry is unverified, so a hand-edited map
cannot reach the database without passing the tag check first.

Idempotent and convergent: resources are keyed by slug and updated in place,
and any row this module owns that the map no longer lists is retired, so the
database ends up matching the map rather than accumulating whatever it has ever
contained.

    python -m app.content.apply_dsa_exact_problems [--dry-run]
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content.dsa_exact_problems import DSA_EXACT_PROBLEMS
from app.content.verify_dsa_problems import CACHE, audit
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic
from app.db.session import SessionLocal

#: The collection pages that used to stand in for exact practice.
COLLECTION_URLS = (
    "https://neetcode.io/practice/practice/neetcode150",
    "https://neetcode.io/practice/practice/coreSkills",
)

#: Exact problems sort ahead of anything already on the lesson.
FIRST_ORDER_INDEX = 10

#: Completion values that mean real work happened against a row.
DONE_STATUSES = {"complete", "completed", "done"}

MINUTES_BY_DIFFICULTY = {"Easy": 15, "Medium": 25, "Hard": 40}


def _resource_slug(topic_slug: str, problem_slug: str) -> str:
    # 160 chars in the column; the longest real pair is far below that.
    return f"{topic_slug}--lc-{problem_slug}"[:160]


def _lesson_for(db: Session, topic: CurriculumTopic) -> CurriculumLesson | None:
    return db.execute(
        select(CurriculumLesson)
        .where(CurriculumLesson.topic_id == topic.id)
        .order_by(CurriculumLesson.order_index, CurriculumLesson.id)
    ).scalars().first()


def apply(db: Session, *, dry_run: bool = False) -> dict[str, int]:
    facts = json.loads(CACHE.read_text(encoding="utf-8"))
    failures = audit(facts)
    if failures:
        raise SystemExit(
            f"refusing to write: {len(failures)} unverified or mis-tagged entries.\n"
            "Run: python -m app.content.verify_dsa_problems"
        )

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    stats = {
        "created": 0,
        "updated": 0,
        "demoted": 0,
        "skipped_no_lesson": 0,
        "retired_deleted": 0,
        "retired_hidden": 0,
    }

    for topic_slug, spec in DSA_EXACT_PROBLEMS.items():
        topic = db.execute(
            select(CurriculumTopic).where(CurriculumTopic.slug == topic_slug)
        ).scalar_one_or_none()
        if topic is None:
            continue
        lesson = _lesson_for(db, topic)
        if lesson is None:
            stats["skipped_no_lesson"] += 1
            continue

        for position, (problem_slug, expected_tags, why) in enumerate(spec["problems"]):
            fact = facts[problem_slug]
            slug = _resource_slug(topic_slug, problem_slug)
            row = db.execute(
                select(CurriculumResource).where(CurriculumResource.slug == slug)
            ).scalar_one_or_none()
            existed = row is not None
            if row is None:
                row = CurriculumResource(slug=slug)
                db.add(row)

            row.title = f"{fact['number']}. {fact['title']}"
            row.url = fact["url"]
            row.resource_type = "coding_problem"
            row.provider = "LeetCode"
            row.difficulty = fact["difficulty"]
            row.description = why
            row.notes = spec["technique"]
            row.official_unofficial = "official"
            row.order_index = FIRST_ORDER_INDEX + position
            row.lesson_id = lesson.id
            row.role = "PRACTICE"
            row.exactness = "EXACT"
            row.verification_status = "VERIFIED"
            row.estimated_minutes = MINUTES_BY_DIFFICULTY.get(fact["difficulty"], 25)
            row.required_concepts_covered = sorted(set(expected_tags) & set(fact["tags"]))
            row.estimate_confidence = "MEDIUM"
            row.estimate_method = "difficulty_band"
            row.verification_evidence = json.dumps(
                {
                    "source": "leetcode graphql questionData",
                    "checked_at": now,
                    "difficulty": fact["difficulty"],
                    "paid_only": fact["paid_only"],
                    "leetcode_tags": fact["tags"],
                    "claimed_tags": sorted(expected_tags),
                },
                sort_keys=True,
            )
            row.last_verified_at = now
            row.learner_visible = True
            row.visibility_class = "LEARNER"
            if not existed:
                row.completion_status = "not_started"
            stats["updated" if existed else "created"] += 1

    # Retire rows this module owns that the map no longer lists.
    #
    # Without this the writer is additive, and that made it useless as a
    # correction path: dropping a problem from the map left its row in place --
    # still PRACTICE, still EXACT, still learner-visible -- so the topic went on
    # offering a problem the map had already rejected, and the freed order_index
    # collided with whatever replaced it.
    for topic_slug, spec in DSA_EXACT_PROBLEMS.items():
        prefix = f"{topic_slug}--lc-"
        keep = {_resource_slug(topic_slug, problem[0]) for problem in spec["problems"]}
        owned = [
            row
            for row in db.execute(
                select(CurriculumResource)
                .join(CurriculumLesson, CurriculumLesson.id == CurriculumResource.lesson_id)
                .join(CurriculumTopic, CurriculumTopic.id == CurriculumLesson.topic_id)
                .where(CurriculumTopic.slug == topic_slug)
            ).scalars()
            if (row.slug or "").startswith(prefix)
        ]
        for row in owned:
            if row.slug in keep:
                continue
            if (row.completion_status or "").lower() in DONE_STATUSES:
                # Work already done stays on the record; it just stops being
                # offered. Deleting it would silently erase solved problems.
                row.learner_visible = False
                row.visibility_class = "ARCHIVED"
                stats["retired_hidden"] += 1
            else:
                db.delete(row)
                stats["retired_deleted"] += 1
    db.flush()

    # Demote the collections. Same query the day engine walks, so nothing that
    # feeds a DSA block is missed.
    rows = db.execute(
        select(CurriculumResource)
        .join(CurriculumLesson, CurriculumLesson.id == CurriculumResource.lesson_id)
        .join(CurriculumTopic, CurriculumTopic.id == CurriculumLesson.topic_id)
        .where(
            CurriculumTopic.domain_key == "dsa",
            CurriculumResource.url.in_(COLLECTION_URLS),
        )
    ).scalars().all()
    for row in rows:
        if row.role == "PRACTICE" or row.exactness == "EXACT":
            row.role = "REFERENCE"
            row.exactness = "COLLECTION"
            row.notes = (
                "Problem set, not a single problem. Demoted from PRACTICE/EXACT: the "
                "day's DSA block needs one named problem, which now comes from "
                "dsa_exact_problems."
            )
            stats["demoted"] += 1

    if dry_run:
        db.rollback()
    else:
        db.commit()
    return stats


def refresh_open_plan_items(db: Session, *, dry_run: bool = False) -> int:
    """Re-point today's unfinished DSA blocks at the resource that now wins.

    daily_plan_items denormalises the chosen resource, so fixing the curriculum
    alone leaves the block a learner is looking at right now still pointing at
    yesterday's answer. Finished and skipped blocks are left alone: what they
    recorded is history, not a stale pointer.
    """
    from app.learning.day_engine import ACTIVITY_DSA, pick_resource, resources_for_topics
    from app.learning.day_models import DailyPlanItem

    items = db.execute(
        select(DailyPlanItem)
        .join(CurriculumTopic, CurriculumTopic.id == DailyPlanItem.topic_id)
        .where(
            DailyPlanItem.status.in_(("pending", "active")),
            DailyPlanItem.activity_type == ACTIVITY_DSA,
            CurriculumTopic.domain_key == "dsa",
        )
    ).scalars().all()
    if not items:
        return 0

    grouped = resources_for_topics(db, [i.topic_id for i in items])
    changed = 0
    for item in items:
        picked = pick_resource(grouped.get(item.topic_id, []), ACTIVITY_DSA)
        if picked is None or picked.url == item.resource_url:
            continue
        item.resource_id = picked.id
        item.resource_title = picked.title
        item.resource_provider = picked.provider
        item.resource_url = picked.url
        item.resource_kind = picked.resource_type
        changed += 1

    if dry_run:
        db.rollback()
    else:
        db.commit()
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        stats = apply(db, dry_run=args.dry_run)
        stats["plan_items_repointed"] = refresh_open_plan_items(db, dry_run=args.dry_run)
    finally:
        db.close()
    prefix = "[dry run] " if args.dry_run else ""
    print(prefix + ", ".join(f"{k}={v}" for k, v in stats.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
