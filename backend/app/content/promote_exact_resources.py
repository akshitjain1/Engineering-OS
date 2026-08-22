"""Promote exact documentation to PRIMARY; demote collection hubs/playlists.

Does not change topic graph (slugs/prereqs/next_topic). Only resource role/url/section.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.content.verification import (
    EXACTNESS_COLLECTION,
    EXACTNESS_EXACT,
    EXACTNESS_MULTI_TOPIC,
    VERIFICATION_COLLECTION_ONLY,
    VERIFICATION_NEEDS_REVIEW,
)
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic

EXACT_HOST_HINTS = (
    "dev.java/learn/",
    "docs.oracle.com",
    "developer.mozilla.org",
    "docs.python.org",
    "git-scm.com/book",
    "git-scm.com/docs",
    "www.geeksforgeeks.org/",
    "cp-algorithms.com",
    "pytorch.org/tutorials",
    "scikit-learn.org",
    "postgresql.org/docs",
    "docs.docker.com",
    "kubernetes.io/docs",
    "missing.csail.mit.edu",
    "web.mit.edu",
    "ocw.mit.edu",
)

COLLECTION_HINTS = (
    "playlist?list=",
    "/tag/",
    "/tags/",
    "neetcode.io/practice",
    "youtube.com/playlist",
)


DSA_EXACT_LEARN: dict[str, tuple[str, str]] = {
    # slug -> (url, section/title hint)
    "dsa-array-traversal": ("https://www.geeksforgeeks.org/array-data-structure-guide/", "Array traversal"),
    "dsa-array-insert-delete": ("https://www.geeksforgeeks.org/insertion-and-deletion-in-arrays/", "Insert/Delete"),
    "dsa-prefix-sums": ("https://www.geeksforgeeks.org/prefix-sum-array-implementation-applications-competitive-programming/", "Prefix sum"),
    "dsa-array-frequency": ("https://www.geeksforgeeks.org/counting-frequencies-of-array-elements/", "Frequency counting"),
    "dsa-array-patterns": ("https://www.geeksforgeeks.org/two-pointers-technique/", "Array patterns / two pointers"),
    "dsa-string-manipulation": ("https://www.geeksforgeeks.org/string-data-structure/", "String basics"),
    "dsa-singly-linked-list": ("https://www.geeksforgeeks.org/singly-linked-list/", "Singly linked list"),
    "dsa-stack-fundamentals": ("https://www.geeksforgeeks.org/stack-data-structure/", "Stack"),
    "dsa-queue-deque": ("https://www.geeksforgeeks.org/queue-data-structure/", "Queue"),
    "dsa-hash-map": ("https://www.geeksforgeeks.org/hashing-data-structure/", "Hashing"),
    "dsa-binary-search-classic": ("https://www.geeksforgeeks.org/binary-search/", "Binary search"),
    "dsa-binary-search-boundaries": ("https://www.geeksforgeeks.org/lower-and-upper-bound/", "Lower/upper bound"),
    "dsa-recursion-model": ("https://www.geeksforgeeks.org/introduction-to-recursion-data-structure-and-algorithm-tutorials/", "Recursion"),
    "dsa-binary-trees": ("https://www.geeksforgeeks.org/binary-tree-data-structure/", "Binary tree"),
    "dsa-bst": ("https://www.geeksforgeeks.org/binary-search-tree-data-structure/", "BST"),
    "dsa-heapify": ("https://www.geeksforgeeks.org/heap-sort/", "Heapify / heap"),
    "dsa-graph-bfs": ("https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/", "BFS"),
    "dsa-graph-dfs": ("https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/", "DFS"),
    "dsa-dp-1d": ("https://www.geeksforgeeks.org/introduction-to-dynamic-programming-data-structures-and-algorithm-tutorials/", "1D DP intro"),
    "dsa-dp-2d": ("https://www.geeksforgeeks.org/dynamic-programming/", "DP overview"),
    "dsa-big-o": ("https://www.geeksforgeeks.org/analysis-of-algorithms-big-o-analysis/", "Big-O"),
    "dsa-best-worst-average": ("https://www.geeksforgeeks.org/analysis-of-algorithms-set-2-asymptotic-analysis/", "Best/worst/average"),
    "dsa-algorithmic-thinking": ("https://www.geeksforgeeks.org/what-is-an-algorithm-definition-types-complexity-examples/", "Algorithm definition"),
}


def _is_collection_url(url: str) -> bool:
    u = (url or "").lower()
    return any(h in u for h in COLLECTION_HINTS)


def _is_exactish_url(url: str) -> bool:
    u = (url or "").lower()
    if _is_collection_url(u):
        return False
    return any(h in u for h in EXACT_HOST_HINTS)


def _lesson(db: Session, topic: CurriculumTopic) -> Optional[CurriculumLesson]:
    lessons = (
        db.query(CurriculumLesson)
        .filter(CurriculumLesson.topic_id == topic.id)
        .order_by(CurriculumLesson.order_index)
        .all()
    )
    return lessons[0] if lessons else None


def _dsa_learn_url(slug: str, name: str) -> tuple[str, str]:
    if slug in DSA_EXACT_LEARN:
        return DSA_EXACT_LEARN[slug]
    s = f"{slug} {name}".lower()
    # Heuristic exact GFG learn pages for remaining DSA spine topics
    mapping = [
        (("two-pointer", "two pointer"), "https://www.geeksforgeeks.org/two-pointers-technique/", "Two pointers"),
        (("sliding",), "https://www.geeksforgeeks.org/window-sliding-technique/", "Sliding window"),
        (("sorting", "sort"), "https://www.geeksforgeeks.org/sorting-algorithms/", "Sorting"),
        (("merge-sort",), "https://www.geeksforgeeks.org/merge-sort/", "Merge sort"),
        (("quick-sort",), "https://www.geeksforgeeks.org/quick-sort/", "Quick sort"),
        (("heap", "priority"), "https://www.geeksforgeeks.org/heap-data-structure/", "Heap"),
        (("trie",), "https://www.geeksforgeeks.org/trie-insert-and-search/", "Trie"),
        (("backtrack",), "https://www.geeksforgeeks.org/backtracking-algorithms/", "Backtracking"),
        (("greedy",), "https://www.geeksforgeeks.org/greedy-algorithms/", "Greedy"),
        (("graph",), "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/", "Graphs"),
        (("tree", "bst"), "https://www.geeksforgeeks.org/binary-tree-data-structure/", "Trees"),
        (("linked",), "https://www.geeksforgeeks.org/data-structures/linked-list/", "Linked list"),
        (("stack",), "https://www.geeksforgeeks.org/stack-data-structure/", "Stack"),
        (("queue",), "https://www.geeksforgeeks.org/queue-data-structure/", "Queue"),
        (("hash",), "https://www.geeksforgeeks.org/hashing-data-structure/", "Hashing"),
        (("string",), "https://www.geeksforgeeks.org/string-data-structure/", "Strings"),
        (("array",), "https://www.geeksforgeeks.org/array-data-structure-guide/", "Arrays"),
        (("bit",), "https://www.geeksforgeeks.org/bits-manipulation-important-tactics/", "Bit manipulation"),
        (("recursion",), "https://www.geeksforgeeks.org/introduction-to-recursion-data-structure-and-algorithm-tutorials/", "Recursion"),
        (("dp", "dynamic"), "https://www.geeksforgeeks.org/dynamic-programming/", "DP"),
        (("binary-search", "search"), "https://www.geeksforgeeks.org/binary-search/", "Binary search"),
    ]
    for keys, url, section in mapping:
        if any(k in s for k in keys):
            return url, section
    return ("https://www.geeksforgeeks.org/data-structures/", "Data structures overview")


def promote_exact_resources(db: Session) -> dict[str, int]:
    promoted = 0
    demoted = 0
    dsa_injected = 0
    topics = (
        db.query(CurriculumTopic)
        .options(selectinload(CurriculumTopic.lessons).selectinload(CurriculumLesson.resources))
        .all()
    )
    now = datetime.now(timezone.utc).isoformat()

    for topic in topics:
        lesson = _lesson(db, topic)
        if not lesson:
            continue
        resources = list(lesson.resources or [])
        primaries = [r for r in resources if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")]
        refs = [
            r
            for r in resources
            if (r.role or "").upper() in ("REFERENCE", "SUPPLEMENT", "DEEP_DIVE")
            and _is_exactish_url(r.url or "")
        ]

        # DSA: inject exact GFG learn page as PRIMARY for all DSA topics
        if (topic.domain_key == "dsa") or (topic.slug or "").startswith("dsa-"):
            url, section = _dsa_learn_url(topic.slug or "", topic.name or "")
            learn_slug = f"{topic.slug}-learn-exact"
            row = db.query(CurriculumResource).filter(CurriculumResource.slug == learn_slug).first()
            if not row:
                row = CurriculumResource(
                    slug=learn_slug,
                    title=f"Learn: {topic.name}",
                    url=url,
                    resource_type="documentation",
                    provider="GeeksforGeeks",
                    lesson_id=lesson.id,
                    role="PRIMARY",
                    order_index=-1,
                    official_unofficial="unofficial",
                    verification_status=VERIFICATION_NEEDS_REVIEW,
                )
                db.add(row)
                dsa_injected += 1
            else:
                row.url = url
                row.role = "PRIMARY"
                row.order_index = -1
            row.section = section
            row.exactness = EXACTNESS_EXACT
            row.last_verified_at = now
            for p in primaries:
                if p.slug == learn_slug:
                    continue
                if _is_collection_url(p.url or "") or (p.exactness or "") == EXACTNESS_COLLECTION or "youtube.com" in (p.url or ""):
                    p.role = "SUPPLEMENT"
                    p.exactness = EXACTNESS_COLLECTION
                    p.verification_status = VERIFICATION_COLLECTION_ONLY
                    demoted += 1
            continue

        # Java / general: if primary is collection and a reference is exactish, swap
        for p in primaries:
            collectionish = _is_collection_url(p.url or "") or (p.exactness or "") == EXACTNESS_COLLECTION or (
                p.verification_status or ""
            ) == VERIFICATION_COLLECTION_ONLY
            if not collectionish:
                if _is_exactish_url(p.url or "") and not p.section:
                    if "mooc.fi" in (p.url or ""):
                        p.exactness = EXACTNESS_MULTI_TOPIC
                        p.section = p.section or (p.url or "").rstrip("/").split("/")[-1]
                    continue
                continue
            if not refs:
                if "mooc.fi" in (p.url or ""):
                    p.exactness = EXACTNESS_MULTI_TOPIC
                    p.section = p.section or (p.url or "").rstrip("/").split("/")[-1]
                    p.verification_status = VERIFICATION_NEEDS_REVIEW
                continue
            best = refs[0]
            best.role = "PRIMARY"
            best.order_index = min(p.order_index or 0, 0) - 1
            best.exactness = EXACTNESS_EXACT
            best.section = best.section or best.title
            best.verification_status = VERIFICATION_NEEDS_REVIEW
            p.role = "SUPPLEMENT"
            p.exactness = EXACTNESS_COLLECTION
            p.verification_status = VERIFICATION_COLLECTION_ONLY
            promoted += 1
            demoted += 1

    db.flush()
    return {"promoted": promoted, "demoted": demoted, "dsa_injected": dsa_injected}
