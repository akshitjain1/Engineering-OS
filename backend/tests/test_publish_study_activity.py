"""What Engineering OS hands to the study-activity repo must be what happened.

That repo's bot renders activity.json into a public daily log and then empties
it. So an entry here becomes a line in a log that stands as a record of the
day -- claiming a problem you did not solve, or the same one twice, makes the
record worth less than no record.

Two properties carry the weight: only finished work is reported, and running
the publisher twice in a day leaves one line per topic rather than two.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.db import models
from app.db.session import Base, SessionLocal, engine
from scripts.publish_study_activity import SEPARATOR, key_of, merge, summarise_day

DAY = "2026-09-03"


@pytest.fixture
def db_with_day():
    """A day with a finished LEARN topic, a finished DSA topic, and an abandoned one."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

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

    made = {}
    for i, (slug, name) in enumerate(
        [("cf-storage", "Storage"), ("dsa-bigo", "Big-O notation"), ("dsa-bwa", "Best, worst, average")]
    ):
        topic = models.CurriculumTopic(slug=slug, name=name, module_id=module.id, order_index=i)
        db.add(topic)
        db.flush()
        lesson = models.CurriculumLesson(
            slug=f"{slug}-l1", title=name, topic_id=topic.id, order_index=1
        )
        db.add(lesson)
        db.flush()
        made[name] = {"topic": topic.id, "lesson": lesson.id}
    db.commit()
    try:
        yield db, made
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _item(db, **kw):
    from app.learning.day_models import DailyPlanItem

    defaults = dict(
        user_id="akshit", plan_date=DAY, position=0, title="x", planned_minutes=10,
        actual_minutes=10, status="done",
    )
    defaults.update(kw)
    db.add(DailyPlanItem(**defaults))
    db.commit()


def _completed_today(db, topic_id):
    db.add(models.UserProgress(
        user_id="akshit", topic_id=topic_id, progress_state="completed",
        last_activity_at=datetime(2026, 9, 3, 12, 0, 0),
    ))
    db.commit()


def _problem(db, lesson_id, title, slug, done=True):
    db.add(models.CurriculumResource(
        slug=slug, title=title, url=f"https://leetcode.com/problems/{slug}/",
        resource_type="coding_problem", lesson_id=lesson_id, role="PRACTICE",
        order_index=0, completion_status="completed" if done else "not_started",
    ))
    db.commit()


def test_only_finished_blocks_are_reported(db_with_day):
    db, made = db_with_day
    _item(db, activity_type="LEARN", title="Storage", topic_id=made["Storage"]["topic"],
          actual_minutes=18)
    _item(db, activity_type="LEARN", title="Abandoned", topic_id=made["Big-O notation"]["topic"],
          position=1, actual_minutes=5, status="active")

    out = summarise_day(db, DAY)
    assert out["learning"] == [f"Storage{SEPARATOR}18 min"]
    assert out["dsa"] == []


def test_learn_and_practice_minutes_add_up_per_topic(db_with_day):
    db, made = db_with_day
    tid = made["Storage"]["topic"]
    _item(db, activity_type="LEARN", title="Storage", topic_id=tid, actual_minutes=18)
    _item(db, activity_type="PRACTICE", title="Practice: Storage", topic_id=tid, position=1,
          actual_minutes=15)

    assert summarise_day(db, DAY)["learning"] == [f"Storage{SEPARATOR}33 min"]


def test_a_dsa_topic_lists_the_problems_it_finished(db_with_day):
    db, made = db_with_day
    tid, lid = made["Big-O notation"]["topic"], made["Big-O notation"]["lesson"]
    _item(db, activity_type="DSA", title="DSA: Big-O notation", topic_id=tid, actual_minutes=42)
    _completed_today(db, tid)
    _problem(db, lid, "1. Two Sum", "two-sum")

    assert summarise_day(db, DAY)["dsa"] == [
        f"Big-O notation{SEPARATOR}42 min (solved: 1. Two Sum)"
    ]


def test_an_unfinished_dsa_topic_claims_no_problems(db_with_day):
    """Completing the topic is what marks its problems solved, so before that
    there is nothing to report."""
    db, made = db_with_day
    tid, lid = made["Big-O notation"]["topic"], made["Big-O notation"]["lesson"]
    _item(db, activity_type="DSA", title="DSA: Big-O notation", topic_id=tid, actual_minutes=42)
    _problem(db, lid, "1. Two Sum", "two-sum")

    entry = summarise_day(db, DAY)["dsa"][0]
    assert entry == f"Big-O notation{SEPARATOR}42 min"
    assert "solved" not in entry


def test_a_problem_in_two_topics_is_counted_once(db_with_day):
    """Two Sum is pinned to five topics. A day that finishes two of them still
    solved it once, and a log saying otherwise is inflating the record."""
    db, made = db_with_day
    for i, name in enumerate(["Big-O notation", "Best, worst, average"]):
        tid, lid = made[name]["topic"], made[name]["lesson"]
        _item(db, activity_type="DSA", title=f"DSA: {name}", topic_id=tid, position=i,
              actual_minutes=20)
        _completed_today(db, tid)
        _problem(db, lid, "1. Two Sum", f"two-sum-{i}")

    mentions = sum(e.count("1. Two Sum") for e in summarise_day(db, DAY)["dsa"])
    assert mentions == 1, "the same problem was reported under both topics"


def test_build_blocks_become_projects(db_with_day):
    db, made = db_with_day
    _item(db, activity_type="BUILD", title="Ship the parser", topic_id=None, actual_minutes=45)
    assert summarise_day(db, DAY)["projects"] == [f"Ship the parser{SEPARATOR}45 min"]


def test_reflect_and_review_are_not_logged(db_with_day):
    """Closing the day is not study material."""
    db, _ = db_with_day
    _item(db, activity_type="REFLECT", title="Close the day", topic_id=None, actual_minutes=2)
    _item(db, activity_type="REVIEW", title="Recall 2 due items", topic_id=None, position=1,
          actual_minutes=8)

    out = summarise_day(db, DAY)
    assert out == {"dsa": [], "projects": [], "learning": []}


def test_publishing_twice_leaves_one_line_per_topic():
    """The app is opened and closed more than once a day."""
    first = merge({"dsa": [], "projects": [], "learning": []},
                  {"dsa": [], "projects": [], "learning": [f"Storage{SEPARATOR}18 min"]})
    second = merge(first,
                   {"dsa": [], "projects": [], "learning": [f"Storage{SEPARATOR}33 min"]})

    assert second["learning"] == [f"Storage{SEPARATOR}33 min"], (
        "a second run appended a duplicate instead of updating the count"
    )


def test_entries_you_wrote_by_hand_survive():
    existing = {"dsa": ["Grinding neetcode75 on my own"], "projects": [], "learning": []}
    out = merge(existing, {"dsa": [f"Big-O notation{SEPARATOR}42 min"], "projects": [],
                           "learning": []})
    assert "Grinding neetcode75 on my own" in out["dsa"]
    assert len(out["dsa"]) == 2


def test_unknown_keys_in_the_file_are_preserved():
    """The repo's schema is not ours to prune."""
    out = merge({"dsa": [], "projects": [], "learning": [], "notes": ["keep me"]},
                {"dsa": [], "projects": [], "learning": []})
    assert out["notes"] == ["keep me"]


def test_key_is_the_text_before_the_separator():
    assert key_of(f"Best, worst, average{SEPARATOR}15 min (solved: x)") == "Best, worst, average"
