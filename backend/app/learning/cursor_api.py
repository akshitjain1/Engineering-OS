"""Where the learner is, independent of today's session.

/learn needs the current CORE topic for its "Continue" banner. It used to read
that off /api/day, which broke once GET /api/day became read-only: on a fresh
day there is no plan, so a catalog page showed no banner until the runner had
been opened.

/api/dashboard's focus.current carries the same topic and agrees with this
(both resolve to the CORE cursor), but it also creates user_xp and user_streaks
rows on first call and costs ~0.4s to assemble a ~10KB payload for four fields.
This is read-only and reads from day_engine.cursors -- the same source /today
and /dsa use, so all three surfaces name the same topic by construction.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import CurriculumTopic
from app.db.session import SessionLocal
from app.learning import day_engine

router = APIRouter()
DEFAULT_USER = "akshit"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _serialize(topic: Optional[CurriculumTopic]) -> Optional[dict[str, Any]]:
    if topic is None:
        return None
    return {
        "topic_id": topic.id,
        "slug": topic.slug,
        "name": topic.name,
        "domain": (getattr(topic, "domain_key", None) or "").lower() or None,
        "module_name": topic.module.name if topic.module else None,
        "estimated_minutes": topic.estimated_minutes or topic.total_training_minutes or 0,
    }


def read_cursors(db: Session, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    core, dsa, _completion = day_engine.cursors(db, user_id)
    return {"core": _serialize(core), "dsa": _serialize(dsa)}


@router.get("/api/cursor", tags=["Cursor"])
def cursor(db: Session = Depends(get_db)):
    """The next incomplete CORE and DSA topic. Never writes."""
    return read_cursors(db, user_id=DEFAULT_USER)
