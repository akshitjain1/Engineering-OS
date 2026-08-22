"""Domain 2 DSA — Part 1: Algorithmic thinking through linked lists (28 topics)."""

from __future__ import annotations

from _d2_helpers import *

CONTENT = {}


def _add(slug, **kwargs):
    CONTENT[slug] = unit(**kwargs)


_MASTERY = [
    "Explain the core idea without notes (language-independent).",
    "Implement the pattern in Java without copying a solution.",
    "State the C++ equivalent structure at a high level where it applies.",
    "Solve 2–3 representative NeetCode 150 problems in the listed category.",
    "Transfer: solve a similar unseen problem without hints.",
    "State time and space complexity of your approach.",
    "Score >= 80% on topic questions.",
]


_add(
    "dsa-algorithmic-thinking",
    hours=1.0,
    objective="Approach problems with input/output, invariants, and worked examples before coding.",
    explanation=(
        RELEARN + " "
        "Algorithmic thinking is language-independent: define input and output, write two small examples "
        "(including an edge case), state an invariant or brute-force sketch, then choose a structure. "
        "You already decompose problems in C++; Java is the interview implementation language. "
        + JAVA_PRIMARY + " "
        "Watching Abdul Bari or MIT lectures clarifies vocabulary — it is not mastery."
    ),
    mastery=_MASTERY,
    resources=[
        bari_video("dsa-algorithmic-thinking", "Abdul Bari — 1. Introduction to Algorithms", BARI_INTRO),
        mit_dd("dsa-algorithmic-thinking", "MIT 6.006 Lecture 1 — Algorithms and Computation", MIT_L1),
    ],
    questions=[
        q(
            "dsa-algorithmic-thinking-q1",
            "Before writing Java for an unfamiliar prompt, what is the highest-value first step?",
            [
                "Memorize a LeetCode solution template.",
                "Define input/output, write two examples, and sketch brute force.",
                "Import every java.util class.",
                "Optimize for O(1) space immediately.",
            ],
            "Define input/output, write two examples, and sketch brute force.",
            "Concrete I/O and examples expose edge cases and guide structure choice.",
            mastery=True,
        ),
        q(
            "dsa-algorithmic-thinking-q2",
            "An invariant is best described as:",
            [
                "A Java keyword for loops.",
                "A condition that stays true across algorithm steps and justifies correctness.",
                "The worst-case time bound.",
                "A comment required by the compiler.",
            ],
            "A condition that stays true across algorithm steps and justifies correctness.",
            "Invariants connect each step to the final answer.",
            mastery=True,
        ),
        q(
            "dsa-algorithmic-thinking-q3",
            "You know the C++ solution uses std::unordered_map. In Java you should first ask:",
            [
                "Whether HashMap gives the same expected O(1) keyed lookup role.",
                "Whether Java has pointers.",
                "Whether to rewrite in assembly.",
                "Whether String is mutable.",
            ],
            "Whether HashMap gives the same expected O(1) keyed lookup role.",
            CPP["map"] + " Map the algorithmic role, not syntax trivia.",
        ),
        q(
            "dsa-algorithmic-thinking-q4",
            "Why write a brute-force version before optimizing?",
            [
                "Brute force is always the interview answer.",
                "It proves the problem is understood and gives a correctness baseline.",
                "Java cannot express optimized code without brute force first.",
                "NeetCode requires brute force submissions.",
            ],
            "It proves the problem is understood and gives a correctness baseline.",
            "Optimization without understanding risks subtle bugs.",
        ),
        q(
            "dsa-algorithmic-thinking-q5",
            "Edge cases in problem setup usually include:",
            [
                "Only inputs of length exactly 10.",
                "Empty input, single element, duplicates, and boundary indices.",
                "Only positive numbers.",
                "Only inputs that fit recursion depth 1000.",
            ],
            "Empty input, single element, duplicates, and boundary indices.",
            "Small degenerate inputs break naive loops and indexing.",
        ),
        q(
            "dsa-algorithmic-thinking-q6",
            "After watching an algorithms video, mastery requires:",
            [
                "Rewatching until the playlist ends.",
                "Implementing, tracing on paper, and solving representative problems.",
                "Bookmarking the video.",
                "Copying slides into notes without coding.",
            ],
            "Implementing, tracing on paper, and solving representative problems.",
            "Video is orientation; implementation and problems are mastery.",
            mastery=True,
        ),
    ],
    exercises=[
        ex(
            "dsa-algorithmic-thinking-ex1",
            "Problem setup drill",
            "IMPLEMENT: Write only the Java method signature (no body) for: given int[] nums and int target, "
            "return indices of two numbers that sum to target. "
            "TRACE/EXPLAIN: For nums=[2,7,11,15], target=9, document input, output, brute-force steps, "
            "and one invariant a one-pass HashMap approach would maintain. "
            "SOLVE: From NeetCode 150 Arrays & Hashing, solve Two Sum and Contains Duplicate. "
            "TRANSFER (internal): Package IDs arrive in order; find the first duplicate ID — outline approach "
            "and complexity without looking up a solution.",
        ),
    ],
)

_add(
    "dsa-big-o",
    hours=1.0,
    objective="Read and write simple big-O for loops and nested loops.",
    explanation=(
        RELEARN + " "
        "Big-O describes asymptotic growth: constant factors and lower terms drop out. "
        "Count dominant operations in loops — one loop over n is O(n), nested loops often O(n²). "
        "This formalizes Domain 0's complexity intro. Same reasoning in C++ and Java. "
        "Watching Time Complexity / Asymptotic Notation lectures is not mastery."
    ),
    mastery=_MASTERY,
    resources=[
        bari_primary("dsa-big-o", "Time Complexity / Asymptotic Notation"),
        mit_dd("dsa-big-o", "MIT 6.006 Lecture 1 — Algorithms and Computation", MIT_L1),
        mit_dd("dsa-big-o-l19", "MIT 6.006 Lecture 19 — Complexity", MIT_L19),
    ],
    questions=[
        q(
            "dsa-big-o-q1",
            "What is the time complexity of:\nfor (int i = 0; i < n; i++) { sum += a[i]; }",
            ["O(1)", "O(log n)", "O(n)", "O(n²)"],
            "O(n)",
            "Single loop visits each element once.",
            mastery=True,
        ),
        q(
            "dsa-big-o-q2",
            "What is the time complexity of:\nfor (int i = 0; i < n; i++)\n  for (int j = 0; j < n; j++)\n    count++;",
            ["O(n)", "O(n log n)", "O(n²)", "O(2^n)"],
            "O(n²)",
            "Outer and inner both run n times.",
            mastery=True,
        ),
        q(
            "dsa-big-o-q3",
            "Why do we ignore constants in big-O?",
            [
                "Constants are illegal in Java.",
                "As n grows, growth rate dominates fixed overhead.",
                "Only recursive algorithms have constants.",
                "Interviewers forbid constants.",
            ],
            "As n grows, growth rate dominates fixed overhead.",
            "O(2n) and O(n) are both linear asymptotically.",
        ),
        q(
            "dsa-big-o-q4",
            "A binary search on a sorted array of size n is:",
            ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
            "O(log n)",
            "Each step halves the search space.",
        ),
        q(
            "dsa-big-o-q5",
            "Space complexity counts:",
            [
                "Only heap allocations in C++.",
                "Extra memory used by the algorithm beyond input storage.",
                "Lines of source code.",
                "Number of public methods.",
            ],
            "Extra memory used by the algorithm beyond input storage.",
            "Auxiliary space matters for large inputs.",
        ),
        q(
            "dsa-big-o-q6",
            "O(n) + O(n) simplified is:",
            ["O(n²)", "O(2n)", "O(n)", "O(log n)"],
            "O(n)",
            "Same order class; constants dropped.",
        ),
    ],
    exercises=[
        ex(
            "dsa-big-o-ex1",
            "Complexity classification",
            "IMPLEMENT: Write three Java methods: (1) find max in int[] — O(n); (2) print all pairs i<j — O(n²); "
            "(3) binary search on sorted int[] — O(log n). Stub bodies are fine if you annotate complexity above each. "
            "TRACE/EXPLAIN: For n=8, how many times does the inner loop run in the pair printer? "
            "SOLVE: From NeetCode 150 Arrays & Hashing, classify time/space for Valid Anagram and Two Sum after solving. "
            "TRANSFER (internal): A function scans an array once and uses a HashMap of size at most k — state time and "
            "auxiliary space in terms of n and k.",
        ),
    ],
)

_add(
    "dsa-best-worst-average",
    hours=0.75,
    objective="Distinguish best, worst, and average case; default to worst-case in interviews.",
    explanation=(
        RELEARN + " "
        "The same algorithm can differ by input shape: quicksort is O(n log n) average but O(n²) worst on bad pivots. "
        "HashMap lookup is O(1) average but degrades with many collisions. "
        "Interviews usually ask worst-case unless stated otherwise. "
        "Abdul Bari's Frequency Count / analysis lectures and MIT L19 deepen this — not mastery alone."
    ),
    mastery=_MASTERY,
    resources=[
        bari_primary("dsa-best-worst-average", "Frequency Count / case analysis"),
        mit_dd("dsa-best-worst-average", "MIT 6.006 Lecture 19 — Complexity", MIT_L19),
    ],
    questions=[
        q(
            "dsa-best-worst-average-q1",
            "Linear search for a target in an unsorted array has worst-case time:",
            ["O(1)", "O(log n)", "O(n)", "O(n²)"],
            "O(n)",
            "Target may be last or absent — scan all n.",
            mastery=True,
        ),
        q(
            "dsa-best-worst-average-q2",
            "HashMap.get in Java is typically quoted as O(1) because:",
            [
                "It is always exactly one CPU instruction.",
                "Average-case expected constant time under good hashing.",
                "It uses a tree internally.",
                "Keys are always integers.",
            ],
            "Average-case expected constant time under good hashing.",
            "Worst-case can degrade with collisions; interviews often say expected O(1).",
        ),
        q(
            "dsa-best-worst-average-q3",
            "When an interviewer asks 'complexity?' without qualification, assume:",
            [
                "Best case",
                "Average case only",
                "Worst case",
                "Amortized case only for arrays",
            ],
            "Worst case",
            "Worst-case bounds are the safe default unless they specify average/amortized.",
            mastery=True,
        ),
        q(
            "dsa-best-worst-average-q3b",
            "Inserting at index 0 in ArrayList is O(n) worst-case because:",
            [
                "Java recompiles the class.",
                "Elements right of index 0 shift by one position.",
                "Hashing is required.",
                "ArrayList cannot insert.",
            ],
            "Elements right of index 0 shift by one position.",
            "Contiguous storage requires shifting — same as vector insert at front in C++.",
        ),
        q(
            "dsa-best-worst-average-q4",
            "Amortized O(1) append on ArrayList means:",
            [
                "Every single append is O(1) worst-case.",
                "Over many appends, average cost per append is constant though occasional resizes cost O(n).",
                "Append is impossible.",
                "Only works for sorted data.",
            ],
            "Over many appends, average cost per append is constant though occasional resizes cost O(n).",
            "Dynamic array doubling gives amortized constant append.",
        ),
        q(
            "dsa-best-worst-average-q5",
            "Best case for finding a target at index 0 in unsorted array:",
            ["O(1)", "O(log n)", "O(n)", "O(n²)"],
            "O(1)",
            "One comparison succeeds immediately — best ≠ worst.",
        ),
    ],
    exercises=[
        ex(
            "dsa-best-worst-average-ex1",
            "Case analysis",
            "IMPLEMENT: Write Java linearSearch(int[] a, int target) returning index or -1. "
            "TRACE/EXPLAIN: State best, worst, and average comparisons for random target not in array. "
            "SOLVE: After solving Contains Duplicate from NeetCode 150 Arrays & Hashing, state best/worst for "
            "sort-based vs HashSet-based approaches. "
            "TRANSFER (internal): Inserting into a sorted ArrayList at random positions — describe worst-case "
            "per insert and for n inserts.",
        ),
    ],
)

_add(
    "dsa-array-traversal",
    hours=0.75,
    objective="Scan an array in linear time without unnecessary copying.",
    explanation=(
        RELEARN + " "
        "Traversal is index-driven linear scan: forward, backward, or with a step. "
        + CPP["array"] + " "
        "Use enhanced for when you only need values; use index loops when you need i or in-place writes. "
        "No Domain 1 array syntax lesson — focus on algorithmic scans."
    ),
    mastery=_MASTERY,
    resources=[
        bari_primary("dsa-array-traversal", "Arrays / array analysis"),
        mit_dd("dsa-array-traversal", "MIT 6.006 Lecture 2 — Data Structures and Dynamic Arrays", MIT_L2),
        nccore("dsa-array-traversal", "Design Dynamic Array"),
        nc150("dsa-array-traversal", "Arrays & Hashing"),
    ],
    questions=[
        q(
            "dsa-array-traversal-q1",
            "What is the time to find the maximum of int[] a of length n?",
            ["O(1)", "O(log n)", "O(n)", "O(n²)"],
            "O(n)",
            "Must examine each element once in the worst case.",
            mastery=True,
        ),
        q(
            "dsa-array-traversal-q2",
            "Trace: int[] a = {3,1,4}; int s=0; for (int x : a) s+=x; Final s?",
            ["3", "4", "7", "8"],
            "8",
            "3+1+4=8.",
        ),
        q(
            "dsa-array-traversal-q3",
            "When must you use an indexed for-loop instead of enhanced for?",
            [
                "Never — enhanced for is always faster.",
                "When you need the index, modify elements in place, or scan two indices.",
                "Only for char arrays.",
                "Only when array length exceeds 1000.",
            ],
            "When you need the index, modify elements in place, or scan two indices.",
            "Enhanced for gives values only; in-place updates need indices.",
        ),
        q(
            "dsa-array-traversal-q4",
            "Reverse traversal from n-1 down to 0 is still:",
            ["O(1)", "O(log n)", "O(n)", "O(n²)"],
            "O(n)",
            "Direction does not change linear scan cost.",
        ),
        q(
            "dsa-array-traversal-q5",
            "Copying an entire int[] before scanning when mutation is forbidden costs:",
            ["O(1) time", "O(n) extra space", "O(n²) time", "No space"],
            "O(n) extra space",
            "A copy is linear auxiliary space.",
        ),
        q(
            "dsa-array-traversal-q6",
            "In C++ you used vector indexing; in Java raw int[] indexing:",
            [
                "Uses pointers like C++.",
                "Uses 0-based int indices with bounds checking on access.",
                "Is 1-based.",
                "Requires .at(i) only.",
            ],
            "Uses 0-based int indices with bounds checking on access.",
            "Same 0-based mental model; Java checks bounds on a[i].",
        ),
    ],
    exercises=[
        ex(
            "dsa-array-traversal-ex1",
            "Linear scans",
            "IMPLEMENT: max(int[]), countEvens(int[]), and reverseInPlace(int[]) in Java. "
            "TRACE/EXPLAIN: Dry-run reverseInPlace on [1,2,3,4] showing indices each swap. "
            "SOLVE: NeetCode 150 Arrays & Hashing — Product of Array Except Self and Valid Sudoku. "
            "TRANSFER (internal): Given daily temperatures, find days until warmer — name naive O(n²) and "
            "the later pattern that improves it.",
        ),
    ],
)

_add(
    "dsa-array-insert-delete",
    hours=0.75,
    objective="Explain insert/delete cost in contiguous arrays and dynamic arrays.",
    explanation=(
        RELEARN + " "
        "Contiguous arrays shift elements on middle insert/delete — O(n) worst case. "
        "ArrayList append is amortized O(1); insert at index i costs O(n-i). "
        + CPP["array"] + " Same shifting intuition as C++ vector."
    ),
    mastery=_MASTERY,
    resources=[
        bari_primary("dsa-array-insert-delete", "Arrays / insertion analysis"),
        mit_dd("dsa-array-insert-delete", "MIT 6.006 Lecture 2 — Data Structures and Dynamic Arrays", MIT_L2),
        nccore("dsa-array-insert-delete", "Design Dynamic Array"),
        nc150("dsa-array-insert-delete", "Arrays & Hashing"),
    ],
    questions=[
        q("dsa-array-insert-delete-q1", "Insert at index 0 in ArrayList size n — worst case:",
          ["O(1)", "O(log n)", "O(n)", "O(n²)"], "O(n)", "All elements shift right.", mastery=True),
        q("dsa-array-insert-delete-q2", "Append to ArrayList end is amortized O(1) because:",
          ["Never resizes", "Resize cost spread over many appends", "Uses linked nodes", "Is synchronized"],
          "Resize cost spread over many appends", "Doubling strategy.", mastery=True),
        q("dsa-array-insert-delete-q3", "Delete middle index requires:",
          ["Only nulling slot", "Shifting tail left", "Sorting", "Binary search"],
          "Shifting tail left", "Maintain contiguity."),
        q("dsa-array-insert-delete-q4", "vector::insert vs ArrayList.add(index):",
          ["Same O(n-i) shift cost for middle insert", "Java is always O(1)", "C++ never shifts", "Unrelated"],
          "Same O(n-i) shift cost for middle insert", "Contiguous storage behaves alike."),
        q("dsa-array-insert-delete-q5", "Frequent middle inserts favor:",
          ["Bigger array only", "Linked structure if node reference known", "HashSet", "Heap"],
          "Linked structure if node reference known", "Trade random access for local insert."),
        q("dsa-array-insert-delete-q6", "Remove last element from ArrayList:",
          ["O(1)", "O(log n)", "O(n)", "O(n²)"], "O(1)", "No shift of other elements."),
    ],
    exercises=[
        ex("dsa-array-insert-delete-ex1", "Dynamic array costs",
           "IMPLEMENT: NeetCode Core Skills — Design Dynamic Array. "
           "TRACE/EXPLAIN: Count copies when capacity doubles from 4 to 8 after 8 appends. "
           "SOLVE: NeetCode 150 — Remove Element and Move Zeroes. "
           "TRANSFER (internal): Text editor buffer insert at cursor — compare array vs list cost."),
    ],
)

_add(
    "dsa-prefix-sums",
    hours=1.0,
    objective="Build and query prefix sums for range-sum in O(1) after O(n) preprocess.",
    explanation=(
        RELEARN + " "
        "prefix[i] = sum(a[0..i]). Range l..r = prefix[r] - prefix[l-1] (l=0 → prefix[r]). "
        "O(n) build, O(1) query — same prefix array technique as C++."
    ),
    mastery=_MASTERY,
    resources=[
        bari_primary("dsa-prefix-sums", "Arrays / prefix analysis"),
        mit_dd("dsa-prefix-sums", "MIT 6.006 Lecture 2 — Data Structures and Dynamic Arrays", MIT_L2),
        nc150("dsa-prefix-sums", "Arrays & Hashing"),
    ],
    questions=[
        q("dsa-prefix-sums-q1", "sum(a[l..r]) with prefix (l>0):",
          ["prefix[r]", "prefix[r]-prefix[l-1]", "prefix[r]+prefix[l]", "a[r]-a[l]"],
          "prefix[r]-prefix[l-1]", "Subtract before l.", mastery=True),
        q("dsa-prefix-sums-q2", "Build prefix for n elements:",
          ["O(1)", "O(log n)", "O(n)", "O(n²)"], "O(n)", "Single pass."),
        q("dsa-prefix-sums-q3", "Trace a=[1,2,3,4]. prefix[2]?",
          ["3", "6", "10", "4"], "6", "1+2+3=6."),
        q("dsa-prefix-sums-q4", "Prefix sums excel when:",
          ["Many range queries on static data", "One query only", "Constant updates", "Only trees"],
          "Many range queries on static data", "Precompute once."),
        q("dsa-prefix-sums-q5", "1D prefix space:",
          ["O(1)", "O(log n)", "O(n)", "O(n²)"], "O(n)", "n stored values."),
        q("dsa-prefix-sums-q6", "Product Except Self uses prefix/suffix because:",
          ["Division banned or zero issues", "Cannot multiply", "Needs sort", "Needs stack"],
          "Division banned or zero issues", "Handles zeros safely."),
    ],
    exercises=[
        ex("dsa-prefix-sums-ex1", "Prefix array",
           "IMPLEMENT: buildPrefix and rangeSum in Java. "
           "TRACE/EXPLAIN: a=[2,-1,3,1], sum[1..2]. "
           "SOLVE: NeetCode 150 — Product of Array Except Self. "
           "TRANSFER (internal): Hourly rainfall range totals — preprocess/query plan."),
    ],
)

_add(
    "dsa-array-frequency",
    hours=0.75,
    objective="Count values with a fixed-size array when alphabet is bounded.",
    explanation=(
        RELEARN + " "
        "Small fixed domain → int[26], int[10], etc. O(1) update per element. "
        "Graduate to HashMap when keys are large or unbounded. Same counting array idea as C++."
    ),
    mastery=_MASTERY,
    resources=[
        bari_primary("dsa-array-frequency", "Frequency count"),
        mit_dd("dsa-array-frequency", "MIT 6.006 Lecture 2 — Data Structures and Dynamic Arrays", MIT_L2),
        nc150("dsa-array-frequency", "Arrays & Hashing"),
    ],
    questions=[
        q("dsa-array-frequency-q1", "Count lowercase letters length n with int[26]:",
          ["O(26n)", "O(n)", "O(n²)", "O(log n)"], "O(n)", "26 is constant.", mastery=True),
        q("dsa-array-frequency-q2", "freq[s.charAt(i)-'a']++ assumes:",
          ["Lowercase English", "Sorted input", "Mutable String", "UTF-32 only"],
          "Lowercase English", "Maps a-z to 0-25."),
        q("dsa-array-frequency-q3", "int[26] beats HashMap when:",
          ["Fixed small dense alphabet", "Arbitrary strings as keys", "Need order", "Huge alphabet"],
          "Fixed small dense alphabet", "Direct indexing wins."),
        q("dsa-array-frequency-q4", "Trace s='aab', freq[0] after count?",
          ["1", "2", "3", "0"], "2", "Two a's."),
        q("dsa-array-frequency-q5", "Valid Anagram with int[26] auxiliary space:",
          ["O(1)", "O(n)", "O(n²)", "O(log n)"], "O(1)", "26 buckets constant."),
        q("dsa-array-frequency-q6", "C++ int freq[26] vs Java int[26]:",
          ["Same counting pattern", "Java cannot count", "C++ uses HashMap only", "Unrelated"],
          "Same counting pattern", "Algorithm identical."),
    ],
    exercises=[
        ex("dsa-array-frequency-ex1", "Bounded counting",
           "IMPLEMENT: isAnagram with int[26]. TRACE: 'listen'/'silent'. "
           "SOLVE: NeetCode 150 — Valid Anagram. "
           "TRANSFER (internal): Digit frequency check for divisibility by 3."),
    ],
)

_add(
    "dsa-array-patterns",
    hours=1.0,
    objective="Recognize in-place scans and bridge patterns toward two pointers.",
    explanation=(
        RELEARN + " "
        "Patterns: compaction with write index, opposite pointers on sorted data, partition reorder. "
        "Foundation for two pointers and sliding window modules."
    ),
    mastery=_MASTERY,
    resources=[
        bari_primary("dsa-array-patterns", "Array techniques"),
        mit_dd("dsa-array-patterns", "MIT 6.006 Lecture 2 — Data Structures and Dynamic Arrays", MIT_L2),
        nc150("dsa-array-patterns", "Arrays & Hashing"),
    ],
    questions=[
        q("dsa-array-patterns-q1", "Remove-val in-place uses:",
          ["Write index for survivors", "Full copy always", "Sort first", "BFS"],
          "Write index for survivors", "Read/write compaction.", mastery=True),
        q("dsa-array-patterns-q2", "Compaction time:",
          ["O(1)", "O(log n)", "O(n)", "O(n²)"], "O(n)", "Single pass."),
        q("dsa-array-patterns-q3", "Sorted array + opposite pointers for:",
          ["Pair sum without O(n²) brute", "Only unsorted", "DFS", "Heap only"],
          "Pair sum without O(n²) brute", "Exploit order."),
        q("dsa-array-patterns-q4", "Dutch national flag is:",
          ["Partition multi-pointer", "Prefix only", "Hash only", "LL reverse"],
          "Partition multi-pointer", "Three-way partition."),
        q("dsa-array-patterns-q5", "Seen-before on unbounded values needs:",
          ["HashSet/HashMap", "int[10] always", "Sort only", "Stack only"],
          "HashSet/HashMap", "No fixed small alphabet."),
        q("dsa-array-patterns-q6", "Move Zeroes uses:",
          ["Write pointer compaction", "Sort", "Recursion", "Binary search"],
          "Write pointer compaction", "Same-direction pattern."),
    ],
    exercises=[
        ex("dsa-array-patterns-ex1", "Pattern recognition",
           "IMPLEMENT: removeDuplicatesSorted, moveZeroes. "
           "TRACE: Classify pointer directions. "
           "SOLVE: NeetCode 150 — Remove Duplicates from Sorted Array, Move Zeroes, Squares of a Sorted Array. "
           "TRANSFER (internal): Partition negatives before non-negatives in one pass."),
    ],
)

_add(
    "dsa-string-manipulation",
    hours=0.75,
    objective="Transform strings with clear index logic; treat as char sequences.",
    explanation=(
        RELEARN + " "
        + CPP["string"] + " "
        "DSA focus: index walks, substring views, two-pointer on chars. "
        "Use StringBuilder for assembly in loops — not a Domain 1 syntax lesson."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-string-manipulation", "Arrays & Hashing")],
    questions=[
        q("dsa-string-manipulation-q1", "Reverse a String algorithmically without extra String objects in loop:",
          ["Mutate String with +=", "StringBuilder or char[] swap", "Intern pool", "Only recursion"],
          "StringBuilder or char[] swap", "String is immutable.", mastery=True),
        q("dsa-string-manipulation-q2", "s.substring(i,j) in Java creates:",
          ["New String sharing/new char range", "Mutates s", "int only", "char primitive"],
          "New String sharing/new char range", "Immutability preserved."),
        q("dsa-string-manipulation-q3", "Compare strings by content in Java:",
          ["==", "equals", "compareTo only for identity", "hashCode only"],
          "equals", "== compares references."),
        q("dsa-string-manipulation-q4", "Two-pointer on palindrome checks:",
          ["Indices from both ends inward", "Only left to right", "Sort first", "Hash only"],
          "Indices from both ends inward", "Skip non-alphanumeric as needed."),
        q("dsa-string-manipulation-q5", "C++ string[i] mutable; Java String charAt:",
          ["Java needs char[]/StringBuilder to mutate chars", "Java mutates in place", "No difference", "Java forbids chars"],
          "Java needs char[]/StringBuilder to mutate chars", "Immutability difference."),
        q("dsa-string-manipulation-q6", "Trim/reverse scan complexity for length n:",
          ["O(1)", "O(log n)", "O(n)", "O(n²)"], "O(n)", "Touch each char once."),
    ],
    exercises=[
        ex("dsa-string-manipulation-ex1", "String transforms",
           "IMPLEMENT: isPalindrome ignoring case (a-z,0-9) with two indices. "
           "TRACE: 'A man, a plan, a canal: Panama'. "
           "SOLVE: NeetCode 150 — Valid Palindrome, Reverse String. "
           "TRANSFER (internal): Check if string can become palindrome by deleting at most one char."),
    ],
)

_add(
    "dsa-string-frequency",
    hours=0.75,
    objective="Count characters or tokens for anagram and frequency problems.",
    explanation=(
        RELEARN + " "
        "Character frequency drives anagrams, permutations-in-window, and multiset comparisons. "
        "int[26] or HashMap depending on alphabet — same counting logic as C++."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-string-frequency", "Arrays & Hashing")],
    questions=[
        q("dsa-string-frequency-q1", "Anagram equivalence means:",
          ["Same char multiset", "Same reference", "Same hashCode always", "Same length only"],
          "Same char multiset", "Order irrelevant.", mastery=True),
        q("dsa-string-frequency-q2", "Group Anagrams keys often use:",
          ["Sorted string or freq signature", "Random UUID", "Object identity", "length only"],
          "Sorted string or freq signature", "Buckets by canonical form."),
        q("dsa-string-frequency-q3", "After counting s and t, anagram check:",
          ["Compare freq arrays", "Compare references", "Sort both always required", "Use == on Strings"],
          "Compare freq arrays", "O(1) compare for fixed alphabet."),
        q("dsa-string-frequency-q4", "Trace: increment freq for 'a','b','a'. freq['a']?",
          ["1", "2", "3", "0"], "2", "Two a's."),
        q("dsa-string-frequency-q5", "Unicode note at V1 depth:",
          ["char is UTF-16 unit; anagram problems usually specify ASCII/lowercase", "Java has no char", "Always use byte[]", "Ignore encoding"],
          "char is UTF-16 unit; anagram problems usually specify ASCII/lowercase", "Stay within problem constraints."),
        q("dsa-string-frequency-q6", "Space for freq map on lowercase n-length string:",
          ["O(1) buckets or O(k) distinct", "O(n²)", "O(n log n)", "O(1) always for any alphabet"],
          "O(1) buckets or O(k) distinct", "Bounded alphabet → O(1); else O(k)."),
    ],
    exercises=[
        ex("dsa-string-frequency-ex1", "Character counts",
           "IMPLEMENT: groupAnagrams(List<String>) using freq signature or sorted key. "
           "TRACE: ['eat','tea','tan','ate','nat','bat'] buckets. "
           "SOLVE: NeetCode 150 — Group Anagrams, Valid Anagram, Ransom Note. "
           "TRANSFER (internal): Two strings — min deletions to make anagram."),
    ],
)

_add(
    "dsa-character-processing",
    hours=0.75,
    objective="Classify and map characters: case, digits, ASCII offsets.",
    explanation=(
        RELEARN + " "
        "char arithmetic: '0'..'9', 'a'..'z', Character.isLetterOrDigit. "
        "Map digits to ints with c-'0'. Same char classification as C++."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-character-processing", "Arrays & Hashing")],
    questions=[
        q("dsa-character-processing-q1", "Digit char to int:",
          ["c - '0'", "c + '0'", "Integer.parseInt(c)", "c / 0"],
          "c - '0'", "ASCII offset trick.", mastery=True),
        q("dsa-character-processing-q2", "Lowercase toggle at interview depth often uses:",
          ["Character.toLowerCase or manual offset", "Only regex", "String.intern", "Reflection"],
          "Character.toLowerCase or manual offset", "Be explicit about locale."),
        q("dsa-character-processing-q3", "isPalindrome skip non-alphanumeric:",
          ["Advance pointers while !isLetterOrDigit", "Delete all punctuation from String", "Sort", "HashMap"],
          "Advance pointers while !isLetterOrDigit", "Two-pointer skip."),
        q("dsa-character-processing-q4", "'A' and 'a' differ by:",
          ["32 in ASCII for Latin letters", "1 always", "256", "0"],
          "32 in ASCII for Latin letters", "Case bit pattern."),
        q("dsa-character-processing-q5", "C++ isdigit vs Java Character.isDigit:",
          ["Same role at problem level", "Unrelated", "Java has no digits", "C++ only"],
          "Same role at problem level", "Use problem's charset rules."),
        q("dsa-character-processing-q6", "Parsing multi-digit number from char array:",
          ["Accumulate res = res*10 + (c-'0')", "Concatenate Strings", "Only parseInt on whole string", "Impossible"],
          "Accumulate res = res*10 + (c-'0')", "Linear scan build."),
    ],
    exercises=[
        ex("dsa-character-processing-ex1", "Char transforms",
           "IMPLEMENT: atoi-style parseInts from char[] until non-digit. "
           "TRACE: \"-123abc\" → -123. "
           "SOLVE: NeetCode 150 — Valid Palindrome (skip/judge chars). "
           "TRANSFER (internal): Sum numbers separated by '+' in a string."),
    ],
)

_add(
    "dsa-string-patterns",
    hours=1.0,
    objective="Apply common string interview patterns as array-like problems.",
    explanation=(
        RELEARN + " "
        "Strings are immutable sequences: hashing, two pointers, sliding window all apply. "
        "Pattern recognition beats syntax drills."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-string-patterns", "Arrays & Hashing")],
    questions=[
        q("dsa-string-patterns-q1", "Longest substring without repeat uses:",
          ["Variable window + last-seen index/map", "Sort string", "Only brute O(n³)", "Stack only"],
          "Variable window + last-seen index/map", "Shrink when duplicate.", mastery=True),
        q("dsa-string-patterns-q2", "Anagram search in string often uses:",
          ["Fixed/variable window with freq match", "DFS on trie only", "Binary search on string", "Heap"],
          "Fixed/variable window with freq match", "Compare window counts to target."),
        q("dsa-string-patterns-q3", "String vs char[] for in-place swap:",
          ["char[] mutable; String needs new object", "Both mutable", "Neither works", "Only StringBuilder"],
          "char[] mutable; String needs new object", "Immutability constraint."),
        q("dsa-string-patterns-q4", "Encode strings pattern (NeetCode) tests:",
          ["Serialization with length delimiters", "Only sorting", "Graph BFS", "Union find"],
          "Serialization with length delimiters", "Parse with index discipline."),
        q("dsa-string-patterns-q5", "Treat string problems as array when:",
          ["You reason by indices and windows", "Never", "Only in C++", "Only for palindrome"],
          "You reason by indices and windows", "Same algorithmic patterns."),
        q("dsa-string-patterns-q6", "Valid Anagram pattern category:",
          ["Frequency / sorting multiset", "Graph shortest path", "Monotonic stack", "BST"],
          "Frequency / sorting multiset", "Counting pattern."),
    ],
    exercises=[
        ex("dsa-string-patterns-ex1", "String pattern set",
           "IMPLEMENT: lengthOfLongestSubstring (variable window sketch). "
           "TRACE: 'abcabcbb' window moves. "
           "SOLVE: NeetCode 150 — Longest Substring Without Repeating Characters, Valid Anagram, "
           "Encode and Decode Strings (read problem carefully). "
           "TRANSFER (internal): Longest substring with at most k distinct characters — outline window state."),
    ],
)

_add(
    "dsa-hash-map",
    hours=1.0,
    objective="Use HashMap for expected O(1) keyed lookup and counting.",
    explanation=(
        RELEARN + " "
        + CPP["map"] + " "
        "HashMap: put/get/remove average O(1). Keys need consistent equals/hashCode. "
        "Collisions handled internally — know expected vs worst case. "
        "Implement Design Hash Table via NeetCode Core Skills on this topic."
    ),
    mastery=_MASTERY,
    resources=[
        mit_dd("dsa-hash-map", "MIT 6.006 Lecture 4 — Hashing", MIT_L4),
        nccore("dsa-hash-map", "Design Hash Table"),
        nc150("dsa-hash-map", "Arrays & Hashing"),
    ],
    questions=[
        q("dsa-hash-map-q1", "HashMap.get average time:",
          ["O(1) expected", "O(log n) always", "O(n) always", "O(1) worst guaranteed"],
          "O(1) expected", "Hashing with collisions.", mastery=True),
        q("dsa-hash-map-q2", "Two Sum one-pass uses map to store:",
          ["Value → index seen so far", "Index → random", "Sorted order", "Heap top"],
          "Value → index seen so far", "Complement lookup.", mastery=True),
        q("dsa-hash-map-q3", "unordered_map in C++ closest Java analog:",
          ["HashMap", "TreeMap", "ArrayList", "PriorityQueue"],
          "HashMap", "Unordered keyed map."),
        q("dsa-hash-map-q4", "Bad String key equality (==) causes:",
          ["Silent wrong lookups", "Compile error always", "Faster code", "Automatic fix"],
          "Silent wrong lookups", "Use equals for content."),
        q("dsa-hash-map-q5", "map.put(k,v) if k exists:",
          ["Replaces value, returns old", "Throws always", "Ignores", "Duplicates key"],
          "Replaces value, returns old", "One key one slot."),
        q("dsa-hash-map-q6", "Frequency map space for n items k distinct keys:",
          ["O(k)", "O(1)", "O(n²)", "O(log n)"], "O(k)", "Stores each distinct key."),
        q("dsa-hash-map-q7", "When NOT to use HashMap:",
          ["Need sorted key order → TreeMap", "Need O(1) lookup", "Count frequencies", "Store complements"],
          "Need sorted key order → TreeMap", "TreeMap for ordering."),
    ],
    exercises=[
        ex("dsa-hash-map-ex1", "Hash map core",
           "IMPLEMENT: NeetCode Core Skills — Design Hash Table; then twoSum(int[], int) with HashMap. "
           "TRACE: nums=[2,7,11,15], target=9 map growth. "
           "SOLVE: NeetCode 150 — Two Sum, Group Anagrams. "
           "TRANSFER (internal): First non-repeating character in stream — map char→last index or count."),
    ],
)

_add(
    "dsa-hash-set",
    hours=0.75,
    objective="Use HashSet for O(1) expected membership tests.",
    explanation=(
        RELEARN + " "
        + CPP["set"] + " "
        "HashSet stores unique elements; add/contains/remove expected O(1). "
        "Use when you only need presence, not key→value."
    ),
    mastery=_MASTERY,
    resources=[
        mit_dd("dsa-hash-set", "MIT 6.006 Lecture 4 — Hashing", MIT_L4),
        nc150("dsa-hash-set", "Arrays & Hashing"),
    ],
    questions=[
        q("dsa-hash-set-q1", "Contains Duplicate in O(n) uses:",
          ["HashSet add/contains", "Nested loops only", "Sort only", "Stack"],
          "HashSet add/contains", "Detect repeat on insert.", mastery=True),
        q("dsa-hash-set-q2", "unordered_set ≈",
          ["HashSet", "TreeSet", "ArrayDeque", "HashMap"],
          "HashSet", "Unique unordered set."),
        q("dsa-hash-set-q3", "Set vs Map choose Set when:",
          ["Only membership needed", "Need counts per key", "Need key→value", "Need sorted keys"],
          "Only membership needed", "No associated value."),
        q("dsa-hash-set-q4", "HashSet allows:",
          ["One copy per equals-equal element", "Duplicates", "Null in generic Set<?> always forbidden", "Ordered iteration guaranteed"],
          "One copy per equals-equal element", "Uniqueness by equals/hashCode."),
        q("dsa-hash-set-q5", "Longest consecutive sequence uses set because:",
          ["O(1) check for x+1 neighbors", "Sets sort automatically", "Sets store order", "Maps forbidden"],
          "O(1) check for x+1 neighbors", "Only start of streak from x-1 absent."),
        q("dsa-hash-set-q6", "Space for set of n inserted elements:",
          ["O(n)", "O(1)", "O(log n)", "O(n²)"], "O(n)", "Stores each element."),
    ],
    exercises=[
        ex("dsa-hash-set-ex1", "Set membership",
           "IMPLEMENT: containsDuplicate(int[]) with HashSet. "
           "TRACE: [1,2,3,1] when duplicate found. "
           "SOLVE: NeetCode 150 — Contains Duplicate, Longest Consecutive Sequence. "
           "TRANSFER (internal): Return true if any value appears >=3 times — set or map choice."),
    ],
)

_add(
    "dsa-frequency-maps",
    hours=0.75,
    objective="Count with HashMap when alphabet is large or keys are non-char.",
    explanation=(
        RELEARN + " "
        "Map<T,Integer> freq when domain is not 26 letters — words, arbitrary ints, etc. "
        "getOrDefault / merge for increments. Same as unordered_map counting in C++."
    ),
    mastery=_MASTERY,
    resources=[
        mit_dd("dsa-frequency-maps", "MIT 6.006 Lecture 4 — Hashing", MIT_L4),
        nc150("dsa-frequency-maps", "Arrays & Hashing"),
    ],
    questions=[
        q("dsa-frequency-maps-q1", "Increment freq map idiom:",
          ["map.put(k, map.getOrDefault(k,0)+1)", "map[k]++ like C++ without get", "Only merge sort", "freq[256] always"],
          "map.put(k, map.getOrDefault(k,0)+1)", "Java lacks map[k]++.", mastery=True),
        q("dsa-frequency-maps-q2", "Top K Frequent uses freq map then:",
          ["Bucket sort by freq or heap", "Only sort keys alphabetically", "BFS", "Two pointers only"],
          "Bucket sort by freq or heap", "Extract top k by frequency."),
        q("dsa-frequency-maps-q3", "Array freq vs map freq:",
          ["Array when dense small domain; map when sparse/large", "Always map", "Always array", "Never count"],
          "Array when dense small domain; map when sparse/large", "Space tradeoff."),
        q("dsa-frequency-maps-q4", "Anagram with HashMap for Unicode-heavy input:",
          ["Still count keys", "Impossible", "Must sort only", "Use TreeMap only"],
          "Still count keys", "Map generalizes counting."),
        q("dsa-frequency-maps-q5", "Time to build freq of n words average length L with hashing:",
          ["O(nL) to process chars/tokens", "O(1)", "O(n²)", "O(log n)"],
          "O(nL) to process chars/tokens", "Touch each character/token."),
        q("dsa-frequency-maps-q6", "C++ unordered_map<char,int> ++ vs Java:",
          ["Java needs getOrDefault/merge", "Identical syntax", "Java cannot count", "C++ cannot count"],
          "Java needs getOrDefault/merge", "Syntax differs, logic same."),
    ],
    exercises=[
        ex("dsa-frequency-maps-ex1", "Frequency map",
           "IMPLEMENT: topKFrequent(int[] nums, int k) using HashMap + buckets or heap. "
           "TRACE: nums=[1,1,1,2,2,3], k=2. "
           "SOLVE: NeetCode 150 — Top K Frequent Elements, Group Anagrams. "
           "TRANSFER (internal): Most common word in log file — tokenize + freq map outline."),
    ],
)

_add(
    "dsa-lookup-patterns",
    hours=1.25,
    objective="Apply complement lookup, seen-set, and index-map patterns.",
    explanation=(
        RELEARN + " "
        "Classic patterns: one-pass complement (Two Sum), prefix+map (subarray sum), "
        "seen values for duplicates. Hashing as algorithmic tool — not Java API trivia."
    ),
    mastery=_MASTERY,
    resources=[
        mit_dd("dsa-lookup-patterns", "MIT 6.006 Lecture 4 — Hashing", MIT_L4),
        nc150("dsa-lookup-patterns", "Arrays & Hashing"),
    ],
    questions=[
        q("dsa-lookup-patterns-q1", "Two Sum one-pass checks:",
          ["target - nums[i] in map before adding i", "All pairs nested", "Sort only", "Stack"],
          "target - nums[i] in map before adding i", "Complement lookup.", mastery=True),
        q("dsa-lookup-patterns-q2", "Subarray sum equals k often uses:",
          ["Prefix sum + map of prefix→count", "Only brute force", "Heap", "DFS"],
          "Prefix sum + map of prefix→count", "Count prefixes with needed complement."),
        q("dsa-lookup-patterns-q3", "Seen-set on streaming values detects:",
          ["First repeat in O(1) amortized per step", "Sort order", "Median", "Shortest path"],
          "First repeat in O(1) amortized per step", "Membership test."),
        q("dsa-lookup-patterns-q4", "Why store index in Two Sum map:",
          ["Return original indices", "Sort requirement", "Hash stability", "Memory leak"],
          "Return original indices", "Problem asks for indices."),
        q("dsa-lookup-patterns-q5", "Lookup pattern fails if you use == on String keys:",
          ["Wrong bucket for equal content", "Faster", "Compile error", "Auto-fixed"],
          "Wrong bucket for equal content", "equals/hashCode contract."),
        q("dsa-lookup-patterns-q6", "3Sum reduces duplicate work by:",
          ["Sort + opposite pointers after fixing one element", "HashMap only O(n)", "Stack", "BFS"],
          "Sort + opposite pointers after fixing one element", "Combine hashing sort with two pointers."),
        q("dsa-lookup-patterns-q7", "Longest Consecutive uses set to:",
          ["Start streak only if x-1 not present", "Sort O(1)", "Store order", "Count primes"],
          "Start streak only if x-1 not present", "O(n) total with constant work per start."),
        q("dsa-lookup-patterns-q8", "Space-time trade: HashMap lookup vs nested loop:",
          ["O(n) time O(n) space vs O(n²) time O(1) space", "Always O(1) both", "Map always slower", "No tradeoff"],
          "O(n) time O(n) space vs O(n²) time O(1) space", "Classic interview tradeoff."),
    ],
    exercises=[
        ex("dsa-lookup-patterns-ex1", "Lookup drills",
           "IMPLEMENT: twoSum and subarraySum(int[], int k) with prefix+map. "
           "TRACE: Dry-run Two Sum and one prefix-map example. "
           "SOLVE: NeetCode 150 — Two Sum, Longest Consecutive Sequence, Subarray Sum Equals K (if listed). "
           "TRANSFER (internal): Find if array has duplicate within distance k — map value→last index."),
    ],
)

_add(
    "dsa-two-pointers-opposite",
    hours=1.0,
    objective="Move pointers from both ends on sorted or monotonic data.",
    explanation=(
        RELEARN + " "
        "Left/right pointers converge based on comparison — Two Sum II, container area, palindrome. "
        "Requires often sorted input or monotonic decision to move one side."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-two-pointers-opposite", "Two Pointers")],
    questions=[
        q("dsa-two-pointers-opposite-q1", "Two Sum II on sorted array uses:",
          ["Opposite pointers moving by sum compare", "HashMap only", "Stack", "BFS"],
          "Opposite pointers moving by sum compare", "Move low or high based on sum vs target.", mastery=True),
        q("dsa-two-pointers-opposite-q2", "Container With Most Water moves:",
          ["Pointer at shorter line inward", "Always left", "Always right", "Random"],
          "Pointer at shorter line inward", "Greedy height bottleneck."),
        q("dsa-two-pointers-opposite-q3", "Valid palindrome opposite pointers skip:",
          ["Non-alphanumeric as needed", "All chars including space", "Only vowels", "Digits only"],
          "Non-alphanumeric as needed", "Problem dependent."),
        q("dsa-two-pointers-opposite-q4", "Opposite pointers on sorted array time:",
          ["O(n)", "O(n²)", "O(log n)", "O(1)"], "O(n)", "Each pointer moves at most n steps."),
        q("dsa-two-pointers-opposite-q5", "Why sorting helps 3Sum outer loop:",
          ["Enables two-pointer on remainder with duplicate skip", "Required for HashMap", "No reason", "Makes O(1)"],
          "Enables two-pointer on remainder with duplicate skip", "Fix one value, pair scan."),
        q("dsa-two-pointers-opposite-q6", "C++ two iterators vs Java indices:",
          ["Same algorithmic idea", "Unrelated", "Java forbids two indices", "C++ only"],
          "Same algorithmic idea", "Index-based is fine in Java."),
    ],
    exercises=[
        ex("dsa-two-pointers-opposite-ex1", "Opposite pointers",
           "IMPLEMENT: twoSumSorted(int[], int) and maxArea(int[] height). "
           "TRACE: height=[1,8,6,2,5,4,8,3,7] pointer moves. "
           "SOLVE: NeetCode 150 Two Pointers — Two Sum II, Container With Most Water, Valid Palindrome. "
           "TRANSFER (internal): Sorted array — count pairs with sum < target."),
    ],
)

_add(
    "dsa-two-pointers-same",
    hours=1.0,
    objective="Advance read/write or slow/fast indexes in one direction.",
    explanation=(
        RELEARN + " "
        "Same-direction pointers: read scans all, write compacts; or slow/fast for in-place transforms. "
        "O(n) single pass, O(1) extra space typical."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-two-pointers-same", "Two Pointers")],
    questions=[
        q("dsa-two-pointers-same-q1", "Remove duplicates sorted in-place uses:",
          ["Write index for next unique", "HashSet copy", "Sort again", "Recursion"],
          "Write index for next unique", "Read/write same direction.", mastery=True),
        q("dsa-two-pointers-same-q2", "Move Zeroes pattern:",
          ["Write non-zeros then fill zeros", "Swap all pairs", "Sort", "Stack"],
          "Write non-zeros then fill zeros", "Compaction then optional zero fill."),
        q("dsa-two-pointers-same-q3", "Read always advances; write advances when:",
          ["Element kept / condition met", "Never", "Every iteration both++ always", "Only at end"],
          "Element kept / condition met", "Invariant: a[0..write) valid."),
        q("dsa-two-pointers-same-q4", "Time for read/write on length n:",
          ["O(n)", "O(n²)", "O(log n)", "O(1)"], "O(n)", "Single pass."),
        q("dsa-two-pointers-same-q5", "Squares of sorted array can use:",
          ["Two indices from ends writing to back", "Only sort after square", "BFS", "Union find"],
          "Two indices from ends writing to back", "Merge-like from largest squares."),
        q("dsa-two-pointers-same-q6", "Opposite vs same direction choice:",
          ["Depends on sorted pair search vs in-place compaction", "Always opposite", "Always same", "Random"],
          "Depends on sorted pair search vs in-place compaction", "Pattern recognition."),
    ],
    exercises=[
        ex("dsa-two-pointers-same-ex1", "Same-direction compaction",
           "IMPLEMENT: removeDuplicates(int[] sorted) and moveZeroes. "
           "TRACE: [0,1,0,3,12] read/write steps. "
           "SOLVE: NeetCode 150 — Remove Duplicates from Sorted Array, Move Zeroes, Squares of a Sorted Array. "
           "TRANSFER (internal): Compact array removing all occurrences of val in-place."),
    ],
)

_add(
    "dsa-two-pointers-partition",
    hours=1.0,
    objective="Partition arrays around a pivot or multi-way condition.",
    explanation=(
        RELEARN + " "
        "Lomuto/Hoare intuition, Dutch flag (0/1/2), quickselect preview. "
        "Pointers swap regions maintaining invariants — same partition thinking as C++."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-two-pointers-partition", "Two Pointers")],
    questions=[
        q("dsa-two-pointers-partition-q1", "Sort Colors (Dutch flag) maintains:",
          ["Regions [0..low) 0, [low..mid) 1, (high..] 2", "Sorted full array via sort()", "Heap property", "BST"],
          "Regions [0..low) 0, [low..mid) 1, (high..] 2", "Three-way partition.", mastery=True),
        q("dsa-two-pointers-partition-q2", "Partition around pivot p:",
          ["Elements <p left, >=p right (variant dependent)", "Always equal split", "Only recursion", "Hash only"],
          "Elements <p left, >=p right (variant dependent)", "Lomuto/Hoare variants."),
        q("dsa-two-pointers-partition-q3", "3Sum avoids duplicate triplets by:",
          ["Skip equal fixed i and equal l after moves", "Using Set only", "Sorting descending only", "BFS"],
          "Skip equal fixed i and equal l after moves", "Duplicate skip on sorted array."),
        q("dsa-two-pointers-partition-q4", "Partition in-place extra space:",
          ["O(1)", "O(n)", "O(n log n)", "O(n²)"], "O(1)", "Swaps only."),
        q("dsa-two-pointers-partition-q5", "QuickSort partition relates to:",
          ["This module's partition patterns", "Graph BFS", "Heapify only", "Trie"],
          "This module's partition patterns", "Preview of full quicksort later."),
        q("dsa-two-pointers-partition-q6", "Trapping Rain Water (two pointer variant) tracks:",
          ["Left/right max heights", "Only prefix sums always", "Hash frequencies", "Cycle detection"],
          "Left/right max heights", "Opposite pointers with max tracking."),
    ],
    exercises=[
        ex("dsa-two-pointers-partition-ex1", "Partition patterns",
           "IMPLEMENT: sortColors(int[] nums) Dutch flag. "
           "TRACE: [2,0,2,1,1,0] low/mid/high. "
           "SOLVE: NeetCode 150 — Sort Colors, 3Sum, Trapping Rain Water. "
           "TRANSFER (internal): Partition array into odds before evens in one pass."),
    ],
)

_add(
    "dsa-window-fixed",
    hours=1.0,
    objective="Maintain a window of fixed length k while scanning.",
    explanation=(
        RELEARN + " "
        "Fixed window: add entering element, subtract leaving element — O(n) not O(n·k). "
        "Applies to max in window (deque later), averages, anagram match length k."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-window-fixed", "Sliding Window")],
    questions=[
        q("dsa-window-fixed-q1", "Fixed window size k on length n: optimal scans:",
          ["O(n) with enter/leave updates", "O(nk) restart each position", "O(n²) always", "O(1)"],
          "O(n) with enter/leave updates", "Slide instead of recomputing.", mastery=True),
        q("dsa-window-fixed-q2", "First window sum indices 0..k-1, slide removes:",
          ["Element at i-k", "Element at i", "Element at 0 always", "Max element"],
          "Element at i-k", "Leave left end as i advances."),
        q("dsa-window-fixed-q3", "Permutation in String uses fixed window on:",
          ["s2 length over s1", "Entire string sort", "Graph", "Heap only"],
          "s2 length over s1", "Compare freq signatures."),
        q("dsa-window-fixed-q4", "Window invariant for fixed k:",
          ["Exactly k elements in current range", "At most k", "Unbounded", "Always full array"],
          "Exactly k elements in current range", "Size constant while sliding."),
        q("dsa-window-fixed-q5", "Naive re-sum each window costs:",
          ["O(nk)", "O(n)", "O(log n)", "O(1)"], "O(nk)", "Why sliding matters."),
        q("dsa-window-fixed-q6", "C++ sliding window vs Java:",
          ["Same index arithmetic on arrays/strings", "Java cannot slide", "Only C++", "Requires streams"],
          "Same index arithmetic on arrays/strings", "Language-agnostic pattern."),
        q("dsa-window-fixed-q7", "Find all anagrams uses window freq match:",
          ["Update enter/leave counts", "Sort each window O(k log k)", "DFS", "Union find"],
          "Update enter/leave counts", "O(1) count updates per slide."),
        q("dsa-window-fixed-q8", "When fixed window inappropriate:",
          ["Constraint is 'at most/longest' variable size", "k known constant", "Need linear scan", "String input"],
          "Constraint is 'at most/longest' variable size", "Use variable window instead."),
    ],
    exercises=[
        ex("dsa-window-fixed-ex1", "Fixed window",
           "IMPLEMENT: maxSumSubarrayOfSizeK(int[], int k) and checkInclusion(s1,s2) sketch. "
           "TRACE: nums=[2,1,5,1,3,2], k=3 sums slide. "
           "SOLVE: NeetCode 150 Sliding Window — Permutation in String, Find All Anagrams in a String. "
           "TRANSFER (internal): Average of all subarrays of length k in stream — O(1) update formula."),
    ],
)

_add(
    "dsa-window-variable",
    hours=1.25,
    objective="Grow and shrink window to satisfy at-most / at-least constraints.",
    explanation=(
        RELEARN + " "
        "Variable window: expand right until invalid, shrink left until valid. "
        "Tracks longest/shortest subarray satisfying constraint — two pointers as window boundaries."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-window-variable", "Sliding Window")],
    questions=[
        q("dsa-window-variable-q1", "Longest substring without repeat shrinks when:",
          ["Duplicate char enters window", "Window empty", "Always immediately", "Never"],
          "Duplicate char enters window", "Restore uniqueness invariant.", mastery=True),
        q("dsa-window-variable-q2", "Variable window vs restarting at each i:",
          ["Amortized O(n) pointer moves", "Same O(n²)", "Always O(n³)", "O(1)"],
          "Amortized O(n) pointer moves", "Each element enters/leaves once."),
        q("dsa-window-variable-q3", "Minimum window substring grows/shrinks to:",
          ["Cover all required chars then minimize", "Maximize length only", "Sort string", "DFS"],
          "Cover all required chars then minimize", "At-least constraint then shrink."),
        q("dsa-window-variable-q4", "Best Time to Buy/Sell Stock I is:",
          ["One pass min-so-far not classic window", "Fixed window k=2 always", "BFS", "Heap"],
          "One pass min-so-far not classic window", "Related linear scan; multi-day is kadane/window variants."),
        q("dsa-window-variable-q5", "Window [left,right] inclusive size:",
          ["right-left+1", "right-left", "left-right", "n always"],
          "right-left+1", "Count indices carefully."),
        q("dsa-window-variable-q6", "At-most K distinct uses:",
          ["Shrink when distinct > K", "Fixed size K always", "Sort", "Stack only"],
          "Shrink when distinct > K", "Variable until constraint met."),
        q("dsa-window-variable-q7", "Why not reset left to 0 each right:",
          ["Loses O(n) amortized benefit", "Required always", "Faster", "Java bug"],
          "Loses O(n) amortized benefit", "Monotonic left movement."),
        q("dsa-window-variable-q8", "Space for char-last-seen window:",
          ["O(alphabet) or O(k)", "O(1) always", "O(n²)", "O(n log n)"],
          "O(alphabet) or O(k)", "Map/array for last index or counts."),
    ],
    exercises=[
        ex("dsa-window-variable-ex1", "Variable window",
           "IMPLEMENT: lengthOfLongestSubstring and minWindow template sketch. "
           "TRACE: 'abcba' longest unique. "
           "SOLVE: NeetCode 150 — Longest Substring Without Repeating Characters, Minimum Window Substring, "
           "Longest Repeating Character Replacement. "
           "TRANSFER (internal): Longest subarray with sum <= S for positive ints — shrink when sum too large."),
    ],
)

_add(
    "dsa-window-frequency",
    hours=1.25,
    objective="Track counts or distinct values inside a sliding window.",
    explanation=(
        RELEARN + " "
        "Window state = frequency map or distinct counter updated on enter/leave. "
        "Needs hashing for general alphabets; int[] for small fixed sets."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-window-frequency", "Sliding Window")],
    questions=[
        q("dsa-window-frequency-q1", "On slide right, update freq by:",
          ["Increment enter char, decrement leave char", "Rebuild entire map", "Sort window", "Only increment"],
          "Increment enter char, decrement leave char", "O(1) per slide with map/array.", mastery=True),
        q("dsa-window-frequency-q2", "Anagram window match checks:",
          ["freq window equals target freq", "Sorted strings equal each slide O(k log k)", "Hash identity", "Length only"],
          "freq window equals target freq", "Multiset equality."),
        q("dsa-window-frequency-q3", "Distinct count in window can track:",
          ["Map count + distinct counter or freq array", "Only HashSet rebuild O(k)", "Stack", "BST only"],
          "Map count + distinct counter or freq array", "Avoid O(k) rebuild each step."),
        q("dsa-window-frequency-q4", "Character replacement window tracks:",
          ["Max freq in window vs window size", "Only left pointer", "Graph degrees", "Heap always required"],
          "Max freq in window vs window size", "k replacements = size - maxFreq <= k."),
        q("dsa-window-frequency-q5", "Remove leave char when count hits 0:",
          ["Delete key or decrement distinct", "Ignore", "Throw", "Sort"],
          "Delete key or decrement distinct", "Keep map accurate."),
        q("dsa-window-frequency-q6", "Fixed k anagram: space:",
          ["O(alphabet)", "O(n)", "O(n²)", "O(1) for any Unicode without map"],
          "O(alphabet)", "Bounded freq storage."),
        q("dsa-window-frequency-q7", "Minimum window needs freq of:",
          ["Required chars from t", "Entire s alphabet always", "Primes", "Indices only"],
          "Required chars from t", "Track coverage of target multiset."),
        q("dsa-window-frequency-q8", "C++ window freq vs Java HashMap:",
          ["Same enter/leave discipline", "Unrelated", "Java cannot slide", "C++ only arrays"],
          "Same enter/leave discipline", "Identical algorithm."),
    ],
    exercises=[
        ex("dsa-window-frequency-ex1", "Frequency window",
           "IMPLEMENT: findAnagrams(s,p) with freq enter/leave. "
           "TRACE: s='cbaebabacd', p='abc' windows. "
           "SOLVE: NeetCode 150 — Find All Anagrams in a String, Permutation in String, "
           "Longest Repeating Character Replacement. "
           "TRANSFER (internal): Window with at most 2 distinct integers — freq + shrink pattern."),
    ],
)

_add(
    "dsa-singly-linked-list",
    hours=1.0,
    objective="Represent a singly linked list with Node references.",
    explanation=(
        RELEARN + " "
        + CPP["node"] + " "
        "class ListNode { int val; ListNode next; }. Head reference is entry; null terminates. "
        "No random access — walk next. NeetCode Core Skills — Design Singly Linked List on this topic."
    ),
    mastery=_MASTERY,
    resources=[
        nccore("dsa-singly-linked-list", "Design Singly Linked List"),
        nc150("dsa-singly-linked-list", "Linked List"),
    ],
    questions=[
        q("dsa-singly-linked-list-q1", "Singly linked list random access by index i:",
          ["O(i) walk from head", "O(1) like array", "O(log i)", "Impossible"],
          "O(i) walk from head", "No indexing.", mastery=True),
        q("dsa-singly-linked-list-q2", "Java ListNode.next is:",
          ["Reference to another node or null", "C++ raw pointer syntax", "Primitive int", "Array index"],
          "Reference to another node or null", "Reference semantics like Node*."),
        q("dsa-singly-linked-list-q3", "Empty list represented as:",
          ["head == null", "head.val == 0", "head.next == head", "size -1"],
          "head == null", "No nodes."),
        q("dsa-singly-linked-list-q4", "Insert after known node ref (singly):",
          ["O(1) pointer rewiring", "O(n) always", "O(log n)", "Requires array copy"],
          "O(1) pointer rewiring", "Given node reference."),
        q("dsa-singly-linked-list-q5", "Traverse list length n time:",
          ["O(n)", "O(1)", "O(log n)", "O(n²)"], "O(n)", "Visit each node once."),
        q("dsa-singly-linked-list-q6", "C++ struct Node* head vs Java ListNode head:",
          ["Same linked structure", "Unrelated", "Java uses arrays only", "C++ cannot link"],
          "Same linked structure", "Syntax differs."),
        q("dsa-singly-linked-list-q7", "Dummy head node simplifies:",
          ["Insert/delete at head edge cases", "Sorting only", "Cycle detection only", "Nothing"],
          "Insert/delete at head edge cases", "Avoid null head special cases."),
        q("dsa-singly-linked-list-q8", "Space for n nodes singly linked:",
          ["O(n) nodes + references", "O(1)", "O(n²)", "O(log n)"],
          "O(n) nodes + references", "One node per element."),
    ],
    exercises=[
        ex("dsa-singly-linked-list-ex1", "List structure",
           "IMPLEMENT: NeetCode Core Skills — Design Singly Linked List (get, addAtHead, addAtTail, etc.). "
           "TRACE: Draw nodes for 1→2→3 with head and tail pointers. "
           "SOLVE: NeetCode 150 Linked List — Reverse Linked List (understand nodes first). "
           "TRANSFER (internal): Merge two lists without new nodes — only rewiring next."),
    ],
)

_add(
    "dsa-list-operations",
    hours=1.25,
    objective="Insert, delete, and find by walking next pointers.",
    explanation=(
        RELEARN + " "
        "Operations need predecessor tracking for delete; dummy node helps. "
        "Find kth from end uses length or two-pointer offset."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-list-operations", "Linked List")],
    questions=[
        q("dsa-list-operations-q1", "Delete node with only node reference (no head) in singly list:",
          ["Copy next val and skip next (if tail not allowed) or need head", "O(1) always with head unknown", "Impossible ever", "Sort first"],
          "Copy next val and skip next (if tail not allowed) or need head", "Classic trick or need predecessor.", mastery=True),
        q("dsa-list-operations-q2", "Insert at head:",
          ["newNode.next=head; head=newNode", "head.next only", "Sort", "Array copy"],
          "newNode.next=head; head=newNode", "O(1) with head ref."),
        q("dsa-list-operations-q3", "Find middle in one pass uses:",
          ["Slow/fast pointers", "Array index n/2", "Stack only", "HashMap only"],
          "Slow/fast pointers", "Fast at end when slow at middle."),
        q("dsa-list-operations-q4", "Remove nth from end dummy head helps:",
          ["Fast pointer n ahead then move both", "Only recursion", "Sort list", "BFS"],
          "Fast pointer n ahead then move both", "One pass removal."),
        q("dsa-list-operations-q5", "Search value in list:",
          ["O(n)", "O(1)", "O(log n)", "O(n²)"], "O(n)", "Linear scan."),
        q("dsa-list-operations-q6", "Delete requires knowing:",
          ["Predecessor node for singly linked", "Nothing", "Only tail", "Array index always"],
          "Predecessor node for singly linked", "Rewire prev.next."),
        q("dsa-list-operations-q7", "Add Two Numbers lists digits reversed:",
          ["Traverse with carry dummy head", "Convert to int only", "Sort digits", "BFS"],
          "Traverse with carry dummy head", "Digit-by-digit simulation."),
        q("dsa-list-operations-q8", "C++ list::erase vs Java manual:",
          ["Java rewires next references manually", "Java has std::list built-in", "Identical API", "Cannot delete in Java"],
          "Java rewires next references manually", "No STL list in Java standard."),
    ],
    exercises=[
        ex("dsa-list-operations-ex1", "List ops",
           "IMPLEMENT: removeNthFromEnd(ListNode head, int n) with dummy. "
           "TRACE: 1→2→3→4→5, n=2. "
           "SOLVE: NeetCode 150 — Remove Nth Node From End of List, Add Two Numbers. "
           "TRANSFER (internal): Delete all nodes with value x given head."),
    ],
)

_add(
    "dsa-list-reversal",
    hours=1.0,
    objective="Reverse a singly linked list iteratively in O(n) O(1).",
    explanation=(
        RELEARN + " "
        "Three-pointer iterative reverse: prev, curr, next. "
        "Recursive reverse possible but master iterative for interviews."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-list-reversal", "Linked List")],
    questions=[
        q("dsa-list-reversal-q1", "Iterative reverse needs pointers:",
          ["prev, curr, next", "Only head", "Array temp", "Stack only"],
          "prev, curr, next", "Rewire each step.", mastery=True),
        q("dsa-list-reversal-q2", "Reverse in-place space:",
          ["O(1)", "O(n)", "O(log n)", "O(n²)"], "O(1)", "Pointer swaps only."),
        q("dsa-list-reversal-q3", "After reverse, new head is:",
          ["Old tail / last non-null", "Old head", "Middle always", "null"],
          "Old tail / last non-null", "Former tail becomes head."),
        q("dsa-list-reversal-q4", "Trace 1→2→3: after full reverse:",
          ["3→2→1", "1→2→3", "2→1→3", "null"],
          "3→2→1", "All links flipped."),
        q("dsa-list-reversal-q5", "Reverse sublist between left and right:",
          ["Find left prev, reverse segment, reconnect", "Copy to array only", "Sort", "BFS"],
          "Find left prev, reverse segment, reconnect", "Local reverse pattern."),
        q("dsa-list-reversal-q6", "Reorder list (L0,Ln,L1...) combines:",
          ["Find middle, reverse second half, merge", "Sort O(n log n) only", "Hash only", "BFS"],
          "Find middle, reverse second half, merge", "Multi-step list pattern."),
        q("dsa-list-reversal-q7", "Recursive reverse base case:",
          ["curr == null return prev", "n==0", "head==tail", "Never base"],
          "curr == null return prev", "Standard recursion."),
        q("dsa-list-reversal-q8", "C++ reverse linked list vs Java:",
          ["Same pointer logic", "Java cannot reverse", "C++ only iterative", "Uses vector only"],
          "Same pointer logic", "Algorithm identical."),
    ],
    exercises=[
        ex("dsa-list-reversal-ex1", "Reverse list",
           "IMPLEMENT: reverseList(ListNode head) iterative. "
           "TRACE: 1→2→3→null step table prev/curr/next. "
           "SOLVE: NeetCode 150 — Reverse Linked List, Reverse Nodes in k-Group (read constraints). "
           "TRANSFER (internal): Palindrome linked list — reverse second half compare."),
    ],
)

_add(
    "dsa-fast-slow",
    hours=1.0,
    objective="Use slow (+1) and fast (+2) pointers on linked lists.",
    explanation=(
        RELEARN + " "
        "Fast/slow finds middle, detects cycles, finds cycle start (Floyd). "
        "Fast moves 2x speed; when fast hits end, slow at midpoint."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-fast-slow", "Linked List")],
    questions=[
        q("dsa-fast-slow-q1", "Middle of list: fast at end, slow at:",
          ["Middle (or upper middle per definition)", "Head", "Tail always", "null"],
          "Middle (or upper middle per definition)", "2:1 speed ratio.", mastery=True),
        q("dsa-fast-slow-q2", "Fast pointer steps per iteration:",
          ["2", "1", "3", "n/2"], "2", "Defines fast/slow."),
        q("dsa-fast-slow-q3", "If cycle exists fast and slow:",
          ["Eventually meet inside cycle", "Never meet", "Always at head", "Hit null"],
          "Eventually meet inside cycle", "Floyd cycle detection."),
        q("dsa-fast-slow-q4", "Find middle time:",
          ["O(n)", "O(n²)", "O(log n)", "O(1)"], "O(n)", "Single pass."),
        q("dsa-fast-slow-q5", "No cycle: fast becomes:",
          ["null at end", "head again", "middle", "tail.prev"],
          "null at end", "Termination condition."),
        q("dsa-fast-slow-q6", "Reorder list finds split via:",
          ["Slow/fast middle", "Sort", "Hash only", "BFS"],
          "Slow/fast middle", "Split then reverse/merge."),
        q("dsa-fast-slow-q7", "C++ tortoise/hare vs Java:",
          ["Same algorithm", "Java forbids two pointers", "Different math", "Only arrays"],
          "Same algorithm", "Language-agnostic."),
        q("dsa-fast-slow-q8", "Palindrome list can use fast/slow to:",
          ["Reach middle before second half reverse", "Detect sort order", "Count nodes only", "Hash frequencies"],
          "Reach middle before second half reverse", "Combine with reversal."),
    ],
    exercises=[
        ex("dsa-fast-slow-ex1", "Fast/slow pointers",
           "IMPLEMENT: middleNode(ListNode head) and hasCycle sketch. "
           "TRACE: 1→2→3→4→5 slow/fast positions. "
           "SOLVE: NeetCode 150 — Middle of the Linked List, Linked List Cycle. "
           "TRANSFER (internal): Find duplicate in array treated as linked cycle — explain mapping."),
    ],
)

_add(
    "dsa-cycle-detection",
    hours=1.0,
    objective="Detect a cycle with Floyd's fast/slow algorithm.",
    explanation=(
        RELEARN + " "
        "Phase 1: detect meet. Phase 2: reset one to head, move both +1 to find entry. "
        "Proof intuition: distances align modulo cycle length."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-cycle-detection", "Linked List")],
    questions=[
        q("dsa-cycle-detection-q1", "hasCycle returns true when:",
          ["Fast meets slow inside cycle", "Head equals tail", "List length even", "Values duplicate"],
          "Fast meets slow inside cycle", "Floyd detection.", mastery=True),
        q("dsa-cycle-detection-q2", "After meeting, find cycle start by:",
          ["Reset slow to head, advance both 1 until meet", "Sort list", "Hash all nodes only", "Reverse list"],
          "Reset slow to head, advance both 1 until meet", "Entry point algorithm."),
        q("dsa-cycle-detection-q3", "Cycle detection space Floyd:",
          ["O(1)", "O(n)", "O(log n)", "O(n²)"], "O(1)", "Two pointers only."),
        q("dsa-cycle-detection-q4", "HashSet cycle detection space:",
          ["O(n)", "O(1)", "O(log n)", "O(1) always better than Floyd"],
          "O(n)", "Trades space for simpler code."),
        q("dsa-cycle-detection-q5", "Why fast cannot skip 3 steps generally:",
          ["May miss meeting inside cycle", "Faster always", "Required for proof", "Java limitation"],
          "May miss meeting inside cycle", "Step size 2 standard."),
        q("dsa-cycle-detection-q6", "Linked List Cycle II asks for:",
          ["Node where cycle begins", "Cycle length only", "Sort list", "Delete cycle"],
          "Node where cycle begins", "Phase two of Floyd."),
        q("dsa-cycle-detection-q7", "Find Duplicate Number (array as linked list) uses:",
          ["Same Floyd idea on implicit next index", "Only sorting", "BFS", "Trie"],
          "Same Floyd idea on implicit next index", "Cycle in permutation graph."),
        q("dsa-cycle-detection-q8", "No cycle: Floyd phase one ends with:",
          ["fast == null or fast.next == null", "slow == head", "meet at tail", "exception"],
          "fast == null or fast.next == null", "Reached end."),
    ],
    exercises=[
        ex("dsa-cycle-detection-ex1", "Cycle detection",
           "IMPLEMENT: hasCycle and detectCycle(ListNode head). "
           "TRACE: Draw cycle entering at node 3, meeting point intuition. "
           "SOLVE: NeetCode 150 — Linked List Cycle, Linked List Cycle II, Find the Duplicate Number. "
           "TRANSFER (internal): Happy number sequence cycle — Floyd on implicit iteration."),
    ],
)

_add(
    "dsa-list-merge",
    hours=1.25,
    objective="Merge two sorted lists and apply merge patterns.",
    explanation=(
        RELEARN + " "
        "Dummy head + tail pointer builds merged sorted list O(n+m). "
        "Foundation for merge sort on lists and multi-list merge with heap later."
    ),
    mastery=_MASTERY,
    resources=[nc150("dsa-list-merge", "Linked List")],
    questions=[
        q("dsa-list-merge-q1", "Merge two sorted lists time:",
          ["O(n+m)", "O(n*m)", "O(n log m)", "O(1)"], "O(n+m)", "Each node visited once.", mastery=True),
        q("dsa-list-merge-q2", "Dummy head in merge:",
          ["Simplifies first node attach", "Required for recursion only", "Increases space O(n)", "Sorts automatically"],
          "Simplifies first node attach", "Tail pointer walks result."),
        q("dsa-list-merge-q3", "Compare l1.val and l2.val pick smaller, advance:",
          ["Chosen list pointer", "Both always", "Head only", "Random"],
          "Chosen list pointer", "Standard merge."),
        q("dsa-list-merge-q4", "When one list exhausted:",
          ["Attach remainder", "Stop and discard rest", "Sort remainder", "Reverse remainder"],
          "Attach remainder", "Already sorted tail attaches."),
        q("dsa-list-merge-q5", "Merge K lists later uses:",
          ["Heap or divide-merge", "Only O(kn) pairwise always required", "BFS only", "Hash only"],
          "Heap or divide-merge", "Extension of two-merge."),
        q("dsa-list-merge-q6", "Merge in-place space:",
          ["O(1) extra if reusing nodes", "O(n+m) new nodes required always", "O(log n)", "O(n²)"],
          "O(1) extra if reusing nodes", "Rewire next pointers."),
        q("dsa-list-merge-q7", "C++ merge two list nodes vs Java:",
          ["Identical two-pointer merge", "Java copies arrays", "Cannot merge in Java", "Uses TreeMap"],
          "Identical two-pointer merge", "Same algorithm."),
        q("dsa-list-merge-q8", "Recursive merge base:",
          ["One list null return other", "Both null impossible", "Always sort", "n==1 only arrays"],
          "One list null return other", "Recursive structure."),
    ],
    exercises=[
        ex("dsa-list-merge-ex1", "Merge sorted lists",
           "IMPLEMENT: mergeTwoLists(ListNode l1, ListNode l2) iterative with dummy. "
           "TRACE: 1→3→5 and 2→4→6 merge steps. "
           "SOLVE: NeetCode 150 — Merge Two Sorted Lists, Reorder List (uses merge/split ideas). "
           "TRANSFER (internal): Merge two sorted arrays in-place in O(m+n) — relate to list merge."),
    ],
)
