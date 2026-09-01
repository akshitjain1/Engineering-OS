"""Exact problems for every DSA topic, not a link to a problem set.

Why this exists
---------------
Every DSA topic's PRACTICE resource used to be one of two NeetCode collection
pages -- `practice/neetcode150` or `practice/coreSkills` -- and both were stored
with `exactness = EXACT`. That claim was false, and `pick_resource` believes it,
so the day's DSA block sent the learner to a list of 150 problems and left them
to guess which one trains today's topic. Picking the problem is the part the
curriculum is supposed to have already done.

The contract for an entry here
------------------------------
A problem is only listed under a topic if the topic's technique is *the* way the
problem is solved -- not merely a technique that could touch it. Every entry
names the expected LeetCode topic tags, and the loader refuses to write a row
unless LeetCode's own tags for that problem include one of them. So this file
cannot silently drift into wishful mapping: a wrong slug or a mis-filed problem
fails verification instead of reaching the learner.

Nothing here is invented. Slugs are checked against LeetCode's public GraphQL
endpoint, which also supplies the canonical title and difficulty, so titles are
never typed by hand. Problems behind LeetCode Premium are deliberately absent --
they resolve but the learner cannot open them.

Ordering inside a topic is the intended progression and is what order_index is
built from, so the first entry is what the day's DSA block actually opens.
Difficulty is non-decreasing down each list -- entry point, representative,
stretch -- and a test enforces that.
"""

from __future__ import annotations

#: topic slug -> {"technique": str, "problems": [(leetcode_slug, expected_tags, why)]}
#:
#: `expected_tags` are LeetCode's own tag slugs. At least one must appear in the
#: problem's real tag list or the loader drops the entry.
DSA_EXACT_PROBLEMS: dict[str, dict] = {
    # -- Foundations ------------------------------------------------------
    "dsa-algorithmic-thinking": {
        "technique": "Turning a stated problem into a procedure before writing code",
        "problems": [
            ("fizz-buzz", ["math", "string", "simulation"],
             "Smallest possible gap between a spec in words and a correct loop."),
            ("two-sum", ["array", "hash-table"],
             "Brute force first, then notice the repeated lookup -- the core move of the whole subject."),
            ("maximum-subarray", ["array", "dynamic-programming", "divide-and-conquer"],
             "Same input admits an O(n^2) and an O(n) reading; the gap is the lesson."),
        ],
    },
    "dsa-big-o": {
        "technique": "Counting work as a function of input size, not wall clock",
        "problems": [
            ("contains-duplicate", ["array", "hash-table", "sorting"],
             "Three correct solutions at O(n^2), O(n log n) and O(n) -- write all three and time them."),
            ("two-sum", ["array", "hash-table"],
             "The nested-loop and hash solutions differ only in what you are willing to store."),
            ("maximum-subarray", ["array", "dynamic-programming"],
             "Cubic, quadratic and linear versions all fit on one screen."),
        ],
    },
    "dsa-best-worst-average": {
        "technique": "Separating the input that is typical from the input that is adversarial",
        "problems": [
            ("kth-largest-element-in-an-array", ["array", "divide-and-conquer", "sorting", "quickselect"],
             "Quickselect is average O(n) and worst O(n^2) -- the canonical demonstration."),
            ("sort-an-array", ["array", "divide-and-conquer", "sorting"],
             "Compare a pivot-based sort against a merge sort on adversarial input."),
            ("search-in-rotated-sorted-array", ["array", "binary-search"],
             "Best case hits immediately; worst case still must be logarithmic."),
        ],
    },

    # -- Arrays -----------------------------------------------------------
    "dsa-array-traversal": {
        "technique": "One linear pass, carrying state as you go",
        "problems": [
            ("running-sum-of-1d-array", ["array", "prefix-sum"],
             "Carry one accumulator left to right. Nothing else."),
            ("richest-customer-wealth", ["array", "matrix"],
             "Nested traversal with a running maximum."),
            ("find-numbers-with-even-number-of-digits", ["array"],
             "Traverse and test each element -- the plainest possible scan."),
        ],
    },
    "dsa-array-insert-delete": {
        "technique": "In-place add and remove with a write pointer",
        "problems": [
            ("remove-element", ["array", "two-pointers"],
             "A write index trailing a read index -- the whole idea in one problem."),
            ("remove-duplicates-from-sorted-array", ["array", "two-pointers"],
             "Same write-pointer move, with a comparison guarding the write."),
            ("duplicate-zeros", ["array", "two-pointers"],
             "Shifting in place without a second array forces you to walk backwards."),
        ],
    },
    "dsa-prefix-sums": {
        "technique": "Precompute cumulative totals so any range answers in O(1)",
        "problems": [
            ("find-pivot-index", ["array", "prefix-sum"],
             "Left total and right total from one cumulative pass."),
            ("range-sum-query-immutable", ["array", "design", "prefix-sum"],
             "The data structure *is* the prefix array."),
            ("subarray-sum-equals-k", ["array", "hash-table", "prefix-sum"],
             "Prefix sums plus a hash of seen totals -- the pattern behind a whole family."),
        ],
    },
    "dsa-array-frequency": {
        "technique": "Counting occurrences and reasoning from the counts",
        "problems": [
            ("majority-element", ["array", "hash-table", "counting", "sorting"],
             "Count, then read the answer off the counts."),
            ("single-number", ["array", "bit-manipulation"],
             "Frequency reasoning that a hash map solves and XOR solves better."),
            ("top-k-frequent-elements", ["array", "hash-table", "counting", "heap-priority-queue"],
             "Build counts, then select over them -- counting as a first stage, not the answer."),
        ],
    },
    "dsa-array-patterns": {
        "technique": "The recurring shapes: running best, in-place rotate, merge from the back",
        "problems": [
            ("best-time-to-buy-and-sell-stock", ["array", "dynamic-programming"],
             "Running minimum and running best answer in one pass."),
            ("merge-sorted-array", ["array", "two-pointers", "sorting"],
             "Filling from the back is the trick worth internalising."),
            ("rotate-array", ["array", "math", "two-pointers"],
             "Three reversals -- a rearrangement that looks impossible in O(1) space until it doesn't."),
        ],
    },

    # -- Strings ----------------------------------------------------------
    "dsa-string-manipulation": {
        "technique": "Treating a string as an array you may not be allowed to resize",
        "problems": [
            ("reverse-string", ["two-pointers", "string"],
             "In-place reversal with two ends closing in."),
            ("length-of-last-word", ["string"],
             "Scanning from the right and handling trailing blanks."),
            ("reverse-words-in-a-string", ["two-pointers", "string"],
             "Tokenise, reverse, rejoin -- with the whitespace rules that trip people up."),
        ],
    },
    "dsa-string-frequency": {
        "technique": "Character counts as the comparison key",
        "problems": [
            ("valid-anagram", ["hash-table", "string", "sorting"],
             "Two strings are equal as multisets -- count and compare."),
            ("ransom-note", ["hash-table", "string", "counting"],
             "Counts must cover, not match exactly."),
            ("group-anagrams", ["array", "hash-table", "string", "sorting"],
             "The count vector becomes a dictionary key."),
        ],
    },
    "dsa-character-processing": {
        "technique": "Per-character classification and mapping",
        "problems": [
            ("to-lower-case", ["string"],
             "Character arithmetic with no library help."),
            ("reverse-vowels-of-a-string", ["two-pointers", "string"],
             "Two pointers that skip everything failing a character test."),
            ("roman-to-integer", ["hash-table", "math", "string"],
             "A per-character map plus one lookahead rule."),
        ],
    },
    "dsa-string-patterns": {
        "technique": "Finding structure inside a string: palindromes, prefixes, occurrences",
        "problems": [
            ("longest-common-prefix", ["array", "string", "trie"],
             "Compare columns across strings rather than strings across each other."),
            ("find-the-index-of-the-first-occurrence-in-a-string", ["two-pointers", "string", "string-matching"],
             "Naive matching first; it is the baseline every fast matcher is measured against."),
            ("longest-palindromic-substring", ["string", "dynamic-programming", "two-pointers"],
             "Expand around each centre -- the structure-finding move for palindromes."),
        ],
    },

    # -- Hashing ----------------------------------------------------------
    "dsa-hash-map": {
        "technique": "Trading memory for O(1) lookup by key",
        "problems": [
            ("two-sum", ["array", "hash-table"],
             "Store what you have seen so the complement is one lookup away."),
            ("isomorphic-strings", ["hash-table", "string"],
             "Two maps enforcing a bijection."),
            ("word-pattern", ["hash-table", "string"],
             "The same bijection idea across two different alphabets."),
        ],
    },
    "dsa-hash-set": {
        "technique": "Membership without counts",
        "problems": [
            ("contains-duplicate", ["array", "hash-table", "sorting"],
             "Seen-before is the entire question."),
            ("intersection-of-two-arrays", ["array", "hash-table", "sorting", "binary-search"],
             "Set semantics, including the deduplication."),
            ("longest-consecutive-sequence", ["array", "hash-table", "union-find"],
             "A set turns 'is n-1 present' into O(1) and an O(n log n) problem into O(n)."),
        ],
    },
    "dsa-frequency-maps": {
        "technique": "A map from value to count, then a decision over the map",
        "problems": [
            ("find-the-difference", ["hash-table", "string", "bit-manipulation", "sorting"],
             "Counts differ by exactly one character."),
            ("sort-characters-by-frequency", ["hash-table", "string", "sorting", "heap-priority-queue", "counting"],
             "Count, then order by the count."),
            ("top-k-frequent-elements", ["array", "hash-table", "counting", "bucket-sort"],
             "Counting is stage one; bucketing by count is stage two."),
        ],
    },
    "dsa-lookup-patterns": {
        "technique": "Precomputing a map so an inner loop collapses",
        "problems": [
            ("two-sum", ["array", "hash-table"],
             "The inner loop collapses because the complement is one lookup away."),
            ("4sum-ii", ["array", "hash-table"],
             "Two nested pairs beat four nested loops because one half is hashed."),
            ("subarray-sum-equals-k", ["array", "hash-table", "prefix-sum"],
             "The map holds prefix totals, not values -- the generalisation worth seeing."),
        ],
    },

    # -- Two pointers -----------------------------------------------------
    "dsa-two-pointers-opposite": {
        "technique": "Two indices starting at the ends and closing in",
        "problems": [
            ("valid-palindrome", ["two-pointers", "string"],
             "Ends move inward, skipping whatever does not count."),
            ("two-sum-ii-input-array-is-sorted", ["array", "two-pointers", "binary-search"],
             "Sortedness tells you which pointer to move -- the reason the pattern works at all."),
            ("container-with-most-water", ["array", "two-pointers", "greedy"],
             "Move the limiting side; proving that is safe is the exercise."),
        ],
    },
    "dsa-two-pointers-same": {
        "technique": "A slow write pointer trailing a fast read pointer",
        "problems": [
            ("move-zeroes", ["array", "two-pointers"],
             "Slow marks where the next kept value belongs."),
            ("is-subsequence", ["two-pointers", "string", "dynamic-programming"],
             "Two pointers over two sequences, only one of which advances on a miss."),
            ("remove-duplicates-from-sorted-array-ii", ["array", "two-pointers"],
             "The same shape with a counter, which is where most people slip."),
        ],
    },
    "dsa-two-pointers-partition": {
        "technique": "Rearranging around a predicate in one pass",
        "problems": [
            ("sort-array-by-parity", ["array", "two-pointers", "sorting"],
             "Two-way partition with the simplest possible predicate."),
            ("sort-colors", ["array", "two-pointers", "sorting"],
             "Dutch national flag -- three-way partition in a single pass."),
            ("partition-list", ["linked-list", "two-pointers"],
             "The same partition on a structure you cannot index."),
        ],
    },

    # -- Sliding window ---------------------------------------------------
    "dsa-window-fixed": {
        "technique": "A window of constant width sliding by one",
        "problems": [
            ("maximum-average-subarray-i", ["array", "sliding-window"],
             "Add the entering element, drop the leaving one."),
            ("find-all-anagrams-in-a-string", ["hash-table", "string", "sliding-window"],
             "Fixed width plus a count vector compared at each step."),
            ("permutation-in-string", ["hash-table", "two-pointers", "string", "sliding-window"],
             "The same machinery, phrased as a search."),
        ],
    },
    "dsa-window-variable": {
        "technique": "Grow the right edge, shrink the left only while the window is invalid",
        "problems": [
            ("longest-substring-without-repeating-characters", ["hash-table", "string", "sliding-window"],
             "The canonical grow/shrink loop."),
            ("minimum-size-subarray-sum", ["array", "binary-search", "sliding-window", "prefix-sum"],
             "Shrinking is the answer-producing step here, not just cleanup."),
            ("longest-repeating-character-replacement", ["hash-table", "string", "sliding-window"],
             "Validity depends on a count inside the window, not on the newest element."),
        ],
    },
    "dsa-window-frequency": {
        "technique": "Carrying a count map as window state",
        "problems": [
            ("fruit-into-baskets", ["array", "hash-table", "sliding-window"],
             "At most k distinct -- the count map decides validity."),
            ("permutation-in-string", ["hash-table", "sliding-window", "two-pointers"],
             "A matched-character counter avoids re-comparing the whole map."),
            ("minimum-window-substring", ["hash-table", "string", "sliding-window"],
             "The hardest version of exactly this state."),
        ],
    },

    # -- Linked lists -----------------------------------------------------
    "dsa-singly-linked-list": {
        "technique": "Walking a chain you can only follow forwards",
        "problems": [
            ("middle-of-the-linked-list", ["linked-list", "two-pointers"],
             "You cannot index, so you walk -- or walk twice as fast."),
            ("remove-linked-list-elements", ["linked-list", "recursion"],
             "A dummy head removes every edge case at once."),
            ("design-linked-list", ["linked-list", "design"],
             "Build the structure and the pointer bugs become yours to fix."),
        ],
    },
    "dsa-list-operations": {
        "technique": "Splice, delete and reorder by rewiring pointers",
        "problems": [
            ("remove-duplicates-from-sorted-list", ["linked-list"],
             "Delete in place while walking."),
            ("remove-nth-node-from-end-of-list", ["linked-list", "two-pointers"],
             "A gap between two pointers turns a two-pass problem into one pass."),
            ("odd-even-linked-list", ["linked-list"],
             "Two chains built simultaneously, then joined."),
        ],
    },
    "dsa-list-reversal": {
        "technique": "Turning links around with a three-pointer walk",
        "problems": [
            ("reverse-linked-list", ["linked-list", "recursion"],
             "prev / curr / next -- iterate it, then write it recursively."),
            ("palindrome-linked-list", ["linked-list", "two-pointers", "stack", "recursion"],
             "Find the middle, reverse the tail, compare -- reversal as a subroutine."),
            ("reverse-linked-list-ii", ["linked-list"],
             "Reversing a segment, where the boundary joins are the real work."),
        ],
    },
    "dsa-fast-slow": {
        "technique": "Two pointers advancing at different rates",
        "problems": [
            ("middle-of-the-linked-list", ["linked-list", "two-pointers"],
             "Fast reaches the end exactly as slow reaches the middle."),
            ("linked-list-cycle", ["hash-table", "linked-list", "two-pointers"],
             "If they ever meet, there is a loop."),
            ("find-the-duplicate-number", ["array", "two-pointers", "binary-search", "bit-manipulation"],
             "An array read as a linked list -- the pattern outside its usual home."),
        ],
    },
    "dsa-cycle-detection": {
        "technique": "Floyd meeting point, and turning it into an entry point",
        "problems": [
            ("linked-list-cycle", ["hash-table", "linked-list", "two-pointers"],
             "Detection only."),
            ("happy-number", ["hash-table", "math", "two-pointers"],
             "Cycle detection on a sequence with no nodes at all."),
            ("linked-list-cycle-ii", ["hash-table", "linked-list", "two-pointers"],
             "Where the loop starts -- the part with the proof worth understanding."),
        ],
    },
    "dsa-list-merge": {
        "technique": "Weaving sorted chains together",
        "problems": [
            ("merge-two-sorted-lists", ["linked-list", "recursion"],
             "The merge step, isolated."),
            ("add-two-numbers", ["linked-list", "math", "recursion"],
             "Simultaneous walk with a carry."),
            ("merge-k-sorted-lists", ["linked-list", "divide-and-conquer", "heap-priority-queue", "merge-sort"],
             "The same merge, applied pairwise or through a heap."),
        ],
    },

    # -- Stack ------------------------------------------------------------
    "dsa-stack-fundamentals": {
        "technique": "Last-in first-out as a way to remember what is unfinished",
        "problems": [
            ("valid-parentheses", ["string", "stack"],
             "The stack holds exactly what is still open."),
            ("baseball-game", ["array", "stack", "simulation"],
             "Straight simulation -- push, pop, read the top."),
            ("min-stack", ["stack", "design"],
             "Auxiliary state alongside the stack, in O(1)."),
        ],
    },
    "dsa-monotonic-stack": {
        "technique": "A stack kept sorted, popping whatever the new element invalidates",
        "problems": [
            ("next-greater-element-i", ["array", "hash-table", "stack", "monotonic-stack"],
             "The pattern with the answer written on the label."),
            ("daily-temperatures", ["array", "stack", "monotonic-stack"],
             "Indices on the stack, so you can measure the distance."),
            ("largest-rectangle-in-histogram", ["array", "stack", "monotonic-stack"],
             "Both boundaries from one monotonic pass."),
        ],
    },

    # -- Queue ------------------------------------------------------------
    "dsa-queue-deque": {
        "technique": "First-in first-out, and the double-ended version",
        "problems": [
            ("implement-queue-using-stacks", ["stack", "design", "queue"],
             "Two stacks amortise to a queue, which forces the FIFO contract to be explicit."),
            ("number-of-recent-calls", ["design", "queue", "data-stream"],
             "A sliding time window expressed purely as enqueue and dequeue."),
            ("design-circular-queue", ["array", "linked-list", "design", "queue"],
             "Fixed capacity with wraparound indices."),
        ],
    },
    "dsa-queue-bfs-relationship": {
        "technique": "A queue is what makes breadth-first order happen",
        "problems": [
            ("binary-tree-level-order-traversal", ["tree", "breadth-first-search", "binary-tree"],
             "The queue produces the levels; nothing else does."),
            ("rotting-oranges", ["array", "breadth-first-search", "matrix"],
             "Multi-source BFS, where the queue holds a whole frontier."),
            ("01-matrix", ["array", "dynamic-programming", "breadth-first-search", "matrix"],
             "Distance falls out of the order the queue imposes."),
        ],
    },

    # -- Recursion --------------------------------------------------------
    "dsa-recursion-model": {
        "technique": "Base case plus a strictly smaller subproblem",
        "problems": [
            ("fibonacci-number", ["math", "dynamic-programming", "recursion", "memoization"],
             "The definition is the recursion."),
            ("reverse-linked-list", ["linked-list", "recursion"],
             "Write it recursively after writing it iteratively, then compare."),
            ("powx-n", ["math", "recursion"],
             "Halving the exponent -- recursion that actually buys you something."),
        ],
    },
    "dsa-call-stack": {
        "technique": "What the machine remembers while a recursion is in flight",
        "problems": [
            ("binary-tree-inorder-traversal", ["stack", "tree", "depth-first-search", "binary-tree"],
             "Write it recursively, then with an explicit stack -- that stack is the call stack."),
            ("maximum-depth-of-binary-tree", ["tree", "depth-first-search", "binary-tree"],
             "Depth of recursion is literally the answer."),
            ("binary-tree-preorder-traversal", ["stack", "tree", "depth-first-search", "binary-tree"],
             "The order changes with where you touch the node relative to the calls."),
        ],
    },
    "dsa-recursive-trees": {
        "technique": "Solve for a node by asking its children",
        "problems": [
            ("same-tree", ["tree", "depth-first-search", "binary-tree"],
             "Two recursions walking in lockstep."),
            ("invert-binary-tree", ["tree", "depth-first-search", "binary-tree"],
             "Do the work then recurse, or the reverse -- both are correct here."),
            ("balanced-binary-tree", ["tree", "depth-first-search", "binary-tree"],
             "Returning two facts from one traversal instead of recomputing height."),
        ],
    },
    "dsa-recursion-to-iteration": {
        "technique": "Replacing the call stack with one you manage",
        "problems": [
            ("binary-tree-preorder-traversal", ["stack", "tree", "depth-first-search"],
             "The easiest conversion -- push right, then left."),
            ("binary-tree-inorder-traversal", ["stack", "tree", "depth-first-search"],
             "Harder: you must remember where you were, not just where to go."),
            ("flatten-binary-tree-to-linked-list", ["linked-list", "stack", "tree", "depth-first-search"],
             "Recursive and iterative differ enough to be worth writing both."),
        ],
    },

    # -- Backtracking -----------------------------------------------------
    "dsa-subsets": {
        "technique": "Choose or skip each element, undoing the choice on the way out",
        "problems": [
            ("subsets", ["array", "backtracking", "bit-manipulation"],
             "The include/exclude tree in its purest form."),
            ("subsets-ii", ["array", "backtracking", "bit-manipulation"],
             "Duplicates force an explicit skip rule after sorting."),
            ("combination-sum", ["array", "backtracking"],
             "Subsets with a running total and a pruning condition."),
        ],
    },
    "dsa-permutations": {
        "technique": "Order matters, so every unused element is a branch",
        "problems": [
            ("permutations", ["array", "backtracking"],
             "A used-marker and an undo after each call."),
            ("permutations-ii", ["array", "backtracking", "sorting"],
             "Skipping equal siblings is the only difference, and it is subtle."),
            ("letter-case-permutation", ["string", "backtracking", "bit-manipulation"],
             "A branch only where a character has two cases."),
        ],
    },
    "dsa-combinations": {
        "technique": "Order does not matter, so the recursion only moves forward",
        "problems": [
            ("combinations", ["backtracking"],
             "A start index is what stops you regenerating the same set."),
            ("combination-sum-ii", ["array", "backtracking", "sorting"],
             "Forward-only plus duplicate skipping."),
            ("letter-combinations-of-a-phone-number", ["hash-table", "string", "backtracking"],
             "One branch per digit -- a product, not a subset."),
        ],
    },
    "dsa-constraint-search": {
        "technique": "Prune the moment a partial answer becomes impossible",
        "problems": [
            ("word-search", ["array", "string", "backtracking", "depth-first-search", "matrix"],
             "Mark visited, recurse, unmark -- the undo is the whole difficulty."),
            ("palindrome-partitioning", ["string", "dynamic-programming", "backtracking"],
             "The constraint is checked before recursing, not after."),
            ("n-queens", ["array", "backtracking"],
             "Pruning is what makes it finish at all."),
        ],
    },

    # -- Sorting ----------------------------------------------------------
    # The three quadratic sorts have no dedicated LeetCode problem. These are
    # chosen because their constraints are small enough that a hand-written
    # O(n^2) sort passes, so you can submit the algorithm you are learning
    # rather than a library call.
    "dsa-bubble-sort": {
        "technique": "Repeated adjacent swaps until nothing is out of order",
        "problems": [
            ("height-checker", ["array", "sorting", "counting-sort"],
             "n is at most 100, so a hand-written bubble sort submits and passes."),
            ("sort-array-by-parity", ["array", "two-pointers", "sorting"],
             "Small input; bubble the odd values rightwards and watch the swap count."),
            ("sort-an-array", ["array", "divide-and-conquer", "sorting"],
             "Submit bubble sort here to see it time out -- that failure is the point."),
        ],
    },
    "dsa-selection-sort": {
        "technique": "Repeatedly select the minimum of the unsorted remainder",
        "problems": [
            ("height-checker", ["array", "sorting", "counting-sort"],
             "Small n, so the selection loop is submittable."),
            ("sort-the-people", ["array", "hash-table", "string", "sorting"],
             "Selection over one key while carrying a second array along."),
            ("minimum-number-of-moves-to-seat-everyone", ["array", "greedy", "sorting", "counting-sort"],
             "Sort both sides, then pair -- correctness does not depend on which sort."),
        ],
    },
    "dsa-insertion-sort": {
        "technique": "Grow a sorted prefix by inserting each next element into place",
        "problems": [
            ("height-checker", ["array", "sorting"],
             "Small n makes the direct implementation viable -- write the loop, submit it."),
            ("insertion-sort-list", ["linked-list", "sorting"],
             "Insertion sort by name, on a structure where shifting is free."),
            ("insert-interval", ["array"],
             "Insertion into a sorted sequence, with merging as the twist."),
        ],
    },
    "dsa-merge-sort": {
        "technique": "Split, sort each half, merge",
        "problems": [
            ("merge-sorted-array", ["array", "two-pointers", "sorting"],
             "The merge step alone, with no recursion around it yet."),
            ("sort-list", ["linked-list", "two-pointers", "divide-and-conquer", "sorting", "merge-sort"],
             "Merge sort is the natural fit here, since a list cannot be indexed for a pivot."),
            ("count-of-smaller-numbers-after-self", ["array", "binary-search", "divide-and-conquer", "merge-sort"],
             "Counting during the merge -- the classic non-obvious use."),
        ],
    },
    "dsa-quick-sort": {
        "technique": "Partition around a pivot, recurse on both sides",
        "problems": [
            ("sort-colors", ["array", "two-pointers", "sorting"],
             "The partition step, isolated and three-way."),
            ("sort-an-array", ["array", "divide-and-conquer", "sorting"],
             "A real quicksort, where pivot choice decides whether you pass."),
            ("kth-largest-element-in-an-array", ["array", "divide-and-conquer", "sorting", "quickselect"],
             "Quickselect -- recurse on one side only."),
        ],
    },
    "dsa-heap-sort": {
        "technique": "Build a heap, then repeatedly extract the extreme",
        "problems": [
            ("last-stone-weight", ["array", "heap-priority-queue"],
             "Extract the two largest, repeatedly -- heap behaviour with nothing else attached."),
            ("kth-largest-element-in-an-array", ["array", "sorting", "heap-priority-queue"],
             "A size-k heap instead of a full sort."),
            ("sort-an-array", ["array", "divide-and-conquer", "sorting", "heap-priority-queue"],
             "Write heapify and sift-down yourself here."),
        ],
    },
    "dsa-counting-radix": {
        "technique": "Sorting without comparisons, by bucketing on the value itself",
        "problems": [
            ("height-checker", ["array", "sorting", "counting-sort"],
             "Bounded values, so counting sort is the intended solution."),
            ("sort-colors", ["array", "two-pointers", "sorting"],
             "Three possible values -- counting sort in two passes."),
            ("maximum-gap", ["array", "sorting", "bucket-sort", "radix-sort"],
             "Linear-time sorting is what makes the required bound reachable."),
        ],
    },
    "dsa-sort-stability": {
        "technique": "Preserving the original order of equal keys, and why it matters",
        "problems": [
            ("relative-sort-array", ["array", "hash-table", "sorting", "counting-sort"],
             "Order among equals is dictated externally -- stability is the whole question."),
            ("sort-the-people", ["array", "hash-table", "string", "sorting"],
             "Sorting one array by another array's key."),
            ("sort-characters-by-frequency", ["hash-table", "string", "sorting", "counting"],
             "Ties on frequency expose whether your sort is stable."),
        ],
    },
    "dsa-sort-complexity": {
        "technique": "Comparison lower bounds, and when a custom comparator changes the problem",
        "problems": [
            ("largest-number", ["array", "string", "greedy", "sorting"],
             "The comparator is the algorithm; proving it is a valid ordering is the work."),
            ("sort-an-array", ["array", "divide-and-conquer", "sorting"],
             "Where the O(n log n) bound stops being theoretical."),
            ("merge-intervals", ["array", "sorting"],
             "Sorting first is what makes the linear sweep afterwards correct."),
        ],
    },

    # -- Binary search ----------------------------------------------------
    "dsa-binary-search-classic": {
        "technique": "Halve a sorted range until the target is found",
        "problems": [
            ("binary-search", ["array", "binary-search"],
             "The template, with nothing on top of it."),
            ("search-insert-position", ["array", "binary-search"],
             "Same loop, but the miss case now has to return something useful."),
            ("sqrtx", ["math", "binary-search"],
             "Binary search where there is no array at all."),
        ],
    },
    "dsa-binary-search-boundaries": {
        "technique": "Lower and upper bound, and getting the loop invariant right",
        "problems": [
            ("search-insert-position", ["array", "binary-search"],
             "Lower bound in disguise."),
            ("find-smallest-letter-greater-than-target", ["array", "binary-search"],
             "Upper bound, with wraparound."),
            ("find-first-and-last-position-of-element-in-sorted-array", ["array", "binary-search"],
             "Both bounds in one problem, which is where off-by-one errors surface."),
        ],
    },
    "dsa-first-last-occurrence": {
        "technique": "Binary search that keeps going after a hit",
        "problems": [
            ("first-bad-version", ["binary-search", "interactive"],
             "First true in a monotone predicate -- one boundary, nothing else."),
            ("find-first-and-last-position-of-element-in-sorted-array", ["array", "binary-search"],
             "Do not stop on equality -- keep narrowing toward the edge, twice."),
            ("peak-index-in-a-mountain-array", ["array", "binary-search"],
             "A boundary defined by a comparison with the neighbour."),
        ],
    },
    "dsa-search-on-answer": {
        "technique": "Binary search the answer, not the array, using a feasibility test",
        "problems": [
            ("koko-eating-bananas", ["array", "binary-search"],
             "Guess a rate, test feasibility, narrow -- the pattern stated plainly."),
            ("capacity-to-ship-packages-within-d-days", ["array", "binary-search"],
             "Same shape, and the feasibility check is a greedy sweep."),
            ("split-array-largest-sum", ["array", "binary-search", "dynamic-programming", "greedy"],
             "The hard version, where the feasibility test is the difficult half."),
        ],
    },
    "dsa-rotated-arrays": {
        "technique": "Binary search when sortedness holds on only one side of the midpoint",
        "problems": [
            ("find-minimum-in-rotated-sorted-array", ["array", "binary-search"],
             "Find the pivot before worrying about targets."),
            ("search-in-rotated-sorted-array", ["array", "binary-search"],
             "Decide which half is sorted, then whether the target lives there."),
            ("search-in-rotated-sorted-array-ii", ["array", "binary-search"],
             "Duplicates break the deciding test, and the fix is instructive."),
        ],
    },

    # -- Trees ------------------------------------------------------------
    "dsa-tree-terminology": {
        "technique": "Root, height, depth, leaf -- and counting them",
        "problems": [
            ("maximum-depth-of-binary-tree", ["tree", "depth-first-search", "binary-tree"],
             "Depth and height, distinguished by doing it."),
            ("binary-tree-preorder-traversal", ["stack", "tree", "depth-first-search"],
             "Naming the visit orders."),
            ("count-complete-tree-nodes", ["binary-search", "tree", "binary-tree"],
             "Complete versus full is a definition you have to use, not recite."),
        ],
    },
    "dsa-binary-trees": {
        "technique": "Node with two children, and recursion over that shape",
        "problems": [
            ("invert-binary-tree", ["tree", "depth-first-search", "binary-tree"],
             "The smallest tree mutation there is."),
            ("symmetric-tree", ["tree", "depth-first-search", "binary-tree"],
             "Two pointers, but into a tree."),
            ("binary-tree-level-order-traversal", ["tree", "breadth-first-search", "binary-tree"],
             "The other way to walk the same structure."),
        ],
    },
    "dsa-tree-dfs": {
        "technique": "Go deep first; the traversal order is where you touch the node",
        "problems": [
            ("binary-tree-inorder-traversal", ["stack", "tree", "depth-first-search"],
             "In-order, which for a BST is the sorted order."),
            ("path-sum", ["tree", "depth-first-search", "binary-tree"],
             "Carrying a running value down the recursion."),
            ("diameter-of-binary-tree", ["tree", "depth-first-search", "binary-tree"],
             "The answer is computed on the way back up, not on the way down."),
        ],
    },
    "dsa-tree-bfs": {
        "technique": "Level by level, with the queue holding one level at a time",
        "problems": [
            ("average-of-levels-in-binary-tree", ["tree", "breadth-first-search", "binary-tree"],
             "You must know where a level ends -- that is the whole technique."),
            ("binary-tree-right-side-view", ["tree", "breadth-first-search", "binary-tree"],
             "Last node of each level."),
            ("binary-tree-zigzag-level-order-traversal", ["tree", "breadth-first-search", "binary-tree"],
             "Same traversal, alternating output order."),
        ],
    },
    "dsa-tree-height": {
        "technique": "Height as a value returned upward through the recursion",
        "problems": [
            ("maximum-depth-of-binary-tree", ["tree", "depth-first-search", "binary-tree"],
             "One line once you see it."),
            ("minimum-depth-of-binary-tree", ["tree", "depth-first-search", "breadth-first-search"],
             "The half-leaf case makes the naive mirror image wrong."),
            ("balanced-binary-tree", ["tree", "depth-first-search", "binary-tree"],
             "Height plus a balance verdict from a single pass."),
        ],
    },
    "dsa-tree-paths": {
        "technique": "Accumulating a route from root to somewhere, then undoing it",
        "problems": [
            ("binary-tree-paths", ["string", "backtracking", "tree", "depth-first-search"],
             "Path building with an explicit undo."),
            ("path-sum-ii", ["backtracking", "tree", "depth-first-search", "binary-tree"],
             "Every root-to-leaf route with a target sum."),
            ("binary-tree-maximum-path-sum", ["dynamic-programming", "tree", "depth-first-search"],
             "A path that need not touch the root, which changes what you return."),
        ],
    },
    "dsa-tree-construction": {
        "technique": "Rebuilding a tree from the orders it was walked in",
        "problems": [
            ("convert-sorted-array-to-binary-search-tree", ["array", "divide-and-conquer", "tree", "binary-search-tree"],
             "The middle becomes the root -- construction at its simplest."),
            ("construct-binary-tree-from-preorder-and-inorder-traversal", ["array", "hash-table", "divide-and-conquer", "tree"],
             "Preorder gives the root, inorder gives the split."),
            ("maximum-binary-tree", ["array", "divide-and-conquer", "stack", "tree", "monotonic-stack"],
             "Construction driven by a maximum instead of a middle."),
        ],
    },

    # -- Binary search trees ----------------------------------------------
    "dsa-bst-search": {
        "technique": "The ordering invariant tells you which child to descend into",
        "problems": [
            ("search-in-a-binary-search-tree", ["tree", "binary-search-tree", "binary-tree"],
             "One comparison per level."),
            ("range-sum-of-bst", ["tree", "depth-first-search", "binary-search-tree"],
             "The invariant lets you prune whole subtrees."),
            ("lowest-common-ancestor-of-a-binary-search-tree", ["tree", "depth-first-search", "binary-search-tree"],
             "The split point is where the two targets diverge."),
        ],
    },
    "dsa-bst-insert": {
        "technique": "Descend to the empty slot the invariant points at",
        "problems": [
            ("convert-sorted-array-to-binary-search-tree", ["array", "divide-and-conquer", "binary-search-tree"],
             "Build one first -- repeated insertion versus balanced construction, and the shapes differ."),
            ("increasing-order-search-tree", ["stack", "tree", "depth-first-search", "binary-search-tree"],
             "Rebuilding by insertion in traversal order."),
            ("insert-into-a-binary-search-tree", ["tree", "binary-search-tree", "binary-tree"],
             "Insertion is a search that ran out of nodes."),
        ],
    },
    "dsa-bst-delete": {
        "technique": "The three deletion cases, and the successor swap",
        "problems": [
            ("delete-node-in-a-bst", ["tree", "binary-search-tree", "binary-tree"],
             "Leaf, one child, two children -- all three in one problem."),
            ("trim-a-binary-search-tree", ["tree", "depth-first-search", "binary-search-tree"],
             "Bulk deletion driven by the invariant."),
            ("binary-search-tree-to-greater-sum-tree", ["tree", "depth-first-search", "binary-search-tree"],
             "Reverse in-order, which is the same walk deletion relies on."),
        ],
    },
    "dsa-bst-validate": {
        "technique": "The invariant is a range constraint, not a parent comparison",
        "problems": [
            ("minimum-absolute-difference-in-bst", ["tree", "depth-first-search", "binary-search-tree"],
             "In-order makes the answer adjacent -- see the sorted sequence before you police it."),
            ("validate-binary-search-tree", ["tree", "depth-first-search", "binary-search-tree"],
             "Comparing only against the parent is the classic wrong answer."),
            ("recover-binary-search-tree", ["tree", "depth-first-search", "binary-search-tree"],
             "Find the two nodes that break the in-order sequence."),
        ],
    },
    "dsa-bst-ordered-properties": {
        "technique": "In-order traversal of a BST is sorted, and that is the tool",
        "problems": [
            ("kth-smallest-element-in-a-bst", ["tree", "depth-first-search", "binary-search-tree"],
             "Stop the in-order walk at k."),
            ("binary-search-tree-iterator", ["stack", "tree", "design", "binary-search-tree", "iterator"],
             "The in-order walk, paused and resumed on demand."),
            ("convert-bst-to-greater-tree", ["tree", "depth-first-search", "binary-search-tree"],
             "Right-to-left in-order with an accumulator."),
        ],
    },

    # -- Heaps and priority queues ----------------------------------------
    "dsa-heap-structure": {
        "technique": "A complete tree in an array, with the heap property on every node",
        "problems": [
            ("last-stone-weight", ["array", "heap-priority-queue"],
             "Push and pop the maximum, nothing more."),
            ("kth-largest-element-in-a-stream", ["tree", "design", "binary-search-tree", "heap-priority-queue"],
             "A bounded heap as a live data structure."),
            ("sort-an-array", ["array", "sorting", "heap-priority-queue"],
             "Implement sift-up and sift-down by hand here."),
        ],
    },
    "dsa-priority-queue": {
        "technique": "Always serve the most extreme item next",
        "problems": [
            ("kth-largest-element-in-an-array", ["array", "sorting", "heap-priority-queue"],
             "A size-k queue answers it without a full sort."),
            ("k-closest-points-to-origin", ["array", "math", "divide-and-conquer", "sorting", "heap-priority-queue"],
             "Priority by a computed key rather than the value itself."),
            ("design-twitter", ["hash-table", "linked-list", "design", "heap-priority-queue"],
             "A priority queue inside a larger design."),
        ],
    },
    "dsa-heapify": {
        "technique": "Turning an arbitrary array into a heap in linear time",
        "problems": [
            ("last-stone-weight", ["array", "heap-priority-queue"],
             "Build once from the whole array, then only pop."),
            ("kth-largest-element-in-an-array", ["array", "divide-and-conquer", "heap-priority-queue"],
             "Bottom-up build versus n pushes -- measure both."),
            ("sort-an-array", ["array", "sorting", "heap-priority-queue"],
             "Sift-down written out is the whole of heapify."),
        ],
    },
    "dsa-top-k": {
        "technique": "Keep exactly k, and evict the worst",
        "problems": [
            ("top-k-frequent-elements", ["array", "hash-table", "sorting", "heap-priority-queue", "bucket-sort"],
             "Count, then take k -- heap or buckets."),
            ("k-closest-points-to-origin", ["array", "sorting", "heap-priority-queue", "quickselect"],
             "The same selection with a distance key."),
            ("top-k-frequent-words", ["array", "hash-table", "string", "trie", "sorting", "heap-priority-queue"],
             "Ties broken lexicographically, which the comparator must encode."),
        ],
    },
    "dsa-heap-scheduling": {
        "technique": "A heap as the clock: whatever finishes or starts next comes off the top",
        "problems": [
            ("task-scheduler", ["array", "hash-table", "greedy", "sorting", "heap-priority-queue", "counting"],
             "Most frequent task first, cooldown enforced by the queue."),
            ("single-threaded-cpu", ["array", "sorting", "heap-priority-queue"],
             "Availability and priority as two separate orderings."),
            ("find-median-from-data-stream", ["two-pointers", "design", "sorting", "heap-priority-queue", "data-stream"],
             "Two heaps balanced against each other."),
        ],
    },

    # -- Graphs -----------------------------------------------------------
    "dsa-graph-representations": {
        "technique": "Adjacency list versus matrix, and grids as implicit graphs",
        "problems": [
            ("find-center-of-star-graph", ["graph"],
             "An edge list you must read as a structure."),
            ("find-if-path-exists-in-graph", ["depth-first-search", "breadth-first-search", "union-find", "graph"],
             "Build the adjacency list before you can traverse anything."),
            ("number-of-islands", ["array", "depth-first-search", "breadth-first-search", "union-find", "matrix"],
             "A grid is a graph whose edges you never store."),
        ],
    },
    "dsa-graph-bfs": {
        "technique": "Frontier by frontier, marking visited on enqueue",
        "problems": [
            ("number-of-islands", ["array", "breadth-first-search", "depth-first-search", "matrix"],
             "Flood fill, done breadth-first."),
            ("rotting-oranges", ["array", "breadth-first-search", "matrix"],
             "Many sources at once, and the level count is the answer."),
            ("word-ladder", ["hash-table", "string", "breadth-first-search"],
             "The graph is implicit -- neighbours are generated, not stored."),
        ],
    },
    "dsa-graph-dfs": {
        "technique": "Follow one path to exhaustion, then back out",
        "problems": [
            ("max-area-of-island", ["array", "depth-first-search", "breadth-first-search", "union-find", "matrix"],
             "The recursion returns a size, so the flood fill computes as it goes."),
            ("clone-graph", ["hash-table", "depth-first-search", "breadth-first-search", "graph"],
             "A visited map that stores copies, not just flags."),
            ("pacific-atlantic-water-flow", ["array", "depth-first-search", "breadth-first-search", "matrix"],
             "Two traversals from the edges inward, then intersected."),
        ],
    },
    "dsa-connected-components": {
        "technique": "Count how many traversals it takes to cover every node",
        "problems": [
            ("number-of-provinces", ["depth-first-search", "breadth-first-search", "union-find", "graph"],
             "Each unvisited node starts one more component."),
            ("number-of-islands", ["array", "depth-first-search", "union-find", "matrix"],
             "The same count on a grid."),
            ("count-sub-islands", ["array", "depth-first-search", "breadth-first-search", "union-find", "matrix"],
             "Components with a containment condition attached."),
        ],
    },
    "dsa-graph-cycle": {
        "technique": "A cycle is a back edge -- what that means differs for directed and undirected",
        "problems": [
            ("course-schedule", ["depth-first-search", "breadth-first-search", "graph", "topological-sort"],
             "Directed cycle detection, phrased as feasibility."),
            ("redundant-connection", ["depth-first-search", "breadth-first-search", "union-find", "graph"],
             "Undirected: the edge that closes a loop is the one union-find rejects."),
            ("find-eventual-safe-states", ["depth-first-search", "breadth-first-search", "graph", "topological-sort"],
             "Three-colour marking, which is cycle detection with memory."),
        ],
    },
    "dsa-bipartite": {
        "technique": "Two-colour the graph; a conflict proves it is not bipartite",
        "problems": [
            ("is-graph-bipartite", ["depth-first-search", "breadth-first-search", "union-find", "graph"],
             "Colour on traversal, fail on a same-colour edge."),
            ("possible-bipartition", ["depth-first-search", "breadth-first-search", "union-find", "graph"],
             "The same test wearing a word problem."),
        ],
    },
    "dsa-topological-sort": {
        "technique": "Order a DAG so every edge points forward",
        "problems": [
            ("course-schedule", ["depth-first-search", "breadth-first-search", "graph", "topological-sort"],
             "Does an order exist -- Kahn's in-degree loop answers it."),
            ("course-schedule-ii", ["depth-first-search", "breadth-first-search", "graph", "topological-sort"],
             "Produce the order, not just its existence."),
            ("minimum-height-trees", ["depth-first-search", "breadth-first-search", "graph", "topological-sort"],
             "Peeling leaves -- the same in-degree idea on an undirected graph."),
        ],
    },
    "dsa-union-find": {
        "technique": "Disjoint sets with path compression and union by rank",
        "problems": [
            ("number-of-provinces", ["depth-first-search", "union-find", "graph"],
             "Components without any traversal at all."),
            ("redundant-connection", ["depth-first-search", "union-find", "graph"],
             "Union fails exactly when the edge is redundant."),
            ("accounts-merge", ["array", "hash-table", "string", "depth-first-search", "union-find", "sorting"],
             "Union-find over strings, where the mapping is half the work."),
        ],
    },
    "dsa-unweighted-shortest": {
        "technique": "BFS gives shortest paths when every edge costs the same",
        "problems": [
            ("shortest-path-in-binary-matrix", ["array", "breadth-first-search", "matrix"],
             "Uniform cost, so the first arrival is optimal."),
            ("01-matrix", ["array", "dynamic-programming", "breadth-first-search", "matrix"],
             "Multi-source BFS computing a distance field."),
            ("word-ladder", ["hash-table", "string", "breadth-first-search"],
             "Shortest transformation, with neighbours generated on the fly."),
        ],
    },
    "dsa-dijkstra": {
        "technique": "A priority queue relaxing the cheapest frontier node first",
        "problems": [
            ("network-delay-time", ["depth-first-search", "breadth-first-search", "graph", "heap-priority-queue", "shortest-path"],
             "Textbook Dijkstra with weights that vary."),
            ("path-with-minimum-effort", ["array", "binary-search", "depth-first-search", "union-find", "heap-priority-queue", "matrix"],
             "Cost is a maximum along the path, not a sum -- the relaxation changes."),
            ("cheapest-flights-within-k-stops", ["dynamic-programming", "breadth-first-search", "graph", "heap-priority-queue", "shortest-path"],
             "An extra dimension in the state, which plain Dijkstra cannot carry."),
        ],
    },
    "dsa-mst": {
        "technique": "Cheapest edge set that keeps everything connected",
        "problems": [
            ("min-cost-to-connect-all-points", ["array", "union-find", "graph", "heap-priority-queue", "minimum-spanning-tree"],
             "Prim or Kruskal on a complete graph you never fully build."),
            ("find-critical-and-pseudo-critical-edges-in-minimum-spanning-tree", ["union-find", "graph", "sorting", "minimum-spanning-tree"],
             "Requires an MST routine you can call repeatedly."),
        ],
    },

    # -- Greedy -----------------------------------------------------------
    "dsa-greedy-reasoning": {
        "technique": "Take the locally best move and be able to say why it is safe",
        "problems": [
            ("assign-cookies", ["array", "greedy", "two-pointers", "sorting"],
             "Sort both sides and match smallest to smallest."),
            ("lemonade-change", ["array", "greedy"],
             "Spend the large notes first; the argument is one sentence."),
            ("best-time-to-buy-and-sell-stock-ii", ["array", "dynamic-programming", "greedy"],
             "Every upward step is worth taking, which is not obvious until proved."),
        ],
    },
    "dsa-greedy-exchange": {
        "technique": "Proving greedy by showing any optimal answer can be exchanged into yours",
        "problems": [
            ("jump-game", ["array", "dynamic-programming", "greedy"],
             "Track the furthest reachable index and never look back."),
            ("jump-game-ii", ["array", "dynamic-programming", "greedy"],
             "The exchange argument is what makes the interval jump correct."),
            ("gas-station", ["array", "greedy"],
             "The failure point tells you the answer -- and why no earlier start works."),
        ],
    },
    "dsa-interval-problems": {
        "technique": "Sort by an endpoint, then sweep",
        "problems": [
            ("merge-intervals", ["array", "sorting"],
             "Sort by start; overlap becomes adjacency."),
            ("insert-interval", ["array"],
             "Already sorted, so the sweep is all that is left."),
            ("non-overlapping-intervals", ["array", "dynamic-programming", "greedy", "sorting"],
             "Sort by end -- choosing the wrong key quietly gives wrong answers."),
        ],
    },
    "dsa-greedy-scheduling": {
        "technique": "Choosing what to run next so nothing later is blocked",
        "problems": [
            ("minimum-number-of-arrows-to-burst-balloons", ["array", "greedy", "sorting"],
             "Earliest end time, the scheduling classic."),
            ("task-scheduler", ["array", "hash-table", "greedy", "sorting", "counting"],
             "The most frequent task dictates the shape of the schedule."),
            ("course-schedule-iii", ["array", "greedy", "heap-priority-queue"],
             "Greedy with regret -- swap out the worst choice already made."),
        ],
    },
    "dsa-greedy-patterns": {
        "technique": "The recurring greedy shapes: partition, pair off, sort by a custom key",
        "problems": [
            ("partition-labels", ["hash-table", "two-pointers", "string", "greedy"],
             "Last occurrence defines the cut."),
            ("hand-of-straights", ["array", "hash-table", "greedy", "sorting"],
             "Always start a group at the smallest remaining card."),
            ("valid-parenthesis-string", ["string", "dynamic-programming", "stack", "greedy"],
             "Track a range of possible counts instead of one."),
        ],
    },

    # -- Dynamic programming ----------------------------------------------
    "dsa-dp-mindset": {
        "technique": "Spotting overlapping subproblems and optimal substructure",
        "problems": [
            ("climbing-stairs", ["math", "dynamic-programming", "memoization"],
             "The recursion is obvious; the repetition inside it is the discovery."),
            ("fibonacci-number", ["math", "dynamic-programming", "recursion", "memoization"],
             "Draw the call tree once and the whole subject clicks."),
            ("min-cost-climbing-stairs", ["array", "dynamic-programming"],
             "First problem where the choice at each step actually costs something."),
        ],
    },
    "dsa-memoization": {
        "technique": "Top-down recursion with answers cached on the way back",
        "problems": [
            ("fibonacci-number", ["math", "dynamic-programming", "recursion", "memoization"],
             "Add a dictionary to the naive version and watch it finish."),
            ("house-robber", ["array", "dynamic-programming"],
             "Write it top-down first; the state is the index."),
            ("word-break", ["array", "hash-table", "string", "dynamic-programming", "trie", "memoization"],
             "Without memoisation this is exponential and visibly so."),
        ],
    },
    "dsa-tabulation": {
        "technique": "Bottom-up, filling a table in dependency order",
        "problems": [
            ("climbing-stairs", ["math", "dynamic-programming", "memoization"],
             "Convert your memoised version into a loop."),
            ("min-cost-climbing-stairs", ["array", "dynamic-programming"],
             "The table is one dimensional and the order is forced."),
            ("unique-paths", ["math", "dynamic-programming", "combinatorics"],
             "Two dimensions, and the fill order becomes a real decision."),
        ],
    },
    "dsa-dp-state": {
        "technique": "Choosing what the subproblem index actually means",
        "problems": [
            ("house-robber", ["array", "dynamic-programming"],
             "State is the index; the choice is take or skip."),
            ("house-robber-ii", ["array", "dynamic-programming"],
             "A circular constraint solved by running the same DP twice."),
            ("best-time-to-buy-and-sell-stock-with-cooldown", ["array", "dynamic-programming"],
             "State needs a second dimension -- holding, sold, resting."),
        ],
    },
    "dsa-dp-transition": {
        "technique": "Writing the recurrence that links a state to smaller ones",
        "problems": [
            ("coin-change", ["array", "dynamic-programming", "breadth-first-search"],
             "One transition per coin, minimised."),
            ("decode-ways", ["string", "dynamic-programming"],
             "Two transitions with a validity condition on each."),
            ("longest-increasing-subsequence", ["array", "binary-search", "dynamic-programming"],
             "The O(n^2) transition is the honest starting point."),
        ],
    },
    "dsa-dp-1d": {
        "technique": "One index is enough to describe the subproblem",
        "problems": [
            ("house-robber", ["array", "dynamic-programming"],
             "The archetype."),
            ("coin-change", ["array", "dynamic-programming"],
             "Unbounded choices over a single axis."),
            ("word-break", ["array", "hash-table", "string", "dynamic-programming"],
             "The index is a position in the string."),
        ],
    },
    "dsa-dp-2d": {
        "technique": "Two indices, usually two sequences or a grid",
        "problems": [
            ("unique-paths", ["math", "dynamic-programming", "combinatorics"],
             "The smallest possible two-dimensional table."),
            ("longest-common-subsequence", ["string", "dynamic-programming"],
             "Two strings, so two indices -- the canonical pairing."),
            ("edit-distance", ["string", "dynamic-programming"],
             "Three transitions per cell, and every one of them matters."),
        ],
    },
    "dsa-subsequence-dp": {
        "technique": "Subsequences keep order but drop elements, so the state is a position pair",
        "problems": [
            ("is-subsequence", ["two-pointers", "string", "dynamic-programming"],
             "Greedy suffices, which is worth knowing before you reach for a table."),
            ("longest-common-subsequence", ["string", "dynamic-programming"],
             "Where the table becomes necessary."),
            ("distinct-subsequences", ["string", "dynamic-programming"],
             "Counting rather than maximising changes the recurrence."),
        ],
    },
    "dsa-knapsack": {
        "technique": "Capacity as one axis, items as the other",
        "problems": [
            ("partition-equal-subset-sum", ["array", "dynamic-programming"],
             "Subset-sum, which is 0/1 knapsack with a yes/no payoff."),
            ("target-sum", ["array", "dynamic-programming", "backtracking"],
             "Signs reduce to a subset-sum after one algebraic step."),
            ("coin-change-ii", ["array", "dynamic-programming"],
             "Unbounded knapsack, where the loop order decides what you count."),
        ],
    },
    "dsa-grid-dp": {
        "technique": "A table whose axes are the grid itself",
        "problems": [
            ("minimum-path-sum", ["array", "dynamic-programming", "matrix"],
             "Each cell depends on two neighbours."),
            ("unique-paths-ii", ["array", "dynamic-programming", "matrix"],
             "Obstacles make some states unreachable rather than merely costly."),
            ("maximal-square", ["array", "dynamic-programming", "matrix"],
             "The state is a property of the square ending at a cell."),
        ],
    },
    "dsa-interval-dp": {
        "technique": "The subproblem is a range, and you split it at every interior point",
        "problems": [
            ("longest-palindromic-subsequence", ["string", "dynamic-programming"],
             "Ranges shrinking from both ends."),
            ("burst-balloons", ["array", "dynamic-programming"],
             "Choosing what to do last, not first, is what makes it tractable."),
            ("minimum-cost-to-cut-a-stick", ["array", "dynamic-programming", "sorting"],
             "The same last-move-first inversion on a different story."),
        ],
    },
    "dsa-dp-optimization": {
        "technique": "Cutting the table down once you see which parts you reuse",
        "problems": [
            ("climbing-stairs", ["math", "dynamic-programming", "memoization"],
             "Rolling two variables instead of an array -- the smallest possible saving."),
            ("maximum-subarray", ["array", "dynamic-programming", "divide-and-conquer"],
             "Kadane is a DP that kept two variables."),
            ("longest-increasing-subsequence", ["array", "binary-search", "dynamic-programming"],
             "Binary search replaces the inner loop and the complexity drops."),
        ],
    },

    # -- Advanced patterns ------------------------------------------------
    "dsa-tries": {
        "technique": "A tree over characters, so prefixes are shared",
        "problems": [
            ("implement-trie-prefix-tree", ["hash-table", "string", "design", "trie"],
             "Build the structure before using it anywhere."),
            ("design-add-and-search-words-data-structure", ["string", "depth-first-search", "design", "trie"],
             "Wildcards turn lookup into a traversal."),
            ("word-search-ii", ["array", "string", "backtracking", "trie", "matrix"],
             "The trie prunes a backtracking search -- why tries earn their keep."),
        ],
    },
    "dsa-bit-manipulation": {
        "technique": "Treating an integer as a set of flags",
        "problems": [
            ("number-of-1-bits", ["divide-and-conquer", "bit-manipulation"],
             "n & (n-1) clears the lowest set bit."),
            ("single-number", ["array", "bit-manipulation"],
             "XOR cancels pairs -- the identity worth memorising."),
            ("counting-bits", ["dynamic-programming", "bit-manipulation"],
             "Bit tricks and DP meeting in one recurrence."),
        ],
    },
    "dsa-segment-tree-concept": {
        "technique": "A tree over ranges, so updates and range queries are both logarithmic",
        "problems": [
            ("range-sum-query-immutable", ["array", "design", "prefix-sum"],
             "Prefix sums first -- the baseline a segment tree has to beat."),
            ("range-sum-query-mutable", ["array", "design", "binary-indexed-tree", "segment-tree"],
             "Updates are what break prefix sums and justify the tree."),
            ("count-of-smaller-numbers-after-self", ["array", "binary-search", "divide-and-conquer", "binary-indexed-tree", "segment-tree", "merge-sort"],
             "A counting structure used during a traversal."),
        ],
    },
    "dsa-advanced-graphs": {
        "technique": "Weighted, layered and constrained graph problems",
        "problems": [
            ("network-delay-time", ["graph", "heap-priority-queue", "shortest-path"],
             "Dijkstra as a building block rather than the whole answer."),
            ("swim-in-rising-water", ["array", "binary-search", "depth-first-search", "union-find", "heap-priority-queue", "matrix"],
             "Binary search over a threshold, with connectivity as the test."),
            ("reconstruct-itinerary", ["depth-first-search", "graph", "eulerian-circuit"],
             "Eulerian path -- an ordering that only exists under a degree condition."),
        ],
    },
    "dsa-advanced-dp": {
        "technique": "Harder state spaces: strings, matching, and last-move-first inversions",
        "problems": [
            ("edit-distance", ["string", "dynamic-programming"],
             "The reference two-string DP."),
            ("regular-expression-matching", ["string", "dynamic-programming", "recursion"],
             "The transition depends on a lookahead, which breaks the usual template."),
            ("burst-balloons", ["array", "dynamic-programming"],
             "Interval DP at full difficulty."),
        ],
    },
    "dsa-pattern-selection": {
        "technique": "Reading a problem statement and naming the technique before coding",
        "problems": [
            ("3sum", ["array", "two-pointers", "sorting"],
             "Sorted plus two pointers, once you notice sorting is allowed."),
            ("longest-substring-without-repeating-characters", ["hash-table", "string", "sliding-window"],
             "The words contiguous and longest are the tell."),
            ("product-of-array-except-self", ["array", "prefix-sum"],
             "No division and O(n) forces prefix and suffix passes."),
        ],
    },
    "dsa-interview-hygiene": {
        "technique": "Clarify, state complexity, handle edges, test aloud",
        "problems": [
            ("two-sum", ["array", "hash-table"],
             "Short enough that the only thing to practise is how you talk through it."),
            ("valid-parentheses", ["string", "stack"],
             "Edge cases are where this one is won or lost."),
            ("merge-intervals", ["array", "sorting"],
             "Long enough to need a stated plan before you type."),
        ],
    },
}
