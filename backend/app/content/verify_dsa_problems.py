"""Check every problem in DSA_EXACT_PROBLEMS against LeetCode itself.

Three things are verified per entry, and all three have to hold:

1. the slug resolves -- a typo becomes a hard failure, not a dead link
   shipped to the learner;
2. the problem is not Premium -- it resolves, but the learner cannot open it;
3. LeetCode's own topic tags include at least one tag the mapping claims.

(3) is the one that matters. It is what stops the file drifting back into
wishful mapping: a problem filed under the wrong technique fails here even
though its URL is perfectly valid.

Canonical title and difficulty come back from the same call, so no title in
the database is ever typed by hand.

Results are cached to `data/dsa_problem_facts.json` so the loader can run
offline and so a rerun does not hammer the endpoint.

    python -m app.content.verify_dsa_problems [--refresh]
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import httpx

from app.content.dsa_exact_problems import DSA_EXACT_PROBLEMS

GRAPHQL = "https://leetcode.com/graphql"
PROBLEM_URL = "https://leetcode.com/problems/{slug}/"
SOLUTIONS_URL = "https://leetcode.com/problems/{slug}/solutions/"
CACHE = Path(__file__).parent / "data" / "dsa_problem_facts.json"

_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionFrontendId
    title
    titleSlug
    difficulty
    isPaidOnly
    topicTags { slug }
  }
}
"""

#: The "Stuck?" link sends the learner to community solutions. That link is only
#: worth offering if solutions actually exist, so the count is fetched and
#: asserted rather than assumed -- LeetCode serves 403 to non-browser clients on
#: the HTML page, so this is the only way to check it from here.
_SOLUTIONS_QUERY = """
query solutionArticles($questionSlug: String!) {
  ugcArticleSolutionArticles(questionSlug: $questionSlug, first: 1) {
    totalNum
  }
}
"""

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
}


def fetch(slug: str, client: httpx.Client) -> dict[str, Any] | None:
    """Canonical facts for one problem, or None if LeetCode does not know it."""
    resp = client.post(
        GRAPHQL,
        json={"query": _QUERY, "variables": {"titleSlug": slug}},
        headers=_HEADERS,
        timeout=25,
    )
    resp.raise_for_status()
    question = (resp.json().get("data") or {}).get("question")
    if not question:
        return None

    solutions = client.post(
        GRAPHQL,
        json={"query": _SOLUTIONS_QUERY, "variables": {"questionSlug": slug}},
        headers=_HEADERS,
        timeout=25,
    )
    solutions.raise_for_status()
    articles = (solutions.json().get("data") or {}).get("ugcArticleSolutionArticles")
    solution_count = int(articles["totalNum"]) if articles else 0

    return {
        "slug": question["titleSlug"],
        "number": int(question["questionFrontendId"]),
        "title": question["title"],
        "difficulty": question["difficulty"],
        "paid_only": bool(question["isPaidOnly"]),
        "tags": sorted(t["slug"] for t in question["topicTags"]),
        "url": PROBLEM_URL.format(slug=question["titleSlug"]),
        "solution_count": solution_count,
        "solutions_url": SOLUTIONS_URL.format(slug=question["titleSlug"]),
    }


def load_cache() -> dict[str, Any]:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def collect(refresh: bool = False) -> tuple[dict[str, Any], list[str]]:
    """Fetch facts for every distinct slug. Returns (facts, problems)."""
    slugs = sorted({p[0] for topic in DSA_EXACT_PROBLEMS.values() for p in topic["problems"]})
    facts = {} if refresh else load_cache()
    missing = [s for s in slugs if s not in facts]
    problems: list[str] = []

    if missing:
        with httpx.Client(follow_redirects=True) as client:
            for i, slug in enumerate(missing, 1):
                try:
                    data = fetch(slug, client)
                except Exception as exc:  # noqa: BLE001
                    problems.append(f"{slug}: request failed -- {type(exc).__name__} {exc}")
                    continue
                if data is None:
                    problems.append(f"{slug}: LeetCode has no problem with this slug")
                    continue
                facts[slug] = data
                if i % 25 == 0:
                    print(f"  ... {i}/{len(missing)}")
                time.sleep(0.35)  # be a polite client
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(facts, indent=2, sort_keys=True), encoding="utf-8")

    return facts, problems


def audit(facts: dict[str, Any]) -> list[str]:
    """Every mapping rule that the fetched facts contradict."""
    failures: list[str] = []
    for topic_slug, spec in DSA_EXACT_PROBLEMS.items():
        seen: set[str] = set()
        for problem_slug, expected_tags, why in spec["problems"]:
            if problem_slug in seen:
                failures.append(f"{topic_slug}: '{problem_slug}' listed twice")
            seen.add(problem_slug)
            if not why.strip():
                failures.append(f"{topic_slug}/{problem_slug}: empty rationale")
            fact = facts.get(problem_slug)
            if fact is None:
                failures.append(f"{topic_slug}/{problem_slug}: unverified")
                continue
            if fact["paid_only"]:
                failures.append(f"{topic_slug}/{problem_slug}: Premium-only, learner cannot open it")
            if fact.get("solution_count", 0) < 1:
                failures.append(
                    f"{topic_slug}/{problem_slug}: no community solutions, "
                    "so the Stuck? link would be a dead end"
                )
            overlap = set(expected_tags) & set(fact["tags"])
            if not overlap:
                failures.append(
                    f"{topic_slug}/{problem_slug}: claimed {expected_tags} "
                    f"but LeetCode tags it {fact['tags']}"
                )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="ignore the cache and refetch")
    args = parser.parse_args()

    topics = len(DSA_EXACT_PROBLEMS)
    entries = sum(len(t["problems"]) for t in DSA_EXACT_PROBLEMS.values())
    print(f"{topics} topics, {entries} entries, "
          f"{len({p[0] for t in DSA_EXACT_PROBLEMS.values() for p in t['problems']})} distinct problems")

    facts, fetch_problems = collect(refresh=args.refresh)
    failures = fetch_problems + audit(facts)

    if failures:
        print(f"\n{len(failures)} problem(s):\n")
        for line in failures:
            print("  FAIL " + line)
        return 1

    by_difficulty: dict[str, int] = {}
    for fact in facts.values():
        by_difficulty[fact["difficulty"]] = by_difficulty.get(fact["difficulty"], 0) + 1
    print("\nAll entries verified against LeetCode.")
    print("  difficulty mix: " + ", ".join(f"{k} {v}" for k, v in sorted(by_difficulty.items())))
    print(f"  facts cached at {CACHE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
