"""Fixing a resource must fix the day that points at it.

A plan item stores its own copy of the resource title, provider and URL,
written when the day was generated. That froze mistakes as well as facts:
"System calls" pointed at MIT's *Debugging and Profiling* lecture, the
curriculum row was corrected to a page about system calls, and today's screen
went on offering the old link -- because it was reading its own snapshot, not
the row.

Two weeks of "you said you fixed this and it is still wrong" has this shape.
The copy is now a fallback; the row is the answer.
"""

from __future__ import annotations

import pytest

from app.db import models
from app.db.session import SessionLocal
from app.learning import day_engine
from app.learning.day_models import DailyPlanItem
from app.learning.streak import local_today


@pytest.fixture
def day_with_one_resource(client):
    """A one-item day whose block points at a curriculum resource."""
    db = SessionLocal()
    track = models.CurriculumTrack(slug="t", name="Track", order_index=1)
    level = models.CurriculumLevel(slug="l", name="Level", order_index=1)
    db.add_all([track, level])
    db.flush()
    subject = models.CurriculumSubject(slug="s", name="Subject", track_id=track.id,
                                       level_id=level.id, order_index=1)
    db.add(subject)
    db.flush()
    module = models.CurriculumModule(slug="m", name="Module", subject_id=subject.id,
                                     order_index=1)
    db.add(module)
    db.flush()
    topic = models.CurriculumTopic(slug="cf-system-calls", name="System calls",
                                   module_id=module.id, order_index=1,
                                   domain_key="foundations")
    db.add(topic)
    db.flush()
    lesson = models.CurriculumLesson(slug="l1", title="System calls",
                                     topic_id=topic.id, order_index=1)
    db.add(lesson)
    db.flush()
    resource = models.CurriculumResource(
        slug="r1", title="MIT Missing Semester - Debugging and Profiling",
        url="https://missing.csail.mit.edu/2026/debugging-profiling/",
        resource_type="documentation", lesson_id=lesson.id, role="PRIMARY",
        order_index=0, learner_visible=True, provider="MIT",
    )
    db.add(resource)
    db.flush()

    item = DailyPlanItem(
        user_id=day_engine.DEFAULT_USER,
        plan_date=local_today(),
        position=0,
        activity_type=day_engine.ACTIVITY_LEARN,
        title="System calls",
        topic_id=topic.id,
        topic_slug=topic.slug,
        domain="foundations",
        resource_id=resource.id,
        resource_title=resource.title,
        resource_provider="MIT",
        resource_url=resource.url,
        resource_kind="reading",
        planned_minutes=45,
        status="pending",
    )
    db.add(item)
    db.commit()
    try:
        yield db, resource, item
    finally:
        db.close()


def _resource_of_first_block(db):
    return day_engine.get_day(db)["items"][0]["resource"]


def test_correcting_the_resource_corrects_todays_block(day_with_one_resource):
    """The reported bug, end to end."""
    db, resource, _item = day_with_one_resource

    resource.url = "https://www.geeksforgeeks.org/operating-systems/introduction-of-system-call/"
    resource.title = "System Call"
    resource.provider = "GeeksforGeeks"
    db.commit()

    served = _resource_of_first_block(db)
    assert served["url"].endswith("/introduction-of-system-call/")
    assert served["title"] == "System Call"
    assert served["provider"] == "GeeksforGeeks"


def test_a_completed_block_is_corrected_too(day_with_one_resource):
    """Deliberate: a finished block still shows the right page.

    Keeping the old link would be defensible as a record of what was opened,
    but the day screen is a place you go back to in order to re-read something,
    and pointing it at a link we know is wrong makes it useless for that.
    """
    db, resource, item = day_with_one_resource
    item.status = "done"
    resource.url = "https://www.geeksforgeeks.org/operating-systems/introduction-of-system-call/"
    db.commit()

    assert "geeksforgeeks" in _resource_of_first_block(db)["url"]


def test_the_frozen_copy_is_used_when_the_row_is_gone(day_with_one_resource):
    """A deleted resource must not blank the block.

    The snapshot stops being the source of truth but keeps being the safety
    net: a day that shows nothing to open is worse than one showing a stale
    title.
    """
    db, resource, _item = day_with_one_resource
    db.delete(resource)
    db.commit()

    served = _resource_of_first_block(db)
    assert served is not None
    assert served["url"] == "https://missing.csail.mit.edu/2026/debugging-profiling/"


def test_a_row_with_no_url_falls_back_rather_than_serving_nothing(day_with_one_resource):
    db, resource, _item = day_with_one_resource
    resource.url = ""
    db.commit()

    served = _resource_of_first_block(db)
    assert served is not None and served["url"].startswith("https://missing.csail.mit.edu")


def test_a_block_with_no_resource_stays_without_one(day_with_one_resource):
    db, _resource, item = day_with_one_resource
    item.resource_id = None
    item.resource_url = None
    db.commit()

    assert _resource_of_first_block(db) is None
