"""Fetch every NeetCode problem URL and check it is the problem it claims.

The slugs behind these URLs are scraped out of a minified site bundle, because
NeetCode's published JSON does not carry them. That is exactly the kind of
source that works today and rots quietly, and the app has been burned by
quietly-rotten links before: 261 dead URLs sat behind audits that only checked
whether a title existed.

So every URL is opened and its <title> compared against the problem's name.
NeetCode renames problems on its own site -- "Contains Duplicate" lives at
/problems/duplicate-integer/ -- so the check is against the title the page
serves, not against the slug.

    python -m app.content.verify_neetcode_problem_urls
    python -m app.content.verify_neetcode_problem_urls --json out.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.console import use_utf8  # noqa: E402
from app.content.neetcode_sections import _HEADERS, fetch, sections  # noqa: E402

_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)

#: NeetCode's title is "<Problem> - NeetCode".
SUFFIX = " - NeetCode"


def page_title(html: str) -> str:
    match = _TITLE.search(html)
    if not match:
        return ""
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(1))).strip()
    return text[: -len(SUFFIX)].strip() if text.endswith(SUFFIX) else text


def _normalise(text: str) -> str:
    """Compared loosely on purpose: the two sides differ in punctuation and
    casing more often than in substance ("Encode and Decode Strings" against
    "String Encode and Decode")."""
    return " ".join(sorted(re.findall(r"[a-z0-9]+", (text or "").lower())))


#: A 5xx from a busy site is not a broken link. One problem out of 150 came
#: back 503 on the first pass and 200 immediately after, and recording that as
#: a dead URL would have removed a working problem from the set.
RETRIES = 3


def check(client: httpx.Client, problem: dict) -> dict:
    row = {"problem": problem["problem"], "url": problem["url"]}
    resp = None
    for attempt in range(RETRIES):
        try:
            resp = client.get(problem["url"])
        except Exception as exc:  # noqa: BLE001
            row["status"] = None
            row["error"] = f"{type(exc).__name__}: {exc}"
            if attempt == RETRIES - 1:
                row["verdict"] = "unreachable"
                return row
            time.sleep(1.5 * (attempt + 1))
            continue
        if resp.status_code < 500:
            break
        if attempt < RETRIES - 1:
            time.sleep(1.5 * (attempt + 1))

    row.pop("error", None)
    row["status"] = resp.status_code
    row["title"] = page_title(resp.text) if resp.status_code == 200 else ""

    if resp.status_code != 200:
        row["verdict"] = f"http-{resp.status_code}"
    elif not row["title"]:
        row["verdict"] = "no-title"
    elif _normalise(row["title"]) == _normalise(problem["problem"]):
        row["verdict"] = "exact"
    else:
        row["verdict"] = "renamed"
    return row


def main(argv: list[str] | None = None) -> int:
    use_utf8()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", dest="json_out")
    parser.add_argument(
        "--write-titles",
        action="store_true",
        help="store each verified page title in the cache, so the card can "
             "label a link with the name the destination actually uses",
    )
    args = parser.parse_args(argv)

    problems = [p for section in sections(fetch()).values() for p in section["problems"]]
    print(f"checking {len(problems)} NeetCode problem URLs...\n")

    results = []
    with httpx.Client(headers=_HEADERS, timeout=30, follow_redirects=True) as client:
        for i, problem in enumerate(problems, 1):
            results.append(check(client, problem))
            if i % 25 == 0:
                print(f"  ... {i}/{len(problems)}")
            time.sleep(0.25)

    counts: dict[str, int] = {}
    for row in results:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    print()
    for verdict, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {verdict:<14} {n}")

    # A page that serves a different title is not necessarily wrong -- NeetCode
    # renames -- but it is the only category a human needs to look at.
    renamed = [r for r in results if r["verdict"] == "renamed"]
    if renamed:
        print(f"\n{len(renamed)} page(s) whose title differs from the problem name:")
        for row in renamed:
            print(f"  {row['problem'][:38]:<38} -> {row['title'][:38]}")

    broken = [r for r in results
              if r["verdict"] not in ("exact", "renamed")]
    if broken:
        print(f"\n{len(broken)} URL(s) that did not serve a problem page:")
        for row in broken:
            print(f"  {row['verdict']:<14} {row['problem'][:34]:<34} {row['url']}")

    if args.write_titles:
        from app.content.neetcode_sections import CACHE

        titles = {
            r["problem"]: r["title"]
            for r in results
            if r["verdict"] in ("exact", "renamed") and r["title"]
        }
        rows = json.loads(CACHE.read_text(encoding="utf-8"))
        missing = [r["problem"] for r in rows if r["problem"] not in titles]
        if missing:
            print(f"\nRefusing to write titles: {len(missing)} problem(s) were not "
                  f"confirmed, starting with {missing[:3]}.")
            return 1
        for record in rows:
            record["nc_title"] = titles[record["problem"]]
        CACHE.write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8")
        print(f"\nwrote {len(titles)} verified page titles into {CACHE.name}")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(results, indent=1, sort_keys=True), encoding="utf-8"
        )
        print(f"\nfull report -> {args.json_out}")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
