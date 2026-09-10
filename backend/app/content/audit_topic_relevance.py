"""Is the mapped page *about* the topic, or does it merely contain it?

Nothing asked this before. Every audit in this project checks something else:
whether the URL resolves, whether the provider matches the host, whether the
title is the page's real title, whether a DSA topic got a section index instead
of its own page. A page can pass all four and still be the wrong page.

So they were found one at a time, on the morning each came up:

    "System calls"     ->  MIT Missing Semester, "Debugging and Profiling"
    "Array traversal"  ->  the index for the entire Arrays section
    "Pipes"            ->  "Course Overview + Introduction to the Shell"

Two weeks of fixing reported instances, because the thing being reported was
never measured.

THE SIGNAL
----------
The first version of this asked "does the page mention the topic". That is the
wrong question, and it cleared the very case that prompted it: MIT's debugging
lecture has a section headed "System Call Tracing", so the words were there and
the page passed. The words being there was never the point.

What matters is *where* the topic sits:

    subject       the topic is in the page <title> or <h1>       -- correct
    section-of    only in a lower heading: one part of a bigger  -- suspect
                  page, and the bigger the page the worse it is
    mentioned     only in the prose: a passing reference         -- wrong
    off-topic     nowhere on the page                            -- wrong

A topic worth a day of study needs a page whose subject it is. "System calls"
being section 5 of 25 on a debugging page is the whole complaint, and now it
has a name.

Matching is conjunctive and phrase-first: every word of the topic name must be
present in the tier being tested. The old version OR'd them, so "System calls"
matched a page containing "system" in one heading and "Callgrind" in another.

    python -m app.content.audit_topic_relevance              # report
    python -m app.content.audit_topic_relevance --refresh    # refetch pages
    python -m app.content.audit_topic_relevance --json out.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.console import use_utf8  # noqa: E402
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402

CACHE = Path(__file__).parent / "data" / "page_text.json"

#: Bumped when `extract` starts recording a field the verdict depends on.
#: Entries carrying an older number are refetched rather than judged on fields
#: they do not have -- an absent <h1> must not read as "no h1 on the page".
CACHE_VERSION = 2

#: How much page body is kept. See the note in extract().
BODY_CHARS = 4000

#: Roles the learner is actually sent to read. A REFERENCE or DEEP_DIVE row is
#: extra material and is judged less strictly.
AUDITED_ROLES = ("PRIMARY",)

#: Hosts whose served HTML carries no readable statement of the subject: a
#: YouTube watch page is a JavaScript shell, arXiv is an abstract stub, and a
#: raw notebook is JSON. Judging these on their markup produced false accusations
#: -- the U-Net paper was flagged as off-topic for the U-Net lesson -- so they
#: are recorded as unjudgeable and left to a human.
OPAQUE_HOSTS = (
    "youtube.com", "youtu.be", "arxiv.org", "raw.githubusercontent.com",
    "colab.research.google.com", "kaggle.com", "vimeo.com",
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

#: Wikipedia and friends refuse a spoofed browser string and serve 403, which
#: this audit then reported as a dead link. They accept a UA that says who is
#: asking, so a 403 is retried with one before being believed.
_POLITE_HEADERS = {
    "User-Agent": (
        "EngineeringOS/1.0 (personal study planner; "
        "+https://github.com/akshitjain1/engineering-os)"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

#: Words that carry no subject meaning, so their presence proves nothing.
#: Dropped from the topic phrase before matching, which is also why the phrase
#: stays contiguous: "Introduction of System Call" still contains "system call".
STOPWORDS = {
    "and", "the", "for", "with", "from", "into", "your", "that", "this", "what",
    "how", "why", "when", "basic", "basics", "intro", "introduction", "concept",
    "concepts", "fundamental", "fundamentals", "overview", "awareness", "using",
    "about", "part", "model", "models", "type", "types",
    "work", "works", "working", "understand", "understanding", "definition",
    "example", "examples", "guide", "tutorial", "learn", "learning", "topic",
    "step", "steps", "first", "next", "more", "other", "both", "than", "then",
    "solution", "solutions", "based",
    # Editorial words: they describe the learner's relationship to the subject,
    # not the subject. Taken from the curriculum's own topic names rather than
    # imagined -- these are the trailing modifiers that actually occur, led by
    # "basics" (22 topics), "awareness" (14) and "intuition" (12). Requiring
    # them accused correct pages: "Greedy reasoning" against GeeksforGeeks'
    # "Greedy Algorithms Tutorial", "Classic search" against "Binary Search".
    #
    # Dropping a word can only make matching easier, never harsher, so the
    # cost of being generous here is a missed flag -- and the two signals that
    # actually caught the reported bug (section-of, and one page serving many
    # topics) do not depend on the phrase at all.
    "intuition", "reasoning", "thinking", "essentials", "mechanics", "hygiene",
    "classic", "foundations", "primer", "recap", "mindset", "know", "must",
}

#: Domain prefixes on topic slugs, which say nothing about the subject.
SLUG_PREFIXES = ("cf-", "dsa-", "java-", "ml-", "dl-", "cv-", "nlp-", "genai-", "ai-")

#: Bodies served instead of the page: a bot challenge, a login wall, a consent
#: interstitial. Treating one as evidence produced five accusations against
#: Khan Academy pages that are perfectly correct -- Cloudflare had answered with
#: "Client Challenge" and the audit read that as the lesson.
BLOCK_SIGNS = (
    "client challenge", "just a moment", "enable javascript", "captcha",
    "access denied", "attention required", "verifying you are human",
    "unusual traffic", "are you a robot",
)

#: Where a topic can be found on a page, best first. The verdict is the best
#: tier that holds the whole topic name.
SUBJECT = "subject"
SECTION_OF = "section-of"
MENTIONED = "mentioned-only"
OFF_TOPIC = "off-topic"

ACCEPTED = "accepted"


def accepted_reasons() -> dict[str, str]:
    """slug -> why its page is right even though the phrase test fails.

    A handful of topics have no page anywhere whose title says their name:
    "filesystem navigation" is cd and ls, the best build-system material is
    called "Makefile Tutorial By Example", and a dry run is written up as a
    trace table. Those need somewhere to be written down, or the audit reports
    them forever and its output stops being read.

    Kept in the source maps next to the mappings themselves, each with a
    sentence of prose, so an exemption is a thing you can read rather than a
    silence. Missing modules are not an error -- the audit predates them and
    must still run without them.
    """
    reasons: dict[str, str] = {}
    for module in ("app.content.foundations_primary_sources",):
        try:
            mod = __import__(module, fromlist=["ACCEPTED"])
        except Exception:  # noqa: BLE001
            continue
        reasons.update(getattr(mod, "ACCEPTED", {}) or {})
    return reasons


#: A page whose subject is the topic but which also has this many headings is
#: still a fine page. One that merely *contains* the topic among this many is a
#: chapter of something else being sold as the day's material.
CROWDED_PAGE = 8


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _stem(word: str) -> str:
    """Crude but predictable: enough to match plural to singular and -ing forms.

    A real stemmer would be better and is not worth a dependency here; the
    comparison only has to be good enough to tell "system call" from
    "debugging and profiling".

    Every rule below was added because a correct mapping was being flagged:
    Git's "Rebasing" page against a topic named "Rebase", "Merging" against
    "Merge", "processes" against "process". A stemmer that folds the plural but
    not the singular is worse than none, because it fails silently.
    """
    # "ss" is not a plural: stripping it turned the singular "process" into
    # "proces" while "processes" became "process", so the two never met.
    if word.endswith("ss"):
        return word
    if len(word) > 6 and word.endswith("ies"):
        word = word[:-3] + "y"          # memories -> memory
    elif len(word) > 5 and word.endswith("ing"):
        word = word[:-3]                # rebasing -> rebas
    elif len(word) > 5 and word.endswith("ed"):
        word = word[:-2]                # linked -> link
    elif len(word) > 5 and word.endswith("es"):
        word = word[:-2]                # processes -> process
    elif len(word) > 4 and word.endswith("s"):
        word = word[:-1]                # calls -> call
    if len(word) > 6 and word.endswith("ment"):
        word = word[:-4]                # management -> manage -> manag
    # Trailing "e" last, so the gerund and the bare verb meet in the middle:
    # "rebasing" -> "rebas" and "rebase" -> "rebas".
    if len(word) > 3 and word.endswith("e"):
        word = word[:-1]
    return word


def normalise(text: str) -> str:
    """Stemmed words, single-spaced, padded -- so a phrase test is a substring
    test that still respects word boundaries."""
    return " " + " ".join(_stem(w) for w in _words(text)) + " "


def topic_phrase(name: str, slug: str) -> list[str]:
    """The stemmed words that must all be present for a page to be on this topic.

    Taken from the name, falling back to the slug when the name is nothing but
    stopwords. Focus concepts are deliberately excluded: a page can name every
    concept in a topic's list and still be a different lesson, and including
    them is what let broad course pages match eleven narrow topics each.
    """
    for source in (name, _slug_words(slug)):
        words = [_stem(w) for w in _words(source) if w not in STOPWORDS and len(w) >= 3]
        if words:
            return words
    return []


def _slug_words(slug: str) -> str:
    bare = slug or ""
    for prefix in SLUG_PREFIXES:
        if bare.startswith(prefix):
            bare = bare[len(prefix) :]
            break
    return bare.replace("-", " ")


#: Written both ways in the wild. A page titled "File System in Operating
#: System" is the right page for a topic named "Filesystems", and refusing it
#: over a space would send the audit hunting for a page that does not exist.
COMPOUNDS = {
    "filesystem": "file system",
    "filename": "file name",
    "runtime": "run time",
    "hashmap": "hash map",
    "linkedlist": "linked list",
    "commandline": "command line",
    "bytecode": "byte code",
    "multithreading": "multi threading",
}


def holds(text: str, phrase: list[str]) -> bool:
    """Does `text` contain the whole topic name?

    Contiguously if it can -- "system call" as a phrase -- and otherwise with
    every word present somewhere. Conjunctive either way: the old version was
    happy with any single word, which is how a debugging lecture passed for
    "System calls" on the strength of "system" and "Callgrind".
    """
    if not phrase:
        return False
    hay = normalise(text)
    if f" {' '.join(phrase)} " in hay:
        return True
    return all(_word_in(hay, word) for word in phrase)


def _word_in(hay: str, word: str) -> bool:
    if f" {word} " in hay:
        return True
    split = COMPOUNDS.get(word)
    return bool(split) and f" {normalise(split).strip()} " in hay


def looks_blocked(entry: dict[str, Any]) -> bool:
    """The response is an obstacle, not the document."""
    title = (entry.get("title") or "").strip().lower()
    if any(sign in title for sign in BLOCK_SIGNS):
        return True
    body = (entry.get("lead") or "").lower()[:600]
    if any(sign in body for sign in BLOCK_SIGNS):
        return True
    # A real article has a title and some prose. Neither means we were handed a
    # shell, and a shell is not evidence about the subject either way.
    return not title and len(body) < 200


def placement(entry: dict[str, Any], phrase: list[str]) -> str:
    """Which tier of the page holds the topic name."""
    if holds(f"{entry.get('title') or ''} {entry.get('h1') or ''}", phrase):
        return SUBJECT
    if holds(entry.get("headings") or "", phrase):
        return SECTION_OF
    if holds(entry.get("lead") or "", phrase):
        return MENTIONED
    return OFF_TOPIC


def extract(html: str) -> dict[str, Any]:
    """What the page says it is about, split by how loudly it says it."""
    no_script = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)

    def _text(fragment: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).strip()

    title = ""
    match = re.search(r"<title[^>]*>(.*?)</title>", no_script, re.I | re.S)
    if match:
        title = _text(match.group(1))

    # h1 is kept apart from h2/h3 because it is the page's subject, while an
    # h2 is one of its parts -- and that distinction is the whole verdict.
    h1 = [t for t in (_text(f) for f in
                      re.findall(r"<h1[^>]*>(.*?)</h1>", no_script, re.I | re.S)) if t]
    lower = [t for t in (_text(f) for f in
                         re.findall(r"<h[23][^>]*>(.*?)</h[23]>", no_script, re.I | re.S)) if t]

    # Enough body to tell a passing mention from silence, and no more. An
    # earlier version kept six paragraphs and accused correct pages of being
    # off-topic because the topic was named late; the version after that kept
    # 20,000 characters and made this cache 6.6MB in a repo that exists to be
    # a backup.
    #
    # Depth stopped mattering when the title and h1 became the thing that
    # decides "subject". The body now only separates "mentioned in passing"
    # from "not there at all", and both of those are flagged either way -- so a
    # short read can misfile a bad mapping between two bad labels, but it can
    # no longer clear or condemn a page on its own.
    body = _text(no_script)

    return {
        "v": CACHE_VERSION,
        "title": title,
        "h1": " | ".join(h1[:5]),
        "headings": " | ".join(lower[:60]),
        "heading_count": len(lower),
        "lead": body[:BODY_CHARS],
    }


def load_cache() -> dict[str, Any]:
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def _stale(entry: dict[str, Any]) -> bool:
    """An entry from before a field the verdict reads was recorded."""
    return entry.get("v", 1) < CACHE_VERSION and not entry.get("error") \
        and not entry.get("unreadable") and entry.get("status") == 200


def fetch_pages(urls: list[str], refresh: bool = False) -> dict[str, Any]:
    facts = {} if refresh else load_cache()
    missing = [u for u in urls if u not in facts or _stale(facts[u])]
    if not missing:
        return facts

    print(f"fetching {len(missing)} page(s)...")
    with httpx.Client(follow_redirects=True, timeout=30, headers=_HEADERS) as client:
        for i, url in enumerate(missing, 1):
            entry: dict[str, Any] = {"url": url, "v": CACHE_VERSION}
            try:
                resp = client.get(url)
                if resp.status_code == 403:
                    # Not necessarily a dead link -- some hosts only object to
                    # being told we are Chrome.
                    retry = client.get(url, headers=_POLITE_HEADERS)
                    if retry.status_code == 200:
                        resp = retry
                        entry["polite_ua"] = True
                entry["status"] = resp.status_code
                entry["final_url"] = str(resp.url)
                kind = resp.headers.get("content-type", "")
                entry["content_type"] = kind
                if any(h in url for h in OPAQUE_HOSTS):
                    entry["unreadable"] = True
                elif resp.status_code == 200 and "html" in kind.lower():
                    entry.update(extract(resp.text))
                elif resp.status_code == 200:
                    # A PDF or notebook cannot be read this way. Not a failure,
                    # and not evidence either -- recorded as unjudgeable.
                    entry["unreadable"] = True
            except Exception as exc:  # noqa: BLE001
                entry["error"] = f"{type(exc).__name__}: {exc}"
            facts[url] = entry
            if i % 20 == 0:
                print(f"  ... {i}/{len(missing)}")
                _save(facts)
            time.sleep(0.3)
    _save(facts)
    return facts


def _save(facts: dict[str, Any]) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE.with_name(CACHE.name + ".tmp")
    tmp.write_text(json.dumps(facts, indent=1, sort_keys=True), encoding="utf-8")
    tmp.replace(CACHE)


def rows(db) -> list[tuple[Any, Any]]:
    return (
        db.query(CurriculumResource, CurriculumTopic)
        .join(CurriculumLesson, CurriculumLesson.id == CurriculumResource.lesson_id)
        .join(CurriculumTopic, CurriculumTopic.id == CurriculumLesson.topic_id)
        .filter(
            CurriculumResource.role.in_(AUDITED_ROLES),
            CurriculumResource.url.isnot(None),
            CurriculumResource.url != "",
        )
        .all()
    )


def assess(db, facts: dict[str, Any]) -> list[dict[str, Any]]:
    """One verdict per audited resource."""
    pairs = [(r, t) for r, t in rows(db) if getattr(r, "learner_visible", True) is not False]

    # One page serving many topics is the shape of this whole class of bug: a
    # course week or a shell overview mapped to every topic it touches. Counted
    # here so triage can start with the worst offenders.
    served: dict[str, int] = {}
    for resource, _ in pairs:
        served[resource.url] = served.get(resource.url, 0) + 1

    accepted = accepted_reasons()
    out = []
    for resource, topic in pairs:
        entry = facts.get(resource.url) or {}
        phrase = topic_phrase(topic.name, topic.slug)

        if entry.get("error"):
            verdict = "unreachable"
        elif entry.get("status") != 200:
            verdict = f"http-{entry.get('status')}"
        elif entry.get("unreadable"):
            verdict = "unjudgeable"
        elif looks_blocked(entry):
            verdict = "blocked"
        elif not phrase:
            verdict = "no-terms"
        else:
            verdict = placement(entry, phrase)
            if verdict != SUBJECT and topic.slug in accepted:
                verdict = ACCEPTED

        out.append({
            "topic": topic.name,
            "slug": topic.slug,
            "domain": topic.domain_key,
            "resource_id": resource.id,
            "url": resource.url,
            "stored_title": resource.title,
            "page_title": entry.get("title"),
            "verdict": verdict,
            "phrase": " ".join(phrase),
            "heading_count": entry.get("heading_count"),
            "topics_sharing_page": served[resource.url],
            "accepted_because": accepted.get(topic.slug) if verdict == ACCEPTED else None,
        })
    return out


def crowding(row: dict[str, Any]) -> int:
    """How badly a section-of page is diluted, for ranking triage."""
    return (row.get("heading_count") or 0) + 4 * (row.get("topics_sharing_page") or 1)


def main(argv: list[str] | None = None) -> int:
    use_utf8()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="ignore the cache")
    parser.add_argument("--json", dest="json_out", help="write the full report here")
    parser.add_argument("--domain", help="limit to one domain_key")
    args = parser.parse_args(argv)

    db = SessionLocal()
    try:
        pairs = rows(db)
        urls = sorted({r.url for r, _ in pairs})
        facts = fetch_pages(urls, refresh=args.refresh)
        report = assess(db, facts)
    finally:
        db.close()

    if args.domain:
        report = [r for r in report if r["domain"] == args.domain]

    counts: dict[str, int] = {}
    for row in report:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1

    print(f"\naudited {len(report)} primary resources\n")
    for verdict, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {verdict:<14} {n}")

    exempt = [r for r in report if r["verdict"] == ACCEPTED]
    if exempt:
        print(f"\n{len(exempt)} mapping(s) accepted despite the phrase test:\n")
        for row in sorted(exempt, key=lambda r: r["slug"]):
            print(f"  [{row['domain']}] {row['topic']}")
            print(f"      {row['accepted_because']}")

    sections = sorted(
        (r for r in report if r["verdict"] == SECTION_OF), key=crowding, reverse=True
    )
    if sections:
        print(f"\n{len(sections)} topic(s) whose page covers them as one section "
              f"of something larger:\n")
        for row in sections:
            print(f"  [{row['domain']}] {row['topic']}")
            print(f"      page  : {row['page_title']}")
            print(f"      shape : {row['heading_count']} headings, "
                  f"serves {row['topics_sharing_page']} topic(s)")
            print(f"      url   : {row['url']}")

    for verdict, blurb in ((MENTIONED, "mention their topic only in passing"),
                           (OFF_TOPIC, "never mention their own topic")):
        bad = [r for r in report if r["verdict"] == verdict]
        if not bad:
            continue
        print(f"\n{len(bad)} page(s) that {blurb}:\n")
        for row in sorted(bad, key=lambda r: (r["domain"] or "", r["slug"])):
            print(f"  [{row['domain']}] {row['topic']}   (wanted: {row['phrase']})")
            print(f"      page : {row['page_title']}")
            print(f"      url  : {row['url']}")

    broken = [r for r in report
              if r["verdict"] == "unreachable" or r["verdict"].startswith("http-")]
    if broken:
        print(f"\n{len(broken)} page(s) that did not load:")
        for row in broken:
            print(f"  [{row['domain']}] {row['topic']:<34} {row['verdict']}  {row['url'][:60]}")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report, indent=1, sort_keys=True), encoding="utf-8"
        )
        print(f"\nfull report -> {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
