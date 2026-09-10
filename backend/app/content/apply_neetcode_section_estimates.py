"""Give every NeetCode collection row the size it actually is.

All 128 of them said 20 minutes. Arrays & Hashing is nine problems and about
195; Trees is fifteen and about 345; the whole 150 is roughly 63 hours. The
estimate was a constant with no method recorded against it, so nothing in the
app could tell it apart from a measured one.

This writes, per row:

    estimated_minutes  the section's problems costed at the same per-difficulty
                       rates as every LeetCode problem in the curriculum
    item_count         how many problems are in the section
    difficulty_mix     {"easy": 3, "medium": 6, "hard": 0}
    estimate_method    so a later reader can see where the number came from
    description        the problems by name, easiest first

Nothing is invented and nothing is dropped: the section keeps all of its
problems, which is the point -- the complaint was that twenty minutes was a
lie about nine problems, not that nine problems was too many.

    python -m app.content.apply_neetcode_section_estimates          # dry run
    python -m app.content.apply_neetcode_section_estimates --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.console import use_utf8  # noqa: E402
from app.content.neetcode_sections import describe, fetch, sections  # noqa: E402
from app.db.models import CurriculumResource  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402

#: "NeetCode 150 - Arrays & Hashing (representative subset)" -> "Arrays & Hashing".
#: An em dash, because that is what the titles use.
TITLE = re.compile(r"NeetCode 150\s*[—-]\s*(.+?)\s*\(", re.I)

METHOD = "neetcode_section_sum"

#: The titles in the curriculum abbreviate two sections that NeetCode spells
#: out. Without these, twenty-two dynamic-programming rows kept their flat 20
#: while everything around them was corrected -- the silent half of a fix.
ALIASES = {
    "1-d dp": "1-D Dynamic Programming",
    "2-d dp": "2-D Dynamic Programming",
    "1d dp": "1-D Dynamic Programming",
    "2d dp": "2-D Dynamic Programming",
}

#: Two rows are titled "NeetCode 150 - NeetCode 150", meaning the whole list
#: rather than one section. They are the whole list: 150 problems, ~63 hours.
WHOLE_LIST = "NeetCode 150"

#: The Core Skills rows are a different NeetCode tab and are not in the 150
#: data, so their minutes cannot be derived from it. They are single
#: implementation exercises, so the existing 20 is at least plausible -- but it
#: is still a default, and saying so is the whole point of this exercise.
CORE_SKILLS_METHOD = "unverified_default"


def section_of(title: str) -> str | None:
    match = TITLE.search(title or "")
    if not match:
        return None
    name = match.group(1).strip()
    return ALIASES.get(name.lower(), name)


def whole_list(known: dict[str, dict]) -> dict:
    """Every section at once, for the rows that point at the entire 150."""
    problems = [p for section in known.values() for p in section["problems"]]
    mix = {
        key: sum(section["mix"][key] for section in known.values())
        for key in ("easy", "medium", "hard")
    }
    return {
        "problems": problems,
        "count": len(problems),
        "mix": mix,
        "minutes": sum(section["minutes"] for section in known.values()),
    }


def main(argv: list[str] | None = None) -> int:
    use_utf8()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="write to the database")
    parser.add_argument("--refresh", action="store_true", help="refetch NeetCode's data")
    args = parser.parse_args(argv)

    from app.db.migrate import ensure_optional_columns

    ensure_optional_columns(engine)

    known = sections(fetch(refresh=args.refresh))
    known[WHOLE_LIST] = whole_list(known)

    db = SessionLocal()
    try:
        rows = (
            db.query(CurriculumResource)
            .filter(CurriculumResource.url.like("%neetcode.io%"))
            .order_by(CurriculumResource.id)
            .all()
        )

        matched: list[tuple[CurriculumResource, str]] = []
        core_skills: list[CurriculumResource] = []
        unmatched: list[CurriculumResource] = []

        for row in rows:
            name = section_of(row.title or "")
            if name and name in known:
                matched.append((row, name))
            elif "core skills" in (row.title or "").lower():
                core_skills.append(row)
            else:
                unmatched.append(row)

        print(f"{len(rows)} NeetCode rows: {len(matched)} sized from the 150 data, "
              f"{len(core_skills)} Core Skills, {len(unmatched)} unmatched\n")

        seen: set[str] = set()
        for row, name in matched:
            section = known[name]
            if name not in seen:
                seen.add(name)
                mix = section["mix"]
                print(f"  {name:<26} {row.estimated_minutes:>3} -> "
                      f"{section['minutes']:>4} min   ({section['count']} problems: "
                      f"E{mix['easy']} M{mix['medium']} H{mix['hard']})")

        if unmatched:
            print("\nUnmatched -- left alone, and worth a look:")
            for row in unmatched:
                print(f"  res={row.id}  {row.title}")

        if not args.apply:
            print("\nDry run. Re-run with --apply to write.")
            return 0

        for row, name in matched:
            section = known[name]
            row.estimated_minutes = section["minutes"]
            row.item_count = section["count"]
            row.difficulty_mix = section["mix"]
            # The problems themselves, each with its own page. Before this the
            # card could only link at the whole 150 and say "open the Arrays &
            # Hashing section" -- NeetCode does have per-problem URLs, and the
            # slug is its own rather than LeetCode's.
            row.collection_items = section["problems"]
            row.estimate_method = METHOD
            row.estimate_confidence = "HIGH"
            row.description = (
                describe(name, section) if name != WHOLE_LIST
                else (f"All of NeetCode 150: {section['count']} problems "
                      f"({section['mix']['easy']} easy, {section['mix']['medium']} medium, "
                      f"{section['mix']['hard']} hard), about "
                      f"{section['minutes'] // 60} hours in total. This is the whole "
                      "roadmap, not one topic's worth -- work the section that matches "
                      "today's pattern.")
            )
        for row in core_skills:
            # One exercise, so the count is honest even if the minutes are a
            # default. Marking the method is what stops it reading as measured.
            row.item_count = 1
            row.estimate_method = CORE_SKILLS_METHOD
            row.estimate_confidence = "LOW"
        db.commit()
        print(f"\n{len(matched)} collection(s) resized, "
              f"{len(core_skills)} Core Skills row(s) marked as defaults.")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
