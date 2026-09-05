"""Time you set aside must come back as work, not as a suggestion.

A 250-minute weekend produced 210 minutes of curriculum and a 40-minute block
titled "Extra reps", whose instruction was "pick one: more DSA problems on
today's pattern, or re-derive this week's hardest topic from a blank page".
That is the planner handing the planning back at the exact moment the plan was
the thing being asked for.

There are a hundred more DSA topics and three hundred more core topics. If the
budget has room, the day should name what fills it.
"""

from __future__ import annotations

import pytest

from app.db import models
from app.db.session import Base, SessionLocal, engine
from app.learning import day_engine


@pytest.fixture
def curriculum():
    """A spine with several core and several DSA topics, each with a source."""
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

    order = 0
    for domain, count in (("foundations", 4), ("dsa", 4)):
        for n in range(count):
            slug = f"{domain}-{n}"
            topic = models.CurriculumTopic(
                slug=slug, name=f"{domain.title()} {n}", module_id=module.id,
                order_index=order, domain_key=domain,
            )
            db.add(topic)
            db.flush()
            lesson = models.CurriculumLesson(
                slug=f"{slug}-l", title=slug, topic_id=topic.id, order_index=1
            )
            db.add(lesson)
            db.flush()
            db.add(models.CurriculumResource(
                slug=f"{slug}-r", title=f"Read {slug}", url=f"https://example.com/{slug}",
                resource_type="documentation", lesson_id=lesson.id, role="PRIMARY",
                order_index=0, learner_visible=True,
            ))
            order += 1
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _blocks(db, budget, plan_date="2026-09-05"):
    return day_engine.build_blocks(db, budget_minutes=budget, plan_date=plan_date)


def _named(blocks):
    return [b for b in blocks if b.topic is not None]


def test_a_large_budget_produces_no_generic_filler(curriculum):
    """The exact report: 250 minutes, and a block called "Extra reps"."""
    blocks = _blocks(curriculum, 250)

    titles = [b.title for b in blocks]
    assert "Extra reps" not in titles, f"filler is back: {titles}"


def test_the_extra_time_lands_on_a_real_topic(curriculum):
    """Not just "no filler" -- the minutes must buy something with a name."""
    small = _blocks(curriculum, 120)
    large = _blocks(curriculum, 250)

    assert len(_named(large)) > len(_named(small)), (
        "a bigger budget scheduled no additional topic"
    )
    for block in _named(large):
        assert block.topic is not None and block.topic.name


def test_every_extra_block_carries_a_source(curriculum):
    """A block you cannot start is not better than filler."""
    for block in _named(_blocks(curriculum, 300)):
        if block.activity_type in (day_engine.ACTIVITY_LEARN, day_engine.ACTIVITY_DSA):
            assert block.resource is not None, f"{block.title} has nothing to open"


def test_no_topic_is_taught_twice_in_one_day(curriculum):
    """A big budget must reach new topics, not re-serve the cursor's answer.

    Counted over LEARN and DSA only: a PRACTICE block shares its LEARN block's
    topic by design, which is the pair working as intended and not a duplicate.
    """
    blocks = _blocks(curriculum, 300)
    teaching = [
        b for b in _named(blocks)
        if b.activity_type in (day_engine.ACTIVITY_LEARN, day_engine.ACTIVITY_DSA)
    ]
    ids = [b.topic.id for b in teaching]

    assert len(ids) == len(set(ids)), f"a topic was taught twice: {ids}"


def test_practice_stays_paired_with_its_own_topic(curriculum):
    """The other half of the rule above: PRACTICE must not drift onto a topic
    the day never taught."""
    blocks = _blocks(curriculum, 300)
    taught = {b.topic.id for b in _named(blocks)
              if b.activity_type in (day_engine.ACTIVITY_LEARN, day_engine.ACTIVITY_DSA)}

    for block in _named(blocks):
        if block.activity_type == day_engine.ACTIVITY_PRACTICE:
            assert block.topic.id in taught, (
                f"practice on {block.topic.name}, which today never taught"
            )


def test_reflect_still_closes_the_day(curriculum):
    """Extra blocks are inserted before it, never after."""
    blocks = _blocks(curriculum, 250)
    assert blocks[-1].activity_type == day_engine.ACTIVITY_REFLECT


def test_a_small_budget_is_unchanged(curriculum):
    """Nothing extra is invented when there is no room for it."""
    blocks = _blocks(curriculum, 90)
    assert "Extra reps" not in [b.title for b in blocks]
    kinds = [b.activity_type for b in blocks]
    assert kinds.count(day_engine.ACTIVITY_DSA) == 1


def test_an_exhausted_curriculum_does_not_loop_or_crash(curriculum):
    """When there is nothing left to schedule, stop -- do not spin."""
    db = curriculum
    for topic in db.query(models.CurriculumTopic).all():
        db.add(models.UserProgress(
            user_id="akshit", topic_id=topic.id, progress_state="completed",
        ))
    db.commit()

    blocks = _blocks(db, 300)  # must return rather than hang
    assert _named(blocks) == []
