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


def test_the_description_states_the_size_of_the_set(found):
    """The old description said "solve the small representative subset listed
    in the exercise" and the lesson had no exercise, so the subset was never
    named anywhere: nine problems and no way to know which.

    It no longer recites the names either -- the card lists each problem as its
    own link now, and printing them twice made the card unreadable. What the
    description still has to carry is the size, the spread and the fact that
    this is not one sitting.
    """
    text = nc.describe("Arrays & Hashing", found["Arrays & Hashing"])
    assert "9 problems" in text
    assert "3 easy, 6 medium" in text
    assert "195 minutes" in text
    assert "across sessions" in text


def test_the_problems_are_reachable_even_though_the_prose_stopped_listing_them(found):
    """The pair to the test above: dropping the names from the prose is only
    acceptable because every problem is in `problems` with its own URL."""
    section = found["Arrays & Hashing"]
    names = {p["problem"] for p in section["problems"]}
    assert {"Contains Duplicate", "Two Sum", "Valid Sudoku"} <= names
    assert len(section["problems"]) == section["count"] == 9


def test_the_description_does_not_point_at_a_missing_exercise(found):
    text = nc.describe("Trees", found["Trees"])
    assert "listed in the exercise" not in text


# ---------------------------------------------------------------------------
# per-problem links
# ---------------------------------------------------------------------------

def test_every_problem_links_to_its_own_neetcode_page(found):
    """The card used to offer one button to the whole 150-problem index.

    NeetCode does publish per-problem URLs, and they keep the list context:
    https://neetcode.io/problems/duplicate-integer/question?list=neetcode150
    """
    for section in found.values():
        for problem in section["problems"]:
            assert problem["url"].startswith("https://neetcode.io/problems/")
            assert problem["url"].endswith("/question?list=neetcode150")
            slug = problem["url"].removeprefix("https://neetcode.io/problems/").split("/")[0]
            assert slug, f"empty slug for {problem['problem']}"


def test_the_slug_is_neetcodes_own_not_leetcodes(found):
    """"Contains Duplicate" is /problems/duplicate-integer/ on NeetCode.

    Building these URLs from the LeetCode slug -- which is the only one in
    NeetCode's published JSON -- would have produced 150 dead links that all
    looked plausible.
    """
    by_name = {
        p["problem"]: p for section in found.values() for p in section["problems"]
    }
    assert "duplicate-integer" in by_name["Contains Duplicate"]["url"]
    assert "contains-duplicate" not in by_name["Contains Duplicate"]["url"]
    assert "is-anagram" in by_name["Valid Anagram"]["url"]


def test_the_leetcode_url_is_kept_alongside(found):
    for section in found.values():
        for problem in section["problems"]:
            assert problem["leetcode_url"].startswith("https://leetcode.com/problems/")
            assert not problem["leetcode_url"].endswith("problems//")


def test_each_problem_carries_its_own_minutes(found):
    """A set that lists nine problems and one number is still hiding the
    timing. Each line has to say what it costs."""
    for section in found.values():
        for problem in section["problems"]:
            assert problem["minutes"] == MINUTES_BY_DIFFICULTY[problem["difficulty"].title()]
        assert sum(p["minutes"] for p in section["problems"]) == section["minutes"]


def test_the_label_is_the_title_the_page_serves(found):
    """NeetCode renames: "Rotting Oranges" is "Rotting Fruit" there.

    Every title in the cache was read off the live page. Labelling a link with
    the LeetCode name would send the reader looking for a heading that is not
    on the screen they land on.
    """
    by_name = {
        p["problem"]: p for section in found.values() for p in section["problems"]
    }
    assert by_name["Rotting Oranges"]["title"] == "Rotting Fruit"
    assert by_name["Walls And Gates"]["title"] == "Islands and Treasure"
    assert by_name["Contains Duplicate"]["title"] == "Contains Duplicate"


def test_every_problem_has_a_verified_title(found):
    """A missing title would silently fall back to the LeetCode name, which is
    the failure this is meant to make loud."""
    rows = nc.fetch()
    missing = [r["problem"] for r in rows if not r.get("nc_title")]
    assert not missing, f"{len(missing)} problem(s) never had their page read: {missing[:5]}"


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
