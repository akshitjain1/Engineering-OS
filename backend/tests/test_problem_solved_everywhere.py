"""A problem you have solved is solved wherever the mapping shows it.

57 problems are pinned to more than one topic; Two Sum alone sits under five.
Each was its own row with its own tick, so solving Two Sum under Algorithmic
thinking left it reading "Mark solved" when Big-O served it the next day. The
app was asking whether you had done something it already knew you had.

What must NOT spread is a non-problem source. The same article can be mapped to
two topics for different sections, and reading one is not reading the other.
"""

from __future__ import annotations

import pytest

from app.db import models
from app.db.session import Base, SessionLocal, engine
from app.learning import service

TWO_SUM = "https://leetcode.com/problems/two-sum/"
ARTICLE = "https://www.geeksforgeeks.org/some-article/"


@pytest.fixture
def two_topics():
    """Two topics that both pin Two Sum, and both pin the same article."""
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

        made = {}
        for i, (slug, name) in enumerate(
            [("dsa-algo", "Algorithmic thinking"), ("dsa-hash", "Hash map")]
        ):
            topic = models.CurriculumTopic(
                slug=slug, name=name, module_id=module.id, order_index=i
            )
            db.add(topic)
            db.flush()
            lesson = models.CurriculumLesson(
                slug=f"{slug}-l1", title=name, topic_id=topic.id, order_index=1
            )
            db.add(lesson)
            db.flush()
            problem = models.CurriculumResource(
                slug=f"{slug}-two-sum", title="1. Two Sum", url=TWO_SUM,
                resource_type="coding_problem", lesson_id=lesson.id, role="PRACTICE",
                order_index=0, completion_status="not_started",
            )
            article = models.CurriculumResource(
                slug=f"{slug}-article", title="An article", url=ARTICLE,
                resource_type="documentation", lesson_id=lesson.id, role="PRIMARY",
                order_index=1, completion_status="not_started",
            )
            db.add_all([problem, article])
            db.flush()
            made[name] = {"topic": topic.id, "problem": problem.id, "article": article.id}
        db.commit()
        yield db, made
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _status(db, resource_id):
    return db.get(models.CurriculumResource, resource_id).completion_status


def test_solving_a_problem_marks_it_solved_in_every_topic(two_topics):
    db, made = two_topics
    here = db.get(models.CurriculumResource, made["Algorithmic thinking"]["problem"])

    service.set_problem_solved(db, here, True)
    db.commit()

    assert _status(db, made["Hash map"]["problem"]) == "completed", (
        "the same problem under another topic still reads unsolved"
    )


def test_unsolving_also_travels(two_topics):
    """Otherwise a mistaken tick can only be undone in the topic you made it."""
    db, made = two_topics
    here = db.get(models.CurriculumResource, made["Algorithmic thinking"]["problem"])
    service.set_problem_solved(db, here, True)
    db.commit()
    service.set_problem_solved(db, here, False)
    db.commit()

    assert _status(db, made["Hash map"]["problem"]) == "not_started"


def test_an_article_does_not_spread(two_topics):
    """Two topics can point at one article for different sections."""
    db, made = two_topics
    here = db.get(models.CurriculumResource, made["Algorithmic thinking"]["article"])

    service.set_problem_solved(db, here, True)
    db.commit()

    assert _status(db, made["Algorithmic thinking"]["article"]) == "completed"
    assert _status(db, made["Hash map"]["article"]) == "not_started", (
        "reading an article for one topic was counted as reading it for another"
    )


def test_finishing_a_topic_spreads_its_problems(two_topics):
    """The completion cascade goes through the same rule."""
    db, made = two_topics

    service.complete_topic(db, made["Algorithmic thinking"]["topic"])
    db.commit()

    assert _status(db, made["Hash map"]["problem"]) == "completed"
    assert _status(db, made["Hash map"]["article"]) == "not_started"


def test_the_topic_payload_names_the_other_topics(client, two_topics):
    """So a pre-ticked problem can explain itself instead of looking wrong."""
    db, made = two_topics
    payload = client.get(f"/api/topic/{made['Algorithmic thinking']['topic']}").json()
    practice = (payload.get("resources_by_role") or {}).get("PRACTICE") or []
    assert practice, "the fixture's problem is missing from the payload"
    assert practice[0]["also_in_topics"] == ["Hash map"]
