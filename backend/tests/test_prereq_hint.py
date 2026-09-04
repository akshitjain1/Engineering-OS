"""A block must say what it assumes you already know.

"Array traversal" arrived as the day's DSA block while `java-arrays` -- the
topic that explains what an array *is* -- sat weeks away on the main track. The
curriculum knew: dsa-array-traversal lists java-arrays as a REQUIRED
prerequisite. The block said nothing, so the day read as though traversal were
the natural place to begin.

Gating is not the answer and must not become one. Every one of the 103
remaining DSA topics depends on a Java topic the DSA lane deliberately does not
wait for, so refusing to serve a blocked topic would stop the daily reps
entirely -- the one thing that lane exists to protect.
"""

from __future__ import annotations

from app.learning.day_engine import _prereq_hint


class FakeTopic:
    def __init__(self, prerequisites):
        self.prerequisites = prerequisites


NAMES = {
    "java-arrays": "Arrays",
    "java-references": "References",
    "java-list": "List",
    "dsa-best-worst-average": "Best, worst, average",
}


def test_nothing_is_said_when_the_ground_is_covered():
    topic = FakeTopic([{"slug": "java-arrays", "type": "REQUIRED"}])
    assert _prereq_hint(topic, {"java-arrays": True}, NAMES) == ""


def test_a_topic_with_no_prerequisites_says_nothing():
    assert _prereq_hint(FakeTopic([]), {}, NAMES) == ""
    assert _prereq_hint(FakeTopic(None), {}, NAMES) == ""


def test_the_missing_prerequisite_is_named_not_slugged():
    """"java-arrays" tells the reader nothing that "Arrays" does not tell them
    better."""
    hint = _prereq_hint(FakeTopic([{"slug": "java-arrays"}]), {}, NAMES)

    assert "Arrays" in hint
    assert "java-arrays" not in hint


def test_the_slug_is_used_when_no_name_is_known():
    """Better a slug than a blank where a topic name should be."""
    hint = _prereq_hint(FakeTopic([{"slug": "some-unmapped-topic"}]), {}, NAMES)
    assert "some-unmapped-topic" in hint


def test_two_missing_prerequisites_read_as_a_sentence():
    hint = _prereq_hint(
        FakeTopic([{"slug": "java-arrays"}, {"slug": "java-references"}]), {}, NAMES
    )
    assert "Arrays and References" in hint


def test_a_long_list_is_summarised_rather_than_dumped():
    """Four slugs in a row is not a sentence anyone reads."""
    topic = FakeTopic(
        [{"slug": s} for s in ("java-arrays", "java-references", "java-list", "x-other")]
    )
    hint = _prereq_hint(topic, {}, NAMES)

    assert "Arrays, References and 2 more" in hint
    assert "x-other" not in hint


def test_the_hint_advises_rather_than_forbids():
    """It must never read as a refusal: the block is still served."""
    hint = _prereq_hint(FakeTopic([{"slug": "java-arrays"}]), {}, NAMES)

    assert "skim first" in hint
    for word in ("blocked", "locked", "cannot", "must complete"):
        assert word not in hint.lower()


def test_plain_string_prerequisites_still_work():
    """Older manifest rows list a slug directly rather than an object."""
    assert "Arrays" in _prereq_hint(FakeTopic(["java-arrays"]), {}, NAMES)


def test_names_are_optional():
    """Callers that have no index still get a usable hint."""
    assert "java-arrays" in _prereq_hint(FakeTopic([{"slug": "java-arrays"}]), {})
