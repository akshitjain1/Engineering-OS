"""DB-backed learning engine operations. Planning never resets user_progress."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session, selectinload

from app.curriculum import evaluate_prerequisites, is_lesson_complete
from app.db.models import (
    AssessmentSession,
    CurriculumLesson,
    CurriculumModule,
    CurriculumResource,
    CurriculumSubject,
    CurriculumTopic,
    CurriculumTrack,
    DailyPlan,
    DiagnosticAnswer,
    DiagnosticSession,
    EngineeringProject,
    LessonExercise,
    MasteryEvidence,
    RevisionSchedule,
    TopicMastery,
    UserProgress,
    UserProjectProgress,
    UserStudySettings,
)
from app.content.resources import (
    attach_source_fields,
    empty_source_fields,
    orientation_from_description,
    select_resource_for_activity,
    serialize_resource,
)
from app.learning.diagnostic import score_response
from app.learning.diagnostic_bank import all_questions, public_question, questions_by_id
from app.learning.mastery import (
    apply_implementation_cap,
    labels_from_score,
    summarize_mastery,
    topic_requires_implementation,
)
from app.learning.planner import (
    RevisionView,
    TopicView,
    build_daily_plan,
    domain_from_slug,
    track_code_from_learning_track,
)
from app.learning.streak import get_or_create_streak, local_today, record_activity, serialize_streak
from app.learning.xp import (
    DIAGNOSTIC_COMPLETE_XP,
    LESSON_COMPLETE_XP,
    MASTERY_BONUS_XP,
    assessment_xp,
    award_xp,
    exercise_xp,
    get_or_create_xp,
    serialize_xp,
)


# ---------------------------------------------------------------------------
# Request-scoped view cache
# ---------------------------------------------------------------------------
# A ContextVar, not a module-level dict: the cache only exists for the span of
# one request and is discarded afterwards, so completion changes can never be
# served stale. Outside a request (tests, CLI) the var is None and every call
# recomputes, which is the old behaviour exactly.
_view_cache: ContextVar[Optional[dict[str, Any]]] = ContextVar(
    "topic_view_cache", default=None
)


@contextmanager
def request_view_cache():
    """Memoize build_topic_views for the duration of one read-only request."""
    token = _view_cache.set({})
    try:
        yield
    finally:
        _view_cache.reset(token)


ASSESSMENT_MINUTES = 15

DEFAULT_USER = "akshit"
REVISION_INTERVALS = [1, 3, 7, 14, 30, 60]
DEFAULT_GOAL = "Software Engineering + ML career readiness"


def revision_interval(confidence: float) -> int:
    index = min(max(int(confidence / 20), 0), len(REVISION_INTERVALS) - 1)
    return REVISION_INTERVALS[index]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _topics_index(db: Session) -> dict[str, CurriculumTopic]:
    topics = db.query(CurriculumTopic).options(selectinload(CurriculumTopic.lessons)).all()
    index: dict[str, CurriculumTopic] = {}
    for topic in topics:
        if topic.name:
            index[topic.name] = topic
        if topic.slug:
            index[topic.slug] = topic
    return index


def ordered_topics(db: Session) -> list[CurriculumTopic]:
    tracks = (
        db.query(CurriculumTrack)
        .options(
            selectinload(CurriculumTrack.subjects)
            .selectinload(CurriculumSubject.modules)
            .selectinload(CurriculumModule.topics)
            .selectinload(CurriculumTopic.lessons)
        )
        .order_by(CurriculumTrack.order_index)
        .all()
    )
    result: list[CurriculumTopic] = []
    for track in tracks:
        for subject in sorted(track.subjects, key=lambda item: (item.level_id or 0, item.order_index)):
            for module in sorted(subject.modules, key=lambda item: item.order_index):
                result.extend(sorted(module.topics, key=lambda item: item.order_index))
    return result or db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()


def topic_by_slug(db: Session, slug: str) -> Optional[CurriculumTopic]:
    return db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()


def upsert_evidence(
    db: Session,
    *,
    topic_slug: str,
    source: str,
    category: str,
    score: float,
    payload: Optional[dict[str, Any]] = None,
    user_id: str = DEFAULT_USER,
) -> None:
    """Register write: one row per (user, topic, source, category).

    Re-writing a register replaces the row so mastery reflects current
    evidence, never cumulative history. Question attempts intentionally do
    not write evidence; only completed assessments do.
    """
    existing = (
        db.query(MasteryEvidence)
        .filter(
            MasteryEvidence.user_id == user_id,
            MasteryEvidence.topic_slug == topic_slug,
            MasteryEvidence.source == source,
            MasteryEvidence.category == category,
        )
        .first()
    )
    if existing:
        existing.score = score
        existing.payload = payload
        existing.created_at = _now()
    else:
        db.add(
            MasteryEvidence(
                user_id=user_id,
                topic_slug=topic_slug,
                source=source,
                category=category,
                score=score,
                payload=payload,
            )
        )
    db.flush()


def evidence_for_slug(db: Session, slug: str, user_id: str = DEFAULT_USER) -> list[dict[str, Any]]:
    rows = (
        db.query(MasteryEvidence)
        .filter(MasteryEvidence.user_id == user_id, MasteryEvidence.topic_slug == slug)
        .order_by(MasteryEvidence.id)
        .all()
    )
    return [
        {"category": row.category, "score": row.score, "source": row.source, "payload": row.payload}
        for row in rows
    ]


def _upsert_revision(
    db: Session,
    topic_id: int,
    confidence: float,
    user_id: str,
    now: datetime,
    days: int,
) -> None:
    existing = (
        db.query(RevisionSchedule)
        .filter(
            RevisionSchedule.user_id == user_id,
            RevisionSchedule.item_id == topic_id,
            RevisionSchedule.item_type == "topic",
        )
        .first()
    )
    next_review = now + timedelta(days=days)
    if existing:
        existing.confidence = confidence
        existing.review_interval = days
        existing.next_review = next_review
        existing.last_reviewed = now
        return
    db.add(
        RevisionSchedule(
            user_id=user_id,
            item_id=topic_id,
            item_type="topic",
            confidence=confidence,
            last_reviewed=now,
            next_review=next_review,
            review_interval=days,
        )
    )


def sync_mastery_row(
    db: Session,
    slug: str,
    *,
    topic_id: Optional[int] = None,
    lesson_completed: bool = False,
    attempt: bool = False,
    award_bonus: bool = True,
    sync_revision: bool = True,
    user_id: str = DEFAULT_USER,
) -> TopicMastery:
    """Recompute a topic mastery row from its current evidence registers.

    `attempt` is True only for completed assessment sessions (diagnostic or
    topic assessment): repeated correctness clicks must not inflate attempts.
    `award_bonus` is False during reconciliation so a pure correction of
    stale evidence never changes XP totals or XP events. `sync_revision` is
    False during reconciliation so the review queue is not rewritten either.
    """
    summary = summarize_mastery(slug, evidence_for_slug(db, slug, user_id))
    topic = db.get(CurriculumTopic, topic_id) if topic_id else topic_by_slug(db, slug)
    row = (
        db.query(TopicMastery)
        .filter(TopicMastery.user_id == user_id, TopicMastery.topic_slug == slug)
        .first()
    )
    previous_status = row.status if row else None
    previous_score = row.mastery_score if row else None
    now = _now()
    if not row:
        row = TopicMastery(user_id=user_id, topic_slug=slug, topic_id=topic.id if topic else topic_id)
        db.add(row)
    if topic and not row.topic_id:
        row.topic_id = topic.id
    row.status = summary["status"]
    row.mastery_score = summary["mastery_score"]
    row.confidence = summary["mastery_score"] or 0
    if attempt:
        row.attempts = (row.attempts or 0) + 1
    row.last_assessed_at = now
    if lesson_completed:
        row.last_completed_at = now
    row.pace_mode = summary["pace_mode"]
    row.has_implementation_evidence = summary["has_implementation_evidence"]
    row.evidence = evidence_for_slug(db, slug, user_id)[-12:]
    if summary["mastery_score"] is not None:
        days = revision_interval(summary["mastery_score"])
        row.next_review_at = now + timedelta(days=days)
        if sync_revision and row.topic_id:
            _upsert_revision(db, row.topic_id, summary["mastery_score"], user_id, now, days)
    db.flush()
    crossed_into_mastered = (
        summary["status"] == "MASTERED"
        and previous_status != "MASTERED"
        and (previous_score is None or previous_score < 90)
    )
    if crossed_into_mastered and award_bonus:
        award_xp(
            db,
            idempotency_key=f"mastery:{user_id}:{slug}",
            amount=MASTERY_BONUS_XP,
            activity="mastery",
            user_id=user_id,
        )
    return row


def serialize_mastery(row: TopicMastery) -> dict[str, Any]:
    status, pace = labels_from_score(row.mastery_score)
    if row.topic_slug:
        status = apply_implementation_cap(
            status,
            requires_implementation=topic_requires_implementation(row.topic_slug),
            has_impl=row.has_implementation_evidence,
        )
    return {
        "id": row.id,
        "topic_id": row.topic_id,
        "topic_slug": row.topic_slug,
        "status": status,
        "mastery_score": row.mastery_score,
        "confidence": row.confidence,
        "attempts": row.attempts,
        "last_assessed_at": str(row.last_assessed_at) if row.last_assessed_at else None,
        "last_completed_at": str(row.last_completed_at) if row.last_completed_at else None,
        "next_review_at": str(row.next_review_at) if row.next_review_at else None,
        "evidence": row.evidence or [],
        "pace_mode": pace,
        "has_implementation_evidence": row.has_implementation_evidence,
    }


def mastery_counts(db: Session, user_id: str = DEFAULT_USER) -> dict[str, int]:
    rows = db.query(TopicMastery).filter(TopicMastery.user_id == user_id).all()
    counts = {"MASTERED": 0, "LEARNING": 0, "FAMILIAR": 0, "NEEDS_REVIEW": 0, "UNKNOWN": 0}
    for row in rows:
        status = serialize_mastery(row)["status"]
        counts[status] = counts.get(status, 0) + 1
    return counts


def diagnostic_status(db: Session, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    session = (
        db.query(DiagnosticSession)
        .filter(DiagnosticSession.user_id == user_id)
        .order_by(DiagnosticSession.id.desc())
        .first()
    )
    bank = all_questions()
    if not session:
        return {"started": False, "completed": False, "total": len(bank), "answered": 0, "current": None}
    ids = session.question_ids or [item["id"] for item in bank]
    answered = db.query(DiagnosticAnswer).filter(DiagnosticAnswer.session_id == session.id).count()
    current = None
    if session.status == "in_progress" and session.current_index < len(ids):
        qid = ids[session.current_index]
        current = public_question(questions_by_id()[qid])
    return {
        "started": True,
        "completed": session.status == "completed",
        "session_id": session.id,
        "status": session.status,
        "total": len(ids),
        "answered": answered,
        "index": session.current_index,
        "current": current,
        "summary": session.summary,
    }


def diagnostic_start(db: Session, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    existing = (
        db.query(DiagnosticSession)
        .filter(DiagnosticSession.user_id == user_id, DiagnosticSession.status == "in_progress")
        .order_by(DiagnosticSession.id.desc())
        .first()
    )
    if existing:
        return diagnostic_status(db, user_id)
    ids = [item["id"] for item in all_questions()]
    db.add(DiagnosticSession(user_id=user_id, status="in_progress", question_ids=ids, current_index=0))
    db.flush()
    return diagnostic_status(db, user_id)


def diagnostic_answer(
    db: Session,
    *,
    session_id: int,
    question_id: str,
    payload: dict[str, Any],
    user_id: str = DEFAULT_USER,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    session = db.get(DiagnosticSession, session_id)
    if not session or session.user_id != user_id:
        raise KeyError("session")
    if session.status != "in_progress":
        raise ValueError("session completed")
    question = questions_by_id().get(question_id)
    if not question:
        raise KeyError("question")
    ids = session.question_ids or []
    if question_id not in ids:
        raise KeyError("question")
    score = score_response(question, payload)
    row = (
        db.query(DiagnosticAnswer)
        .filter(DiagnosticAnswer.session_id == session.id, DiagnosticAnswer.question_id == question_id)
        .first()
    )
    if row:
        row.payload = payload
        row.score = score
        row.submitted_at = _now()
    else:
        db.add(DiagnosticAnswer(session_id=session.id, question_id=question_id, payload=payload, score=score))
        try:
            session.current_index = max(session.current_index, ids.index(question_id) + 1)
        except ValueError:
            session.current_index += 1
    record_activity(
        db,
        activity_type="assessment",
        minutes=2,
        source=f"diagnostic:{question_id}",
        timezone_name=timezone_name,
        user_id=user_id,
    )
    db.flush()
    return {
        "question_id": question_id,
        "score": score,
        "explanation": question.get("explanation"),
        "topics": question["topics"],
        "secondary": question.get("secondary") or [],
        **diagnostic_status(db, user_id),
    }


def diagnostic_complete(
    db: Session,
    session_id: int,
    user_id: str = DEFAULT_USER,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    session = db.get(DiagnosticSession, session_id)
    if not session or session.user_id != user_id:
        raise KeyError("session")
    answers = {
        row.question_id: row
        for row in db.query(DiagnosticAnswer).filter(DiagnosticAnswer.session_id == session.id)
    }
    bank = questions_by_id()
    slugs: set[str] = set()
    per_domain: dict[str, list[float]] = {"foundations": [], "java": [], "dsa": []}
    per_topic_category: dict[tuple[str, str], list[float]] = {}
    for qid, answer in answers.items():
        question = bank[qid]
        score = answer.score if answer.score is not None else 0.0
        per_domain[question["domain"]].append(score)
        for slug in list(question["topics"]) + list(question.get("secondary") or []):
            per_topic_category.setdefault((slug, question["category"]), []).append(score)
            slugs.add(slug)
    for (slug, category), scores in per_topic_category.items():
        upsert_evidence(
            db,
            topic_slug=slug,
            source="diagnostic",
            category=category,
            score=round(sum(scores) / len(scores), 2),
            payload={"question_ids": list(answers), "session_id": session.id},
            user_id=user_id,
        )
    for slug in slugs:
        sync_mastery_row(db, slug, attempt=True, user_id=user_id)

    def _avg(values: list[float]) -> Optional[float]:
        return round(sum(values) / len(values), 2) if values else None

    summary = {
        "foundations": _avg(per_domain["foundations"]),
        "java": _avg(per_domain["java"]),
        "dsa": _avg(per_domain["dsa"]),
        "topics_updated": sorted(slugs),
        "answered": len(answers),
        "total": len(session.question_ids or []),
    }
    session.status = "completed"
    session.completed_at = _now()
    session.summary = summary
    award_xp(
        db,
        idempotency_key=f"diagnostic_complete:{session.id}",
        amount=DIAGNOSTIC_COMPLETE_XP,
        activity="assessment",
        user_id=user_id,
    )
    record_activity(
        db,
        activity_type="diagnostic",
        minutes=20,
        source=f"diagnostic_complete:{session.id}",
        timezone_name=timezone_name,
        user_id=user_id,
    )
    db.flush()
    return {"session_id": session.id, "summary": summary, "mastery": mastery_counts(db, user_id)}


def on_lesson_completed(
    db: Session,
    lesson: CurriculumLesson,
    user_id: str = DEFAULT_USER,
    timezone_name: str | None = None,
) -> int:
    awarded, _ = award_xp(
        db,
        idempotency_key=f"lesson_complete:{lesson.id}",
        amount=LESSON_COMPLETE_XP,
        activity="lesson",
        user_id=user_id,
    )
    topic = lesson.topic or db.get(CurriculumTopic, lesson.topic_id)
    if topic and topic.slug:
        upsert_evidence(
            db,
            topic_slug=topic.slug,
            source="lesson",
            category="conceptual",
            score=55,
            payload={"lesson_id": lesson.id},
            user_id=user_id,
        )
        sync_mastery_row(db, topic.slug, topic_id=topic.id, lesson_completed=True, user_id=user_id)
    record_activity(
        db,
        activity_type="lesson",
        minutes=10,
        source=f"lesson:{lesson.id}",
        timezone_name=timezone_name,
        user_id=user_id,
    )
    return awarded


def on_exercise_completed(
    db: Session,
    exercise: LessonExercise,
    user_id: str = DEFAULT_USER,
    timezone_name: str | None = None,
) -> int:
    awarded, _ = award_xp(
        db,
        idempotency_key=f"exercise_complete:{exercise.id}",
        amount=exercise_xp(exercise.difficulty),
        activity="exercise",
        user_id=user_id,
    )
    lesson = db.get(CurriculumLesson, exercise.lesson_id)
    topic = lesson.topic if lesson else None
    if topic and topic.slug:
        upsert_evidence(
            db,
            topic_slug=topic.slug,
            source="exercise",
            category="implementation",
            score=80,
            payload={"exercise_id": exercise.id},
            user_id=user_id,
        )
        sync_mastery_row(db, topic.slug, topic_id=topic.id, user_id=user_id)
    record_activity(
        db,
        activity_type="exercise",
        minutes=15,
        source=f"exercise:{exercise.id}",
        timezone_name=timezone_name,
        user_id=user_id,
    )
    return awarded


def record_question_activity(
    db: Session,
    *,
    question_id: int,
    user_id: str = DEFAULT_USER,
    timezone_name: str | None = None,
) -> None:
    """Practice attempts record activity only.

    They never write mastery evidence, award XP, or bump attempts; a topic's
    score changes only when an assessment session is completed.
    """
    record_activity(
        db,
        activity_type="assessment",
        minutes=3,
        source=f"question:{question_id}",
        timezone_name=timezone_name,
        user_id=user_id,
    )


def _unfinished_exercise_count(topic: CurriculumTopic) -> int:
    count = 0
    for lesson in topic.lessons or []:
        for exercise in getattr(lesson, "exercises", []) or []:
            if not is_lesson_complete(exercise.completion_status):
                count += 1
    return count


def _topic_resources_and_tasks(topic: CurriculumTopic) -> tuple[list, list, list]:
    lessons = sorted(topic.lessons or [], key=lambda item: item.order_index)
    resources = [resource for lesson in lessons for resource in (lesson.resources or [])]
    exercises = [exercise for lesson in lessons for exercise in (lesson.exercises or [])]
    questions = [question for lesson in lessons for question in (lesson.questions or [])]
    return lessons, resources, exercises, questions


def latest_assessment_summary(
    db: Session, topic_id: int, user_id: str = DEFAULT_USER
) -> Optional[dict[str, Any]]:
    """Latest completed assessment session summary for a topic, if any."""
    session = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.user_id == user_id,
            AssessmentSession.topic_id == topic_id,
            AssessmentSession.status == "completed",
        )
        .order_by(AssessmentSession.id.desc())
        .first()
    )
    return (session.summary or {}) if session else None


def topic_completion_state(db: Session, topic: CurriculumTopic, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    """Completion contract that adapts to what the topic contains.

    A topic-level UserProgress row marked completed is authoritative (V3's
    explicit "Mark topic complete" action). Otherwise the contract requires:
    learning activity (lesson completed, or a consumed resource when a topic
    has no lessons) AND all exercises done (when any exist) AND a passed
    assessment (when questions exist). Missing pieces relax the contract
    instead of blocking forever.
    """
    lessons, resources, exercises, questions = _topic_resources_and_tasks(topic)
    forced = _topic_progress_forced_complete(db, topic.id, user_id)
    if forced:
        return {
            "complete": True,
            "learning_done": True,
            "lessons_complete": True,
            "resources_complete": True,
            "exercises_complete": True,
            "has_questions": bool(questions),
            "assessment_ok": True if questions else None,
            "lesson_count": len(lessons),
        }
    lessons_complete = bool(lessons) and all(is_lesson_complete(item.completion_status) for item in lessons)
    resources_complete = bool(resources) and any(
        is_lesson_complete(item.completion_status) for item in resources
    )
    learning_done = lessons_complete or resources_complete
    exercises_complete = (not exercises) or all(
        is_lesson_complete(item.completion_status) for item in exercises
    )
    has_questions = bool(questions)
    assessment_ok: Optional[bool] = None
    if has_questions:
        summary = latest_assessment_summary(db, topic.id, user_id)
        assessment_ok = bool(summary and (summary.get("score") or 0) >= 50)
    complete = bool(learning_done) and exercises_complete and (assessment_ok is not False)
    return {
        "complete": complete,
        "learning_done": learning_done,
        "lessons_complete": lessons_complete,
        "resources_complete": resources_complete,
        "exercises_complete": exercises_complete,
        "has_questions": has_questions,
        "assessment_ok": assessment_ok,
        "lesson_count": len(lessons),
    }


def _topic_progress_forced_complete(db: Session, topic_id: int, user_id: str) -> bool:
    """True when the user explicitly marked the topic complete (V3 Done action)."""
    row = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.topic_id == topic_id,
            UserProgress.lesson_id.is_(None),
        )
        .first()
    )
    return bool(row and is_lesson_complete(row.progress_state))


def topic_completion_index(db: Session, user_id: str = DEFAULT_USER) -> dict[str, bool]:
    """slug -> completion contract result for every topic (one pass)."""
    topics = db.query(CurriculumTopic).options(
        selectinload(CurriculumTopic.lessons)
        .selectinload(CurriculumLesson.resources),
        selectinload(CurriculumTopic.lessons)
        .selectinload(CurriculumLesson.exercises),
        selectinload(CurriculumTopic.lessons)
        .selectinload(CurriculumLesson.questions),
    ).all()
    forced = {
        row.topic_id
        for row in db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id.is_(None),
            UserProgress.topic_id.isnot(None),
        )
        .all()
        if is_lesson_complete(row.progress_state)
    }
    sessions = (
        db.query(AssessmentSession)
        .filter(AssessmentSession.user_id == user_id, AssessmentSession.status == "completed")
        .order_by(AssessmentSession.id.desc())
        .all()
    )
    latest_by_topic: dict[int, dict] = {}
    for session in sessions:
        latest_by_topic.setdefault(session.topic_id, session.summary or {})
    result: dict[str, bool] = {}
    for topic in topics:
        if topic.id in forced:
            result[topic.slug] = True
            if topic.name:
                result[topic.name] = True
            continue
        lessons, resources, exercises, questions = _topic_resources_and_tasks(topic)
        lessons_complete = bool(lessons) and all(
            is_lesson_complete(item.completion_status) for item in lessons
        )
        learning_done = lessons_complete or (
            bool(resources)
            and any(is_lesson_complete(item.completion_status) for item in resources)
        )
        exercises_complete = (not exercises) or all(
            is_lesson_complete(item.completion_status) for item in exercises
        )
        assessment_ok: Optional[bool] = None
        if questions:
            summary = latest_by_topic.get(topic.id)
            assessment_ok = bool(summary and (summary.get("score") or 0) >= 50)
        result[topic.slug] = bool(learning_done) and exercises_complete and (assessment_ok is not False)
        if topic.name:
            result[topic.name] = result[topic.slug]
    return result


def is_coding_problem(resource: Any) -> bool:
    """A row that stands for a problem on a judge, rather than something to read."""
    url = (getattr(resource, "url", None) or "").strip()
    if not url:
        return False
    kind = (getattr(resource, "resource_type", None) or "").lower()
    return "problem" in kind or "leetcode.com/problems/" in url


def set_problem_solved(db: Session, resource: Any, completed: bool) -> list[Any]:
    """Record a problem as solved, everywhere that problem appears.

    The mapping deliberately reuses problems: 57 of them are pinned to more than
    one topic, and Two Sum alone sits under five. Each was its own row with its
    own tick, so solving Two Sum under Algorithmic thinking left it reading
    "Mark solved" when Big-O served it the next day -- the app asking whether
    you had done something it already knew you had.

    Solved is a fact about the problem, not about the row that happened to show
    it, so it is written to every row with the same URL. Non-problem resources
    are untouched: the same article can be set for different sections in
    different topics, and reading one is not reading the other.

    Returns the rows that were changed.
    """
    status = "completed" if completed else "not_started"
    if not is_coding_problem(resource):
        changed = [] if resource.completion_status == status else [resource]
        resource.completion_status = status
        return changed

    rows = (
        db.query(CurriculumResource)
        .filter(CurriculumResource.url == resource.url)
        .all()
    )
    changed = []
    for row in rows or [resource]:
        if row.completion_status != status:
            row.completion_status = status
            changed.append(row)
    return changed


#: Roles that make up a topic's actual work -- the source the day sends you to
#: read, and the problems it sends you to solve. Finishing the topic means you
#: did these, so completion marks them consumed.
#:
#: REFERENCE, SUPPLEMENT and DEEP_DIVE are deliberately not here. The flow never
#: routes you through them, Deep Dive is its own optional section on the topic
#: page, and ticking material you were never asked to open would make the page
#: claim you had read something you had not.
TOPIC_WORK_ROLES = {"PRIMARY", "PRACTICE"}


def complete_topic(db: Session, topic_id: int, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    """V3 Done action: mark a topic complete. Idempotent, no XP, no mastery.

    Completes any unfinished lessons, exercises and work resources directly and
    records a topic-level UserProgress row so the completion index unlocks the
    next topic. Never writes mastery evidence, never awards XP, never touches
    revision schedules.
    """
    topic = db.get(CurriculumTopic, topic_id)
    if not topic:
        raise KeyError("topic")
    now = _now()
    lessons = sorted(topic.lessons or [], key=lambda item: item.order_index)
    for lesson in lessons:
        if not is_lesson_complete(lesson.completion_status):
            lesson.completion_status = "completed"
        for exercise in getattr(lesson, "exercises", []) or []:
            if not is_lesson_complete(exercise.completion_status):
                exercise.completion_status = "completed"
                exercise.attempted_at = now
        # Resources were the one thing completion never touched. Lessons and
        # exercises were closed out, so saying "finished this topic" left the
        # source you had just spent the whole block reading still labelled
        # "Not consumed" -- and asked you to tick it again by hand, which is
        # bookkeeping the app already had the answer to.
        for resource in getattr(lesson, "resources", []) or []:
            if (resource.role or "").upper() not in TOPIC_WORK_ROLES:
                continue
            if getattr(resource, "learner_visible", True) is False:
                continue
            if not is_lesson_complete(resource.completion_status):
                # Through the helper, so finishing a DSA topic marks its
                # problems solved wherever else they are mapped as well.
                set_problem_solved(db, resource, True)
    row = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.topic_id == topic.id,
            UserProgress.lesson_id.is_(None),
        )
        .first()
    )
    if not row:
        row = UserProgress(user_id=user_id, topic_id=topic.id)
        db.add(row)
    row.progress_state = "completed"
    row.last_activity_at = now
    db.flush()
    return {
        "topic_id": topic.id,
        "topic_slug": topic.slug,
        "name": topic.name,
        "complete": True,
        "status": "completed",
    }


def mark_exercise_complete(db: Session, exercise_id: int, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    """V3 Build step: mark an implementation task done without XP or evidence."""
    exercise = db.get(LessonExercise, exercise_id)
    if not exercise:
        raise KeyError("exercise")
    exercise.completion_status = "completed"
    exercise.attempted_at = _now()
    db.flush()
    return {
        "id": exercise.id,
        "title": exercise.title,
        "completed": True,
        "completion_status": "completed",
    }


def explore_topic(db: Session, topic_id: int, user_id: str = DEFAULT_USER) -> Optional[dict[str, Any]]:
    """Public assessment data for a topic (no answers, no session creation)."""
    topic = db.get(CurriculumTopic, topic_id)
    if not topic:
        return None
    lessons = sorted(topic.lessons or [], key=lambda item: item.order_index)
    questions = [question for lesson in lessons for question in (lesson.questions or [])]
    return {
        "topic_id": topic.id,
        "slug": topic.slug,
        "name": topic.name,
        "locked": False,
        "questions": [
            {"id": question.id, "prompt": question.question, "options": question.options or [], "difficulty": question.difficulty}
            for question in questions
        ],
    }


def assessment_start(
    db: Session,
    topic_id: int,
    user_id: str = DEFAULT_USER,
) -> dict[str, Any]:
    topic = db.get(CurriculumTopic, topic_id)
    if not topic:
        raise KeyError("topic")
    lessons = sorted(topic.lessons or [], key=lambda item: item.order_index)
    questions = [question for lesson in lessons for question in (lesson.questions or [])]
    if not questions:
        raise ValueError("topic has no assessment questions")
    existing = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.user_id == user_id,
            AssessmentSession.topic_id == topic_id,
            AssessmentSession.status == "in_progress",
        )
        .order_by(AssessmentSession.id.desc())
        .first()
    )
    if existing:
        return assessment_state(db, existing.id, user_id)
    session = AssessmentSession(
        user_id=user_id,
        topic_id=topic_id,
        status="in_progress",
        question_ids=[question.id for question in questions],
        current_index=0,
        answers=[],
    )
    db.add(session)
    db.flush()
    return assessment_state(db, session.id, user_id)


def assessment_state(db: Session, session_id: int, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    session = db.get(AssessmentSession, session_id)
    if not session or session.user_id != user_id:
        raise KeyError("session")
    return _serialize_assessment_session(db, session)


def _serialize_assessment_session(db: Session, session: AssessmentSession) -> dict[str, Any]:
    topic = db.get(CurriculumTopic, session.topic_id)
    lessons = sorted(topic.lessons or [], key=lambda item: item.order_index)
    bank = {
        question.id: question
        for lesson in lessons
        for question in (lesson.questions or [])
    }
    ids = session.question_ids or []
    answered: list[int] = [item.get("question_id") for item in (session.answers or [])]
    current = None
    for qid in ids:
        if qid not in answered:
            question = bank.get(qid)
            current = {
                "id": question.id,
                "prompt": question.question,
                "options": question.options or [],
                "difficulty": question.difficulty,
            }
            break
    previous = None
    if answered:
        last_id = answered[-1]
        detail = next((item for item in (session.answers or []) if item.get("question_id") == last_id), None)
        if detail:
            question = bank.get(last_id)
            previous = {
                "question_id": last_id,
                "prompt": question.question if question else None,
                "selected": detail.get("selected"),
                "correct": detail.get("correct"),
                "explanation": question.explanation if question else None,
            }
    return {
        "session_id": session.id,
        "topic_id": session.topic_id,
        "topic_name": topic.name if topic else None,
        "status": session.status,
        "total": len(ids),
        "answered": len(answered),
        "current": current,
        "previous": previous,
        "complete": session.status == "completed",
        "summary": session.summary,
    }


def assessment_answer(
    db: Session,
    *,
    session_id: int,
    question_id: int,
    selected: str,
    user_id: str = DEFAULT_USER,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    session = db.get(AssessmentSession, session_id)
    if not session or session.user_id != user_id:
        raise KeyError("session")
    if session.status != "in_progress":
        raise ValueError("session completed")
    ids = session.question_ids or []
    if question_id not in ids:
        raise KeyError("question")
    if any(item.get("question_id") == question_id for item in (session.answers or [])):
        raise ValueError("question already answered")
    topic = db.get(CurriculumTopic, session.topic_id)
    lessons = sorted(topic.lessons or [], key=lambda item: item.order_index)
    bank = {question.id: question for lesson in lessons for question in (lesson.questions or [])}
    question = bank.get(question_id)
    if not question:
        raise KeyError("question")
    correct = (selected or "").strip().lower() == (question.answer or "").strip().lower()
    answers = list(session.answers or [])
    answers.append(
        {
            "question_id": question_id,
            "selected": selected,
            "correct": correct,
        }
    )
    session.answers = answers
    session.current_index = max(session.current_index, ids.index(question_id) + 1)
    record_activity(
        db,
        activity_type="assessment",
        minutes=2,
        source=f"assessment:{session.id}:{question_id}",
        timezone_name=timezone_name,
        user_id=user_id,
    )
    db.flush()
    return {
        "question_id": question_id,
        "correct": correct,
        "answer": question.answer,
        "explanation": question.explanation,
        **assessment_state(db, session.id, user_id),
    }


def assessment_complete(
    db: Session,
    session_id: int,
    user_id: str = DEFAULT_USER,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    session = db.get(AssessmentSession, session_id)
    if not session or session.user_id != user_id:
        raise KeyError("session")
    if session.status == "completed":
        return _finished_assessment_payload(db, session)
    answers = session.answers or []
    correct_count = sum(1 for item in answers if item.get("correct"))
    total = len(session.question_ids or [])
    score = round((correct_count / total) * 100, 2) if total else 0.0
    category_scores: dict[str, float] = {"conceptual": score}
    summary = {
        "score": score,
        "correct": correct_count,
        "total": total,
        "attempted": len(answers),
        "per_category": category_scores,
        "topic_id": session.topic_id,
    }
    session.status = "completed"
    session.completed_at = _now()
    session.summary = summary
    topic = db.get(CurriculumTopic, session.topic_id)
    if topic and topic.slug:
        for category, category_score in category_scores.items():
            upsert_evidence(
                db,
                topic_slug=topic.slug,
                source="assessment",
                category=category,
                score=category_score,
                payload={"session_id": session.id, "topic_id": session.topic_id},
                user_id=user_id,
            )
        sync_mastery_row(db, topic.slug, topic_id=topic.id, attempt=True, user_id=user_id)
    awarded, _ = award_xp(
        db,
        idempotency_key=f"assessment_complete:{session.id}",
        amount=assessment_xp(score),
        activity="assessment",
        user_id=user_id,
    )
    record_activity(
        db,
        activity_type="assessment",
        minutes=ASSESSMENT_MINUTES,
        source=f"assessment:{session.id}",
        timezone_name=timezone_name,
        user_id=user_id,
    )
    db.flush()
    result = _finished_assessment_payload(db, session)
    result["xp_awarded"] = awarded
    return result


def _finished_assessment_payload(db: Session, session: AssessmentSession) -> dict[str, Any]:
    payload = _serialize_assessment_session(db, session)
    topic = db.get(CurriculumTopic, session.topic_id)
    mastery = None
    if topic and topic.slug:
        row = (
            db.query(TopicMastery)
            .filter(TopicMastery.user_id == session.user_id, TopicMastery.topic_slug == topic.slug)
            .first()
        )
        if row:
            mastery = serialize_mastery(row)
    payload["mastery"] = mastery
    return payload


def _practice_pending_count(topic: CurriculumTopic) -> int:
    """Pending practice load: PRACTICE-role resources + explicit exercise
    contracts (PART H) that are still incomplete."""
    count = 0
    for lesson in topic.lessons or []:
        for resource in lesson.resources or []:
            if getattr(resource, "role", None) == "PRACTICE" and not is_lesson_complete(resource.completion_status):
                count += 1
        for exercise in lesson.exercises or []:
            if not is_lesson_complete(exercise.completion_status):
                count += 1
    return count


def build_topic_views(db: Session, user_id: str = DEFAULT_USER) -> list[TopicView]:
    """Every topic as a planner-ready view.

    /api/dashboard reaches this four times per request (directly, plus inside
    tracks_snapshot and study_focus). The result only depends on (db, user_id),
    so a read-only request memoizes it -- see request_view_cache.
    """
    cache = _view_cache.get()
    if cache is not None and user_id in cache:
        return cache[user_id]
    views = _build_topic_views_uncached(db, user_id)
    if cache is not None:
        cache[user_id] = views
    return views


def _build_topic_views_uncached(db: Session, user_id: str) -> list[TopicView]:
    from app.content.audit import audit_topic, build_audit_index

    index = _topics_index(db)
    completion = topic_completion_index(db, user_id)
    # One prefetch for all 449 audits instead of ~7 queries per topic.
    audit_index = build_audit_index(db)
    views: list[TopicView] = []
    for topic in ordered_topics(db):
        lock = evaluate_prerequisites(
            topic.prerequisites if topic.prerequisites else [],
            index,
            completion_lookup=completion,
        )
        slug = topic.slug or f"topic-{topic.id}"
        learning_track = getattr(topic, "learning_track", None) or "CORE"
        domain = getattr(topic, "domain_key", None) or domain_from_slug(slug)
        readiness = None
        try:
            audited = audit_topic(db, slug, audit_index) if topic.slug else None
            readiness = audited.readiness if audited else None
        except Exception:  # noqa: BLE001
            readiness = None
        views.append(
            TopicView(
                id=topic.id,
                slug=slug,
                name=topic.name,
                locked=bool(lock["locked"]),
                lessons_complete=bool(completion.get(slug)),
                domain=domain,
                track=track_code_from_learning_track(learning_track),
                # Pass prerequisite refs through verbatim: planner supports both
                # legacy string slugs and enhanced {"slug","type"} dicts. Never
                # stringify here — str() would break dict-ref slug resolution
                # and permanently lock enhanced-format topics.
                prerequisite_slugs=list(topic.prerequisites or []),
                unfinished_exercises=_unfinished_exercise_count(topic),
                practice_pending=_practice_pending_count(topic),
                project_embedding=learning_track.upper() == "BUILD",
                parallel_eligible=bool(getattr(topic, "parallel_eligible", False)),
                learning_track=learning_track.upper(),
                depth_target=getattr(topic, "depth_target", None) or "WORKING_KNOWLEDGE",
                estimated_minutes=getattr(topic, "estimated_minutes", None),
                content_readiness=readiness,
                topic_type=getattr(topic, "topic_type", None) or "LEARNABLE",
            )
        )
    return views


def get_or_create_study_settings(
    db: Session, user_id: str = DEFAULT_USER
) -> UserStudySettings:
    row = db.query(UserStudySettings).filter(UserStudySettings.user_id == user_id).first()
    if row:
        return row
    row = UserStudySettings(user_id=user_id)
    db.add(row)
    db.flush()
    return row


def serialize_study_settings(row: UserStudySettings) -> dict[str, Any]:
    return {
        "weekday_capacity_minutes": row.weekday_capacity_minutes,
        "weekend_capacity_minutes": row.weekend_capacity_minutes,
        "timezone": row.timezone,
        "revision_weighted": bool(row.revision_weighted),
    }


def update_study_settings(
    db: Session,
    *,
    weekday_capacity_minutes: Optional[int] = None,
    weekend_capacity_minutes: Optional[int] = None,
    timezone_name: Optional[str] = None,
    revision_weighted: Optional[bool] = None,
    user_id: str = DEFAULT_USER,
) -> dict[str, Any]:
    row = get_or_create_study_settings(db, user_id)
    if weekday_capacity_minutes is not None:
        row.weekday_capacity_minutes = max(15, min(360, int(weekday_capacity_minutes)))
    if weekend_capacity_minutes is not None:
        row.weekend_capacity_minutes = max(15, min(480, int(weekend_capacity_minutes)))
    if timezone_name:
        row.timezone = timezone_name
    if revision_weighted is not None:
        row.revision_weighted = bool(revision_weighted)
    db.flush()
    return serialize_study_settings(row)


def plan_mode_and_budget(
    db: Session,
    *,
    minutes: Optional[int] = None,
    timezone_name: str | None = None,
    user_id: str = DEFAULT_USER,
) -> tuple[str, int]:
    """Return (mode, budget_minutes) from explicit minutes or weekday/weekend settings."""
    settings = get_or_create_study_settings(db, user_id)
    tz_name = timezone_name or settings.timezone or "Asia/Kolkata"
    today = local_today(tz_name)
    # local_today returns YYYY-MM-DD; weekday from date
    from datetime import date as date_cls

    day = date_cls.fromisoformat(today)
    is_weekend = day.weekday() >= 5  # Sat/Sun
    mode = "weekend" if is_weekend else "weekday"
    if minutes is not None:
        return mode, int(minutes)
    budget = (
        settings.weekend_capacity_minutes if is_weekend else settings.weekday_capacity_minutes
    )
    return mode, int(budget)


def tracks_snapshot(db: Session, user_id: str = DEFAULT_USER) -> list[dict[str, Any]]:
    views = build_topic_views(db, user_id)
    labels = {
        "CORE": "Core",
        "SPECIALIZATION": "Specialization",
        "ALWAYS_ON": "Always-On",
        "BUILD": "Build",
        "OPTIONAL": "Optional",
    }
    order = ["CORE", "SPECIALIZATION", "ALWAYS_ON", "BUILD", "OPTIONAL"]
    by_track: dict[str, list[TopicView]] = {key: [] for key in order}
    for view in views:
        key = view.learning_track if view.learning_track in by_track else "CORE"
        by_track[key].append(view)

    snapshot = []
    for key in order:
        bucket = by_track[key]
        if not bucket and key == "OPTIONAL":
            continue
        total = len(bucket)
        complete = sum(1 for t in bucket if t.lessons_complete)
        next_topic = next(
            (t for t in bucket if not t.locked and not t.lessons_complete), None
        )
        snapshot.append(
            {
                "key": key,
                "label": labels.get(key, key),
                "total": total,
                "complete": complete,
                "next": (
                    {
                        "topic_id": next_topic.id,
                        "slug": next_topic.slug,
                        "name": next_topic.name,
                        "locked": next_topic.locked,
                    }
                    if next_topic
                    else None
                ),
            }
        )
    return snapshot


def this_week_summary(
    db: Session, user_id: str = DEFAULT_USER, timezone_name: str | None = None
) -> dict[str, Any]:
    settings = get_or_create_study_settings(db, user_id)
    tz_name = timezone_name or settings.timezone
    today = local_today(tz_name)
    from datetime import date as date_cls, timedelta as td

    day = date_cls.fromisoformat(today)
    start = day - td(days=day.weekday())  # Monday
    capacity = 0
    for offset in range(7):
        d = start + td(days=offset)
        if d.weekday() >= 5:
            capacity += settings.weekend_capacity_minutes
        else:
            capacity += settings.weekday_capacity_minutes
    plans = (
        db.query(DailyPlan)
        .filter(
            DailyPlan.user_id == user_id,
            DailyPlan.plan_date >= start.isoformat(),
            DailyPlan.plan_date <= (start + td(days=6)).isoformat(),
        )
        .all()
    )
    scheduled = 0
    for plan in plans:
        for item in plan.items or []:
            scheduled += int(item.get("minutes") or 0)
    return {
        "week_start": start.isoformat(),
        "capacity_minutes": capacity,
        "scheduled_minutes": scheduled,
        "remaining_minutes": max(0, capacity - scheduled),
    }


def _available_project_hint(db: Session, user_id: str = DEFAULT_USER) -> Optional[dict[str, Any]]:
    """Highest-priority available / in-progress project for planner BUILD slots."""
    try:
        from app.learning import projects as projects_svc
    except ImportError:
        return None
    projects_svc.sync_project_unlocks(db, user_id)
    available = projects_svc.list_projects(db, user_id)
    for bucket in ("in_progress", "available"):
        rows = available.get(bucket) or []
        if rows:
            row = rows[0]
            return {
                "title": row["title"],
                "minutes": min(60, int(float(row.get("estimated_hours") or 2) * 60)),
                "why": f"Project: {row['title']}",
                "topic_slug": None,
                "domain": "build",
                "project_id": row["id"],
            }
    return None


def pending_revisions(db: Session, user_id: str = DEFAULT_USER) -> list[dict[str, Any]]:
    horizon = _now() + timedelta(days=1)
    rows = (
        db.query(RevisionSchedule)
        .filter(RevisionSchedule.user_id == user_id, RevisionSchedule.next_review <= horizon)
        .order_by(RevisionSchedule.next_review)
        .all()
    )
    payload = []
    for row in rows:
        title = f"{row.item_type} #{row.item_id}"
        slug = None
        if row.item_type == "topic":
            topic = db.get(CurriculumTopic, row.item_id)
            if topic:
                title = topic.name
                slug = topic.slug
        payload.append(
            {
                "id": row.id,
                "item_id": row.item_id,
                "item_type": row.item_type,
                "confidence": row.confidence,
                "next_review": str(row.next_review) if row.next_review else None,
                "review_interval": row.review_interval,
                "title": title,
                "topic_slug": slug,
            }
        )
    return payload


def _resources_for_topic(db: Session, topic_id: int) -> list[CurriculumResource]:
    return (
        db.query(CurriculumResource)
        .join(CurriculumLesson, CurriculumResource.lesson_id == CurriculumLesson.id)
        .filter(CurriculumLesson.topic_id == topic_id)
        .order_by(CurriculumResource.order_index, CurriculumResource.id)
        .all()
    )


def enrich_plan_item(db: Session, item: dict[str, Any]) -> dict[str, Any]:
    """Attach source metadata to a planner item. Never invents URLs or video IDs."""
    activity = item.get("type")
    topic_id = item.get("topic_id")
    topic = db.get(CurriculumTopic, topic_id) if topic_id else None
    enriched = {
        **item,
        "activity_type": activity,
        "reason": item.get("why"),
        "topic_title": topic.name if topic else item.get("title"),
        "topic_slug": item.get("topic_slug") or (topic.slug if topic else None),
    }
    if activity not in {"LEARN", "REFERENCE", "PRACTICE"}:
        enriched.update({**empty_source_fields(), "resource_status": None, "verification_status": None})
        return enriched
    if not topic:
        enriched.update(empty_source_fields())
        return enriched
    chosen = select_resource_for_activity(_resources_for_topic(db, topic.id), activity)
    if not chosen:
        enriched.update(empty_source_fields())
        return enriched
    enriched.update(attach_source_fields(serialize_resource(chosen)))
    return enriched


def enrich_plan_items(db: Session, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [enrich_plan_item(db, item) for item in items]


def generate_daily_plan(
    db: Session,
    *,
    budget_minutes: Optional[int] = None,
    goal: str = DEFAULT_GOAL,
    user_id: str = DEFAULT_USER,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    progress_before = db.query(UserProgress).filter(UserProgress.user_id == user_id).count()
    mode, resolved_minutes = plan_mode_and_budget(
        db, minutes=budget_minutes, timezone_name=timezone_name, user_id=user_id
    )
    plan_date = local_today(timezone_name)
    overdue = [
        RevisionView(
            id=item["id"],
            item_id=item["item_id"],
            item_type=item["item_type"],
            title=item["title"],
            topic_slug=item.get("topic_slug"),
        )
        for item in pending_revisions(db, user_id)
    ]
    project_hint = _available_project_hint(db, user_id)
    built = build_daily_plan(
        budget_minutes=resolved_minutes,
        topics=build_topic_views(db, user_id),
        overdue_revisions=overdue,
        goal=goal,
        mode=mode,
        project_hint=project_hint,
    )
    index = _topics_index(db)
    completion = topic_completion_index(db, user_id)
    for item in built["items"]:
        if item["type"] in {"LEARN", "PRACTICE", "BUILD", "ALWAYS_ON", "PROJECT"} and item.get(
            "topic_id"
        ):
            topic = db.get(CurriculumTopic, item["topic_id"])
            if topic:
                lock = evaluate_prerequisites(
                    topic.prerequisites if topic.prerequisites else [],
                    index,
                    completion_lookup=completion,
                )
                if lock["locked"]:
                    raise RuntimeError("planner emitted a locked topic")
    built["items"] = enrich_plan_items(db, built["items"])
    # Refresh groups after enrichment
    groups = {"core": [], "parallel": [], "practice": [], "build": []}
    for item in built["items"]:
        groups.setdefault(item.get("group") or "core", []).append(item)
    built["groups"] = groups
    existing = (
        db.query(DailyPlan).filter(DailyPlan.user_id == user_id, DailyPlan.plan_date == plan_date).first()
    )
    if existing:
        existing.budget_minutes = resolved_minutes
        existing.goal = goal
        existing.items = built["items"]
        existing.generated_at = _now()
        row = existing
    else:
        row = DailyPlan(
            user_id=user_id,
            plan_date=plan_date,
            budget_minutes=resolved_minutes,
            goal=goal,
            items=built["items"],
        )
        db.add(row)
    db.flush()
    progress_after = db.query(UserProgress).filter(UserProgress.user_id == user_id).count()
    if progress_before != progress_after:
        raise RuntimeError("planning mutated user_progress")
    return {"id": row.id, "plan_date": row.plan_date, **built}


def get_daily_plan(
    db: Session, user_id: str = DEFAULT_USER, timezone_name: str | None = None
) -> Optional[dict[str, Any]]:
    plan_date = local_today(timezone_name)
    row = db.query(DailyPlan).filter(DailyPlan.user_id == user_id, DailyPlan.plan_date == plan_date).first()
    if not row:
        return None
    items = enrich_plan_items(db, row.items or [])
    groups = {"core": [], "parallel": [], "practice": [], "build": []}
    for item in items:
        groups.setdefault(item.get("group") or "core", []).append(item)
    return {
        "id": row.id,
        "plan_date": row.plan_date,
        "budget_minutes": row.budget_minutes,
        "total_minutes": sum(item.get("minutes", 0) for item in items),
        "goal": row.goal,
        "items": items,
        "groups": groups,
        "generated_at": str(row.generated_at) if row.generated_at else None,
    }


OFFICIAL_TRACK_SLUG = "engineering-os-v1"


def official_spine(db: Session) -> list[CurriculumTopic]:
    return [
        topic
        for topic in ordered_topics(db)
        if topic.module
        and topic.module.subject
        and topic.module.subject.track
        and topic.module.subject.track.slug == OFFICIAL_TRACK_SLUG
    ]


def serialize_focus_topic(db: Session, topic: CurriculumTopic, view: TopicView) -> dict[str, Any]:
    chosen = select_resource_for_activity(_resources_for_topic(db, topic.id), "LEARN")
    primary = serialize_resource(chosen) if chosen else None
    if view.locked:
        status = "locked"
    elif view.lessons_complete:
        status = "completed"
    else:
        status = "in_progress"
    return {
        "topic_id": topic.id,
        "slug": topic.slug,
        "name": topic.name,
        "domain": view.domain,
        "module_name": topic.module.name if topic.module else None,
        "locked": view.locked,
        "lessons_complete": view.lessons_complete,
        "status": status,
        "hours_estimated": sum((lesson.hours_estimated or 0) for lesson in (topic.lessons or [])),
        "why": orientation_from_description(topic.description),
        "primary": primary,
        "resource_status": (primary or {}).get("verification_status") or "UNRESOLVED",
    }


def study_focus(db: Session, user_id: str = DEFAULT_USER, upcoming_count: int = 5) -> dict[str, Any]:
    spine = official_spine(db)
    views = {item.id: item for item in build_topic_views(db, user_id)}
    current = None
    index = None
    for offset, topic in enumerate(spine):
        view = views.get(topic.id)
        if view and not view.locked and not view.lessons_complete:
            current = serialize_focus_topic(db, topic, view)
            index = offset
            break
    upcoming = []
    if index is not None:
        for topic in spine[index + 1 : index + 1 + upcoming_count]:
            view = views.get(topic.id)
            if view:
                upcoming.append(serialize_focus_topic(db, topic, view))
    next_topic = None
    if index is not None and index + 1 < len(spine):
        nxt = spine[index + 1]
        view = views.get(nxt.id)
        next_topic = serialize_focus_topic(db, nxt, view) if view else {"topic_id": nxt.id, "name": nxt.name, "slug": nxt.slug}
    return {"current": current, "upcoming": upcoming, "next": next_topic}


def dashboard_snapshot(
    db: Session, user_id: str = DEFAULT_USER, timezone_name: str | None = None
) -> dict[str, Any]:
    xp = get_or_create_xp(db, user_id)
    streak = get_or_create_streak(db, user_id)
    counts = mastery_counts(db, user_id)
    plan = get_daily_plan(db, user_id, timezone_name)
    views = build_topic_views(db, user_id)
    cursor = next(
        (
            topic
            for topic in views
            if topic.learning_track == "CORE"
            and not topic.locked
            and not topic.lessons_complete
        ),
        None,
    )
    if cursor is None:
        cursor = next(
            (topic for topic in views if not topic.locked and not topic.lessons_complete),
            None,
        )
    recent = (
        db.query(MasteryEvidence)
        .filter(MasteryEvidence.user_id == user_id)
        .order_by(MasteryEvidence.id.desc())
        .limit(8)
        .all()
    )
    focus = study_focus(db, user_id)
    return {
        "user_id": user_id,
        "streak": serialize_streak(streak),
        "xp": serialize_xp(xp),
        "mastery": counts,
        "revision_due": len(pending_revisions(db, user_id)),
        "today_plan": plan,
        "focus": focus,
        "tracks": tracks_snapshot(db, user_id),
        "this_week": this_week_summary(db, user_id, timezone_name),
        "study_settings": serialize_study_settings(get_or_create_study_settings(db, user_id)),
        "curriculum_position": (
            {
                "topic_id": cursor.id,
                "topic_slug": cursor.slug,
                "name": cursor.name,
            }
            if cursor
            else None
        ),
        "recent_activity": [
            {
                "topic_slug": row.topic_slug,
                "source": row.source,
                "category": row.category,
                "score": row.score,
            }
            for row in recent
            if row.source not in {"open_dashboard", "dashboard"}
        ],
    }
