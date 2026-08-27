"""Apply the authoritative Batch 2A/2B tree and sorting resource mappings."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic


TARGETS: dict[str, dict[str, Any]] = {
    "dsa-tree-terminology": {"title": "GFG — Introduction to Binary Tree", "url": "https://www.geeksforgeeks.org/dsa/introduction-to-binary-tree/", "section": "Root; Node; Edge; Leaf; Internal node; Subtree; Path; Depth/level; Height"},
    "dsa-binary-trees": {"title": "GFG — Introduction to Binary Tree", "url": "https://www.geeksforgeeks.org/dsa/introduction-to-binary-tree/", "section": "Introduction; Structural definition of a binary tree"},
    "dsa-bst-search": {"title": "GFG — Searching in Binary Search Tree (BST)", "url": "https://www.geeksforgeeks.org/dsa/binary-search-tree-set-1-search-and-insertion/", "section": "Search explanation; Search procedure"},
    "dsa-bst-insert": {"title": "GFG — Insertion in Binary Search Tree (BST)", "url": "https://www.geeksforgeeks.org/dsa/insertion-in-binary-search-tree/", "section": "Recursive insertion; Iterative insertion"},
    "dsa-bst-delete": {"title": "GFG — Binary Search Tree", "url": "https://www.geeksforgeeks.org/dsa/binary-search-tree-data-structure/", "section": "Deletion: leaf; one child; two children"},
    "dsa-recursive-trees": {"title": "GFG — DFS Traversal of a Tree", "url": "https://www.geeksforgeeks.org/dsa/dfs-traversal-of-a-tree-using-recursion/", "section": "Recursive DFS/tree traversal"},
    "dsa-tree-dfs": {"title": "GFG — Tree Traversal Techniques", "url": "https://www.geeksforgeeks.org/dsa/tree-traversals-inorder-preorder-and-postorder/", "section": "Inorder; Preorder; Postorder; Traversal logic"},
    "dsa-tree-bfs": {"title": "GFG — Level Order Traversal (Breadth First Search) of Binary Tree", "url": "https://www.geeksforgeeks.org/dsa/level-order-tree-traversal/", "section": "Queue-based level-order traversal"},
    "dsa-bst-validate": {"title": "GFG — Check if a Binary Tree is BST or not", "url": "https://www.geeksforgeeks.org/dsa/a-program-to-check-if-a-binary-tree-is-bst-or-not/", "section": "BST validity definition; Range validation; Inorder validation"},
    "dsa-tree-height": {"title": "GFG — Maximum Depth or Height of a Binary Tree", "url": "https://www.geeksforgeeks.org/dsa/find-the-maximum-depth-or-height-of-a-tree/", "section": "Recursive definition; Recurrence"},
    "dsa-bst-ordered-properties": {"title": "GFG — Introduction to Binary Search Tree", "url": "https://www.geeksforgeeks.org/dsa/introduction-to-binary-search-tree/", "section": "Ordering invariant; Balanced-vs-skewed complexity"},
    "dsa-tree-paths": {"title": "GFG — Print Root-to-Leaf Paths in a Binary Tree", "url": "https://www.geeksforgeeks.org/dsa/given-a-binary-tree-print-all-root-to-leaf-paths/", "section": "Recursion; Backtracking"},
    "dsa-tree-construction": {"title": "GFG — Construct a Binary Tree from Postorder and Inorder", "url": "https://www.geeksforgeeks.org/dsa/construct-a-binary-tree-from-postorder-and-inorder/", "section": "Construction explanation; Recursive decomposition"},
    "dsa-segment-tree-concept": {"title": "GFG — Introduction to Segment Trees", "url": "https://www.geeksforgeeks.org/dsa/introduction-to-segment-trees-2/", "section": "Definition; Range-query intuition; Tree structure; Construction; Merge operation"},
    "dsa-bubble-sort": {"title": "GFG — Bubble Sort Algorithm", "url": "https://www.geeksforgeeks.org/dsa/bubble-sort-algorithm/", "section": "Full algorithm article"},
    "dsa-selection-sort": {"title": "GFG — Selection Sort Algorithm", "url": "https://www.geeksforgeeks.org/dsa/selection-sort-algorithm-2/", "section": "Full algorithm article"},
    "dsa-insertion-sort": {"title": "GFG — Insertion Sort Algorithm", "url": "https://www.geeksforgeeks.org/dsa/insertion-sort-algorithm/", "section": "Full algorithm article"},
    "dsa-merge-sort": {"title": "GFG — Merge Sort", "url": "https://www.geeksforgeeks.org/dsa/merge-sort/", "section": "Full algorithm article"},
    "dsa-quick-sort": {"title": "GFG — Quick Sort Algorithm", "url": "https://www.geeksforgeeks.org/dsa/quick-sort-algorithm/", "section": "Full algorithm article"},
    "dsa-heap-sort": {"title": "GFG — Heap Sort", "url": "https://www.geeksforgeeks.org/dsa/heap-sort/", "section": "Full algorithm article"},
    "dsa-topological-sort": {"title": "GFG — Topological Sorting", "url": "https://www.geeksforgeeks.org/dsa/topological-sorting-indegree-based-solution/", "section": "Full algorithm article"},
    "dsa-sort-stability": {"title": "GFG — Analysis of Different Sorting Techniques", "url": "https://www.geeksforgeeks.org/dsa/analysis-of-different-sorting-techniques/", "section": "Stability section/table"},
    "dsa-sort-complexity": {"title": "GFG — Introduction to Sorting Algorithm", "url": "https://www.geeksforgeeks.org/dsa/introduction-to-sorting-algorithm/", "section": "Complexity comparison section/table"},
}


def _topic_lesson(db: Session, slug: str) -> tuple[CurriculumTopic, CurriculumLesson]:
    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
    if not topic:
        raise ValueError(f"Missing topic: {slug}")
    lesson = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).first()
    if not lesson:
        raise ValueError(f"Missing lesson for topic: {slug}")
    return topic, lesson


def apply_dsa_tree_sort_repairs(db: Session, *, commit: bool = True) -> dict[str, Any]:
    repaired_at = datetime.now(timezone.utc).isoformat()
    changed: list[dict[str, Any]] = []
    for topic_slug, spec in TARGETS.items():
        topic, lesson = _topic_lesson(db, topic_slug)
        rows = db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id).all()
        primaries = [row for row in rows if row.role == "PRIMARY" and row.learner_visible]
        row = next((item for item in rows if item.slug == f"{topic_slug}-learn-exact"), None)
        if not row:
            raise ValueError(f"Missing target resource: {topic_slug}-learn-exact")
        if not primaries:
            raise ValueError(f"Missing current PRIMARY: {topic_slug}")
        old = {"slug": primaries[0].slug, "title": primaries[0].title, "url": primaries[0].url, "section": primaries[0].section}
        for other in primaries:
            if other is not row:
                other.role = "REFERENCE"
                other.learner_visible = False
                other.visibility_class = "INTERNAL"
        row.title = spec["title"]
        row.url = spec["url"]
        row.provider = "GeeksforGeeks"
        row.resource_type = "documentation"
        row.role = "PRIMARY"
        row.learner_visible = True
        row.visibility_class = "LEARNER"
        row.section = spec["section"]
        row.boundary_type = "FULL_SINGLE_PAGE" if spec["section"] == "Full algorithm article" else "ARTICLE_SECTION"
        row.start_boundary = spec["section"]
        row.end_boundary = spec["section"]
        row.exactness = "EXACT"
        row.verification_status = "NEEDS_REVIEW"
        row.notes = "Authoritative Batch 2A/2B mapping supplied by user."
        row.verification_evidence = json.dumps({"repair": "dsa_tree_sort_resource_repairs", "repaired_at": repaired_at})
        changed.append({"topic_slug": topic.slug, "resource_slug": row.slug, "old_primary": old, "new_primary": {"title": row.title, "url": row.url, "boundary": row.section}})
    if commit:
        db.commit()
    return {"updated": len(changed), "changed": changed}