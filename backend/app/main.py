from typing import Any, Optional
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from .curriculum import (
    compose_topic_status,
    evaluate_prerequisites,
    is_lesson_complete,
    lesson_ui_status,
    module_progress,
    normalize_lesson_state,
    ratio,
    subject_progress,
    topic_lesson_progress,
    UI_LESSON_STATES,
)
from .content.resources import (
    group_resources_by_role,
    orientation_from_description,
    serialize_resource,
)
from .db.migrate import ensure_optional_columns
from .db.session import engine, SessionLocal
from .db.models import (
    Base,
    CurriculumTrack,
    CurriculumLevel,
    CurriculumSubject,
    CurriculumModule,
    CurriculumTopic,
    CurriculumLesson,
    CurriculumResource,
    LessonQuestion,
    LessonExercise,
    DSATopic,
    UserProgress,
    UserXP,
    RevisionSchedule,
    ProgressState,
    TopicMastery,
)
from .learning.api import router as learning_router
from .learning import service as learning_service
from .learning import revision_engine
from .learning.planner import domain_from_slug
from .learning.streak import get_or_create_streak
from .learning.xp import award_xp, get_or_create_xp

DEFAULT_USER = "akshit"
VALID_PROGRESS_STATES = {state.value for state in ProgressState} | set(UI_LESSON_STATES)
REVISION_INTERVALS = [1, 3, 7, 14, 30, 60]
LESSON_COMPLETE_XP = 10

# Models must be imported before create_all so they register on the shared Base.
Base.metadata.create_all(bind=engine)
ensure_optional_columns(engine)

# Additive track backfill for existing curriculum (idempotent).
with SessionLocal() as _db:
    from .content.backfill_tracks import backfill_topic_tracks
    from .content.domain0_repair import apply_domain0_repairs
    from .learning.projects import seed_projects
    from .content.learner_visibility import (
        apply_learner_visibility,
        restore_content_verification_statuses,
    )

    backfill_topic_tracks(_db)
    apply_domain0_repairs(_db)
    from .content.dsa_practice import enrich_dsa_practice

    enrich_dsa_practice(_db)
    seed_projects(_db)
    # After repairs: restore content-verification statuses, then hide internal resources.
    restore_content_verification_statuses(_db)
    apply_learner_visibility(_db)
    _db.commit()

app = FastAPI(
    title="Akshit Engineering OS API",
    description="Private personal learning platform API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(learning_router)


class DSATopicCreate(BaseModel):
    name: str
    pattern: str = ""
    difficulty: str = ""
    source: str = ""
    url: str = ""
    difficulty_level: str = ""


class QuestionAttemptBody(BaseModel):
    selected: str


class CompletionBody(BaseModel):
    completed: bool = True


class ExerciseAnswerBody(BaseModel):
    answer: Optional[str] = None
    code: Optional[str] = None
    explanation: Optional[str] = None
    complexity: Optional[str] = None


class AssessmentAnswerBody(BaseModel):
    session_id: int
    question_id: int
    selected: str
    timezone: Optional[str] = None


class AssessmentCompleteBody(BaseModel):
    session_id: int
    timezone: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _iso(value: Optional[datetime]) -> Optional[str]:
    return str(value) if value else None


def _serialize_dsa(topic: DSATopic) -> dict[str, Any]:
    return {
        "id": topic.id,
        "name": topic.name,
        "pattern": topic.pattern,
        "difficulty": topic.difficulty,
        "source": topic.source,
        "url": topic.url,
        "solution_notes": topic.solution_notes,
        "attempt_count": topic.attempt_count,
        "time_taken": topic.time_taken,
        "solved_status": topic.solved_status,
        "revision_status": topic.revision_status,
        "last_attempted": _iso(topic.last_attempted),
        "next_revision": _iso(topic.next_revision),
        "personal_notes": topic.personal_notes,
        "difficulty_level": topic.difficulty_level,
    }


def _serialize_progress(progress: UserProgress) -> dict[str, Any]:
    return {
        "id": progress.id,
        "user_id": progress.user_id,
        "lesson_id": progress.lesson_id,
        "topic_id": progress.topic_id,
        "dsa_topic_id": progress.dsa_topic_id,
        "progress_state": progress.progress_state,
        "mastery_status": progress.mastery_status,
        "xp_earned": progress.xp_earned,
        "last_activity_at": _iso(progress.last_activity_at),
        "streak_days": progress.streak_days,
        "total_streak_days": progress.total_streak_days,
    }


def _serialize_xp(xp_record: UserXP) -> dict[str, Any]:
    return {
        "id": xp_record.id,
        "user_id": xp_record.user_id,
        "total_xp": xp_record.total_xp,
        "level": xp_record.level,
        "xp_this_session": xp_record.xp_this_session,
        "sessions_completed": xp_record.sessions_completed,
    }


def _get_or_create_xp(db: Session) -> UserXP:
    return get_or_create_xp(db, DEFAULT_USER)


def _overview_progress(db: Session) -> UserProgress:
    items = db.query(UserProgress).filter(UserProgress.user_id == DEFAULT_USER).all()
    overview = next(
        (
            row
            for row in items
            if row.lesson_id is None and row.topic_id is None and row.dsa_topic_id is None
        ),
        None,
    )
    if overview:
        return overview
    overview = UserProgress(user_id=DEFAULT_USER)
    db.add(overview)
    db.flush()
    return overview


def _revision_interval(confidence: float) -> int:
    index = min(max(int(confidence / 20), 0), len(REVISION_INTERVALS) - 1)
    return REVISION_INTERVALS[index]


def _topics_index(db: Session) -> dict[str, CurriculumTopic]:
    topics = db.query(CurriculumTopic).options(selectinload(CurriculumTopic.lessons)).all()
    index: dict[str, CurriculumTopic] = {}
    for topic in topics:
        if topic.name:
            index[topic.name] = topic
        if topic.slug:
            index[topic.slug] = topic
    return index


def _lock_for_topic(
    topic: CurriculumTopic,
    topics_index: dict[str, CurriculumTopic],
    completion_lookup: Optional[dict[str, bool]] = None,
) -> dict[str, Any]:
    return evaluate_prerequisites(
        topic.prerequisites if topic.prerequisites else [],
        topics_index,
        completion_lookup=completion_lookup,
    )


def _assert_topic_unlocked(topic: CurriculumTopic, topics_index: dict[str, CurriculumTopic]) -> None:
    lock = _lock_for_topic(topic, topics_index)
    if lock["locked"]:
        raise HTTPException(status_code=403, detail={"error": "Topic is locked", **lock})


def _serialize_question_public(question: LessonQuestion) -> dict[str, Any]:
    return {
        "id": question.id,
        "question": question.question,
        "options": question.options or [],
        "difficulty": question.difficulty,
        "mastery_requirement": question.mastery_requirement,
        "attempt_count": question.attempt_count or 0,
        "last_answer": question.last_answer,
        "last_correct": question.last_correct,
    }


def _serialize_resource(resource: CurriculumResource) -> dict[str, Any]:
    return serialize_resource(resource)


def _serialize_exercise(exercise: LessonExercise) -> dict[str, Any]:
    payload = {
        "id": exercise.id,
        "title": exercise.title,
        "description": exercise.description,
        "difficulty": exercise.difficulty,
        "exercise_type": exercise.exercise_type,
        "completion_status": lesson_ui_status(exercise.completion_status),
        "completed": is_lesson_complete(exercise.completion_status),
        "evaluated": bool(exercise.evaluated),
        "user_answer": exercise.user_answer,
        "user_code": exercise.user_code,
        "user_explanation": exercise.user_explanation,
        "user_complexity": exercise.user_complexity,
    }
    if exercise.evaluated or is_lesson_complete(exercise.completion_status):
        payload["correct_answer"] = exercise.correct_answer
    return payload


def _serialize_lesson_summary(lesson: CurriculumLesson) -> dict[str, Any]:
    status = lesson_ui_status(lesson.completion_status)
    return {
        "id": lesson.id,
        "title": lesson.title,
        "description": lesson.description,
        "topic_id": lesson.topic_id,
        "order_index": lesson.order_index,
        "completion_status": status,
        "hours_estimated": lesson.hours_estimated,
    }


def _topic_payload(
    topic: CurriculumTopic,
    topics_by_name: dict[str, CurriculumTopic],
    completion_lookup: Optional[dict[str, bool]] = None,
) -> dict[str, Any]:
    lessons = sorted(topic.lessons, key=lambda item: item.order_index)
    progress = topic_lesson_progress(lessons)
    lock = _lock_for_topic(topic, topics_by_name, completion_lookup)
    status = compose_topic_status(lock["locked"], progress)
    if not lock["locked"] and completion_lookup is not None:
        slug = topic.slug
        if slug and completion_lookup.get(slug):
            status = "completed"
    next_lesson = next((lesson for lesson in lessons if not is_lesson_complete(lesson.completion_status)), None)
    return {
        "id": topic.id,
        "slug": topic.slug,
        "name": topic.name,
        "description": topic.description,
        "module_id": topic.module_id,
        "order_index": topic.order_index,
        "fast_trackable": topic.fast_trackable,
        "prerequisites": lock["items"],
        "locked": lock["locked"],
        "lock_message": lock["message"],
        "status": status,
        "progress": {"completed": progress["completed"], "total": progress["total"], "percent": progress["percent"]},
        "lessons": [_serialize_lesson_summary(lesson) for lesson in lessons],
        "next_lesson_id": None if lock["locked"] else (next_lesson.id if next_lesson else None),
        "hours_estimated": sum((lesson.hours_estimated or 0) for lesson in lessons),
        "domain": domain_from_slug(topic.slug or ""),
        "learning_objective": orientation_from_description(topic.description),
    }


@app.get("/", tags=["Root"])
def root():
    return {"message": "Akshit Engineering OS API", "version": "0.1.0"}


@app.get("/api/health", tags=["Root"])
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/curriculum/tree", tags=["Curriculum"])
def curriculum_tree(db: Session = Depends(get_db)):
    return _curriculum_tree_payload(db)


@app.get("/api/roadmap", tags=["Curriculum"])
def roadmap(db: Session = Depends(get_db)):
    """Roadmap tree: completed / in-progress / next / locked, per topic."""
    return _curriculum_tree_payload(db)


def _curriculum_tree_payload(db: Session) -> dict[str, Any]:
    tracks = (
        db.query(CurriculumTrack)
        .options(
            selectinload(CurriculumTrack.subjects)
            .selectinload(CurriculumSubject.level),
            selectinload(CurriculumTrack.subjects)
            .selectinload(CurriculumSubject.modules)
            .selectinload(CurriculumModule.topics)
            .selectinload(CurriculumTopic.lessons),
        )
        .order_by(CurriculumTrack.order_index)
        .all()
    )
    topics_by_name = _topics_index(db)
    completion_lookup = learning_service.topic_completion_index(db)
    payload, next_action = [], None

    for track in tracks:
        subjects_by_level: dict[int, list[CurriculumSubject]] = {}
        level_order: list[CurriculumLevel] = []
        seen_levels: set[int] = set()
        for subject in sorted(track.subjects, key=lambda item: (item.level.order_index, item.order_index)):
            if subject.level_id not in seen_levels:
                seen_levels.add(subject.level_id)
                level_order.append(subject.level)
            subjects_by_level.setdefault(subject.level_id, []).append(subject)

        level_nodes = []
        for level in level_order:
            subject_nodes = []
            for subject in subjects_by_level.get(level.id, []):
                module_nodes = []
                for module in sorted(subject.modules, key=lambda item: item.order_index):
                    topic_nodes = [
                        _topic_payload(topic, topics_by_name, completion_lookup)
                        for topic in sorted(module.topics, key=lambda item: item.order_index)
                    ]
                    for topic in topic_nodes:
                        if next_action is None and topic["status"] not in {"locked", "completed"}:
                            next_action = {
                                "track_id": track.id,
                                "track_name": track.name,
                                "module_id": module.id,
                                "module_name": module.name,
                                "topic_id": topic["id"],
                                "topic_name": topic["name"],
                                "lesson_id": topic["next_lesson_id"],
                            }
                    module_nodes.append(
                        {
                            "id": module.id,
                            "name": module.name,
                            "description": module.description,
                            "order_index": module.order_index,
                            "progress": module_progress(topic_nodes),
                            "topics": topic_nodes,
                        }
                    )
                subject_nodes.append(
                    {
                        "id": subject.id,
                        "name": subject.name,
                        "description": subject.description,
                        "order_index": subject.order_index,
                        "progress": subject_progress(module_nodes),
                        "modules": module_nodes,
                    }
                )
            level_nodes.append(
                {
                    "id": level.id,
                    "name": level.name,
                    "description": level.description,
                    "order_index": level.order_index,
                    "subjects": subject_nodes,
                }
            )

        subject_count = sum(len(level["subjects"]) for level in level_nodes)
        completed_subjects = sum(
            1
            for level in level_nodes
            for subject in level["subjects"]
            if subject["progress"]["total"] and subject["progress"]["completed"] == subject["progress"]["total"]
        )
        payload.append(
            {
                "id": track.id,
                "name": track.name,
                "description": track.description,
                "order_index": track.order_index,
                "progress": ratio(completed_subjects, subject_count),
                "levels": level_nodes,
            }
        )

    return {"tracks": payload, "next": next_action}


@app.get("/api/tracks", tags=["Curriculum"])
def list_tracks(db: Session = Depends(get_db)):
    tracks = db.query(CurriculumTrack).order_by(CurriculumTrack.order_index).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "order_index": t.order_index,
        }
        for t in tracks
    ]


@app.get("/api/tracks/{track_id}", tags=["Curriculum"])
def get_track(track_id: int, db: Session = Depends(get_db)):
    track = db.get(CurriculumTrack, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return {
        "id": track.id,
        "name": track.name,
        "description": track.description,
        "order_index": track.order_index,
    }


@app.get("/api/levels", tags=["Curriculum"])
def list_levels(db: Session = Depends(get_db)):
    levels = db.query(CurriculumLevel).order_by(CurriculumLevel.order_index).all()
    return [
        {
            "id": l.id,
            "name": l.name,
            "description": l.description,
            "order_index": l.order_index,
        }
        for l in levels
    ]


@app.get("/api/subjects", tags=["Curriculum"])
def list_subjects(db: Session = Depends(get_db)):
    subjects = db.query(CurriculumSubject).order_by(CurriculumSubject.order_index).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "track_id": s.track_id,
            "level_id": s.level_id,
            "order_index": s.order_index,
        }
        for s in subjects
    ]


@app.get("/api/subjects/{subject_id}", tags=["Curriculum"])
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.get(CurriculumSubject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {
        "id": subject.id,
        "name": subject.name,
        "description": subject.description,
        "track_id": subject.track_id,
        "level_id": subject.level_id,
        "order_index": subject.order_index,
    }


@app.get("/api/modules/{subject_id}", tags=["Curriculum"])
def list_modules(subject_id: int, db: Session = Depends(get_db)):
    modules = (
        db.query(CurriculumModule)
        .filter(CurriculumModule.subject_id == subject_id)
        .order_by(CurriculumModule.order_index)
        .all()
    )
    return [
        {
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "subject_id": m.subject_id,
            "order_index": m.order_index,
        }
        for m in modules
    ]


@app.get("/api/topics/{module_id}", tags=["Curriculum"])
def list_topics(module_id: int, db: Session = Depends(get_db)):
    """List topics for a module. Path param is module_id (legacy naming)."""
    module = db.get(CurriculumModule, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    topics = (
        db.query(CurriculumTopic)
        .options(selectinload(CurriculumTopic.lessons))
        .filter(CurriculumTopic.module_id == module_id)
        .order_by(CurriculumTopic.order_index)
        .all()
    )
    topics_by_name = _topics_index(db)
    completion_lookup = learning_service.topic_completion_index(db)
    return [_topic_payload(t, topics_by_name, completion_lookup) for t in topics]


@app.get("/api/prerequisite-bridge/{topic_slug}", tags=["Curriculum"])
def get_prerequisite_bridge(topic_slug: str, db: Session = Depends(get_db)):
    """Just-in-time prerequisite bridge: minimal missing REQUIRED prereqs."""
    from .learning.bridges import prerequisite_bridge as compute_bridge

    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == topic_slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    all_topics = (
        db.query(CurriculumTopic)
        .options(selectinload(CurriculumTopic.lessons))
        .all()
    )
    completion_lookup = learning_service.topic_completion_index(db)

    def lessons_complete(t: CurriculumTopic) -> bool:
        return bool(
            t.lessons
            and all(
                (l.completion_status or "").lower() in ("complete", "completed", "done")
                for l in t.lessons
            )
        )

    completed = {
        t.slug
        for t in all_topics
        if t.slug and (completion_lookup.get(t.slug) or lessons_complete(t))
    }
    topics_map = {
        t.slug: {
            "slug": t.slug,
            "name": t.name,
            "prerequisites": t.prerequisites or [],
            "estimated_minutes": t.estimated_minutes,
        }
        for t in all_topics
        if t.slug
    }
    result = compute_bridge(topic_slug, topics_map, completed)
    result["topic_name"] = topic.name
    return result


@app.get("/api/topic/{topic_id}", tags=["Curriculum"])
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = (
        db.query(CurriculumTopic)
        .options(
            selectinload(CurriculumTopic.lessons).selectinload(CurriculumLesson.questions),
            selectinload(CurriculumTopic.lessons).selectinload(CurriculumLesson.exercises),
            selectinload(CurriculumTopic.lessons).selectinload(CurriculumLesson.resources),
            selectinload(CurriculumTopic.module).selectinload(CurriculumModule.subject),
        )
        .filter(CurriculumTopic.id == topic_id)
        .first()
    )
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    topics_by_name = _topics_index(db)
    payload = _topic_payload(topic, topics_by_name, learning_service.topic_completion_index(db))
    lessons = sorted(topic.lessons, key=lambda item: item.order_index)
    payload["questions"] = [
        _serialize_question_public(question)
        for lesson in lessons
        for question in lesson.questions
    ]
    payload["exercises"] = [
        _serialize_exercise(exercise)
        for lesson in lessons
        for exercise in lesson.exercises
    ]
    implement = []
    transfer = []
    for lesson in lessons:
        for exercise in lesson.exercises:
            blob = f"{exercise.title or ''} {exercise.description or ''}"
            if "TRANSFER" in blob.upper() or "unseen" in blob.lower():
                transfer.append(_serialize_exercise(exercise))
            else:
                implement.append(_serialize_exercise(exercise))
    payload["implement"] = implement
    payload["transfer"] = transfer
    resources = [resource for lesson in lessons for resource in (lesson.resources or [])]
    from app.content.learner_visibility import learner_facing_resources

    learner_resources = learner_facing_resources(resources)
    payload["resources"] = [_serialize_resource(resource) for resource in learner_resources]
    payload["resources_by_role"] = group_resources_by_role(resources, for_learner=True)
    primaries = payload["resources_by_role"].get("PRIMARY") or []
    payload["source_readiness"] = (primaries[0].get("source_readiness") if primaries else "UNRESOLVED")
    mastery_row = (
        db.query(TopicMastery)
        .filter(TopicMastery.user_id == DEFAULT_USER, TopicMastery.topic_id == topic.id)
        .first()
    )
    if mastery_row is None and topic.slug:
        mastery_row = (
            db.query(TopicMastery)
            .filter(TopicMastery.user_id == DEFAULT_USER, TopicMastery.topic_slug == topic.slug)
            .first()
        )
    payload["mastery"] = (
        learning_service.serialize_mastery(mastery_row)
        if mastery_row
        else {
            "topic_id": topic.id,
            "topic_slug": topic.slug,
            "status": "UNKNOWN",
            "mastery_score": None,
            "confidence": 0,
            "attempts": 0,
            "evidence": [],
            "pace_mode": "FOUNDATION",
            "next_review_at": None,
            "has_implementation_evidence": False,
        }
    )
    payload["completion"] = learning_service.topic_completion_state(db, topic)
    payload["assessment"] = learning_service.latest_assessment_summary(db, topic.id)
    payload["pace_mode"] = payload["mastery"]["pace_mode"]
    next_in_sequence = None
    spine = learning_service.official_spine(db)
    for index, item in enumerate(spine):
        if item.id == topic.id and index + 1 < len(spine):
            nxt = spine[index + 1]
            next_in_sequence = {"id": nxt.id, "slug": nxt.slug, "name": nxt.name}
            break
    payload["next_in_sequence"] = next_in_sequence
    subject = topic.module.subject if topic.module else None
    payload["breadcrumb"] = {
        "track_id": subject.track_id if subject else None,
        "level_id": subject.level_id if subject else None,
        "subject_id": subject.id if subject else None,
        "subject_name": subject.name if subject else None,
        "module_id": topic.module_id,
        "module_name": topic.module.name if topic.module else None,
        "topic_id": topic.id,
        "topic_name": topic.name,
    }
    # Study contract — navigation answers without gamification chrome
    primary0 = primaries[0] if primaries else None
    practice_ex = next(
        (
            ex
            for lesson in lessons
            for ex in (lesson.exercises or [])
            if (ex.exercise_type or "").upper() in {"ACTION_CHECKLIST", "CODING", "SELF_REFLECTION"}
            or "PRACTICE" in (ex.title or "").upper()
        ),
        None,
    )
    build_ex = next(
        (
            ex
            for lesson in lessons
            for ex in (lesson.exercises or [])
            if "IMPLEMENT" in ((ex.description or "") + (ex.title or "")).upper()
            or "BUILD" in (ex.title or "").upper()
        ),
        None,
    )
    from app.content.audit import audit_topic

    audit = audit_topic(db, topic.slug) if topic.slug else None
    payload["learning_track"] = getattr(topic, "learning_track", None) or "CORE"
    payload["depth_target"] = getattr(topic, "depth_target", None) or "WORKING_KNOWLEDGE"
    payload["domain_key"] = getattr(topic, "domain_key", None)
    payload["parallel_eligible"] = bool(getattr(topic, "parallel_eligible", False))
    payload["study_contract"] = {
        "why_now": orientation_from_description(topic.description)
        or (lessons[0].description if lessons else None),
        "learn": {
            "title": (primary0 or {}).get("title"),
            "provider": (primary0 or {}).get("provider"),
            "url": (primary0 or {}).get("url"),
            "section": (primary0 or {}).get("section"),
            "lecture": (primary0 or {}).get("lecture"),
            "verification_status": (primary0 or {}).get("verification_status"),
            "exactness": (primary0 or {}).get("exactness"),
            "estimated_minutes": (primary0 or {}).get("estimated_minutes")
            or (int((topic.estimated_minutes or 45))),
            "estimate_confidence": getattr(
                next((r for lesson in lessons for r in (lesson.resources or []) if (r.role or "").upper() == "PRIMARY"), None),
                "estimate_confidence",
                None,
            ),
        },
        "focus_concepts": (audit.required_concepts if audit else [])[:12],
        "practice": {
            "title": practice_ex.title if practice_ex else None,
            "instructions": (
                getattr(practice_ex, "practice_instructions", None)
                or (practice_ex.description if practice_ex else None)
            ),
            "destination_type": getattr(practice_ex, "destination_type", None) if practice_ex else None,
            "destination_url": getattr(practice_ex, "destination_url", None) if practice_ex else None,
            "quantity": getattr(practice_ex, "quantity", None) if practice_ex else None,
        },
        "build": {
            "title": build_ex.title if build_ex else None,
            "instructions": build_ex.description if build_ex else None,
        },
        "done_when": [
            "Finish the LEARN source segment/page listed above",
            "Complete the PRACTICE quantity/destination",
            "Finish BUILD/implement if listed",
        ],
        "next": next_in_sequence,
        "readiness": audit.readiness if audit else None,
        "missing_concepts": audit.missing_required if audit else [],
        "resource_notes": audit.notes if audit else None,
    }
    return payload


@app.post("/api/topic/{topic_id}/complete", tags=["Curriculum"])
def complete_topic(topic_id: int, db: Session = Depends(get_db)):
    """V3 Done action: mark a topic complete (idempotent, no XP, no mastery).

    Completes the topic's lessons and implementation tasks, records the
    topic-level completion, and unlocks the next topic in sequence.
    """
    topic = db.get(CurriculumTopic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    _assert_topic_unlocked(topic, _topics_index(db))
    try:
        result = learning_service.complete_topic(db, topic_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return result


@app.post("/api/exercise/{exercise_id}/complete", tags=["Curriculum"])
def complete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """V3 Build step: mark an implementation task done. No XP or evidence."""
    exercise = db.get(LessonExercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    lesson = db.get(CurriculumLesson, exercise.lesson_id)
    if lesson:
        _assert_topic_unlocked(lesson.topic, _topics_index(db))
    try:
        result = learning_service.mark_exercise_complete(db, exercise_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return result


@app.get("/api/lessons/{topic_id}", tags=["Curriculum"])
def list_lessons(topic_id: int, db: Session = Depends(get_db)):
    topic = db.get(CurriculumTopic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    lessons = (
        db.query(CurriculumLesson)
        .filter(CurriculumLesson.topic_id == topic_id)
        .order_by(CurriculumLesson.order_index)
        .all()
    )
    return [_serialize_lesson_summary(lesson) for lesson in lessons]


@app.get("/api/lesson/{lesson_id}", tags=["Curriculum"])
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = (
        db.query(CurriculumLesson)
        .options(
            selectinload(CurriculumLesson.resources),
            selectinload(CurriculumLesson.questions),
            selectinload(CurriculumLesson.exercises),
            selectinload(CurriculumLesson.topic).selectinload(CurriculumTopic.module),
        )
        .filter(CurriculumLesson.id == lesson_id)
        .first()
    )
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    topics_by_name = _topics_index(db)
    lock = _lock_for_topic(lesson.topic, topics_by_name)
    status = lesson_ui_status(lesson.completion_status)
    return {
        "id": lesson.id,
        "title": lesson.title,
        "description": lesson.description,
        "topic_id": lesson.topic_id,
        "order_index": lesson.order_index,
        "completion_status": status,
        "hours_estimated": lesson.hours_estimated,
        "locked": lock["locked"],
        "lock_message": lock["message"],
        "prerequisites": lock["items"],
        "breadcrumb": {
            "module_id": lesson.topic.module_id if lesson.topic else None,
            "module_name": lesson.topic.module.name if lesson.topic and lesson.topic.module else None,
            "topic_id": lesson.topic_id,
            "topic_name": lesson.topic.name if lesson.topic else None,
            "lesson_id": lesson.id,
            "lesson_title": lesson.title,
        },
        "resources": [
            _serialize_resource(resource)
            for resource in sorted(lesson.resources, key=lambda item: item.order_index)
        ],
        "questions": [_serialize_question_public(question) for question in lesson.questions],
        "exercises": [_serialize_exercise(exercise) for exercise in lesson.exercises],
    }


@app.get("/api/dsa/topics", tags=["DSA"])
def list_dsa_topics(db: Session = Depends(get_db)):
    topics = db.query(DSATopic).order_by(DSATopic.id).all()
    return [_serialize_dsa(t) for t in topics]


@app.post("/api/dsa/topics", tags=["DSA"])
def create_dsa_topic(topic: DSATopicCreate, db: Session = Depends(get_db)):
    new_topic = DSATopic(
        name=topic.name,
        pattern=topic.pattern or None,
        difficulty=topic.difficulty or None,
        source=topic.source or None,
        url=topic.url or None,
        difficulty_level=topic.difficulty_level or None,
    )
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return {"id": new_topic.id, "name": new_topic.name}


@app.get("/api/dsa/topics/{topic_name}", tags=["DSA"])
def get_dsa_topic(topic_name: str, db: Session = Depends(get_db)):
    result = db.query(DSATopic).filter(DSATopic.name == topic_name).first()
    if not result:
        raise HTTPException(status_code=404, detail="DSA topic not found")
    return _serialize_dsa(result)


@app.get("/api/progress", tags=["Progress"])
def get_progress(db: Session = Depends(get_db)):
    overview = _overview_progress(db)
    xp_record = _get_or_create_xp(db)
    streak = get_or_create_streak(db, DEFAULT_USER)
    overview.streak_days = streak.current_streak or 0
    overview.total_streak_days = streak.longest_streak or 0
    db.commit()
    items = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == DEFAULT_USER)
        .order_by(UserProgress.id)
        .all()
    )
    counts = learning_service.mastery_counts(db)
    return {
        "user_id": DEFAULT_USER,
        "streak_days": streak.current_streak or 0,
        "total_streak_days": streak.longest_streak or 0,
        "longest_streak": streak.longest_streak or 0,
        "xp_earned": xp_record.total_xp,
        "level": xp_record.level,
        "topics_mastered": counts.get("MASTERED", 0),
        "topics_learning": counts.get("LEARNING", 0),
        "topics_needs_review": counts.get("NEEDS_REVIEW", 0),
        "items": [_serialize_progress(item) for item in items],
    }


@app.post("/api/progress/lesson/{lesson_id}", tags=["Progress"])
def update_lesson_progress(
    lesson_id: int,
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    if state not in VALID_PROGRESS_STATES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state. Expected one of: {sorted(VALID_PROGRESS_STATES)}",
        )
    lesson = db.get(CurriculumLesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    topics_by_name = _topics_index(db)
    _assert_topic_unlocked(lesson.topic, topics_by_name)

    persisted = normalize_lesson_state(state)
    if persisted not in UI_LESSON_STATES:
        persisted = lesson_ui_status(state)

    already_complete = is_lesson_complete(lesson.completion_status)

    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == DEFAULT_USER, UserProgress.lesson_id == lesson_id)
        .first()
    )
    if not progress:
        progress = UserProgress(user_id=DEFAULT_USER, lesson_id=lesson_id)
        db.add(progress)

    progress.progress_state = persisted
    progress.last_activity_at = datetime.now(timezone.utc)
    lesson.completion_status = persisted
    xp_awarded = 0
    if persisted == "completed" and not already_complete:
        xp_awarded = learning_service.on_lesson_completed(db, lesson)
        progress.xp_earned = (progress.xp_earned or 0) + xp_awarded
        # Lesson completion is progress, not automatic MASTERED.
        progress.mastery_status = "learning"
    db.commit()
    db.refresh(progress)
    result = _serialize_progress(progress)
    result["completion_status"] = persisted
    result["xp_awarded"] = xp_awarded
    return result


@app.post("/api/progress/resource/{resource_id}", tags=["Progress"])
def update_resource_progress(
    resource_id: int,
    body: CompletionBody,
    db: Session = Depends(get_db),
):
    resource = db.get(CurriculumResource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    if resource.lesson_id:
        lesson = db.get(CurriculumLesson, resource.lesson_id)
        if lesson:
            _assert_topic_unlocked(lesson.topic, _topics_index(db))
    resource.completion_status = "completed" if body.completed else "not_started"
    db.commit()
    db.refresh(resource)
    return _serialize_resource(resource)


@app.post("/api/progress/exercise/{exercise_id}", tags=["Progress"])
def update_exercise_progress(
    exercise_id: int,
    body: CompletionBody,
    db: Session = Depends(get_db),
):
    exercise = db.get(LessonExercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    lesson = db.get(CurriculumLesson, exercise.lesson_id)
    if lesson:
        _assert_topic_unlocked(lesson.topic, _topics_index(db))
    already_complete = is_lesson_complete(exercise.completion_status)
    exercise.completion_status = "completed" if body.completed else "not_started"
    exercise.attempted_at = datetime.now(timezone.utc)
    xp_awarded = 0
    if body.completed and not already_complete:
        xp_awarded = learning_service.on_exercise_completed(db, exercise)
    db.commit()
    db.refresh(exercise)
    result = _serialize_exercise(exercise)
    result["xp_awarded"] = xp_awarded
    return result


@app.post("/api/questions/{question_id}/attempt", tags=["Progress"])
def attempt_question(
    question_id: int,
    body: QuestionAttemptBody,
    db: Session = Depends(get_db),
):
    """Practice attempt: idempotent state on the question, never cumulative.

    Updates last_answer / last_correct / attempt_count / last_attempt_at and
    records activity. No XP and no mastery evidence: a topic's score changes
    only when an assessment session is completed.
    """
    question = db.get(LessonQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    lesson = db.get(CurriculumLesson, question.lesson_id)
    if lesson:
        _assert_topic_unlocked(lesson.topic, _topics_index(db))
    selected = (body.selected or "").strip()
    expected = (question.answer or "").strip()
    correct = selected.lower() == expected.lower()
    question.attempt_count = (question.attempt_count or 0) + 1
    question.last_answer = selected
    question.last_correct = correct
    question.last_attempt_at = datetime.now(timezone.utc)
    learning_service.record_question_activity(db, question_id=question.id)
    db.commit()
    db.refresh(question)
    payload = _serialize_question_public(question)
    payload.update(
        {
            "correct": correct,
            "answer": question.answer,
            "explanation": question.explanation,
            "xp_awarded": 0,
        }
    )
    return payload


@app.post("/api/exercise/{exercise_id}/answer", tags=["Progress"])
def answer_exercise(
    exercise_id: int,
    body: ExerciseAnswerBody,
    db: Session = Depends(get_db),
):
    """Answer an exercise by its declared type.

    NUMERIC and SHORT_ANSWER are evaluated (lenient compare) with retry until
    correct; CODE, SELF_REFLECTION and ACTION_CHECKLIST are self-evaluated and
    recorded, never executed in a sandbox.
    """
    exercise = db.get(LessonExercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    lesson = db.get(CurriculumLesson, exercise.lesson_id)
    if lesson:
        _assert_topic_unlocked(lesson.topic, _topics_index(db))

    exercise_type = (exercise.exercise_type or "SELF_REFLECTION").upper()
    evaluated = False
    correct: Optional[bool] = None
    already_complete = is_lesson_complete(exercise.completion_status)

    if exercise_type in {"NUMERIC", "SHORT_ANSWER"}:
        evaluated = True
        submitted = (body.answer or "").strip()
        expected = (exercise.correct_answer or "").strip()
        correct = _lenient_answer_match(submitted, expected, numeric=exercise_type == "NUMERIC")
        exercise.user_answer = submitted
        exercise.evaluated = True
        if correct:
            exercise.completion_status = "completed"
    elif exercise_type == "CODE":
        exercise.user_code = body.code or ""
        exercise.user_explanation = body.explanation
        exercise.user_complexity = body.complexity or ""
        exercise.evaluated = True
        exercise.completion_status = "completed"
    else:
        exercise.user_answer = (body.answer or body.code or "").strip()
        exercise.evaluated = True
        exercise.completion_status = "completed"

    exercise.attempted_at = datetime.now(timezone.utc)
    xp_awarded = 0
    if is_lesson_complete(exercise.completion_status) and not already_complete:
        if exercise_type in {"NUMERIC", "SHORT_ANSWER"} and not correct:
            correct = False
        xp_awarded = learning_service.on_exercise_completed(db, exercise)
    db.commit()
    db.refresh(exercise)
    payload = _serialize_exercise(exercise)
    payload.update(
        {
            "correct": correct,
            "xp_awarded": xp_awarded,
            "evaluated": evaluated,
        }
    )
    return payload


def _lenient_answer_match(submitted: str, expected: str, *, numeric: bool) -> bool:
    """Lenient answer comparison without inventing semantics.

    Numeric: strips whitespace, commas, and unit words; compares as floats.
    Short answer: lowercase, single-space normalized comparison.
    """
    if not submitted or not expected:
        return False
    if numeric:
        def _to_float(value: str) -> Optional[float]:
            token = value.strip().replace(",", "").lower()
            import re

            match = re.match(r"^([+-]?\d+\.?\d*)", token)
            return float(match.group(1)) if match else None

        left = _to_float(submitted)
        right = _to_float(expected)
        if left is None or right is None:
            return False
        abs_diff = abs(left - right)
        scale = max(abs(left), abs(right), 1.0)
        return abs_diff <= 1e-6 * scale
    return " ".join(submitted.lower().split()) == " ".join(expected.lower().split())


@app.post("/api/assessment/topic/{topic_id}/start", tags=["Assessment"])
def start_assessment(topic_id: int, db: Session = Depends(get_db)):
    topic = db.get(CurriculumTopic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    _assert_topic_unlocked(topic, _topics_index(db))
    try:
        result = learning_service.assessment_start(db, topic_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return result


@app.get("/api/assessment/{session_id}", tags=["Assessment"])
def get_assessment(session_id: int, db: Session = Depends(get_db)):
    try:
        return learning_service.assessment_state(db, session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/assessment/answer", tags=["Assessment"])
def answer_assessment(body: AssessmentAnswerBody, db: Session = Depends(get_db)):
    try:
        result = learning_service.assessment_answer(
            db,
            session_id=body.session_id,
            question_id=body.question_id,
            selected=body.selected,
            timezone_name=body.timezone,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return result


@app.post("/api/assessment/complete", tags=["Assessment"])
def complete_assessment(body: AssessmentCompleteBody, db: Session = Depends(get_db)):
    try:
        result = learning_service.assessment_complete(
            db,
            body.session_id,
            timezone_name=body.timezone,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return result


@app.post("/api/progress/dsa/{topic_id}", tags=["Progress"])
def update_dsa_progress(
    topic_id: int,
    solved: bool,
    time_taken: float = 0,
    db: Session = Depends(get_db),
):
    dsa_topic = db.get(DSATopic, topic_id)
    if not dsa_topic:
        raise HTTPException(status_code=404, detail="DSA topic not found")

    dsa_topic.attempt_count = (dsa_topic.attempt_count or 0) + 1
    dsa_topic.solved_status = solved
    if time_taken > 0:
        dsa_topic.time_taken = time_taken
    dsa_topic.last_attempted = datetime.now(timezone.utc)
    if solved:
        dsa_topic.revision_status = "mastered"

    db.commit()
    db.refresh(dsa_topic)
    return {
        "id": dsa_topic.id,
        "name": dsa_topic.name,
        "attempt_count": dsa_topic.attempt_count,
        "solved_status": dsa_topic.solved_status,
        "revision_status": dsa_topic.revision_status,
    }


@app.get("/api/xp", tags=["XP"])
def get_xp(db: Session = Depends(get_db)):
    xp_record = _get_or_create_xp(db)
    db.commit()
    db.refresh(xp_record)
    return _serialize_xp(xp_record)


@app.post("/api/xp/award", tags=["XP"])
def award_xp_endpoint(
    amount: int = Query(..., ge=0),
    activity: str = Query(...),
    idempotency_key: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    from uuid import uuid4

    key = idempotency_key or f"manual:{uuid4()}"
    awarded, xp_record = award_xp(
        db,
        idempotency_key=key,
        amount=amount,
        activity=activity,
    )
    db.commit()
    db.refresh(xp_record)
    result = _serialize_xp(xp_record)
    result["xp_awarded"] = awarded
    return result


@app.post("/api/revision/schedule", tags=["Revision"])
def schedule_revision(
    item_id: int,
    item_type: str,
    confidence: float,
    db: Session = Depends(get_db),
):
    if confidence < 0 or confidence > 100:
        raise HTTPException(status_code=400, detail="confidence must be between 0 and 100")

    now = datetime.now(timezone.utc)

    existing = (
        db.query(RevisionSchedule)
        .filter(
            RevisionSchedule.user_id == DEFAULT_USER,
            RevisionSchedule.item_id == item_id,
            RevisionSchedule.item_type == item_type,
        )
        .first()
    )

    if not existing:
        # Seed with the initial ladder step (+1 day) before applying the attempt.
        existing = RevisionSchedule(
            user_id=DEFAULT_USER,
            item_id=item_id,
            item_type=item_type,
            confidence=confidence,
            last_reviewed=now,
            next_review=now + timedelta(days=_revision_interval(confidence)),
            review_interval=_revision_interval(confidence),
        )
        db.add(existing)
        db.flush()

    revision_engine.schedule_update(existing, confidence, now=now)
    db.commit()
    db.refresh(existing)
    return {
        "id": existing.id,
        "item_id": existing.item_id,
        "item_type": existing.item_type,
        "confidence": existing.confidence,
        "review_interval": existing.review_interval,
        "next_review": _iso(existing.next_review),
        "last_reviewed": _iso(existing.last_reviewed),
        "ease": round(float(existing.ease), 2),
        "retrieval_success_count": existing.retrieval_success_count,
        "retrieval_fail_count": existing.retrieval_fail_count,
    }


@app.get("/api/revision/pending", tags=["Revision"])
def get_pending_revisions(db: Session = Depends(get_db)):
    return learning_service.pending_revisions(db)
