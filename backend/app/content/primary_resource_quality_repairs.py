"""Authoritative learner-visible PRIMARY repairs for the specified resource batch."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import CurriculumLesson, CurriculumResource


TARGETS: dict[str, dict[str, Any]] = {
    "dsa-character-processing": {"title": "NeetCode — Valid Anagram", "url": "https://neetcode.io/solutions/valid-anagram", "provider": "NeetCode", "section": "Hash Map (Using Array); String", "mins": 18},
    "dsa-frequency-maps": {"title": "NeetCode — Top K Frequent Elements", "url": "https://neetcode.io/solutions/top-k-frequent-elements", "provider": "NeetCode", "section": "Hash Map; Frequency counting; Min-Heap; Bucket Sort", "mins": 25},
    "dsa-window-fixed": {"title": "NeetCode — Sliding Window Maximum", "url": "https://neetcode.io/solutions/sliding-window-maximum", "provider": "NeetCode", "section": "Fixed Window; Monotonic Queue", "mins": 25},
    "dsa-window-variable": {"title": "NeetCode — Longest Substring Without Repeating Characters", "url": "https://neetcode.io/solutions/longest-substring-without-repeating-characters", "provider": "NeetCode", "section": "Variable Window; Two Pointers", "mins": 20},
    "dsa-window-frequency": {"title": "NeetCode — Permutation in String", "url": "https://neetcode.io/solutions/permutation-in-string", "provider": "NeetCode", "section": "Frequency Window; Hash Map/Array", "mins": 20},
    "dsa-list-operations": {"title": "GeeksforGeeks — Linked List Data Structure", "url": "https://www.geeksforgeeks.org/dsa/linked-list-data-structure/", "provider": "GeeksforGeeks", "section": "Introduction; Insertion; Deletion; Traversal", "mins": 25},
    "dsa-list-reversal": {"title": "NeetCode — Reverse Linked List", "url": "https://neetcode.io/solutions/reverse-linked-list", "provider": "NeetCode", "section": "Iterative reversal; Recursive reversal; Complexity", "mins": 15},
    "dsa-fast-slow": {"title": "NeetCode — Linked List Cycle", "url": "https://neetcode.io/solutions/linked-list-cycle", "provider": "NeetCode", "section": "Floyd's Algorithm; Fast and Slow Pointers", "mins": 15},
    "dsa-cycle-detection": {"title": "NeetCode — Course Schedule", "url": "https://neetcode.io/solutions/course-schedule", "provider": "NeetCode", "section": "Cycle Detection; Topological Sort", "mins": 25},
    "dsa-list-merge": {"title": "NeetCode — Merge Two Sorted Linked Lists", "url": "https://neetcode.io/solutions/merge-two-sorted-linked-lists", "provider": "NeetCode", "section": "Two-pointer linked-list merge", "mins": 15},
    "dsa-subsets": {"title": "NeetCode — Subsets", "url": "https://neetcode.io/solutions/subsets", "provider": "NeetCode", "section": "Backtracking; Choose/Skip", "mins": 20},
    "dsa-combinations": {"title": "NeetCode — Combinations", "url": "https://neetcode.io/solutions/combinations", "provider": "NeetCode", "section": "Backtracking; Algorithm; Complexity", "mins": 20},
    "dsa-first-last-occurrence": {"title": "NeetCode — Find First and Last Position of Element in Sorted Array", "url": "https://neetcode.io/solutions/find-first-and-last-position-of-element-in-sorted-array", "provider": "NeetCode", "section": "Binary Search; Left boundary; Right boundary", "mins": 20},
    "dsa-connected-components": {"title": "NeetCode — Number of Connected Components In An Undirected Graph", "url": "https://neetcode.io/solutions/number-of-connected-components-in-an-undirected-graph", "provider": "NeetCode", "section": "DFS; BFS; Union Find; Complexity", "mins": 20},
    "dsa-unweighted-shortest": {"title": "NeetCode — Shortest Path in Binary Matrix", "url": "https://neetcode.io/solutions/shortest-path-in-binary-matrix", "provider": "NeetCode", "section": "Breadth First Search; Unweighted Shortest Path", "mins": 20},
    "dsa-dijkstra": {"title": "NeetCode — Network Delay Time", "url": "https://neetcode.io/solutions/network-delay-time", "provider": "NeetCode", "section": "Dijkstra's Algorithm; Min-Heap; Complexity", "mins": 25},
    "dsa-mst": {"title": "NeetCode — Min Cost to Connect All Points", "url": "https://neetcode.io/solutions/min-cost-to-connect-all-points", "provider": "NeetCode", "section": "Minimum Spanning Tree; Prim; Kruskal", "mins": 25},
    "dsa-interval-problems": {"title": "NeetCode — Merge Intervals", "url": "https://neetcode.io/solutions/merge-intervals", "provider": "NeetCode", "section": "Sorting; Interval merging", "mins": 20},
    "dsa-tabulation": {"title": "NeetCode — Coin Change", "url": "https://neetcode.io/solutions/coin-change", "provider": "NeetCode", "section": "Dynamic Programming; Bottom-Up Tabulation", "mins": 25},
    "dsa-pattern-selection": {"title": "NeetCode — DSA for Beginners", "url": "https://neetcode.io/courses/dsa-for-beginners/0", "provider": "NeetCode", "section": "How to identify and apply patterns; Course progression", "mins": 20},
    "cv-convolution-in-cv": {"title": "Stanford CS231n — Convolutional layers", "url": "https://cs231n.github.io/convolutional-networks/", "provider": "Stanford CS231n", "section": None, "mins": 25},
}


def apply_primary_resource_quality_repairs(db: Session, *, commit: bool = True) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    changed: list[dict[str, Any]] = []
    missing: list[str] = []
    for topic_slug, spec in TARGETS.items():
        lesson = db.query(CurriculumLesson).filter(CurriculumLesson.slug == f"{topic_slug}-lesson").first()
        if not lesson:
            lesson = db.query(CurriculumLesson).join(CurriculumLesson.topic).filter_by(slug=topic_slug).first()
        if not lesson:
            missing.append(topic_slug)
            continue
        rows = db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id).all()
        target_slug = f"{topic_slug}-learn-exact" if topic_slug != "cv-convolution-in-cv" else "cv-convolution-in-cv-primary"
        row = next((item for item in rows if item.slug == target_slug), None)
        if not row:
            row = CurriculumResource(slug=target_slug, title=spec["title"], url=spec["url"], resource_type="documentation", lesson_id=lesson.id)
            db.add(row)
            rows.append(row)
        for other in rows:
            if other is not row and other.role == "PRIMARY" and other.learner_visible:
                other.role = "SUPPLEMENT"
                other.learner_visible = False
                other.visibility_class = "INTERNAL"
        row.title = spec["title"]
        row.url = spec["url"]
        row.provider = spec["provider"]
        row.resource_type = "documentation"
        row.role = "PRIMARY"
        row.learner_visible = True
        row.visibility_class = "LEARNER"
        row.section = spec["section"]
        row.estimated_minutes = spec["mins"]
        row.estimate_confidence = "MEDIUM"
        row.estimate_method = "RESEARCHED_SECTION_ESTIMATE" if spec["section"] else "FULL_SINGLE_PAGE_ESTIMATE"
        row.boundary_type = "ARTICLE_SECTION" if spec["section"] else "FULL_SINGLE_PAGE"
        row.start_boundary = spec["section"]
        row.end_boundary = spec["section"]
        row.exactness = "EXACT"
        row.verification_status = "NEEDS_REVIEW"
        row.notes = "Authoritative mapping supplied for this repair batch."
        row.verification_evidence = json.dumps({"repair": "primary_resource_quality", "repaired_at": now})
        changed.append({"topic_slug": topic_slug, "resource_slug": row.slug, "lesson_id": lesson.id})
    if missing:
        db.rollback()
        raise ValueError("Missing required topic lessons: " + ", ".join(missing))
    if commit:
        db.commit()
    return {"updated": len(changed), "missing": missing, "changed": changed}