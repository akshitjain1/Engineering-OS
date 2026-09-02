"""Flag problems that need a technique the curriculum has not taught yet.

The tag check in verify_dsa_problems proves a problem *uses* the technique it is
filed under. It cannot prove the learner can reach it: "correctly classified"
and "solvable from today's reading" are different claims, and only the first one
is machine-checkable.

This closes as much of that gap as can honestly be closed. Every LeetCode tag
that corresponds to a module in the DSA track is mapped to that module's
position. A problem carrying a tag from a *later* module is reported, ranked by
how far ahead it sits, because a large gap is far more likely to be a real
sequencing error than a small one.

It is a review tool, not a gate. Plenty of flags are false positives by design:
Two Sum is tagged `hash-table` but its brute-force solution needs nothing, so it
is perfectly reachable in module 0. Judgment decides; confirmed decisions get
written down as tests. Read the report, not the exit code.

    python -m app.content.audit_dsa_reachability
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select

from app.content.dsa_exact_problems import DSA_EXACT_PROBLEMS
from app.content.verify_dsa_problems import CACHE
from app.db.models import CurriculumModule, CurriculumTopic
from app.db.session import SessionLocal

#: Snapshot of the track's shape -- module order and which module each topic
#: sits in. Held as a file for the same reason the problem facts are: it is
#: curriculum design, not runtime state, and tests run against an empty
#: database where a live query would silently return nothing. Refresh it with
#: `--refresh` after changing the module order.
SHAPE = Path(__file__).parent / "data" / "dsa_curriculum_shape.json"

#: LeetCode tag -> the DSA module that teaches it, by module name. Only tags the
#: curriculum actually teaches appear here; the rest (math, simulation, design,
#: geometry...) gate nothing and are deliberately absent.
TAG_MODULE = {
    "array": "Arrays",
    "matrix": "Arrays",
    "prefix-sum": "Arrays",
    "string": "Strings",
    "string-matching": "Strings",
    "hash-table": "Hashing",
    "hash-function": "Hashing",
    "counting": "Hashing",
    "two-pointers": "Two Pointers",
    "sliding-window": "Sliding Window",
    "linked-list": "Linked Lists",
    "doubly-linked-list": "Linked Lists",
    "stack": "Stack",
    "monotonic-stack": "Stack",
    "queue": "Queue",
    "monotonic-queue": "Queue",
    # The Queue module contains dsa-queue-bfs-relationship, so BFS is introduced
    # here. Filing it under Trees made every queue-BFS problem read as 5 modules
    # early when it is exactly on time.
    "breadth-first-search": "Queue",
    "recursion": "Recursion",
    "memoization": "Recursion",
    "backtracking": "Backtracking",
    "sorting": "Sorting",
    "merge-sort": "Sorting",
    "quickselect": "Sorting",
    "bucket-sort": "Sorting",
    "radix-sort": "Sorting",
    "counting-sort": "Sorting",
    "divide-and-conquer": "Sorting",
    "binary-search": "Binary Search",
    "tree": "Trees",
    "binary-tree": "Trees",
    "depth-first-search": "Trees",
    "binary-search-tree": "Binary Search Trees",
    "heap-priority-queue": "Heaps & Priority Queues",
    "graph": "Graphs",
    "topological-sort": "Topological Sorting",
    "union-find": "Union-Find",
    "shortest-path": "Shortest Paths",
    "minimum-spanning-tree": "Minimum Spanning Trees",
    "greedy": "Greedy Algorithms",
    "line-sweep": "Greedy Algorithms",
    "dynamic-programming": "Dynamic Programming",
    "trie": "Advanced Problem-Solving Patterns",
    "bit-manipulation": "Advanced Problem-Solving Patterns",
    "bitmask": "Advanced Problem-Solving Patterns",
    "segment-tree": "Advanced Problem-Solving Patterns",
    "binary-indexed-tree": "Advanced Problem-Solving Patterns",
    "eulerian-circuit": "Advanced Problem-Solving Patterns",
    "rolling-hash": "Advanced Problem-Solving Patterns",
    "suffix-array": "Advanced Problem-Solving Patterns",
}


def module_positions() -> dict[str, int]:
    """Module name -> order_index, for the modules holding DSA topics."""
    db = SessionLocal()
    try:
        rows = db.execute(
            select(CurriculumModule.name, CurriculumModule.order_index)
            .join(CurriculumTopic, CurriculumTopic.module_id == CurriculumModule.id)
            .where(CurriculumTopic.domain_key == "dsa")
            .distinct()
        ).all()
        return {name: index for name, index in rows}
    finally:
        db.close()


def topic_modules() -> dict[str, str]:
    """Topic slug -> the name of the module it sits in."""
    db = SessionLocal()
    try:
        rows = db.execute(
            select(CurriculumTopic.slug, CurriculumModule.name)
            .join(CurriculumModule, CurriculumModule.id == CurriculumTopic.module_id)
            .where(CurriculumTopic.domain_key == "dsa")
        ).all()
        return {slug: name for slug, name in rows}
    finally:
        db.close()


def write_shape() -> dict:
    """Snapshot module order and topic placement from the live curriculum."""
    shape = {"modules": module_positions(), "topics": topic_modules()}
    SHAPE.parent.mkdir(parents=True, exist_ok=True)
    SHAPE.write_text(json.dumps(shape, indent=2, sort_keys=True), encoding="utf-8")
    return shape


def load_shape() -> dict:
    if not SHAPE.exists():
        return write_shape()
    return json.loads(SHAPE.read_text(encoding="utf-8"))


def find_flags() -> list[dict]:
    """Every (topic, problem, tag) where the tag is taught after the topic."""
    facts = json.loads(CACHE.read_text(encoding="utf-8"))
    shape = load_shape()
    positions = shape["modules"]
    modules = shape["topics"]
    flags: list[dict] = []

    for topic_slug, spec in DSA_EXACT_PROBLEMS.items():
        module_name = modules.get(topic_slug)
        if module_name is None:
            continue
        here = positions[module_name]
        for problem_slug, _expected, why in spec["problems"]:
            fact = facts.get(problem_slug)
            if fact is None:
                continue
            ahead = []
            for tag in fact["tags"]:
                owner = TAG_MODULE.get(tag)
                if owner is None or owner not in positions:
                    continue
                gap = positions[owner] - here
                if gap > 0:
                    ahead.append((gap, tag, owner))
            if ahead:
                worst = max(ahead)
                flags.append(
                    {
                        "gap": worst[0],
                        "topic": topic_slug,
                        "module": module_name,
                        "problem": fact["title"],
                        "difficulty": fact["difficulty"],
                        "needs": sorted({f"{t} ({o})" for _g, t, o in ahead}),
                        "why": why,
                    }
                )
    flags.sort(key=lambda f: (-f["gap"], f["topic"]))
    return flags


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true",
                        help="re-snapshot module order from the database first")
    if parser.parse_args().refresh:
        shape = write_shape()
        print(f"shape refreshed: {len(shape['modules'])} modules, "
              f"{len(shape['topics'])} topics")

    flags = find_flags()
    total = sum(len(t["problems"]) for t in DSA_EXACT_PROBLEMS.values())
    print(f"{len(flags)} of {total} entries carry a tag taught later in the track.\n")
    print("Ranked by how far ahead. A large gap is much more likely to be a real")
    print("sequencing error; a gap of 1-2 is usually a tag the problem does not")
    print("actually require. Judgement, not a gate.\n")
    for f in flags:
        print(f"  +{f['gap']:<3} {f['topic']:<32} {f['difficulty']:<7} {f['problem']}")
        print(f"        module: {f['module']}")
        print(f"        needs:  {', '.join(f['needs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
