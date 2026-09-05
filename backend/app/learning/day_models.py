"""Durable daily-session items.

Why this table exists
--------------------
`DailyPlan.items` is a JSON blob. A blob cannot be started, completed, timed,
or resumed, so the UI had to keep "done" in React state, which is lost on
refresh. Every plan item now gets a row, an id, and a status. That single change
is what makes a guided session (start -> complete -> auto-advance) possible.

The table is additive. `daily_plans` keeps working exactly as before.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped

from app.db.session import Base

# Activity kinds. DSA is deliberately its own kind, not a flavour of PRACTICE,
# because it runs on its own cursor and must appear every single day.
ACTIVITY_REVIEW = "REVIEW"
ACTIVITY_LEARN = "LEARN"
ACTIVITY_PRACTICE = "PRACTICE"
ACTIVITY_DSA = "DSA"
ACTIVITY_BUILD = "BUILD"
ACTIVITY_REFLECT = "REFLECT"

ACTIVITY_TYPES = (
    ACTIVITY_REVIEW,
    ACTIVITY_LEARN,
    ACTIVITY_PRACTICE,
    ACTIVITY_DSA,
    ACTIVITY_BUILD,
    ACTIVITY_REFLECT,
)

STATUS_PENDING = "pending"
STATUS_ACTIVE = "active"
STATUS_DONE = "done"
STATUS_SKIPPED = "skipped"

OPEN_STATUSES = (STATUS_PENDING, STATUS_ACTIVE)


class DailyPlanItem(Base):
    """One block of work on one day. Ordered, resumable, and timed."""

    __tablename__ = "daily_plan_items"
    __table_args__ = (
        UniqueConstraint("user_id", "plan_date", "position", name="uq_day_item_position"),
        Index("ix_day_item_user_date", "user_id", "plan_date"),
    )

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    plan_date: Mapped[str] = Column(String(16), nullable=False, index=True)
    position: Mapped[int] = Column(Integer, nullable=False, default=0)

    activity_type: Mapped[str] = Column(String(20), nullable=False)
    title: Mapped[str] = Column(String(240), nullable=False)
    subtitle: Mapped[Optional[str]] = Column(String(240), nullable=True)
    why: Mapped[Optional[str]] = Column(Text, nullable=True)
    how: Mapped[Optional[str]] = Column(Text, nullable=True)

    topic_id: Mapped[Optional[int]] = Column(
        Integer, ForeignKey("curriculum_topics.id"), nullable=True, index=True
    )
    topic_slug: Mapped[Optional[str]] = Column(String(160), nullable=True)
    domain: Mapped[Optional[str]] = Column(String(40), nullable=True)

    resource_id: Mapped[Optional[int]] = Column(
        Integer, ForeignKey("curriculum_resources.id"), nullable=True
    )
    resource_title: Mapped[Optional[str]] = Column(String(300), nullable=True)
    resource_provider: Mapped[Optional[str]] = Column(String(120), nullable=True)
    resource_url: Mapped[Optional[str]] = Column(Text, nullable=True)
    resource_kind: Mapped[Optional[str]] = Column(String(40), nullable=True)

    planned_minutes: Mapped[int] = Column(Integer, nullable=False, default=20)
    actual_minutes: Mapped[int] = Column(Integer, nullable=False, default=0)

    status: Mapped[str] = Column(String(16), nullable=False, default=STATUS_PENDING, index=True)
    started_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    note: Mapped[Optional[str]] = Column(Text, nullable=True)

    created_at: Mapped[datetime] = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class DayJournal(Base):
    """One reflection note per day. Replaces the throwaway textarea on /journal."""

    __tablename__ = "day_journals"
    __table_args__ = (UniqueConstraint("user_id", "entry_date", name="uq_day_journal"),)

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    entry_date: Mapped[str] = Column(String(16), nullable=False, index=True)
    learned: Mapped[Optional[str]] = Column(Text, nullable=True)
    struggled: Mapped[Optional[str]] = Column(Text, nullable=True)
    tomorrow: Mapped[Optional[str]] = Column(Text, nullable=True)
    #: Project or job work done today. The study log has a "projects" section
    #: that had no way to be filled -- BUILD blocks are rare, and the work that
    #: actually happens on a weekday happens at a job this app never sees.
    built: Mapped[Optional[str]] = Column(Text, nullable=True)
    minutes_logged: Mapped[int] = Column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
