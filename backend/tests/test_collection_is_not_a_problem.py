"""A problem set is not a problem, and the topic page must not treat it as one.

Two consequences showed up on the same card:

1.  "Solving it once counts for all of them" is a true and useful thing to say
    about Two Sum, which four topics pin. Said about a section index it is
    nonsense -- and because all 128 NeetCode rows share the single URL
    https://neetcode.io/practice/practice/neetcode150, the query behind it
    returned every topic that maps any part of NeetCode 150. The card printed
    about ninety topic names under a nine-problem set, headed "Solved already
    - this problem also belongs to".

2.  The row is a set of nine problems worth ~195 minutes, so it needs to carry
    its count and its difficulty spread, not just one number.
"""

from __future__ import annotations

import pytest

from app.db import models
from app.db.session import SessionLocal

NEETCODE = "https://neetcode.io/practice/practice/neetcode150"
TWO_SUM = "https://leetcode.com/problems/two-sum/"


@pytest.fixture
def two_topics(client):
    """Two topics that both pin the same set page and the same single problem."""
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

    ids = []
    for n, name in enumerate(("Array traversal", "Hash map")):
        topic = models.CurriculumTopic(slug=f"dsa-t{n}", name=name, module_id=module.id,
                                       order_index=n, domain_key="dsa")
        db.add(topic)
        db.flush()
        lesson = models.CurriculumLesson(slug=f"l{n}", title=name, topic_id=topic.id,
                                         order_index=1)
        db.add(lesson)
        db.flush()
        db.add(models.CurriculumResource(
            slug=f"nc{n}", title="NeetCode 150 — Arrays & Hashing (representative subset)",
            url=NEETCODE, resource_type="coding_problem", lesson_id=lesson.id,
            role="PRACTICE", order_index=0, learner_visible=True, provider="NeetCode",
            verification_status="VERIFIED", exactness="COLLECTION",
            estimated_minutes=195, item_count=9,
            difficulty_mix={"easy": 3, "medium": 6, "hard": 0},
            estimate_method="neetcode_section_sum",
        ))
        db.add(models.CurriculumResource(
            slug=f"ts{n}", title="1. Two Sum", url=TWO_SUM,
            resource_type="coding_problem", lesson_id=lesson.id, role="PRACTICE",
            order_index=1, learner_visible=True, provider="LeetCode",
            verification_status="VERIFIED", exactness="EXACT",
            estimated_minutes=15, difficulty="Easy",
        ))
        ids.append(topic.id)
    db.commit()
    db.close()
    return ids


def _practice(client, topic_id):
    payload = client.get(f"/api/topic/{topic_id}").json()
    rows = payload["resources_by_role"]["PRACTICE"]
    return {r["slug"]: r for r in rows}


def test_a_set_does_not_claim_to_belong_to_other_topics(client, two_topics):
    """The reported card: ninety topic names under a nine-problem set."""
    rows = _practice(client, two_topics[0])
    assert rows["nc0"]["also_in_topics"] == []


def test_a_single_problem_still_says_where_else_it_counts(client, two_topics):
    """The other half. Suppressing this everywhere would hide a real fact: a
    problem arriving already ticked looks broken unless the page says why."""
    rows = _practice(client, two_topics[0])
    assert rows["ts0"]["also_in_topics"] == ["Hash map"]


def test_a_set_is_marked_as_a_set(client, two_topics):
    rows = _practice(client, two_topics[0])
    assert rows["nc0"]["is_collection"] is True
    assert rows["ts0"]["is_collection"] is False


def test_a_set_carries_its_size_and_spread(client, two_topics):
    """One number cannot say "nine problems, three easy and six medium"."""
    row = _practice(client, two_topics[0])["nc0"]
    assert row["item_count"] == 9
    assert row["difficulty_mix"] == {"easy": 3, "medium": 6, "hard": 0}
    assert row["estimated_minutes"] == 195


def test_the_estimate_says_how_it_was_reached(client, two_topics):
    """A default and a measurement must not look alike. Every NeetCode row
    carried a flat 20 with this field empty."""
    rows = _practice(client, two_topics[0])
    assert rows["nc0"]["estimate_method"] == "neetcode_section_sum"


def test_an_unverified_single_problem_is_not_mistaken_for_a_set(client):
    """`exactness_label` returns "Collection" as its fallback, so an
    unverified single problem reads as a collection there. Using that label to
    decide would have suppressed the shared-problem note on real problems."""
    db = SessionLocal()
    track = models.CurriculumTrack(slug="t2", name="T", order_index=1)
    level = models.CurriculumLevel(slug="l2", name="L", order_index=1)
    db.add_all([track, level])
    db.flush()
    subject = models.CurriculumSubject(slug="s2", name="S", track_id=track.id,
                                       level_id=level.id, order_index=1)
    db.add(subject)
    db.flush()
    module = models.CurriculumModule(slug="m2", name="M", subject_id=subject.id,
                                     order_index=1)
    db.add(module)
    db.flush()
    topic = models.CurriculumTopic(slug="dsa-x", name="Reversal", module_id=module.id,
                                   order_index=0, domain_key="dsa")
    db.add(topic)
    db.flush()
    lesson = models.CurriculumLesson(slug="lx", title="Reversal", topic_id=topic.id,
                                     order_index=1)
    db.add(lesson)
    db.flush()
    db.add(models.CurriculumResource(
        slug="unver", title="206. Reverse Linked List",
        url="https://leetcode.com/problems/reverse-linked-list/",
        resource_type="coding_problem", lesson_id=lesson.id, role="PRACTICE",
        order_index=0, learner_visible=True, provider="LeetCode",
        verification_status="NEEDS_REVIEW", exactness="EXACT", estimated_minutes=15,
    ))
    db.commit()
    topic_id = topic.id
    db.close()

    row = _practice(client, topic_id)["unver"]
    assert row["exactness"] == "Collection", "fixture no longer reproduces the trap"
    assert row["is_collection"] is False
