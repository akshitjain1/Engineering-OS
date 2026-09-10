"""A problem set must be priced at the work it contains.

The DSA practice card offered:

    NeetCode 150 - Arrays & Hashing (representative subset)      ~20 min

Arrays & Hashing is nine problems: three easy and six medium. At the rates this
curriculum already uses for LeetCode problems that is 195 minutes, and all 128
NeetCode rows carried the same flat 20 with no estimate_method recorded, so
nothing could tell the constant apart from a measurement.

The counts come from NeetCode's own published problem list, cached in the repo,
so these tests need no network.
"""

from __future__ import annotations

import pytest

from app.content import neetcode_sections as nc
from app.content.apply_dsa_exact_problems import MINUTES_BY_DIFFICULTY
from app.content.apply_neetcode_section_estimates import (
    ALIASES,
    WHOLE_LIST,
    section_of,
    whole_list,
)


@pytest.fixture(scope="module")
def found():
    if not nc.CACHE.exists():
        pytest.skip("no cached NeetCode data; run app.content.neetcode_sections --refresh")
    return nc.sections(nc.fetch())


# ---------------------------------------------------------------------------
# the reported case
# ---------------------------------------------------------------------------

def test_arrays_and_hashing_is_nine_problems_not_twenty_minutes(found):
    """The section in the screenshot, by name and by number."""
    section = found["Arrays & Hashing"]
    assert section["count"] == 9
    assert section["mix"] == {"easy": 3, "medium": 6, "hard": 0}
    assert section["minutes"] == 3 * 15 + 6 * 25 == 195


def test_no_section_could_be_finished_in_twenty_minutes(found):
    """The old estimate was not merely low for one section -- it was wrong for
    every one of them. The smallest is Tries, at ninety minutes."""
    assert min(s["minutes"] for s in found.values()) > 20
    assert min(s["count"] for s in found.values()) >= 3


# ---------------------------------------------------------------------------
# the numbers add up
# ---------------------------------------------------------------------------

def test_the_sections_account_for_all_one_hundred_and_fifty(found):
    assert sum(s["count"] for s in found.values()) == 150


def test_the_difficulty_totals_match_neetcodes_own_dashboard(found):
    """neetcode.io reports 28 easy, 101 medium, 21 hard.

    Checked because it is the one place this data can be compared against the
    site a learner actually opens -- if these drift, the numbers on the card
    stop matching the numbers on the page it links to.
    """
    totals = {"easy": 0, "medium": 0, "hard": 0}
    for section in found.values():
        for key, n in section["mix"].items():
            totals[key] += n
    assert totals == {"easy": 28, "medium": 101, "hard": 21}


def test_minutes_are_the_sum_of_the_problems(found):
    """No fudge factor, no rounding to a nice number."""
    for name, section in found.items():
        expected = sum(
            MINUTES_BY_DIFFICULTY[p["difficulty"].title()] for p in section["problems"]
        )
        assert section["minutes"] == expected, name


def test_the_rates_are_the_ones_used_for_single_problems():
    """A set costed on a different scale is a set you cannot compare with the
    problem listed beside it."""
    assert MINUTES_BY_DIFFICULTY == {"Easy": 15, "Medium": 25, "Hard": 40}


# ---------------------------------------------------------------------------
# ordering and description
# ---------------------------------------------------------------------------

def test_problems_are_listed_easiest_first(found):
    """"Solve the first two" has to mean two you can start on."""
    rank = {"easy": 0, "medium": 1, "hard": 2}
    for name, section in found.items():
        ranks = [rank[p["difficulty"].lower()] for p in section["problems"]]
        assert ranks == sorted(ranks), name


def test_the_description_names_the_problems(found):
    """The old description said "solve the small representative subset listed
    in the exercise" and the lesson had no exercise, so the subset was never
    named anywhere. Nine problems and no way to know which."""
    text = nc.describe("Arrays & Hashing", found["Arrays & Hashing"])
    assert "9 problems" in text
    assert "3 easy, 6 medium" in text
    assert "195 minutes" in text
    for problem in ("Contains Duplicate", "Two Sum", "Valid Sudoku"):
        assert problem in text
    assert "across sessions" in text


def test_the_description_does_not_point_at_a_missing_exercise(found):
    text = nc.describe("Trees", found["Trees"])
    assert "listed in the exercise" not in text


def test_every_problem_carries_a_leetcode_url(found):
    for section in found.values():
        for problem in section["problems"]:
            assert problem["url"].startswith("https://leetcode.com/problems/")
            assert not problem["url"].endswith("problems//")


# ---------------------------------------------------------------------------
# title matching
# ---------------------------------------------------------------------------

def test_a_section_title_resolves_to_its_section():
    assert section_of("NeetCode 150 — Arrays & Hashing (representative subset)") == (
        "Arrays & Hashing"
    )


def test_the_abbreviated_dynamic_programming_titles_resolve(found):
    """Twenty-two rows say "1-D DP" and "2-D DP"; NeetCode spells them out.

    Without the alias these kept their flat 20 while every section around them
    was corrected, which is the worst outcome available: a fix that looks
    complete and is not.
    """
    assert section_of("NeetCode 150 — 1-D DP (representative subset)") in found
    assert section_of("NeetCode 150 — 2-D DP (representative subset)") in found
    for alias, real in ALIASES.items():
        assert real in found, f"{alias} points at a section that does not exist"


def test_a_single_problem_title_does_not_resolve_to_a_section():
    """"NeetCode - Valid Anagram" is one problem with its own estimate, and
    resizing it to its section's 195 minutes would be a new lie."""
    assert section_of("NeetCode — Valid Anagram") is None
    assert section_of("NeetCode Core Skills — Design Hash Table") is None


def test_the_whole_list_row_is_the_whole_list(found):
    """Two rows are titled "NeetCode 150 - NeetCode 150"."""
    assert section_of("NeetCode 150 — NeetCode 150 (representative subset)") == WHOLE_LIST
    combined = whole_list(found)
    assert combined["count"] == 150
    assert combined["minutes"] == sum(s["minutes"] for s in found.values())
    assert combined["mix"] == {"easy": 28, "medium": 101, "hard": 21}
