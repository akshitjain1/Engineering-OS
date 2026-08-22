from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    CurriculumLesson,
    CurriculumLevel,
    CurriculumModule,
    CurriculumResource,
    CurriculumSubject,
    CurriculumTopic,
    CurriculumTrack,
    LessonExercise,
    LessonQuestion,
)
from .resources import metadata_from_spec
from .schema import (
    CurriculumManifest,
    ExerciseSpec,
    LessonSpec,
    ModuleSpec,
    QuestionSpec,
    ResourceSpec,
    SubjectSpec,
    TopicSpec,
)
from .validate import validate_manifest


PROGRESS_LESSON_FIELDS = {"completion_status", "mastery_status", "confidence"}
PROGRESS_RESOURCE_FIELDS = {"completion_status"}
PROGRESS_QUESTION_FIELDS = {"last_answer", "attempt_count", "last_correct"}
PROGRESS_EXERCISE_FIELDS = {
    "completion_status",
    "time_taken",
    "attempted_at",
    "solution_notes",
    "evaluated",
    "user_answer",
    "user_code",
    "user_explanation",
    "user_complexity",
}


def import_manifest(db: Session, data: dict[str, Any]) -> dict[str, int]:
    existing_topic_slugs = {
        slug for (slug,) in db.query(CurriculumTopic.slug).filter(CurriculumTopic.slug.is_not(None))
    }
    manifest = validate_manifest(data, existing_topic_slugs=existing_topic_slugs)
    stats = {"created": 0, "updated": 0, "unchanged": 0, "skipped_resources": 0}
    try:
        _apply(db, manifest, stats)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return stats


def _apply(db: Session, manifest: CurriculumManifest, stats: dict[str, int]) -> None:
    track = _upsert(
        db,
        CurriculumTrack,
        manifest.track.slug,
        {
            "name": manifest.track.name,
            "description": manifest.track.description,
            "order_index": manifest.track.order,
        },
        match_name=True,
        stats=stats,
    )
    for level_spec in manifest.track.levels:
        level = _upsert(
            db,
            CurriculumLevel,
            level_spec.slug,
            {
                "name": level_spec.name,
                "description": level_spec.description,
                "order_index": level_spec.order,
            },
            match_name=True,
            stats=stats,
        )
        for subject_spec in level_spec.subjects:
            _apply_subject(db, track, level, subject_spec, stats)


def _apply_subject(db: Session, track, level, spec: SubjectSpec, stats: dict[str, int]) -> None:
    subject = _upsert(
        db,
        CurriculumSubject,
        spec.slug,
        {
            "name": spec.name,
            "description": spec.description,
            "order_index": spec.order,
            "track_id": track.id,
            "level_id": level.id,
        },
        match_name=True,
        stats=stats,
    )
    for module_spec in spec.modules:
        _apply_module(db, subject, module_spec, stats)


def _apply_module(db: Session, subject, spec: ModuleSpec, stats: dict[str, int]) -> None:
    module = _upsert(
        db,
        CurriculumModule,
        spec.slug,
        {
            "name": spec.name,
            "description": spec.description,
            "order_index": spec.order,
            "subject_id": subject.id,
        },
        match_filters={"subject_id": subject.id, "name": spec.name},
        stats=stats,
    )
    for topic_spec in spec.topics:
        _apply_topic(db, module, topic_spec, stats)


def _topic_description(spec: TopicSpec) -> str:
    parts = []
    if spec.description:
        parts.append(spec.description.strip())
    if spec.learning_objective:
        parts.append(f"Objective: {spec.learning_objective.strip()}")
    if spec.mastery_criteria:
        bullets = "\n".join(f"- {item}" for item in spec.mastery_criteria)
        parts.append("Mastery:\n" + bullets)
    if spec.next_topic:
        parts.append(f"Next topic: {spec.next_topic}")
    return "\n\n".join(parts) if parts else spec.description


def _apply_topic(db: Session, module, spec: TopicSpec, stats: dict[str, int]) -> None:
    fields: dict = {
        "name": spec.name,
        "description": spec.description,
        "order_index": spec.order,
        "module_id": module.id,
        "prerequisites": list(spec.prerequisites),
        "fast_trackable": spec.fast_trackable,
        "description": _topic_description(spec),
    }
    if spec.learning_track is not None:
        fields["learning_track"] = spec.learning_track
    if spec.depth_target is not None:
        fields["depth_target"] = spec.depth_target
    if spec.parallel_eligible is not None:
        fields["parallel_eligible"] = spec.parallel_eligible
    if spec.estimated_minutes is not None:
        fields["estimated_minutes"] = spec.estimated_minutes
    if spec.domain_key is not None:
        fields["domain_key"] = spec.domain_key
    topic = _upsert(
        db,
        CurriculumTopic,
        spec.slug,
        fields,
        match_filters={"module_id": module.id, "name": spec.name},
        stats=stats,
    )
    for lesson_spec in spec.lessons:
        _apply_lesson(db, topic, lesson_spec, stats)


def _apply_lesson(db: Session, topic, spec: LessonSpec, stats: dict[str, int]) -> None:
    lesson = _upsert(
        db,
        CurriculumLesson,
        spec.slug,
        {
            "title": spec.title,
            "description": spec.description,
            "order_index": spec.order,
            "topic_id": topic.id,
            "hours_estimated": spec.hours_estimated,
        },
        match_filters={"topic_id": topic.id, "title": spec.title},
        preserve=PROGRESS_LESSON_FIELDS,
        stats=stats,
    )
    for resource in spec.resources:
        _apply_resource(db, lesson, resource, stats)
    for question in spec.questions:
        _apply_question(db, lesson, question, stats)
    for exercise in spec.exercises:
        _apply_exercise(db, lesson, exercise, stats)


def _apply_resource(db: Session, lesson, spec: ResourceSpec, stats: dict[str, int]) -> None:
    if not spec.url:
        stats["skipped_resources"] = stats.get("skipped_resources", 0) + 1
        return
    meta = metadata_from_spec(
        url=spec.url,
        resource_type=spec.type,
        role=spec.role,
        section=spec.section,
        lecture=spec.lecture,
        video_id=spec.video_id,
        verification_status=spec.verification_status,
    )
    _upsert(
        db,
        CurriculumResource,
        spec.slug,
        {
            "title": spec.title,
            "url": spec.url,
            "resource_type": spec.type,
            "provider": spec.provider,
            "description": spec.description,
            "duration": spec.duration,
            "difficulty": spec.difficulty,
            "official_unofficial": "official" if spec.official else "unofficial",
            "order_index": spec.order,
            "lesson_id": lesson.id,
            **meta,
        },
        match_filters={"lesson_id": lesson.id, "url": spec.url},
        preserve=PROGRESS_RESOURCE_FIELDS,
        stats=stats,
    )


def _apply_question(db: Session, lesson, spec: QuestionSpec, stats: dict[str, int]) -> None:
    _upsert(
        db,
        LessonQuestion,
        spec.slug,
        {
            "question": spec.prompt,
            "answer": spec.answer,
            "options": list(spec.options),
            "explanation": spec.explanation,
            "difficulty": spec.difficulty,
            "mastery_requirement": spec.mastery_requirement,
            "lesson_id": lesson.id,
        },
        match_filters={"lesson_id": lesson.id, "question": spec.prompt},
        preserve=PROGRESS_QUESTION_FIELDS,
        stats=stats,
    )


def _apply_exercise(db: Session, lesson, spec: ExerciseSpec, stats: dict[str, int]) -> None:
    _upsert(
        db,
        LessonExercise,
        spec.slug,
        {
            "title": spec.title,
            "description": spec.instructions,
            "difficulty": spec.difficulty,
            "lesson_id": lesson.id,
            "exercise_type": spec.type or "SELF_REFLECTION",
            "correct_answer": spec.answer,
        },
        match_filters={"lesson_id": lesson.id, "title": spec.title},
        preserve=PROGRESS_EXERCISE_FIELDS,
        stats=stats,
    )


def _upsert(
    db: Session,
    model,
    slug: str,
    values: dict[str, Any],
    stats: dict[str, int],
    match_name: bool = False,
    match_filters: dict[str, Any] | None = None,
    preserve: set[str] | None = None,
):
    preserve = preserve or set()
    row = db.query(model).filter(model.slug == slug).first()
    if row is None and match_name and "name" in values:
        row = db.query(model).filter(model.name == values["name"]).first()
    if row is None and match_filters:
        row = db.query(model).filter_by(**match_filters).first()
    if row is None:
        row = model(slug=slug, **values)
        db.add(row)
        db.flush()
        stats["created"] += 1
        return row

    changed = False
    if getattr(row, "slug", None) != slug:
        row.slug = slug
        changed = True
    for key, value in values.items():
        if key in preserve:
            continue
        if getattr(row, key) != value:
            setattr(row, key, value)
            changed = True
    stats["updated" if changed else "unchanged"] += 1
    db.flush()
    return row
