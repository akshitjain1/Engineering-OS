"""The study contract must describe the page, not promise work that isn't there.

The contract panel is the one place that tells you what today requires. On 191
topics it read "Complete 3 exercises on cf-storage" while the topic had one
exercise and no PRACTICE resource at all -- the panel whose whole job is to be
authoritative was the panel making things up.

These pin the two halves: an overclaim is replaced by what the page actually
offers, and a real instruction is still passed through untouched.
"""

from __future__ import annotations

from app.db import models


def _topic_with(db, *, exercises: int, quantity: int | None, practice_resources: int = 0):
    """A topic carrying `exercises` exercise rows, the first claiming `quantity`."""
    track = models.CurriculumTrack(slug="t", name="Track", order_index=1)
    level = models.CurriculumLevel(slug="l", name="Level", order_index=1)
    db.add_all([track, level])
    db.flush()
    subject = models.CurriculumSubject(
        slug="s", name="Subject", track_id=track.id, level_id=level.id, order_index=1
    )
    db.add(subject)
    db.flush()
    module = models.CurriculumModule(slug="m", name="Module", subject_id=subject.id, order_index=1)
    db.add(module)
    db.flush()
    topic = models.CurriculumTopic(slug="cf-storage", name="Storage", module_id=module.id,
                                   order_index=1)
    db.add(topic)
    db.flush()
    lesson = models.CurriculumLesson(slug="cf-storage-l1", title="Storage", topic_id=topic.id,
                                     order_index=1)
    db.add(lesson)
    db.flush()

    for i in range(exercises):
        db.add(models.LessonExercise(
            lesson_id=lesson.id,
            title=f"Exercise {i + 1}",
            description="Do the thing.",
            exercise_type="CODING",
            practice_instructions=f"Complete {quantity} exercises on cf-storage.",
            quantity=quantity if i == 0 else None,
        ))
    for i in range(practice_resources):
        db.add(models.CurriculumResource(
            slug=f"prac-{i}", title=f"Practice {i}", url="https://example.com/p",
            resource_type="documentation", lesson_id=lesson.id, role="PRACTICE",
            order_index=i,
        ))
    db.commit()
    return topic


def test_overclaimed_practice_is_replaced_by_what_the_page_offers(client):
    """One exercise, no practice resource, a contract claiming three."""
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        topic = _topic_with(db, exercises=1, quantity=3)
        topic_id = topic.id
    finally:
        db.close()

    contract = client.get(f"/api/topic/{topic_id}").json()["study_contract"]["practice"]

    assert contract["quantity"] is None, "a quantity nothing can satisfy must not be published"
    assert "Complete 3 exercises" not in (contract["instructions"] or "")
    assert "practice prompt" in (contract["instructions"] or "")
    assert "recall questions" in (contract["instructions"] or "")


def test_done_when_matches_the_replaced_practice(client):
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        topic_id = _topic_with(db, exercises=1, quantity=3).id
    finally:
        db.close()

    done_when = client.get(f"/api/topic/{topic_id}").json()["study_contract"]["done_when"]
    joined = " ".join(done_when)
    assert "PRACTICE quantity/destination" not in joined, (
        "the checklist still points at a quantity that was withdrawn"
    )
    assert "recall questions" in joined


def test_a_claim_the_topic_can_meet_is_left_alone(client):
    """Three exercises and a claim of three: nothing is overclaimed, nothing changes."""
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        topic_id = _topic_with(db, exercises=3, quantity=3).id
    finally:
        db.close()

    contract = client.get(f"/api/topic/{topic_id}").json()["study_contract"]["practice"]
    assert contract["quantity"] == 3
    assert "Complete 3 exercises" in (contract["instructions"] or "")


def test_a_mapped_practice_resource_keeps_the_original_instruction(client):
    """With somewhere to practise, the row is trusted even if the count is high.

    The replacement is for topics with nothing mapped. A topic that has a
    practice resource has a destination, so its instruction still means
    something.
    """
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        topic_id = _topic_with(db, exercises=1, quantity=3, practice_resources=1).id
    finally:
        db.close()

    contract = client.get(f"/api/topic/{topic_id}").json()["study_contract"]["practice"]
    assert contract["quantity"] == 3
    assert "Complete 3 exercises" in (contract["instructions"] or "")
