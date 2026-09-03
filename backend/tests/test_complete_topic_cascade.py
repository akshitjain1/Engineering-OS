"""Finishing a topic finishes the work it asked of you.

"Done — next block" with "Finished this topic" ticked completed the lessons and
the exercises and then left every resource reading "Not consumed" -- including
the source you had just spent the whole block reading. The app already knew you
were done; it asked you to say so a second time by hand.

What it must NOT do is tick material the flow never routes you through. Ticking
a Deep Dive nobody opened is the same failure in the other direction: the page
claiming you read something you did not.
"""

from __future__ import annotations

import pytest

from app.db import models
from app.db.session import Base, SessionLocal, engine
from app.learning import service


@pytest.fixture
def topic_with_resources():
    """A topic carrying one resource of every role, plus an exercise.

    The suite shares one in-memory database, so the schema is rebuilt here --
    otherwise the second test to run collides on a slug the first inserted.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        track = models.CurriculumTrack(slug="t", name="Track", order_index=1)
        level = models.CurriculumLevel(slug="l", name="Level", order_index=1)
        db.add_all([track, level])
        db.flush()
        subject = models.CurriculumSubject(
            slug="s", name="Subject", track_id=track.id, level_id=level.id, order_index=1
        )
        db.add(subject)
        db.flush()
        module = models.CurriculumModule(
            slug="m", name="Module", subject_id=subject.id, order_index=1
        )
        db.add(module)
        db.flush()
        topic = models.CurriculumTopic(
            slug="cf-storage", name="Storage", module_id=module.id, order_index=1
        )
        db.add(topic)
        db.flush()
        lesson = models.CurriculumLesson(
            slug="cf-storage-l1", title="Storage", topic_id=topic.id, order_index=1
        )
        db.add(lesson)
        db.flush()

        for i, role in enumerate(["PRIMARY", "PRACTICE", "REFERENCE", "SUPPLEMENT", "DEEP_DIVE"]):
            db.add(models.CurriculumResource(
                slug=f"r-{role.lower()}", title=role.title(), url="https://example.com/x",
                resource_type="documentation", lesson_id=lesson.id, role=role,
                order_index=i, completion_status="not_started", learner_visible=True,
            ))
        db.add(models.LessonExercise(
            lesson_id=lesson.id, title="Save vs run", description="Do it.",
            exercise_type="CODING", completion_status="not_started",
        ))
        db.commit()
        yield db, topic.id
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _by_role(db, topic_id):
    rows = (
        db.query(models.CurriculumResource)
        .join(models.CurriculumLesson,
              models.CurriculumLesson.id == models.CurriculumResource.lesson_id)
        .filter(models.CurriculumLesson.topic_id == topic_id)
        .all()
    )
    return {r.role: r.completion_status for r in rows}


def test_finishing_a_topic_consumes_the_source_you_just_read(topic_with_resources):
    db, topic_id = topic_with_resources
    assert _by_role(db, topic_id)["PRIMARY"] == "not_started"

    service.complete_topic(db, topic_id)
    db.commit()

    assert _by_role(db, topic_id)["PRIMARY"] == "completed", (
        "the source the block sent you to read is still unconsumed"
    )


def test_finishing_a_topic_consumes_its_practice(topic_with_resources):
    db, topic_id = topic_with_resources
    service.complete_topic(db, topic_id)
    db.commit()
    assert _by_role(db, topic_id)["PRACTICE"] == "completed"


def test_optional_material_is_left_alone(topic_with_resources):
    """Deep dives and references are never routed to, so they are never claimed."""
    db, topic_id = topic_with_resources
    service.complete_topic(db, topic_id)
    db.commit()

    roles = _by_role(db, topic_id)
    for role in ("REFERENCE", "SUPPLEMENT", "DEEP_DIVE"):
        assert roles[role] == "not_started", (
            f"{role} was marked consumed though nothing ever asked you to open it"
        )


def test_exercises_and_lessons_still_complete(topic_with_resources):
    db, topic_id = topic_with_resources
    service.complete_topic(db, topic_id)
    db.commit()

    lesson = db.query(models.CurriculumLesson).filter(
        models.CurriculumLesson.topic_id == topic_id).one()
    assert lesson.completion_status == "completed"
    exercise = db.query(models.LessonExercise).filter(
        models.LessonExercise.lesson_id == lesson.id).one()
    assert exercise.completion_status == "completed"


def test_completion_is_still_idempotent(topic_with_resources):
    db, topic_id = topic_with_resources
    service.complete_topic(db, topic_id)
    db.commit()
    first = _by_role(db, topic_id)

    service.complete_topic(db, topic_id)
    db.commit()
    assert _by_role(db, topic_id) == first

    rows = db.query(models.UserProgress).filter(
        models.UserProgress.topic_id == topic_id,
        models.UserProgress.lesson_id.is_(None),
    ).all()
    assert len(rows) == 1, "a second completion added another progress row"


def test_hidden_resources_are_not_touched(topic_with_resources):
    """Verification-only rows are not learner material and stay as they are."""
    db, topic_id = topic_with_resources
    lesson = db.query(models.CurriculumLesson).filter(
        models.CurriculumLesson.topic_id == topic_id).one()
    hidden = models.CurriculumResource(
        slug="r-hidden", title="Hidden", url="https://example.com/h",
        resource_type="documentation", lesson_id=lesson.id, role="PRIMARY",
        order_index=99, completion_status="not_started", learner_visible=False,
    )
    db.add(hidden)
    db.commit()

    service.complete_topic(db, topic_id)
    db.commit()
    db.refresh(hidden)
    assert hidden.completion_status == "not_started"
