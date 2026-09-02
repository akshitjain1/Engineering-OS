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
    _resource_slug,
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


#: Topics that sit before any technique has been taught. Their PRIMARY source is
#: a definition page, so a problem needing a named algorithm does not follow
#: from it however well its tags line up. This is the rule the tag check cannot
#: express: "correctly classified" is not the same as "reachable from today's
#: reading". Kept deliberately small -- best/worst/average genuinely needs
#: quickselect to make its point, so it is not in here.
FOUNDATION_TOPICS = ("dsa-algorithmic-thinking", "dsa-big-o")


def test_foundation_topics_stay_solvable_from_their_reading(facts):
    for topic_slug in FOUNDATION_TOPICS:
        for problem_slug, _tags, _why in DSA_EXACT_PROBLEMS[topic_slug]["problems"]:
            fact = facts[problem_slug]
            assert fact["difficulty"] == "Easy", (
                f"{topic_slug} maps {fact['title']} ({fact['difficulty']}). "
                "Nothing above Easy follows from a definition page."
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


# --- the writer has to converge, not just accumulate -------------------


def _managed_rows(topic_slug: str, *, visible_only: bool = True):
    db = SessionLocal()
    try:
        rows = (
            db.query(CurriculumResource)
            .join(CurriculumLesson, CurriculumLesson.id == CurriculumResource.lesson_id)
            .join(CurriculumTopic, CurriculumTopic.id == CurriculumLesson.topic_id)
            .filter(CurriculumTopic.slug == topic_slug)
            .all()
        )
        prefix = f"{topic_slug}--lc-"
        return [
            r for r in rows
            if (r.slug or "").startswith(prefix) and (r.learner_visible or not visible_only)
        ]
    finally:
        db.close()


def test_dropping_a_problem_from_the_map_retires_its_row(client, monkeypatch):
    """A correction to the map has to actually reach the database.

    The writer used to be additive, so removing a problem left its row in place
    -- still PRACTICE, still EXACT, still offered -- and the correction was
    invisible in the app.
    """
    topic_slug = "dsa-array-traversal"
    _seed([topic_slug])
    db = SessionLocal()
    try:
        apply(db)
        db.commit()
    finally:
        db.close()

    full = DSA_EXACT_PROBLEMS[topic_slug]
    assert len(full["problems"]) >= 2
    dropped_slug = full["problems"][-1][0]
    trimmed = dict(DSA_EXACT_PROBLEMS)
    trimmed[topic_slug] = {**full, "problems": full["problems"][:-1]}

    import app.content.apply_dsa_exact_problems as mod
    monkeypatch.setattr(mod, "DSA_EXACT_PROBLEMS", trimmed)

    db = SessionLocal()
    try:
        stats = mod.apply(db)
        db.commit()
    finally:
        db.close()

    assert stats["retired_deleted"] == 1
    remaining = {r.slug for r in _managed_rows(topic_slug)}
    assert _resource_slug(topic_slug, dropped_slug) not in remaining
    assert len(remaining) == len(trimmed[topic_slug]["problems"])


def test_a_solved_problem_is_hidden_rather_than_deleted(client, monkeypatch):
    """Retiring must never erase evidence of work already done."""
    topic_slug = "dsa-array-traversal"
    _seed([topic_slug])
    db = SessionLocal()
    try:
        apply(db)
        db.commit()
    finally:
        db.close()

    full = DSA_EXACT_PROBLEMS[topic_slug]
    dropped_slug = full["problems"][-1][0]
    row_slug = _resource_slug(topic_slug, dropped_slug)

    db = SessionLocal()
    try:
        row = db.query(CurriculumResource).filter(CurriculumResource.slug == row_slug).one()
        row.completion_status = "completed"
        db.commit()
    finally:
        db.close()

    trimmed = dict(DSA_EXACT_PROBLEMS)
    trimmed[topic_slug] = {**full, "problems": full["problems"][:-1]}
    import app.content.apply_dsa_exact_problems as mod
    monkeypatch.setattr(mod, "DSA_EXACT_PROBLEMS", trimmed)

    db = SessionLocal()
    try:
        stats = mod.apply(db)
        db.commit()
    finally:
        db.close()

    assert stats["retired_hidden"] == 1
    assert stats["retired_deleted"] == 0
    db = SessionLocal()
    try:
        row = db.query(CurriculumResource).filter(CurriculumResource.slug == row_slug).one()
        assert row.completion_status == "completed", "solved work was destroyed"
        assert not row.learner_visible, "a dropped problem is still being offered"
    finally:
        db.close()
    assert row_slug not in {r.slug for r in _managed_rows(topic_slug)}


def test_order_index_has_no_duplicates_within_a_topic(client):
    _seed(SAMPLE_TOPICS)
    db = SessionLocal()
    try:
        apply(db)
        db.commit()
    finally:
        db.close()
    for topic_slug in SAMPLE_TOPICS:
        indices = [r.order_index for r in _managed_rows(topic_slug)]
        assert len(indices) == len(set(indices)), f"{topic_slug} has colliding order_index {indices}"


# --- reachability: reviewed, then ratcheted ----------------------------

#: Entries that sit 10+ modules before a technique LeetCode tags them with, and
#: which have been read individually and accepted. In every case the advanced
#: tag names an *alternative* solution, not a requirement:
#:
#:   Missing Number            the sum formula needs nothing at all
#:   Single Number             a count map solves it; XOR is the upgrade
#:   Best Time to Buy/Sell     one pass with a running minimum, no DP
#:   Longest Common Prefix     scan columns; the trie tag is a different route
#:   Find the Difference       counting; bit tricks are optional
#:   Longest Palindromic Sub.  expand around each centre, no table
#:   Is Subsequence            two pointers; the DP tag is the harder variant
#:   Find the Duplicate Number Floyd on an array -- that IS the topic
#:   Container With Most Water the two-pointer move; "greedy" names its proof
#:   Longest Consecutive Seq.  a hash set is the intended solution
#:   01 Matrix                 multi-source BFS -- that IS the topic
#:   Letter Case Permutation   backtracking; bitmask is the alternative
#:   Fibonacci Number          plain recursion; memoisation comes later
#:   Subsets / Subsets II      backtracking; the bitmask route is optional
#:   Binary Search             a 3-line loop, standard in a complexity lesson
#:   Palindrome Partitioning   backtracking with a palindrome check
#:   Sort Characters By Freq.  counting then ordering; sorted() is a call
#:   Top K Frequent Elements   counting then ordering; sorted() is a call
#:   Count of Smaller Numbers  counting during the merge -- that IS the topic
#:   Contains Duplicate        brute force, sort, or set: the point is comparing
#:   Majority Element          counting
#:   Merge Sorted Array        the merge step by hand
#:   Split Array Largest Sum   binary search on the answer -- that IS the topic
#:   Min Number of Moves       sort both sides and pair; sorted() is a call
#:   Largest Number            a comparator -- that IS the topic
#:   Count Complete Tree Nodes definition of completeness -- that IS the topic
REVIEWED_EARLY = {
    ("dsa-array-frequency", "Majority Element"),
    ("dsa-array-frequency", "Single Number"),
    ("dsa-array-patterns", "Best Time to Buy and Sell Stock"),
    ("dsa-array-patterns", "Merge Sorted Array"),
    ("dsa-best-worst-average", "Binary Search"),
    ("dsa-best-worst-average", "Contains Duplicate"),
    ("dsa-big-o", "Contains Duplicate"),
    ("dsa-big-o", "Missing Number"),
    ("dsa-constraint-search", "Palindrome Partitioning"),
    ("dsa-fast-slow", "Find the Duplicate Number"),
    ("dsa-frequency-maps", "Find the Difference"),
    ("dsa-frequency-maps", "Sort Characters By Frequency"),
    ("dsa-frequency-maps", "Top K Frequent Elements"),
    ("dsa-hash-set", "Longest Consecutive Sequence"),
    ("dsa-merge-sort", "Count of Smaller Numbers After Self"),
    ("dsa-permutations", "Letter Case Permutation"),
    ("dsa-queue-bfs-relationship", "01 Matrix"),
    ("dsa-recursion-model", "Fibonacci Number"),
    ("dsa-search-on-answer", "Split Array Largest Sum"),
    ("dsa-selection-sort", "Minimum Number of Moves to Seat Everyone"),
    ("dsa-sort-complexity", "Largest Number"),
    ("dsa-string-patterns", "Longest Common Prefix"),
    ("dsa-string-patterns", "Longest Palindromic Substring"),
    ("dsa-subsets", "Subsets"),
    ("dsa-subsets", "Subsets II"),
    ("dsa-two-pointers-opposite", "Container With Most Water"),
    ("dsa-two-pointers-same", "Is Subsequence"),
    ("dsa-tree-terminology", "Count Complete Tree Nodes"),
}

#: Below this, the tag is nearly always an alternative route rather than a
#: prerequisite, and pinning every one of them would be noise.
EARLY_GAP_THRESHOLD = 10


def test_no_unreviewed_problem_sits_far_before_its_technique(client):
    """A ratchet, not a proof.

    Tag checking shows a problem *uses* the technique it is filed under. It
    cannot show the learner can reach it -- that is judgement. So the judgement
    is written down once in REVIEWED_EARLY, and this fails the moment a new
    entry lands far ahead of the module that teaches what it needs.
    """
    from app.content.audit_dsa_reachability import find_flags

    current = {
        (f["topic"], f["problem"]) for f in find_flags() if f["gap"] >= EARLY_GAP_THRESHOLD
    }
    unreviewed = current - REVIEWED_EARLY
    assert not unreviewed, (
        "these sit far before the technique they need and have not been reviewed:\n  "
        + "\n  ".join(f"{t} -> {p}" for t, p in sorted(unreviewed))
        + "\nEither remap them, or add them to REVIEWED_EARLY with the reason."
    )

    stale = REVIEWED_EARLY - current
    assert not stale, (
        "REVIEWED_EARLY names entries that no longer flag; drop them:\n  "
        + "\n  ".join(f"{t} -> {p}" for t, p in sorted(stale))
    )


def test_every_problem_has_solutions_to_fall_back_on(facts):
    """The Stuck? button must never lead somewhere empty."""
    for slug, fact in facts.items():
        assert fact.get("solution_count", 0) > 0, f"{slug} has no community solutions"
        assert fact["solutions_url"] == f"https://leetcode.com/problems/{slug}/solutions/"
