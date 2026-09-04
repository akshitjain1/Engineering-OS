"""The exact page each DSA topic should open, instead of a section index.

Found on a real morning: "Array traversal" opened
geeksforgeeks.org/array-data-structure-guide/ -- the index for the whole Arrays
section -- when the page for that topic, /dsa/traversal-in-array/, exists. The
title read "Learn: Array traversal", which is not a page title at all but the
topic name with a word in front.

All 44 of these were generated the same way, and eight of them pointed at
geeksforgeeks.org/data-structures/ -- the index for the entire subject. Opening
a 40-topic index and being told to read it is not a reading assignment.

Each entry is (path, why). The path is the canonical GeeksforGeeks URL, already
carrying the /dsa/ prefix the site now redirects to, so nothing has to bounce.
Titles are never written here: they are read from the page itself when this is
applied, because a title typed by hand is exactly how the old ones came to
describe pages that did not exist.

Where no better page was found, the entry keeps the current URL and says so.
A vague page honestly titled beats a specific-sounding invention.
"""

from __future__ import annotations

GFG = "https://www.geeksforgeeks.org/"

#: topic slug -> (path after the domain, why this page)
DSA_PRIMARY_SOURCES: dict[str, tuple[str, str]] = {
    # --- Algorithmic thinking -------------------------------------------
    "dsa-algorithmic-thinking": (
        "dsa/introduction-to-algorithms/",
        "What an algorithm is, before any structure is introduced.",
    ),
    # --- Arrays -----------------------------------------------------------
    "dsa-array-traversal": (
        "dsa/traversal-in-array/",
        "The topic is traversal. The array index page is the section, not the lesson.",
    ),
    "dsa-prefix-sums": (
        "dsa/prefix-sum-array-implementation-applications-competitive-programming/",
        "Already the right page; canonicalised and retitled.",
    ),
    # --- Strings ----------------------------------------------------------
    "dsa-string-manipulation": (
        "dsa/string-data-structure/",
        "The fundamentals page for strings, which is what this topic is.",
    ),
    "dsa-string-frequency": (
        "dsa/counting-frequencies-of-array-elements/",
        "Frequency counting, worked directly.",
    ),
    "dsa-string-patterns": (
        "dsa/pattern-searching/",
        "Pattern searching, rather than the strings index all three string topics shared.",
    ),
    # --- Hashing ----------------------------------------------------------
    "dsa-hash-map": (
        "dsa/introduction-to-hashing-2/",
        "How hashing works, which is what a map is built on.",
    ),
    "dsa-hash-set": (
        "dsa/hashing-data-structure/",
        "The hashing structure page; distinct from the introduction used for maps.",
    ),
    "dsa-lookup-patterns": (
        "dsa/applications-of-hashing/",
        "What hashing is used for -- the topic exactly. Was on the whole-subject index.",
    ),
    # --- Two pointers -----------------------------------------------------
    "dsa-two-pointers-opposite": (
        "dsa/two-pointers-technique/",
        "The canonical two-pointers page.",
    ),
    "dsa-two-pointers-same": (
        "dsa/window-sliding-technique/",
        "Same-direction pointers is the sliding window; a different page from the opposite case.",
    ),
    "dsa-two-pointers-partition": (
        "dsa/two-pointers-technique/",
        "No separate partition page found; kept, honestly titled.",
    ),
    # --- Stack ------------------------------------------------------------
    "dsa-stack-fundamentals": (
        "dsa/introduction-to-stack-data-structure-and-algorithm-tutorials/",
        "The introduction, not the stack section index.",
    ),
    "dsa-monotonic-stack": (
        "dsa/introduction-to-monotonic-stack-2/",
        "Monotonic stacks have their own page; this shared the stack index.",
    ),
    # --- Queue ------------------------------------------------------------
    "dsa-queue-deque": (
        "dsa/deque-set-1-introduction-applications/",
        "The deque page, since the topic is queue *and deque*.",
    ),
    "dsa-queue-bfs-relationship": (
        "dsa/breadth-first-search-or-bfs-for-a-graph/",
        "The relationship being taught is BFS, which is where the queue earns its place.",
    ),
    # --- Recursion --------------------------------------------------------
    "dsa-recursion-model": (
        "dsa/introduction-to-recursion-2/",
        "Already the right page; canonicalised and retitled.",
    ),
    "dsa-call-stack": (
        "dsa/stack-data-structure/",
        "No dedicated call-stack page found; kept, honestly titled.",
    ),
    "dsa-recursion-to-iteration": (
        "dsa/difference-between-recursion-and-iteration/",
        "The topic is the conversion, and this page is about exactly that.",
    ),
    # --- Backtracking -----------------------------------------------------
    "dsa-permutations": (
        "dsa/introduction-to-backtracking-2/",
        "Backtracking, rather than the whole-subject index it had.",
    ),
    "dsa-constraint-search": (
        "dsa/introduction-to-backtracking-2/",
        "Constraint search is backtracking. It was pointing at binary search, a different technique.",
    ),
    # --- Sorting ----------------------------------------------------------
    "dsa-counting-radix": (
        "dsa/counting-sort/",
        "Counting sort itself, rather than the whole-subject index.",
    ),
    # --- Binary search ----------------------------------------------------
    "dsa-binary-search-classic": (
        "dsa/binary-search/",
        "Already the right page; canonicalised and retitled.",
    ),
    "dsa-search-on-answer": (
        "dsa/binary-search-on-answer-tutorial-with-problems/",
        "Searching the answer space has its own page; this shared the plain binary search one.",
    ),
    "dsa-rotated-arrays": (
        "dsa/array-data-structure-guide/",
        "No rotated-array search page resolved; kept, honestly titled.",
    ),
    # --- Heaps ------------------------------------------------------------
    "dsa-heap-structure": (
        "dsa/heap-data-structure/",
        "The structure page, which is what this topic is.",
    ),
    "dsa-priority-queue": (
        "dsa/priority-queue-set-1-introduction/",
        "The priority queue introduction; it shared the heap page.",
    ),
    "dsa-heap-scheduling": (
        "dsa/k-largestor-smallest-elements-in-an-array/",
        "The classic heap-selection problem, rather than the heap index again.",
    ),
    # --- Graphs -----------------------------------------------------------
    "dsa-graph-representations": (
        "dsa/graph-and-its-representations/",
        "Representation specifically; it had the graph section index.",
    ),
    "dsa-graph-bfs": (
        "dsa/breadth-first-search-or-bfs-for-a-graph/",
        "Already the right page; canonicalised and retitled.",
    ),
    "dsa-graph-dfs": (
        "dsa/depth-first-search-or-dfs-for-a-graph/",
        "Already the right page; canonicalised and retitled.",
    ),
    "dsa-graph-cycle": (
        "dsa/detect-cycle-in-a-graph/",
        "Cycle detection; it had the graph section index.",
    ),
    "dsa-bipartite": (
        "dsa/bipartite-graph/",
        "Bipartite graphs; it had the graph section index.",
    ),
    "dsa-advanced-graphs": (
        "dsa/strongly-connected-components/",
        "A concrete advanced graph topic, rather than the section index.",
    ),
    # --- Union-Find -------------------------------------------------------
    "dsa-union-find": (
        "dsa/introduction-to-disjoint-set-data-structure-or-union-find-algorithm/",
        "The union-find introduction. It was on the whole-subject index.",
    ),
    # --- Greedy -----------------------------------------------------------
    "dsa-greedy-reasoning": (
        "dsa/greedy-algorithms/",
        "The greedy tutorial, which is the reasoning topic.",
    ),
    "dsa-greedy-exchange": (
        "dsa/greedy-approach-vs-dynamic-programming/",
        "When greedy is safe and when it is not -- the argument this topic teaches.",
    ),
    "dsa-greedy-scheduling": (
        "dsa/job-sequencing-problem/",
        "A scheduling problem, rather than the greedy index all four greedy topics shared.",
    ),
    "dsa-greedy-patterns": (
        "dsa/activity-selection-problem-greedy-algo-1/",
        "The canonical greedy pattern, worked.",
    ),
    # --- Dynamic programming ----------------------------------------------
    "dsa-memoization": (
        "dsa/memoization-1d-2d-and-3d/",
        "Memoization itself; it had the whole-subject index.",
    ),
    "dsa-knapsack": (
        "dsa/0-1-knapsack-problem-dp-10/",
        "The knapsack problem; it had the whole-subject index.",
    ),
    # --- Advanced ---------------------------------------------------------
    "dsa-tries": (
        "dsa/trie-insert-and-search/",
        "Already the right page; canonicalised and retitled.",
    ),
    "dsa-bit-manipulation": (
        "dsa/bits-manipulation-important-tactics/",
        "Already the right page; canonicalised and retitled.",
    ),
    # These three were missed on the first pass: their titles were real, so the
    # placeholder-title filter never saw them, while their URLs were section
    # indexes all the same. Top-K was on the whole-subject index.
    "dsa-top-k": (
        "dsa/k-largestor-smallest-elements-in-an-array/",
        "The k-largest problem itself. It was on the index for the entire subject.",
    ),
    "dsa-bst-delete": (
        "dsa/deletion-in-binary-search-tree/",
        "Deletion specifically, rather than the BST section index.",
    ),
    "dsa-list-operations": (
        "dsa/insertion-in-linked-list/",
        "A concrete list operation, rather than the linked-list section index.",
    ),
    "dsa-interview-hygiene": (
        "dsa/commonly-asked-data-structure-interview-questions-set-1/",
        "Interview questions, rather than the whole-subject index.",
    ),
}


def url_for(topic_slug: str) -> str | None:
    entry = DSA_PRIMARY_SOURCES.get(topic_slug)
    return GFG + entry[0] if entry else None
