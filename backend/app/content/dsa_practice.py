"""Enrich DSA exercises with explicit destination + quantity (additive)."""

from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.db.models import CurriculumLesson, CurriculumTopic, LessonExercise

DSA_PRACTICE: dict[str, dict] = {
    "dsa-array-traversal": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/array/",
        "quantity": 5,
        "instructions": (
            "AFTER LEARN + IMPLEMENT from scratch: Solve 2 Easy traversal, "
            "2 Easy/Medium pattern warmups, 1 variation. DESTINATION: LeetCode Array tag. "
            "Do not use a problem as the PRIMARY learning resource."
        ),
    },
    "dsa-array-patterns": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/array/",
        "quantity": 5,
        "instructions": "PRACTICE: 2 Easy, 2 Medium array patterns, 1 variation. LeetCode Array tag.",
    },
    "dsa-string-manipulation": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/string/",
        "quantity": 5,
        "instructions": "PRACTICE: 2 Easy string scans, 2 Medium manipulations, 1 variation. String tag.",
    },
    "dsa-singly-linked-list": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/linked-list/",
        "quantity": 5,
        "instructions": "PRACTICE: 2 Easy walks, 2 reverse/merge, 1 cycle detection. Linked List tag.",
    },
    "dsa-stack-fundamentals": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/stack/",
        "quantity": 4,
        "instructions": "PRACTICE: 2 Easy stack sims, 2 Medium monotonic/parse. Stack tag.",
    },
    "dsa-queue-deque": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/queue/",
        "quantity": 3,
        "instructions": "PRACTICE: 2 Easy queue sims, 1 BFS-style use. Queue tag.",
    },
    "dsa-hash-map": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/hash-table/",
        "quantity": 5,
        "instructions": "PRACTICE: 2 Easy frequency maps, 2 Medium lookups, 1 variation. Hash Table tag.",
    },
    "dsa-binary-search-classic": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/binary-search/",
        "quantity": 7,
        "instructions": (
            "PRACTICE progression: 2 basic binary search, 3 standard bound/search-space, "
            "2 variations. DESTINATION: LeetCode Binary Search. Implement binary search yourself first."
        ),
    },
    "dsa-binary-search-boundaries": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/binary-search/",
        "quantity": 5,
        "instructions": "PRACTICE: 2 lower/upper bound, 2 search-on-answer warmups, 1 rotated variant. Binary Search tag.",
    },
    "dsa-recursion-model": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/recursion/",
        "quantity": 4,
        "instructions": "PRACTICE: 2 Easy recursive formulations, 2 Medium warmups. Recursion tag.",
    },
    "dsa-binary-trees": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/tree/",
        "quantity": 6,
        "instructions": "PRACTICE: 2 Easy traversals, 3 Medium path/height, 1 construction. Tree tag.",
    },
    "dsa-graph-bfs": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/breadth-first-search/",
        "quantity": 4,
        "instructions": "PRACTICE: 2 Easy BFS, 2 Medium grid/graph BFS. BFS tag.",
    },
    "dsa-graph-dfs": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/depth-first-search/",
        "quantity": 4,
        "instructions": "PRACTICE: 2 Easy DFS, 2 Medium component/path DFS. DFS tag.",
    },
    "dsa-dp-1d": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/dynamic-programming/",
        "quantity": 6,
        "instructions": "PRACTICE: 2 Easy 1D, 3 classic Medium, 1 variation. Write recurrence before coding. DP tag.",
    },
    "dsa-dp-2d": {
        "destination_type": "LEETCODE",
        "destination_url": "https://leetcode.com/tag/dynamic-programming/",
        "quantity": 5,
        "instructions": "PRACTICE: 2 Easy/Medium 2D DP, 2 classic, 1 optimization. DP tag.",
    },
}


def enrich_dsa_practice(db: Session) -> dict[str, int]:
    updated = 0
    created = 0
    # Explicit map first
    topics = (
        db.query(CurriculumTopic)
        .options(selectinload(CurriculumTopic.lessons).selectinload(CurriculumLesson.exercises))
        .filter(CurriculumTopic.domain_key == "dsa")
        .all()
    )

    def _heuristic(slug: str, name: str) -> dict:
        s = f"{slug} {name}".lower()
        tag = "array"
        qty = 4
        if "binary-search" in s or "binary search" in s:
            tag, qty = "binary-search", 5
        elif "linked" in s:
            tag, qty = "linked-list", 4
        elif "stack" in s:
            tag, qty = "stack", 4
        elif "queue" in s or "deque" in s:
            tag, qty = "queue", 3
        elif "hash" in s or "map" in s:
            tag, qty = "hash-table", 4
        elif "tree" in s or "bst" in s:
            tag, qty = "tree", 5
        elif "heap" in s or "priority" in s:
            tag, qty = "heap-priority-queue", 4
        elif "graph" in s or "bfs" in s or "dfs" in s:
            tag, qty = "graph", 4
        elif "dp" in s or "dynamic" in s:
            tag, qty = "dynamic-programming", 5
        elif "string" in s:
            tag, qty = "string", 4
        elif "sort" in s:
            tag, qty = "sorting", 4
        elif "greedy" in s:
            tag, qty = "greedy", 4
        elif "backtrack" in s:
            tag, qty = "backtracking", 4
        elif "two-pointer" in s or "two pointer" in s:
            tag, qty = "two-pointers", 4
        elif "sliding" in s:
            tag, qty = "sliding-window", 4
        elif "bit" in s:
            tag, qty = "bit-manipulation", 3
        elif "trie" in s:
            tag, qty = "trie", 3
        return {
            "destination_type": "LEETCODE",
            "destination_url": f"https://leetcode.com/tag/{tag}/",
            "quantity": qty,
            "instructions": (
                f"AFTER learning the concept and implementing it from scratch: "
                f"solve {qty} problems on LeetCode tag '{tag}' "
                f"(prefer Easy→Medium progression). Do not use problems as PRIMARY learn."
            ),
        }

    for topic in topics:
        spec = DSA_PRACTICE.get(topic.slug or "") or _heuristic(topic.slug or "", topic.name or "")
        lesson = sorted(topic.lessons or [], key=lambda l: l.order_index)[0] if topic.lessons else None
        if not lesson:
            continue
        practice = next(
            (e for e in (lesson.exercises or []) if e.destination_type or "PRACTICE" in (e.title or "").upper()),
            None,
        )
        if practice is None and lesson.exercises:
            practice = lesson.exercises[0]
        if practice is None:
            practice = LessonExercise(
                slug=f"{topic.slug}-explicit-practice",
                title=f"Practice: {topic.name}",
                description=spec["instructions"],
                lesson_id=lesson.id,
                exercise_type="ACTION_CHECKLIST",
                difficulty="medium",
            )
            db.add(practice)
            created += 1
        practice.description = spec["instructions"]
        practice.practice_instructions = spec["instructions"]
        practice.destination_type = spec["destination_type"]
        practice.destination_url = spec["destination_url"]
        practice.quantity = spec["quantity"]
        practice.concepts_required = []
        updated += 1
    db.flush()
    return {"updated": updated, "created": created}
