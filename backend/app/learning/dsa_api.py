"""Read-only DSA pattern board.

Built entirely from ``curriculum_topics`` where ``domain_key='dsa'``. The legacy
``dsa_topics`` table is empty and is deliberately not consulted here -- the table
and its model stay in place because ``user_progress.dsa_topic_id`` still points
at it.

Everything is bulk-queried. One pass for topics, one GROUP BY each for question
and exercise counts, one pass for resources. No per-topic queries.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import (
    CurriculumLesson,
    CurriculumModule,
    CurriculumSubject,
    CurriculumTopic,
    LessonExercise,
    LessonQuestion,
)
from app.db.session import SessionLocal
from app.learning import day_engine

router = APIRouter()
DEFAULT_USER = "akshit"
DSA_SUBJECT = "Data Structures & Algorithms"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _counts_by_topic(db: Session, model: Any, topic_ids: list[int]) -> dict[int, int]:
    """One GROUP BY for the whole board rather than a count per topic."""
    if not topic_ids:
        return {}
    rows = db.execute(
        select(CurriculumLesson.topic_id, func.count(model.id))
        .join(model, model.lesson_id == CurriculumLesson.id)
        .where(CurriculumLesson.topic_id.in_(topic_ids))
        .group_by(CurriculumLesson.topic_id)
    ).all()
    return {topic_id: count for topic_id, count in rows}


def build_board(db: Session, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    _core, dsa_cursor, completion = day_engine.cursors(db, user_id)

    rows = db.execute(
        select(CurriculumTopic, CurriculumModule)
        .join(CurriculumModule, CurriculumModule.id == CurriculumTopic.module_id)
        .join(CurriculumSubject, CurriculumSubject.id == CurriculumModule.subject_id)
        .where(
            func.lower(CurriculumTopic.domain_key) == day_engine.DSA_DOMAIN,
            CurriculumSubject.name == DSA_SUBJECT,
        )
        .order_by(
            CurriculumModule.order_index,
            CurriculumModule.id,
            CurriculumTopic.order_index,
            CurriculumTopic.id,
        )
    ).all()

    topic_ids = [topic.id for topic, _module in rows]
    question_counts = _counts_by_topic(db, LessonQuestion, topic_ids)
    exercise_counts = _counts_by_topic(db, LessonExercise, topic_ids)
    resources = day_engine.resources_for_topics(db, topic_ids)

    modules: list[dict[str, Any]] = []
    by_module: dict[int, dict[str, Any]] = {}
    completed_total = 0

    for topic, module in rows:
        bucket = by_module.get(module.id)
        if bucket is None:
            bucket = {
                "id": module.id,
                "name": module.name,
                "order_index": module.order_index,
                "topics": [],
            }
            by_module[module.id] = bucket
            modules.append(bucket)

        done = bool(completion.get(topic.slug))
        if done:
            completed_total += 1

        practice: Optional[dict[str, Any]] = None
        picked = day_engine.pick_resource(resources.get(topic.id, []), "PRACTICE")
        if picked is not None:
            practice = {
                "title": picked.title,
                "provider": picked.provider,
                "url": picked.url,
            }

        bucket["topics"].append(
            {
                "topic_id": topic.id,
                "slug": topic.slug,
                "name": topic.name,
                "completed": done,
                "estimated_minutes": topic.estimated_minutes
                or topic.total_training_minutes
                or 0,
                "question_count": question_counts.get(topic.id, 0),
                "exercise_count": exercise_counts.get(topic.id, 0),
                "practice": practice,
            }
        )

    cursor = None
    if dsa_cursor is not None:
        cursor = {
            "topic_id": dsa_cursor.id,
            "name": dsa_cursor.name,
            "slug": dsa_cursor.slug,
        }

    return {
        "cursor": cursor,
        "totals": {
            "topics": len(topic_ids),
            "completed": completed_total,
            "questions": sum(question_counts.values()),
            "exercises": sum(exercise_counts.values()),
        },
        "modules": modules,
    }


@router.get("/api/dsa/board", tags=["DSA"])
def read_board(db: Session = Depends(get_db)):
    """The pattern board: every DSA topic grouped by module, with practice links."""
    return build_board(db, user_id=DEFAULT_USER)
