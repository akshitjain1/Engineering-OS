"""Apply the authoritative Batch 4 DP resource mappings only."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic


TARGETS: dict[str, dict[str, Any]] = {
    "dsa-dp-state": {"title": "Steps to solve a Dynamic Programming Problem", "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/dsa/solve-dynamic-programming-problem/", "rtype": "documentation", "boundary": "ARTICLE_SECTION", "start": "Step 2: Decide a state expression with the Least parameters.", "end": "Step 3: Formulate state and transition relationship.", "instruction": "Learn how to define a DP state using the smallest set of parameters that uniquely describes a subproblem. Do the knapsack example mentally and explain what dp[index][capacity] means."},
    "dsa-dp-transition": {"title": "Steps to solve a Dynamic Programming Problem", "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/dsa/solve-dynamic-programming-problem/", "rtype": "documentation", "boundary": "ARTICLE_SECTION", "start": "Step 3: Formulate state and transition relationship.", "end": "Step 4: Add memoization or tabulation.", "instruction": "Learn how a DP transition converts smaller solved states into the current state. Be able to write a recurrence from the meaning of the state before thinking about code."},
    "dsa-advanced-dp": {"title": "CP-Algorithms — Knuth's Optimization", "provider": "CP-Algorithms", "url": "https://cp-algorithms.com/dynamic_programming/knuth-optimization.html", "rtype": "documentation", "boundary": "FULL_SINGLE_PAGE", "start": "FULL_SINGLE_PAGE", "end": "FULL_SINGLE_PAGE", "instruction": "Treat this as an introduction to what advanced DP means: exploiting additional mathematical structure in a transition to reduce complexity. Understand range DP, optimal split points, the monotonicity condition, and why the optimization can reduce O(n^3) range DP to O(n^2)."},
    "dsa-dp-2d": {"title": "Dynamic Programming (DP) on Grids", "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/dsa/dp-on-grids/", "rtype": "documentation", "boundary": "ARTICLE_SECTION", "start": "Idea behind Dynamic Programming (DP) on Grids", "end": "Iteratively filling the DP table", "instruction": "Learn why grid coordinates become DP states, how transitions come from neighbouring cells, how base cases are chosen, and how the 2D table is filled."},
    "dsa-subsequence-dp": {"title": "Longest Increasing Subsequence (LIS)", "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/dsa/longest-increasing-subsequence-dp-3/", "rtype": "documentation", "boundary": "ARTICLE_SECTION", "start": "Naive Approach", "end": "Using Dynamic Programming", "instruction": "Learn the canonical subsequence-DP pattern using LIS: define what dp[i] means, compare previous elements, derive the recurrence, and understand why the state depends on earlier subsequences."},
    "dsa-grid-dp": {"title": "Dynamic Programming (DP) on Grids", "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/dsa/dp-on-grids/", "rtype": "documentation", "boundary": "ARTICLE_SECTION", "start": "Idea behind Dynamic Programming (DP) on Grids", "end": "Use Cases of Dynamic Programming (DP) on Grids", "instruction": "Learn the standard grid-DP pattern: cell as state, valid movement as transition, boundary/base conditions, and iterative computation."},
    "dsa-interval-dp": {"title": "Matrix Chain Multiplication", "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/dsa/matrix-chain-multiplication-dp-8/", "rtype": "documentation", "boundary": "ARTICLE_SECTION", "start": "Better Approach 1] Using Top-Down DP (Memoization)", "end": "Better Approach 2] Using Bottom-Up DP (Tabulation)", "instruction": "Learn interval/range DP through Matrix Chain Multiplication. Focus on dp[i][j] representing an interval, trying every split k, combining the two subintervals, and filling states in increasing interval length."},
    "dsa-dp-optimization": {"title": "Count Unique Paths in a Grid", "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/dsa/count-possible-paths-top-left-bottom-right-nxm-matrix/", "rtype": "documentation", "boundary": "ARTICLE_SECTION", "start": "Better Approach: Using DP", "end": "Expected Approach: Using Combinatorics", "instruction": "Focus on the space optimization idea: recognize when the current state depends only on the previous row/current left state, replace a full 2D table with a 1D array, and reason about the correct update order."},
}


def _resolve(db: Session, slug: str) -> tuple[CurriculumTopic, CurriculumLesson, list[CurriculumResource]]:
    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
    if not topic:
        raise ValueError(f"Missing topic: {slug}")
    lesson = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).first()
    if not lesson:
        raise ValueError(f"Missing lesson for topic: {slug}")
    return topic, lesson, db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id).all()


def apply_batch4_dp_mapping(db: Session, *, commit: bool = True) -> dict[str, Any]:
    repaired_at = datetime.now(timezone.utc).isoformat()
    changed = []
    unresolved = [{"topic": "dsa-dp-mindset", "reason": "NEEDS_BOUNDARY_VERIFICATION", "detail": "Full duration for video 5dRGRueKU3M is not present in existing repository data."}]
    for slug, spec in TARGETS.items():
        topic, lesson, rows = _resolve(db, slug)
        primaries = [row for row in rows if row.role == "PRIMARY" and row.learner_visible]
        target = next((row for row in rows if row.slug == f"{slug}-learn-exact"), None)
        if not target or not primaries:
            raise ValueError(f"Missing target/current PRIMARY for {slug}")
        old = {"slug": primaries[0].slug, "title": primaries[0].title, "url": primaries[0].url, "boundary": primaries[0].section}
        for row in primaries:
            if row is not target:
                row.role = "REFERENCE"
                row.learner_visible = False
                row.visibility_class = "INTERNAL"
        target.title = spec["title"]
        target.url = spec["url"]
        target.provider = spec["provider"]
        target.resource_type = spec["rtype"]
        target.role = "PRIMARY"
        target.learner_visible = True
        target.visibility_class = "LEARNER"
        target.section = spec["start"] if spec["start"] == spec["end"] else f"{spec['start']} through {spec['end']}"
        target.boundary_type = spec["boundary"]
        target.start_boundary = spec["start"]
        target.end_boundary = spec["end"]
        target.exactness = "EXACT"
        target.verification_status = "NEEDS_REVIEW"
        target.description = spec["instruction"]
        target.notes = "Authoritative Batch 4 DP mapping supplied by user."
        target.verification_evidence = json.dumps({"repair": "batch4_dp_resource_mapping", "repaired_at": repaired_at})
        changed.append({"topic": topic.slug, "lesson_id": lesson.id, "old_primary": old, "new_primary": {"slug": target.slug, "title": target.title, "provider": target.provider, "url": target.url, "boundary": target.section, "instruction": target.description}})
    if commit:
        db.commit()
    return {"processed": len(changed), "changed": changed, "unresolved": unresolved}