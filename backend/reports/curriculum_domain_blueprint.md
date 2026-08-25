# Curriculum Domain Blueprint

Generated from real DB state on 2026-08-24T14:19:48.207894+00:00

Total topics: **316** across 17 domains.

## PHASE_10_AI_ENGINEERING

### Domain: AI Engineering / Agents

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `ai-eng-awareness` | AI Engineering awareness |  | ai-eng-path | OPTIONAL | AWARENESS |
| `ai-eng-path` | AI Engineering learning path | ai-eng-awareness |  | OPTIONAL | AWARENESS |
### Domain: MLOps

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `mlops-tracking` | Experiment tracking | ml-sklearn-pipeline | mlops-model-packaging | SPECIALIZATION | STRONG |
| `mlops-model-packaging` | Model packaging | mlops-tracking | mlops-serving | SPECIALIZATION | STRONG |
| `mlops-serving` | Model serving APIs | mlops-model-packaging, be-fastapi-intro | mlops-monitoring | SPECIALIZATION | STRONG |
| `mlops-monitoring` | Model monitoring basics | mlops-serving |  | SPECIALIZATION | STRONG |

## PHASE_10_SYSTEM_DESIGN

### Domain: System Design

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `sysdesign-awareness` | System Design awareness |  | sysdesign-path | OPTIONAL | AWARENESS |
| `sysdesign-path` | System Design learning path | sysdesign-awareness |  | OPTIONAL | AWARENESS |

## PHASE_1_ENGINEERING_FUNDAMENTALS

### Domain: CS Foundations

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `cf-bits-and-bytes` | Bits and bytes |  | cf-binary | CORE | WORKING_KNOWLEDGE |
| `cf-binary` | Binary | cf-bits-and-bytes | cf-hexadecimal | CORE | WORKING_KNOWLEDGE |
| `cf-hexadecimal` | Hexadecimal | cf-binary | cf-cpu | CORE | WORKING_KNOWLEDGE |
| `cf-cpu` | CPU | cf-hexadecimal | cf-alu | CORE | WORKING_KNOWLEDGE |
| `cf-alu` | ALU | cf-cpu | cf-registers | CORE | WORKING_KNOWLEDGE |
| `cf-registers` | Registers | cf-alu | cf-ram | CORE | WORKING_KNOWLEDGE |
| `cf-ram` | RAM | cf-registers | cf-cache | CORE | WORKING_KNOWLEDGE |
| `cf-cache` | Cache | cf-ram | cf-storage | CORE | WORKING_KNOWLEDGE |
| `cf-storage` | Storage | cf-cache | cf-instruction-execution | CORE | WORKING_KNOWLEDGE |
| `cf-instruction-execution` | Instruction execution | cf-storage | cf-machine-code | CORE | WORKING_KNOWLEDGE |
| `cf-machine-code` | Machine code | cf-instruction-execution | cf-compiler | CORE | WORKING_KNOWLEDGE |
| `cf-compiler` | Compiler | cf-machine-code | cf-ide, cf-interpreter | CORE | WORKING_KNOWLEDGE |
| `cf-interpreter` | Interpreter | cf-compiler | cf-program | CORE | WORKING_KNOWLEDGE |
| `cf-program` | Program | cf-interpreter | cf-process | CORE | WORKING_KNOWLEDGE |
| `cf-process` | Process | cf-program | cf-kernel | CORE | WORKING_KNOWLEDGE |
| `cf-kernel` | Kernel | cf-process | cf-os-processes | CORE | WORKING_KNOWLEDGE |
| `cf-os-processes` | Processes | cf-kernel | cf-threads | CORE | WORKING_KNOWLEDGE |
| `cf-threads` | Threads | cf-os-processes | cf-system-calls | CORE | WORKING_KNOWLEDGE |
| `cf-system-calls` | System calls | cf-threads | cf-os-memory | CORE | WORKING_KNOWLEDGE |
| `cf-os-memory` | Memory | cf-system-calls | cf-virtual-memory-basics | CORE | WORKING_KNOWLEDGE |
| `cf-virtual-memory-basics` | Virtual memory basics | cf-os-memory | cf-filesystems | CORE | WORKING_KNOWLEDGE |
| `cf-filesystems` | Filesystems | cf-virtual-memory-basics | cf-os-permissions | CORE | WORKING_KNOWLEDGE |
| `cf-os-permissions` | Permissions | cf-filesystems | cf-os-environment-variables | CORE | WORKING_KNOWLEDGE |
| `cf-os-environment-variables` | Environment variables | cf-os-permissions | cf-shell | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-shell` | Shell | cf-os-environment-variables | cf-command-line, ops-docker-intro | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-command-line` | Command line | cf-shell | cf-filesystem-navigation, py-syntax | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-filesystem-navigation` | Filesystem navigation | cf-command-line | cf-linux-files | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-linux-files` | Files | cf-filesystem-navigation | cf-pipes | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-pipes` | Pipes | cf-linux-files | cf-redirection | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-redirection` | Redirection | cf-pipes | cf-grep | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-grep` | grep | cf-redirection | cf-find | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-find` | find | cf-grep | cf-linux-permissions | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-linux-permissions` | Permissions | cf-find | cf-linux-processes | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-linux-processes` | Processes | cf-linux-permissions | cf-package-management, ops-linux-services | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-package-management` | Package management | cf-linux-processes | cf-linux-environment-variables | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-linux-environment-variables` | Environment variables | cf-package-management | cf-repository | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-repository` | Repository | cf-linux-environment-variables | cf-commits | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-commits` | Commits | cf-repository | cf-branches | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-branches` | Branches | cf-commits | cf-merge | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-merge` | Merge | cf-branches | cf-rebase | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-rebase` | Rebase | cf-merge | cf-remote | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-remote` | Remote | cf-rebase | cf-pull-push | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-pull-push` | Pull and push | cf-remote | cf-conflicts | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-conflicts` | Conflicts | cf-pull-push | cf-reset-revert | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-reset-revert` | Reset and revert | cf-conflicts | cf-cherry-pick | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-cherry-pick` | Cherry-pick | cf-reset-revert | cf-stash | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-stash` | Stash | cf-cherry-pick | cf-github-workflow | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-github-workflow` | GitHub workflow | cf-stash | cf-ide | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-ide` | IDE | cf-github-workflow, cf-compiler | cf-dev-compiler | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-dev-compiler` | Compiler | cf-ide | cf-debugger | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-debugger` | Debugger | cf-dev-compiler | cf-formatter | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-formatter` | Formatter | cf-debugger | cf-linter | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-linter` | Linter | cf-formatter | cf-dev-package-manager | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-dev-package-manager` | Package manager | cf-linter | cf-build-system | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-build-system` | Build system | cf-dev-package-manager | cf-dependency-management | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-dependency-management` | Dependency management | cf-build-system | cf-problem-decomposition, java-jdk-jre | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-problem-decomposition` | Problem decomposition | cf-dependency-management | cf-pseudocode | CORE | WORKING_KNOWLEDGE |
| `cf-pseudocode` | Pseudocode | cf-problem-decomposition | cf-algorithms | CORE | WORKING_KNOWLEDGE |
| `cf-algorithms` | Algorithms | cf-pseudocode | cf-dry-runs | CORE | WORKING_KNOWLEDGE |
| `cf-dry-runs` | Dry runs | cf-algorithms | cf-edge-cases | CORE | WORKING_KNOWLEDGE |
| `cf-edge-cases` | Edge cases | cf-dry-runs | cf-debugging-thinking | CORE | WORKING_KNOWLEDGE |
| `cf-debugging-thinking` | Debugging | cf-edge-cases | cf-time-complexity-intro | ALWAYS_ON | WORKING_KNOWLEDGE |
| `cf-time-complexity-intro` | Time complexity introduction | cf-debugging-thinking | cf-space-complexity-intro, dsa-algorithmic-thinking | CORE | WORKING_KNOWLEDGE |
| `cf-space-complexity-intro` | Space complexity introduction | cf-time-complexity-intro | java-jdk-jre | CORE | WORKING_KNOWLEDGE |

## PHASE_1_SUPPORTING

### Domain: Networking / DevOps

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `devops-awareness` | DevOps awareness |  | devops-path | OPTIONAL | AWARENESS |
| `devops-path` | DevOps learning path | devops-awareness |  | OPTIONAL | AWARENESS |
| `net-internet-basics` | Internet basics |  | net-dns, net-http, net-tcp-udp | SPECIALIZATION | WORKING_KNOWLEDGE |
| `net-dns` | DNS | net-internet-basics |  | SPECIALIZATION | WORKING_KNOWLEDGE |
| `net-tcp-udp` | TCP vs UDP | net-internet-basics |  | SPECIALIZATION | WORKING_KNOWLEDGE |
| `net-http` | HTTP deep dive | net-internet-basics, be-http | net-https-tls, net-websockets | SPECIALIZATION | WORKING_KNOWLEDGE |
| `net-https-tls` | HTTPS & TLS | net-http |  | SPECIALIZATION | WORKING_KNOWLEDGE |
| `net-websockets` | WebSockets | net-http |  | SPECIALIZATION | WORKING_KNOWLEDGE |

## PHASE_2_PROGRAMMING_DSA

### Domain: Java

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `java-jdk-jre` | JDK and JRE | cf-space-complexity-intro, cf-dependency-management | java-first-program | CORE | STRONG |
| `java-first-program` | First program | java-jdk-jre | java-compile-and-run | CORE | STRONG |
| `java-compile-and-run` | Compile and run | java-first-program | java-primitives | CORE | STRONG |
| `java-primitives` | Primitives | java-compile-and-run | java-type-conversion | CORE | STRONG |
| `java-type-conversion` | Type conversion | java-primitives | java-console-io | CORE | STRONG |
| `java-console-io` | Console input and output | java-type-conversion | java-operators | CORE | STRONG |
| `java-operators` | Operators | java-console-io | java-if-else | CORE | STRONG |
| `java-if-else` | if/else | java-operators | java-switch | CORE | STRONG |
| `java-switch` | switch | java-if-else | java-loops | CORE | STRONG |
| `java-loops` | Loops | java-switch | java-break-continue | CORE | STRONG |
| `java-break-continue` | break and continue | java-loops | java-method-basics | CORE | STRONG |
| `java-method-basics` | Method basics | java-break-continue | dsa-algorithmic-thinking, dsa-recursion-model, java-overloading | CORE | STRONG |
| `java-overloading` | Overloading | java-method-basics | java-scope | CORE | STRONG |
| `java-scope` | Scope | java-overloading | java-arrays | CORE | STRONG |
| `java-arrays` | Arrays | java-scope | dsa-array-traversal, dsa-binary-search-classic, dsa-bubble-sort (+3) | CORE | STRONG |
| `java-strings` | Strings | java-arrays | dsa-string-manipulation, java-stringbuilder | CORE | STRONG |
| `java-stringbuilder` | StringBuilder | java-strings | java-classes-objects | CORE | STRONG |
| `java-classes-objects` | Classes and objects | java-stringbuilder | dsa-bst-search, dsa-graph-representations, dsa-mst (+8) | CORE | STRONG |
| `java-references` | References | java-classes-objects | dsa-bst-search, dsa-graph-representations, dsa-mst (+8) | CORE | STRONG |
| `java-constructors` | Constructors | java-references | java-encapsulation | CORE | STRONG |
| `java-encapsulation` | Encapsulation | java-constructors | java-inheritance | CORE | STRONG |
| `java-inheritance` | Inheritance | java-encapsulation | java-polymorphism | CORE | STRONG |
| `java-polymorphism` | Polymorphism | java-inheritance | java-abstract-classes | CORE | STRONG |
| `java-abstract-classes` | Abstract classes | java-polymorphism | java-interfaces | CORE | STRONG |
| `java-interfaces` | Interfaces | java-abstract-classes | java-composition | CORE | STRONG |
| `java-composition` | Composition | java-interfaces | java-try-catch | CORE | STRONG |
| `java-try-catch` | try/catch | java-composition | java-checked-unchecked | CORE | STRONG |
| `java-checked-unchecked` | Checked and unchecked | java-try-catch | java-custom-exceptions | CORE | STRONG |
| `java-custom-exceptions` | Custom exceptions | java-checked-unchecked | java-list | CORE | STRONG |
| `java-list` | List | java-custom-exceptions | dsa-graph-representations, dsa-mst, dsa-queue-deque (+5) | CORE | STRONG |
| `java-set` | Set | java-list | dsa-hash-map, java-map | CORE | STRONG |
| `java-map` | Map | java-set | dsa-graph-representations, dsa-hash-map, dsa-mst (+5) | CORE | STRONG |
| `java-iteration` | Iteration | java-map | java-priority-queue | CORE | STRONG |
| `java-priority-queue` | PriorityQueue | java-iteration | dsa-heap-structure, dsa-unweighted-shortest, java-generic-types | CORE | STRONG |
| `java-generic-types` | Generic types | java-priority-queue | java-generic-bounds | CORE | STRONG |
| `java-generic-bounds` | Bounds | java-generic-types | java-comparable-comparator | CORE | STRONG |
| `java-comparable-comparator` | Comparable and Comparator | java-generic-bounds | dsa-heap-structure, java-functional-interfaces | CORE | STRONG |
| `java-functional-interfaces` | Functional interfaces | java-comparable-comparator | java-lambdas | CORE | STRONG |
| `java-lambdas` | Lambdas | java-functional-interfaces | java-stream-pipeline | CORE | STRONG |
| `java-stream-pipeline` | Stream pipeline | java-lambdas | java-stream-operations | CORE | STRONG |
| `java-stream-operations` | Common operations | java-stream-pipeline | java-paths-files | CORE | STRONG |
| `java-paths-files` | Paths and files | java-stream-operations | java-readers-writers | CORE | STRONG |
| `java-readers-writers` | Readers and writers | java-paths-files | java-junit-basics | CORE | STRONG |
| `java-junit-basics` | JUnit basics | java-readers-writers | java-assertions | CORE | STRONG |
| `java-assertions` | Assertions | java-junit-basics | java-threads | CORE | STRONG |
| `java-threads` | Threads | java-assertions | java-synchronization-basics | CORE | STRONG |
| `java-synchronization-basics` | Synchronization basics | java-threads | java-bytecode | CORE | STRONG |
| `java-bytecode` | Bytecode | java-synchronization-basics | java-memory-model-basics | CORE | STRONG |
| `java-memory-model-basics` | Memory model basics | java-bytecode | java-gc-intro | CORE | STRONG |
| `java-gc-intro` | Garbage collection intro | java-memory-model-basics | java-packages | CORE | STRONG |
| `java-packages` | Packages | java-gc-intro | java-api-hygiene | CORE | STRONG |
| `java-api-hygiene` | API hygiene | java-packages |  | CORE | STRONG |
### Domain: DSA & Algorithms

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `dsa-algorithmic-thinking` | Algorithmic thinking | cf-time-complexity-intro, java-method-basics | dsa-big-o | CORE | STRONG |
| `dsa-big-o` | Big-O notation | dsa-algorithmic-thinking | dsa-best-worst-average | CORE | STRONG |
| `dsa-best-worst-average` | Best, worst, average | dsa-big-o | dsa-array-traversal | CORE | STRONG |
| `dsa-array-traversal` | Array traversal | dsa-best-worst-average, java-arrays | dsa-array-insert-delete | CORE | STRONG |
| `dsa-array-insert-delete` | Insertion and deletion concepts | dsa-array-traversal | dsa-prefix-sums | CORE | STRONG |
| `dsa-prefix-sums` | Prefix sums | dsa-array-insert-delete | dsa-array-frequency | CORE | STRONG |
| `dsa-array-frequency` | Frequency counting | dsa-prefix-sums | dsa-array-patterns | CORE | STRONG |
| `dsa-array-patterns` | Array patterns | dsa-array-frequency | dsa-string-manipulation | CORE | STRONG |
| `dsa-string-manipulation` | String manipulation | dsa-array-patterns, java-strings | dsa-string-frequency | CORE | STRONG |
| `dsa-string-frequency` | String frequency | dsa-string-manipulation | dsa-character-processing | CORE | STRONG |
| `dsa-character-processing` | Character processing | dsa-string-frequency | dsa-string-patterns | CORE | STRONG |
| `dsa-string-patterns` | String patterns | dsa-character-processing | dsa-hash-map | CORE | STRONG |
| `dsa-hash-map` | Hash map | dsa-string-patterns, java-map, java-set | dsa-hash-set | CORE | STRONG |
| `dsa-hash-set` | Hash set | dsa-hash-map | dsa-frequency-maps | CORE | STRONG |
| `dsa-frequency-maps` | Frequency maps | dsa-hash-set | dsa-lookup-patterns | CORE | STRONG |
| `dsa-lookup-patterns` | Lookup patterns | dsa-frequency-maps | dsa-two-pointers-opposite | CORE | STRONG |
| `dsa-two-pointers-opposite` | Opposite-direction pointers | dsa-lookup-patterns, java-arrays | dsa-two-pointers-same | CORE | STRONG |
| `dsa-two-pointers-same` | Same-direction pointers | dsa-two-pointers-opposite | dsa-two-pointers-partition | CORE | STRONG |
| `dsa-two-pointers-partition` | Partition-style patterns | dsa-two-pointers-same | dsa-window-fixed | CORE | STRONG |
| `dsa-window-fixed` | Fixed window | dsa-two-pointers-partition, java-arrays, java-map | dsa-window-variable | CORE | STRONG |
| `dsa-window-variable` | Variable window | dsa-window-fixed | dsa-window-frequency | CORE | STRONG |
| `dsa-window-frequency` | Frequency window state | dsa-window-variable | dsa-singly-linked-list | CORE | STRONG |
| `dsa-singly-linked-list` | Singly linked list | dsa-window-frequency, java-classes-objects, java-references | dsa-list-operations | CORE | STRONG |
| `dsa-list-operations` | List operations | dsa-singly-linked-list | dsa-list-reversal | CORE | STRONG |
| `dsa-list-reversal` | Reversal | dsa-list-operations | dsa-fast-slow | CORE | STRONG |
| `dsa-fast-slow` | Fast and slow pointers | dsa-list-reversal | dsa-cycle-detection | CORE | STRONG |
| `dsa-cycle-detection` | Cycle detection | dsa-fast-slow | dsa-list-merge | CORE | STRONG |
| `dsa-list-merge` | Merge patterns | dsa-cycle-detection | dsa-stack-fundamentals | CORE | STRONG |
| `dsa-stack-fundamentals` | Stack fundamentals | dsa-list-merge, java-classes-objects, java-references (+1) | dsa-monotonic-stack | CORE | STRONG |
| `dsa-monotonic-stack` | Monotonic stack | dsa-stack-fundamentals | dsa-queue-deque | CORE | STRONG |
| `dsa-queue-deque` | Queue and deque | dsa-monotonic-stack, java-classes-objects, java-references (+1) | dsa-queue-bfs-relationship | CORE | STRONG |
| `dsa-queue-bfs-relationship` | BFS relationship | dsa-queue-deque | dsa-recursion-model | CORE | STRONG |
| `dsa-recursion-model` | Recursion model | dsa-queue-bfs-relationship, java-method-basics | dsa-call-stack | CORE | STRONG |
| `dsa-call-stack` | Call stack | dsa-recursion-model | dsa-recursive-trees | CORE | STRONG |
| `dsa-recursive-trees` | Recursive tree problems | dsa-call-stack | dsa-recursion-to-iteration | CORE | STRONG |
| `dsa-recursion-to-iteration` | Recursion to iteration | dsa-recursive-trees | dsa-subsets | CORE | STRONG |
| `dsa-subsets` | Subsets | dsa-recursion-to-iteration | dsa-permutations | CORE | STRONG |
| `dsa-permutations` | Permutations | dsa-subsets | dsa-combinations | CORE | STRONG |
| `dsa-combinations` | Combinations | dsa-permutations | dsa-constraint-search | CORE | STRONG |
| `dsa-constraint-search` | Constraint search | dsa-combinations | dsa-bubble-sort | CORE | STRONG |
| `dsa-bubble-sort` | Bubble sort | dsa-constraint-search, java-arrays | dsa-selection-sort | CORE | STRONG |
| `dsa-selection-sort` | Selection sort | dsa-bubble-sort | dsa-insertion-sort | CORE | STRONG |
| `dsa-insertion-sort` | Insertion sort | dsa-selection-sort | dsa-merge-sort | CORE | STRONG |
| `dsa-merge-sort` | Merge sort | dsa-insertion-sort | dsa-quick-sort | CORE | STRONG |
| `dsa-quick-sort` | Quick sort | dsa-merge-sort | dsa-heap-sort | CORE | STRONG |
| `dsa-heap-sort` | Heap sort | dsa-quick-sort | dsa-counting-radix | CORE | STRONG |
| `dsa-counting-radix` | Counting and radix concepts | dsa-heap-sort | dsa-sort-stability | CORE | STRONG |
| `dsa-sort-stability` | Stability | dsa-counting-radix | dsa-sort-complexity | CORE | STRONG |
| `dsa-sort-complexity` | Complexity comparison | dsa-sort-stability | dsa-binary-search-classic | CORE | STRONG |
| `dsa-binary-search-classic` | Classic search | dsa-sort-complexity, java-arrays | dsa-binary-search-boundaries | CORE | STRONG |
| `dsa-binary-search-boundaries` | Boundaries | dsa-binary-search-classic | dsa-first-last-occurrence | CORE | STRONG |
| `dsa-first-last-occurrence` | First and last occurrence | dsa-binary-search-boundaries | dsa-search-on-answer | CORE | STRONG |
| `dsa-search-on-answer` | Search on the answer | dsa-first-last-occurrence | dsa-rotated-arrays | CORE | STRONG |
| `dsa-rotated-arrays` | Rotated arrays | dsa-search-on-answer | dsa-tree-terminology | CORE | STRONG |
| `dsa-tree-terminology` | Tree terminology | dsa-rotated-arrays, java-classes-objects, java-references | dsa-binary-trees | CORE | STRONG |
| `dsa-binary-trees` | Binary trees | dsa-tree-terminology | dsa-tree-dfs | CORE | STRONG |
| `dsa-tree-dfs` | DFS traversals | dsa-binary-trees | dsa-tree-bfs | CORE | STRONG |
| `dsa-tree-bfs` | BFS / level order | dsa-tree-dfs | dsa-tree-height | CORE | STRONG |
| `dsa-tree-height` | Height and depth | dsa-tree-bfs | dsa-tree-paths | CORE | STRONG |
| `dsa-tree-paths` | Path problems | dsa-tree-height | dsa-tree-construction | CORE | STRONG |
| `dsa-tree-construction` | Construction | dsa-tree-paths | dsa-bst-search | CORE | STRONG |
| `dsa-bst-search` | BST search | dsa-tree-construction, java-classes-objects, java-references | dsa-bst-insert | CORE | STRONG |
| `dsa-bst-insert` | BST insertion | dsa-bst-search | dsa-bst-delete | CORE | STRONG |
| `dsa-bst-delete` | BST deletion | dsa-bst-insert | dsa-bst-validate | CORE | STRONG |
| `dsa-bst-validate` | BST validation | dsa-bst-delete | dsa-bst-ordered-properties | CORE | STRONG |
| `dsa-bst-ordered-properties` | Ordered properties | dsa-bst-validate | dsa-heap-structure | CORE | STRONG |
| `dsa-heap-structure` | Heap structure | dsa-bst-ordered-properties, java-priority-queue, java-comparable-comparator | dsa-priority-queue | CORE | STRONG |
| `dsa-priority-queue` | Priority queue | dsa-heap-structure | dsa-heapify | CORE | STRONG |
| `dsa-heapify` | Heapify | dsa-priority-queue | dsa-top-k | CORE | STRONG |
| `dsa-top-k` | Top-K | dsa-heapify | dsa-heap-scheduling | CORE | STRONG |
| `dsa-heap-scheduling` | Scheduling patterns | dsa-top-k | dsa-graph-representations | CORE | STRONG |
| `dsa-graph-representations` | Graph representations | dsa-heap-scheduling, java-list, java-map (+2) | dsa-graph-bfs | CORE | STRONG |
| `dsa-graph-bfs` | Graph BFS | dsa-graph-representations | dsa-graph-dfs | CORE | STRONG |
| `dsa-graph-dfs` | Graph DFS | dsa-graph-bfs | dsa-connected-components | CORE | STRONG |
| `dsa-connected-components` | Connected components | dsa-graph-dfs | dsa-graph-cycle | CORE | STRONG |
| `dsa-graph-cycle` | Cycle detection | dsa-connected-components | dsa-bipartite | CORE | STRONG |
| `dsa-bipartite` | Bipartite graphs | dsa-graph-cycle | dsa-topological-sort | CORE | STRONG |
| `dsa-topological-sort` | Topological sorting | dsa-bipartite, java-list, java-map (+2) | dsa-union-find | CORE | STRONG |
| `dsa-union-find` | Union-Find | dsa-topological-sort, java-list, java-map (+2) | dsa-unweighted-shortest | CORE | STRONG |
| `dsa-unweighted-shortest` | Unweighted shortest paths | dsa-union-find, java-list, java-map (+3) | dsa-dijkstra | CORE | STRONG |
| `dsa-dijkstra` | Dijkstra | dsa-unweighted-shortest | dsa-mst | CORE | STRONG |
| `dsa-mst` | MST | dsa-dijkstra, java-list, java-map (+2) | dsa-greedy-reasoning | CORE | STRONG |
| `dsa-greedy-reasoning` | Greedy reasoning | dsa-mst | dsa-greedy-exchange | CORE | STRONG |
| `dsa-greedy-exchange` | Exchange / intuitive proof | dsa-greedy-reasoning | dsa-interval-problems | CORE | STRONG |
| `dsa-interval-problems` | Interval problems | dsa-greedy-exchange | dsa-greedy-scheduling | CORE | STRONG |
| `dsa-greedy-scheduling` | Scheduling | dsa-interval-problems | dsa-greedy-patterns | CORE | STRONG |
| `dsa-greedy-patterns` | Classic greedy patterns | dsa-greedy-scheduling | dsa-dp-mindset | CORE | STRONG |
| `dsa-dp-mindset` | DP mindset | dsa-greedy-patterns | dsa-memoization | CORE | STRONG |
| `dsa-memoization` | Memoization | dsa-dp-mindset | dsa-tabulation | CORE | STRONG |
| `dsa-tabulation` | Tabulation | dsa-memoization | dsa-dp-state | CORE | STRONG |
| `dsa-dp-state` | State definition | dsa-tabulation | dsa-dp-transition | CORE | STRONG |
| `dsa-dp-transition` | Transition | dsa-dp-state | dsa-dp-1d | CORE | STRONG |
| `dsa-dp-1d` | 1D DP | dsa-dp-transition | dsa-dp-2d | CORE | STRONG |
| `dsa-dp-2d` | 2D DP | dsa-dp-1d | dsa-subsequence-dp | CORE | STRONG |
| `dsa-subsequence-dp` | Subsequence DP | dsa-dp-2d | dsa-knapsack | CORE | STRONG |
| `dsa-knapsack` | Knapsack | dsa-subsequence-dp | dsa-grid-dp | CORE | STRONG |
| `dsa-grid-dp` | Grid DP | dsa-knapsack | dsa-interval-dp | CORE | STRONG |
| `dsa-interval-dp` | Interval DP concepts | dsa-grid-dp | dsa-dp-optimization | CORE | STRONG |
| `dsa-dp-optimization` | DP optimization | dsa-interval-dp | dsa-tries | CORE | STRONG |
| `dsa-tries` | Tries | dsa-dp-optimization | dsa-bit-manipulation | CORE | STRONG |
| `dsa-bit-manipulation` | Bit manipulation | dsa-tries | dsa-segment-tree-concept | CORE | STRONG |
| `dsa-segment-tree-concept` | Segment tree concept | dsa-bit-manipulation | dsa-advanced-graphs | CORE | STRONG |
| `dsa-advanced-graphs` | Advanced graph concepts | dsa-segment-tree-concept | dsa-advanced-dp | CORE | STRONG |
| `dsa-advanced-dp` | Advanced DP | dsa-advanced-graphs | dsa-pattern-selection | CORE | STRONG |
| `dsa-pattern-selection` | Pattern selection | dsa-advanced-dp | dsa-interview-hygiene | CORE | STRONG |
| `dsa-interview-hygiene` | Interview hygiene | dsa-pattern-selection |  | CORE | STRONG |

## PHASE_3_ENGINEERING

### Domain: Software Engineering

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `se-sdlc` | SDLC overview |  | se-requirements, se-solid-srp, se-testing-pyramid (+1) | CORE | WORKING_KNOWLEDGE |
| `se-requirements` | Requirements & scope | se-sdlc | se-api-design | CORE | WORKING_KNOWLEDGE |
| `se-versioning` | Semantic versioning | se-sdlc |  | CORE | WORKING_KNOWLEDGE |
| `se-solid-srp` | SOLID — Single Responsibility | se-sdlc | se-solid-ocp | CORE | WORKING_KNOWLEDGE |
| `se-solid-ocp` | SOLID — Open/Closed | se-solid-srp |  | CORE | WORKING_KNOWLEDGE |
| `se-testing-pyramid` | Testing pyramid | se-sdlc | se-unit-tests | CORE | WORKING_KNOWLEDGE |
| `se-unit-tests` | Unit testing basics | se-testing-pyramid | py-testing, se-ci-basics, se-code-review | CORE | WORKING_KNOWLEDGE |
| `se-api-design` | API design basics | se-requirements |  | CORE | WORKING_KNOWLEDGE |
| `se-code-review` | Code review habits | se-unit-tests |  | ALWAYS_ON | WORKING_KNOWLEDGE |
| `se-ci-basics` | CI basics | se-unit-tests | ops-ci-github-actions | CORE | WORKING_KNOWLEDGE |
### Domain: Backend & Databases

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `db-sql-select` | SQL SELECT |  | be-persistence, db-indexes, db-sql-joins (+2) | CORE | WORKING_KNOWLEDGE |
| `db-sql-joins` | SQL JOINs | db-sql-select | db-schema-design | CORE | WORKING_KNOWLEDGE |
| `db-indexes` | Indexes & query plans | db-sql-select | sys-scalability | CORE | WORKING_KNOWLEDGE |
| `db-transactions` | Transactions | db-sql-select |  | CORE | WORKING_KNOWLEDGE |
| `db-schema-design` | Schema design basics | db-sql-joins |  | CORE | WORKING_KNOWLEDGE |
| `be-http` | HTTP fundamentals |  | be-json, be-rest, net-http | CORE | WORKING_KNOWLEDGE |
| `be-rest` | REST resources | be-http | be-fastapi-intro | CORE | WORKING_KNOWLEDGE |
| `be-json` | JSON APIs | be-http | be-fastapi-intro | CORE | WORKING_KNOWLEDGE |
| `be-fastapi-intro` | FastAPI intro | be-rest, be-json | be-auth-basics, be-errors, be-persistence (+2) | CORE | WORKING_KNOWLEDGE |
| `be-auth-basics` | Auth basics | be-fastapi-intro |  | CORE | WORKING_KNOWLEDGE |
| `be-errors` | API error handling | be-fastapi-intro |  | CORE | WORKING_KNOWLEDGE |
| `be-persistence` | API + SQL persistence | be-fastapi-intro, db-sql-select | sys-scalability | CORE | WORKING_KNOWLEDGE |

## PHASE_3_PYTHON_MATH

### Domain: Python

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `py-syntax` | Python syntax & tooling | cf-command-line | py-data-structures | CORE | STRONG |
| `py-data-structures` | Python data structures | py-syntax | py-functions-modules | CORE | STRONG |
| `py-functions-modules` | Functions & modules | py-data-structures | py-oop, py-testing | CORE | STRONG |
| `py-oop` | Python OOP | py-functions-modules |  | CORE | STRONG |
| `py-testing` | pytest for Python | py-functions-modules, se-unit-tests |  | CORE | STRONG |

## PHASE_4_MACHINE_LEARNING

### Domain: Machine Learning

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `ml-what-is-ml` | What is machine learning | math-probability | ml-features-labels | CORE | WORKING_KNOWLEDGE |
| `ml-features-labels` | Features & labels | ml-what-is-ml | ml-train-test | CORE | WORKING_KNOWLEDGE |
| `ml-train-test` | Train/test split | ml-features-labels | ml-classification, ml-linear-regression | CORE | WORKING_KNOWLEDGE |
| `ml-linear-regression` | Linear regression | ml-train-test, math-vectors |  | CORE | WORKING_KNOWLEDGE |
| `ml-classification` | Classification basics | ml-train-test | ml-metrics | CORE | STRONG |
| `ml-metrics` | ML metrics | ml-classification | ml-overfitting | CORE | STRONG |
| `ml-overfitting` | Overfitting & regularization | ml-metrics | ml-sklearn-pipeline | CORE | STRONG |
| `ml-sklearn-pipeline` | sklearn Pipeline | ml-overfitting | dl-nn-basics, mlops-tracking | CORE | STRONG |
### Domain: Data Science

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `ds-numpy` | NumPy foundations | math-vectors | ds-pandas | SPECIALIZATION | WORKING_KNOWLEDGE |
| `ds-pandas` | Pandas foundations | ds-numpy | ds-eda, ds-sql-analytics | SPECIALIZATION | WORKING_KNOWLEDGE |
| `ds-eda` | Exploratory data analysis | ds-pandas, math-stats-summary | ds-feature-eng | SPECIALIZATION | WORKING_KNOWLEDGE |
| `ds-feature-eng` | Feature engineering | ds-eda |  | SPECIALIZATION | WORKING_KNOWLEDGE |
| `ds-sql-analytics` | SQL for analytics | db-sql-select, ds-pandas |  | SPECIALIZATION | WORKING_KNOWLEDGE |

## PHASE_5_JIT_MATH

### Domain: Mathematics for ML

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `math-vectors` | Vectors intuition |  | ds-numpy, math-gradient-intuition, math-matrices (+1) | CORE | WORKING_KNOWLEDGE |
| `math-matrices` | Matrices intuition | math-vectors |  | CORE | WORKING_KNOWLEDGE |
| `math-probability` | Probability basics |  | math-distributions, math-stats-summary, ml-what-is-ml | CORE | WORKING_KNOWLEDGE |
| `math-distributions` | Distributions intuition | math-probability |  | CORE | WORKING_KNOWLEDGE |
| `math-stats-summary` | Summary statistics | math-probability | ds-eda | CORE | WORKING_KNOWLEDGE |
| `math-gradient-intuition` | Gradient intuition | math-vectors | dl-nn-basics | CORE | WORKING_KNOWLEDGE |

## PHASE_6_DEEP_LEARNING

### Domain: Deep Learning

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `dl-awareness` | Deep Learning awareness |  | dl-path | OPTIONAL | AWARENESS |
| `dl-path` | Deep Learning learning path | dl-awareness |  | OPTIONAL | AWARENESS |
| `dl-nn-basics` | Neural network basics | ml-sklearn-pipeline, math-gradient-intuition | dl-backprop, dl-cnn, dl-transformers-intro | SPECIALIZATION | DEEP |
| `dl-backprop` | Backpropagation intuition | dl-nn-basics |  | SPECIALIZATION | DEEP |
| `dl-cnn` | CNN basics | dl-nn-basics |  | SPECIALIZATION | DEEP |
| `dl-transformers-intro` | Transformers intro | dl-nn-basics | genai-embeddings | SPECIALIZATION | DEEP |

## PHASE_8_NLP

### Domain: NLP

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `nlp-awareness` | NLP awareness |  | nlp-path | OPTIONAL | AWARENESS |
| `nlp-path` | NLP learning path | nlp-awareness |  | OPTIONAL | AWARENESS |

## PHASE_9_GENAI_LLM

### Domain: Generative AI / LLMs

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `genai-awareness` | Generative AI awareness |  | genai-path | OPTIONAL | AWARENESS |
| `genai-path` | Generative AI learning path | genai-awareness |  | OPTIONAL | AWARENESS |
| `genai-embeddings` | Embeddings & semantic search | dl-transformers-intro | genai-rag | SPECIALIZATION | DEEP |
| `genai-rag` | RAG systems | genai-embeddings, be-fastapi-intro | genai-agents, genai-eval | SPECIALIZATION | DEEP |
| `genai-agents` | Tool-using agents | genai-rag |  | SPECIALIZATION | DEEP |
| `genai-eval` | LLM evaluation | genai-rag |  | SPECIALIZATION | DEEP |

## PHASE_UNSORTED

### Domain: Other

| Slug | Title | Prereqs | Unlocks | Track | Depth |
|------|-------|---------|---------|-------|-------|
| `web-html-basics` | HTML basics |  | web-css-basics, web-forms-a11y, web-js-basics | SPECIALIZATION | WORKING_KNOWLEDGE |
| `web-css-basics` | CSS basics | web-html-basics | web-forms-a11y, web-responsive | SPECIALIZATION | WORKING_KNOWLEDGE |
| `web-responsive` | Responsive design | web-css-basics |  | SPECIALIZATION | WORKING_KNOWLEDGE |
| `web-js-basics` | JavaScript basics | web-html-basics | web-react-intro, web-ts-intro | SPECIALIZATION | WORKING_KNOWLEDGE |
| `web-ts-intro` | TypeScript intro | web-js-basics |  | SPECIALIZATION | WORKING_KNOWLEDGE |
| `web-react-intro` | React intro | web-js-basics | web-nextjs-intro | SPECIALIZATION | WORKING_KNOWLEDGE |
| `web-nextjs-intro` | Next.js intro | web-react-intro |  | SPECIALIZATION | WORKING_KNOWLEDGE |
| `web-forms-a11y` | Forms & accessibility | web-html-basics, web-css-basics |  | SPECIALIZATION | WORKING_KNOWLEDGE |
| `ops-docker-intro` | Docker intro | cf-shell | ops-compose, ops-k8s-awareness, ops-observability | SPECIALIZATION | WORKING_KNOWLEDGE |
| `ops-compose` | Docker Compose | ops-docker-intro | ops-k8s-awareness | SPECIALIZATION | WORKING_KNOWLEDGE |
| `ops-ci-github-actions` | GitHub Actions CI | se-ci-basics |  | SPECIALIZATION | WORKING_KNOWLEDGE |
| `ops-linux-services` | Linux services basics | cf-linux-processes |  | SPECIALIZATION | WORKING_KNOWLEDGE |
| `ops-k8s-awareness` | Kubernetes awareness | ops-docker-intro, ops-compose |  | OPTIONAL | AWARENESS |
| `ops-observability` | Observability basics | ops-docker-intro | sys-observability-design | SPECIALIZATION | WORKING_KNOWLEDGE |
| `sys-scalability` | Scalability basics | be-persistence, db-indexes | sys-caching, sys-observability-design, sys-queues | SPECIALIZATION | STRONG |
| `sys-caching` | Caching strategies | sys-scalability |  | SPECIALIZATION | STRONG |
| `sys-queues` | Message queues | sys-scalability |  | SPECIALIZATION | STRONG |
| `sys-observability-design` | Observability in design | ops-observability, sys-scalability |  | SPECIALIZATION | STRONG |
