from .session import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class ProgressState(Enum):
    NOT_STARTED = "not_started"
    LEARNING = "learning"
    PRACTICING = "practicing"
    MASTERED = "mastered"
    FAST_TRACKED = "fast_tracked"
    NEEDS_REVISION = "needs_revision"


class Difficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ResourceType(Enum):
    YOUTUBE_VIDEO = "youtube_video"
    YOUTUBE_PLAYLIST = "youtube_playlist"
    DOCUMENTATION = "documentation"
    ARTICLE = "article"
    BOOK = "book"
    INTERACTIVE_TUTORIAL = "interactive_tutorial"
    GITHUB_REPO = "github_repo"
    EXERCISE = "exercise"
    CODING_PROBLEM = "coding_problem"


class CurriculumTrack(Base):
    __tablename__ = "curriculum_tracks"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    slug: Mapped[Optional[str]] = Column(String(160), nullable=True, unique=True, index=True)
    name: Mapped[str] = Column(String(100), nullable=False, unique=True)
    description: Mapped[str] = Column(Text, nullable=True)
    order_index: Mapped[int] = Column(Integer, default=0, nullable=False)

    subjects = relationship("CurriculumSubject", back_populates="track", cascade="all, delete-orphan")


class CurriculumLevel(Base):
    __tablename__ = "curriculum_levels"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    slug: Mapped[Optional[str]] = Column(String(160), nullable=True, unique=True, index=True)
    name: Mapped[str] = Column(String(50), nullable=False, unique=True)
    description: Mapped[str] = Column(Text, nullable=True)
    order_index: Mapped[int] = Column(Integer, default=0, nullable=False)

    subjects = relationship("CurriculumSubject", back_populates="level", cascade="all, delete-orphan")


class CurriculumSubject(Base):
    __tablename__ = "curriculum_subjects"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    slug: Mapped[Optional[str]] = Column(String(160), nullable=True, unique=True, index=True)
    name: Mapped[str] = Column(String(100), nullable=False, unique=True)
    description: Mapped[str] = Column(Text, nullable=True)
    track_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_tracks.id"), nullable=False)
    level_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_levels.id"), nullable=False)
    order_index: Mapped[int] = Column(Integer, default=0, nullable=False)

    track: Mapped["CurriculumTrack"] = relationship("CurriculumTrack", back_populates="subjects")
    level: Mapped["CurriculumLevel"] = relationship("CurriculumLevel", back_populates="subjects")
    modules = relationship("CurriculumModule", back_populates="subject", cascade="all, delete-orphan")


class CurriculumModule(Base):
    __tablename__ = "curriculum_modules"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    slug: Mapped[Optional[str]] = Column(String(160), nullable=True, unique=True, index=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    subject_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_subjects.id"), nullable=False)
    order_index: Mapped[int] = Column(Integer, default=0, nullable=False)

    subject: Mapped["CurriculumSubject"] = relationship("CurriculumSubject", back_populates="modules")
    topics = relationship("CurriculumTopic", back_populates="module", cascade="all, delete-orphan")


class CurriculumTopic(Base):
    __tablename__ = "curriculum_topics"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    slug: Mapped[Optional[str]] = Column(String(160), nullable=True, unique=True, index=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    module_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_modules.id"), nullable=False)
    order_index: Mapped[int] = Column(Integer, default=0, nullable=False)
    prerequisites: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    fast_trackable: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    # Product expansion (additive): planner tracks + depth targets
    learning_track: Mapped[str] = Column(String(20), default="CORE", nullable=False)
    depth_target: Mapped[str] = Column(String(30), default="WORKING_KNOWLEDGE", nullable=False)
    parallel_eligible: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    estimated_minutes: Mapped[Optional[int]] = Column(Integer, nullable=True)
    domain_key: Mapped[Optional[str]] = Column(String(60), nullable=True)

    module: Mapped["CurriculumModule"] = relationship("CurriculumModule", back_populates="topics")
    lessons = relationship("CurriculumLesson", back_populates="topic", cascade="all, delete-orphan")


class CurriculumLesson(Base):
    __tablename__ = "curriculum_lessons"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    slug: Mapped[Optional[str]] = Column(String(160), nullable=True, unique=True, index=True)
    title: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    topic_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_topics.id"), nullable=False)
    order_index: Mapped[int] = Column(Integer, default=0, nullable=False)
    completion_status: Mapped[str] = Column(String(20), default="not_started", nullable=False)
    mastery_status: Mapped[str] = Column(String(20), default="not_started", nullable=False)
    confidence: Mapped[float] = Column(Float, default=0.0, nullable=False)
    hours_estimated: Mapped[float] = Column(Float, default=1.0, nullable=False)

    topic: Mapped["CurriculumTopic"] = relationship("CurriculumTopic", back_populates="lessons")
    resources = relationship("CurriculumResource", back_populates="lesson", cascade="all, delete-orphan")
    questions = relationship("LessonQuestion", back_populates="lesson", cascade="all, delete-orphan")
    exercises = relationship("LessonExercise", back_populates="lesson", cascade="all, delete-orphan")
    progress_records = relationship("UserProgress", back_populates="lesson", cascade="all, delete-orphan")


class CurriculumResource(Base):
    __tablename__ = "curriculum_resources"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    slug: Mapped[Optional[str]] = Column(String(160), nullable=True, unique=True, index=True)
    title: Mapped[str] = Column(String(200), nullable=False)
    url: Mapped[str] = Column(String(500), nullable=False)
    resource_type: Mapped[str] = Column(String(50), nullable=False)
    provider: Mapped[Optional[str]] = Column(String(100), nullable=True)
    topic: Mapped[str] = Column(String(100), nullable=True)
    duration: Mapped[float] = Column(Float, nullable=True)
    difficulty: Mapped[str] = Column(String(20), nullable=True)
    description: Mapped[str] = Column(Text, nullable=True)
    official_unofficial: Mapped[str] = Column(String(10), default="official", nullable=False)
    order_index: Mapped[int] = Column(Integer, default=0, nullable=False)
    completion_status: Mapped[str] = Column(String(20), default="not_started", nullable=False)
    lesson_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_lessons.id"), nullable=True)
    role: Mapped[Optional[str]] = Column(String(20), nullable=True)
    section: Mapped[Optional[str]] = Column(String(200), nullable=True)
    lecture: Mapped[Optional[str]] = Column(String(200), nullable=True)
    video_id: Mapped[Optional[str]] = Column(String(40), nullable=True)
    verification_status: Mapped[str] = Column(String(20), default="UNRESOLVED", nullable=False)

    # --- Verification extension (additive, nullable, backward-compatible) ---
    estimated_minutes: Mapped[Optional[int]] = Column(Integer, nullable=True)
    required_concepts_covered: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    exactness: Mapped[Optional[str]] = Column(String(20), nullable=True)  # EXACT | MULTI_TOPIC | COLLECTION
    notes: Mapped[Optional[str]] = Column(Text, nullable=True)
    estimate_confidence: Mapped[Optional[str]] = Column(String(10), nullable=True)  # HIGH | MEDIUM | LOW
    estimate_method: Mapped[Optional[str]] = Column(String(40), nullable=True)
    verification_evidence: Mapped[Optional[str]] = Column(Text, nullable=True)  # JSON string
    last_verified_at: Mapped[Optional[str]] = Column(String(40), nullable=True)

    lesson: Mapped["CurriculumLesson"] = relationship("CurriculumLesson", back_populates="resources")


class LessonQuestion(Base):
    __tablename__ = "lesson_questions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    slug: Mapped[Optional[str]] = Column(String(160), nullable=True, unique=True, index=True)
    question: Mapped[str] = Column(Text, nullable=False)
    answer: Mapped[str] = Column(Text, nullable=True)
    explanation: Mapped[str] = Column(Text, nullable=True)
    difficulty: Mapped[str] = Column(String(20), nullable=True)
    topic: Mapped[str] = Column(String(100), nullable=True)
    source: Mapped[str] = Column(String(200), nullable=True)
    mastery_requirement: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    lesson_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_lessons.id"), nullable=False)
    options: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True)
    last_answer: Mapped[Optional[str]] = Column(Text, nullable=True)
    attempt_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    last_correct: Mapped[Optional[bool]] = Column(Boolean, nullable=True)
    last_attempt_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)

    lesson: Mapped["CurriculumLesson"] = relationship("CurriculumLesson", back_populates="questions")


class LessonExercise(Base):
    __tablename__ = "lesson_exercises"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    slug: Mapped[Optional[str]] = Column(String(160), nullable=True, unique=True, index=True)
    title: Mapped[str] = Column(String(200), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    difficulty: Mapped[str] = Column(String(20), nullable=True)
    topic: Mapped[str] = Column(String(100), nullable=True)
    completion_status: Mapped[str] = Column(String(20), default="not_started", nullable=False)
    solution_notes: Mapped[str] = Column(Text, nullable=True)
    time_taken: Mapped[float] = Column(Float, nullable=True)
    attempted_at: Mapped[datetime] = Column(DateTime, nullable=True)
    lesson_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_lessons.id"), nullable=False)
    exercise_type: Mapped[str] = Column(String(20), default="SELF_REFLECTION", nullable=False)
    correct_answer: Mapped[Optional[str]] = Column(Text, nullable=True)
    user_answer: Mapped[Optional[str]] = Column(Text, nullable=True)
    user_code: Mapped[Optional[str]] = Column(Text, nullable=True)
    user_explanation: Mapped[Optional[str]] = Column(Text, nullable=True)
    user_complexity: Mapped[Optional[str]] = Column(String(20), nullable=True)
    evaluated: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    # Explicit practice contract (additive)
    destination_type: Mapped[Optional[str]] = Column(String(40), nullable=True)
    destination_url: Mapped[Optional[str]] = Column(String(500), nullable=True)
    quantity: Mapped[Optional[int]] = Column(Integer, nullable=True)
    concepts_required: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    practice_instructions: Mapped[Optional[str]] = Column(Text, nullable=True)

    lesson: Mapped["CurriculumLesson"] = relationship("CurriculumLesson", back_populates="exercises")


class DSATopic(Base):
    __tablename__ = "dsa_topics"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    pattern: Mapped[str] = Column(String(50), nullable=True)
    difficulty: Mapped[str] = Column(String(20), nullable=True)
    source: Mapped[str] = Column(String(200), nullable=True)
    url: Mapped[str] = Column(String(500), nullable=True)
    solution_notes: Mapped[str] = Column(Text, nullable=True)
    attempt_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    time_taken: Mapped[float] = Column(Float, default=0.0, nullable=False)
    solved_status: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    revision_status: Mapped[str] = Column(String(20), default="not_started", nullable=False)
    last_attempted: Mapped[datetime] = Column(DateTime, nullable=True)
    next_revision: Mapped[datetime] = Column(DateTime, nullable=True)
    personal_notes: Mapped[str] = Column(Text, nullable=True)
    difficulty_level: Mapped[str] = Column(String(20), nullable=True)

    progress_records = relationship("UserProgress", back_populates="dsa_topic", cascade="all, delete-orphan")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit")
    lesson_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_lessons.id"), nullable=True)
    topic_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_topics.id"), nullable=True)
    dsa_topic_id: Mapped[int] = Column(Integer, ForeignKey("dsa_topics.id"), nullable=True)

    progress_state: Mapped[str] = Column(String(20), default="not_started", nullable=False)
    mastery_status: Mapped[str] = Column(String(20), default="not_started", nullable=False)
    xp_earned: Mapped[int] = Column(Integer, default=0, nullable=False)
    last_activity_at: Mapped[datetime] = Column(DateTime, nullable=True)
    streak_days: Mapped[int] = Column(Integer, default=0, nullable=False)
    total_streak_days: Mapped[int] = Column(Integer, default=0, nullable=False)

    lesson: Mapped["CurriculumLesson"] = relationship("CurriculumLesson", back_populates="progress_records")
    dsa_topic: Mapped["DSATopic"] = relationship("DSATopic", back_populates="progress_records")


class UserXP(Base):
    __tablename__ = "user_xp"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_xp_user_id"),)

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    total_xp: Mapped[int] = Column(Integer, default=0, nullable=False)
    level: Mapped[int] = Column(Integer, default=1, nullable=False)
    xp_this_session: Mapped[int] = Column(Integer, default=0, nullable=False)
    sessions_completed: Mapped[int] = Column(Integer, default=0, nullable=False)


class RevisionSchedule(Base):
    __tablename__ = "revision_schedules"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit")
    item_id: Mapped[int] = Column(Integer, nullable=False)
    item_type: Mapped[str] = Column(String(50), nullable=False)
    confidence: Mapped[float] = Column(Float, default=0.0, nullable=False)
    last_reviewed: Mapped[datetime] = Column(DateTime, nullable=True)
    next_review: Mapped[datetime] = Column(DateTime, nullable=False)
    review_interval: Mapped[int] = Column(Integer, default=1, nullable=False)

    __table_args__ = (
        Index("ix_revision_schedules_next_review", "next_review"),
        UniqueConstraint("user_id", "item_id", "item_type", name="uq_revision_user_item"),
    )


class TopicMastery(Base):
    """Topic-level mastery for the personal learning engine. Independent of lesson completion."""

    __tablename__ = "topic_mastery"
    __table_args__ = (UniqueConstraint("user_id", "topic_slug", name="uq_mastery_user_slug"),)

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    topic_id: Mapped[Optional[int]] = Column(Integer, ForeignKey("curriculum_topics.id"), nullable=True)
    topic_slug: Mapped[str] = Column(String(160), nullable=False, index=True)
    status: Mapped[str] = Column(String(20), default="UNKNOWN", nullable=False)
    mastery_score: Mapped[Optional[float]] = Column(Float, nullable=True)
    confidence: Mapped[float] = Column(Float, default=0.0, nullable=False)
    attempts: Mapped[int] = Column(Integer, default=0, nullable=False)
    last_assessed_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    last_completed_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    next_review_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    evidence: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    pace_mode: Mapped[str] = Column(String(20), default="FOUNDATION", nullable=False)
    has_implementation_evidence: Mapped[bool] = Column(Boolean, default=False, nullable=False)


class MasteryEvidence(Base):
    """One row per evidence register (user, topic, source, category).

    Re-writing a register replaces the row: current evidence, never cumulative
    history. Registers: lesson, exercise, diagnostic, assessment.
    """

    __tablename__ = "mastery_evidence"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    topic_slug: Mapped[str] = Column(String(160), nullable=False, index=True)
    source: Mapped[str] = Column(String(40), nullable=False)
    category: Mapped[str] = Column(String(40), nullable=False)
    score: Mapped[float] = Column(Float, nullable=False)
    payload: Mapped[Optional[dict[str, Any]]] = Column(JSON, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    status: Mapped[str] = Column(String(20), default="in_progress", nullable=False)
    question_ids: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    current_index: Mapped[int] = Column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    summary: Mapped[Optional[dict[str, Any]]] = Column(JSON, nullable=True)


class DiagnosticAnswer(Base):
    __tablename__ = "diagnostic_answers"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_diagnostic_answer"),)

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = Column(Integer, ForeignKey("diagnostic_sessions.id"), nullable=False)
    question_id: Mapped[str] = Column(String(80), nullable=False)
    payload: Mapped[Optional[dict[str, Any]]] = Column(JSON, nullable=True)
    score: Mapped[Optional[float]] = Column(Float, nullable=True)
    submitted_at: Mapped[datetime] = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class DailyPlan(Base):
    __tablename__ = "daily_plans"
    __table_args__ = (UniqueConstraint("user_id", "plan_date", name="uq_daily_plan_user_date"),)

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    plan_date: Mapped[str] = Column(String(16), nullable=False)
    budget_minutes: Mapped[int] = Column(Integer, nullable=False)
    goal: Mapped[str] = Column(String(200), default="Software Engineering + ML career readiness", nullable=False)
    items: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    generated_at: Mapped[datetime] = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class AssessmentSession(Base):
    """One run of a topic assessment. Scored once at completion."""

    __tablename__ = "assessment_sessions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    topic_id: Mapped[int] = Column(Integer, ForeignKey("curriculum_topics.id"), nullable=False, index=True)
    status: Mapped[str] = Column(String(20), default="in_progress", nullable=False)
    question_ids: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    current_index: Mapped[int] = Column(Integer, default=0, nullable=False)
    answers: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    started_at: Mapped[datetime] = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    summary: Mapped[Optional[dict[str, Any]]] = Column(JSON, nullable=True)


class XpEvent(Base):
    __tablename__ = "xp_events"
    __table_args__ = (UniqueConstraint("user_id", "idempotency_key", name="uq_xp_event_key"),)

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    idempotency_key: Mapped[str] = Column(String(200), nullable=False)
    amount: Mapped[int] = Column(Integer, nullable=False)
    activity: Mapped[str] = Column(String(80), nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class UserStreak(Base):
    __tablename__ = "user_streaks"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_streak"),)

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    current_streak: Mapped[int] = Column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = Column(Integer, default=0, nullable=False)
    last_learning_date: Mapped[Optional[str]] = Column(String(16), nullable=True)


class LearningActivity(Base):
    __tablename__ = "learning_activities"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    local_date: Mapped[str] = Column(String(16), nullable=False, index=True)
    activity_type: Mapped[str] = Column(String(40), nullable=False)
    minutes: Mapped[int] = Column(Integer, default=0, nullable=False)
    source: Mapped[str] = Column(String(80), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class UserStudySettings(Base):
    """Weekday/weekend study capacity. Single-user defaults."""

    __tablename__ = "user_study_settings"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_study_settings"),)

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    weekday_capacity_minutes: Mapped[int] = Column(Integer, default=90, nullable=False)
    weekend_capacity_minutes: Mapped[int] = Column(Integer, default=180, nullable=False)
    timezone: Mapped[str] = Column(String(64), default="Asia/Kolkata", nullable=False)


class EngineeringProject(Base):
    """Progressive build projects unlocked by topic completion."""

    __tablename__ = "engineering_projects"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = Column(String(160), nullable=False, unique=True, index=True)
    title: Mapped[str] = Column(String(200), nullable=False)
    goal: Mapped[str] = Column(Text, nullable=True)
    level: Mapped[int] = Column(Integer, default=1, nullable=False)  # 1–4
    difficulty: Mapped[str] = Column(String(20), default="beginner", nullable=False)
    estimated_hours: Mapped[float] = Column(Float, default=2.0, nullable=False)
    prerequisites: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    concepts_applied: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    milestones: Mapped[Optional[list[Any]]] = Column(JSON, nullable=True, default=list)
    deliverable: Mapped[Optional[str]] = Column(Text, nullable=True)
    order_index: Mapped[int] = Column(Integer, default=0, nullable=False)

    progress_records = relationship(
        "UserProjectProgress", back_populates="project", cascade="all, delete-orphan"
    )


class UserProjectProgress(Base):
    __tablename__ = "user_project_progress"
    __table_args__ = (UniqueConstraint("user_id", "project_id", name="uq_user_project"),)

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = Column(String(50), nullable=False, default="akshit", index=True)
    project_id: Mapped[int] = Column(Integer, ForeignKey("engineering_projects.id"), nullable=False)
    state: Mapped[str] = Column(String(20), default="locked", nullable=False)
    started_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)

    project: Mapped["EngineeringProject"] = relationship(
        "EngineeringProject", back_populates="progress_records"
    )