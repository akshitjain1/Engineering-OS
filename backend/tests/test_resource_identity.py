"""A resource's title and provider must describe the page it opens.

Found on a DSA block: a card headed "NeetCode - Best Time to Buy and Sell
Stock" whose "Open official resource" button opened a GeeksforGeeks article on
asymptotic analysis. The URL was right for the topic; the title and provider
were left over from something else, so the card described a page that does not
exist. A wrong link announces itself when you click it. A wrong title does not.

The host decides, because the URL is the one field that cannot be wrong about
itself. The title is only rebuilt when it opens by naming a publisher -- that
is the part that turns out to be false.
"""

from __future__ import annotations

import pytest

from app.content import verify_resource_identity as vri
from app.db import models
from app.db.session import Base, SessionLocal, engine

GFG_ASYMPTOTIC = "https://www.geeksforgeeks.org/analysis-of-algorithms-set-2-asymptotic-analysis/"
FACTS = {
    GFG_ASYMPTOTIC: {
        "page_title": "Worst, Average and Best Case Analysis of Algorithms - GeeksforGeeks"
    }
}


def test_clean_page_title_strips_a_trailing_site_name():
    assert vri.clean_page_title("Heap Sort - GeeksforGeeks") == "Heap Sort"


def test_clean_page_title_strips_a_leading_site_name():
    """Seeing Theory puts its name first, which would otherwise be doubled."""
    assert vri.clean_page_title("Seeing Theory - Basic Probability") == "Basic Probability"


def test_clean_page_title_strips_html_comments():
    assert vri.clean_page_title("LLM Settings | Prompt Engineering Guide<!-- -->") == "LLM Settings"


def test_clean_page_title_actually_changes_something():
    """Guards the bug that made this function a no-op.

    An earlier version wrote the en and em dashes as escapes inside a raw
    string, so the pattern searched for the literal text and stripped nothing,
    while reading correctly to anyone reviewing it.
    """
    raw = "Two Pointers Technique - GeeksforGeeks"
    assert vri.clean_page_title(raw) != raw


@pytest.mark.parametrize(
    "title, expected",
    [
        ("NeetCode " + vri.EM_DASH + " Valid Anagram", "NeetCode"),
        ("MDN: TCP vs UDP", "MDN"),
        ("IBM: Requirements & scope", "IBM"),
        ("Khan Academy: Summary statistics", "Khan Academy"),
        ("Bayes theorem", None),
        ("Text preprocessing (tokenizers intro)", None),
    ],
)
def test_opens_with_attribution(title, expected):
    assert vri.opens_with_attribution(title) == expected


@pytest.fixture
def one_resource():
    """One learner-visible resource whose fields the test sets."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    def make(*, title, provider, url):
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
        topic = models.CurriculumTopic(
            slug="dsa-bwa", name="Best, worst, average", module_id=module.id, order_index=1
        )
        db.add(topic)
        db.flush()
        lesson = models.CurriculumLesson(
            slug="dsa-bwa-l1", title="Best, worst, average", topic_id=topic.id, order_index=1
        )
        db.add(lesson)
        db.flush()
        resource = models.CurriculumResource(
            slug="r1", title=title, provider=provider, url=url,
            resource_type="documentation", lesson_id=lesson.id, role="PRIMARY",
            order_index=0, learner_visible=True,
        )
        db.add(resource)
        db.commit()
        return resource

    try:
        yield db, make
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_the_reported_row_is_corrected(one_resource):
    """The exact card that was wrong on screen."""
    db, make = one_resource
    make(
        title="NeetCode " + vri.EM_DASH + " Best Time to Buy and Sell Stock",
        provider="NeetCode",
        url=GFG_ASYMPTOTIC,
    )

    change = vri.corrections(db, FACTS)[0]
    assert change["provider_to"] == "GeeksforGeeks"
    assert change["title_to"] == (
        "GFG " + vri.EM_DASH + " Worst, Average and Best Case Analysis of Algorithms"
    )
    assert "Best Time to Buy" not in change["title_to"]


def test_a_matching_provider_is_left_alone(one_resource):
    db, make = one_resource
    make(title="GFG " + vri.EM_DASH + " Heap Sort", provider="GeeksforGeeks",
         url="https://www.geeksforgeeks.org/heap-sort/")
    assert vri.corrections(db, {}) == []


def test_a_descriptive_title_keeps_its_wording(one_resource):
    """Only titles that claim a publisher are rebuilt.

    "Bayes theorem" is not lying about anything, and some of these pages return
    a <title> of "406" -- replacing good wording with that would be worse.
    """
    db, make = one_resource
    make(title="Bayes theorem", provider="Khan Academy",
         url="https://onlinestatbook.com/2/probability/bayes.html")

    change = vri.corrections(db, {})[0]
    assert change["provider_to"] == "Online StatBook"
    assert change["title_to"] is None


def test_youtube_rows_are_never_rewritten(one_resource):
    """A video's provider is its channel, which the host cannot tell us."""
    db, make = one_resource
    make(title="The Fetch Decode Execute Cycle", provider="Computer Science Lessons",
         url="https://www.youtube.com/watch?v=ByllwN8q2ss")
    assert vri.corrections(db, {}) == []


def test_an_unknown_host_is_not_renamed(one_resource):
    """Guessing a publisher's name is the fault this module exists to remove."""
    db, make = one_resource
    make(title="Some article", provider="Someone", url="https://example.com/thing")
    assert vri.corrections(db, {}) == []
