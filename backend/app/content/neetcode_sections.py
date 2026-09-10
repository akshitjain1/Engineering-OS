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
    rows = [
        {k: row.get(k) for k in ("problem", "pattern", "difficulty", "link", "neetcode150")}
        for row in resp.json()
        if row.get("neetcode150")
    ]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8")
    return rows


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
                {"problem": i["problem"], "difficulty": i["difficulty"],
                 "url": f"https://leetcode.com/problems/{(i['link'] or '').strip('/')}/"}
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
    listing = ", ".join(
        f"{p['problem']} ({p['difficulty'].lower()})" for p in section["problems"]
    )
    return (
        f"The {name} section of NeetCode 150: {section['count']} problems "
        f"({', '.join(parts)}), about {section['minutes']} minutes in total. "
        f"Easiest first: {listing}. "
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
