"""The audit must tell "is about" apart from "happens to contain".

"System calls" was mapped to MIT's *Debugging and Profiling* lecture for weeks.
The first version of this audit was written to catch exactly that and cleared
it: the lecture has a section headed "System Call Tracing", so the words were
present and the page passed. Presence was never the question.

So the first test here is that case, by name. If it ever returns "subject"
again, this file fails.
"""

from __future__ import annotations

from app.content import audit_topic_relevance as audit

# The real headings of https://missing.csail.mit.edu/2026/debugging-profiling/,
# fetched on 2026-09-10. "System Call Tracing" is section 5 of 25.
MIT_DEBUGGING = {
    "v": audit.CACHE_VERSION,
    "status": 200,
    "title": "Debugging and Profiling &middot; Missing Semester",
    "h1": "Debugging and Profiling",
    "headings": (
        "Debugging | Printf Debugging and Logging | Debuggers | "
        "Record-Replay Debugging | System Call Tracing | strace (Linux) and "
        "dtruss (macOS) | bpftrace and eBPF | Network Debugging | Memory "
        "Debugging | Sanitizers | Valgrind | AI for Debugging | Profiling | "
        "Timing | Resource Monitoring | CPU Profilers | perf | "
        "Valgrind's Callgrind | Memory Profilers | Benchmarking | Exercises"
    ),
    "heading_count": 21,
    "lead": "In this lecture we cover strace, ltrace and other tools.",
}

# https://www.geeksforgeeks.org/operating-systems/introduction-of-system-call/
GFG_SYSTEM_CALL = {
    "v": audit.CACHE_VERSION,
    "status": 200,
    "title": "Introduction of System Call - GeeksforGeeks",
    "h1": "Introduction of System Call",
    "headings": "Services Provided by System Calls | Types of System Calls",
    "heading_count": 2,
    "lead": "A system call is a programmatic way a program requests a service.",
}


def _verdict(entry, name, slug):
    phrase = audit.topic_phrase(name, slug)
    if audit.looks_blocked(entry):
        return "blocked"
    return audit.placement(entry, phrase)


# --------------------------------------------------------------------------
# the reported case
# --------------------------------------------------------------------------

def test_a_lecture_with_one_section_on_the_topic_is_not_its_subject():
    """The bug, as reported, as a test."""
    assert _verdict(MIT_DEBUGGING, "System calls", "cf-system-calls") == audit.SECTION_OF


def test_the_page_the_learner_asked_for_is_the_subject():
    assert _verdict(GFG_SYSTEM_CALL, "System calls", "cf-system-calls") == audit.SUBJECT


def test_the_two_are_not_scored_the_same():
    """Ordering, not just labels: whatever the tiers are called, the dedicated
    page must rank above the lecture that mentions the topic in a heading."""
    order = [audit.SUBJECT, audit.SECTION_OF, audit.MENTIONED, audit.OFF_TOPIC]
    good = order.index(_verdict(GFG_SYSTEM_CALL, "System calls", "cf-system-calls"))
    weak = order.index(_verdict(MIT_DEBUGGING, "System calls", "cf-system-calls"))
    assert good < weak


# --------------------------------------------------------------------------
# the matcher itself
# --------------------------------------------------------------------------

def test_the_topic_name_is_matched_whole_not_word_by_word():
    """The defect underneath the defect.

    The old matcher OR'd the topic's words, so a page saying "system" in one
    heading and "Callgrind" in another satisfied "System calls".
    """
    scattered = dict(MIT_DEBUGGING, headings="Resource Monitoring | Valgrind's Callgrind",
                     lead="No mention of the kernel interface here.")
    assert _verdict(scattered, "System calls", "cf-system-calls") == audit.OFF_TOPIC


def test_stopwords_between_the_words_do_not_break_the_phrase():
    """"Introduction of System Call" contains "system call"."""
    assert audit.holds("Introduction of System Call", ["system", "call"])


def test_plural_and_singular_match():
    assert audit.holds("Types of System Calls", ["system", "call"])
    assert audit.holds("What is a system call?", ["system", "call"])


def test_a_word_inside_a_longer_word_does_not_count():
    """"Callgrind" is not "call"; "subprocess" is not "process"."""
    assert not audit.holds("Valgrind's Callgrind profiler", ["call"])
    assert not audit.holds("Managing subprocesses", ["process"])


def test_a_compound_matches_its_spaced_spelling():
    """"File System in Operating System" is the right page for "Filesystems".

    Insisting on the closed spelling would have this audit reject the correct
    page and keep hunting for one that does not exist.
    """
    assert audit.holds("File System in Operating System", ["filesystem"])
    assert audit.holds("Filesystem layout", ["filesystem"])
    assert not audit.holds("Operating System Concepts", ["filesystem"])


def test_body_only_is_a_passing_reference():
    buried = dict(MIT_DEBUGGING, headings="Timing | Benchmarking",
                  lead="Later on we use strace to trace a system call or two.")
    assert _verdict(buried, "System calls", "cf-system-calls") == audit.MENTIONED


def test_a_page_about_nothing_related_is_off_topic():
    other = {"v": audit.CACHE_VERSION, "status": 200, "title": "Baking Sourdough",
             "h1": "Baking Sourdough", "headings": "Starter | Proofing",
             "heading_count": 2, "lead": "Flour, water, salt and time." * 30}
    assert _verdict(other, "System calls", "cf-system-calls") == audit.OFF_TOPIC


def test_the_slug_carries_the_topic_when_the_name_cannot():
    """A name made only of stopwords still has to be judged on something."""
    assert audit.topic_phrase("Overview", "cf-virtual-memory") == ["virtual", "memory"]


def test_plurals_fold_onto_their_singular_not_onto_a_stub():
    """"memories" and "memory" must reach the same stem, or a page titled
    "Virtual Memory" fails to match a topic written in the plural."""
    assert audit._stem("memories") == audit._stem("memory")
    assert audit._stem("processes") == audit._stem("process")
    assert audit._stem("arrays") == audit._stem("array")


def test_a_gerund_title_matches_the_bare_verb():
    """Git's page is titled "Rebasing"; the topic is named "Rebase".

    Both of those mappings are correct and both were being flagged, which is
    the failure mode that matters most here: a stemmer that folds one side of
    a pair and not the other reports good work as broken.
    """
    for bare, gerund in (("rebase", "rebasing"), ("merge", "merging"),
                         ("pipe", "piping"), ("code", "coding")):
        assert audit._stem(bare) == audit._stem(gerund), f"{bare} != {gerund}"
    # Through topic_phrase, because that is how a phrase reaches holds(): the
    # topic side is stemmed exactly once, like the page side.
    assert audit.holds("Git - Rebasing", audit.topic_phrase("Rebase", "cf-rebase"))
    assert audit.holds("Basic Branching and Merging", audit.topic_phrase("Merge", "cf-merge"))


def test_the_stemmer_is_applied_exactly_once_on_each_side():
    """_stem is deliberately not idempotent, and callers must not double it.

    "rebase" stems to "rebas", and stemming *that* again strips the trailing
    "s" to "reba". Both sides of a comparison go through _stem once -- the page
    via normalise(), the topic via topic_phrase() -- and this pins that down so
    a future "stem it again to be safe" is caught here rather than silently
    breaking every match ending in s.
    """
    once = audit._stem("rebase")
    assert once == "rebas"
    assert audit._stem(once) != once, (
        "if _stem becomes idempotent this test is obsolete, not wrong -- "
        "delete it rather than working around it"
    )


def test_a_past_participle_matches_too():
    assert audit._stem("linked") == audit._stem("link")
    assert audit._stem("sorted") == audit._stem("sort")


def test_a_nominalisation_matches_its_verb():
    """"Managing Application Dependencies" is the page for "Dependency
    management", and the -ment suffix was all that stood between them."""
    assert audit._stem("management") == audit._stem("managing")
    assert audit._stem("management") == audit._stem("manage")
    assert audit.holds(
        "Managing Application Dependencies - Python Packaging User Guide",
        audit.topic_phrase("Dependency management", "cf-dependency-management"),
    )


def test_focus_concepts_are_not_part_of_the_phrase():
    """A broad course page names every concept a topic lists and is still the
    wrong page. Including them is how one shell overview matched eleven topics.
    """
    assert audit.topic_phrase("Pipes", "cf-pipes") == [audit._stem("pipes")]


# --------------------------------------------------------------------------
# things that are not evidence
# --------------------------------------------------------------------------

def test_a_bot_challenge_is_not_an_accusation():
    """Cloudflare answered five correct Khan Academy links with a challenge
    page, and an earlier run read that as the lesson being off-topic."""
    challenge = {"v": audit.CACHE_VERSION, "status": 200, "title": "Just a moment...",
                 "h1": "", "headings": "", "heading_count": 0,
                 "lead": "Enable JavaScript and cookies to continue."}
    assert _verdict(challenge, "System calls", "cf-system-calls") == "blocked"


def test_an_empty_shell_is_not_an_accusation():
    shell = {"v": audit.CACHE_VERSION, "status": 200, "title": "", "h1": "",
             "headings": "", "heading_count": 0, "lead": "loading"}
    assert audit.looks_blocked(shell)


# --------------------------------------------------------------------------
# extraction
# --------------------------------------------------------------------------

HTML = """
<html><head><title>Introduction of System Call - GeeksforGeeks</title></head>
<body><h1>Introduction of System Call</h1>
<h2>Services Provided by System Calls</h2><p>A system call is how a program
asks the kernel for something.</p><h3>Types</h3>
<script>var x = "off-topic noise about sourdough";</script>
</body></html>
"""


def test_extract_keeps_h1_apart_from_lower_headings():
    """The whole verdict rests on this split: an h1 is the page's subject, an
    h2 is one of its parts. The first version merged h1-h3 into one field and
    therefore could not tell them apart."""
    got = audit.extract(HTML)
    assert got["h1"] == "Introduction of System Call"
    assert "Services Provided" in got["headings"]
    assert "Introduction of System Call" not in got["headings"]


def test_extract_counts_the_sections():
    assert audit.extract(HTML)["heading_count"] == 2


def test_extract_drops_script_text():
    assert "sourdough" not in audit.extract(HTML)["lead"]


def test_extract_stamps_the_cache_version():
    assert audit.extract(HTML)["v"] == audit.CACHE_VERSION


def test_entries_from_before_the_h1_split_are_refetched():
    """A cached page with no `h1` field is not a page without an h1.

    Judging one on the fields it lacks would silently mark good pages as
    section-of, which is worse than a slow run.
    """
    assert audit._stale({"v": 1, "status": 200, "title": "x"})
    assert not audit._stale({"v": audit.CACHE_VERSION, "status": 200, "title": "x"})
    # Nothing to re-extract from these, so refetching them buys nothing.
    assert not audit._stale({"v": 1, "error": "ConnectError: nope"})
    assert not audit._stale({"v": 1, "status": 200, "unreadable": True})


def test_crowding_ranks_the_worst_offender_first():
    """Triage order: a page serving eleven topics is a bigger problem than a
    long page serving one."""
    shared = {"heading_count": 6, "topics_sharing_page": 11}
    long_one = {"heading_count": 25, "topics_sharing_page": 1}
    assert audit.crowding(shared) > audit.crowding(long_one)
