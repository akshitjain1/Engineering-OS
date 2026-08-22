"""Domain 2 DSA: MST through greedy, DP, advanced patterns, interview hygiene."""

from __future__ import annotations

from _d2_helpers import *  # noqa: F403

CONTENT: dict = {}


def _add(slug, **kwargs):
    CONTENT[slug] = unit(**kwargs)


# --- MST ---------------------------------------------------------------------

_add(
    "dsa-mst",
    hours=1.25,
    objective="Explain a minimum spanning tree and contrast Kruskal vs Prim at a high level.",
    explanation=(
        RELEARN + " "
        "An MST connects all vertices with minimum total edge weight and has no cycles. "
        "Kruskal sorts edges and adds light edges that do not form a cycle (union-find detects cycles). "
        "Prim grows a tree from a start vertex using a min-heap of frontier edges. "
        "Both are greedy on safe light edges. " + JAVA_PRIMARY + " "
        + CPP["heap"] + " Union-find from the prior topic is Kruskal's cycle check."
    ),
    mastery=[
        "Contrast Kruskal vs Prim and when each is natural.",
        "Relate Kruskal to union-find.",
        "Sketch one MST algorithm in Java.",
        "Solve Min Cost to Connect All Points and Redundant Connection from NeetCode Advanced Graphs.",
        "State time/space complexity.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-mst", "Minimum Spanning Tree / Kruskal / Prim"),
        nccore("dsa-mst", "Kruskal's Algorithm"),
        nc150("dsa-mst", "Advanced Graphs"),
        mit_dd("dsa-mst", "MIT 6.006 — Weighted shortest paths context", MIT_L11),
    ],
    questions=[
        q("dsa-mst-q1",
          "A minimum spanning tree of a connected weighted graph:",
          ["Has minimum total weight among all spanning trees.",
           "Is always unique.", "Uses Dijkstra.", "Requires negative edges."],
          "Has minimum total weight among all spanning trees.",
          "Tie weights can yield multiple MSTs.",
          mastery=True),
        q("dsa-mst-q2",
          "Kruskal's algorithm needs union-find mainly to:",
          ["Detect whether adding an edge creates a cycle.",
           "Sort edges.", "Pick the start vertex.", "Handle negative weights."],
          "Detect whether adding an edge creates a cycle.",
          "Two endpoints in the same set ⇒ cycle."),
        q("dsa-mst-q3",
          "Prim's algorithm is closest to:",
          ["Growing one tree with a priority queue of cut edges.",
           "Sorting all edges once.", "BFS on unweighted graphs.", "Bellman-Ford."],
          "Growing one tree with a priority queue of cut edges.",
          "Dense graphs often favor Prim; sparse graphs often favor Kruskal."),
        q("dsa-mst-q4",
          "MST edge count for n vertices:",
          ["n - 1", "n", "n + 1", "E"],
          "n - 1",
          "A tree on n nodes has n-1 edges."),
        q("dsa-mst-q5",
          "Kruskal time with union-find (α amortized):",
          ["O(E log E) from sorting dominates.", "O(V^2) always.", "O(VE).", "O(V)."],
          "O(E log E) from sorting dominates.",
          "α is inverse Ackermann — effectively constant per op."),
        q("dsa-mst-q6",
          "Can Dijkstra from every vertex build an MST?",
          ["No — Dijkstra finds shortest paths, not MSTs.",
           "Yes, always.", "Only on trees.", "Only with negative edges."],
          "No — Dijkstra finds shortest paths, not MSTs.",
          "Do not confuse single-source shortest paths with global spanning cost."),
    ],
    exercises=[
        ex("dsa-mst-ex1", "Kruskal sketch + practice",
           "Implement Kruskal with union-find in Java (or complete NeetCode Core Skills Kruskal). "
           "On paper: trace both algorithms on a 5-node example. "
           "Solve Min Cost to Connect All Points and Redundant Connection (Advanced Graphs). "
           "TRANSFER (internal): given coordinates of cities, argue Kruskal vs Prim without coding."),
    ],
)

# --- Greedy ------------------------------------------------------------------

_add(
    "dsa-greedy-reasoning",
    hours=1.0,
    objective="Identify when a locally optimal choice can be globally optimal — and when it cannot.",
    explanation=(
        RELEARN + " "
        "Greedy builds a solution by repeatedly taking the best-looking local option. "
        "It works when greedy-choice and optimal substructure hold (often proved by exchange argument). "
        "Classic failure: coin change with coins [1,3,4] and amount 6 — greedy takes 4+1+1 (3 coins) "
        "but optimal is 3+3 (2 coins). That tempting greedy FAILS; you need DP. "
        + JAVA_PRIMARY
    ),
    mastery=[
        "Give one greedy success and one greedy failure.",
        "State why the failure breaks greedy.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-greedy-reasoning", "Greedy Method / Activity Selection"),
        nc150("dsa-greedy-reasoning", "Greedy"),
    ],
    questions=[
        q("dsa-greedy-reasoning-q1",
          "Coins [1,3,4], amount 6 — greedy (largest first) gives:",
          ["3 coins (4+1+1); optimal is 2 (3+3) — greedy FAILS.",
           "2 coins; greedy optimal.", "Impossible.", "Needs sorting."],
          "3 coins (4+1+1); optimal is 2 (3+3) — greedy FAILS.",
          "Always cite a failure case before trusting greedy on counting problems.",
          mastery=True),
        q("dsa-greedy-reasoning-q2",
          "Activity selection (sort by finish time) succeeds because:",
          ["Exchange argument: swapping to earliest finisher never reduces count.",
           "DP is impossible.", "Graph is a tree.", "Weights are negative."],
          "Exchange argument: swapping to earliest finisher never reduces count.",
          "Finish-time sort is the standard greedy key."),
        q("dsa-greedy-reasoning-q3",
          "Fractional knapsack is greedy-friendly; 0/1 knapsack usually is not because:",
          ["You cannot take fractions — local value/weight ratio misleads.",
           "Items are sorted.", "Capacity is infinite.", "Weights are equal."],
          "You cannot take fractions — local value/weight ratio misleads.",
          "0/1 needs DP or branch-and-bound."),
        q("dsa-greedy-reasoning-q4",
          "Before coding greedy, you should:",
          ["Try to disprove it with a small counterexample.",
           "Always sort descending.", "Use memoization first.", "Run Bellman-Ford."],
          "Try to disprove it with a small counterexample.",
          "One counterexample saves an interview."),
        q("dsa-greedy-reasoning-q5",
          "Jump Game I (can reach end) greedy checks:",
          ["Farthest reachable index while scanning left to right.",
           "Shortest path with Dijkstra.", "All subsets.", "BST order."],
          "Farthest reachable index while scanning left to right.",
          "Linear scan — not every greedy needs a heap."),
        q("dsa-greedy-reasoning-q6",
          "Greedy vs DP rule of thumb:",
          ["If local choice can be exchanged without hurting optimality → try greedy; else DP.",
           "Always DP first.", "Greedy always optimal.", "Same complexity always."],
          "If local choice can be exchanged without hurting optimality → try greedy; else DP.",
          "Pattern selection comes later; start with counterexamples."),
    ],
    exercises=[
        ex("dsa-greedy-reasoning-ex1", "Success + failure",
           "Prove activity selection greedy on paper with a 4-interval toy example. "
           "Show coin change [1,3,4] amount 6 failure. "
           "Solve Jump Game and Maximum Subarray (Greedy section). "
           "TRANSFER (internal): invent a coin set where greedy works for all amounts up to 20."),
    ],
)

_add(
    "dsa-greedy-exchange",
    hours=1.0,
    objective="Justify a greedy choice with an intuitive exchange argument.",
    explanation=(
        RELEARN + " "
        "Exchange proof sketch: assume an optimal solution differs from greedy; "
        "swap one greedy choice into the optimal solution without increasing cost. "
        "Repeat until they match. "
        "If you cannot find such an exchange, greedy may fail (see coin change). "
        + JAVA_PRIMARY
    ),
    mastery=[
        "Sketch an exchange argument for one interval or scheduling problem.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-greedy-exchange", "Greedy Method / Activity Selection"),
        nc150("dsa-greedy-exchange", "Greedy"),
    ],
    questions=[
        q("dsa-greedy-exchange-q1",
          "Exchange argument goal:",
          ["Show any optimal solution can be transformed to the greedy solution without worsening cost.",
           "Prove P=NP.", "Sort inputs.", "Use BFS."],
          "Show any optimal solution can be transformed to the greedy solution without worsening cost.",
          "Not a formal course — one paragraph is enough in interviews.",
          mastery=True),
        q("dsa-greedy-exchange-q2",
          "Interval scheduling: swap a non-greedy first pick for earliest-finishing compatible interval:",
          ["Never reduces the number of intervals chosen.",
           "Always increases count.", "Requires DP table.", "Only works on trees."],
          "Never reduces the number of intervals chosen.",
          "Standard exchange for activity selection."),
        q("dsa-greedy-exchange-q3",
          "When exchange fails, typical next step:",
          ["Try DP or prove impossibility of greedy.", "Increase heap size.", "Use radix sort.", "Skip proof."],
          "Try DP or prove impossibility of greedy.",
          "Coin change is the canonical failure."),
        q("dsa-greedy-exchange-q4",
          "Gas station circuit (if total gas >= total cost):",
          ["Greedy start index works with running tank exchange reasoning.",
           "Always start at index 0 only.", "Needs MST.", "Impossible always."],
          "Greedy start index works with running tank exchange reasoning.",
          "NeetCode Greedy — total feasibility gate first."),
        q("dsa-greedy-exchange-q5",
          "Huffman coding greedy merges:",
          ["Two least frequent symbols — exchange shows no better prefix tree.",
           "Two most frequent.", "Random pairs.", "BFS order."],
          "Two least frequent symbols — exchange shows no better prefix tree.",
          "V1 depth: recognize pattern, not implement full Huffman."),
        q("dsa-greedy-exchange-q6",
          "Interview level for exchange proofs:",
          ["Intuitive swap narrative on a small example.",
           "Formal induction required always.", "Never explain.", "Only for graphs."],
          "Intuitive swap narrative on a small example.",
          "Clarity beats notation."),
    ],
    exercises=[
        ex("dsa-greedy-exchange-ex1", "Exchange on paper",
           "Write a 5-sentence exchange proof for activity selection. "
           "Solve Gas Station and Hand of Straights (Greedy). "
           "TRANSFER (internal): explain why exchange fails for 0/1 knapsack with a 3-item counterexample."),
    ],
)

_add(
    "dsa-interval-problems",
    hours=1.0,
    objective="Solve interval overlap and merging with sort + greedy scan.",
    explanation=(
        RELEARN + " "
        "Sort intervals by start or end depending on the goal. "
        "Merge: sweep and extend current end. "
        "Non-overlapping removal: sort by end, greedily keep early-finishing intervals. "
        "Insert interval: merge pass or binary search on starts. "
        + JAVA_PRIMARY + " " + CPP["array"]
    ),
    mastery=[
        "Pick the correct sort key for merge vs non-overlap.",
        "Implement merge intervals in Java.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-interval-problems", "Activity Selection / Interval Scheduling"),
        nc150("dsa-interval-problems", "Intervals"),
    ],
    questions=[
        q("dsa-interval-problems-q1",
          "Merge Intervals sort key:",
          ["Sort by start (or end with care); merge overlapping neighbors.",
           "Sort by length only.", "Heapify intervals.", "Random shuffle."],
          "Sort by start (or end with care); merge overlapping neighbors.",
          "Classic linear merge after sort.",
          mastery=True),
        q("dsa-interval-problems-q2",
          "Non-overlapping intervals — maximize count, sort by:",
          ["End time ascending.", "Start descending.", "Length descending.", "Random."],
          "End time ascending.",
          "Greedy keeps earliest finisher."),
        q("dsa-interval-problems-q3",
          "Meeting rooms II (min rooms) typical approach:",
          ["Sort starts and ends; sweep line counting concurrent meetings.",
           "MST.", "Trie.", "Only DP."],
          "Sort starts and ends; sweep line counting concurrent meetings.",
          "Also solvable with min-heap of end times."),
        q("dsa-interval-problems-q4",
          "[[1,3],[2,6],[8,10]] merged:",
          ["[[1,6],[8,10]]", "[[1,10]]", "[[2,6]]", "No merge"],
          "[[1,6],[8,10]]",
          "2 and 6 overlap 1-3."),
        q("dsa-interval-problems-q5",
          "Insert interval into sorted non-overlapping list:",
          ["One linear merge pass after locating position.",
           "Rebuild BST.", "Dijkstra.", "Union-find only."],
          "One linear merge pass after locating position.",
          "Binary search can find insert index first."),
        q("dsa-interval-problems-q6",
          "Interval DP vs greedy:",
          ["Greedy for selection/merge; DP when optimal cost on merged subintervals (burst balloons).",
           "Always greedy.", "Always segment tree.", "Never sort."],
          "Greedy for selection/merge; DP when optimal cost on merged subintervals (burst balloons).",
          "Interval DP is a separate topic."),
    ],
    exercises=[
        ex("dsa-interval-problems-ex1", "Interval trio",
           "Implement merge intervals and non-overlapping intervals in Java. "
           "Solve Insert Interval from Intervals section. "
           "TRANSFER (internal): given employee [start,end] shifts, compute minimum rooms without code."),
    ],
)

_add(
    "dsa-greedy-scheduling",
    hours=1.0,
    objective="Apply greedy scheduling patterns with the correct sort key.",
    explanation=(
        RELEARN + " "
        "Scheduling greeds sort by finish time, deadline, or profit density. "
        "Task scheduler with cooldown uses frequency + heap/gaps. "
        "Not OS kernel scheduling — interview patterns only. "
        + JAVA_PRIMARY + " " + CPP["heap"]
    ),
    mastery=[
        "State the sort key for a classic scheduling greedy.",
        "Solve Task Scheduler from Greedy.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-greedy-scheduling", "Job Sequencing with Deadlines / Activity Selection"),
        nc150("dsa-greedy-scheduling", "Greedy"),
    ],
    questions=[
        q("dsa-greedy-scheduling-q1",
          "Activity selection maximizes count by sorting intervals by:",
          ["Finish time.", "Start time only.", "Duration descending.", "Weight."],
          "Finish time.",
          "Earliest finish leaves most room.",
          mastery=True),
        q("dsa-greedy-scheduling-q2",
          "Task Scheduler (n tasks, cooldown k) greedy insight:",
          ["Schedule most frequent tasks first with idle slots.",
           "Always sort ascending.", "Use Dijkstra.", "BST inorder."],
          "Schedule most frequent tasks first with idle slots.",
          "Heap on frequencies is common."),
        q("dsa-greedy-scheduling-q3",
          "Job sequencing with deadlines (unit time jobs):",
          ["Sort profit desc; place each job in latest free slot ≤ deadline.",
           "Sort deadline asc only.", "MST.", "No greedy works."],
          "Sort profit desc; place each job in latest free slot ≤ deadline.",
          "Disjoint-set or bucket slots."),
        q("dsa-greedy-scheduling-q4",
          "Car fleet (monotonic stack / speed sort):",
          ["Sort by position; stack fleets by arrival time at destination.",
           "Sort by speed only.", "DP table.", "Trie walk."],
          "Sort by position; stack fleets by arrival time at destination.",
          "Greedy + stack pattern."),
        q("dsa-greedy-scheduling-q5",
          "Partition labels (max parts with unique letters):",
          ["Track last index of each letter; extend part to max last seen.",
           "Sort alphabetically.", "BFS layers.", "Knapsack."],
          "Track last index of each letter; extend part to max last seen.",
          "Linear greedy scan."),
        q("dsa-greedy-scheduling-q6",
          "Wrong sort key symptom:",
          ["Counterexample where greedy picks block better future choices.",
           "Always AC.", "Only TLE.", "Compilation error."],
          "Counterexample where greedy picks block better future choices.",
          "Return to exchange argument or DP."),
    ],
    exercises=[
        ex("dsa-greedy-scheduling-ex1", "Schedule implementations",
           "Solve Task Scheduler and Partition Labels. "
           "On paper: job sequencing with deadlines for 4 jobs. "
           "TRANSFER (internal): meeting rooms with varying durations — pick sort key and justify."),
    ],
)

_add(
    "dsa-greedy-patterns",
    hours=1.0,
    objective="Recognize classic greedy patterns and classify greedy vs DP.",
    explanation=(
        RELEARN + " "
        "Patterns: activity selection, Huffman merges, two-pointer greedy on sorted arrays, "
        "reachability (jump game), interval sweeps. "
        "When counts or combinations matter (coin change, 0/1 knapsack), greedy often fails — use DP. "
        + JAVA_PRIMARY
    ),
    mastery=[
        "Classify a prompt as greedy vs DP.",
        "Solve two Greedy section problems independently.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-greedy-patterns", "Huffman Coding / Greedy Method"),
        nc150("dsa-greedy-patterns", "Greedy"),
    ],
    questions=[
        q("dsa-greedy-patterns-q1",
          "0/1 knapsack vs fractional knapsack:",
          ["Fractional: greedy by value/weight; 0/1: DP typically.",
           "Both greedy.", "Both need trie.", "Neither needs sort."],
          "Fractional: greedy by value/weight; 0/1: DP typically.",
          "Pattern selection checkpoint.",
          mastery=True),
        q("dsa-greedy-patterns-q2",
          "Assign cookies (sort + two pointers):",
          ["Greedy match smallest sufficient cookie to each child.",
           "DP on subsets.", "Graph coloring.", "Segment tree."],
          "Greedy match smallest sufficient cookie to each child.",
          "Two-pointer greedy after sort."),
        q("dsa-greedy-patterns-q3",
          "Boats to save people (sort + two pointers):",
          ["Pair lightest with heaviest if within limit.",
           "Always pair adjacent.", "MST.", "Bitmask DP."],
          "Pair lightest with heaviest if within limit.",
          "Classic two-pointer greedy."),
        q("dsa-greedy-patterns-q4",
          "Coin change minimum coins — greedy fails when:",
          ["Denomination set lacks canonical property (e.g., 1,3,4).",
           "All coins are 1.", "Amount is 0.", "Coins are sorted."],
          "Denomination set lacks canonical property (e.g., 1,3,4).",
          "DP or BFS on amounts."),
        q("dsa-greedy-patterns-q5",
          "Huffman coding at V1 depth:",
          ["Repeatedly merge two least frequent — optimal prefix code.",
           "Sort once by frequency.", "Use Dijkstra.", "BST insert."],
          "Repeatedly merge two least frequent — optimal prefix code.",
          "Recognition, not full implementation gate."),
        q("dsa-greedy-patterns-q6",
          "Maximum units on a truck (sort packages by units per box):",
          ["Greedy take highest density first.",
           "DP knapsack required always.", "BFS.", "Union-find."],
          "Greedy take highest density first.",
          "Fractional-like greedy on boxes."),
    ],
    exercises=[
        ex("dsa-greedy-patterns-ex1", "Classify + solve",
           "Classify 5 prompts (provided in comments: coin change, jump game II, 0/1 knapsack, "
           "merge intervals, task scheduler) as greedy vs DP. "
           "Solve Boats to Save People and Assign Cookies. "
           "TRANSFER (internal): design a greedy that fails for a custom coin set."),
    ],
)

# --- DP mindset through optimization -------------------------------------------

_DP_MASTERY_TAIL = [
    "Document STATE, TRANSITION, BASE, ORDER, COMPLEXITY for the template problem.",
    "Implement in Java without copying.",
    "Solve representative NeetCode problems from the mapped section.",
    "Score >= 80% on the topic questions.",
]


def _dp_questions(slug, topic_hint):
    """Shared conceptual MCQs; topic_hint personalizes the mastery question."""
    return [
        q(f"{slug}-q1",
          "Overlapping subproblems mean:",
          ["The same subproblem is solved many times in naive recursion.",
           "Subproblems never repeat.", "Only graphs overlap.", "Arrays cannot overlap."],
          "The same subproblem is solved many times in naive recursion.",
          "Memo/tabulation exist to pay each subproblem once.",
          mastery=True),
        q(f"{slug}-q2",
          "Optimal substructure means:",
          ["An optimal solution uses optimal solutions to subproblems.",
           "Every subproblem is independent.", "Greedy always works.", "Only trees have it."],
          "An optimal solution uses optimal solutions to subproblems.",
          "Verify before applying DP."),
        q(f"{slug}-q3",
          "Memoization vs tabulation:",
          ["Top-down cache vs bottom-up fill; same recurrence often.",
           "Tabulation is always faster.", "Memoization cannot use arrays.", "They are unrelated."],
          "Top-down cache vs bottom-up fill; same recurrence often.",
          "Pick based on state shape and iteration order."),
        q(f"{slug}-q4",
          "A DP state should be:",
          ["Minimal information to describe a subproblem uniquely.",
           "The entire input copied.", "Always one integer.", "Always a graph."],
          "Minimal information to describe a subproblem uniquely.",
          "Most DP bugs are bad state definition."),
        q(f"{slug}-q5",
          "Fill ORDER matters when:",
          ["A transition depends on not-yet-computed states in the same table.",
           "Never.", "Only in greedy.", "Only in BFS."],
          "A transition depends on not-yet-computed states in the same table.",
          "0/1 knapsack iterates capacity descending per item."),
        q(f"{slug}-q6",
          "Space optimization to O(1) or O(n) is valid when:",
          ["Only recent prior rows/layers are needed for transitions.",
           "Always for 2D DP.", "Never.", "Only with segment trees."],
          "Only recent prior rows/layers are needed for transitions.",
          "Rolling array technique."),
        q(f"{slug}-q7",
          "Naive recursion time without memo for fib(n):",
          ["Exponential — repeated subcalls.", "O(n).", "O(log n).", "O(1)."],
          "Exponential — repeated subcalls.",
          "Memo drops to O(n)."),
        q(f"{slug}-q8",
          f"For {topic_hint}, first step in an interview:",
          ["Define state in one sentence, then write BASE and TRANSITION.",
           "Code immediately.", "Sort the input.", "Use BFS."],
          "Define state in one sentence, then write BASE and TRANSITION.",
          "SRTBOT-style discipline."),
        q(f"{slug}-q9",
          "Bottom-up BASE cases are:",
          ["Smallest subproblems with known answers before loops.",
           "Always empty.", "Only for graphs.", "The final answer."],
          "Smallest subproblems with known answers before loops.",
          "Initialize table corners carefully."),
        q(f"{slug}-q10",
          "DP time is usually:",
          ["O(number of states × work per transition).",
           "Always O(n^2).", "Always exponential.", "O(1)."],
          "O(number of states × work per transition).",
          "Count states before coding."),
    ]


_add(
    "dsa-dp-mindset",
    hours=1.0,
    objective="Recognize overlapping subproblems and optimal substructure.",
    explanation=(
        RELEARN + " "
        "DP applies when naive recursion repeats work and optimal pieces compose. "
        "Write recurrence before code. MIT 6.006 SRTBOT: Subproblems, Relate, Topological order, "
        "Base, Original, Time. " + JAVA_PRIMARY
    ),
    mastery=[
        "Write a recurrence for a toy problem on paper.",
        "Explain overlapping subproblems vs divide-and-conquer.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-dp-mindset", "Dynamic Programming / Fibonacci / Memoization"),
        nc150("dsa-dp-mindset", "1-D DP"),
        mit_dd("dsa-dp-mindset", "MIT 6.006 — DP Part 1 (SRTBOT)", MIT_L15),
    ],
    questions=_dp_questions("dsa-dp-mindset", "climbing stairs"),
    exercises=[
        ex("dsa-dp-mindset-ex1", "Fib → stairs template",
           "For Fibonacci/stairs: STATE dp[i], TRANSITION, BASE, ORDER, COMPLEXITY on paper. "
           "Implement bottom-up stairs in Java. "
           "Solve Climbing Stairs (1-D DP). "
           "TRANSFER (internal): min cost climbing stairs with costs array — define state only."),
    ],
)

_add(
    "dsa-memoization",
    hours=1.0,
    objective="Cache recursive DP results top-down in Java.",
    explanation=(
        RELEARN + " "
        "Wrap recursion with a memo map or array; check before recomputing. "
        + JAVA_PRIMARY + " " + CPP["map"] + " "
        "Top-down is natural when state space is sparse or hard to order."
    ),
    mastery=[
        "Implement memoized recursion for a 1D recurrence.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-memoization", "Dynamic Programming / Memoization"),
        nc150("dsa-memoization", "1-D DP"),
        mit_dd("dsa-memoization", "MIT 6.006 — DP Part 1", MIT_L15),
    ],
    questions=_dp_questions("dsa-memoization", "house robber") + [
        q("dsa-memoization-q11",
          "Memoization in Java often uses:",
          ["int[] or HashMap keyed by state parameters.",
           "Only global variables without keys.", "Synchronized blocks only.", "Stack pop only."],
          "int[] or HashMap keyed by state parameters.",
          "Array when indices are dense."),
    ],
    exercises=[
        ex("dsa-memoization-ex1", "Top-down robber",
           "House Robber: STATE, TRANSITION, BASE, ORDER, COMPLEXITY; implement memoized recursion. "
           "Solve House Robber (1-D DP). "
           "TRANSFER (internal): memoized decode ways for s='12' — trace call tree."),
    ],
)

_add(
    "dsa-tabulation",
    hours=1.0,
    objective="Fill a DP table bottom-up with correct iteration order.",
    explanation=(
        RELEARN + " "
        "Tabulation iterates subproblems in topological order filling a table. "
        "Often avoids recursion stack limits. " + JAVA_PRIMARY
    ),
    mastery=[
        "Convert a memoized solution to tabulation.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-tabulation", "Dynamic Programming / Tabulation"),
        nc150("dsa-tabulation", "1-D DP"),
        mit_dd("dsa-tabulation", "MIT 6.006 — DP Part 1", MIT_L15),
    ],
    questions=_dp_questions("dsa-tabulation", "coin change") + [
        q("dsa-tabulation-q11",
          "Iterating i from 0..n-1 for dp[i] depends on smaller indices means:",
          ["Forward fill order is valid.",
           "Must fill backward only.", "Need recursion.", "Invalid tabulation."],
          "Forward fill order is valid.",
          "Order follows dependency direction."),
    ],
    exercises=[
        ex("dsa-tabulation-ex1", "Tabulate coin change",
           "Coin Change: STATE dp[amount], TRANSITION over coins, BASE dp[0]=0, ORDER, COMPLEXITY. "
           "Implement tabulation in Java. "
           "Solve Coin Change (1-D DP). "
           "TRANSFER (internal): tabulate min coins for amount 11 with coins [1,3,4] — fill table on paper."),
    ],
)

_add(
    "dsa-dp-state",
    hours=1.25,
    objective="Choose a DP state that uniquely describes a subproblem.",
    explanation=(
        RELEARN + " "
        "State = what you store per subproblem (index, capacity, last choice, etc.). "
        "Too small → wrong answer; too big → TLE/MLE. " + JAVA_PRIMARY
    ),
    mastery=[
        "Name indices/parameters for a novel prompt.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-dp-state", "Dynamic Programming / 0/1 Knapsack state"),
        nc150("dsa-dp-state", "1-D DP"),
        mit_dd("dsa-dp-state", "MIT 6.006 — DP Part 1", MIT_L15),
    ],
    questions=_dp_questions("dsa-dp-state", "LCS") + [
        q("dsa-dp-state-q11",
          "LCS state dp[i][j] means:",
          ["LCS length of first i chars of A and first j chars of B.",
           "Longest substring only.", "Edit distance.", "Number of paths."],
          "LCS length of first i chars of A and first j chars of B.",
          "2D state from two sequences."),
        q("dsa-dp-state-q12",
          "House Robber II (circle) state trick:",
          ["Run linear robber on [0..n-2] and [1..n-1]; take max.",
           "Single dp on circle array.", "Greedy.", "BFS."],
          "Run linear robber on [0..n-2] and [1..n-1]; take max.",
          "Break symmetry by fixing first/last exclusion."),
    ],
    exercises=[
        ex("dsa-dp-state-ex1", "State design drill",
           "For House Robber II: STATE, TRANSITION, BASE, ORDER, COMPLEXITY on paper. "
           "Also define states for LCS and 0/1 knapsack in one sentence each. "
           "Implement House Robber II in Java. "
           "TRANSFER (internal): state for deleting adjacent equal pairs in a string."),
    ],
)

_add(
    "dsa-dp-transition",
    hours=1.25,
    objective="Write recurrence transitions between DP states.",
    explanation=(
        RELEARN + " "
        "Transition = how dp[state] combines smaller solved states (min/max/sum/or). "
        "Write the recurrence before loops. " + JAVA_PRIMARY
    ),
    mastery=[
        "Write one transition equation for a standard family.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-dp-transition", "Dynamic Programming / Knapsack recurrence"),
        nc150("dsa-dp-transition", "1-D DP"),
        mit_dd("dsa-dp-transition", "MIT 6.006 — DP Part 2", MIT_L16),
    ],
    questions=_dp_questions("dsa-dp-transition", "knapsack") + [
        q("dsa-dp-transition-q11",
          "0/1 knapsack transition (item i, cap w):",
          ["dp[i][w] = max(skip, take) using row i-1.",
           "dp[i][w] = sum of all items.", "Always greedy take.", "BFS layer."],
          "dp[i][w] = max(skip, take) using row i-1.",
          "Take uses dp[i-1][w-weight]."),
        q("dsa-dp-transition-q12",
          "LCS transition when chars match:",
          ["dp[i][j] = dp[i-1][j-1] + 1.",
           "dp[i][j] = 0.", "dp[i][j] = dp[i-1][j].", "dp[i][j] = i + j."],
          "dp[i][j] = dp[i-1][j-1] + 1.",
          "Mismatch takes max of skip either side."),
    ],
    exercises=[
        ex("dsa-dp-transition-ex1", "Write transitions",
           "LIS: STATE, TRANSITION, BASE, ORDER, COMPLEXITY on paper; implement in Java. "
           "Also write TRANSITION + BASE for 0/1 knapsack and LCS. "
           "TRANSFER (internal): transition for word break boolean dp."),
    ],
)

_add(
    "dsa-dp-1d",
    hours=1.5,
    objective="Solve linear 1D DP families in Java.",
    explanation=(
        RELEARN + " "
        "1D examples: stairs, robber, LIS, coin change, decode ways. "
        "Watch index direction and base cases. " + JAVA_PRIMARY
    ),
    mastery=[
        "Implement a 1D DP without copying.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-dp-1d", "Dynamic Programming / 1D problems"),
        nc150("dsa-dp-1d", "1-D DP"),
        mit_dd("dsa-dp-1d", "MIT 6.006 — DP Part 2 (LIS, coins)", MIT_L16),
    ],
    questions=_dp_questions("dsa-dp-1d", "LIS") + [
        q("dsa-dp-1d-q11",
          "LIS O(n^2) transition:",
          ["dp[i] = 1 + max dp[j] for j<i if nums[j]<nums[i].",
           "Sort and greedy.", "Only dp[i-1].", "BFS depth."],
          "dp[i] = 1 + max dp[j] for j<i if nums[j]<nums[i].",
          "Patience sorting gives O(n log n) variant."),
        q("dsa-dp-1d-q12",
          "Decode Ways: dp[i] uses:",
          ["Valid single char and valid two-char slice ending at i.",
           "Only one char.", "Graph BFS.", "Trie."],
          "Valid single char and valid two-char slice ending at i.",
          "Handle leading zero carefully."),
    ],
    exercises=[
        ex("dsa-dp-1d-ex1", "1D trio",
           "House Robber + Coin Change: STATE, TRANSITION, BASE, ORDER, COMPLEXITY kit. "
           "Solve Decode Ways. "
           "TRANSFER (internal): min jumps to end — define dp[i] and transition."),
    ],
)

_add(
    "dsa-dp-2d",
    hours=1.75,
    objective="Fill DP tables over two indices.",
    explanation=(
        RELEARN + " "
        "2D DP: two sequences, grid paths, paired prefixes. "
        "Nested loops follow dependency order. " + JAVA_PRIMARY
    ),
    mastery=[
        "Dry-run a small 2D table.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-dp-2d", "Dynamic Programming / 2D tables"),
        nc150("dsa-dp-2d", "2-D DP"),
        mit_dd("dsa-dp-2d", "MIT 6.006 — DP Part 2", MIT_L16),
    ],
    questions=_dp_questions("dsa-dp-2d", "unique paths") + [
        q("dsa-dp-2d-q11",
          "Unique Paths dp[i][j] on grid:",
          ["Paths to cell = dp[i-1][j] + dp[i][j-1] (with bases on first row/col).",
           "Product of neighbors.", "BFS count.", "Greedy diagonal."],
          "Paths to cell = dp[i-1][j] + dp[i][j-1] (with bases on first row/col).",
          "Classic grid DP."),
        q("dsa-dp-2d-q12",
          "Space reduce unique paths to O(n):",
          ["Single row updated left-to-right.",
           "Impossible.", "Need full 2D always.", "Use segment tree."],
          "Single row updated left-to-right.",
          "Only previous row needed."),
    ],
    exercises=[
        ex("dsa-dp-2d-ex1", "2D grid + strings",
           "Unique Paths + Min Path Sum: STATE, TRANSITION, BASE, ORDER, COMPLEXITY; implement in Java. "
           "Solve Longest Common Subsequence (2-D DP). "
           "TRANSFER (internal): edit distance — fill 3×3 table on paper."),
    ],
)

_add(
    "dsa-subsequence-dp",
    hours=1.75,
    objective="Handle LCS/LIS-style subsequence DP states.",
    explanation=(
        RELEARN + " "
        "Subsequence allows skips — transitions usually consider match or skip. "
        "LCS, LIS, delete operations strings. " + JAVA_PRIMARY
    ),
    mastery=[
        "Define LCS state in one sentence.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-subsequence-dp", "Longest Common Subsequence"),
        nc150("dsa-subsequence-dp", "2-D DP"),
        mit_dd("dsa-subsequence-dp", "MIT 6.006 — DP Part 2 (LCS)", MIT_L16),
    ],
    questions=_dp_questions("dsa-subsequence-dp", "LCS") + [
        q("dsa-subsequence-dp-q11",
          "Longest Palindromic Subsequence uses:",
          ["Interval DP on i..j or 2D on reversed prefixes.",
           "Greedy two pointers only always.", "MST.", "Trie only."],
          "Interval DP on i..j or 2D on reversed prefixes.",
          "Related to LCS with reversed string."),
        q("dsa-subsequence-dp-q12",
          "Subsequence vs substring DP difference:",
          ["Subsequence allows skipping; substring is contiguous.",
           "No difference.", "Substring uses graph.", "Subsequence uses heap."],
          "Subsequence allows skipping; substring is contiguous.",
          "State design changes accordingly."),
    ],
    exercises=[
        ex("dsa-subsequence-dp-ex1", "LCS + palindrome subseq",
           "LCS: STATE, TRANSITION, BASE, ORDER, COMPLEXITY + Java implementation. "
           "Solve Longest Palindromic Subsequence. "
           "TRANSFER (internal): shortest common supersequence length from LCS formula."),
    ],
)

_add(
    "dsa-knapsack",
    hours=2.0,
    objective="Use 0/1 knapsack as a DP template; name unbounded variant.",
    explanation=(
        RELEARN + " "
        "0/1 knapsack: each item once. Unbounded: unlimited copies. "
        "Watch inner loop direction for 0/1 vs unbounded. "
        + JAVA_PRIMARY + " " + CPP["array"]
    ),
    mastery=[
        "Write the 0/1 knapsack transition.",
        "Implement 0/1 and unbounded variants.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_video("dsa-knapsack", "Abdul Bari — 4.5 0/1 Knapsack DP", BARI_KNAP),
        nccore("dsa-knapsack", "0/1 Knapsack"),
        r("dsa-knapsack-nccore-unbounded", "NeetCode Core Skills — Unbounded Knapsack", NC_CORE,
          "NeetCode", "PRACTICE", "coding_problem", 2,
          "Implement Unbounded Knapsack from Core Skills. Inner capacity loop is forward."),
        nc150("dsa-knapsack", "1-D DP"),
        mit_dd("dsa-knapsack", "MIT 6.006 — DP Part 4 (subset sum)", MIT_L18),
    ],
    questions=_dp_questions("dsa-knapsack", "0/1 knapsack") + [
        q("dsa-knapsack-q11",
          "0/1 knapsack inner loop over capacity should be:",
          ["Descending to avoid reusing item i.",
           "Ascending always.", "Random.", "Only capacity 0."],
          "Descending to avoid reusing item i.",
          "Unbounded uses ascending."),
        q("dsa-knapsack-q12",
          "Unbounded knapsack differs by:",
          ["Forward capacity loop allows reuse of item i.",
           "No DP needed.", "Greedy always.", "Uses MST."],
          "Forward capacity loop allows reuse of item i.",
          "Same state shape, different order."),
    ],
    exercises=[
        ex("dsa-knapsack-ex1", "Knapsack pair",
           "0/1 Knapsack: STATE dp[w], TRANSITION per item, BASE, ORDER (desc cap), COMPLEXITY. "
           "Implement 0/1 and unbounded in Java (Core Skills). "
           "Solve Partition Equal Subset Sum and Target Sum (1-D DP). "
           "TRANSFER (internal): bounded knapsack with counts — describe state change, no code."),
    ],
)

_add(
    "dsa-grid-dp",
    hours=1.5,
    objective="DP on grids: path counts, min cost, with obstacles.",
    explanation=(
        RELEARN + " "
        "Grid DP uses cell (i,j) states; transitions from top/left (or four directions). "
        "Handle obstacles by skipping bad cells. " + JAVA_PRIMARY
    ),
    mastery=[
        "Count paths or min path on a small grid.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-grid-dp", "Dynamic Programming / grid problems"),
        nc150("dsa-grid-dp", "2-D DP"),
        mit_dd("dsa-grid-dp", "MIT 6.006 — DP Part 2", MIT_L16),
    ],
    questions=_dp_questions("dsa-grid-dp", "min path sum") + [
        q("dsa-grid-dp-q11",
          "Obstacle grid unique paths:",
          ["dp[i][j]=0 if blocked else sum of top+left.",
           "Greedy diagonal.", "BFS only.", "DSU."],
          "dp[i][j]=0 if blocked else sum of top+left.",
          "Base cells on first row/col need care."),
        q("dsa-grid-dp-q12",
          "Maximal square of 1s (dp as side length):",
          ["dp[i][j] = 1 + min(top, left, top-left) if cell is 1.",
           "Sum top+left.", "LIS.", "Trie depth."],
          "dp[i][j] = 1 + min(top, left, top-left) if cell is 1.",
          "Track max over dp."),
    ],
    exercises=[
        ex("dsa-grid-dp-ex1", "Grid implementations",
           "Min Path Sum + Unique Paths II: STATE, TRANSITION, BASE, ORDER, COMPLEXITY. "
           "Solve Maximal Square (2-D DP). "
           "TRANSFER (internal): min path with at most k obstacles — state idea only."),
    ],
)

_add(
    "dsa-interval-dp",
    hours=1.5,
    objective="Explain DP on intervals at a conceptual level.",
    explanation=(
        RELEARN + " "
        "State is often dp[i][j] = best on subarray i..j. "
        "Fill by increasing length. Burst Balloons / palindrome partitions are interview recognition. "
        "Not full contest drill. " + JAVA_PRIMARY
    ),
    mastery=[
        "State when a subarray/interval is the subproblem.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-interval-dp", "Matrix Chain Multiplication / interval DP"),
        nc150("dsa-interval-dp", "2-D DP"),
        mit_dd("dsa-interval-dp", "MIT 6.006 — DP Part 3 (parens)", MIT_L17),
    ],
    questions=_dp_questions("dsa-interval-dp", "burst balloons") + [
        q("dsa-interval-dp-q11",
          "Interval DP iteration order:",
          ["Increasing interval length (j-i).",
           "Decreasing only i.", "Random.", "BFS queue."],
          "Increasing interval length (j-i).",
          "Smaller intervals before larger."),
        q("dsa-interval-dp-q12",
          "Matrix chain multiplication state:",
          ["dp[i][j] = min cost to multiply matrices i..j.",
           "Greedy always.", "LIS.", "Trie."],
          "dp[i][j] = min cost to multiply matrices i..j.",
          "Try split k between i..j."),
    ],
    exercises=[
        ex("dsa-interval-dp-ex1", "Interval recognition",
           "Burst Balloons: STATE dp[i][j], TRANSITION via last burst k, BASE, ORDER, COMPLEXITY on paper. "
           "Implement Palindrome Partitioning II if time. "
           "TRANSFER (internal): explain why merge intervals is greedy not interval DP."),
    ],
)

_add(
    "dsa-dp-optimization",
    hours=1.25,
    objective="Name space/time DP optimizations at V1 depth.",
    explanation=(
        RELEARN + " "
        "Rolling arrays, single-row updates, monotone deque for some 1D optimizations. "
        "No convex hull trick / Knuth optimization as mastery gates. " + JAVA_PRIMARY
    ),
    mastery=[
        "Reduce a 2-row DP to rolling arrays when valid.",
        *_DP_MASTERY_TAIL,
    ],
    resources=[
        bari_primary("dsa-dp-optimization", "Dynamic Programming / space optimization"),
        nc150("dsa-dp-optimization", "1-D DP"),
        mit_dd("dsa-dp-optimization", "MIT 6.006 — DP Part 4 (pseudopolynomial)", MIT_L18),
    ],
    questions=_dp_questions("dsa-dp-optimization", "rolling array") + [
        q("dsa-dp-optimization-q11",
          "0/1 knapsack space O(W) uses:",
          ["One row updated descending per item.",
           "Two full 2D tables always.", "Greedy.", "Segment tree."],
          "One row updated descending per item.",
          "Row reuse is safe with correct order."),
        q("dsa-dp-optimization-q12",
          "Not required at V1:",
          ["Convex hull trick, Knuth optimization, digit DP contests.",
           "Rolling array.", "O(n) fib.", "LIS n log n."],
          "Convex hull trick, Knuth optimization, digit DP contests.",
          "Recognition only for advanced DP topic."),
    ],
    exercises=[
        ex("dsa-dp-optimization-ex1", "Roll the table",
           "Rewrite 0/1 knapsack from 2D to 1D row; document ORDER invariant. "
           "STATE/BASE/TRANSITION/COMPLEXITY after optimization. "
           "TRANSFER (internal): which 2D DP cannot roll to 1D and why (LCS example)."),
    ],
)

# --- Advanced patterns -------------------------------------------------------

_add(
    "dsa-tries",
    hours=1.25,
    objective="Implement a trie for prefix search in Java.",
    explanation=(
        RELEARN + " "
        "Trie nodes map char → child; mark word ends. "
        "Use for prefix autocomplete, word search helpers, XOR max path (interview level). "
        + JAVA_PRIMARY + " " + CPP["map"] + " "
        "Array[26] children faster for lowercase English."
    ),
    mastery=[
        "Insert and search words in a trie.",
        "Solve Implement Trie from NeetCode Tries.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-tries", "Trie data structure"),
        nc150("dsa-tries", "Tries"),
    ],
    questions=[
        q("dsa-tries-q1",
          "Trie excels when queries involve:",
          ["Prefixes over a static dictionary.",
           "Only sorted array binary search.", "Only graphs.", "Matrix multiply."],
          "Prefixes over a static dictionary.",
          "Autocomplete, prefix counts.",
          mastery=True),
        q("dsa-tries-q2",
          "Java trie node often uses:",
          ["Map<Character, TrieNode> or Node[26].",
           "PriorityQueue.", "ArrayDeque only.", "Union-find."],
          "Map<Character, TrieNode> or Node[26].",
          CPP["map"]),
        q("dsa-tries-q3",
          "Search prefix vs full word:",
          ["Prefix: walk chars; word: also check end flag.",
           "Same operation.", "Only hash set.", "BST only."],
          "Prefix: walk chars; word: also check end flag.",
          "isEnd or similar marker."),
        q("dsa-tries-q4",
          "Space tradeoff vs hash set of words:",
          ["Trie shares prefixes; can use more nodes for sparse alphabets.",
           "Trie always smaller.", "Hash set shares prefixes.", "Equal always."],
          "Trie shares prefixes; can use more nodes for sparse alphabets.",
          "Interview practical choice."),
        q("dsa-tries-q5",
          "Word Search II pattern:",
          ["Trie of words + DFS on grid pruning by prefix.",
           "Only BFS.", "Dijkstra.", "MST."],
          "Trie of words + DFS on grid pruning by prefix.",
          "Prune dead prefixes early."),
        q("dsa-tries-q6",
          "Maximum XOR of two numbers (bit trie):",
          ["Walk bits choosing opposite bit when branch exists.",
           "Sort array.", "Greedy sum.", "LCS."],
          "Walk bits choosing opposite bit when branch exists.",
          "Interview-level bit trie."),
    ],
    exercises=[
        ex("dsa-tries-ex1", "Trie from scratch",
           "Implement Trie with insert, search, startsWith in Java. "
           "Solve Implement Trie and Word Search II (Tries). "
           "TRANSFER (internal): count words with given prefix without scanning all words."),
    ],
)

_add(
    "dsa-bit-manipulation",
    hours=1.25,
    objective="Use AND/OR/XOR/shifts for interview bit tricks in Java.",
    explanation=(
        RELEARN + " "
        "Java: int is 32-bit two's complement; use >>> for logical right shift. "
        "XOR cancels duplicates; masks select bits. Not a CPU architecture course. "
        + JAVA_PRIMARY + " C++ bit ops are equivalent for interview purposes."
    ),
    mastery=[
        "Check a bit and count set bits.",
        "Solve 2–3 Bit Manipulation NeetCode problems.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-bit-manipulation", "Bitwise operations"),
        nc150("dsa-bit-manipulation", "Bit Manipulation"),
    ],
    questions=[
        q("dsa-bit-manipulation-q1",
          "n & (n-1) clears:",
          ["Lowest set bit.",
           "Highest set bit.", "Sign bit only.", "All bits."],
          "Lowest set bit.",
          "Used in Brian Kernighan popcount.",
          mastery=True),
        q("dsa-bit-manipulation-q2",
          "a ^ a equals:",
          ["0 for any a.", "1.", "a.", "-a."],
          "0 for any a.",
          "XOR duplicate cancellation."),
        q("dsa-bit-manipulation-q3",
          "Single number (every other appears twice):",
          ["XOR all numbers.",
           "Sort.", "Hash map only.", "MST."],
          "XOR all numbers.",
          "Linear time O(1) space."),
        q("dsa-bit-manipulation-q4",
          "Check bit k of n in Java:",
          ["(n >> k) & 1 == 1", "n % k", "n | k", "n ^ k"],
          "(n >> k) & 1 == 1",
          "Mind 0-based indexing."),
        q("dsa-bit-manipulation-q5",
          "Counting bits for 0..n DP:",
          ["dp[i] = dp[i >> 1] + (i & 1).",
           "dp[i] = i.", "Greedy.", "Trie only."],
          "dp[i] = dp[i >> 1] + (i & 1).",
          "NeetCode pattern."),
        q("dsa-bit-manipulation-q6",
          "Java >>> vs >>:",
          [">>> is unsigned/logical; >> preserves sign.",
           "Same always.", ">>> preserves sign.", ">> is unsigned."],
          ">>> is unsigned/logical; >> preserves sign.",
          "Interview gotcha for negatives."),
    ],
    exercises=[
        ex("dsa-bit-manipulation-ex1", "Bit toolkit",
           "Implement single number, count bits for 0..n, sum of two integers without + (optional). "
           "Solve Number of 1 Bits and Counting Bits. "
           "TRANSFER (internal): find two unique numbers when all others appear twice — outline XOR split."),
    ],
)

_add(
    "dsa-segment-tree-concept",
    hours=1.0,
    objective="Explain segment tree range queries; implement via Core Skills if coding.",
    explanation=(
        RELEARN + " "
        "Segment tree stores aggregate intervals; update/query O(log n). "
        "Fenwick tree alternative for prefix sums. "
        "V1: concept + Design Segment Tree implementation from Core Skills — not contest catalog. "
        + JAVA_PRIMARY
    ),
    mastery=[
        "State what each node stores and how query merges children.",
        "Complete Design Segment Tree from Core Skills OR explain on paper.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-segment-tree-concept", "Segment Tree"),
        nccore("dsa-segment-tree-concept", "Design Segment Tree"),
    ],
    questions=[
        q("dsa-segment-tree-concept-q1",
          "Segment tree typical query time:",
          ["O(log n) per query/update.",
           "O(1) always.", "O(n) per query only.", "O(n^2)."],
          "O(log n) per query/update.",
          "Balanced binary tree over index range.",
          mastery=True),
        q("dsa-segment-tree-concept-q2",
          "Each internal node stores:",
          ["Aggregate of its index interval (sum/min/max).",
           "Single element only.", "Graph edge.", "Hash of strings."],
          "Aggregate of its index interval (sum/min/max).",
          "Merge function defines semantics."),
        q("dsa-segment-tree-concept-q3",
          "Vs prefix sum array:",
          ["Segment tree handles point updates + range query faster than rebuilding prefix.",
           "Prefix always better.", "No difference.", "Segment tree is BFS."],
          "Segment tree handles point updates + range query faster than rebuilding prefix.",
          "Range Sum Query mutable is the motivation."),
        q("dsa-segment-tree-concept-q4",
          "Fenwick (BIT) compared to segment tree:",
          ["Often simpler for prefix/range sums; less general merges.",
           "Always harder.", "Same structure.", "Only for tries."],
          "Often simpler for prefix/range sums; less general merges.",
          "One-paragraph interview answer."),
        q("dsa-segment-tree-concept-q5",
          "Lazy propagation is for:",
          ["Range updates without O(n) walks each time.",
           "Sorting.", "MST.", "LCS."],
          "Range updates without O(n) walks each time.",
          "Named at concept level."),
        q("dsa-segment-tree-concept-q6",
          "Not in V1 scope:",
          ["Heavy-light decomposition, suffix automata, contest-only variants.",
           "Basic sum segment tree.", "Point update.", "Range query."],
          "Heavy-light decomposition, suffix automata, contest-only variants.",
          "Recognition boundaries."),
    ],
    exercises=[
        ex("dsa-segment-tree-concept-ex1", "Design segment tree",
           "On paper: tree array size ~4n, merge = sum, query range [l,r]. "
           "Implement Design Segment Tree (Core Skills) in Java. "
           "TRANSFER (internal): explain when prefix sum + diff array suffices instead."),
    ],
)

_add(
    "dsa-advanced-graphs",
    hours=1.25,
    objective="Recognize SCC, bridges, articulation points — not CP encyclopedia.",
    explanation=(
        RELEARN + " "
        "Strongly connected components (Kosaraju/Tarjan), bridges and articulation points via DFS low-link. "
        "Know when BFS/DFS/Dijkstra is insufficient. No HLD. " + JAVA_PRIMARY
    ),
    mastery=[
        "State one situation needing more than vanilla BFS/DFS.",
        "Solve 2 Advanced Graphs NeetCode problems.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-advanced-graphs", "Strongly Connected Components / Bridges"),
        nc150("dsa-advanced-graphs", "Advanced Graphs"),
    ],
    questions=[
        q("dsa-advanced-graphs-q1",
          "SCC identifies:",
          ["Maximal mutually reachable vertex groups in directed graphs.",
           "MST components.", "Bipartite color classes only.", "Shortest paths."],
          "Maximal mutually reachable vertex groups in directed graphs.",
          "Course schedule III style recognition.",
          mastery=True),
        q("dsa-advanced-graphs-q2",
          "Bridge edge:",
          ["Removing it increases connected components.",
           "Any heavy edge.", "MST edge only.", "Self-loop."],
          "Removing it increases connected components.",
          "DFS low-link detection."),
        q("dsa-advanced-graphs-q3",
          "Articulation point:",
          ["Vertex whose removal splits the graph.",
           "Any high-degree node.", "Heap root.", "Trie node."],
          "Vertex whose removal splits the graph.",
          "Cut vertex."),
        q("dsa-advanced-graphs-q4",
          "Redundant Connection (undirected) often uses:",
          ["Union-find; last edge joining same component is redundant.",
           "Dijkstra.", "Trie.", "LCS."],
          "Union-find; last edge joining same component is redundant.",
          "Advanced Graphs practice."),
        q("dsa-advanced-graphs-q5",
          "Cheapest flights within K stops needs:",
          ["Shortest path with hop limit — Bellman-Ford style or BFS layers, not plain Dijkstra only.",
           "MST.", "SCC only.", "Topological sort only."],
          "Shortest path with hop limit — Bellman-Ford style or BFS layers, not plain Dijkstra only.",
          "Recognition over implementation drill."),
        q("dsa-advanced-graphs-q6",
          "Not required V1:",
          ["Heavy-light decomposition, fibonacci heaps, suffix automata.",
           "Knowing SCC name.", "Bridge definition.", "Union-find redundant edge."],
          "Heavy-light decomposition, fibonacci heaps, suffix automata.",
          "Career recognition depth."),
    ],
    exercises=[
        ex("dsa-advanced-graphs-ex1", "Advanced recognition",
           "Solve Redundant Connection and Cheapest Flights Within K Stops. "
           "On paper: label bridges in a tiny undirected graph. "
           "TRANSFER (internal): when would you run Kosaraju after course schedule fails?"),
    ],
)

_add(
    "dsa-advanced-dp",
    hours=1.0,
    objective="Recognize digit DP, tree DP, bitmask DP by name.",
    explanation=(
        RELEARN + " "
        "Bitmask DP when n ≤ ~20 and subsets matter. "
        "Tree DP when subproblems are subtrees. "
        "Digit DP for counting numbers with digit constraints. "
        "Interview recognition only — not mastery of every variant. " + JAVA_PRIMARY
    ),
    mastery=[
        "State when bitmask DP applies (small n).",
        "Name tree DP and digit DP situations.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-advanced-dp", "Dynamic Programming on subsets / advanced"),
        nc150("dsa-advanced-dp", "2-D DP"),
    ],
    questions=[
        q("dsa-advanced-dp-q1",
          "Bitmask DP state often includes:",
          ["A subset mask of processed items (n small).",
           "Entire input string duplicated.", "MST parent.", "Heap index only."],
          "A subset mask of processed items (n small).",
          "2^n states — n must be small.",
          mastery=True),
        q("dsa-advanced-dp-q2",
          "Traveling Salesperson (n≤15 interview toy) uses:",
          ["DP over (mask, last city).",
           "Greedy nearest neighbor always optimal.", "BFS only.", "Trie."],
          "DP over (mask, last city).",
          "Recognition, not full CP."),
        q("dsa-advanced-dp-q3",
          "Tree DP (e.g., house robber III):",
          ["DFS returns aggregated values per subtree.",
           "BFS layers only.", "Dijkstra.", "Sorting."],
          "DFS returns aggregated values per subtree.",
          "Post-order compute."),
        q("dsa-advanced-dp-q4",
          "Digit DP counts:",
          ["Numbers in range satisfying per-digit constraints.",
           "Only palindromes in arrays.", "Graph paths only.", "MST weight."],
          "Numbers in range satisfying per-digit constraints.",
          "Named only at V1."),
        q("dsa-advanced-dp-q5",
          "Out of V1 mastery gate:",
          ["Full contest digit DP implementations, Knuth optimization.",
           "Knowing bitmask idea.", "Tree DP on robber III.", "Small n subset idea."],
          "Full contest digit DP implementations, Knuth optimization.",
          "Boundaries."),
        q("dsa-advanced-dp-q6",
          "Partition to K equal subsets (n≤16) hint:",
          ["Bitmask/backtracking with pruning — subset sum structure.",
           "Always greedy.", "MST.", "Trie walk."],
          "Bitmask/backtracking with pruning — subset sum structure.",
          "Advanced recognition link to knapsack."),
        q("dsa-advanced-dp-q7",
          "When n in a subset problem is 25:",
          ["Bitmask 2^n is too large — look for greedy, meet-in-middle, or different state.",
           "Use bitmask anyway.", "Always DP table 2^n.", "Use trie."],
          "Bitmask 2^n is too large — look for greedy, meet-in-middle, or different state.",
          "Constraint reading."),
        q("dsa-advanced-dp-q8",
          "Tree DP post-order computes:",
          ["Children results before parent combines them.",
           "Parent before children always.", "Level order only.", "MST first."],
          "Children results before parent combines them.",
          "DFS post-order pattern."),
    ],
    exercises=[
        ex("dsa-advanced-dp-ex1", "Name the DP",
           "House Robber III: STATE, TRANSITION, BASE, ORDER, COMPLEXITY on paper (tree DP). "
           "For 5 prompts (TSP n=10, robber on tree, count numbers with digit 4, burst balloons, LCS), "
           "name DP type without coding all. "
           "TRANSFER (internal): choose bitmask vs 1D knapsack for n=12 subset partition."),
    ],
)

_add(
    "dsa-pattern-selection",
    hours=1.25,
    objective="Classify unseen prompts: hash, two pointers, window, graph, DP, greedy.",
    explanation=(
        RELEARN + " "
        "Read constraints and asks: counting vs optimization vs existence vs construction. "
        "Try greedy counterexample, DP state sketch, graph model, or hash/window. "
        + JAVA_PRIMARY
    ),
    mastery=[
        "Classify 5 unseen prompts on paper.",
        "Pick a pattern before coding in a timed drill.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-pattern-selection", "Problem solving strategies"),
        nc150("dsa-pattern-selection", "NeetCode 150"),
    ],
    questions=[
        q("dsa-pattern-selection-q1",
          "If a problem asks 'minimum number of coins' with arbitrary denominations:",
          ["Try greedy counterexample first → likely DP (unbounded knapsack style).",
           "Always two pointers.", "Always trie.", "Always MST."],
          "Try greedy counterexample first → likely DP (unbounded knapsack style).",
          "Connects greedy failure to DP.",
          mastery=True),
        q("dsa-pattern-selection-q2",
          "Sorted array pair sum target:",
          ["Two pointers opposite ends.",
           "Union-find.", "Segment tree.", "Bitmask DP."],
          "Two pointers opposite ends.",
          "Pattern recall."),
        q("dsa-pattern-selection-q3",
          "Shortest path non-negative weights:",
          ["Dijkstra with priority queue.",
           "Bellman-Ford first always.", "MST.", "Trie."],
          "Dijkstra with priority queue.",
          "Graph family selection."),
        q("dsa-pattern-selection-q4",
          "Contiguous subarray sum equals K (counts):",
          ["Prefix sum + hash map of counts.",
           "Only greedy.", "Only LCS.", "AVL tree."],
          "Prefix sum + hash map of counts.",
          "Hash pattern."),
        q("dsa-pattern-selection-q5",
          "Dependencies between courses:",
          ["Topological sort / cycle detect.",
           "MST.", "LIS.", "Bit trie."],
          "Topological sort / cycle detect.",
          "Graph pattern."),
        q("dsa-pattern-selection-q6",
          "First 15 minutes in interview:",
          ["Restate, examples, brute force, pattern, optimized approach, complexity.",
           "Code immediately.", "Skip tests.", "Only discuss C++."],
          "Restate, examples, brute force, pattern, optimized approach, complexity.",
          "Leads to hygiene topic."),
    ],
    exercises=[
        ex("dsa-pattern-selection-ex1", "Five-prompt drill",
           "Classify: (1) max subarray, (2) word break, (3) number of islands, "
           "(4) merge k sorted lists, (5) longest substring k distinct — pattern + why. "
           "Solve one problem from each chosen family (NeetCode). "
           "TRANSFER (internal): mixed set of 3 new prompts from a mock list."),
    ],
)

_add(
    "dsa-interview-hygiene",
    hours=1.0,
    objective="Present Java solutions with complexity, edges, and clear narration.",
    explanation=(
        RELEARN + " "
        "Talk while thinking: constraints, approach, complexity, tests. "
        "Java primary in interviews; mention C++ only if asked. "
        "Use NeetCode 150 as the verified interview list. Individual LeetCode problem URLs were not mapped "
        "(automated verification returned Cloudflare 403). Transfer with internal problems plus NeetCode. "
        + JAVA_PRIMARY
    ),
    mastery=[
        "Present one solution with complexity and test cases aloud.",
        "Run a timed mock with narration.",
        "Score >= 80% on the topic questions.",
    ],
    resources=[
        bari_primary("dsa-interview-hygiene", "Interview problem solving"),
        nc150("dsa-interview-hygiene", "NeetCode 150"),
    ],
    questions=[
        q("dsa-interview-hygiene-q1",
          "After coding, you should state:",
          ["Time and space complexity and key edge cases tested.",
           "Only 'done'.", "Compiler flags.", "Git history."],
          "Time and space complexity and key edge cases tested.",
          "Hygiene baseline.",
          mastery=True),
        q("dsa-interview-hygiene-q2",
          "Empty input edge case:",
          ["Discuss before coding; handle explicitly.",
           "Ignore.", "Assume n≥1 always.", "Only for DP."],
          "Discuss before coding; handle explicitly.",
          "Shows maturity."),
        q("dsa-interview-hygiene-q3",
          "Interviewer asks C++ when you coded Java:",
          ["Brief equivalence (vector/ArrayList, unordered_map/HashMap) if you know C++.",
           "Refuse.", "Rewrite entire course.", "Switch to Python only."],
          "Brief equivalence (vector/ArrayList, unordered_map/HashMap) if you know C++.",
          "You already know C++; keep it high level."),
        q("dsa-interview-hygiene-q4",
          "Stuck for 3 minutes:",
          ["State what you tried, ask for hint, or switch to brute force.",
           "Stay silent.", "Guess output.", "Change language randomly."],
          "State what you tried, ask for hint, or switch to brute force.",
          "Communication matters."),
        q("dsa-interview-hygiene-q5",
          "Test cases to mention:",
          ["Empty, single element, duplicates, max constraint sketch.",
           "Only large random.", "None.", "Only TLE case."],
          "Empty, single element, duplicates, max constraint sketch.",
          "Structured testing."),
        q("dsa-interview-hygiene-q6",
          "Primary implementation language in this curriculum:",
          ["Java.", "C++.", "Python only.", "SQL."],
          "Java.",
          "Matches Domain 1 + Domain 2 policy."),
    ],
    exercises=[
        ex("dsa-interview-hygiene-ex1", "Mock narration",
           "45-minute mock: pick 2 NeetCode 150 problems (different patterns). "
           "Narrate approach, code in Java, state complexity, list 4 test cases each. "
           "Optional: browse LeetCode study-plan hub for extra ordering ideas — no individual problem URLs required. "
           "TRANSFER (internal): record yourself explaining one old solution in under 5 minutes."),
    ],
)
