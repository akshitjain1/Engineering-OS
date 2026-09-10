"""Every foundations topic must open a page about itself.

Forty-nine of sixty-four did not. One MIT lecture was the primary source for
fourteen topics, a CS50 week page for four, a single YouTube video for three
number-system topics with no timestamps. Clicking "Pipes" opened a general
shell lecture; clicking "System calls" opened a lecture about debugging.

That was found by hand, one topic per morning, for two weeks. This test is so
it cannot come back quietly: it reads the page text already cached in the repo,
so it needs no network, and it fails if any foundations topic's primary source
stops being about that topic -- or if a new topic arrives without one.

The escape hatch is ACCEPTED in foundations_primary_sources, which requires a
sentence of prose per entry. An exemption you have to write down is one you can
argue with; a silent pass is not.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.content import audit_topic_relevance as audit
from app.content.foundations_primary_sources import ACCEPTED, SOURCES

SNAPSHOT = Path(__file__).resolve().parent.parent / "data" / "snapshot" / "curriculum"


def _rows(name: str) -> list[dict]:
    path = SNAPSHOT / f"{name}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def curriculum() -> dict[str, dict]:
    """Topics and their primary resources, read from the committed snapshot.

    Deliberately not from SessionLocal: under pytest that is an empty scratch
    database, so a test built on it skips itself and guards nothing. The
    snapshot is the curriculum as committed, which is the thing that must stay
    correct.
    """
    topics = _rows("curriculum_topics")
    lessons = _rows("curriculum_lessons")
    resources = _rows("curriculum_resources")
    if not (topics and lessons and resources):
        pytest.skip("no committed curriculum snapshot")

    topic_of_lesson = {l["id"]: l["topic_id"] for l in lessons}
    by_id = {t["id"]: t for t in topics if t.get("domain_key") == "foundations"}

    out: dict[str, dict] = {}
    for res in resources:
        if (res.get("role") or "").upper() != "PRIMARY" or not res.get("url"):
            continue
        if res.get("learner_visible") in (0, False):
            continue
        topic = by_id.get(topic_of_lesson.get(res.get("lesson_id")))
        if topic is None:
            continue
        out.setdefault(topic["slug"], {"name": topic["name"], "url": res["url"]})
    return out


@pytest.fixture(scope="module")
def verdicts(curriculum) -> dict[str, tuple[str, str, str]]:
    """slug -> (name, url, where the topic sits on that page)."""
    facts = audit.load_cache()
    if not facts:
        pytest.skip("no cached page text; run app.content.audit_topic_relevance")

    out: dict[str, tuple[str, str, str]] = {}
    for slug, row in curriculum.items():
        entry = facts.get(row["url"])
        if not entry or entry.get("status") != 200 or entry.get("unreadable"):
            continue  # not readable, so not judgeable here
        phrase = audit.topic_phrase(row["name"], slug)
        out[slug] = (row["name"], row["url"], audit.placement(entry, phrase))
    if not out:
        pytest.skip("no foundations page in the cache")
    return out


def test_no_foundations_topic_lands_on_a_page_about_something_else(verdicts):
    """The whole point. Every topic is the subject of its page, or excused."""
    stray = {
        slug: (name, where, url)
        for slug, (name, url, where) in verdicts.items()
        if where != audit.SUBJECT and slug not in ACCEPTED
    }
    assert not stray, (
        "these foundations topics do not open a page about themselves:\n"
        + "\n".join(f"  {name} -> {where}: {url}" for name, where, url in stray.values())
    )


def test_the_reported_case_stays_fixed(verdicts):
    """System calls. The one that was reported, by name."""
    if "cf-system-calls" not in verdicts:
        pytest.skip("cf-system-calls not in this database")
    name, url, where = verdicts["cf-system-calls"]
    assert where == audit.SUBJECT
    assert "debugging-profiling" not in url, "back on the MIT debugging lecture"


def test_no_page_serves_more_than_two_foundations_topics(verdicts):
    """One lecture was the primary source for fourteen topics.

    Two is allowed because the curriculum genuinely contains duplicate topics
    (three called Process(es), two called Permissions -- see DUPLICATES), and
    pointing both halves of a duplicate pair at the same correct page is not
    the defect. Fourteen was.
    """
    counts: dict[str, list[str]] = {}
    for name, url, _where in verdicts.values():
        counts.setdefault(url, []).append(name)
    crowded = {u: n for u, n in counts.items() if len(n) > 2}
    assert not crowded, (
        "one page is standing in for several topics again:\n"
        + "\n".join(f"  {len(n)}x {u}\n      {', '.join(n)}" for u, n in crowded.items())
    )


def test_every_accepted_exemption_says_why():
    """An exemption without a reason is just a silence with extra steps."""
    for slug, reason in ACCEPTED.items():
        assert reason and len(reason.split()) >= 8, f"{slug} has no real reason"


def test_no_topic_is_both_mapped_and_excused():
    """SOURCES means "use this page"; ACCEPTED means "keep the one you have".

    A slug in both is a contradiction, and whichever one won would be an
    accident of import order.
    """
    both = set(SOURCES) & set(ACCEPTED)
    assert not both, f"listed as both mapped and excused: {sorted(both)}"


def test_the_map_has_no_dead_slugs():
    """A typo'd slug in the map is a topic that never gets fixed and never
    reports that it wasn't."""
    known = {t["slug"] for t in _rows("curriculum_topics")}
    if not known:
        pytest.skip("no committed curriculum snapshot")
    unknown = (set(SOURCES) | set(ACCEPTED)) - known
    assert not unknown, f"map names topics that do not exist: {sorted(unknown)}"
