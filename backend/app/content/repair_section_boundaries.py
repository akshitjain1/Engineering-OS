"""Stop resources claiming a section boundary they do not have.

The topic page renders a resource's ``section`` as **"Exact section: ..."**.
That is a promise: this page is long, and here is the part that is yours. 104
of 455 PRIMARY resources broke the promise by storing a string derived from the
URL itself:

    url:     https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository
    section: Git-Basics-Recording-Changes-to-the-Repository

    url:     https://cs50.harvard.edu/x/weeks/0/
    section: 0

    url:     https://missing.csail.mit.edu/2026/command-line-environment/
    section: command-line-environment

Zero information, and worse than nothing: it reads as though someone pinned a
section when nobody did.

A further 132 PRIMARY resources stored no section at all, which leaves the
same question unanswered. Both cases are handled the same way, because the
honest answer depends only on one thing: whether any other topic opens the
same page.

There are two situations underneath, and they need opposite fixes:

**The URL is already the whole topic.** Each Git Book page is one chapter on
one subject, and only one topic points at it. The honest value is
``FULL_SINGLE_PAGE`` -- read the page, all of it. That is what this script
writes.

**The URL is shared by several topics.** Four topics open CS50 Week 0; six open
the Missing Semester command-line lecture. Here a boundary genuinely is needed
and genuinely is missing, and inventing one would be worse than admitting it.
This script leaves those alone, clears the misleading string, and lists them so
the gap is visible. The topic page already warns when a multi-topic resource
has no boundary.

Run:
    python -m app.content.repair_section_boundaries --dry-run
    python -m app.content.repair_section_boundaries
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

BACKEND = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND / "dev.db"
REPORTS = BACKEND / "reports"

_EXT = re.compile(r"\.(html?|md|mdx|py|pdf|php|aspx)$", re.I)

#: Some titles already carry the boundary as an instruction -- "Abdul Bari
#: Algorithms playlist - watch: Merge Sort". 101 DSA topics share that playlist
#: and every one of them names its own video this way, but the instruction sat
#: in the title while the section stayed empty, so the page showed a
#: "section/timestamp missing" warning next to a title that answered it.
_TITLE_BOUNDARY = re.compile(
    r"(?:watch|read|see|study)\s*:\s*(?P<part>.+?)\s*$", re.I
)


def echoes_url(section: str | None, url: str | None) -> bool:
    """True when the section string carries nothing the URL did not already."""
    if not section or not url:
        return False
    value = section.strip()
    if not value or value == "FULL_SINGLE_PAGE":
        return False

    lowered = value.lower()
    # "above; content inspection pending" -- a note to self, not a boundary.
    if lowered.startswith("above"):
        return True
    # A bare number, e.g. section "0" for CS50 Week 0.
    if re.fullmatch(r"\d+", lowered):
        return True

    segments = [s for s in urlparse(url).path.lower().split("/") if s]
    if not segments:
        return False
    last = segments[-1]
    stem = _EXT.sub("", last)
    candidates = {last, stem, stem.replace("-", " "), stem.replace("_", " ")}
    return lowered in candidates or lowered.replace(" ", "-") in {last, stem}


def boundary_from_title(title: str | None) -> str | None:
    """Pull an explicit "watch: X" / "read: X" instruction out of a title."""
    if not title:
        return None
    match = _TITLE_BOUNDARY.search(title)
    if not match:
        return None
    part = match.group("part").strip(" .-")
    # Guard against a title that merely ends in the word, or a whole sentence.
    return part if 2 <= len(part) <= 120 else None


def collect(conn: sqlite3.Connection) -> tuple[list[dict], list[dict], list[dict]]:
    """Return (set FULL_SINGLE_PAGE, needs a real boundary, boundary in title)."""
    conn.row_factory = sqlite3.Row
    rows = list(
        conn.execute(
            """
            SELECT r.id, r.url, r.section, r.role, r.exactness, r.title,
                   t.slug AS topic_slug, m.slug AS module_slug
              FROM curriculum_resources r
              JOIN curriculum_lessons l ON r.lesson_id = l.id
              JOIN curriculum_topics t ON l.topic_id = t.id
              JOIN curriculum_modules m ON t.module_id = m.id
             WHERE r.url IS NOT NULL AND r.url != ''
            """
        )
    )

    # How many distinct topics open each URL at all, in any role. A page one
    # topic owns can be read whole; a page six topics share cannot.
    topics_per_url: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        topics_per_url[row["url"]].add(row["topic_slug"])

    sole, shared, from_title = [], [], []
    for row in rows:
        stored = (row["section"] or "").strip()
        # Before anything else: if the title states the boundary and the
        # section does not, move it to where the page looks for it.
        if not stored:
            named = boundary_from_title(row["title"])
            if named:
                from_title.append(
                    {
                        "id": row["id"],
                        "topic_slug": row["topic_slug"],
                        "module_slug": row["module_slug"],
                        "url": row["url"],
                        "old_section": row["section"],
                        "new_section": named,
                        "new_exactness": None,
                        "from_title": row["title"],
                        "topics_sharing_url": [],
                    }
                )
                continue
        # Two cases get the same treatment: a section that merely echoes the
        # URL, and no section at all. Both leave the learner without an answer
        # to "how much of this page is mine?", and the honest answer depends
        # only on whether anyone else opens the same page.
        empty_primary = not stored and (row["role"] or "").upper() == "PRIMARY"
        if not empty_primary and not echoes_url(stored, row["url"]):
            continue
        entry = {
            "id": row["id"],
            "topic_slug": row["topic_slug"],
            "module_slug": row["module_slug"],
            "url": row["url"],
            "old_section": row["section"],
            "topics_sharing_url": sorted(topics_per_url[row["url"]]),
        }
        if len(topics_per_url[row["url"]]) == 1:
            if stored == "FULL_SINGLE_PAGE":
                continue
            entry["new_section"] = "FULL_SINGLE_PAGE"
            entry["new_exactness"] = None  # leave as recorded
            sole.append(entry)
        else:
            # Clear the false claim; do not invent a boundary. Also mark the
            # resource MULTI_TOPIC, because otherwise clearing the section just
            # makes the page render nothing at all -- the topic page only warns
            # about a missing boundary when exactness says the page covers more
            # than this topic. An admitted gap has to be visible to be useful.
            entry["new_section"] = None
            entry["new_exactness"] = "MULTI_TOPIC"
            if not stored and (row["exactness"] or "") in ("MULTI_TOPIC", "COLLECTION"):
                continue  # already admitted; nothing to change
            shared.append(entry)
    return sole, shared, from_title


def apply(conn: sqlite3.Connection, rows: list[dict]) -> int:
    for row in rows:
        conn.execute(
            "UPDATE curriculum_resources "
            "SET section = ?, exactness = COALESCE(?, exactness) "
            "WHERE id = ?",
            (row["new_section"], row.get("new_exactness"), row["id"]),
        )
    conn.commit()
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    sole, shared, from_title = collect(conn)

    print(f"{len(from_title)} resource(s) whose title already names the boundary")
    for row in from_title[:6]:
        print(f"  [{row['topic_slug']}] -> {row['new_section']!r}")
    if len(from_title) > 6:
        print(f"  ... and {len(from_title) - 6} more")

    print(f"\n{len(sole)} resource(s) whose URL is the whole topic -> FULL_SINGLE_PAGE")
    for row in sole[:10]:
        print(f"  [{row['topic_slug']}] {row['old_section']!r}")
    if len(sole) > 10:
        print(f"  ... and {len(sole) - 10} more")

    print(f"\n{len(shared)} resource(s) on a page shared by several topics.")
    print("These need a real boundary. The misleading string is cleared, not replaced:")
    by_url: dict[str, list[dict]] = defaultdict(list)
    for row in shared:
        by_url[row["url"]].append(row)
    for url, group in sorted(by_url.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(group[0]['topics_sharing_url'])} topics open {url}")
        for row in group:
            print(f"      {row['topic_slug']} (was {row['old_section']!r})")

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "section_boundary_repairs.json").write_text(
        json.dumps(
            {
                "boundary_taken_from_title": from_title,
                "set_full_page": sole,
                "needs_a_real_boundary": shared,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    if args.dry_run:
        print("\ndry run — nothing written")
        return

    changed = apply(conn, from_title + sole + shared)
    print(f"\nupdated {changed} resource row(s)")
    print("the shared-page list above is a genuine content gap, recorded in")
    print("reports/section_boundary_repairs.json")


if __name__ == "__main__":
    main()
