"""The DSA block must name a problem, not hand over a problem set.

Coverage contract:
1.  every DSA topic in the map is mapped to at least one problem, and the map
    matches the curriculum's topic slugs exactly
2.  every entry is backed by verified LeetCode facts -- real slug, not Premium,
    and tagged by LeetCode with a technique the mapping claims
3.  applying the map makes pick_resource return a named problem for a DSA
    block, and never a collection page
4.  the collection pages survive as REFERENCE/COLLECTION rather than being
    deleted, so they can still be browsed but can never be picked again
5.  applying twice changes nothing
6.  a DSA block already sitting in today's plan is re-pointed at the new
    problem, while finished blocks keep the record of what they opened

These run offline. The LeetCode facts are read from the cache written by
`python -m app.content.verify_dsa_problems`, so the suite never depends on the
network -- but it does depend on the cache being complete, which is what makes
an unverified hand edit fail here.
"""

import json

import pytest

from app.content.apply_dsa_exact_problems import (
    COLLECTION_URLS,
    apply,
    refresh_open_plan_items,
)
from app.content.dsa_exact_problems import DSA_EXACT_PROBLEMS
from app.content.verify_dsa_problems import CACHE, audit
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
from app.learning.day_engine import ACTIVITY_DSA, pick_resource, resources_for_topics

# A few slugs from different corners of the map, used for the DB-level tests.
SAMPLE_TOPICS = [
    "dsa-array-traversal",
    "dsa-monotonic-stack",
    "dsa-search-on-answer",
    "dsa-knapsack",
    "dsa-union-find",
]


@pytest.fixture
def facts():
    if not CACHE.exists():
        pytest.fail(
            f"{CACHE} is missing. Run: python -m app.content.verify_dsa_problems"
        )
    return json.loads(CACHE.read_text(encoding="utf-8"))


# --- the map itself ----------------------------------------------------


def test_every_topic_maps_to_at_least_one_problem():
    for topic_slug, spec in DSA_EXACT_PROBLEMS.items():
        assert spec["problems"], f"{topic_slug} has no problems"
        assert spec["technique"].strip(), f"{topic_slug} has no technique line"


def test_every_entry_is_verified_and_correctly_tagged(facts):
    """The guard that stops the map drifting back into wishful mapping."""
    assert audit(facts) == []


def test_no_entry_is_premium(facts):
    paid = [slug for slug, f in facts.items() if f["paid_only"]]
    assert paid == [], f"learner cannot open Premium problems: {paid}"


def test_every_url_is_a_single_problem(facts):
    for slug, fact in facts.items():
        assert fact["url"] == f"https://leetcode.com/problems/{slug}/"
        assert "/problemset" not in fact["url"]
        assert "/tag/" not in fact["url"]


def test_difficulty_never_decreases_within_a_topic(facts):
    """order_index comes from this ordering, so the first entry is what the DSA
    block opens. A topic that leads with its stretch problem is a worse landing
    than the collection page it replaced."""
    rank = {"Easy": 0, "Medium": 1, "Hard": 2}
    for topic_slug, spec in DSA_EXACT_PROBLEMS.items():
        pairs = [(p[0], rank[facts[p[0]]["difficulty"]]) for p in spec["problems"]]
        difficulties = [d for _, d in pairs]
        assert difficulties == sorted(difficulties), (
            f"{topic_slug} is not a progression: {[(s, d) for s, d in pairs]}"
        )


def test_no_topic_opens_on_a_hard_problem(facts):
    for topic_slug, spec in DSA_EXACT_PROBLEMS.items():
        first = facts[spec["problems"][0][0]]
        assert first["difficulty"] != "Hard", (
            f"{topic_slug} opens cold on {first['title']}, a Hard problem"
        )


# --- what the day engine actually picks --------------------------------


def _seed(topic_slugs):
    """A DSA topic per slug, each carrying the old collection page."""
    db = SessionLocal()
    try:
        track = CurriculumTrack(name="T", order_index=0)
        level = CurriculumLevel(name="L", order_index=0)
        db.add_all([track, level])
        db.flush()
        subject = CurriculumSubject(
            name="DSA", track_id=track.id, level_id=level.id, order_index=0
        )
        db.add(subject)
        db.flush()
        module = CurriculumModule(name="M", subject_id=subject.id, order_index=0)
        db.add(module)
        db.flush()

        ids = []
        for i, slug in enumerate(topic_slugs):
            topic = CurriculumTopic(
                name=slug, slug=slug, module_id=module.id, order_index=i,
                prerequisites=[], domain_key="dsa", estimated_minutes=45,
            )
            db.add(topic)
            db.flush()
            lesson = CurriculumLesson(title=slug, topic_id=topic.id, order_index=0)
            db.add(lesson)
            db.flush()
            db.add(
                CurriculumResource(
                    slug=f"{slug}-legacy-collection",
                    title="NeetCode 150",
                    url=COLLECTION_URLS[0],
                    resource_type="coding_problem",
                    role="PRACTICE",
                    exactness="EXACT",
                    verification_status="VERIFIED",
                    lesson_id=lesson.id,
                    order_index=0,
                )
            )
            ids.append(topic.id)
        db.commit()
        return ids
    finally:
        db.close()


def test_dsa_block_opens_a_named_problem_not_a_collection(client):
    ids = _seed(SAMPLE_TOPICS)
    db = SessionLocal()
    try:
        apply(db)
        grouped = resources_for_topics(db, ids)
        for topic_id, slug in zip(ids, SAMPLE_TOPICS):
            picked = pick_resource(grouped.get(topic_id, []), ACTIVITY_DSA)
            assert picked is not None, f"{slug} has nothing to open"
            assert picked.url.startswith("https://leetcode.com/problems/"), (
                f"{slug} still opens {picked.url}"
            )
            assert picked.url not in COLLECTION_URLS
            # the block has to say which problem, and why it is this one
            assert picked.title and picked.title[0].isdigit()
            assert picked.description
            assert picked.difficulty in {"Easy", "Medium", "Hard"}
    finally:
        db.close()


def test_the_collection_survives_but_is_never_picked(client):
    ids = _seed(["dsa-array-traversal"])
    db = SessionLocal()
    try:
        apply(db)
        rows = db.query(CurriculumResource).filter(
            CurriculumResource.url.in_(COLLECTION_URLS)
        ).all()
        assert rows, "the collection was deleted rather than demoted"
        for row in rows:
            assert row.role == "REFERENCE"
            assert row.exactness == "COLLECTION"
        # and it is not what a DSA block gets
        picked = pick_resource(resources_for_topics(db, ids).get(ids[0], []), ACTIVITY_DSA)
        assert picked.url not in COLLECTION_URLS
    finally:
        db.close()


def test_applying_twice_changes_nothing(client):
    _seed(SAMPLE_TOPICS)
    db = SessionLocal()
    try:
        first = apply(db)
        second = apply(db)
        assert first["created"] > 0
        assert second["created"] == 0
        assert second["demoted"] == 0
        assert second["updated"] == first["created"]
    finally:
        db.close()


def test_a_topic_with_no_lesson_is_skipped_not_crashed(client):
    """Content is incomplete in places; the loader must tolerate that."""
    db = SessionLocal()
    try:
        track = CurriculumTrack(name="T", order_index=0)
        level = CurriculumLevel(name="L", order_index=0)
        db.add_all([track, level])
        db.flush()
        subject = CurriculumSubject(
            name="DSA", track_id=track.id, level_id=level.id, order_index=0
        )
        db.add(subject)
        db.flush()
        module = CurriculumModule(name="M", subject_id=subject.id, order_index=0)
        db.add(module)
        db.flush()
        db.add(
            CurriculumTopic(
                name="x", slug="dsa-array-traversal", module_id=module.id,
                order_index=0, prerequisites=[], domain_key="dsa", estimated_minutes=45,
            )
        )
        db.commit()
        stats = apply(db)
        assert stats["skipped_no_lesson"] == 1
        assert stats["created"] == 0
    finally:
        db.close()


# --- today's plan, which denormalises the choice -----------------------


def _plan_item(db, topic_id, status, url):
    from app.learning.day_models import DailyPlanItem

    item = DailyPlanItem(
        user_id="akshit", plan_date="2026-09-01", position=0, activity_type="DSA",
        title="DSA", topic_id=topic_id, planned_minutes=30, status=status,
        resource_title="NeetCode 150", resource_url=url, resource_provider="NeetCode",
    )
    db.add(item)
    db.commit()
    return item.id


def test_an_open_block_is_repointed_at_the_new_problem(client):
    """Otherwise the fix does not reach the learner until tomorrow's plan."""
    from app.learning.day_models import DailyPlanItem

    ids = _seed(["dsa-array-traversal"])
    db = SessionLocal()
    try:
        item_id = _plan_item(db, ids[0], "active", COLLECTION_URLS[0])
        apply(db)
        assert refresh_open_plan_items(db) == 1
        item = db.get(DailyPlanItem, item_id)
        assert item.resource_url.startswith("https://leetcode.com/problems/")
        assert item.resource_provider == "LeetCode"
        assert item.resource_title[0].isdigit()
    finally:
        db.close()


def test_a_finished_block_keeps_what_it_opened(client):
    """A completed block is a record of what happened, not a stale pointer."""
    from app.learning.day_models import DailyPlanItem

    ids = _seed(["dsa-array-traversal"])
    db = SessionLocal()
    try:
        item_id = _plan_item(db, ids[0], "done", COLLECTION_URLS[0])
        apply(db)
        assert refresh_open_plan_items(db) == 0
        assert db.get(DailyPlanItem, item_id).resource_url == COLLECTION_URLS[0]
    finally:
        db.close()


def test_repointing_is_idempotent(client):
    ids = _seed(["dsa-array-traversal"])
    db = SessionLocal()
    try:
        _plan_item(db, ids[0], "pending", COLLECTION_URLS[0])
        apply(db)
        assert refresh_open_plan_items(db) == 1
        assert refresh_open_plan_items(db) == 0
    finally:
        db.close()
