"""Streak counts only meaningful learning days (local date)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import LearningActivity, UserStreak

DEFAULT_USER = "akshit"
DEFAULT_TZ = "Asia/Kolkata"
MIN_MINUTES = 30
IST = timezone(timedelta(hours=5, minutes=30))


def _zone(name: str | None):
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo(name or DEFAULT_TZ)
    except Exception:
        return IST


def local_today(timezone_name: str | None = None, now: datetime | None = None) -> str:
    tz = _zone(timezone_name)
    current = now.astimezone(tz) if now else datetime.now(tz)
    return current.date().isoformat()


def get_or_create_streak(db: Session, user_id: str = DEFAULT_USER) -> UserStreak:
    row = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
    if row:
        return row
    row = UserStreak(user_id=user_id, current_streak=0, longest_streak=0, last_learning_date=None)
    try:
        with db.begin_nested():
            db.add(row)
            db.flush()
        return row
    except IntegrityError:
        existing = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
        if existing:
            return existing
        raise


def day_is_meaningful(db: Session, local_date: str, user_id: str = DEFAULT_USER) -> bool:
    rows = (
        db.query(LearningActivity)
        .filter(LearningActivity.user_id == user_id, LearningActivity.local_date == local_date)
        .all()
    )
    minutes = sum(row.minutes or 0 for row in rows)
    if minutes >= MIN_MINUTES:
        return True
    types = {row.activity_type for row in rows}
    return bool(types & {"exercise", "assessment", "diagnostic"})


def _yesterday(iso_date: str) -> str:
    value = date.fromisoformat(iso_date)
    return (value - timedelta(days=1)).isoformat()


def refresh_streak_for_date(db: Session, local_date: str, user_id: str = DEFAULT_USER) -> UserStreak:
    streak = get_or_create_streak(db, user_id)
    if not day_is_meaningful(db, local_date, user_id):
        return streak
    if streak.last_learning_date == local_date:
        return streak
    if streak.last_learning_date == _yesterday(local_date):
        streak.current_streak = (streak.current_streak or 0) + 1
    else:
        streak.current_streak = 1
    streak.longest_streak = max(streak.longest_streak or 0, streak.current_streak)
    streak.last_learning_date = local_date
    db.flush()
    return streak


def record_activity(
    db: Session,
    *,
    activity_type: str,
    minutes: int = 0,
    source: str | None = None,
    local_date: str | None = None,
    timezone_name: str | None = None,
    user_id: str = DEFAULT_USER,
) -> UserStreak:
    day = local_date or local_today(timezone_name)
    db.add(
        LearningActivity(
            user_id=user_id,
            local_date=day,
            activity_type=activity_type,
            minutes=minutes,
            source=source,
        )
    )
    db.flush()
    return refresh_streak_for_date(db, day, user_id)


def serialize_streak(row: UserStreak) -> dict:
    return {
        "user_id": row.user_id,
        "current_streak": row.current_streak or 0,
        "longest_streak": row.longest_streak or 0,
        "last_learning_date": row.last_learning_date,
    }
