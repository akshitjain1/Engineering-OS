"""Deterministic V1.5 baseline diagnostic bank. Does not modify curriculum YAML."""

from __future__ import annotations

from functools import lru_cache
from typing import Any


def _q(
    qid: str,
    domain: str,
    qtype: str,
    prompt: str,
    topics: list[str],
    *,
    category: str,
    options: list[str] | None = None,
    answer: str | None = None,
    keywords: list[str] | None = None,
    expected_complexity: str | None = None,
    explanation: str | None = None,
    secondary: list[str] | None = None,
) -> dict[str, Any]:
    item = {
        "id": qid,
        "domain": domain,
        "type": qtype,
        "prompt": prompt,
        "topics": topics,
        "secondary": secondary or [],
        "category": category,
        "explanation": explanation or "",
    }
    if options is not None:
        item["options"] = options
    if answer is not None:
        item["answer"] = answer
    if keywords:
        item["keywords"] = keywords
    if expected_complexity:
        item["expected_complexity"] = expected_complexity
    return item


def _mcq(qid, domain, prompt, options, answer, topics, category="conceptual", secondary=None, qtype="mcq", explanation=""):
    return _q(
        qid,
        domain,
        qtype,
        prompt,
        topics,
        category=category,
        options=options,
        answer=answer,
        secondary=secondary,
        explanation=explanation,
    )


FOUNDATIONS: list[dict[str, Any]] = [
    _mcq("cf-01", "foundations", "How many bits are in one byte?", ["4", "8", "16", "32"], "8", ["cf-bits-and-bytes"]),
    _mcq("cf-02", "foundations", "What is the decimal value of binary 1010?", ["8", "9", "10", "12"], "10", ["cf-binary"]),
    _mcq("cf-03", "foundations", "Hexadecimal A represents which decimal value?", ["10", "11", "15", "16"], "10", ["cf-hexadecimal"], secondary=["cf-binary"]),
    _mcq("cf-04", "foundations", "The CPU primarily:", ["Stores files permanently", "Executes instructions", "Routes packets", "Draws pixels"], "Executes instructions", ["cf-cpu"]),
    _mcq("cf-05", "foundations", "Which memory is typically volatile and used for running programs?", ["SSD", "HDD", "RAM", "Optical disc"], "RAM", ["cf-ram"], secondary=["cf-storage"]),
    _mcq("cf-06", "foundations", "CPU cache exists mainly to:", ["Replace the kernel", "Hide latency of slower memory", "Encrypt disks", "Schedule processes"], "Hide latency of slower memory", ["cf-cache"]),
    _mcq("cf-07", "foundations", "The classic instruction cycle is:", ["Compile-link-load", "Fetch-decode-execute", "Push-pop-peek", "Map-reduce-filter"], "Fetch-decode-execute", ["cf-instruction-execution"]),
    _mcq("cf-08", "foundations", "A compiler typically:", ["Interprets one line at a time only", "Translates source to another form before run", "Is the operating system kernel", "Stores git history"], "Translates source to another form before run", ["cf-compiler"], secondary=["cf-interpreter"]),
    _mcq("cf-09", "foundations", "A running instance of a program is called a:", ["Repository", "Process", "Byte", "Socket"], "Process", ["cf-process"], secondary=["cf-program"]),
    _mcq("cf-10", "foundations", "The kernel is:", ["A text editor plugin", "Core OS software managing hardware and processes", "A git remote", "A Java package"], "Core OS software managing hardware and processes", ["cf-kernel"]),
    _mcq("cf-11", "foundations", "Threads in the same process typically share:", ["CPU caches exclusively", "Address space / memory of the process", "Nothing at all", "Separate kernels"], "Address space / memory of the process", ["cf-threads"]),
    _mcq("cf-12", "foundations", "Virtual memory mainly lets the OS:", ["Avoid using a filesystem", "Give processes a large address space backed by RAM and disk", "Replace the ALU", "Disable caching"], "Give processes a large address space backed by RAM and disk", ["cf-virtual-memory-basics"], secondary=["cf-os-memory"]),
    _mcq("cf-13", "foundations", "In a Unix shell, a pipe | connects:", ["Two git remotes", "Stdout of one command to stdin of the next", "Only TCP sockets", "Binary to hex"], "Stdout of one command to stdin of the next", ["cf-pipes"], secondary=["cf-shell"]),
    _mcq("cf-14", "foundations", "A git commit records:", ["Only untracked files", "A snapshot (with metadata) of the project at a point in time", "The kernel scheduler", "JVM bytecode"], "A snapshot (with metadata) of the project at a point in time", ["cf-commits"]),
    _mcq("cf-15", "foundations", "A git branch is best described as:", ["A pointer/label to a commit lineage", "A running process", "A CPU register", "A filesystem inode only"], "A pointer/label to a commit lineage", ["cf-branches"]),
    _mcq(
        "cf-16",
        "foundations",
        "If an algorithm's work grows linearly with n, the time complexity is typically:",
        ["O(1)", "O(log n)", "O(n)", "O(n!)"],
        "O(n)",
        ["cf-time-complexity-intro"],
        qtype="complexity",
        category="problem_solving",
    ),
    _mcq("cf-17", "foundations", "A useful first debugging step is often:", ["Rewrite the OS", "Reproduce the failure and inspect actual vs expected state", "Delete git history", "Disable the compiler"], "Reproduce the failure and inspect actual vs expected state", ["cf-debugging-thinking"]),
    _q(
        "cf-18",
        "foundations",
        "short_answer",
        "Name one reason to check empty input and overflow as edge cases.",
        ["cf-edge-cases"],
        category="explanation",
        answer="bugs hide at boundaries",
        keywords=["empty", "boundary", "overflow", "null", "zero", "off-by-one"],
        explanation="Edge cases catch off-by-one, empty, and overflow failures.",
    ),
]

JAVA: list[dict[str, Any]] = [
    _mcq("java-01", "java", "JDK versus JRE: the JDK additionally includes:", ["Only a browser", "Tools to compile Java programs (e.g. javac)", "The Linux kernel", "A GPU driver"], "Tools to compile Java programs (e.g. javac)", ["java-jdk-jre"]),
    _mcq("java-02", "java", "The entry method of a standard Java application is:", ["Main.loop", "public static void main(String[] args)", "init()", "start.jar"], "public static void main(String[] args)", ["java-first-program"]),
    _mcq("java-03", "java", "javac Hello.java then java Hello typically:", ["Runs Python", "Compiles then runs the class", "Pushes to git", "Formats SQL"], "Compiles then runs the class", ["java-compile-and-run"]),
    _mcq("java-04", "java", "Which is a Java primitive type?", ["String", "Integer", "int", "List"], "int", ["java-primitives"]),
    _mcq("java-05", "java", "Narrowing conversion from long to int may:", ["Never compile", "Lose information / truncate", "Always throw", "Change the class loader"], "Lose information / truncate", ["java-type-conversion"]),
    _mcq("java-06", "java", "What does 5 / 2 yield for int operands in Java?", ["2.5", "2", "3", "2.0"], "2", ["java-operators"], qtype="tracing"),
    _mcq("java-07", "java", "A for-loop that must run exactly n times with i from 0 typically uses:", ["i <= n", "i < n", "i == n", "i > n"], "i < n", ["java-loops"]),
    _mcq("java-08", "java", "break in a loop:", ["Ends the method always", "Exits the innermost loop/switch", "Deletes the array", "Starts a thread"], "Exits the innermost loop/switch", ["java-break-continue"]),
    _mcq("java-09", "java", "A method's parameters are:", ["Always global", "Inputs in the method signature", "JVM flags only", "Git remotes"], "Inputs in the method signature", ["java-method-basics"]),
    _mcq("java-10", "java", "Overloading means:", ["Same name, different parameter lists", "Two classes with the same file name only", "Extending Thread", "Using synchronized"], "Same name, different parameter lists", ["java-overloading"]),
    _mcq(
        "java-11",
        "java",
        "After int[] a = {1,2,3}; int[] b = a; b[0] = 9; a[0] is:",
        ["1", "9", "0", "compile error"],
        "9",
        ["java-references"],
        secondary=["java-arrays"],
        qtype="tracing",
    ),
    _mcq("java-12", "java", "String is:", ["A primitive", "An immutable object type", "A kernel call", "Always interned user input"], "An immutable object type", ["java-strings"]),
    _mcq("java-13", "java", "new allocates an object and returns:", ["A primitive copy always", "A reference", "A file descriptor", "A git hash"], "A reference", ["java-classes-objects"], secondary=["java-references"]),
    _mcq("java-14", "java", "A constructor's job is primarily to:", ["Delete class files", "Initialize a new instance", "Start the GC", "Compile JNI"], "Initialize a new instance", ["java-constructors"]),
    _mcq("java-15", "java", "Encapsulation typically uses:", ["Public fields only", "Private state with controlled accessors", "Static imports of Thread", "Hex editors"], "Private state with controlled accessors", ["java-encapsulation"]),
    _mcq("java-16", "java", "List<E> is a:", ["Primitive", "Interface for ordered collections", "CPU cache", "SQL dialect"], "Interface for ordered collections", ["java-list"]),
    _mcq("java-17", "java", "HashMap get/put average complexity is typically:", ["O(n!)", "O(1)", "O(n^3)", "O(n log n log n)"], "O(1)", ["java-map"], qtype="complexity", category="problem_solving", secondary=["dsa-hash-map"]),
    _mcq("java-18", "java", "A Java PriorityQueue is by default a:", ["Max-heap", "Min-heap", "BST", "Deque only"], "Min-heap", ["java-priority-queue"]),
    _mcq("java-19", "java", "Checked exceptions in Java:", ["Must be handled or declared for many APIs", "Are identical to Error", "Only exist in C++", "Disable GC"], "Must be handled or declared for many APIs", ["java-checked-unchecked"], secondary=["java-try-catch"]),
    _mcq("java-20", "java", "An interface can specify:", ["Only private fields in Java 8-only", "A contract of methods a class can implement", "The OS scheduler", "Git LFS"], "A contract of methods a class can implement", ["java-interfaces"]),
    _q(
        "java-21",
        "java",
        "implementation",
        "Implement reverse of an int array in-place in Java. Submit code, a short explanation, and time complexity.",
        ["java-arrays"],
        category="implementation",
        expected_complexity="O(n)",
        explanation="Two pointers swap toward the center; O(n) time, O(1) extra space.",
    ),
    _q(
        "java-22",
        "java",
        "implementation",
        "Implement a frequency counter for an int array (value -> count) in Java. Submit code, explanation, and complexity.",
        ["java-map"],
        category="implementation",
        expected_complexity="O(n)",
        secondary=["dsa-array-frequency"],
        explanation="One pass filling HashMap; average O(n) time.",
    ),
    _q(
        "java-23",
        "java",
        "short_answer",
        "Why can assigning one array variable to another make two names observe the same mutation?",
        ["java-references"],
        category="explanation",
        answer="both variables hold the same reference",
        keywords=["reference", "same object", "alias", "pointer", "not a copy"],
    ),
]

DSA: list[dict[str, Any]] = [
    _mcq("dsa-01", "dsa", "An algorithm is primarily:", ["A CPU brand", "A finite procedure to solve a problem", "A git hook", "A CSS rule"], "A finite procedure to solve a problem", ["dsa-algorithmic-thinking"]),
    _mcq("dsa-02", "dsa", "Big-O describes:", ["Exact milliseconds on your laptop", "Asymptotic upper bound on growth", "RAM vendor", "Git blame"], "Asymptotic upper bound on growth", ["dsa-big-o"], qtype="complexity", category="problem_solving"),
    _mcq("dsa-03", "dsa", "Best / worst / average case differ because:", ["Big-O is unused", "Input structure can change how much work happens", "Java has no arrays", "OS threads vanish"], "Input structure can change how much work happens", ["dsa-best-worst-average"]),
    _mcq("dsa-04", "dsa", "Accessing a[i] in an array is typically:", ["O(n)", "O(1)", "O(n log n)", "O(2^n)"], "O(1)", ["dsa-array-traversal"], qtype="complexity", category="problem_solving"),
    _mcq("dsa-05", "dsa", "Inserting at index 0 in a dense array of n is typically:", ["O(1)", "O(n)", "O(log n)", "O(1) amortized always"], "O(n)", ["dsa-array-insert-delete"], qtype="complexity", category="problem_solving"),
    _mcq("dsa-06", "dsa", "A prefix-sum array helps answer:", ["Range sums quickly after O(n) preprocess", "Only graph coloring", "DNS lookups", "Thread parking"], "Range sums quickly after O(n) preprocess", ["dsa-prefix-sums"]),
    _mcq("dsa-07", "dsa", "HashMap lookup by key is typically:", ["O(n) always", "O(1) average", "O(n^2)", "O(n!)"], "O(1) average", ["dsa-hash-map"], qtype="complexity", category="problem_solving", secondary=["dsa-big-o"]),
    _mcq("dsa-08", "dsa", "HashSet is mainly for:", ["Ordered rank queries only", "Membership tests of unique keys", "GPU shaders", "SQL joins only"], "Membership tests of unique keys", ["dsa-hash-set"]),
    _mcq("dsa-09", "dsa", "Two pointers from both ends often apply when:", ["The array is sorted or partitionable", "You need DFS of a graph", "You need Dijkstra", "You need regex"], "The array is sorted or partitionable", ["dsa-two-pointers-opposite"]),
    _mcq("dsa-10", "dsa", "A sliding window is useful for:", ["Subarray/substring constraints while scanning", "Only heaps", "Only MST", "Bootloaders"], "Subarray/substring constraints while scanning", ["dsa-window-variable"], secondary=["dsa-window-fixed"]),
    _mcq("dsa-11", "dsa", "Singly linked list next-node access from head to tail is:", ["O(1) to the middle always", "O(n) to scan", "O(log n)", "O(1) random access like arrays"], "O(n) to scan", ["dsa-singly-linked-list"], qtype="complexity", category="problem_solving"),
    _mcq("dsa-12", "dsa", "Reversing a singly linked list iteratively uses:", ["Three pointers / prev-curr-next", "Binary search", "Union-find", "Dijkstra"], "Three pointers / prev-curr-next", ["dsa-list-reversal"]),
    _mcq("dsa-13", "dsa", "Fast/slow pointers can detect:", ["A cycle in a linked list", "DNS TTL", "CSS specificity", "Git stash"], "A cycle in a linked list", ["dsa-fast-slow"], secondary=["dsa-cycle-detection"]),
    _mcq("dsa-14", "dsa", "A stack is LIFO; useful for:", ["Matching parentheses / DFS call history", "Only shortest paths in weighted graphs", "TCP congestion", "CSS grid"], "Matching parentheses / DFS call history", ["dsa-stack-fundamentals"]),
    _mcq("dsa-15", "dsa", "BFS on an unweighted graph finds:", ["Maximum spanning tree always", "Shortest path in hops from the source", "Only topological order of DAGs", "Huffman codes"], "Shortest path in hops from the source", ["dsa-graph-bfs"], secondary=["dsa-queue-bfs-relationship"]),
    _mcq("dsa-16", "dsa", "DFS explores:", ["Level by level only", "As far as possible along a branch before backtracking", "Only heaps", "Only radix sort"], "As far as possible along a branch before backtracking", ["dsa-graph-dfs"], secondary=["dsa-tree-dfs"]),
    _mcq("dsa-17", "dsa", "Binary search on a sorted array is typically:", ["O(n)", "O(log n)", "O(n^2)", "O(1) always"], "O(log n)", ["dsa-binary-search-classic"], qtype="complexity", category="problem_solving"),
    _mcq("dsa-18", "dsa", "Merge sort worst-case time is:", ["O(n log n)", "O(n^2)", "O(n)", "O(1)"], "O(n log n)", ["dsa-merge-sort"], qtype="complexity", category="problem_solving", secondary=["dsa-sort-complexity"]),
    _mcq("dsa-19", "dsa", "Quick sort worst case (naive pivot) can be:", ["O(n)", "O(n^2)", "O(log n)", "O(1)"], "O(n^2)", ["dsa-quick-sort"], qtype="complexity", category="problem_solving"),
    _mcq("dsa-20", "dsa", "A min-heap supports insert/peek-min typically:", ["O(1) insert always", "O(log n) insert, O(1) peek", "O(n^2) peek", "O(n!) insert"], "O(log n) insert, O(1) peek", ["dsa-heap-structure"], secondary=["dsa-priority-queue"], qtype="complexity", category="problem_solving"),
    _mcq("dsa-21", "dsa", "BST search in a balanced tree is typically:", ["O(log n)", "O(n^2)", "O(1) always", "O(n!)"], "O(log n)", ["dsa-bst-search"], qtype="complexity", category="problem_solving"),
    _mcq("dsa-22", "dsa", "Dynamic programming stores:", ["Only git blobs", "Answers to overlapping subproblems", "CSS variables", "DNS records"], "Answers to overlapping subproblems", ["dsa-dp-mindset"], secondary=["dsa-memoization"]),
    _mcq("dsa-23", "dsa", "Memoization vs tabulation:", ["Memo is top-down cache; tabulation fills a table bottom-up", "They are git commands", "They only apply to graphs", "They disable recursion forever"], "Memo is top-down cache; tabulation fills a table bottom-up", ["dsa-memoization"], secondary=["dsa-tabulation"]),
    _mcq("dsa-24", "dsa", "Dijkstra computes:", ["Unweighted BFS only", "Shortest paths with non-negative weights", "Maximum flow only", "String hashing only"], "Shortest paths with non-negative weights", ["dsa-dijkstra"]),
    _mcq("dsa-25", "dsa", "Topological sort applies to:", ["Any undirected cycle", "Directed acyclic graphs", "Only binary heaps", "Only hash maps"], "Directed acyclic graphs", ["dsa-topological-sort"]),
    _mcq(
        "dsa-26",
        "dsa",
        "Tracing: binary search mid = (lo+hi)/2 on sorted [1,3,5,7], target 5. First mid index (0-based) is:",
        ["0", "1", "2", "3"],
        "1",
        ["dsa-binary-search-classic"],
        qtype="tracing",
        category="problem_solving",
    ),
    _mcq(
        "dsa-27",
        "dsa",
        "Which HashMap operation is O(1) average?",
        ["Sorting all keys", "get/put by key", "In-order traversal of keys", "Heapify"],
        "get/put by key",
        ["dsa-hash-map"],
        secondary=["dsa-big-o"],
        qtype="complexity",
        category="problem_solving",
    ),
    _q(
        "dsa-28",
        "dsa",
        "implementation",
        "Implement iterative binary search in Java returning the index or -1. Submit code, explanation, and complexity.",
        ["dsa-binary-search-classic"],
        category="implementation",
        expected_complexity="O(log n)",
        secondary=["dsa-big-o"],
    ),
    _q(
        "dsa-29",
        "dsa",
        "implementation",
        "Implement iterative reversal of a singly linked list. Submit code, explanation, and complexity.",
        ["dsa-list-reversal"],
        category="implementation",
        expected_complexity="O(n)",
        secondary=["dsa-singly-linked-list"],
    ),
    _q(
        "dsa-30",
        "dsa",
        "implementation",
        "Implement BFS traversal from a source on an adjacency list. Submit code, explanation, and complexity.",
        ["dsa-graph-bfs"],
        category="implementation",
        expected_complexity="O(n+m)",
        secondary=["dsa-queue-bfs-relationship"],
    ),
    _q(
        "dsa-31",
        "dsa",
        "implementation",
        "Implement a simple 1D DP (e.g. climb stairs / Fibonacci with memo or table). Submit code, explanation, and complexity.",
        ["dsa-dp-1d"],
        category="implementation",
        expected_complexity="O(n)",
        secondary=["dsa-memoization"],
    ),
    _q(
        "dsa-32",
        "dsa",
        "short_answer",
        "Why is HashMap get typically O(1) average but not a worst-case guarantee?",
        ["dsa-hash-map"],
        category="explanation",
        answer="hash collisions can degrade to linear chains",
        keywords=["collision", "hash", "worst", "chain", "bucket"],
        secondary=["dsa-big-o"],
    ),
    _q(
        "dsa-33",
        "dsa",
        "short_answer",
        "In one sentence, what overlapping subproblems means for DP.",
        ["dsa-dp-mindset"],
        category="explanation",
        answer="the same smaller problems are solved many times",
        keywords=["overlap", "subproblem", "reuse", "repeated"],
    ),
    _mcq("dsa-34", "dsa", "Tree BFS uses a queue to visit:", ["Deepest node first always", "Level by level", "Only leaves", "Only BST keys in reverse"], "Level by level", ["dsa-tree-bfs"]),
    _mcq("dsa-35", "dsa", "A variable sliding window grows/shrinks to maintain:", ["A heap invariant only", "A constraint (sum, unique chars, etc.)", "TCP only", "CSS cascade"], "A constraint (sum, unique chars, etc.)", ["dsa-window-variable"]),
]


@lru_cache(maxsize=1)
def all_questions() -> tuple[dict[str, Any], ...]:
    return tuple(FOUNDATIONS + JAVA + DSA)


def questions_by_id() -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in all_questions()}


def public_question(item: dict[str, Any]) -> dict[str, Any]:
    public = {
        "id": item["id"],
        "domain": item["domain"],
        "type": item["type"],
        "prompt": item["prompt"],
        "topics": item["topics"],
        "secondary": item.get("secondary") or [],
        "category": item["category"],
    }
    if item.get("options"):
        public["options"] = item["options"]
    if item["type"] == "implementation":
        public["requires"] = ["code", "explanation", "complexity"]
    return public


def domain_counts() -> dict[str, int]:
    counts = {"foundations": 0, "java": 0, "dsa": 0}
    for item in all_questions():
        counts[item["domain"]] += 1
    return counts
