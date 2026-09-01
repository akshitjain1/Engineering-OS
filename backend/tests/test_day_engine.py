"""Day session engine tests.

Coverage contract:
1.  every budget yields exactly one DSA block, and DSA is never dropped
2.  complete_item returns the next open item and the status survives a reload
3.  a forced regenerate keeps done and skipped items
4.  a skipped item is not re-added by a regenerate
5.  revision-weighted mode shrinks LEARN, grows DSA, and still yields one DSA
6.  extend_day appends a fresh cycle on uncovered topics, never rebuilds
7.  get_day is read-only and reports needs_generation
8.  finishing a LEARN/DSA topic feeds the spaced-review queue
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
from app.db.models import RevisionSchedule
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


# ---------------------------------------------------------------------------
# 6. extend_day
# ---------------------------------------------------------------------------


def _settle_everything(day: dict) -> None:
    db = SessionLocal()
    try:
        for item in day["items"]:
            day_engine.complete_item(db, item["id"], minutes=11)
        db.commit()
    finally:
        db.close()


def _extend(minutes: int = 60) -> dict:
    db = SessionLocal()
    try:
        result = day_engine.extend_day(db, minutes=minutes)
        db.commit()
        return result
    finally:
        db.close()


def test_extend_appends_one_full_cycle(client):
    _seed_curriculum()
    day = _generate(150)
    _settle_everything(day)

    before = {i["id"] for i in day["items"]}
    result = _extend(60)
    added = [i for i in result["items"] if i["id"] not in before]

    assert sorted(i["activity_type"] for i in added) == ["DSA", "LEARN", "PRACTICE"]
    assert result["first_new_item_id"] == added[0]["id"]
    assert result["message"] is None


def test_extend_never_touches_settled_items(client):
    _seed_curriculum()
    day = _generate(150)
    _settle_everything(day)

    db = SessionLocal()
    try:
        baseline = {
            row.id: (row.status, row.actual_minutes, row.planned_minutes, row.title)
            for row in db.query(DailyPlanItem).all()
        }
    finally:
        db.close()

    _extend(60)

    db = SessionLocal()
    try:
        for item_id, snapshot in baseline.items():
            row = db.get(DailyPlanItem, item_id)
            assert row is not None, f"extend deleted settled item {item_id}"
            assert (row.status, row.actual_minutes, row.planned_minutes, row.title) == snapshot
    finally:
        db.close()


def test_extend_advances_even_when_topic_never_marked_complete(client):
    """The whole point: no complete_topic tick, and it still moves on."""
    _seed_curriculum()
    day = _generate(150)
    db = SessionLocal()
    try:
        for item in day["items"]:
            # complete_topic defaults to False -- topics stay incomplete.
            day_engine.complete_item(db, item["id"], minutes=11)
        db.commit()
    finally:
        db.close()

    covered = {i["topic_id"] for i in day["items"] if i["topic_id"]}
    before = {i["id"] for i in day["items"]}
    result = _extend(60)
    added = [i for i in result["items"] if i["id"] not in before]

    new_topics = {i["topic_id"] for i in added if i["topic_id"]}
    assert new_topics, "extend produced no topic-bound blocks"
    assert not (new_topics & covered), "extend re-served a topic already covered today"


def test_extend_keeps_reflect_last_and_never_duplicates_it(client):
    _seed_curriculum()
    day = _generate(150)
    _settle_everything(day)

    result = _extend(60)
    reflects = [i for i in result["items"] if i["activity_type"] == "REFLECT"]
    assert len(reflects) == 1
    assert reflects[0]["position"] == max(i["position"] for i in result["items"])


def test_two_extends_yield_four_distinct_topics(client):
    _seed_curriculum()
    day = _generate(150)
    _settle_everything(day)

    ids_after_day = {i["id"] for i in day["items"]}
    first = _extend(60)
    ids_after_first = {i["id"] for i in first["items"]}
    second = _extend(60)

    cycle1 = [i for i in first["items"] if i["id"] not in ids_after_day]
    cycle2 = [i for i in second["items"] if i["id"] not in ids_after_first]

    anchors = {
        i["topic_id"]
        for i in cycle1 + cycle2
        if i["activity_type"] in ("LEARN", "DSA") and i["topic_id"]
    }
    assert len(anchors) == 4, f"expected 4 distinct LEARN/DSA topics, got {anchors}"


def test_extend_reports_exhaustion_without_erroring(client):
    _seed_curriculum()
    day = _generate(150)
    _settle_everything(day)

    result = None
    for _ in range(12):
        result = _extend(60)
        if result["first_new_item_id"] is None:
            break
    assert result is not None
    assert result["first_new_item_id"] is None
    assert result["message"] == day_engine.CURRICULUM_EXHAUSTED


def test_cursors_exclude_topic_ids_defaults_to_old_behaviour(client):
    seed = _seed_curriculum()
    db = SessionLocal()
    try:
        core_a, dsa_a, _ = day_engine.cursors(db)
        core_b, dsa_b, _ = day_engine.cursors(db, exclude_topic_ids=None)
        assert (core_a.id, dsa_a.id) == (core_b.id, dsa_b.id)
        assert core_a.id == seed["core_ids"][0]
        assert dsa_a.id == seed["dsa_ids"][0]

        # Excluding the current pair moves both lanes on by one.
        core_c, dsa_c, _ = day_engine.cursors(
            db, exclude_topic_ids={core_a.id, dsa_a.id}
        )
        assert core_c.id == seed["core_ids"][1]
        assert dsa_c.id == seed["dsa_ids"][1]
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 7. get_day is read-only
# ---------------------------------------------------------------------------


def test_get_day_writes_nothing_and_flags_needs_generation(client):
    _seed_curriculum()
    db = SessionLocal()
    try:
        assert db.query(DailyPlanItem).count() == 0
        for _ in range(3):
            day = day_engine.get_day(db)
            assert day["needs_generation"] is True
            assert day["items"] == []
        db.commit()
        assert db.query(DailyPlanItem).count() == 0
    finally:
        db.close()


def test_get_day_endpoint_writes_nothing(client):
    _seed_curriculum()
    for _ in range(3):
        body = client.get("/api/day").json()
        assert body["needs_generation"] is True
        assert body["items"] == []

    db = SessionLocal()
    try:
        assert db.query(DailyPlanItem).count() == 0
    finally:
        db.close()

    # Generate is what builds it, and then the flag flips.
    built = client.post("/api/day/generate", json={"minutes": 150}).json()
    assert built["needs_generation"] is False
    assert built["items"]
    assert client.get("/api/day").json()["needs_generation"] is False


# ---------------------------------------------------------------------------
# 8. The revision queue is fed by finishing a topic
# ---------------------------------------------------------------------------


def _revisions() -> list[RevisionSchedule]:
    db = SessionLocal()
    try:
        return db.query(RevisionSchedule).all()
    finally:
        db.close()


def _complete(item_id: int, *, complete_topic: bool, minutes: int = 20) -> None:
    db = SessionLocal()
    try:
        day_engine.complete_item(
            db, item_id, minutes=minutes, complete_topic=complete_topic
        )
        db.commit()
    finally:
        db.close()


def _block(day: dict, activity: str) -> dict:
    return next(i for i in day["items"] if i["activity_type"] == activity)


def _reopen(item_id: int) -> None:
    """Put a finished block back to pending so it can be completed again."""
    db = SessionLocal()
    try:
        row = db.get(DailyPlanItem, item_id)
        row.status = "pending"
        row.completed_at = None
        db.commit()
    finally:
        db.close()


def test_completing_learn_topic_enqueues_one_revision(client):
    _seed_curriculum()
    day = _generate(150)
    learn = _block(day, "LEARN")
    assert _revisions() == []

    _complete(learn["id"], complete_topic=True)

    rows = _revisions()
    assert len(rows) == 1
    assert rows[0].item_type == "topic"
    assert rows[0].item_id == learn["topic_id"]
    assert rows[0].review_interval == day_engine.FIRST_REVIEW_DAYS == 1
    assert rows[0].next_review is not None


def test_completing_dsa_topic_enqueues_a_revision(client):
    _seed_curriculum()
    day = _generate(150)
    dsa = _block(day, "DSA")

    _complete(dsa["id"], complete_topic=True)

    rows = _revisions()
    assert len(rows) == 1
    assert rows[0].item_id == dsa["topic_id"]


def test_completing_the_same_topic_twice_leaves_one_row(client):
    _seed_curriculum()
    day = _generate(150)
    learn = _block(day, "LEARN")

    _complete(learn["id"], complete_topic=True)
    _reopen(learn["id"])
    _complete(learn["id"], complete_topic=True)

    assert len(_revisions()) == 1


def test_re_completing_does_not_reset_a_matured_interval(client):
    """Spacing must survive. A 30-day interval is not knocked back to tomorrow."""
    _seed_curriculum()
    day = _generate(150)
    learn = _block(day, "LEARN")
    _complete(learn["id"], complete_topic=True)

    db = SessionLocal()
    try:
        row = db.query(RevisionSchedule).one()
        row.review_interval = 30
        matured = row.next_review
        db.commit()
    finally:
        db.close()

    _reopen(learn["id"])
    _complete(learn["id"], complete_topic=True)

    db = SessionLocal()
    try:
        row = db.query(RevisionSchedule).one()
        assert row.review_interval == 30
        assert row.next_review == matured
    finally:
        db.close()


def test_complete_topic_false_enqueues_nothing(client):
    _seed_curriculum()
    day = _generate(150)
    learn = _block(day, "LEARN")

    _complete(learn["id"], complete_topic=False)

    assert _revisions() == []


def test_practice_and_reflect_blocks_enqueue_nothing(client):
    _seed_curriculum()
    day = _generate(150)

    _complete(_block(day, "PRACTICE")["id"], complete_topic=True)
    _complete(_block(day, "REFLECT")["id"], complete_topic=True)

    assert _revisions() == []


def test_enqueue_failure_never_blocks_completion(client, monkeypatch):
    _seed_curriculum()
    day = _generate(150)
    learn = _block(day, "LEARN")

    def boom(*_a, **_k):
        raise RuntimeError("revision table on fire")

    monkeypatch.setattr(service, "_upsert_revision", boom)
    _complete(learn["id"], complete_topic=True)

    db = SessionLocal()
    try:
        row = db.get(DailyPlanItem, learn["id"])
        assert row.status == "done", "a broken revision row blocked the completion"
        assert row.actual_minutes == 20
    finally:
        db.close()
    assert _revisions() == []


def test_queued_topic_produces_a_review_block_the_next_day(client):
    from datetime import date, timedelta

    _seed_curriculum()
    day = _generate(150)
    learn = _block(day, "LEARN")
    _complete(learn["id"], complete_topic=True)

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    db = SessionLocal()
    try:
        kinds = [
            b.activity_type
            for b in day_engine.build_blocks(db, budget_minutes=150, plan_date=tomorrow)
        ]
    finally:
        db.close()
    assert "REVIEW" in kinds, kinds


def test_pending_revisions_endpoint_reports_the_queued_topic(client):
    _seed_curriculum()
    day = _generate(150)
    learn = _block(day, "LEARN")
    _complete(learn["id"], complete_topic=True)

    pending = client.get("/api/revision/pending").json()
    match = [r for r in pending if r["item_id"] == learn["topic_id"]]
    assert len(match) == 1
    assert match[0]["item_type"] == "topic"
    assert match[0]["review_interval"] == 1
    assert match[0]["title"]
