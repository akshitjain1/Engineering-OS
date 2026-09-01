"""Day session engine tests.

Coverage contract:
1.  every budget yields exactly one DSA block, and DSA is never dropped
2.  complete_item returns the next open item and the status survives a reload
3.  a forced regenerate keeps done and skipped items
4.  a skipped item is not re-added by a regenerate
5.  revision-weighted mode shrinks LEARN, grows DSA, and still yields one DSA
"""

import pytest

from app.db.models import (
    CurriculumLesson,
    CurriculumLevel,
    CurriculumModule,
    CurriculumResource,
    CurriculumSubject,
    CurriculumTopic,
    CurriculumTrack,
)
from app.db.session import SessionLocal
from app.learning import day_engine, service
from app.learning.day_models import DailyPlanItem

BUDGETS = [90, 150, 240]


def _seed_curriculum() -> dict:
    """A core lane and a DSA lane, so both cursors resolve."""
    db = SessionLocal()
    try:
        track = CurriculumTrack(name="SE-DAY", order_index=0)
        level = CurriculumLevel(name="L1", order_index=0)
        db.add_all([track, level])
        db.flush()

        core_subject = CurriculumSubject(
            name="Foundations", track_id=track.id, level_id=level.id, order_index=0
        )
        dsa_subject = CurriculumSubject(
            name="Data Structures & Algorithms",
            track_id=track.id,
            level_id=level.id,
            order_index=1,
        )
        db.add_all([core_subject, dsa_subject])
        db.flush()

        core_module = CurriculumModule(name="Hardware", subject_id=core_subject.id, order_index=0)
        dsa_module = CurriculumModule(name="Arrays", subject_id=dsa_subject.id, order_index=0)
        db.add_all([core_module, dsa_module])
        db.flush()

        core_topics = []
        for i, name in enumerate(["RAM", "CPU", "Disks"]):
            topic = CurriculumTopic(
                name=name,
                slug=f"cf-{name.lower()}",
                module_id=core_module.id,
                order_index=i,
                prerequisites=[],
                domain_key="computer-fundamentals",
                estimated_minutes=40,
            )
            core_topics.append(topic)

        dsa_topics = []
        for i, name in enumerate(["Two pointers", "Sliding window", "Prefix sums"]):
            topic = CurriculumTopic(
                name=name,
                slug=f"dsa-{name.lower().replace(' ', '-')}",
                module_id=dsa_module.id,
                order_index=i,
                prerequisites=[],
                domain_key="dsa",
                estimated_minutes=45,
            )
            dsa_topics.append(topic)

        db.add_all(core_topics + dsa_topics)
        db.flush()

        for topic in core_topics + dsa_topics:
            lesson = CurriculumLesson(title=f"{topic.name} core", topic_id=topic.id, order_index=0)
            db.add(lesson)
            db.flush()
            db.add(
                CurriculumResource(
                    title=f"{topic.name} primary",
                    url=f"https://example.test/{topic.slug}",
                    resource_type="article",
                    role="PRIMARY",
                    lesson_id=lesson.id,
                    order_index=0,
                )
            )
        db.commit()
        return {
            "core_ids": [t.id for t in core_topics],
            "dsa_ids": [t.id for t in dsa_topics],
        }
    finally:
        db.close()


def _generate(budget: int, force: bool = False) -> dict:
    db = SessionLocal()
    try:
        day = day_engine.generate_day(db, budget_minutes=budget, force=force)
        db.commit()
        return day
    finally:
        db.close()


def _dsa_items(day: dict) -> list[dict]:
    return [item for item in day["items"] if item["activity_type"] == "DSA"]


def _learn_items(day: dict) -> list[dict]:
    return [item for item in day["items"] if item["activity_type"] == "LEARN"]


def _set_revision_weighted(value: bool) -> None:
    db = SessionLocal()
    try:
        service.update_study_settings(db, revision_weighted=value)
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 1. Exactly one DSA block at every budget
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("budget", BUDGETS)
def test_one_dsa_block_at_every_budget(client, budget):
    seed = _seed_curriculum()
    day = _generate(budget)

    dsa = _dsa_items(day)
    assert len(dsa) == 1, f"budget {budget} produced {len(dsa)} DSA blocks"
    # It tracks the DSA cursor, not the core cursor.
    assert dsa[0]["topic_id"] == seed["dsa_ids"][0]
    assert dsa[0]["planned_minutes"] > 0


@pytest.mark.parametrize("budget", [30, 45, 60])
def test_dsa_survives_a_budget_too_small_to_fit_it(client, budget):
    """DSA is non-droppable: a tiny budget drops other blocks, never this one."""
    _seed_curriculum()
    day = _generate(budget)
    assert len(_dsa_items(day)) == 1


# ---------------------------------------------------------------------------
# 2. complete_item returns the next item and persists
# ---------------------------------------------------------------------------


def test_complete_item_returns_next_and_persists(client):
    _seed_curriculum()
    day = _generate(150)
    first, second = day["items"][0], day["items"][1]

    db = SessionLocal()
    try:
        result = day_engine.complete_item(db, first["id"], minutes=20)
        db.commit()
        assert result["item"]["id"] == first["id"]
        assert result["item"]["status"] == "done"
        assert result["item"]["actual_minutes"] == 20
        assert result["next"] is not None
        assert result["next"]["id"] == second["id"]
    finally:
        db.close()

    # Reload from a fresh session: the write is on disk, not just in the response.
    db = SessionLocal()
    try:
        row = db.get(DailyPlanItem, first["id"])
        assert row.status == "done"
        assert row.actual_minutes == 20
        assert row.completed_at is not None
        reloaded = day_engine.get_day(db)
        assert reloaded["totals"]["items_done"] == 1
        assert reloaded["current_item_id"] == second["id"]
    finally:
        db.close()


def test_complete_last_item_has_no_next(client):
    _seed_curriculum()
    day = _generate(150)

    db = SessionLocal()
    try:
        result = None
        for item in day["items"]:
            result = day_engine.complete_item(db, item["id"])
        db.commit()
        assert result is not None
        assert result["next"] is None
        assert day_engine.get_day(db)["totals"]["complete"] is True
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 3 & 4. Forced regenerate preserves settled work
# ---------------------------------------------------------------------------


def test_forced_regenerate_preserves_done_and_skipped(client):
    _seed_curriculum()
    day = _generate(150)
    assert len(day["items"]) >= 3

    done_item = day["items"][0]
    skipped_item = day["items"][1]

    db = SessionLocal()
    try:
        day_engine.complete_item(db, done_item["id"], minutes=30)
        day_engine.skip_item(db, skipped_item["id"], reason="not today")
        db.commit()
    finally:
        db.close()

    after = _generate(150, force=True)
    by_id = {item["id"]: item for item in after["items"]}

    assert done_item["id"] in by_id, "a forced regenerate dropped a completed block"
    assert by_id[done_item["id"]]["status"] == "done"
    assert by_id[done_item["id"]]["actual_minutes"] == 30

    assert skipped_item["id"] in by_id, "a forced regenerate dropped a skipped block"
    assert by_id[skipped_item["id"]]["status"] == "skipped"


def test_skipped_item_is_not_re_added_on_regenerate(client):
    _seed_curriculum()
    day = _generate(150)
    dsa = _dsa_items(day)[0]

    db = SessionLocal()
    try:
        day_engine.skip_item(db, dsa["id"], reason="rest day")
        db.commit()
    finally:
        db.close()

    after = _generate(150, force=True)
    dsa_after = _dsa_items(after)

    # Still exactly one DSA block -- the skipped one. Regenerating must not
    # hand the same block back as fresh work.
    assert len(dsa_after) == 1
    assert dsa_after[0]["id"] == dsa["id"]
    assert dsa_after[0]["status"] == "skipped"


# ---------------------------------------------------------------------------
# 5. Revision-weighted mode
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("budget", BUDGETS)
def test_revision_mode_still_yields_exactly_one_dsa_block(client, budget):
    seed = _seed_curriculum()
    _set_revision_weighted(True)
    day = _generate(budget, force=True)

    dsa = _dsa_items(day)
    assert len(dsa) == 1, f"revision budget {budget} produced {len(dsa)} DSA blocks"
    assert dsa[0]["topic_id"] == seed["dsa_ids"][0]
    assert dsa[0]["planned_minutes"] > 0


@pytest.mark.parametrize("budget", BUDGETS)
def test_revision_mode_shifts_minutes_from_learn_to_dsa(client, budget):
    _seed_curriculum()

    _set_revision_weighted(False)
    normal = _generate(budget, force=True)
    normal_learn = _learn_items(normal)[0]["planned_minutes"]
    normal_dsa = _dsa_items(normal)[0]["planned_minutes"]

    _set_revision_weighted(True)
    revised = _generate(budget, force=True)
    revised_learn = _learn_items(revised)[0]["planned_minutes"]
    revised_dsa = _dsa_items(revised)[0]["planned_minutes"]

    assert revised_learn < normal_learn, "revision mode did not shrink LEARN"
    assert revised_dsa > normal_dsa, "revision mode did not grow DSA"


def test_revision_mode_leaves_practice_and_reflect_alone(client):
    _seed_curriculum()

    _set_revision_weighted(False)
    normal = _generate(150, force=True)
    _set_revision_weighted(True)
    revised = _generate(150, force=True)

    def targets(day, activity):
        return [i["planned_minutes"] for i in day["items"] if i["activity_type"] == activity]

    assert targets(revised, "REFLECT") == targets(normal, "REFLECT")
    # The topic-bound PRACTICE block keeps its own budget; only LEARN and DSA move.
    assert targets(revised, "PRACTICE")[:1] == targets(normal, "PRACTICE")[:1]


def test_revision_mode_defaults_off(client):
    _seed_curriculum()
    db = SessionLocal()
    try:
        assert service.get_or_create_study_settings(db).revision_weighted is False
        assert service.serialize_study_settings(
            service.get_or_create_study_settings(db)
        )["revision_weighted"] is False
    finally:
        db.close()
