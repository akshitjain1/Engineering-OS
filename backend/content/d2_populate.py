"""Apply verified Domain 2 content without touching prereqs/next_topic."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _d2_helpers import bari_primary  # noqa: E402
from _d2_part1 import CONTENT as P1  # noqa: E402
from _d2_part2 import CONTENT as P2  # noqa: E402
from _d2_part3 import CONTENT as P3  # noqa: E402
from _d2_part4 import CONTENT as P4  # noqa: E402

CONTENT = {**P1, **P2, **P3, **P4}
YAML_PATH = HERE / "curriculum" / "dsa" / "02-data-structures-algorithms.yaml"

PRIMARY_HINTS = {
    "dsa-string-manipulation": "treat strings as sequences (analysis/arrays lectures; exact string video unresolved)",
    "dsa-string-frequency": "counting / frequency (exact string video unresolved)",
    "dsa-character-processing": "arrays as sequences of codes (exact video unresolved)",
    "dsa-string-patterns": "pattern problems as array+hash reasoning (exact video unresolved)",
    "dsa-hash-map": "hashing / hash tables",
    "dsa-hash-set": "hashing / hash tables / uniqueness",
    "dsa-frequency-maps": "hashing / counting",
    "dsa-lookup-patterns": "hashing / lookup",
    "dsa-two-pointers-opposite": "two-pointer / array scanning",
    "dsa-two-pointers-same": "two-pointer / in-place array scans",
    "dsa-two-pointers-partition": "partition / quicksort intuition",
    "dsa-window-fixed": "sliding window / two pointers",
    "dsa-window-variable": "sliding window / two pointers",
    "dsa-window-frequency": "sliding window + hashing",
    "dsa-singly-linked-list": "linked lists / nodes",
    "dsa-list-operations": "linked list insert/delete",
    "dsa-list-reversal": "linked list reverse",
    "dsa-fast-slow": "linked list two pointers",
    "dsa-cycle-detection": "linked list cycle / Floyd",
    "dsa-list-merge": "linked list merge",
}


def iter_topics(data: dict):
    for level in data["track"]["levels"]:
        for subject in level["subjects"]:
            for module in subject["modules"]:
                for topic in module["topics"]:
                    yield topic


def normalize_resources(slug: str, resources: list) -> list:
    cleaned = []
    for res in resources:
        if res["role"] == "PRACTICE" and "leetcode.com" in (res.get("url") or ""):
            continue
        cleaned.append(res)
    if not any(res["role"] == "PRIMARY" for res in cleaned):
        hint = PRIMARY_HINTS.get(slug, slug.replace("dsa-", "").replace("-", " "))
        cleaned = [bari_primary(slug, hint)] + cleaned
    for i, res in enumerate(cleaned):
        res["order"] = i
    return cleaned


def uniquify_resource_slugs(data: dict) -> None:
    seen: set[str] = set()
    for topic in iter_topics(data):
        for res in topic["lessons"][0]["resources"]:
            base = res["slug"]
            slug = base
            n = 2
            while slug in seen:
                slug = f"{base}-{n}"
                n += 1
            res["slug"] = slug
            seen.add(slug)


def apply() -> None:
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    found = []
    for topic in iter_topics(data):
        slug = topic["slug"]
        found.append(slug)
        if slug not in CONTENT:
            raise SystemExit(f"missing content for {slug}")
        unit = CONTENT[slug]
        prereqs = list(topic.get("prerequisites") or [])
        nxt = topic.get("next_topic")
        topic["description"] = unit["explanation"]
        if unit.get("learning_objective"):
            topic["learning_objective"] = unit["learning_objective"]
        topic["mastery_criteria"] = list(unit["mastery_criteria"])
        topic["prerequisites"] = prereqs
        topic["next_topic"] = nxt
        lesson = topic["lessons"][0]
        lesson["description"] = unit["explanation"]
        lesson["hours_estimated"] = float(unit["hours_estimated"])
        lesson["resources"] = normalize_resources(slug, list(unit["resources"]))
        lesson["questions"] = unit["questions"]
        lesson["exercises"] = unit["exercises"]

    missing = set(CONTENT) - set(found)
    extra = set(found) - set(CONTENT)
    if missing or extra:
        raise SystemExit(f"slug mismatch missing={sorted(missing)} extra={sorted(extra)}")
    uniquify_resource_slugs(data)
    YAML_PATH.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )
    n_q = n_ex = n_p = n_r = n_pr = n_d = n_unmapped = 0
    unmapped = []
    for topic in iter_topics(data):
        lesson = topic["lessons"][0]
        n_q += len(lesson["questions"])
        n_ex += len(lesson["exercises"])
        for res in lesson["resources"]:
            if res["role"] == "PRIMARY":
                n_p += 1
            elif res["role"] == "REFERENCE":
                n_r += 1
            elif res["role"] == "PRACTICE":
                n_pr += 1
            elif res["role"] == "DEEP_DIVE":
                n_d += 1
        if not any(res["role"] == "PRIMARY" and res.get("url") for res in lesson["resources"]):
            n_unmapped += 1
            unmapped.append(topic["slug"])
    print(
        f"topics={len(found)} questions={n_q} exercises={n_ex} "
        f"PRIMARY={n_p} REFERENCE={n_r} PRACTICE={n_pr} DEEP_DIVE={n_d} "
        f"no_primary_url={n_unmapped}"
    )
    print("no_primary_url:", ", ".join(unmapped) if unmapped else "(none)")


if __name__ == "__main__":
    apply()
