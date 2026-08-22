"""Domain 2 DSA: Stack through Binary Search (part 2)."""

from __future__ import annotations

from _d2_helpers import *

CONTENT = {}


def _add(slug, **kwargs):
    CONTENT[slug] = unit(**kwargs)


M = [
    "Explain the idea without notes (language-independent).",
    "Implement in Java without copying.",
    "State the C++ equivalent at a high level if you already know it.",
    "Solve 2 representative problems independently.",
    "State time and space complexity of a correct approach.",
    "Name one common mistake for this topic.",
    "Score >= 80% on topic questions.",
]


_add(
    "dsa-stack-fundamentals",
    hours=1.0,
    objective="Use LIFO for matching and nested structure.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "A stack is Last-In-First-Out (LIFO): push adds on top, pop removes the most recent. "
        "In Java use `ArrayDeque` as a stack (`push`/`pop`/`peek`). " + CPP["deque"] + " "
        "Do not treat `java.util.Stack` as the preferred API — it extends `Vector`, is synchronized, and is legacy. "
        "C++ `std::stack` is the same LIFO idea. Stacks model nested structure: parentheses matching, undo, DFS frames, "
        "and evaluating postfix notation. Watching Abdul Bari on the stack ADT is orientation; mastery is implement + trace + problems."
    ),
    mastery=[
        "Implement stack operations with ArrayDeque; solve a matching-brackets style problem.",
        *M,
    ],
    resources=[
        bari_primary("dsa-stack-fundamentals", "2.4 Stack ADT / stack operations"),
        nc150("dsa-stack-fundamentals", "Stack"),
        lc_collection("dsa-stack-fundamentals"),
    ],
    questions=[
        q(
            "dsa-stack-fundamentals-q1",
            "Which Java type is the preferred stack implementation in this curriculum?",
            ["java.util.Stack", "ArrayDeque", "PriorityQueue", "LinkedList only as a queue"],
            "ArrayDeque",
            "ArrayDeque implements Deque efficiently without Vector legacy baggage.",
            mastery=True,
        ),
        q(
            "dsa-stack-fundamentals-q2",
            "After pushes 1, 2, 3 then one pop on an ArrayDeque stack, what is peek?",
            ["1", "2", "3", "empty"],
            "2",
            "LIFO: push order 1,2,3 → top is 3; pop removes 3; peek sees 2.",
        ),
        q(
            "dsa-stack-fundamentals-q3",
            "Why is stack natural for valid-parentheses checking?",
            ["Stacks sort characters alphabetically.",
             "An opening symbol waits on the stack until its matching closer arrives.",
             "Stacks always use O(1) memory for any input.",
             "Parentheses require a priority queue."],
            "An opening symbol waits on the stack until its matching closer arrives.",
            "Each opener is pushed; a closer must match the most recent unmatched opener.",
        ),
        q(
            "dsa-stack-fundamentals-q4",
            "C++ `std::stack<int> s; s.push(5);` — what is the C++ equivalent of Java `s.peek()`?",
            ["s.front()", "s.top()", "s.back()", "s.get()"],
            "s.top()",
            "std::stack exposes top() for the LIFO element; push/pop mirror Java.",
        ),
        q(
            "dsa-stack-fundamentals-q5",
            "Time complexity of push/pop on ArrayDeque-backed stack?",
            ["O(n) always", "O(log n)", "O(1) amortized", "O(n log n)"],
            "O(1) amortized",
            "Deque push/pop at ends are amortized constant time.",
        ),
        q(
            "dsa-stack-fundamentals-q6",
            "Trace: push A, push B, pop, push C, pop. Final stack bottom-to-top?",
            ["A", "A C", "B C", "empty"],
            "A",
            "After A,B → pop removes B → push C → pop removes C → only A remains.",
        ),
    ],
    exercises=[
        ex(
            "dsa-stack-fundamentals-ex1",
            "Stack implement, trace, and NeetCode subset",
            "IMPLEMENT: `boolean isValid(String s)` for parentheses/brackets using `ArrayDeque<Character>`. "
            "TRACE: Dry-run on `([])` and `([)]` showing push/pop/peek steps. "
            "SOLVE (NeetCode 150 → Stack): Valid Parentheses, Min Stack, Evaluate Reverse Polish Notation — "
            "open NeetCode 150 Stack section; do not invent LeetCode URLs. "
            "TRANSFER (internal): Given nested XML-style tags `<div><p></p></div>`, return whether tags nest correctly "
            "(same stack idea, different domain — no external URL).",
        ),
    ],
)

_add(
    "dsa-monotonic-stack",
    hours=1.0,
    objective="Maintain an increasing or decreasing stack.",
    explanation=(
        RELEARN + " A monotonic stack keeps elements in sorted order (increasing or decreasing) as you scan. "
        "It is a pattern on top of a normal stack, not a new ADT. Classic use: next greater element — "
        "when you see a larger value, pop smaller indices from the stack because their 'next greater' is now known. "
        "Each element is pushed and popped at most once → O(n). Java: still `ArrayDeque` storing indices or values. "
        "C++: same with `std::stack` or a vector used as stack."
    ),
    mastery=[
        "Dry-run next-greater-element with a monotonic stack.",
        *M,
    ],
    resources=[
        bari_primary("dsa-monotonic-stack", "2.4 Stack — applications / monotonic pattern"),
        nc150("dsa-monotonic-stack", "Stack"),
        lc_collection("dsa-monotonic-stack"),
    ],
    questions=[
        q(
            "dsa-monotonic-stack-q1",
            "What makes a stack 'monotonic' in the NGE pattern?",
            ["Elements are always equal.",
             "Stack order matches increasing (or decreasing) values of stored indices/values.",
             "The stack never pops.",
             "It requires a heap."],
            "Stack order matches increasing (or decreasing) values of stored indices/values.",
            "You discard dominated elements when a better candidate arrives.",
            mastery=True,
        ),
        q(
            "dsa-monotonic-stack-q2",
            "Why store indices instead of values in NGE?",
            ["Indices are always smaller integers.",
             "You need the position to fill the answer array.",
             "Values cannot be compared.",
             "Java requires indices for ArrayDeque."],
            "You need the position to fill the answer array.",
            "The answer is per-index; values alone lose position.",
        ),
        q(
            "dsa-monotonic-stack-q3",
            "Time complexity of monotonic-stack NGE for n elements?",
            ["O(n^2)", "O(n log n)", "O(n)", "O(1)"],
            "O(n)",
            "Each index pushed once and popped once.",
        ),
        q(
            "dsa-monotonic-stack-q4",
            "For `[2,1,2]` scanning left, when index 2 (value 2) arrives, what happens to index 1 (value 1)?",
            ["It stays under 2 forever.",
             "It is popped because 2 is the next greater for 1.",
             "Stack clears entirely.",
             "Value 1 is pushed again."],
            "It is popped because 2 is the next greater for 1.",
            "1 < 2, so index 1's NGE is index 2.",
        ),
        q(
            "dsa-monotonic-stack-q5",
            "Daily Temperatures is monotonic stack because…",
            ["It sorts the array.",
             "Warmer days 'resolve' cooler days waiting in the stack.",
             "It needs BFS.",
             "Temperatures are always monotonic input."],
            "Warmer days 'resolve' cooler days waiting in the stack.",
            "Same NGE structure with temperatures as keys.",
        ),
        q(
            "dsa-monotonic-stack-q6",
            "Common mistake?",
            ["Using ArrayDeque.",
             "Forgetting to pop remaining indices as 'no greater element'.",
             "Using O(n) time.",
             "Storing pairs."],
            "Forgetting to pop remaining indices as 'no greater element'.",
            "After scan, leftover stack entries have no next greater.",
        ),
    ],
    exercises=[
        ex(
            "dsa-monotonic-stack-ex1",
            "Monotonic stack NGE",
            "IMPLEMENT: `int[] nextGreater(int[] nums)` with decreasing monotonic stack of indices. "
            "TRACE: Dry-run `[4,3,2,1,5]` — list each pop and assigned answer. "
            "SOLVE (NeetCode 150 → Stack): Daily Temperatures, Car Fleet — Stack section. "
            "TRANSFER (internal): For heights `[3,1,4,2]`, return how many buildings to the right are taller before a shorter one blocks view "
            "(monotonic decreasing stack of indices).",
        ),
    ],
)

_add(
    "dsa-queue-deque",
    hours=0.75,
    objective="Use FIFO and double-ended queues.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "A queue is First-In-First-Out: enqueue at tail, dequeue from head. "
        "Java: `ArrayDeque` or `LinkedList` implement `Queue`; `Deque` adds `addFirst`/`addLast`. "
        + CPP["deque"] + " "
        "C++: `std::queue` is FIFO adapter; `std::deque` supports both ends. "
        "Use `ArrayDeque` for BFS and sliding-window ends — avoid `java.util.Stack` for LIFO; use Deque for both ends. "
        "Never confuse `Queue.add` throwing on full bounded queues vs `offer` returning false."
    ),
    mastery=[
        "Implement BFS-ready queue usage in Java.",
        *M,
    ],
    resources=[
        bari_primary("dsa-queue-deque", "2.5 Queue ADT / circular queue"),
        nc150("dsa-queue-deque", "Stack"),
        lc_collection("dsa-queue-deque"),
    ],
    questions=[
        q(
            "dsa-queue-deque-q1",
            "FIFO means…",
            ["Last in is first out.", "First in is first out.", "Highest priority first.", "Random order."],
            "First in is first out.",
            "Oldest enqueued element leaves first.",
            mastery=True,
        ),
        q(
            "dsa-queue-deque-q2",
            "Enqueue 1,2,3 then dequeue once — front element?",
            ["1", "2", "3", "empty"],
            "2",
            "Dequeue removes 1; front is now 2.",
        ),
        q(
            "dsa-queue-deque-q3",
            "Java BFS-ready choice?",
            ["java.util.Stack", "ArrayDeque implementing Queue", "HashMap", "PriorityQueue only"],
            "ArrayDeque implementing Queue",
            "Efficient ends; not legacy Stack.",
        ),
        q(
            "dsa-queue-deque-q4",
            "Deque advantage over strict Queue?",
            ["Cannot remove elements.", "Push/pop at both ends in O(1) amortized.",
             "Always sorted.", "Replaces hash table."],
            "Push/pop at both ends in O(1) amortized.",
            "Monotonic stack and 0-1 BFS use both ends.",
        ),
        q(
            "dsa-queue-deque-q5",
            "C++ equivalent of Java `queue.offer(x)`?",
            ["stack.push", "queue.push(x) on std::queue", "map.insert", "sort(x)"],
            "queue.push(x) on std::queue",
            "std::queue pushes at back; pop from front.",
        ),
        q(
            "dsa-queue-deque-q6",
            "Implement queue using two stacks — dequeue cost?",
            ["Always O(1)", "Amortized O(1) with occasional O(n) pour",
             "Always O(log n)", "O(n^2)"],
            "Amortized O(1) with occasional O(n) pour",
            "Pouring stack to stack reverses order for FIFO.",
        ),
    ],
    exercises=[
        ex(
            "dsa-queue-deque-ex1",
            "Queue and deque in Java",
            "IMPLEMENT: `MyQueue` with two `ArrayDeque` stacks (amortized O(1) queue). "
            "Also write `void slidingWindowEnds(int[] a)` using `ArrayDeque<Integer>` as index deque for max-in-window concept (trace only). "
            "TRACE: Enqueue 1,2,3, dequeue, enqueue 4 — state front/back. "
            "SOLVE (NeetCode 150 → Stack): Implement Queue using Stacks, Implement Stack using Queues. "
            "TRANSFER (internal): Process a ticket line: people join at tail, leave from head; simulate 5 operations and state queue contents.",
        ),
    ],
)

_add(
    "dsa-queue-bfs-relationship",
    hours=0.5,
    objective="Explain why BFS uses a queue.",
    explanation=(
        RELEARN + " Breadth-first search explores layer by layer: all nodes at distance d before distance d+1. "
        "A queue preserves that order — dequeue the oldest discovered node, enqueue its unseen neighbors. "
        "DFS uses a stack (or recursion) and goes deep first. You will implement graph BFS later; here the point is the "
        "FIFO discipline matches expanding frontier. Java: `Queue` + `ArrayDeque`; C++: `std::queue`. "
        "Tree level-order is the same pattern without a visited set."
    ),
    mastery=[
        "Contrast stack-DFS vs queue-BFS at a high level.",
        *M,
    ],
    resources=[
        bari_primary("dsa-queue-bfs-relationship", "2.5 Queue — BFS preview / level order"),
        nc150("dsa-queue-bfs-relationship", "Stack"),
        lc_collection("dsa-queue-bfs-relationship"),
    ],
    questions=[
        q(
            "dsa-queue-bfs-relationship-q1",
            "Why queue for BFS?",
            ["Queues sort nodes by key.",
             "FIFO processes nodes in non-decreasing distance from the start.",
             "Stacks are slower in Java.",
             "BFS cannot use recursion."],
            "FIFO processes nodes in non-decreasing distance from the start.",
            "First discovered = first expanded → level order.",
            mastery=True,
        ),
        q(
            "dsa-queue-bfs-relationship-q2",
            "DFS vs BFS on infinite depth path — which finds shortest path in unweighted graph?",
            ["DFS always", "BFS", "Neither", "Both equally"],
            "BFS",
            "BFS first hit at distance d is shortest in unweighted graphs.",
        ),
        q(
            "dsa-queue-bfs-relationship-q3",
            "Tree level-order traversal data structure?",
            ["Stack only", "Queue", "Heap", "Union-find"],
            "Queue",
            "Enqueue children when dequeuing parent.",
        ),
        q(
            "dsa-queue-bfs-relationship-q4",
            "What prevents revisiting nodes in graph BFS?",
            ["Stack", "Visited set or color marking", "Sorting", "Binary search"],
            "Visited set or color marking",
            "Without visited, cycles cause infinite enqueue.",
        ),
        q(
            "dsa-queue-bfs-relationship-q5",
            "Recursive DFS uses which implicit structure?",
            ["Queue", "Call stack (LIFO)", "Hash map", "Deque only"],
            "Call stack (LIFO)",
            "Each call is a frame — stack discipline.",
        ),
    ],
    exercises=[
        ex(
            "dsa-queue-bfs-relationship-ex1",
            "BFS relationship trace",
            "IMPLEMENT: `List<Integer> levelOrder(TreeNode root)` using `Queue<TreeNode>` (`ArrayDeque`). "
            "TRACE: On a tree with root 1, children 2,3, grandchildren 4,5 under 2 — list dequeue order. "
            "SOLVE (NeetCode 150 → Stack): Binary Tree Level Order Traversal (queue pattern; listed under trees but uses queue). "
            "TRANSFER (internal): On an unweighted grid maze, explain in 5 sentences why BFS queue finds shortest steps to exit (no code URL).",
        ),
    ],
)

_add(
    "dsa-recursion-model",
    hours=1.0,
    objective="Write recursive functions with a clear base case.",
    explanation=(
        RELEARN + " Recursion: solve a problem by calling itself on smaller subproblems. Every recursive function needs "
        "(1) base case — stop, return known answer; (2) recursive case — delegate and combine. "
        "Naive Fibonacci `fib(n)=fib(n-1)+fib(n-2)` is teaching-only — exponential time; production uses iteration or memoization. "
        "Java: same syntax as C++; no tail-call optimization guarantee. Trace small inputs on paper before coding."
    ),
    mastery=[
        "Implement a simple recursive function without copying.",
        *M,
    ],
    resources=[
        bari_primary("dsa-recursion-model", "3. Recursion — introduction / base case"),
        lc_collection("dsa-recursion-model"),
    ],
    questions=[
        q(
            "dsa-recursion-model-q1",
            "Every correct recursion must have…",
            ["Only one recursive call.", "A base case that terminates.",
             "A global variable.", "A queue."],
            "A base case that terminates.",
            "Without base case → infinite recursion.",
            mastery=True,
        ),
        q(
            "dsa-recursion-model-q2",
            "Naive Fibonacci time?",
            ["O(n)", "O(log n)", "O(2^n)", "O(1)"],
            "O(2^n)",
            "Teaching tree explodes — not production.",
        ),
        q(
            "dsa-recursion-model-q3",
            "factorial(4) recursive calls after base case reached?",
            ["1", "4", "5", "0"],
            "4",
            "4→3→2→1 base; four delegations.",
        ),
        q(
            "dsa-recursion-model-q4",
            "Production Fibonacci instead of naive recursion?",
            ["Use Stack class", "Iterate or memoize to O(n)",
             "More recursive calls", "Sort first"],
            "Iterate or memoize to O(n)",
            "Naive is for understanding call tree only.",
        ),
        q(
            "dsa-recursion-model-q5",
            "C++ vs Java recursion model?",
            ["Java has no call stack.", "Both use call frames on the stack.",
             "C++ cannot recurse.", "Java optimizes all tail calls."],
            "Both use call frames on the stack.",
            "Each call adds a frame with parameters/locals.",
        ),
        q(
            "dsa-recursion-model-q6",
            "sumArray(a, i) = a[i] + sumArray(a, i+1) if i<n else 0 — base case?",
            ["i < 0", "i >= n", "i == 1", "n == 0 only"],
            "i >= n",
            "When index passes end, sum is 0.",
        ),
    ],
    exercises=[
        ex(
            "dsa-recursion-model-ex1",
            "Recursive sum and power",
            "IMPLEMENT: `int sum(int[] a, int i)` and `int pow(int x, int n)` recursively with clear base cases. "
            "Do NOT submit naive Fibonacci as production — trace it once on n=4 to see duplicate work. "
            "TRACE: Draw call tree for `pow(2,3)`. "
            "SOLVE (NeetCode 150 → Stack): Pow(x, n) — recursion/iteration. "
            "TRANSFER (internal): Recursive GCD `gcd(a,b)` — trace gcd(48,18).",
        ),
    ],
)

_add(
    "dsa-call-stack",
    hours=0.75,
    objective="Trace frames on the call stack.",
    explanation=(
        RELEARN + " Each function call pushes a frame: parameters, locals, return address. Return pops the frame. "
        "Deep recursion can overflow the stack (`StackOverflowError` in Java). Relates to Domain 0 stack memory. "
        "Tracing: write a stack-of-frames table for each call/return. Recursion depth equals pending frames. "
        "Iterative solutions with explicit `ArrayDeque` simulate the call stack."
    ),
    mastery=[
        "Trace recursion on paper for a small input.",
        *M,
    ],
    resources=[
        bari_primary("dsa-call-stack", "3. Recursion — tracing / stack overflow"),
        lc_collection("dsa-call-stack"),
    ],
    questions=[
        q(
            "dsa-call-stack-q1",
            "What lives in one call frame?",
            ["Entire heap.", "Parameters, locals, return context for one invocation.",
             "All global variables.", "The full array."],
            "Parameters, locals, return context for one invocation.",
            "Each call is isolated until return.",
            mastery=True,
        ),
        q(
            "dsa-call-stack-q2",
            "StackOverflowError in Java usually means…",
            ["Heap full.", "Too many nested calls / infinite recursion.",
             "Array index error.", "GC failure only."],
            "Too many nested calls / infinite recursion.",
            "Call stack has a fixed limit.",
        ),
        q(
            "dsa-call-stack-q3",
            "Trace `f(3)` where f(n)=f(n-1)+1, f(0)=0. Frames at deepest point?",
            ["1", "3", "4", "0"],
            "4",
            "f(3),f(2),f(1),f(0) all active before returns.",
        ),
        q(
            "dsa-call-stack-q4",
            "Explicit stack iteration mimics…",
            ["Heap allocation.", "Call stack LIFO order.",
             "Queue FIFO.", "Sorting."],
            "Call stack LIFO order.",
            "Push frame state, pop to continue.",
        ),
        q(
            "dsa-call-stack-q5",
            "After recursive call returns, which frame runs?",
            ["Random frame.", "The caller frame below on the stack.",
             "main always.", "GC frame."],
            "The caller frame below on the stack.",
            "Return pops callee; caller resumes.",
        ),
        q(
            "dsa-call-stack-q6",
            "Space of recursion depth d with O(1) work per frame?",
            ["O(1)", "O(d)", "O(d^2)", "O(log d)"],
            "O(d)",
            "d frames stored simultaneously.",
        ),
    ],
    exercises=[
        ex(
            "dsa-call-stack-ex1",
            "Call stack trace table",
            "IMPLEMENT: `void h(int n)` printing enter/exit — run with n=3. "
            "TRACE: Table columns Frame, n, action for each push/pop. "
            "SOLVE (NeetCode 150 → Stack): Fibonacci Number — trace naive recursion depth on n=5 (teaching only). "
            "TRANSFER (internal): Explain why tail-recursive factorial still grows stack in Java (no TCO).",
        ),
    ],
)

_add(
    "dsa-recursive-trees",
    hours=1.0,
    objective="Recurse on a branching structure.",
    explanation=(
        RELEARN + " A recursion tree visualizes branching calls — each node is a subproblem. "
        "Binary recursion (two children) appears in naive Fibonacci, merge sort, tree traversals. "
        "Count nodes/leaves to estimate time. Tree problems recurse on left/right children or subtrees. "
        "Draw the tree for n≤4 before coding."
    ),
    mastery=[
        "Draw the recursion tree for a tiny input.",
        *M,
    ],
    resources=[
        bari_primary("dsa-recursive-trees", "3. Recursion — tree of calls / divide"),
        lc_collection("dsa-recursive-trees"),
    ],
    questions=[
        q(
            "dsa-recursive-trees-q1",
            "Recursion tree nodes represent…",
            ["Only leaf problems.", "Subproblem invocations (calls).",
             "Heap objects.", "Queue entries."],
            "Subproblem invocations (calls).",
            "Each call is a node; children are recursive calls.",
            mastery=True,
        ),
        q(
            "dsa-recursive-trees-q2",
            "Naive fib(5) recursion tree leaves count ≈?",
            ["5", "8", "16", "2"],
            "8",
            "Binary branching approximates 2^n leaves.",
        ),
        q(
            "dsa-recursive-trees-q3",
            "Tree traversal `visit(node)` recurses on…",
            ["Only root.", "Children subtrees after handling node/order rule.",
             "Parent only.", "Graph neighbors without base."],
            "Children subtrees after handling node/order rule.",
            "DFS on tree = recursive structure.",
        ),
        q(
            "dsa-recursive-trees-q4",
            "Merge sort recursion tree depth for n elements?",
            ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
            "O(log n)",
            "Halving until size 1.",
        ),
        q(
            "dsa-recursive-trees-q5",
            "Work at each level of merge sort tree?",
            ["O(1)", "O(n) total merge work per level.",
             "O(n^2)", "O(log n)"],
            "O(n) total merge work per level.",
            "n log n total across log n levels.",
        ),
        q(
            "dsa-recursive-trees-q6",
            "Drawing the tree helps avoid…",
            ["Using Java.", "Missing base cases and duplicate work awareness.",
             "Using arrays.", "O(n) algorithms."],
            "Missing base cases and duplicate work awareness.",
            "Visual duplicate subtrees jump out.",
        ),
    ],
    exercises=[
        ex(
            "dsa-recursive-trees-ex1",
            "Draw recursion trees",
            "IMPLEMENT: `int treeDepth(TreeNode n)` recursive. "
            "TRACE: Draw recursion trees for naive fib(4) and mergeSort on 4 elements (boxes only). "
            "SOLVE (NeetCode 150 → Stack): Maximum Depth of Binary Tree. "
            "TRANSFER (internal): Count nodes in recursion tree for `T(n)=2T(n/2)+1` — how many levels?",
        ),
    ],
)

_add(
    "dsa-recursion-to-iteration",
    hours=1.0,
    objective="Rewrite simple recursion as a loop or explicit stack.",
    explanation=(
        RELEARN + " Any recursion can use an explicit stack (`ArrayDeque`) holding frame state. "
        "Tail-style recursion (recursive call is last operation) is easiest to turn into a loop. "
        "Tree DFS iterative: push nodes; preorder pop and push children. "
        "When recursion depth risks overflow, iteration + explicit stack is the fix."
    ),
    mastery=[
        "Convert a tail-style recursion to iteration.",
        *M,
    ],
    resources=[
        bari_primary("dsa-recursion-to-iteration", "3. Recursion — converting to iteration"),
        lc_collection("dsa-recursion-to-iteration"),
    ],
    questions=[
        q(
            "dsa-recursion-to-iteration-q1",
            "Explicit stack replaces…",
            ["Heap.", "Call stack frames.",
             "Hash table.", "Sorted order."],
            "Call stack frames.",
            "You store what each frame would hold.",
            mastery=True,
        ),
        q(
            "dsa-recursion-to-iteration-q2",
            "Tail factorial loop: what variable updates?",
            ["Only n.", "Accumulator product and decreasing n.",
             "Stack size.", "Heap pointer."],
            "Accumulator product and decreasing n.",
            "Loop carries state that recursion kept in frames.",
        ),
        q(
            "dsa-recursion-to-iteration-q3",
            "Iterative preorder DFS uses stack order…",
            ["FIFO queue.", "LIFO push children (often right then left for left-first pop).",
             "Priority.", "Sort."],
            "LIFO push children (often right then left for left-first pop).",
            "Stack mimics recursive DFS.",
        ),
        q(
            "dsa-recursion-to-iteration-q4",
            "When prefer explicit stack?",
            ["Never.", "Deep trees/graphs risking stack overflow.",
             "Only for sorting.", "Only in C++."],
            "Deep trees/graphs risking stack overflow.",
            "Control memory bound on depth.",
        ),
        q(
            "dsa-recursion-to-iteration-q5",
            "Convert `void printDown(int n){ if(n>0){ print(n); printDown(n-1);} }` — iterative?",
            ["Cannot convert.", "Simple for-loop from n down to 1.",
             "Needs two stacks.", "Needs BFS."],
            "Simple for-loop from n down to 1.",
            "Not tail-recursive but linear descent = loop.",
        ),
        q(
            "dsa-recursion-to-iteration-q6",
            "ArrayDeque in iterative DFS stores…",
            ["Sorted keys.", "Nodes or frame state pending processing.",
             "Only leaves.", "Hash codes."],
            "Nodes or frame state pending processing.",
            "Each stack entry = work remaining.",
        ),
    ],
    exercises=[
        ex(
            "dsa-recursion-to-iteration-ex1",
            "Recursive DFS to iterative",
            "IMPLEMENT: Iterative preorder `List<Integer>` with `ArrayDeque<TreeNode>`. "
            "Convert tail-recursive `int sumDown(int n)` to while-loop. "
            "TRACE: Compare frame stack vs explicit stack for DFS on 3-node tree. "
            "SOLVE (NeetCode 150 → Stack): Binary Tree Inorder Traversal (iterative stack version). "
            "TRANSFER (internal): Write iterative `isPalindrome` using two indices (no recursion) — contrast with recursive.",
        ),
    ],
)

_add(
    "dsa-subsets",
    hours=1.25,
    objective="Generate subsets by choose/skip.",
    explanation=(
        RELEARN + " Backtracking template: choose → explore → unchoose. Subsets: at each index, include element or skip. "
        "Recursion tree has 2^n leaves. Java: `List<Integer> path` + `List<List<Integer>> res`. "
        "C++: same with `vector` and push_back/pop_back. Choose/explore/unchoose keeps state consistent."
    ),
    mastery=[
        "Dry-run subset recursion on a 3-element set.",
        *M,
    ],
    resources=[
        bari_primary("dsa-subsets", "4. Backtracking — subsets / power set"),
        nc150("dsa-subsets", "Backtracking"),
        lc_collection("dsa-subsets"),
    ],
    questions=[
        q(
            "dsa-subsets-q1",
            "Subset backtracking at index i typically…",
            ["Always includes a[i].", "Branches include a[i] then skip a[i].",
             "Sorts the array.", "Uses a queue."],
            "Branches include a[i] then skip a[i].",
            "Two choices per index → 2^n subsets.",
            mastery=True,
        ),
        q(
            "dsa-subsets-q2",
            "After `path.add(a[i])` and recursive call, you must…",
            ["Return immediately.", "Remove last element (unchoose) before skip branch.",
             "Clear res.", "Sort path."],
            "Remove last element (unchoose) before skip branch.",
            "Unchoose restores state for sibling branch.",
        ),
        q(
            "dsa-subsets-q3",
            "Subsets of {1,2,3} count?",
            ["6", "7", "8", "9"],
            "8",
            "2^3 = 8 including empty set.",
        ),
        q(
            "dsa-subsets-q4",
            "Time to generate all subsets of n elements?",
            ["O(n)", "O(n log n)", "O(2^n)", "O(n^2)"],
            "O(2^n)",
            "Each subset built; output size exponential.",
        ),
        q(
            "dsa-subsets-q5",
            "Where to record a complete subset?",
            ["Only at leaves.", "After each decision when pushing copy of path at each recursion entry or leaf policy.",
             "In base before any choice.", "Never copy path."],
            "After each decision when pushing copy of path at each recursion entry or leaf policy.",
            "Common: add copy of path when index reaches n.",
        ),
        q(
            "dsa-subsets-q6",
            "Common bug?",
            ["Using List.", "Adding path reference without copy — all entries share same mutating list.",
             "Using recursion.", "O(2^n) output."],
            "Adding path reference without copy — all entries share same mutating list.",
            "Use `new ArrayList<>(path)`.",
        ),
        q(
            "dsa-subsets-q7",
            "C++ unchoose equivalent?",
            ["path.clear()", "path.pop_back() after return.",
             "delete path", "stack.top()"],
            "path.pop_back() after return.",
            "Removes chosen element for sibling exploration.",
        ),
        q(
            "dsa-subsets-q8",
            "Subsets II (duplicates) requires…",
            ["More stacks.", "Skip duplicate branches after sorting equal elements.",
             "BFS.", "Binary search."],
            "Skip duplicate branches after sorting equal elements.",
            "Avoid duplicate subsets when equal values repeat.",
        ),
    ],
    exercises=[
        ex(
            "dsa-subsets-ex1",
            "Subsets backtracking",
            "IMPLEMENT: `List<List<Integer>> subsets(int[] a)` with choose/skip at each index; copy path when index==n. "
            "TRACE: Full tree for [1,2] labeling include/skip branches. "
            "SOLVE (NeetCode 150 → Backtracking): Subsets, Subsets II. "
            "TRANSFER (internal): Generate all binary strings of length 3 (same 2-branch backtracking).",
        ),
    ],
)

_add(
    "dsa-permutations",
    hours=1.25,
    objective="Generate permutations by swapping or used-flags.",
    explanation=(
        RELEARN + " Permutations: order matters. Swap-based: swap(i,j) explore swap back. "
        "Used-flag: build path, mark used[i], recurse, unmark. n! leaves. "
        "Backtracking: choose unused element → explore → unchoose. Trace n=3 fully before coding."
    ),
    mastery=[
        "Dry-run permutation search on 3 items.",
        *M,
    ],
    resources=[
        bari_primary("dsa-permutations", "4. Backtracking — permutations"),
        nc150("dsa-permutations", "Backtracking"),
        lc_collection("dsa-permutations"),
    ],
    questions=[
        q(
            "dsa-permutations-q1",
            "Permutations of n distinct items count?",
            ["n", "2^n", "n!", "n^2"],
            "n!",
            "First position n choices, then n-1, etc.",
            mastery=True,
        ),
        q(
            "dsa-permutations-q2",
            "Used-array approach at each level…",
            ["Picks any element regardless of use.",
             "Picks an index not yet used, marks used, recurses, unmarks.",
             "Only swaps.", "Uses queue."],
            "Picks an index not yet used, marks used, recurses, unmarks.",
            "Choose/explore/unchoose on availability.",
        ),
        q(
            "dsa-permutations-q3",
            "Swap-based permutations: after `swap(i,j)` recurse, then…",
            ["swap(i,j) again to undo.", "clear array.", "sort.", "return without undo."],
            "swap(i,j) again to undo.",
            "Unchoose restores array for other branches.",
        ),
        q(
            "dsa-permutations-q4",
            "Time to generate all permutations?",
            ["O(n)", "O(n!)", "O(2^n)", "O(n log n)"],
            "O(n!)",
            "n! permutations, often O(n) work per output.",
        ),
        q(
            "dsa-permutations-q5",
            "Permutations vs subsets branching factor?",
            ["Same.", "Permutations shrink available set; subsets always 2 branches.",
             "Subsets larger.", "Permutations use BFS."],
            "Permutations shrink available set; subsets always 2 branches.",
            "Different search trees.",
        ),
        q(
            "dsa-permutations-q6",
            "When path size equals n, you…",
            ["Continue recursing.", "Record copy of path as complete permutation.",
             "Reset used[] all true.", "Sort path."],
            "Record copy of path as complete permutation.",
            "Full length = one permutation found.",
        ),
        q(
            "dsa-permutations-q7",
            "Permutations with duplicates fix?",
            ["Ignore.", "Sort + skip same value at same recursion depth.",
             "Use Stack.", "Use heap."],
            "Sort + skip same value at same recursion depth.",
            "Same idea as subsets II.",
        ),
        q(
            "dsa-permutations-q8",
            "Space excluding output?",
            ["O(1)", "O(n) for path + used + recursion depth.",
             "O(n!)", "O(n^2)"],
            "O(n) for path + used + recursion depth.",
            "Depth n, auxiliary arrays size n.",
        ),
    ],
    exercises=[
        ex(
            "dsa-permutations-ex1",
            "Permutations backtracking",
            "IMPLEMENT: `List<List<Integer>> permute(int[] a)` with boolean[] used. "
            "TRACE: Tree for [1,2,3] first two levels with chosen order. "
            "SOLVE (NeetCode 150 → Backtracking): Permutations, Permutations II. "
            "TRANSFER (internal): List all 3-letter words from letters A,B,C without repeat (same search).",
        ),
    ],
)

_add(
    "dsa-combinations",
    hours=1.0,
    objective="Generate combinations with an index cursor.",
    explanation=(
        RELEARN + " Combinations: choose k from n, order irrelevant. Use start index to avoid duplicate sets. "
        "Only consider j ≥ start when adding. When path size==k, record. "
        "Contrast: permutations care about order; combinations do not. C++: `vector<int> path` same pattern."
    ),
    mastery=[
        "Contrast combinations vs permutations.",
        *M,
    ],
    resources=[
        bari_primary("dsa-combinations", "4. Backtracking — combinations / n choose k"),
        nc150("dsa-combinations", "Backtracking"),
        lc_collection("dsa-combinations"),
    ],
    questions=[
        q(
            "dsa-combinations-q1",
            "Combinations differ from permutations because…",
            ["They use stacks.", "Order of selection does not matter.",
             "They are O(n).", "They need sorting."],
            "Order of selection does not matter.",
            "[1,2] and [2,1] are same combination.",
            mastery=True,
        ),
        q(
            "dsa-combinations-q2",
            "Start index prevents…",
            ["Recursion.", "Reusing smaller indices and duplicate combos like {2,1} vs {1,2}.",
             "Base case.", "Output."],
            "Reusing smaller indices and duplicate combos like {2,1} vs {1,2}.",
            "Only forward indices keep increasing order.",
        ),
        q(
            "dsa-combinations-q3",
            "C(n,k) count?",
            ["n!", "n^k", "n!/(k!(n-k)!)", "2^n"],
            "n!/(k!(n-k)!)",
            "Binomial coefficient.",
        ),
        q(
            "dsa-combinations-q4",
            "Base for choose-k?",
            ["path.size()==n always.", "path.size()==k record; or start==n stop.",
             "k==0 only.", "never base."],
            "path.size()==k record; or start==n stop.",
            "Stop when picked k elements.",
        ),
        q(
            "dsa-combinations-q5",
            "Combination Sum allows reuse when…",
            ["Always.", "Problem says elements may be reused — recurse with same start index.",
             "Never.", "Only with BFS."],
            "Problem says elements may be reused — recurse with same start index.",
            "NeetCode Combination Sum II forbids reuse — use start+1.",
        ),
        q(
            "dsa-combinations-q6",
            "Prune when remaining elements cannot fill k?",
            ["Never prune.", "If n-start < k-needed, return early.",
             "Always sort.", "Use binary search."],
            "If n-start < k-needed, return early.",
            "Standard combination prune.",
        ),
        q(
            "dsa-combinations-q7",
            "Time worst case generating C(n,k)?",
            ["O(n)", "O(C(n,k)) output driven.", "O(n!)", "O(log n)"],
            "O(C(n,k)) output driven.",
            "Proportional to number of combinations.",
        ),
        q(
            "dsa-combinations-q8",
            "Loop j from start to n-1 in combinations is…",
            ["BFS.", "Choosing each candidate index into path then backtracking.",
             "Sorting.", "Heapify."],
            "Choosing each candidate index into path then backtracking.",
            "Choose j, explore, unchoose.",
        ),
    ],
    exercises=[
        ex(
            "dsa-combinations-ex1",
            "Combinations choose-k",
            "IMPLEMENT: `List<List<Integer>> combine(int n, int k)` with start cursor. "
            "TRACE: List combos for n=4,k=2 in increasing order. "
            "SOLVE (NeetCode 150 → Backtracking): Combination Sum, Combination Sum II. "
            "TRANSFER (internal): Choose 2 teammates from 5 people {A..E} — list pairs (same math).",
        ),
    ],
)

_add(
    "dsa-constraint-search",
    hours=1.25,
    objective="Prune when a partial assignment cannot work.",
    explanation=(
        RELEARN + " Backtracking as constraint search: assign choices; if partial violates constraints, prune — "
        "do not explore descendants. Examples: N-Queens (no two queens attack), Sudoku, word search. "
        "choose/explore/unchoose + early return when invalid. No solver libraries — implement prune logic yourself."
    ),
    mastery=[
        "State one prune condition for a tiny puzzle.",
        *M,
    ],
    resources=[
        bari_primary("dsa-constraint-search", "4. Backtracking — N-Queens / pruning"),
        nc150("dsa-constraint-search", "Backtracking"),
        lc_collection("dsa-constraint-search"),
    ],
    questions=[
        q(
            "dsa-constraint-search-q1",
            "Pruning means…",
            ["Deleting the array.", "Abandoning a partial branch that cannot lead to valid solution.",
             "Sorting first.", "Using more memory."],
            "Abandoning a partial branch that cannot lead to valid solution.",
            "Cut search tree early.",
            mastery=True,
        ),
        q(
            "dsa-constraint-search-q2",
            "N-Queens: before placing queen in row r, check…",
            ["Only row.", "Column and diagonals for conflicts with prior rows.",
             "Nothing.", "Heap property."],
            "Column and diagonals for conflicts with prior rows.",
            "Invalid partial → prune.",
        ),
        q(
            "dsa-constraint-search-q3",
            "Word Search on grid: unchoose step?",
            ["Delete cell.", "Mark visited then unmark after recursion.",
             "Sort grid.", "Pop heap."],
            "Mark visited then unmark after recursion.",
            "Restore cell state for other paths.",
        ),
        q(
            "dsa-constraint-search-q4",
            "Without pruning, N-Queens explores…",
            ["O(n)", "O(n!) placements roughly.", "O(n^2)", "O(1)"],
            "O(n!) placements roughly.",
            "Pruning cuts massive branches.",
        ),
        q(
            "dsa-constraint-search-q5",
            "Generate Parentheses prune when…",
            ["open < 0.", "open < close or open > n/2.",
             "always prune.", "never prune."],
            "open < close or open > n/2.",
            "Invalid prefix — more closes than opens or too many opens.",
        ),
        q(
            "dsa-constraint-search-q6",
            "Constraint search vs blind subsets?",
            ["Same.", "Constraint checks reduce branches before exploring children.",
             "Constraint uses queue.", "Subsets use prune only."],
            "Constraint checks reduce branches before exploring children.",
            "Validity function is the difference.",
        ),
        q(
            "dsa-constraint-search-q7",
            "Sudoku: try digit 1-9 in cell, if invalid…",
            ["Continue all 9.", "Prune — try next digit or return false.",
             "Clear board.", "Sort row."],
            "Prune — try next digit or return false.",
            "Standard backtracking search.",
        ),
        q(
            "dsa-constraint-search-q8",
            "Palindrome Partitioning prune idea?",
            ["Always partition.", "Only extend if current substring is palindrome.",
             "Use stack only.", "Binary search."],
            "Only extend if current substring is palindrome.",
            "Invalid segment — skip extension.",
        ),
    ],
    exercises=[
        ex(
            "dsa-constraint-search-ex1",
            "Constraint backtracking",
            "IMPLEMENT: `List<String> generateParenthesis(int n)` with open/close counters and prune. "
            "TRACE: Prune points for n=3 on first 3 levels. "
            "SOLVE (NeetCode 150 → Backtracking): Generate Parentheses, N-Queens, Word Search. "
            "TRANSFER (internal): 4×4 grid place 2 non-attacking rooks (row/col prune — simpler than N-Queens).",
        ),
    ],
)

_add(
    "dsa-bubble-sort",
    hours=0.5,
    objective="Explain bubble sort and its cost.",
    explanation=(
        RELEARN + " Bubble sort: repeated passes swapping adjacent out-of-order pairs. "
        "Largest elements 'bubble' to end. Teaching sort — O(n^2); not production default. "
        "Implement once in Java to see in-place swapping. C++: same loop structure."
    ),
    mastery=[
        "Dry-run bubble sort on 5 elements.",
        *M,
    ],
    resources=[
        bari_primary("dsa-bubble-sort", "2.7 Sorting — bubble sort"),
        mit_dd("dsa-bubble-sort", "MIT 6.006 — Sets and Sorting", MIT_L3),
        lc_collection("dsa-bubble-sort"),
    ],
    questions=[
        q(
            "dsa-bubble-sort-q1",
            "Bubble sort compares and swaps…",
            ["Random pairs.", "Adjacent elements each pass.",
             "Only first and last.", "Using a heap."],
            "Adjacent elements each pass.",
            "Swap neighbors if wrong order.",
            mastery=True,
        ),
        q(
            "dsa-bubble-sort-q2",
            "Worst-case time on n elements?",
            ["O(n)", "O(n log n)", "O(n^2)", "O(1)"],
            "O(n^2)",
            "n passes × n comparisons.",
        ),
        q(
            "dsa-bubble-sort-q3",
            "After one complete pass on arbitrary input, what is guaranteed?",
            ["Fully sorted.", "Largest element at last index.",
             "Smallest at front always.", "Nothing."],
            "Largest element at last index.",
            "Bubbles max to end.",
        ),
        q(
            "dsa-bubble-sort-q4",
            "Space complexity?",
            ["O(n)", "O(log n)", "O(1) extra", "O(n^2)"],
            "O(1) extra",
            "In-place swaps only.",
        ),
        q(
            "dsa-bubble-sort-q5",
            "Why not default in production?",
            ["Not in-place.", "O(n^2) vs O(n log n) library sorts.",
             "Not stable.", "Uses recursion."],
            "O(n^2) vs O(n log n) library sorts.",
            "Teaching and tiny n only.",
        ),
    ],
    exercises=[
        ex(
            "dsa-bubble-sort-ex1",
            "Bubble sort dry-run",
            "IMPLEMENT: `void bubbleSort(int[] a)` in Java. "
            "TRACE: Full pass trace on [5,1,4,2,8] until sorted. "
            "SOLVE: No NeetCode requirement — compare output with `Arrays.sort` on random small array. "
            "TRANSFER (internal): One pass only — which index holds max after one pass on [3,1,4,2]?",
        ),
    ],
)

_add(
    "dsa-selection-sort",
    hours=0.5,
    objective="Explain selection sort and its cost.",
    explanation=(
        RELEARN + " Selection sort: for each position i, select minimum from i..n-1 and swap into i. "
        "O(n^2) comparisons; O(n) swaps. Teaching sort. Trace minimum index each outer step."
    ),
    mastery=[
        "Dry-run selection sort on 5 elements.",
        *M,
    ],
    resources=[
        bari_primary("dsa-selection-sort", "2.7 Sorting — selection sort"),
        mit_dd("dsa-selection-sort", "MIT 6.006 — Sets and Sorting", MIT_L3),
        lc_collection("dsa-selection-sort"),
    ],
    questions=[
        q(
            "dsa-selection-sort-q1",
            "Selection sort each outer i…",
            ["Inserts random element.", "Finds min of suffix and swaps to i.",
             "Merges halves.", "Uses pivot."],
            "Finds min of suffix and swaps to i.",
            "Repeated minimum selection.",
            mastery=True,
        ),
        q(
            "dsa-selection-sort-q2",
            "Comparison count roughly?",
            ["O(n)", "O(n^2)", "O(n log n)", "O(1)"],
            "O(n^2)",
            "n outer × n inner scan.",
        ),
        q(
            "dsa-selection-sort-q3",
            "Swap count at most?",
            ["O(n^2)", "O(n)", "O(1)", "O(n log n)"],
            "O(n)",
            "One swap per outer position.",
        ),
        q(
            "dsa-selection-sort-q4",
            "After outer i completes, prefix 0..i is…",
            ["Unsorted.", "Sorted and final.",
             "Empty.", "Heap."],
            "Sorted and final.",
            "Min of remaining placed at i.",
        ),
        q(
            "dsa-selection-sort-q5",
            "Stable?",
            ["Always stable.", "Generally not stable (long-distance swaps).",
             "Stable if using queue.", "Stable if n<10."],
            "Generally not stable (long-distance swaps).",
            "Swap can move equal elements past each other.",
        ),
    ],
    exercises=[
        ex(
            "dsa-selection-sort-ex1",
            "Selection sort implement",
            "IMPLEMENT: `void selectionSort(int[] a)`. "
            "TRACE: Record min index each outer step on [7,2,9,1]. "
            "SOLVE: Verify with small array vs `Arrays.sort`. "
            "TRANSFER (internal): Manual selection — pick 3 smallest cards from 5 face-up (same idea).",
        ),
    ],
)

_add(
    "dsa-insertion-sort",
    hours=1.0,
    objective="Explain insertion sort and when it is useful.",
    explanation=(
        RELEARN + " Insertion sort: grow sorted prefix by inserting each element into correct position "
        "(shift larger right). O(n^2) worst; good on nearly sorted data O(n). Stable. "
        "Implement in Java via Core Skills. C++: same inner while shift."
    ),
    mastery=[
        "Dry-run insertion sort on 5 elements.",
        *M,
    ],
    resources=[
        bari_primary("dsa-insertion-sort", "2.7 Sorting — insertion sort"),
        nccore("dsa-insertion-sort", "Insertion Sort"),
        mit_dd("dsa-insertion-sort", "MIT 6.006 — Sets and Sorting", MIT_L3),
        lc_collection("dsa-insertion-sort"),
    ],
    questions=[
        q(
            "dsa-insertion-sort-q1",
            "Insertion sort maintains…",
            ["Heap property.", "Sorted prefix left of index i.",
             "Two sorted halves.", "Queue order."],
            "Sorted prefix left of index i.",
            "Insert a[i] into sorted a[0..i-1].",
            mastery=True,
        ),
        q(
            "dsa-insertion-sort-q2",
            "Nearly sorted array time?",
            ["O(n^2) always", "O(n) when few shifts per insert.",
             "O(log n)", "O(1)"],
            "O(n) when few shifts per insert.",
            "Each element shifts few positions.",
        ),
        q(
            "dsa-insertion-sort-q3",
            "Stable?",
            ["No", "Yes — equal elements not crossed by insert.",
             "Only for ints", "Only stable sort"],
            "Yes — equal elements not crossed by insert.",
            "Insert stops at equal without shifting past.",
        ),
        q(
            "dsa-insertion-sort-q4",
            "Inner loop does…",
            ["Swap random.", "Shift larger elements right until slot for key.",
             "Partition.", "Merge runs."],
            "Shift larger elements right until slot for key.",
            "Classic insertion step.",
        ),
        q(
            "dsa-insertion-sort-q5",
            "Worst-case comparisons?",
            ["O(n)", "O(n^2)", "O(n log n)", "O(1)"],
            "O(n^2)",
            "Reverse sorted forces max shifts.",
        ),
        q(
            "dsa-insertion-sort-q6",
            "When practical over merge/quick?",
            ["Huge n always.", "Very small n or nearly sorted tiny arrays.",
             "Never.", "Only linked lists always."],
            "Very small n or nearly sorted tiny arrays.",
            "Simplicity wins at small scale.",
        ),
    ],
    exercises=[
        ex(
            "dsa-insertion-sort-ex1",
            "Insertion sort Core Skills",
            "IMPLEMENT: `void insertionSort(int[] a)` — match NeetCode Core Skills Insertion Sort. "
            "TRACE: Shift arrows on [3,1,4,2] for each i. "
            "SOLVE: NeetCode Core Skills Insertion Sort implementation check. "
            "TRANSFER (internal): Insert one card into sorted hand of 4 cards — count shifts.",
        ),
    ],
)

_add(
    "dsa-merge-sort",
    hours=1.5,
    objective="Explain divide-and-conquer merge sort.",
    explanation=(
        RELEARN + " Merge sort: split in half, sort halves recursively, merge two sorted runs in O(n). "
        "Stable O(n log n). Trace merge of [1,4] and [2,3]. Implement in Java — Core Skills Merge Sort. "
        "MIT 6.006 Lecture 3 deep dive. C++: same recursive structure; watch extra merge buffer space."
    ),
    mastery=[
        "Trace merge on two sorted runs.",
        *M,
    ],
    resources=[
        bari_primary("dsa-merge-sort", "2.8 Merge Sort / divide and conquer"),
        nccore("dsa-merge-sort", "Merge Sort"),
        mit_dd("dsa-merge-sort", "MIT 6.006 — Sets and Sorting", MIT_L3),
        lc_collection("dsa-merge-sort"),
    ],
    questions=[
        q(
            "dsa-merge-sort-q1",
            "Merge sort combine step time for two halves totaling n?",
            ["O(1)", "O(n)", "O(n^2)", "O(log n)"],
            "O(n)",
            "Each element moved once in merge.",
            mastery=True,
        ),
        q(
            "dsa-merge-sort-q2",
            "Overall time?",
            ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"],
            "O(n log n)",
            "log n levels × O(n) merge per level.",
        ),
        q(
            "dsa-merge-sort-q3",
            "Typical extra space?",
            ["O(1)", "O(n) auxiliary array for merge.",
             "O(n^2)", "O(log n) only always."],
            "O(n) auxiliary array for merge.",
            "Temporary buffer for merged output.",
        ),
        q(
            "dsa-merge-sort-q4",
            "Stable?",
            ["No", "Yes — take left when equal in merge.",
             "Only on ints", "Never"],
            "Yes — take left when equal in merge.",
            "Left copy preserved before right equal.",
        ),
        q(
            "dsa-merge-sort-q5",
            "Recursion tree depth?",
            ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
            "O(log n)",
            "Halving until size 1.",
        ),
        q(
            "dsa-merge-sort-q6",
            "Merge [1,5,9] and [2,3,8] first three output elements?",
            ["1,2,3", "1,5,9", "2,3,8", "9,8,5"],
            "1,2,3",
            "Compare fronts: 1,2,3 next.",
        ),
        q(
            "dsa-merge-sort-q7",
            "vs quicksort worst time?",
            ["Merge worse always.", "Merge guarantees O(n log n); quicksort can O(n^2).",
             "Same always.", "Merge is O(n^2)."],
            "Merge guarantees O(n log n); quicksort can O(n^2).",
            "Trade-off: merge uses more memory.",
        ),
        q(
            "dsa-merge-sort-q8",
            "Bottom-up merge sort avoids…",
            ["Merging.", "Recursive call stack depth.",
             "O(n log n) time.", "Stability."],
            "Recursive call stack depth.",
            "Iterative with increasing run lengths.",
        ),
    ],
    exercises=[
        ex(
            "dsa-merge-sort-ex1",
            "Merge sort implement",
            "IMPLEMENT: `void mergeSort(int[] a)` with helper merge — NeetCode Core Skills Merge Sort. "
            "TRACE: Full merge steps for halves [38,27,43] and [3,9,10]. "
            "SOLVE: Core Skills Merge Sort + NeetCode 150 Sort Colors (merge/partition thinking). "
            "TRANSFER (internal): Merge two sorted exam score lists on paper — 6 total elements.",
        ),
    ],
)

_add(
    "dsa-quick-sort",
    hours=1.5,
    objective="Explain quicksort and pivot partitioning.",
    explanation=(
        RELEARN + " Quicksort: pick pivot, partition so ≤ pivot left, > pivot right, recurse on sides. "
        "Average O(n log n); worst O(n^2) bad pivot. Not stable by typical partition. "
        "PRIMARY: Abdul Bari verified quicksort video. Implement via Core Skills Quick Sort. "
        "Trace one partition step on paper before coding."
    ),
    mastery=[
        "Trace one partition step.",
        *M,
    ],
    resources=[
        bari_video("dsa-quick-sort", "Abdul Bari — QuickSort Algorithm", BARI_QUICK),
        nccore("dsa-quick-sort", "Quick Sort"),
        mit_dd("dsa-quick-sort", "MIT 6.006 — Sets and Sorting", MIT_L3),
        lc_collection("dsa-quick-sort"),
    ],
    questions=[
        q(
            "dsa-quick-sort-q1",
            "After partition around pivot p…",
            ["Pivot at random index always.", "Elements left ≤ p (or < per variant), right > p.",
             "Array sorted.", "Two sorted halves only."],
            "Elements left ≤ p (or < per variant), right > p.",
            "Pivot in final partition position.",
            mastery=True,
        ),
        q(
            "dsa-quick-sort-q2",
            "Average time?",
            ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"],
            "O(n log n)",
            "Balanced partitions ≈ halving.",
        ),
        q(
            "dsa-quick-sort-q3",
            "Worst case when…",
            ["Random pivot always.", "Pivot always min or max — unbalanced partitions.",
             "Array sorted ascending with good pivot.", "n is prime."],
            "Pivot always min or max — unbalanced partitions.",
            "n-1 + n-2 + … = O(n^2).",
        ),
        q(
            "dsa-quick-sort-q4",
            "Typical in-place partition extra space?",
            ["O(n)", "O(log n) stack average", "O(1) besides recursion stack",
             "O(n^2)"],
            "O(1) besides recursion stack",
            "Partition with pointers; stack O(log n) average.",
        ),
        q(
            "dsa-quick-sort-q5",
            "Stable typical Lomuto/Hoare partition?",
            ["Always stable.", "Generally not stable.",
             "Stable if ints.", "Stable if merge first."],
            "Generally not stable.",
            "Swaps can move equals across pivot.",
        ),
        q(
            "dsa-quick-sort-q6",
            "Partition [3,1,4,2] pivot=3 (Lomuto style) — pivot final index?",
            ["0", "1", "2", "3"],
            "2",
            "Typical Lomuto places pivot at partition index 2 for this trace.",
        ),
        q(
            "dsa-quick-sort-q7",
            "Randomized pivot helps…",
            ["Guarantee stability.", "Avoid worst cases on structured bad inputs.",
             "Reduce to O(n).", "Eliminate recursion."],
            "Avoid worst cases on structured bad inputs.",
            "Expected balanced split.",
        ),
        q(
            "dsa-quick-sort-q8",
            "vs merge sort on memory?",
            ["Quick uses more.", "Quick in-place partition; merge needs O(n) buffer.",
             "Equal always.", "Merge uses O(1)."],
            "Quick in-place partition; merge needs O(n) buffer.",
            "Trade-off: quick worst time vs merge memory.",
        ),
    ],
    exercises=[
        ex(
            "dsa-quick-sort-ex1",
            "Quick sort partition",
            "IMPLEMENT: `void quickSort(int[] a)` with partition — NeetCode Core Skills Quick Sort. "
            "TRACE: Lomuto partition on [8,3,1,7,0,10,2] with last-element pivot — show i,j swaps. "
            "SOLVE: Core Skills Quick Sort + NeetCode 150 Kth Largest Element in an Array (quickselect idea). "
            "TRANSFER (internal): Partition names by first letter with pivot 'M' — count before/after pivot.",
        ),
    ],
)

_add(
    "dsa-heap-sort",
    hours=1.0,
    objective="Explain heapsort at a conceptual level.",
    explanation=(
        RELEARN + " Heapsort: build max-heap, repeatedly extract max to end and heapify — O(n log n), not stable. "
        "This topic appears before the full heap module: heapsort is the sorting application; "
        "the heap module deepens heapify, PriorityQueue, and top-k. "
        "Abdul Bari heap/heapsort video (BARI_HEAP) ties build-heap and extract. "
        "Java `PriorityQueue` is different API — heapsort is array-based heap in-place."
    ),
    mastery=[
        "Relate heapsort to the heap structure.",
        *M,
    ],
    resources=[
        bari_primary("dsa-heap-sort", "2.6 Heap / HeapSort overview"),
        r(
            "dsa-heap-sort-bari-heap",
            "Abdul Bari — Heap, HeapSort, Heapify, Priority Queue",
            BARI_HEAP,
            "Abdul Bari",
            "DEEP_DIVE",
            "youtube_video",
            1,
            "Official Abdul Bari video (author verified via YouTube oEmbed). Deepens build-heap and extract before the heap module.",
        ),
        mit_dd("dsa-heap-sort", "MIT 6.006 — Binary Heaps", MIT_L8),
        lc_collection("dsa-heap-sort"),
    ],
    questions=[
        q(
            "dsa-heap-sort-q1",
            "Heapsort first phase…",
            ["Merge halves.", "Build max-heap on array.",
             "Bubble passes.", "Sort with queue."],
            "Build max-heap on array.",
            "Heap property enables extract-max.",
            mastery=True,
        ),
        q(
            "dsa-heap-sort-q2",
            "Time complexity?",
            ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"],
            "O(n log n)",
            "n extract-max × O(log n) heapify.",
        ),
        q(
            "dsa-heap-sort-q3",
            "Space if in-place heapify?",
            ["O(n) extra always.", "O(1) extra besides heap in array.",
             "O(n^2)", "O(log n) queue."],
            "O(1) extra besides heap in array.",
            "Array stores heap; swap to end.",
        ),
        q(
            "dsa-heap-sort-q4",
            "Stable?",
            ["Yes always.", "No — swapping distant elements.",
             "Yes if ints.", "Yes with PriorityQueue."],
            "No — swapping distant elements.",
            "Equal keys can reorder.",
        ),
        q(
            "dsa-heap-sort-q5",
            "Relation to later heap module?",
            ["Unrelated.", "Same heapify/extract logic deepened with PQ and top-k.",
             "Heap module replaces heapsort.", "Only trees."],
            "Same heapify/extract logic deepened with PQ and top-k.",
            "Preview here; module adds operations.",
        ),
        q(
            "dsa-heap-sort-q6",
            "Build-heap from array is O(n) or O(n log n)?",
            ["O(n)", "O(n log n)", "O(n^2)", "O(1)"],
            "O(n)",
            "Bottom-up heapify analysis — Bari/MIT deepen later.",
        ),
    ],
    exercises=[
        ex(
            "dsa-heap-sort-ex1",
            "Heapsort concept trace",
            "IMPLEMENT: `void heapify(int[] a, int n, int i)` and outline `heapSort` (or trace Bari video pseudocode). "
            "TRACE: Build-heap + two extract steps on [4,10,3,5,1]. "
            "SOLVE: Watch BARI_HEAP for extract loop; NeetCode 150 Sort an Array (conceptual — library sort OK for check). "
            "TRANSFER (internal): Explain why child indices in array heap are 2i+1 and 2i+2.",
        ),
    ],
)

_add(
    "dsa-counting-radix",
    hours=1.0,
    objective="Explain non-comparison sorts at V1 depth.",
    explanation=(
        RELEARN + " Counting sort: tally frequencies for bounded integer keys, reconstruct sorted order — O(n+k). "
        "Radix sort: stable digit passes (often counting sort per digit). Not comparison-based; "
        "requires key structure (bounded range / digits). MIT Lecture 5 linear sorting deepens. "
        "Not default interview implementation unless asked."
    ),
    mastery=[
        "State when counting sort applies.",
        *M,
    ],
    resources=[
        bari_primary("dsa-counting-radix", "2.9 Counting / Radix sort"),
        mit_dd("dsa-counting-radix-l3", "MIT 6.006 — Sets and Sorting", MIT_L3),
        mit_dd("dsa-counting-radix-l5", "MIT 6.006 — Linear Sorting", MIT_L5),
        lc_collection("dsa-counting-radix"),
    ],
    questions=[
        q(
            "dsa-counting-radix-q1",
            "Counting sort needs…",
            ["Floating keys only.", "Bounded integer key range k.",
             "Comparison only.", "Heap property."],
            "Bounded integer key range k.",
            "Array size k for frequencies.",
            mastery=True,
        ),
        q(
            "dsa-counting-radix-q2",
            "Counting sort time?",
            ["O(n^2)", "O(n+k)", "O(n log n)", "O(k^2)"],
            "O(n+k)",
            "Count n elements, scan k buckets.",
        ),
        q(
            "dsa-counting-radix-q3",
            "Radix sort processes…",
            ["One random pivot.", "Digits/characters in stable passes.",
             "Heap levels.", "Graph edges."],
            "Digits/characters in stable passes.",
            "Each pass sorts by one digit.",
        ),
        q(
            "dsa-counting-radix-q4",
            "Why stable digit pass matters for radix?",
            ["Speed only.", "Prior digit order preserved within equal current digit.",
             "Memory.", "Not needed."],
            "Prior digit order preserved within equal current digit.",
            "Multi-digit correctness depends on stability.",
        ),
        q(
            "dsa-counting-radix-q5",
            "When NOT use counting sort?",
            ["Small k.", "Huge sparse key universe with few elements.",
             "n=100.", "All positive ints."],
            "Huge sparse key universe with few elements.",
            "k dominates — wasteful array.",
        ),
        q(
            "dsa-counting-radix-q6",
            "Comparison sort lower bound?",
            ["O(n)", "Ω(n log n) for general comparison sorts.",
             "O(n^2)", "O(1)"],
            "Ω(n log n) for general comparison sorts.",
            "Linear sorts bypass by using key structure.",
        ),
    ],
    exercises=[
        ex(
            "dsa-counting-radix-ex1",
            "Counting sort trace",
            "IMPLEMENT: `void countingSort(int[] a, int k)` for non-negative keys < k. "
            "TRACE: Frequencies and output positions for [2,0,2,1,0,1]. "
            "SOLVE: Read MIT_L5 linear sorting section — no invented URLs. "
            "TRANSFER (internal): Sort 5 student IDs known to be 0..50 using tally array.",
        ),
    ],
)

_add(
    "dsa-sort-stability",
    hours=0.5,
    objective="Define stable sorting.",
    explanation=(
        RELEARN + " Stable sort: equal keys retain original relative order. "
        "Matters when sorting by multiple criteria (sort by name then grade) or satellite data. "
        "Merge sort stable; quicksort/heapsort typically not; insertion stable; Java `Arrays.sort` on objects is stable (TimSort)."
    ),
    mastery=[
        "Give one case where stability matters.",
        *M,
    ],
    resources=[
        bari_primary("dsa-sort-stability", "2.7 Sorting — stability concept"),
        mit_dd("dsa-sort-stability", "MIT 6.006 — Sets and Sorting", MIT_L3),
        lc_collection("dsa-sort-stability"),
    ],
    questions=[
        q(
            "dsa-sort-stability-q1",
            "Stable sort means…",
            ["O(n log n).", "Equal keys keep input relative order.",
             "Uses O(1) space.", "Never swaps."],
            "Equal keys keep input relative order.",
            "Ties not rearranged arbitrarily.",
            mastery=True,
        ),
        q(
            "dsa-sort-stability-q2",
            "Which is stable?",
            ["Merge sort", "Heap sort", "Selection sort", "Quick sort typical"],
            "Merge sort",
            "Merge takes left equal first.",
        ),
        q(
            "dsa-sort-stability-q3",
            "Sort students by grade then name needs…",
            ["One unstable sort.", "Stable sort by name after grade (or compound key).",
             "Heap only.", "Radix only."],
            "Stable sort by name after grade (or compound key).",
            "Stability preserves name order within grade.",
        ),
        q(
            "dsa-sort-stability-q4",
            "Insertion sort stable?",
            ["No", "Yes", "Only on doubles", "Unknown"],
            "Yes",
            "Shifts stop before equal element.",
        ),
        q(
            "dsa-sort-stability-q5",
            "Why merge preferred when equal keys must keep order?",
            ["Faster always.", "Stable O(n log n) guarantee.",
             "O(1) space.", "No recursion."],
            "Stable O(n log n) guarantee.",
            "Library TimSort inherits merge ideas.",
        ),
    ],
    exercises=[
        ex(
            "dsa-sort-stability-ex1",
            "Stability demo",
            "IMPLEMENT: Sort `Pair(int key,String tag)` array twice: unstable quicksort partition vs stable mergesort on key — "
            "print tags to see order preserved. "
            "TRACE: [(1,a),(1,b),(2,c)] by key — stable vs unstable tag order. "
            "SOLVE: Explain one multi-key sort scenario from work or exams. "
            "TRANSFER (internal): Sort spreadsheet rows by department then salary — which sorts must be stable?",
        ),
    ],
)

_add(
    "dsa-sort-complexity",
    hours=0.75,
    objective="Compare common sorts by time, space, and stability.",
    explanation=(
        RELEARN + " Fill comparison table from memory: bubble/selection/insertion O(n^2); merge O(n log n) stable O(n) space; "
        "quick average O(n log n) worst O(n^2) in-place; heap O(n log n) not stable; counting O(n+k). "
        "Production Java/C++: prefer library sort (`Arrays.sort`, `std::sort`) unless implementing for learning/interview."
    ),
    mastery=[
        "Fill a comparison table from memory.",
        *M,
    ],
    resources=[
        bari_primary("dsa-sort-complexity", "2.7–2.8 Sorting complexity comparison"),
        mit_dd("dsa-sort-complexity", "MIT 6.006 — Sets and Sorting", MIT_L3),
        lc_collection("dsa-sort-complexity"),
    ],
    questions=[
        q(
            "dsa-sort-complexity-q1",
            "Only stable O(n log n) typical comparison sort listed?",
            ["Quick sort", "Merge sort", "Heap sort", "Selection sort"],
            "Merge sort",
            "Quick/heap standard forms unstable.",
            mastery=True,
        ),
        q(
            "dsa-sort-complexity-q2",
            "Worst O(n^2) among these?",
            ["Merge", "Quick sort bad pivots", "Heap", "Counting with small k"],
            "Quick sort bad pivots",
            "Merge/heap guarantee n log n.",
        ),
        q(
            "dsa-sort-complexity-q3",
            "Extra O(n) space typical?",
            ["Bubble", "Merge sort merge buffer", "Heap sort in-place", "Insertion"],
            "Merge sort merge buffer",
            "Temporary array for merge.",
        ),
        q(
            "dsa-sort-complexity-q4",
            "Production Java sort for `int[]`?",
            ["Hand bubble.", "Arrays.sort (dual-pivot quicksort/TimSort variants).",
             "Only insertion.", "Never sort."],
            "Arrays.sort (dual-pivot quicksort/TimSort variants).",
            "Implement for learning; library for production.",
        ),
        q(
            "dsa-sort-complexity-q5",
            "Nearly sorted small array — reasonable teaching choice?",
            ["Heap sort", "Insertion sort", "Counting with huge k", "Radix on floats"],
            "Insertion sort",
            "O(n) behavior on nearly sorted.",
        ),
        q(
            "dsa-sort-complexity-q6",
            "Comparison sorts cannot beat O(n log n) when…",
            ["Keys are integers.", "General comparison-only model.",
             "Using radix.", "Using counting with small k."],
            "General comparison-only model.",
            "Linear sorts exploit structure.",
        ),
    ],
    exercises=[
        ex(
            "dsa-sort-complexity-ex1",
            "Sort comparison table",
            "IMPLEMENT: Nothing new — write table: algorithm | best | avg | worst | space | stable for 6 sorts. "
            "TRACE: From memory without notes, then verify against MIT_L3 headings. "
            "SOLVE: NeetCode 150 Sort an Array — use `Arrays.sort` and state its expected complexity. "
            "TRANSFER (internal): Pick sort for 1M records with tiny RAM — justify merge vs quick vs heap.",
        ),
    ],
)

_add(
    "dsa-binary-search-classic",
    hours=1.0,
    objective="Search a sorted array.",
    explanation=(
        RELEARN + " Binary search: sorted array, compare mid, discard half. WHY O(log n): each step halves search space → "
        "at most ⌈log₂(n)⌋+1 comparisons. Invariant: answer (if exists) lies in current [lo,hi] range. "
        "Implement in Java without copying. C++: `std::lower_bound` family implements variants."
    ),
    mastery=[
        "Implement binary search in Java without copying.",
        *M,
    ],
    resources=[
        bari_primary("dsa-binary-search-classic", "2.3 Binary Search"),
        nc150("dsa-binary-search-classic", "Binary Search"),
        lc_collection("dsa-binary-search-classic"),
    ],
    questions=[
        q(
            "dsa-binary-search-classic-q1",
            "Binary search requires…",
            ["Hash table.", "Sorted order on the search axis.",
             "Queue.", "Heap."],
            "Sorted order on the search axis.",
            "Discard half needs monotonic order.",
            mastery=True,
        ),
        q(
            "dsa-binary-search-classic-q2",
            "Why O(log n)?",
            ["One comparison total.", "Halving search space each iteration.",
             "n/2 comparisons always.", "Binary uses two threads."],
            "Halving search space each iteration.",
            "T(n)=T(n/2)+O(1).",
        ),
        q(
            "dsa-binary-search-classic-q3",
            "Java classic: `while (lo <= hi)` with `mid = lo + (hi-lo)/2` avoids…",
            ["Sorting.", "Integer overflow in (lo+hi)/2.",
             "Null pointers.", "Recursion."],
            "Integer overflow in (lo+hi)/2.",
            "lo+hi can overflow; difference form is safe.",
        ),
        q(
            "dsa-binary-search-classic-q4",
            "Array [1,3,5,7,9] search 5 — after first mid at index 2 (value 5)?",
            ["Continue left half.", "Found — return index 2.",
             "Continue right.", "Not found."],
            "Found — return index 2.",
            "Mid hits target.",
        ),
        q(
            "dsa-binary-search-classic-q5",
            "Array [1,3,5,7,9] search 4 — outcome?",
            ["Index 2", "Index 3", "Not found", "Index 0"],
            "Not found",
            "4 between 3 and 5 — lo crosses hi.",
        ),
        q(
            "dsa-binary-search-classic-q6",
            "Recursion vs iteration space?",
            ["Recursion O(1).", "Iteration O(1); recursion O(log n) stack.",
             "Both O(n).", "Iteration O(n)."],
            "Iteration O(1); recursion O(log n) stack.",
            "Iterative preferred for depth.",
        ),
        q(
            "dsa-binary-search-classic-q7",
            "C++ `lower_bound` returns…",
            ["Always equal element.", "First position where value could be inserted maintaining order.",
             "Random index.", "Last index always."],
            "First position where value could be inserted maintaining order.",
            "Variant of binary search boundary.",
        ),
        q(
            "dsa-binary-search-classic-q8",
            "Common bug?",
            ["Using sorted array.", "Infinite loop when lo/hi update wrong on equal mid.",
             "O(log n).", "Using int mid."],
            "Infinite loop when lo/hi update wrong on equal mid.",
            "Off-by-one in bounds breaks halving.",
        ),
    ],
    exercises=[
        ex(
            "dsa-binary-search-classic-ex1",
            "Classic binary search",
            "IMPLEMENT: `int binarySearch(int[] a, int target)` iterative with lo/hi/mid. "
            "TRACE: lo/hi/mid table for [2,5,8,12,16,23,38,56,72,91] target 23. "
            "SOLVE (NeetCode 150 → Binary Search): Binary Search, Search a 2D Matrix. "
            "TRANSFER (internal): Guess number 1..100 with 'higher/lower' — max guesses = ⌈log₂100⌋.",
        ),
    ],
)

_add(
    "dsa-binary-search-boundaries",
    hours=1.0,
    objective="Get low/high updates right.",
    explanation=(
        RELEARN + " Boundary bugs dominate binary search failures. Inclusive [lo,hi] uses `lo=0, hi=n-1, while(lo<=hi)`. "
        "Exclusive upper [lo,hi) uses `hi=n` and `while(lo<hi)`. "
        "Pick one invariant and never mix. When `a[mid]==target`, lo/hi updates depend on finding first vs last vs any."
    ),
    mastery=[
        "Explain an off-by-one binary-search bug.",
        *M,
    ],
    resources=[
        bari_primary("dsa-binary-search-boundaries", "2.3 Binary Search — boundaries"),
        nc150("dsa-binary-search-boundaries", "Binary Search"),
        lc_collection("dsa-binary-search-boundaries"),
    ],
    questions=[
        q(
            "dsa-binary-search-boundaries-q1",
            "Inclusive model initialization?",
            ["lo=0 hi=n", "lo=0 hi=n-1", "lo=1 hi=n", "lo=0 hi=0"],
            "lo=0 hi=n-1",
            "Both ends inclusive valid indices.",
            mastery=True,
        ),
        q(
            "dsa-binary-search-boundaries-q2",
            "Inclusive while loop condition?",
            ["lo < hi", "lo <= hi", "hi < lo", "mid < 0"],
            "lo <= hi",
            "When lo==hi one element remains.",
        ),
        q(
            "dsa-binary-search-boundaries-q3",
            "Inclusive search, a[mid] < target — update?",
            ["hi = mid", "lo = mid", "lo = mid + 1", "hi = mid - 1"],
            "lo = mid + 1",
            "Target larger — exclude mid and left.",
        ),
        q(
            "dsa-binary-search-boundaries-q4",
            "Inclusive search, a[mid] > target — update?",
            ["lo = mid + 1", "hi = mid - 1", "lo = mid", "hi = mid"],
            "hi = mid - 1",
            "Target smaller — exclude mid and right.",
        ),
        q(
            "dsa-binary-search-boundaries-q5",
            "Exclusive upper bound hi starts at…",
            ["n-1", "n", "0", "n+1"],
            "n",
            "Valid indices [0,n-1] inside [0,n).",
        ),
        q(
            "dsa-binary-search-boundaries-q6",
            "Mixing inclusive lo with exclusive hi causes…",
            ["O(n).", "Wrong mid / infinite loop / skipped answer.",
             "Stability issues.", "Stable sort."],
            "Wrong mid / infinite loop / skipped answer.",
            "One consistent invariant required.",
        ),
        q(
            "dsa-binary-search-boundaries-q7",
            "Empty array inclusive search?",
            ["lo=0 hi=-1 loop runs.", "lo=0 hi=-1 while lo<=hi false immediately.",
             "Crash always.", "hi=0."],
            "lo=0 hi=-1 while lo<=hi false immediately.",
            "Empty → not found without body.",
        ),
        q(
            "dsa-binary-search-boundaries-q8",
            "When a[mid]==target in 'find any' inclusive search?",
            ["Always lo=mid+1.", "Return mid immediately.",
             "hi=mid-1 always.", "Break invariant."],
            "Return mid immediately.",
            "Classic exact search returns on hit.",
        ),
    ],
    exercises=[
        ex(
            "dsa-binary-search-boundaries-ex1",
            "Boundary invariant drill",
            "IMPLEMENT: Same classic search but write TWO versions — inclusive and exclusive — only one active in submission. "
            "TRACE: Side-by-side lo/hi updates when a[mid]<target on 5 elements. "
            "SOLVE (NeetCode 150 → Binary Search): Binary Search again focusing on zero off-by-one. "
            "TRANSFER (internal): Find first index where arr[i]>=x (lower bound) — which boundary template?",
        ),
    ],
)

_add(
    "dsa-first-last-occurrence",
    hours=1.0,
    objective="Find leftmost or rightmost match.",
    explanation=(
        RELEARN + " Duplicates break 'return any mid'. Find first: when a[mid]==target, hi=mid-1 (or lo=mid in exclusive leftmost template) "
        "and remember answer. Find last: bias lo. These are lower_bound / upper_bound minus one. "
        "Still O(log n) — same halving, different equality handling."
    ),
    mastery=[
        "Adjust classic search for first occurrence.",
        *M,
    ],
    resources=[
        bari_primary("dsa-first-last-occurrence", "2.3 Binary Search — first/last occurrence"),
        nc150("dsa-first-last-occurrence", "Binary Search"),
        lc_collection("dsa-first-last-occurrence"),
    ],
    questions=[
        q(
            "dsa-first-last-occurrence-q1",
            "[1,2,2,2,3] find first 2 — classic 'return mid' on first mid=2 wrong because…",
            ["2 is even.", "Mid may not be leftmost duplicate.",
             "Array unsorted.", "Need O(n)."],
            "Mid may not be leftmost duplicate.",
            "Must continue searching left.",
            mastery=True,
        ),
        q(
            "dsa-first-last-occurrence-q2",
            "Find first occurrence inclusive: a[mid]==target then…",
            ["lo=mid+1", "hi=mid-1 and record mid as candidate",
             "return immediately always", "hi=mid"],
            "hi=mid-1 and record mid as candidate",
            "Search left for earlier equal.",
        ),
        q(
            "dsa-first-last-occurrence-q3",
            "Find last occurrence: a[mid]==target then…",
            ["hi=mid-1", "lo=mid+1 and record mid",
             "return mid", "lo=mid"],
            "lo=mid+1 and record mid",
            "Search right for later equal.",
        ),
        q(
            "dsa-first-last-occurrence-q4",
            "lower_bound(x) returns first index with…",
            ["a[i] > x", "a[i] >= x", "a[i] == x only", "a[i] < x"],
            "a[i] >= x",
            "First not-less position.",
        ),
        q(
            "dsa-first-last-occurrence-q5",
            "upper_bound(x) - 1 gives…",
            ["First x", "Last x if x exists in array",
             "Always n-1", "First < x"],
            "Last x if x exists in array",
            "Upper bound is first > x.",
        ),
        q(
            "dsa-first-last-occurrence-q6",
            "Time for first+last?",
            ["O(n)", "O(log n) each", "O(n^2)", "O(1)"],
            "O(log n) each",
            "Two binary searches.",
        ),
        q(
            "dsa-first-last-occurrence-q7",
            "[2,2,2,2] first 2 index?",
            ["3", "0", "1", "Not found"],
            "0",
            "All equal — leftmost is 0.",
        ),
        q(
            "dsa-first-last-occurrence-q8",
            "Target absent — first occurrence function returns?",
            ["0 always.", "Sentinel like -1 or n depending on API.",
             "mid.", "Random."],
            "Sentinel like -1 or n depending on API.",
            "Document not-found convention.",
        ),
    ],
    exercises=[
        ex(
            "dsa-first-last-occurrence-ex1",
            "First and last position",
            "IMPLEMENT: `int firstOccurrence(int[] a, int x)` and `int lastOccurrence(int[] a, int x)`. "
            "TRACE: [1,2,2,2,3] record candidate each time mid==2 for both functions. "
            "SOLVE (NeetCode 150 → Binary Search): Find First and Last Position of Element in Sorted Array. "
            "TRANSFER (internal): Count occurrences of x in sorted array using first/last — O(log n).",
        ),
    ],
)

_add(
    "dsa-search-on-answer",
    hours=1.25,
    objective="Binary search a monotonic predicate.",
    explanation=(
        RELEARN + " Search on answer: answer lies in numeric range [min,max]. Define predicate P(k) = 'can we achieve k?' "
        "Monotonic: false…false true…true. Binary search the boundary. Examples: min capacity to ship in D days, "
        "Koko eating bananas, split array largest minimum sum. WHY O(log n): search range size halves. "
        "Not searching array index — searching answer space."
    ),
    mastery=[
        "State a monotonic predicate for a minimization prompt.",
        *M,
    ],
    resources=[
        bari_primary("dsa-search-on-answer", "2.3 Binary Search — search space / answer space"),
        nc150("dsa-search-on-answer", "Binary Search"),
        lc_collection("dsa-search-on-answer"),
    ],
    questions=[
        q(
            "dsa-search-on-answer-q1",
            "Search on answer needs predicate P(k) that is…",
            ["Random.", "Monotonic: once true stays true (or dual for maximization).",
             "O(n^2).", "Unsorted."],
            "Monotonic: once true stays true (or dual for maximization).",
            "Enables binary search on k.",
            mastery=True,
        ),
        q(
            "dsa-search-on-answer-q2",
            "Minimize maximum load — search space typically…",
            ["Array indices 0..n-1.", "Answer values from max single element to sum of all.",
             "Only 0..1.", "Heap size."],
            "Answer values from max single element to sum of all.",
            "Lower bound one pile max element; upper all in one.",
        ),
        q(
            "dsa-search-on-answer-q3",
            "Feasibility check usually costs…",
            ["O(1) always.", "O(n) or O(n log n) depending on problem.",
             "O(n^2) required.", "O(log n) only."],
            "O(n) or O(n log n) depending on problem.",
            "Total = O(n log R) often.",
        ),
        q(
            "dsa-search-on-answer-q4",
            "Minimize k such P(k) true — binary search on…",
            ["Descending predicate first true at right.", "Find leftmost k where P(k) true.",
             "Random k.", "Only mid index."],
            "Find leftmost k where P(k) true.",
            "First true in false…true sequence.",
        ),
        q(
            "dsa-search-on-answer-q5",
            "Koko bananas: P(speed) = can finish in h hours with speed…",
            ["Decreases with speed.", "True for fast enough speeds, false for too slow.",
             "Always true.", "Unrelated to h."],
            "True for fast enough speeds, false for too slow.",
            "Higher speed → easier predicate.",
        ),
        q(
            "dsa-search-on-answer-q6",
            "Unlike classic BS, lo/hi are…",
            ["Always 0 and n-1 indices.", "Answer domain values not necessarily array indices.",
             "Always 1..100.", "Heap indices."],
            "Answer domain values not necessarily array indices.",
            "Search numeric answer space.",
        ),
        q(
            "dsa-search-on-answer-q7",
            "Wrong non-monotonic predicate causes…",
            ["O(log n) still.", "Binary search returns wrong answer.",
             "Stable sort.", "O(1) check."],
            "Binary search returns wrong answer.",
            "Monotonicity is required.",
        ),
        q(
            "dsa-search-on-answer-q8",
            "Maximize minimum value with monotonic false…true reversed — search for…",
            ["First false.", "Last true / boundary variant.",
             "Mid index.", "n always."],
            "Last true / boundary variant.",
            "Maximization uses rightmost feasible.",
        ),
    ],
    exercises=[
        ex(
            "dsa-search-on-answer-ex1",
            "Monotonic predicate BS",
            "IMPLEMENT: `int shipWithinDays(int[] weights, int days)` or `int minEatingSpeed(int[] piles, int h)` with `can(k)` predicate. "
            "TRACE: Predicate truth table for speeds 1..10 on tiny piles. "
            "SOLVE (NeetCode 150 → Binary Search): Koko Eating Bananas, Capacity To Ship Packages Within D Days. "
            "TRANSFER (internal): Minimum max stack height when stacking books in order — define P(k).",
        ),
    ],
)

_add(
    "dsa-rotated-arrays",
    hours=1.0,
    objective="Search in a rotated sorted array.",
    explanation=(
        RELEARN + " Rotated sorted array: one pivot where order breaks. At mid, one half is always sorted. "
        "Identify sorted half; check if target lies in sorted range; shrink lo/hi. "
        "Find min in rotated array uses same 'which half is sorted' logic. O(log n)."
    ),
    mastery=[
        "Identify which half is sorted.",
        *M,
    ],
    resources=[
        bari_primary("dsa-rotated-arrays", "2.3 Binary Search — rotated array"),
        nc150("dsa-rotated-arrays", "Binary Search"),
        lc_collection("dsa-rotated-arrays"),
    ],
    questions=[
        q(
            "dsa-rotated-arrays-q1",
            "Rotated sorted array property…",
            ["Fully random.", "Originally sorted, then rotated at unknown pivot.",
             "Heap.", "Two unsorted halves always."],
            "Originally sorted, then rotated at unknown pivot.",
            "One rotation of sorted array.",
            mastery=True,
        ),
        q(
            "dsa-rotated-arrays-q2",
            "At mid in [4,5,6,7,0,1,2], which half sorted?",
            ["Neither.", "Left [4,5,6,7] sorted.",
             "Right only.", "Both unsorted."],
            "Left [4,5,6,7] sorted.",
            "Compare a[lo] and a[mid].",
        ),
        q(
            "dsa-rotated-arrays-q3",
            "If left half sorted and target in [a[lo],a[mid]]…",
            ["hi=mid-1", "lo=mid+1", "return -1", "lo=mid"],
            "hi=mid-1",
            "Search sorted left half.",
        ),
        q(
            "dsa-rotated-arrays-q4",
            "Find minimum element uses…",
            ["BFS.", "Compare mid to right neighbor / which side smaller.",
             "Bubble sort.", "Hash map."],
            "Compare mid to right neighbor / which side smaller.",
            "Min lies toward unsorted side.",
        ),
        q(
            "dsa-rotated-arrays-q5",
            "Time search in rotated array?",
            ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
            "O(log n)",
            "Still halving search space.",
        ),
        q(
            "dsa-rotated-arrays-q6",
            "[1,2,3,4,5] rotated 0 times — algorithm still…",
            ["Fails.", "Works — one half always sorted.",
             "O(n) only.", "Needs different code path only."],
            "Works — one half always sorted.",
            "Degenerate rotation is fine.",
        ),
        q(
            "dsa-rotated-arrays-q7",
            "Common mistake?",
            ["Using lo/hi.", "Checking sorted half with wrong endpoint comparisons.",
             "O(log n).", "Binary search."],
            "Checking sorted half with wrong endpoint comparisons.",
            "Must verify target in closed interval of sorted side.",
        ),
        q(
            "dsa-rotated-arrays-q8",
            "Search vs find-min relationship?",
            ["Unrelated.", "Both use sorted-half identification.",
             "Only find-min uses BS.", "Only search uses rotation."],
            "Both use sorted-half identification.",
            "Same rotated array insight.",
        ),
    ],
    exercises=[
        ex(
            "dsa-rotated-arrays-ex1",
            "Rotated array search",
            "IMPLEMENT: `int searchRotated(int[] a, int target)` and `int findMin(int[] a)`. "
            "TRACE: [4,5,6,7,0,1,2] search 0 — which half chosen each step. "
            "SOLVE (NeetCode 150 → Binary Search): Search in Rotated Sorted Array, Find Minimum in Rotated Sorted Array. "
            "TRANSFER (internal): Rotated array [3,4,5,1,2] — identify pivot index by hand.",
        ),
    ],
)
