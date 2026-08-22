"""Idempotent XP awards. Never call from GET handlers."""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import UserXP, XpEvent

DEFAULT_USER = "akshit"
XP_PER_LEVEL = 100

LESSON_COMPLETE_XP = 10
MASTERY_BONUS_XP = 25
DIAGNOSTIC_COMPLETE_XP = 15

EXERCISE_XP = {
    "beginner": 8,
    "easy": 8,
    "intermediate": 12,
    "medium": 12,
    "advanced": 18,
    "hard": 18,
}


def exercise_xp(difficulty: str | None) -> int:
    key = (difficulty or "intermediate").strip().lower()
    return EXERCISE_XP.get(key, 12)


def assessment_xp(score: float | None) -> int:
    if score is None:
        return 5
    if score >= 90:
        return 20
    if score >= 75:
        return 14
    if score >= 50:
        return 10
    return 6


def get_or_create_xp(db: Session, user_id: str = DEFAULT_USER) -> UserXP:
    rows = db.query(UserXP).filter(UserXP.user_id == user_id).order_by(UserXP.id).all()
    if rows:
        primary = rows[0]
        for duplicate in rows[1:]:
            primary.total_xp = (primary.total_xp or 0) + (duplicate.total_xp or 0)
            primary.xp_this_session = (primary.xp_this_session or 0) + (duplicate.xp_this_session or 0)
            primary.sessions_completed = (primary.sessions_completed or 0) + (duplicate.sessions_completed or 0)
            db.delete(duplicate)
        primary.level = max(1, ((primary.total_xp or 0) // XP_PER_LEVEL) + 1)
        return primary
    record = UserXP(user_id=user_id, total_xp=0, level=1, xp_this_session=0, sessions_completed=0)
    try:
        with db.begin_nested():
            db.add(record)
            db.flush()
        return record
    except IntegrityError:
        existing = db.query(UserXP).filter(UserXP.user_id == user_id).order_by(UserXP.id).first()
        if existing:
            return existing
        raise


def serialize_xp(record: UserXP) -> dict:
    return {
        "id": record.id,
        "user_id": record.user_id,
        "total_xp": record.total_xp,
        "level": record.level,
        "xp_this_session": record.xp_this_session,
        "sessions_completed": record.sessions_completed,
    }


def award_xp(
    db: Session,
    *,
    idempotency_key: str,
    amount: int,
    activity: str,
    user_id: str = DEFAULT_USER,
) -> tuple[int, UserXP]:
    if amount <= 0:
        return 0, get_or_create_xp(db, user_id)
    existing = (
        db.query(XpEvent)
        .filter(XpEvent.user_id == user_id, XpEvent.idempotency_key == idempotency_key)
        .first()
    )
    record = get_or_create_xp(db, user_id)
    if existing:
        return 0, record
    db.add(
        XpEvent(
            user_id=user_id,
            idempotency_key=idempotency_key,
            amount=amount,
            activity=activity,
        )
    )
    record.total_xp = (record.total_xp or 0) + amount
    record.xp_this_session = (record.xp_this_session or 0) + amount
    if activity in {"session", "session_complete"}:
        record.sessions_completed = (record.sessions_completed or 0) + 1
    record.level = max(1, (record.total_xp // XP_PER_LEVEL) + 1)
    db.flush()
    return amount, record
