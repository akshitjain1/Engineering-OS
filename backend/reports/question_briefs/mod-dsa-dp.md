# Question brief: Dynamic Programming (`mod-dsa-dp`)

Subject: Data Structures & Algorithms
Topics: 12

For each topic below, write at least 4 self-check questions in
`content/questions/mod-dsa-dp.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `dsa-dp-mindset` — DP mindset

- Depth target: STRONG  ·  Track: CORE
- Objective: Recognize overlapping subproblems and optimal substructure.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. DP applies when naive recursion repeats work and optimal pieces compose. Write recurrence before code. MIT 6.006 SRTBOT: Subproblems, Relate, Topological order, Base, Original, Time. Implement in Java. C++ is an equivalence note, not a second curriculum.
- Resources:
  - **PRIMARY** MIT OpenCourseWare — MIT OpenCourseWare — Dynamic Programming (~10 min)
    https://ocw.mit.edu/courses/6-00sc-introduction-to-computer-science-and-programming-spring-2011/resources/lecture-23-dynamic-programming/
    exact part: 00:00 through 53:41
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Dynamic Programming / Fibonacci / Memoization (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 1-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 1 (SRTBOT) (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-15-dynamic-programming-part-1-srtbot-fib-dags-bowling/
  - **PRACTICE** LeetCode — 70. Climbing Stairs (~15 min)
    https://leetcode.com/problems/climbing-stairs/
  - **PRACTICE** LeetCode — 509. Fibonacci Number (~15 min)
    https://leetcode.com/problems/fibonacci-number/
  - **PRACTICE** LeetCode — 746. Min Cost Climbing Stairs (~15 min)
    https://leetcode.com/problems/min-cost-climbing-stairs/
- Currently has 10 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 7 more

## `dsa-memoization` — Memoization

- Depth target: STRONG  ·  Track: CORE
- Objective: Cache recursive DP results top-down in Java.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. Wrap recursion with a memo map or array; check before recomputing. Implement in Java. C++ is an equivalence note, not a second curriculum. Java HashMap ≈ C++ unordered_map; TreeMap ≈ map. Top-down is natural when state space is sparse or hard to order.
- Resources:
  - **PRIMARY** GeeksforGeeks — GFG — Memoization (1D, 2D and 3D) (~20 min)
    https://www.geeksforgeeks.org/dsa/memoization-1d-2d-and-3d/
    exact part: Data structures overview
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Dynamic Programming / Memoization (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 1-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 1 (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-15-dynamic-programming-part-1-srtbot-fib-dags-bowling/
  - **PRACTICE** LeetCode — 509. Fibonacci Number (~15 min)
    https://leetcode.com/problems/fibonacci-number/
  - **PRACTICE** LeetCode — 198. House Robber (~25 min)
    https://leetcode.com/problems/house-robber/
  - **PRACTICE** LeetCode — 139. Word Break (~25 min)
    https://leetcode.com/problems/word-break/
- Currently has 11 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 8 more

## `dsa-tabulation` — Tabulation

- Depth target: STRONG  ·  Track: CORE
- Objective: Fill a DP table bottom-up with correct iteration order.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. Tabulation iterates subproblems in topological order filling a table. Often avoids recursion stack limits. Implement in Java. C++ is an equivalence note, not a second curriculum.
- Resources:
  - **PRIMARY** NeetCode — NeetCode — Coin Change (~25 min)
    https://neetcode.io/solutions/coin-change
    exact part: Dynamic Programming; Bottom-Up Tabulation
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Dynamic Programming / Tabulation (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 1-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 1 (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-15-dynamic-programming-part-1-srtbot-fib-dags-bowling/
  - **PRACTICE** LeetCode — 70. Climbing Stairs (~15 min)
    https://leetcode.com/problems/climbing-stairs/
  - **PRACTICE** LeetCode — 746. Min Cost Climbing Stairs (~15 min)
    https://leetcode.com/problems/min-cost-climbing-stairs/
  - **PRACTICE** LeetCode — 62. Unique Paths (~25 min)
    https://leetcode.com/problems/unique-paths/
- Currently has 11 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 8 more

## `dsa-dp-state` — State definition

- Depth target: STRONG  ·  Track: CORE
- Objective: Choose a DP state that uniquely describes a subproblem.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. State = what you store per subproblem (index, capacity, last choice, etc.). Too small → wrong answer; too big → TLE/MLE. Implement in Java. C++ is an equivalence note, not a second curriculum.
- Resources:
  - **PRIMARY** GeeksforGeeks — Steps to solve a Dynamic Programming Problem (~10 min)
    https://www.geeksforgeeks.org/dsa/solve-dynamic-programming-problem/
    exact part: Step 2: Decide a state expression with the Least parameters. through Step 3: Formulate state and transition relationship.
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Dynamic Programming / 0/1 Knapsack state (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 1-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 1 (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-15-dynamic-programming-part-1-srtbot-fib-dags-bowling/
  - **PRACTICE** LeetCode — 198. House Robber (~25 min)
    https://leetcode.com/problems/house-robber/
  - **PRACTICE** LeetCode — 213. House Robber II (~25 min)
    https://leetcode.com/problems/house-robber-ii/
  - **PRACTICE** LeetCode — 309. Best Time to Buy and Sell Stock with Cooldown (~25 min)
    https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/
- Currently has 12 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 9 more

## `dsa-dp-transition` — Transition

- Depth target: STRONG  ·  Track: CORE
- Objective: Write recurrence transitions between DP states.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. Transition = how dp[state] combines smaller solved states (min/max/sum/or). Write the recurrence before loops. Implement in Java. C++ is an equivalence note, not a second curriculum.
- Resources:
  - **PRIMARY** GeeksforGeeks — Steps to solve a Dynamic Programming Problem (~10 min)
    https://www.geeksforgeeks.org/dsa/solve-dynamic-programming-problem/
    exact part: Step 3: Formulate state and transition relationship. through Step 4: Add memoization or tabulation.
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Dynamic Programming / Knapsack recurrence (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 1-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 2 (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-16-dynamic-programming-part-2-lcs-lis-coins/
  - **PRACTICE** LeetCode — 322. Coin Change (~25 min)
    https://leetcode.com/problems/coin-change/
  - **PRACTICE** LeetCode — 91. Decode Ways (~25 min)
    https://leetcode.com/problems/decode-ways/
  - **PRACTICE** LeetCode — 300. Longest Increasing Subsequence (~25 min)
    https://leetcode.com/problems/longest-increasing-subsequence/
- Currently has 12 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 9 more

## `dsa-dp-1d` — 1D DP

- Depth target: STRONG  ·  Track: CORE
- Objective: Solve linear 1D DP families in Java.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. 1D examples: stairs, robber, LIS, coin change, decode ways. Watch index direction and base cases. Implement in Java. C++ is an equivalence note, not a second curriculum.
- Resources:
  - **PRIMARY** GeeksforGeeks — GFG — Dynamic Programming (DP) Introduction (~27 min)
    https://www.geeksforgeeks.org/dsa/introduction-to-dynamic-programming-data-structures-and-algorithm-tutorials/
    exact part: 1D DP intro
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Dynamic Programming / 1D problems (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 1-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 2 (LIS, coins) (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-16-dynamic-programming-part-2-lcs-lis-coins/
  - **PRACTICE** LeetCode — 198. House Robber (~25 min)
    https://leetcode.com/problems/house-robber/
  - **PRACTICE** LeetCode — 322. Coin Change (~25 min)
    https://leetcode.com/problems/coin-change/
  - **PRACTICE** LeetCode — 139. Word Break (~25 min)
    https://leetcode.com/problems/word-break/
- Currently has 12 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 9 more

## `dsa-dp-2d` — 2D DP

- Depth target: STRONG  ·  Track: CORE
- Objective: Fill DP tables over two indices.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. 2D DP: two sequences, grid paths, paired prefixes. Nested loops follow dependency order. Implement in Java. C++ is an equivalence note, not a second curriculum.
- Resources:
  - **PRIMARY** GeeksforGeeks — Dynamic Programming (DP) on Grids (~10 min)
    https://www.geeksforgeeks.org/dsa/dp-on-grids/
    exact part: Idea behind Dynamic Programming (DP) on Grids through Iteratively filling the DP table
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Dynamic Programming / 2D tables (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 2-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 2 (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-16-dynamic-programming-part-2-lcs-lis-coins/
  - **PRACTICE** LeetCode — 62. Unique Paths (~25 min)
    https://leetcode.com/problems/unique-paths/
  - **PRACTICE** LeetCode — 1143. Longest Common Subsequence (~25 min)
    https://leetcode.com/problems/longest-common-subsequence/
  - **PRACTICE** LeetCode — 72. Edit Distance (~25 min)
    https://leetcode.com/problems/edit-distance/
- Currently has 12 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 9 more

## `dsa-subsequence-dp` — Subsequence DP

- Depth target: STRONG  ·  Track: CORE
- Objective: Handle LCS/LIS-style subsequence DP states.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. Subsequence allows skips — transitions usually consider match or skip. LCS, LIS, delete operations strings. Implement in Java. C++ is an equivalence note, not a second curriculum.
- Resources:
  - **PRIMARY** GeeksforGeeks — Longest Increasing Subsequence (LIS) (~10 min)
    https://www.geeksforgeeks.org/dsa/longest-increasing-subsequence-dp-3/
    exact part: Naive Approach through Using Dynamic Programming
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Longest Common Subsequence (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 2-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 2 (LCS) (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-16-dynamic-programming-part-2-lcs-lis-coins/
  - **PRACTICE** LeetCode — 392. Is Subsequence (~15 min)
    https://leetcode.com/problems/is-subsequence/
  - **PRACTICE** LeetCode — 1143. Longest Common Subsequence (~25 min)
    https://leetcode.com/problems/longest-common-subsequence/
  - **PRACTICE** LeetCode — 115. Distinct Subsequences (~40 min)
    https://leetcode.com/problems/distinct-subsequences/
- Currently has 12 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 9 more

## `dsa-knapsack` — Knapsack

- Depth target: STRONG  ·  Track: CORE
- Objective: Use 0/1 knapsack as a DP template; name unbounded variant.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. 0/1 knapsack: each item once. Unbounded: unlimited copies. Watch inner loop direction for 0/1 vs unbounded. Implement in Java. C++ is an equivalence note, not a second curriculum. Java int[] / ArrayList ≈ C++ vector (ArrayList grows; raw arrays are fixed).
- Resources:
  - **PRIMARY** GeeksforGeeks — GFG — 0/1 Knapsack Problem (~20 min)
    https://www.geeksforgeeks.org/dsa/0-1-knapsack-problem-dp-10/
    exact part: Data structures overview
  - **SUPPLEMENT** Abdul Bari — Abdul Bari — 4.5 0/1 Knapsack DP (~25 min)
    https://www.youtube.com/watch?v=nLmhmB6NzcM
  - **REFERENCE** NeetCode — NeetCode Core Skills — Unbounded Knapsack (~20 min)
    https://neetcode.io/practice/practice/coreSkills
  - **REFERENCE** NeetCode — NeetCode 150 — 1-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 4 (subset sum) (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-18-dynamic-programming-part-4-rods-subset-sum-pseudopolynomial/
  - **PRACTICE** LeetCode — 416. Partition Equal Subset Sum (~25 min)
    https://leetcode.com/problems/partition-equal-subset-sum/
  - **PRACTICE** LeetCode — 494. Target Sum (~25 min)
    https://leetcode.com/problems/target-sum/
  - **PRACTICE** LeetCode — 518. Coin Change II (~25 min)
    https://leetcode.com/problems/coin-change-ii/
- Currently has 12 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 9 more

## `dsa-grid-dp` — Grid DP

- Depth target: STRONG  ·  Track: CORE
- Objective: DP on grids: path counts, min cost, with obstacles.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. Grid DP uses cell (i,j) states; transitions from top/left (or four directions). Handle obstacles by skipping bad cells. Implement in Java. C++ is an equivalence note, not a second curriculum.
- Resources:
  - **PRIMARY** GeeksforGeeks — Dynamic Programming (DP) on Grids (~10 min)
    https://www.geeksforgeeks.org/dsa/dp-on-grids/
    exact part: Idea behind Dynamic Programming (DP) on Grids through Use Cases of Dynamic Programming (DP) on Grids
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Dynamic Programming / grid problems (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 2-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 2 (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-16-dynamic-programming-part-2-lcs-lis-coins/
  - **PRACTICE** LeetCode — 64. Minimum Path Sum (~25 min)
    https://leetcode.com/problems/minimum-path-sum/
  - **PRACTICE** LeetCode — 63. Unique Paths II (~25 min)
    https://leetcode.com/problems/unique-paths-ii/
  - **PRACTICE** LeetCode — 221. Maximal Square (~25 min)
    https://leetcode.com/problems/maximal-square/
- Currently has 12 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 9 more

## `dsa-interval-dp` — Interval DP concepts

- Depth target: STRONG  ·  Track: CORE
- Objective: Explain DP on intervals at a conceptual level.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. State is often dp[i][j] = best on subarray i..j. Fill by increasing length. Burst Balloons / palindrome partitions are interview recognition. Not full contest drill. Implement in Java. C++ is an equivalence note, not a second curriculum.
- Resources:
  - **PRIMARY** GeeksforGeeks — Matrix Chain Multiplication (~10 min)
    https://www.geeksforgeeks.org/dsa/matrix-chain-multiplication-dp-8/
    exact part: Better Approach 1] Using Top-Down DP (Memoization) through Better Approach 2] Using Bottom-Up DP (Tabulation)
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Matrix Chain Multiplication / interval DP (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 2-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 3 (parens) (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-17-dynamic-programming-part-3-apsp-parens-piano/
  - **PRACTICE** LeetCode — 516. Longest Palindromic Subsequence (~25 min)
    https://leetcode.com/problems/longest-palindromic-subsequence/
  - **PRACTICE** LeetCode — 312. Burst Balloons (~40 min)
    https://leetcode.com/problems/burst-balloons/
  - **PRACTICE** LeetCode — 1547. Minimum Cost to Cut a Stick (~40 min)
    https://leetcode.com/problems/minimum-cost-to-cut-a-stick/
- Currently has 12 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 9 more

## `dsa-dp-optimization` — DP optimization

- Depth target: STRONG  ·  Track: CORE
- Objective: Name space/time DP optimizations at V1 depth.
- Context: You already know DSA in C++. This is a rebuild of fundamentals for Java interviews and deeper reasoning, not a first course in programming. Rolling arrays, single-row updates, monotone deque for some 1D optimizations. No convex hull trick / Knuth optimization as mastery gates. Implement in Java. C++ is an equivalence note, not a second curriculum.
- Resources:
  - **PRIMARY** GeeksforGeeks — Count Unique Paths in a Grid (~10 min)
    https://www.geeksforgeeks.org/dsa/count-possible-paths-top-left-bottom-right-nxm-matrix/
    exact part: Better Approach: Using DP through Expected Approach: Using Combinatorics
  - **SUPPLEMENT** Abdul Bari — Abdul Bari Algorithms playlist — watch: Dynamic Programming / space optimization (~8 min)
    https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O
  - **REFERENCE** NeetCode — NeetCode 150 — 1-D DP (representative subset) (~20 min)
    https://neetcode.io/practice/practice/neetcode150
  - **DEEP_DIVE** MIT OCW 6.006 — MIT 6.006 — DP Part 4 (pseudopolynomial) (~10 min)
    https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-18-dynamic-programming-part-4-rods-subset-sum-pseudopolynomial/
  - **PRACTICE** LeetCode — 70. Climbing Stairs (~15 min)
    https://leetcode.com/problems/climbing-stairs/
  - **PRACTICE** LeetCode — 53. Maximum Subarray (~25 min)
    https://leetcode.com/problems/maximum-subarray/
  - **PRACTICE** LeetCode — 300. Longest Increasing Subsequence (~25 min)
    https://leetcode.com/problems/longest-increasing-subsequence/
- Currently has 12 question(s), to be replaced:
  - Overlapping subproblems mean:
  - Optimal substructure means:
  - Memoization vs tabulation:
  - ... and 9 more

