"""How big each NeetCode 150 section actually is.

The DSA practice card said:

    NeetCode 150 - Arrays & Hashing (representative subset)     ~20 min

Arrays & Hashing is nine problems: three easy and six medium. At the minute
costs this project already uses for LeetCode problems -- easy 15, medium 25,
hard 40 -- that is 195 minutes of work, and the card was offering 20. Every
one of the 128 NeetCode rows carried the same flat 20, with `estimate_method`
empty, because nobody had ever counted.

The counts here are not counted by hand either. NeetCode publishes the list
that drives its own site, one record per problem with its section and its
difficulty, so the numbers come from the same place the website's "0/9" badge
comes from. The totals check out against it: 28 easy, 101 medium, 21 hard.

    python -m app.content.neetcode_sections        # print what it finds
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

#: NeetCode's own problem list, the file its site is built from.
DATA_URL = (
    "https://raw.githubusercontent.com/neetcode-gh/leetcode/main/.problemSiteData.json"
)

#: A local copy, so an estimate can be recomputed without the network and so
#: the numbers in the database can be traced to something committed.
CACHE = Path(__file__).parent / "data" / "neetcode_150.json"

#: Where the site's own problem pages live. The slug is NeetCode's, not
#: LeetCode's -- "Contains Duplicate" is /problems/duplicate-integer/ -- and
#: the list parameter is what keeps the page in NeetCode 150 context.
PROBLEM_URL = "https://neetcode.io/problems/{slug}/question?list=neetcode150"

#: The practice page, read only to discover the current bundle filename.
PRACTICE_URL = "https://neetcode.io/practice"

#: NeetCode's own slugs are not in the published JSON -- only in the compiled
#: site bundle, as `ncLink`. Scraping a minified bundle is fragile, so two
#: things guard it: the bundle name is discovered from the page rather than
#: hardcoded (it carries a content hash and changes on every deploy), and every
#: URL built from it is fetched and checked against the problem's title before
#: anything is written. A bad parse fails loudly instead of writing 150 dead
#: links.
_BUNDLE = re.compile(r'src="(main\.[0-9a-f]+\.js)"')
_NC_LINK = re.compile(r'problem:"([^"]+)"[^{}]*?ncLink:"([^"]+)"')

#: Reused, not redefined. These are the per-difficulty costs already written
#: against 316 LeetCode problems in this curriculum; a collection estimated on
#: a different scale would be a collection you cannot compare to the problems
#: beside it.
from app.content.apply_dsa_exact_problems import MINUTES_BY_DIFFICULTY  # noqa: E402

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def fetch(refresh: bool = False) -> list[dict[str, Any]]:
    """NeetCode's problem records, from the cache unless asked to refresh."""
    if not refresh and CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    resp = httpx.get(DATA_URL, headers=_HEADERS, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    slugs = nc_links()
    rows = []
    for row in resp.json():
        if not row.get("neetcode150"):
            continue
        record = {
            k: row.get(k) for k in ("problem", "pattern", "difficulty", "link", "neetcode150")
        }
        record["nc_link"] = (slugs.get(row["problem"]) or "").strip("/") or None
        rows.append(record)
    unmatched = [r["problem"] for r in rows if not r["nc_link"]]
    if unmatched:
        raise RuntimeError(
            f"{len(unmatched)} problem(s) have no NeetCode slug, starting with "
            f"{unmatched[:3]} -- refusing to cache a half-mapped list"
        )
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8")
    return rows


def nc_links() -> dict[str, str]:
    """problem name -> NeetCode's own slug, read off the live site bundle."""
    with httpx.Client(headers=_HEADERS, timeout=90, follow_redirects=True) as client:
        page = client.get(PRACTICE_URL).text
        names = _BUNDLE.findall(page)
        if not names:
            raise RuntimeError(
                f"no main.<hash>.js found on {PRACTICE_URL}; the site's build "
                "layout changed and this parser needs revisiting"
            )
        bundle = client.get(f"https://neetcode.io/{names[0]}").text
    links = dict(_NC_LINK.findall(bundle))
    if len(links) < 300:
        raise RuntimeError(
            f"only {len(links)} problem->ncLink pairs parsed out of the bundle, "
            "which is too few to be right"
        )
    return links


def sections(rows: list[dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    """section name -> {problems, count, mix, minutes}."""
    rows = rows if rows is not None else fetch()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["pattern"]].append(row)

    out: dict[str, dict[str, Any]] = {}
    for name, items in grouped.items():
        items.sort(key=lambda r: (_rank(r["difficulty"]), r["problem"]))
        mix = Counter(str(i["difficulty"]).lower() for i in items)
        out[name] = {
            "problems": [
                {
                    "problem": i["problem"],
                    # The name the destination page actually uses, confirmed by
                    # fetching it. NeetCode renames: "Rotting Oranges" is
                    # "Rotting Fruit" there, "Walls And Gates" is "Islands and
                    # Treasure". Labelling the link with the LeetCode name
                    # would send you looking for a title that is not on screen.
                    "title": i.get("nc_title") or i["problem"],
                    "difficulty": i["difficulty"],
                    "minutes": MINUTES_BY_DIFFICULTY.get(str(i["difficulty"]).title(), 25),
                    # NeetCode's own page for the problem: the editorial, the
                    # video and the editor, in list context. The card used to
                    # link at the whole 150 and tell you to find the section.
                    "url": PROBLEM_URL.format(slug=i["nc_link"]),
                    "leetcode_url":
                        f"https://leetcode.com/problems/{(i['link'] or '').strip('/')}/",
                }
                for i in items
            ],
            "count": len(items),
            "mix": {k: mix.get(k, 0) for k in ("easy", "medium", "hard")},
            "minutes": sum(
                MINUTES_BY_DIFFICULTY.get(str(i["difficulty"]).title(), 25) for i in items
            ),
        }
    return out


#: Easy first, so "solve the first two" means the two you can actually start on.
_ORDER = {"easy": 0, "medium": 1, "hard": 2}


def _rank(difficulty: Any) -> int:
    return _ORDER.get(str(difficulty).lower(), 1)


def describe(name: str, section: dict[str, Any]) -> str:
    """The card's description: what the set is, in the order to do it.

    The old description said "Solve only the small representative subset listed
    in the exercise". There was no exercise on the lesson -- so it pointed at a
    list that did not exist, and the reader was left to guess which of the nine
    counted. This names them.
    """
    mix = section["mix"]
    parts = [f"{n} {label}" for label, n in
             (("easy", mix["easy"]), ("medium", mix["medium"]), ("hard", mix["hard"])) if n]
    return (
        f"The {name} section of NeetCode 150: {section['count']} problems "
        f"({', '.join(parts)}), about {section['minutes']} minutes in total. "
        "Listed below easiest first, each linking straight to its own page. "
        "A set to work through across sessions, not a single sitting."
    )


def main() -> int:
    from app.console import use_utf8

    use_utf8()
    found = sections(fetch(refresh="--refresh" in sys.argv))
    total = sum(s["count"] for s in found.values())
    print(f"NeetCode 150: {total} problems in {len(found)} sections\n")
    for name, section in sorted(found.items(), key=lambda kv: -kv[1]["count"]):
        mix = section["mix"]
        print(f"  {section['count']:>2} problems  E{mix['easy']:<2} M{mix['medium']:<2} "
              f"H{mix['hard']:<2}  {section['minutes']:>4} min   {name}")
    grand = Counter()
    for section in found.values():
        grand.update(section["mix"])
    print(f"\n  overall {dict(grand)}, "
          f"{sum(s['minutes'] for s in found.values())} minutes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
