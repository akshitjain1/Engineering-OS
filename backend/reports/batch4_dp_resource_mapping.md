# Batch 4 DP Resource Mapping

Backup: `D:\Akshit Personal OS\backend\dev.db.pre_batch4_dp_resource_mapping_20260827_195640.bak` (3293184 bytes)

Topics updated: 8

| Topic | Old PRIMARY | New PRIMARY | URL | Boundary | Learner instruction |
|---|---|---|---|---|---|
| `dsa-dp-state` | `dsa-dp-state-learn-exact`: https://www.geeksforgeeks.org/dsa/solve-dynamic-programming-problem/ | `Steps to solve a Dynamic Programming Problem` | https://www.geeksforgeeks.org/dsa/solve-dynamic-programming-problem/ | Step 2: Decide a state expression with the Least parameters. through Step 3: Formulate state and transition relationship. | Learn how to define a DP state using the smallest set of parameters that uniquely describes a subproblem. Do the knapsack example mentally and explain what dp[index][capacity] means. |
| `dsa-dp-transition` | `dsa-dp-transition-learn-exact`: https://www.geeksforgeeks.org/dsa/solve-dynamic-programming-problem/ | `Steps to solve a Dynamic Programming Problem` | https://www.geeksforgeeks.org/dsa/solve-dynamic-programming-problem/ | Step 3: Formulate state and transition relationship. through Step 4: Add memoization or tabulation. | Learn how a DP transition converts smaller solved states into the current state. Be able to write a recurrence from the meaning of the state before thinking about code. |
| `dsa-advanced-dp` | `dsa-advanced-dp-learn-exact`: https://cp-algorithms.com/dynamic_programming/knuth-optimization.html | `CP-Algorithms — Knuth's Optimization` | https://cp-algorithms.com/dynamic_programming/knuth-optimization.html | FULL_SINGLE_PAGE | Treat this as an introduction to what advanced DP means: exploiting additional mathematical structure in a transition to reduce complexity. Understand range DP, optimal split points, the monotonicity condition, and why the optimization can reduce O(n^3) range DP to O(n^2). |
| `dsa-dp-2d` | `dsa-dp-2d-learn-exact`: https://www.geeksforgeeks.org/dsa/dp-on-grids/ | `Dynamic Programming (DP) on Grids` | https://www.geeksforgeeks.org/dsa/dp-on-grids/ | Idea behind Dynamic Programming (DP) on Grids through Iteratively filling the DP table | Learn why grid coordinates become DP states, how transitions come from neighbouring cells, how base cases are chosen, and how the 2D table is filled. |
| `dsa-subsequence-dp` | `dsa-subsequence-dp-learn-exact`: https://www.geeksforgeeks.org/dsa/longest-increasing-subsequence-dp-3/ | `Longest Increasing Subsequence (LIS)` | https://www.geeksforgeeks.org/dsa/longest-increasing-subsequence-dp-3/ | Naive Approach through Using Dynamic Programming | Learn the canonical subsequence-DP pattern using LIS: define what dp[i] means, compare previous elements, derive the recurrence, and understand why the state depends on earlier subsequences. |
| `dsa-grid-dp` | `dsa-grid-dp-learn-exact`: https://www.geeksforgeeks.org/dsa/dp-on-grids/ | `Dynamic Programming (DP) on Grids` | https://www.geeksforgeeks.org/dsa/dp-on-grids/ | Idea behind Dynamic Programming (DP) on Grids through Use Cases of Dynamic Programming (DP) on Grids | Learn the standard grid-DP pattern: cell as state, valid movement as transition, boundary/base conditions, and iterative computation. |
| `dsa-interval-dp` | `dsa-interval-dp-learn-exact`: https://www.geeksforgeeks.org/dsa/matrix-chain-multiplication-dp-8/ | `Matrix Chain Multiplication` | https://www.geeksforgeeks.org/dsa/matrix-chain-multiplication-dp-8/ | Better Approach 1] Using Top-Down DP (Memoization) through Better Approach 2] Using Bottom-Up DP (Tabulation) | Learn interval/range DP through Matrix Chain Multiplication. Focus on dp[i][j] representing an interval, trying every split k, combining the two subintervals, and filling states in increasing interval length. |
| `dsa-dp-optimization` | `dsa-dp-optimization-learn-exact`: https://www.geeksforgeeks.org/dsa/count-possible-paths-top-left-bottom-right-nxm-matrix/ | `Count Unique Paths in a Grid` | https://www.geeksforgeeks.org/dsa/count-possible-paths-top-left-bottom-right-nxm-matrix/ | Better Approach: Using DP through Expected Approach: Using Combinatorics | Focus on the space optimization idea: recognize when the current state depends only on the previous row/current left state, replace a full 2D table with a 1D array, and reason about the correct update order. |

## Unresolved items

- `dsa-dp-mindset`: NEEDS_BOUNDARY_VERIFICATION; unchanged because the repository does not contain the full duration for video `5dRGRueKU3M`.

## Learner data

Before: `{"diagnostic_answers": 76, "diagnostic_sessions": 1, "learning_activities": 323, "mastery_evidence": 95, "revision_schedules": 2, "topic_mastery": 80, "user_progress": 9, "user_xp": 1, "xp_events": 37}`

After: `{"diagnostic_answers": 76, "diagnostic_sessions": 1, "learning_activities": 323, "mastery_evidence": 95, "revision_schedules": 2, "topic_mastery": 80, "user_progress": 9, "user_xp": 1, "xp_events": 37}`

Unchanged: `True`

Curriculum graph unchanged: `True`

Tests: 223 passed, 1 warning in 320.67s

Lint: passed

Build: passed
