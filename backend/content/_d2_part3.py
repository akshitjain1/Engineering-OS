"""Domain 2 DSA: Trees, BST, Heaps, Graphs, Shortest Paths (Part 3)."""

from __future__ import annotations

from _d2_helpers import *

CONTENT = {}


def _add(slug, **kwargs):
    CONTENT[slug] = unit(**kwargs)


_D = (
    "Explain the idea without notes (language-independent).",
    "Implement in Java without copying.",
    "State the C++ equivalent at a high level if you already know it.",
    "Solve 2 representative problems independently.",
    "State time and space complexity of a correct approach.",
    "Name one common mistake for this topic.",
    "Score >= 80%.",
)


def _m(*skills):
    out = list(skills)
    for s in _D:
        if s not in out:
            out.append(s)
    return out


_add(
    "dsa-tree-terminology",
    hours=0.75,
    objective="Use root, child, parent, leaf, depth, and height correctly before writing tree code.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "A tree is connected and acyclic: one root, each non-root has exactly one parent. "
        "Depth counts edges from root to a node; height is the longest root-to-leaf distance (edge measure). "
        "Binary tree means at most two children (left/right). "
        + CPP["node"]
    ),
    mastery=_m("Define root, child, parent, leaf, depth, and height without notes."),
    resources=[
        bari_primary("dsa-tree-terminology", "Trees / Binary Trees"),
        mit_dd("dsa-tree-terminology", "MIT 6.006 — Binary Trees (Part 1)", MIT_L6),
        nc150("dsa-tree-terminology", "Trees"),
        lc_collection("dsa-tree-terminology"),
    ],
    questions=[
        q("dsa-tree-terminology-q1", "In a tree with root r, the depth of r is:",
          ["undefined", "0 (by the usual edge-count convention)", "1 always", "equal to the number of leaves"],
          "0 (by the usual edge-count convention)", "Depth from root; height of a single node is 0.", mastery=True),
        q("dsa-tree-terminology-q2", "A leaf is:",
          ["Any node with one child", "A node with no children", "The root only", "A node at depth 1"],
          "A node with no children", "Leaves terminate branches.", "easy"),
        q("dsa-tree-terminology-q3", "Which is always true of a tree (not a general graph)?",
          ["It has a cycle", "There is exactly one simple path between any two nodes",
           "Every node has degree 2", "It must be binary"],
          "There is exactly one simple path between any two nodes",
          "Acyclic + connected defines a tree.", "medium"),
        q("dsa-tree-terminology-q4", "Height of a tree (edge measure) with only root r:",
          ["-1", "0", "1", "undefined"],
          "0", "Single-node tree height is 0.", "easy"),
        q("dsa-tree-terminology-q5", "Parent vs child:",
          ["They are synonyms",
           "Parent is closer to the root; child is one edge away from its parent toward a leaf",
           "Child is always the root", "Parent has no edges"],
          "Parent is closer to the root; child is one edge away from its parent toward a leaf",
          "Direction matters in rooted trees.", "easy"),
        q("dsa-tree-terminology-q6", "A binary tree requires:",
          ["Exactly two children per node", "At most two children per node (left and/or right)",
           "Sorted keys", "Complete shape always"],
          "At most two children per node (left and/or right)",
          "Binary refers to arity cap, not BST order.", "medium"),
    ],
    exercises=[
        ex("dsa-tree-terminology-ex1", "Vocabulary on paper",
           "Draw a 5-node binary tree. Label root, internal nodes, leaves. Mark depth of each node and tree height. "
           "Write one sentence each for parent, child, sibling. No code yet.",
           difficulty="beginner", order=0),
    ],
)

_add(
    "dsa-binary-trees",
    hours=0.75,
    objective="Represent a binary tree with a Java node class using left/right references.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "A binary tree node holds a value and references to left and right children (either may be null). "
        "This is the same aliasing model as C++ Node* left/right — mutations through one reference are visible everywhere. "
        + CPP["node"] + " "
        "Do not confuse binary tree shape with BST ordering (next module)."
    ),
    mastery=_m("Implement a TreeNode class in Java with left and right fields."),
    resources=[
        bari_primary("dsa-binary-trees", "Binary Trees / Tree representation"),
        mit_dd("dsa-binary-trees", "MIT 6.006 — Binary Trees (Part 1)", MIT_L6),
        mit_dd("dsa-binary-trees", "MIT 6.006 — AVL Trees (optional)", MIT_L7),
        nc150("dsa-binary-trees", "Trees"),
        lc_collection("dsa-binary-trees"),
    ],
    questions=[
        q("dsa-binary-trees-q1",
          "class Node { int val; Node left, right; } — n.left = x makes:",
          ["A copy of x on the stack", "n.left refer to the same Node object as x (aliasing)",
           "x immutable", "The JVM clone x automatically"],
          "n.left refer to the same Node object as x (aliasing)",
          "References behave like C++ pointers to objects.", mastery=True),
        q("dsa-binary-trees-q2", "A null child means:",
          ["The node is deleted from memory immediately", "That side of the subtree is empty / absent",
           "The tree is invalid", "The node becomes a leaf automatically with value 0"],
          "That side of the subtree is empty / absent",
          "Null is the base case for recursion.", "easy"),
        q("dsa-binary-trees-q3", "Number of nodes in a binary tree with n nodes:",
          ["Always 2n", "n", "n-1 edges", "Cannot be determined"],
          "n", "Each node is one object in the heap graph.", "easy"),
        q("dsa-binary-trees-q4", "Skewed binary tree (each node has one child):",
          ["Has O(log n) height always", "Can have height n-1 like a linked list",
           "Cannot exist", "Must be a BST"],
          "Can have height n-1 like a linked list",
          "Shape affects complexity even without BST order.", "medium"),
        q("dsa-binary-trees-q5", "C++ struct Node { Node* left, *right; } vs Java Node left, right:",
          ["Unrelated models", "Both are references to heap nodes; Java has no explicit * syntax",
           "Java stores nodes on the stack only", "C++ cannot share subtrees"],
          "Both are references to heap nodes; Java has no explicit * syntax",
          "Same mental model for interviews.", "medium"),
        q("dsa-binary-trees-q6", "Complete binary tree (heap shape) requires:",
          ["All levels full except possibly the last, filled left-to-right",
           "BST ordering", "Every node has two children", "Height log n always"],
          "All levels full except possibly the last, filled left-to-right",
          "Complete ≠ full; used by heaps later.", "medium"),
    ],
    exercises=[
        ex("dsa-binary-trees-ex1", "TreeNode + two traversals",
           "Implement TreeNode and build a small tree in main. Write preorder and inorder recursively. "
           "Trace output on paper before running. "
           "NeetCode 150 Trees: Same Tree and Maximum Depth of Binary Tree (by name on NeetCode 150 — no invented URLs). "
           "TRANSFER (internal): Given preorder with null markers for missing children, explain how you would deserialize — no URL.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-tree-dfs",
    hours=1.0,
    objective="Perform preorder, inorder, and postorder DFS on a binary tree.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "DFS on trees visits each node once via recursion (or an explicit stack). "
        "Preorder: node, left, right. Inorder: left, node, right. Postorder: left, right, node. "
        "Base case: null child returns immediately. "
        "Time O(n), space O(h) for recursion stack where h is height."
    ),
    mastery=_m("Dry-run preorder, inorder, and postorder on a 3-node tree."),
    resources=[
        bari_primary("dsa-tree-dfs", "Tree traversals (pre/in/post order)"),
        mit_dd("dsa-tree-dfs", "MIT 6.006 — Depth-First Search", MIT_L10),
        nc150("dsa-tree-dfs", "Trees"),
        lc_collection("dsa-tree-dfs"),
    ],
    questions=[
        q("dsa-tree-dfs-q1",
          "Tree: root 2, left 1, right 3. Preorder (node-left-right) visits:",
          ["1,2,3", "2,1,3", "1,3,2", "3,2,1"],
          "2,1,3", "Visit node before subtrees.", mastery=True),
        q("dsa-tree-dfs-q2", "Same tree. Inorder visits:",
          ["2,1,3", "1,2,3", "1,3,2", "3,2,1"],
          "1,2,3", "Left, node, right.", "easy"),
        q("dsa-tree-dfs-q3", "Same tree. Postorder visits:",
          ["1,3,2", "2,1,3", "1,2,3", "3,1,2"],
          "1,3,2", "Children before node.", "easy"),
        q("dsa-tree-dfs-q4",
          "void dfs(Node n) { if (n == null) return; dfs(n.left); visit(n); dfs(n.right); } — this is:",
          ["Preorder", "Inorder", "Postorder", "Level order"],
          "Inorder", "Left before visit before right.", "medium"),
        q("dsa-tree-dfs-q5", "Time to visit all n nodes in any DFS order:",
          ["O(log n)", "O(n)", "O(n log n)", "O(h) only"],
          "O(n)", "Each node visited once.", "easy"),
        q("dsa-tree-dfs-q6", "Recursive DFS space on a skewed tree of height h:",
          ["O(1)", "O(h) call stack frames", "O(n) always regardless of shape", "O(log n) always"],
          "O(h) call stack frames",
          "Skewed tree can use O(n) stack.", "medium"),
        q("dsa-tree-dfs-q7", "Postorder is natural when you must:",
          ["Visit parent before children", "Process children before parent (e.g. delete bottom-up)",
           "Visit level by level", "Sort the keys"],
          "Process children before parent (e.g. delete bottom-up)",
          "Postorder = children first.", "medium"),
    ],
    exercises=[
        ex("dsa-tree-dfs-ex1", "Three orders + invert",
           "Implement preorder, inorder, postorder recursively. Dry-run all three on a 4-node tree. "
           "NeetCode 150 Trees: Invert Binary Tree — implement iteratively with a queue OR recursively. "
           "TRANSFER (internal): Delete a binary tree bottom-up using postorder logic — explain why postorder fits.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-tree-bfs",
    hours=1.0,
    objective="Traverse a binary tree level by level with a queue.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "BFS on trees uses a queue (ArrayDeque): enqueue root, dequeue node, visit, enqueue non-null children left then right. "
        "Produces level order. Time O(n), space O(w) where w is max width. "
        "Same queue pattern extends to graphs (after adjacency list exists)."
    ),
    mastery=_m("Implement level-order traversal with ArrayDeque."),
    resources=[
        bari_primary("dsa-tree-bfs", "Level-order / BFS on trees"),
        mit_dd("dsa-tree-bfs", "MIT 6.006 — Breadth-First Search", MIT_L9),
        nc150("dsa-tree-bfs", "Trees"),
        lc_collection("dsa-tree-bfs"),
    ],
    questions=[
        q("dsa-tree-bfs-q1",
          "Level order on root 2 (left 1, right 3, 3.right=4) visits:",
          ["2,1,3,4", "1,2,3,4", "2,3,1,4", "4,3,2,1"],
          "2,1,3,4", "Level 0 then 1 then 2.", mastery=True),
        q("dsa-tree-bfs-q2", "Why ArrayDeque over java.util.Stack for BFS?",
          ["Stack is faster for FIFO", "BFS needs FIFO; Stack is LIFO (legacy Stack is doubly-linked)",
           "Deque cannot hold nodes", "Stack is required by javac"],
          "BFS needs FIFO; Stack is LIFO (legacy Stack is doubly-linked)",
          "Use ArrayDeque as queue.", "easy"),
        q("dsa-tree-bfs-q3", "BFS queue size is bounded by:",
          ["Tree height only", "Maximum width of a level (can be O(n) for a perfect last level)",
           "Always 1", "Number of leaves only"],
          "Maximum width of a level (can be O(n) for a perfect last level)",
          "Wide trees need wide queues.", "medium"),
        q("dsa-tree-bfs-q4",
          "while (!q.isEmpty()) { Node u = q.remove(); visit(u); if (u.left != null) q.add(u.left); if (u.right != null) q.add(u.right); } — order enqueued:",
          ["Right before left", "Left child before right child at each node",
           "Random", "Children before parent"],
          "Left child before right child at each node",
          "Standard left-to-right level order.", "easy"),
        q("dsa-tree-bfs-q5", "BFS vs DFS for shortest path in an unweighted tree:",
          ["DFS always finds shortest", "BFS finds shortest number of edges from root",
           "Both fail", "Only preorder works"],
          "BFS finds shortest number of edges from root",
          "First time BFS reaches a node is via fewest edges.", "medium"),
        q("dsa-tree-bfs-q6", "Time complexity of tree BFS:",
          ["O(h)", "O(n) visiting each node once", "O(n log n)", "O(w^2)"],
          "O(n) visiting each node once",
          "Each node enqueued/dequeued once.", "easy"),
        q("dsa-tree-bfs-q7", "To track levels explicitly in Java you can:",
          ["Use a stack", "Process size=q.size() each iteration or use a null sentinel between levels",
           "Only use recursion", "Sort the queue"],
          "Process size=q.size() each iteration or use a null sentinel between levels",
          "Common interview pattern for zigzag/level lists.", "medium"),
    ],
    exercises=[
        ex("dsa-tree-bfs-ex1", "Level order + zigzag trace",
           "Implement level-order returning List<List<Integer>> using ArrayDeque; trace queue contents on a 3-level tree. "
           "NeetCode 150 Trees: Binary Tree Level Order Traversal. "
           "TRANSFER (internal): Find the right-side view (last node per level) using the same BFS skeleton — no URL.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-tree-height",
    hours=0.75,
    objective="Compute height and depth recursively and reason about balanced vs skewed trees.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Height of null is -1 or 0 depending on convention — pick one and stay consistent (here: null height -1, single node height 0). "
        "height(node) = 1 + max(height(left), height(right)) if measuring nodes, or edge version with null at -1. "
        "AVL rebalancing is optional (MIT L7 deep dive only — not a V1 gate)."
    ),
    mastery=_m("Compute height of a small tree and state O(n) time."),
    resources=[
        bari_primary("dsa-tree-height", "Tree height / balanced trees"),
        mit_dd("dsa-tree-height", "MIT 6.006 — Binary Trees (Part 1)", MIT_L6),
        mit_dd("dsa-tree-height", "MIT 6.006 — AVL Trees (optional deep dive)", MIT_L7),
        nc150("dsa-tree-height", "Trees"),
        lc_collection("dsa-tree-height"),
    ],
    questions=[
        q("dsa-tree-height-q1",
          "int height(Node n) { if (n == null) return -1; return 1 + Math.max(height(n.left), height(n.right)); } — height of single node:",
          ["-1", "0", "1", "2"],
          "0", "Null -1, node alone gives 0.", mastery=True),
        q("dsa-tree-height-q2", "Skewed chain of n nodes (each has one child). Height (edge measure) is:",
          ["O(log n)", "n-1", "0", "1"],
          "n-1", "Like a linked list.", "medium"),
        q("dsa-tree-height-q3", "Balanced tree (heights of subtrees differ by at most 1 at every node):",
          ["Forces height O(log n) for n nodes", "Guarantees BST order", "Means complete tree always", "Has no leaves"],
          "Forces height O(log n) for n nodes",
          "Balance controls worst-case depth.", "medium"),
        q("dsa-tree-height-q4", "Computing height with a post-order recurrence visits each node:",
          ["Once", "Twice always", "Only leaves", "Only root"],
          "Once", "Classic O(n) aggregation.", "easy"),
        q("dsa-tree-height-q5", "Depth of a node vs height of subtree rooted at that node:",
          ["Same thing", "Depth is from global root; height is from that node downward",
           "Depth is always larger", "Height includes ancestors"],
          "Depth is from global root; height is from that node downward",
          "Do not conflate the two.", "easy"),
        q("dsa-tree-height-q6", "AVL trees (MIT L7 optional):",
          ["Are required V1 mastery", "Are an optional deep dive; V1 only needs balanced-vs-skewed awareness",
           "Replace BSTs entirely", "Have no rotations"],
          "Are an optional deep dive; V1 only needs balanced-vs-skewed awareness",
          "Know they exist; do not implement AVL for V1 gate.", "easy"),
    ],
    exercises=[
        ex("dsa-tree-height-ex1", "Height + balanced check sketch",
           "Implement height (edge convention). On paper, decide if a drawn tree is height-balanced. "
           "NeetCode 150 Trees: Diameter of Binary Tree — height helper reused. "
           "TRANSFER (internal): Explain why a skewed BST loses O(log n) search — tie height to complexity.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-tree-paths",
    hours=1.0,
    objective="Accumulate values along root-to-leaf or node-to-node paths with DFS backtracking.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Path problems walk the tree while carrying state (running sum, current path list). "
        "At each node, push choice, recurse, pop (backtrack). "
        "Root-to-leaf: record when reaching a leaf. Node-to-node (e.g. LCA path): may need post-order aggregation."
    ),
    mastery=_m("Dry-run a path-sum check on a tiny tree."),
    resources=[
        bari_primary("dsa-tree-paths", "Tree path problems"),
        mit_dd("dsa-tree-paths", "MIT 6.006 — Binary Trees (Part 1)", MIT_L6),
        nc150("dsa-tree-paths", "Trees"),
        lc_collection("dsa-tree-paths"),
    ],
    questions=[
        q("dsa-tree-paths-q1",
          "hasPathSum(root, target): at leaf with running sum s, success when:",
          ["s == 0 always", "s equals target after subtracting node values along the path",
           "target == 0 at root only", "leaf value equals target regardless of ancestors"],
          "s equals target after subtracting node values along the path",
          "Usually pass remaining = target - node.val down.", mastery=True),
        q("dsa-tree-paths-q2", "Backtracking template on trees:",
          ["Never pop state", "Add node to path, recurse, remove node before returning to parent",
           "Only BFS works", "Must sort nodes first"],
          "Add node to path, recurse, remove node before returning to parent",
          "Choose/explore/unchoose on branches.", "medium"),
        q("dsa-tree-paths-q3",
          "Path 2→1→3 with values summing to 6. hasPathSum(6) from root:",
          ["Always false", "True if you subtract along edges and check at leaf",
           "Only checks root value", "Requires BST"],
          "True if you subtract along edges and check at leaf",
          "6 - 2 - 1 - 3 = 0 at leaf.", "medium"),
        q("dsa-tree-paths-q4", "Space for storing all root-to-leaf paths in a tree with n nodes worst case:",
          ["O(1)", "O(n) paths each up to O(n) — O(n^2) output size possible",
           "O(log n)", "O(n) total always"],
          "O(n) paths each up to O(n) — O(n^2) output size possible",
          "Skewed tree has one long path but many nodes in output lists.", "hard"),
        q("dsa-tree-paths-q5", "DFS path search time:",
          ["O(h)", "O(n) to visit each node once in a single-path check", "O(n^2) always", "O(log n)"],
          "O(n) to visit each node once in a single-path check",
          "Each node constant work for existence check.", "easy"),
        q("dsa-tree-paths-q6", "Global variable vs passing sum parameter:",
          ["Always use global", "Pass remaining sum as parameter — clearer and thread-safe",
           "Java forbids parameters", "BFS cannot pass parameters"],
          "Pass remaining sum as parameter — clearer and thread-safe",
          "Prefer explicit parameters over mutable globals.", "easy"),
    ],
    exercises=[
        ex("dsa-tree-paths-ex1", "Path sum + collect paths",
           "Implement hasPathSum and a version collecting all root-to-leaf paths (backtracking). Trace on a 4-node tree. "
           "NeetCode 150 Trees: Path Sum and Binary Tree Paths. "
           "TRANSFER (internal): Longest univalue path — explain post-order max from each node without coding full solution.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-tree-construction",
    hours=1.25,
    objective="Rebuild a binary tree from preorder and inorder traversals at V1 depth.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Preorder gives root first; inorder splits left subtree (left of root in inorder) and right subtree. "
        "Recursively partition index ranges — O(n) with a hash map of inorder indices. "
        "Not every traversal pair uniquely determines a tree (need valid split)."
    ),
    mastery=_m("Explain why inorder + preorder can reconstruct a binary tree."),
    resources=[
        bari_primary("dsa-tree-construction", "Tree construction from traversals"),
        mit_dd("dsa-tree-construction", "MIT 6.006 — Binary Trees (Part 1)", MIT_L6),
        nc150("dsa-tree-construction", "Trees"),
        lc_collection("dsa-tree-construction"),
    ],
    questions=[
        q("dsa-tree-construction-q1",
          "preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]. Root is:",
          ["9", "3", "20", "15"],
          "3", "First preorder element is root.", mastery=True),
        q("dsa-tree-construction-q2", "In inorder, elements left of root belong to:",
          ["Right subtree only", "Left subtree", "Both subtrees", "Neither — discard them"],
          "Left subtree", "Inorder layout: left, root, right.", "easy"),
        q("dsa-tree-construction-q3", "Why store inorder index in HashMap<Integer,Integer>?",
          ["Required for BFS", "O(1) lookup of root position to split ranges",
           "Java trees need maps", "To sort preorder"],
          "O(1) lookup of root position to split ranges",
          "Avoid scanning inorder each recursion.", "medium"),
        q("dsa-tree-construction-q4", "preorder alone (without null markers) for arbitrary binary trees:",
          ["Always unique", "Not sufficient — multiple trees can share preorder",
           "Is sufficient if BST", "Is sufficient if complete"],
          "Not sufficient — multiple trees can share preorder",
          "Need inorder or null-marked preorder.", "medium"),
        q("dsa-tree-construction-q5", "Time to build tree from n nodes with hash map:",
          ["O(n log n)", "O(n)", "O(n^2) always", "O(h)"],
          "O(n)", "Each node processed once.", "medium"),
        q("dsa-tree-construction-q6", "After choosing root from preorder[lo], left subtree preorder segment length equals:",
          ["Size of right inorder segment", "Size of left inorder segment (rootIn - inLo)",
           "Always 1", "n/2 always"],
          "Size of left inorder segment (rootIn - inLo)",
          "Left count determines preorder partition.", "hard"),
    ],
    exercises=[
        ex("dsa-tree-construction-ex1", "Build from pre+in",
           "Implement buildTree(preorder, inorder) using index ranges + HashMap. Dry-run on 5 nodes. "
           "NeetCode 150 Trees: Construct Binary Tree from Preorder and Inorder Traversal. "
           "TRANSFER (internal): Which extra information would preorder+postorder still miss for uniqueness?",
           difficulty="advanced", order=0),
    ],
)

_add(
    "dsa-bst-search",
    hours=0.75,
    objective="Search a BST using the ordering invariant left < node < right.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "BST property: every node in left subtree has keys less than node; right subtree keys greater (V1 convention: no duplicates or send to one side). "
        "Search compares target with node.val and goes left or right. "
        "O(h) time; h is height (O(log n) if balanced, O(n) if skewed). "
        + CPP["node"]
    ),
    mastery=_m("Trace search for a present and absent key in a small BST."),
    resources=[
        bari_primary("dsa-bst-search", "Binary Search Trees — search"),
        mit_dd("dsa-bst-search", "MIT 6.006 — Binary Trees (Part 1)", MIT_L6),
        nccore("dsa-bst-search", "Design Binary Search Tree"),
        nc150("dsa-bst-search", "Trees"),
        lc_collection("dsa-bst-search"),
    ],
    questions=[
        q("dsa-bst-search-q1",
          "BST: root 8, left 3, right 10. Search 3 goes:",
          ["Right from 8 then stop", "Left from 8 to 3", "Compare only root", "Fails — 3 cannot exist"],
          "Left from 8 to 3", "3 < 8 → left.", mastery=True),
        q("dsa-bst-search-q2",
          "Node search(Node n, int t) { if (n==null) return null; if (t==n.val) return n; "
          "return t < n.val ? search(n.left,t) : search(n.right,t); } — missing key 5 in above tree returns:",
          ["Node 8", "null", "Node 3", "Throws"],
          "null", "Eventually null branch.", "easy"),
        q("dsa-bst-search-q3", "Worst-case search time in skewed BST with n nodes:",
          ["O(log n)", "O(n)", "O(1)", "O(n log n)"],
          "O(n)", "Degenerates to linked list.", "medium"),
        q("dsa-bst-search-q4", "Iterative BST search uses:",
          ["Queue only", "While loop moving left/right pointers — O(h) space O(1)",
           "Must use recursion", "HashMap only"],
          "While loop moving left/right pointers — O(h) space O(1)",
          "Iterative avoids stack frames.", "medium"),
        q("dsa-bst-search-q5", "C++ pointer walk vs Java reference walk in BST search:",
          ["Different semantics", "Same logic; Java uses Node cur = cur.left instead of cur=cur->left",
           "Java cannot go left", "C++ cannot return null"],
          "Same logic; Java uses Node cur = cur.left instead of cur=cur->left",
          "Algorithm identical.", "easy"),
        q("dsa-bst-search-q6", "Local check left.val < node.val < right.val at each node:",
          ["Proves global BST property always", "Is necessary but not sufficient for global validity (see validate topic)",
           "Is useless", "Only for heaps"],
          "Is necessary but not sufficient for global validity (see validate topic)",
          "Global bounds required for validation.", "medium"),
    ],
    exercises=[
        ex("dsa-bst-search-ex1", "Design BST search",
           "Implement BST Node and search (recursive + iterative). Trace search hits/misses on a 7-node BST. "
           "NeetCode Core Skills: Design Binary Search Tree (search + insert stub). "
           "NeetCode 150 Trees: Search in a Binary Search Tree. "
           "TRANSFER (internal): Find closest value to target in BST — explain prune direction.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-bst-insert",
    hours=1.0,
    objective="Insert into a BST while preserving ordering.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Insert walks like search until null child slot found; attach new node. "
        "Duplicates: pick a consistent policy (e.g. go left for <=). "
        "Return root reference if implementing functionally; in Java often mutate tree in place."
    ),
    mastery=_m("Insert a key and draw the resulting BST."),
    resources=[
        bari_primary("dsa-bst-insert", "BST insertion"),
        mit_dd("dsa-bst-insert", "MIT 6.006 — Binary Trees (Part 1)", MIT_L6),
        nccore("dsa-bst-insert", "Design Binary Search Tree"),
        nc150("dsa-bst-insert", "Trees"),
        lc_collection("dsa-bst-insert"),
    ],
    questions=[
        q("dsa-bst-insert-q1",
          "Insert 4 into BST root 5, left 3, right 7. New node attaches as:",
          ["Right child of 3", "Left child of 5", "Root", "Right child of 7"],
          "Right child of 3", "4 < 5 go left; 4 > 3 go right of 3.", mastery=True),
        q("dsa-bst-insert-q2",
          "insert(Node n, int v): if n==null return new Node(v); if v<=n.val n.left=insert(n.left,v); else n.right=insert(n.right,v); return n; — time:",
          ["O(1)", "O(h)", "O(n log n) always", "O(n) always for every insert regardless of tree"],
          "O(h)", "Path length to leaf slot.", "medium"),
        q("dsa-bst-insert-q3", "Inserting sorted 1..n into empty BST yields:",
          ["Complete tree", "Skewed chain height n-1", "Random shape", "Heap"],
          "Skewed chain height n-1", "Classic BST pitfall.", "medium"),
        q("dsa-bst-insert-q4", "Why return Node from recursive insert?",
          ["Java requires it for void methods", "Root may change when tree empty; also uniform recursion pattern",
           "Garbage collection", "To copy the tree"],
          "Root may change when tree empty; also uniform recursion pattern",
          "insert(empty) returns new root.", "medium"),
        q("dsa-bst-insert-q5", "Insert vs search loop structure:",
          ["Unrelated", "Same comparisons; insert stops at null to attach new node",
           "Insert uses BFS", "Search uses queue"],
          "Same comparisons; insert stops at null to attach new node",
          "Shared BST walk.", "easy"),
    ],
    exercises=[
        ex("dsa-bst-insert-ex1", "Insert + inorder check",
           "Complete Design BST insert. After 5 inserts, inorder must be sorted. "
           "NeetCode 150 Trees: Insert into a Binary Search Tree. "
           "TRANSFER (internal): Insert into a max-heap is different — one sentence on why BST insert ≠ heap insert.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-bst-delete",
    hours=1.25,
    objective="Delete a BST node including the two-child case via successor or predecessor.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Cases: (0) not found; (1) leaf — unlink; (2) one child — splice child up; "
        "(3) two children — replace value with inorder successor (min of right subtree) or predecessor, then delete successor node. "
        "O(h) time."
    ),
    mastery=_m("Explain successor-based delete on a node with two children."),
    resources=[
        bari_primary("dsa-bst-delete", "BST deletion"),
        mit_dd("dsa-bst-delete", "MIT 6.006 — Binary Trees (Part 1)", MIT_L6),
        nc150("dsa-bst-delete", "Trees"),
        lc_collection("dsa-bst-delete"),
    ],
    questions=[
        q("dsa-bst-delete-q1", "Delete leaf node:",
          ["Rotate tree", "Set parent pointer to null", "Rebuild from traversals", "Must swap with root"],
          "Set parent pointer to null", "Simple unlink.", mastery=True),
        q("dsa-bst-delete-q2", "Node with one right child only:",
          ["Delete both", "Replace node with its child (splice)", "Forbidden in BST", "Swap with root"],
          "Replace node with its child (splice)", "Standard case 2.", "easy"),
        q("dsa-bst-delete-q3", "Two children: inorder successor is:",
          ["Max of left subtree", "Min of right subtree", "Root's parent", "Any leaf"],
          "Min of right subtree", "Smallest key greater than node.", "medium"),
        q("dsa-bst-delete-q4", "After copying successor value into node, you must:",
          ["Stop — tree is done", "Delete the original successor node (now duplicate value) in right subtree",
           "Rebalance AVL always", "Reinsert all nodes"],
          "Delete the original successor node (now duplicate value) in right subtree",
          "Two-step for case 3.", "medium"),
        q("dsa-bst-delete-q5", "Delete time complexity:",
          ["O(1)", "O(h) — search + maybe successor walk", "O(n log n)", "O(n) always"],
          "O(h) — search + maybe successor walk",
          "Successor is O(h) in skewed tree.", "medium"),
        q("dsa-bst-delete-q6", "Deleting root with two children:",
          ["Impossible", "Use successor/predecessor copy then delete duplicate leaf/single-child node",
           "Must pick new random root", "Only works in AVL"],
          "Use successor/predecessor copy then delete duplicate leaf/single-child node",
          "Case 3 applies to any node including root.", "medium"),
    ],
    exercises=[
        ex("dsa-bst-delete-ex1", "Delete all three cases",
           "Extend Design BST with delete covering 0/1/2-child cases. Test each case on paper first. "
           "NeetCode 150 Trees: Delete Node in a BST. "
           "TRANSFER (internal): Why delete is harder than insert in interviews — list the three cases.",
           difficulty="advanced", order=0),
    ],
)

_add(
    "dsa-bst-validate",
    hours=1.0,
    objective="Validate BST property with global min/max bounds, not just local checks.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Valid BST: all nodes in left subtree < node.val < all in right (strict or consistent duplicate policy). "
        "Local parent-child comparison fails for deep violations — pass (min, max) allowed range down recursion. "
        "Inorder must be strictly increasing for strict BST."
    ),
    mastery=_m("Explain why local left<node<right at each node is insufficient."),
    resources=[
        bari_primary("dsa-bst-validate", "BST validation"),
        mit_dd("dsa-bst-validate", "MIT 6.006 — Binary Trees (Part 1)", MIT_L6),
        nc150("dsa-bst-validate", "Trees"),
        lc_collection("dsa-bst-validate"),
    ],
    questions=[
        q("dsa-bst-validate-q1",
          "Tree: root 5, left subtree root 3 with right child 6. Local checks at each node pass parent comparison. Valid BST?",
          ["Yes", "No — 6 is in left subtree of 5 but 6 > 5", "Yes if complete", "Only invalid if duplicates"],
          "No — 6 is in left subtree of 5 but 6 > 5",
          "Global bound violation.", mastery=True),
        q("dsa-bst-validate-q2",
          "validate(n, min, max): false if n.val <= min or n.val >= max (strict). Left recurse uses:",
          ["Same bounds", "(min, n.val) as new max for left; (n.val, max) as new min for right",
           "No bounds needed", "(max, min)"],
          "(min, n.val) as new max for left; (n.val, max) as new min for right",
          "Tighten allowed interval.", "medium"),
        q("dsa-bst-validate-q3", "Inorder traversal of valid strict BST:",
          ["Is random", "Produces strictly increasing keys", "Is decreasing", "Only works on complete trees"],
          "Produces strictly increasing keys",
          "Alternative validation: check inorder monotonic.", "medium"),
        q("dsa-bst-validate-q4", "Empty tree is valid BST:",
          ["False", "True vacuously", "Only if root null throws", "Depends on heap property"],
          "True vacuously", "Base case true.", "easy"),
        q("dsa-bst-validate-q5", "validate using Integer null as unbounded:",
          ["Illegal in Java", "Common pattern: null min/max means no bound on that side",
           "Only works in C++", "Requires AVL"],
          "Common pattern: null min/max means no bound on that side",
          "Use wrapper or long sentinels carefully.", "medium"),
    ],
    exercises=[
        ex("dsa-bst-validate-ex1", "Bounds validate + inorder check",
           "Implement isValidBST with min/max Long bounds. Cross-check with inorder list on 3 test trees. "
           "NeetCode 150 Trees: Validate Binary Search Tree. "
           "TRANSFER (internal): Minimal counterexample where local-only check passes — draw it.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-bst-ordered-properties",
    hours=0.75,
    objective="Use inorder traversal of a BST as a sorted sequence and find order statistics.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Inorder visits keys in sorted order for a BST. "
        "kth smallest: reverse inorder (right-root-left) for kth largest, or stop after k steps inorder. "
        "Balancing (AVL) is deferred — MIT L7 optional only."
    ),
    mastery=_m("State kth-smallest via inorder and give O(h+k) intuition."),
    resources=[
        bari_primary("dsa-bst-ordered-properties", "BST ordered traversal / kth element"),
        mit_dd("dsa-bst-ordered-properties", "MIT 6.006 — AVL Trees (optional)", MIT_L7),
        nc150("dsa-bst-ordered-properties", "Trees"),
        lc_collection("dsa-bst-ordered-properties"),
    ],
    questions=[
        q("dsa-bst-ordered-properties-q1", "Inorder of a valid BST outputs keys:",
          ["In random order", "Non-decreasing (sorted) order", "Level order", "Postorder"],
          "Non-decreasing (sorted) order", "Core BST property.", mastery=True),
        q("dsa-bst-ordered-properties-q2", "kth smallest (1-indexed) with inorder:",
          ["Always O(n) — must visit all nodes even after finding k", "Stop after k visits — O(h+k)",
           "Requires heap sort first", "Impossible on BST"],
          "Stop after k visits — O(h+k)",
          "Early exit once counter hits k.", "medium"),
        q("dsa-bst-ordered-properties-q3", "Iterative inorder uses:",
          ["Queue only", "Stack simulating recursion", "PriorityQueue only", "Union-Find"],
          "Stack simulating recursion", "Go left pushing nodes, pop, visit, go right.", "medium"),
        q("dsa-bst-ordered-properties-q4", "kth largest from kth smallest:",
          ["kth largest = kth smallest always", "kth largest relates to reverse inorder or (n-k+1)th smallest",
           "Requires Dijkstra", "Only with AVL"],
          "kth largest relates to reverse inorder or (n-k+1)th smallest",
          "Dual order statistic.", "medium"),
        q("dsa-bst-ordered-properties-q5", "Successor of a node (next larger) in BST:",
          ["Always parent", "If right subtree exists: min of right; else climb until coming from left",
           "Random leaf", "Inorder predecessor only"],
          "If right subtree exists: min of right; else climb until coming from left",
          "Standard successor algorithm.", "hard"),
    ],
    exercises=[
        ex("dsa-bst-ordered-properties-ex1", "Kth smallest + range sum sketch",
           "Implement kthSmallest with iterative inorder. Trace k=3 on a 7-node BST. "
           "NeetCode 150 Trees: Kth Smallest Element in a BST and Lowest Common Ancestor of a BST. "
           "TRANSFER (internal): Merge two BSTs into sorted list — why inorder helps.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-heap-structure",
    hours=1.0,
    objective="Explain a binary heap as a complete tree stored in an array with heap-order property.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Min-heap: parent <= children. Stored in array: parent at i, children at 2i+1 and 2i+2 (0-indexed). "
        "Complete tree shape enables array storage. "
        + CPP["heap"] + " "
        "Java PriorityQueue default is min-heap; C++ priority_queue default is max-heap — invert with Comparator or greater<>."
    ),
    mastery=_m("Map heap indices for parent/children and state min-heap property."),
    resources=[
        bari_video("dsa-heap-structure", "Abdul Bari — Heap / HeapSort / Heapify / Priority Queue", BARI_HEAP),
        mit_dd("dsa-heap-structure", "MIT 6.006 — Binary Heaps", MIT_L8),
        nccore("dsa-heap-structure", "Design Heap"),
        nc150("dsa-heap-structure", "Heap / Priority Queue"),
        lc_collection("dsa-heap-structure"),
    ],
    questions=[
        q("dsa-heap-structure-q1", "Min-heap property:",
          ["Left child < parent only", "Every parent <= its children (both sides)",
           "Inorder is sorted", "Root is maximum"],
          "Every parent <= its children (both sides)",
          "Heap-order, not BST-order.", mastery=True),
        q("dsa-heap-structure-q2", "Node at index i (0-based). Parent index:",
          ["i-1", "(i-1)/2 integer division", "2i", "i/2 always"],
          "(i-1)/2 integer division", "Inverse of child formulas.", "easy"),
        q("dsa-heap-structure-q3", "Left child of i:",
          ["2i", "2*i+1", "i+1", "2*i-1"],
          "2*i+1", "Standard 0-index heap.", "easy"),
        q("dsa-heap-structure-q4", "Why must heap be complete (filled left-to-right)?",
          ["For BST order", "So array representation has no gaps and indices predict shape",
           "For graph BFS", "For hash tables"],
          "So array representation has no gaps and indices predict shape",
          "Complete shape ↔ contiguous array.", "medium"),
        q("dsa-heap-structure-q5", "Java new PriorityQueue<>() without comparator extracts:",
          ["Largest element first", "Smallest element first (min-heap)",
           "Random element", "Same as C++ default"],
          "Smallest element first (min-heap)",
          "Opposite default from C++ priority_queue.", "medium"),
        q("dsa-heap-structure-q6", "C++ priority_queue<int> top() returns:",
          ["Minimum", "Maximum by default", "Median", "First inserted"],
          "Maximum by default", "Use greater<int> for min-heap analogue.", "medium"),
        q("dsa-heap-structure-q7", "Height of heap with n elements:",
          ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
          "O(log n)", "Complete tree height.", "easy"),
    ],
    exercises=[
        ex("dsa-heap-structure-ex1", "Array heap + indices",
           "On paper: place [1,3,2,7,5,4] into array min-heap indices; verify parent<=children. "
           "Implement parent/left/right index helpers in Java. "
           "NeetCode Core Skills: Design Heap (push/pop/peek using array). "
           "TRANSFER (internal): Why heap is not sorted array — one paragraph.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-priority-queue",
    hours=0.75,
    objective="Use PriorityQueue as a priority ADT and contrast with BST for dynamic extrema.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Priority queue ADT: insert, extract-min/max, peek. Binary heap gives O(log n) insert/extract. "
        "BST can do ordered operations but heap is simpler for only-min or only-max needs. "
        + CPP["heap"] + " "
        "Use PriorityQueue with Comparator.reverseOrder() for max-heap behavior in Java."
    ),
    mastery=_m("Contrast heap vs BST for repeated extract-min operations."),
    resources=[
        bari_primary("dsa-priority-queue", "Priority Queue / Heap ADT"),
        mit_dd("dsa-priority-queue", "MIT 6.006 — Binary Heaps", MIT_L8),
        nc150("dsa-priority-queue", "Heap / Priority Queue"),
        lc_collection("dsa-priority-queue"),
    ],
    questions=[
        q("dsa-priority-queue-q1", "PriorityQueue in Java is backed by:",
          ["Linked list sorted on insert", "Binary heap in an array", "HashMap", "BST always"],
          "Binary heap in an array", "Standard library choice.", mastery=True),
        q("dsa-priority-queue-q2", "poll() on PriorityQueue:",
          ["Peeks without remove", "Removes and returns head (min by default)", "Clears queue", "Sorts entire queue O(n log n) each time"],
          "Removes and returns head (min by default)", "Extract-min.", "easy"),
        q("dsa-priority-queue-q3", "For max-heap in Java:",
          ["Use Stack", "new PriorityQueue<>(Comparator.reverseOrder()) or custom Comparator",
           "Impossible", "Use TreeMap only"],
          "new PriorityQueue<>(Comparator.reverseOrder()) or custom Comparator",
          "Explicit inversion vs C++ default.", "medium"),
        q("dsa-priority-queue-q4", "BST vs heap for only needing global minimum repeatedly:",
          ["BST always faster", "Heap simpler O(log n) extract-min; BST works but more overhead for just min",
           "Heap cannot extract min", "Equal always"],
          "Heap simpler O(log n) extract-min; BST works but more overhead for just min",
          "Pick structure to operations needed.", "medium"),
        q("dsa-priority-queue-q5", "offer(x) and add(x) on PriorityQueue:",
          ["Different structures", "Both insert; add throws on failure, offer returns boolean",
           "offer removes", "add is O(1) always"],
          "Both insert; add throws on failure, offer returns boolean",
          "Both heap insert O(log n).", "easy"),
        q("dsa-priority-queue-q6", "Iterating PriorityQueue without poll:",
          ["Guaranteed sorted iteration order", "Iterator order not guaranteed sorted — only poll gives extrema order",
           "Illegal", "Same as Collections.sort"],
          "Iterator order not guaranteed sorted — only poll gives extrema order",
          "Common misconception.", "medium"),
    ],
    exercises=[
        ex("dsa-priority-queue-ex1", "Two heaps pattern intro",
           "Use PriorityQueue to merge k sorted lists conceptually (poll smallest, push next). "
           "NeetCode 150 Heap: Last Stone Weight. "
           "TRANSFER (internal): Median from stream needs two heaps — sketch max-heap lower half + min-heap upper half.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-heapify",
    hours=1.0,
    objective="Build a heap with sift-up insert and sift-down heapify; know Floyd O(n) build.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Sift-up: after append at end, swap with parent while heap violated. "
        "Sift-down (heapify): at index i, swap with smaller child until property restored. "
        "Floyd build: sift-down from last non-leaf down to root — O(n) total. "
        "Relates to heap-sort seen earlier — same sift-down core."
    ),
    mastery=_m("Explain Floyd heapify at a high level and why it is O(n)."),
    resources=[
        bari_video("dsa-heapify", "Abdul Bari — Heap / HeapSort / Heapify / Priority Queue", BARI_HEAP),
        mit_dd("dsa-heapify", "MIT 6.006 — Binary Heaps", MIT_L8),
        nccore("dsa-heapify", "Design Heap"),
        nc150("dsa-heapify", "Heap / Priority Queue"),
        lc_collection("dsa-heapify"),
    ],
    questions=[
        q("dsa-heapify-q1", "After inserting into min-heap at end, fix by:",
          ["Sift-down from root", "Sift-up toward root swapping with parent while too small",
           "Sort array", "BFS"],
          "Sift-up toward root swapping with parent while too small",
          "Bubble new leaf upward.", mastery=True),
        q("dsa-heapify-q2", "Sift-down at index i compares node with:",
          ["Parent only", "Children; swap with smaller child in min-heap if violation",
           "Siblings only", "Root only"],
          "Children; swap with smaller child in min-heap if violation",
          "Pick min child to promote.", "medium"),
        q("dsa-heapify-q3", "Floyd heapify starts at index:",
          ["0 (root)", "Last non-leaf (n/2 - 1) down to 0", "Last leaf only", "Random index"],
          "Last non-leaf (n/2 - 1) down to 0",
          "Leaves already valid subtrees.", "medium"),
        q("dsa-heapify-q4", "Building heap by n successive inserts:",
          ["O(n)", "O(n log n)", "O(log n)", "O(n^2) always better than Floyd"],
          "O(n log n)", "Each insert O(log n). Floyd can be O(n).", "medium"),
        q("dsa-heapify-q5", "Single sift-down height:",
          ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
          "O(log n)", "Along tree height.", "easy"),
        q("dsa-heapify-q6", "Heap-sort relationship:",
          ["Unrelated to sift-down", "Repeated extract-max/min uses sift-down — same fix operation as heapify",
           "Uses only BFS", "Requires BST"],
          "Repeated extract-max/min uses sift-down — same fix operation as heapify",
          "Connect to prior heap-sort module.", "medium"),
    ],
    exercises=[
        ex("dsa-heapify-ex1", "Implement heapify",
           "Complete Design Heap: push (sift-up), pop (swap root/last, sift-down), heapify(int[]). "
           "Trace Floyd build on [4,10,3,5,1]. "
           "NeetCode 150 Heap: Kth Largest Element in an Array (heap of size k). "
           "TRANSFER (internal): When is heapify preferred over sort for top-k only?",
           difficulty="advanced", order=0),
    ],
)

_add(
    "dsa-top-k",
    hours=1.0,
    objective="Select top K elements with a size-k heap choosing min vs max heap correctly.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Top K largest: maintain min-heap of size k — if new element > heap min, replace. "
        "Top K smallest: max-heap of size k. "
        "Alternative: sort O(n log n) or quickselect O(n) average — heap is O(n log k). "
        + CPP["heap"]
    ),
    mastery=_m("Choose min-heap vs max-heap for top-K largest vs smallest."),
    resources=[
        bari_primary("dsa-top-k", "Top K / Heap selection"),
        mit_dd("dsa-top-k", "MIT 6.006 — Binary Heaps", MIT_L8),
        nc150("dsa-top-k", "Heap / Priority Queue"),
        lc_collection("dsa-top-k"),
    ],
    questions=[
        q("dsa-top-k-q1", "Top 3 largest in stream — maintain heap of size 3 that is:",
          ["Max-heap of all n", "Min-heap of the current 3 largest candidates",
           "BST", "Queue"],
          "Min-heap of the current 3 largest candidates",
          "Root is smallest of the top-3 set; evict if new value larger.", mastery=True),
        q("dsa-top-k-q2", "Min-heap size k holds k largest seen so far. New value v > heap.peek():",
          ["Ignore v", "Poll min, offer v", "Clear heap", "Sort entire array"],
          "Poll min, offer v", "Replace weakest of top-k.", "medium"),
        q("dsa-top-k-q3", "Time for n elements, heap size k:",
          ["O(n k)", "O(n log k)", "O(n log n) always required", "O(k)"],
          "O(n log k)", "Each of n updates O(log k).", "medium"),
        q("dsa-top-k-q4", "Top K smallest uses:",
          ["Min-heap size k", "Max-heap size k", "Stack", "Union-Find"],
          "Max-heap size k", "Dual of largest case.", "easy"),
        q("dsa-top-k-q5", "Top K frequent elements typically needs:",
          ["Only sort by value", "Frequency map then heap or bucket on frequencies",
           "BFS", "Graph adjacency list"],
          "Frequency map then heap or bucket on frequencies",
          "Count first, select on counts.", "medium"),
        q("dsa-top-k-q6", "Java PriorityQueue for top-3 largest — comparator default (min-heap) is:",
          ["Wrong always", "Correct for size-k largest pattern without reversal",
           "Requires reverseOrder for this pattern", "Same as C++ default max"],
          "Correct for size-k largest pattern without reversal",
          "Min-heap of size k for largest values.", "medium"),
    ],
    exercises=[
        ex("dsa-top-k-ex1", "Top K frequent + trace",
           "Implement topKFrequent using HashMap + size-k min-heap. Trace on [1,1,1,2,2,3], k=2. "
           "NeetCode 150 Heap: Top K Frequent Elements and Top K Frequent Words (compare tie-breaking). "
           "TRANSFER (internal): When bucket sort beats heap for top-k — hint at frequency bound.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-heap-scheduling",
    hours=1.0,
    objective="Use heaps for scheduling and greedy time/priority patterns.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Heap scheduling pattern: always process highest-priority or earliest-deadline next. "
        "Examples: task scheduler cooldown (max-heap counts), merge k sorted lists, meeting rooms (min-heap of end times). "
        "Not OS kernel scheduling theory — interview greedy + heap."
    ),
    mastery=_m("Describe one scheduling pattern that needs a heap."),
    resources=[
        bari_primary("dsa-heap-scheduling", "Heap applications / scheduling"),
        mit_dd("dsa-heap-scheduling", "MIT 6.006 — Binary Heaps", MIT_L8),
        nc150("dsa-heap-scheduling", "Heap / Priority Queue"),
        lc_collection("dsa-heap-scheduling"),
    ],
    questions=[
        q("dsa-heap-scheduling-q1", "Task scheduler with cooldown: greedy picks:",
          ["Lowest frequency task always", "Highest remaining frequency task when idle allows",
           "Random task", "BFS order"],
          "Highest remaining frequency task when idle allows",
          "Max-heap on counts.", mastery=True),
        q("dsa-heap-scheduling-q2", "Merge k sorted lists efficiently:",
          ["Sort all together O(n log n) only", "Min-heap of size k holding current head of each list",
           "Union-Find", "DFS only"],
          "Min-heap of size k holding current head of each list",
          "Poll min, push next from that list.", "medium"),
        q("dsa-heap-scheduling-q3", "Meeting rooms II (minimum rooms): sort by start; min-heap stores:",
          ["Start times", "End times of ongoing meetings — free room if earliest end <= new start",
           "All attendees", "Random"],
          "End times of ongoing meetings — free room if earliest end <= new start",
          "Min end time = room freeing soonest.", "hard"),
        q("dsa-heap-scheduling-q4", "Why heap not sort for streaming tasks arriving online:",
          ["Heap cannot insert", "Need dynamic extract-extremum O(log n) as tasks arrive",
           "Sort is always O(1)", "Heap requires BST"],
          "Need dynamic extract-extremum O(log n) as tasks arrive",
          "Dynamic priority ADT.", "medium"),
        q("dsa-heap-scheduling-q5", "Last stone weight simulation uses:",
          ["Queue FIFO", "Max-heap (use reverseOrder PQ in Java) repeatedly smash two largest",
           "BST inorder", "Topo sort"],
          "Max-heap (use reverseOrder PQ in Java) repeatedly smash two largest",
          "Extract two max each round.", "easy"),
        q("dsa-heap-scheduling-q6", "Car fleet / timeline problems often sort then:",
          ["Binary search only", "Use heap or stack to maintain active set by time/distance",
           "Union-Find only", "Dijkstra always"],
          "Use heap or stack to maintain active set by time/distance",
          "Pattern recognition with sorted order.", "medium"),
    ],
    exercises=[
        ex("dsa-heap-scheduling-ex1", "Task scheduler + meeting rooms trace",
           "Implement Task Scheduler (cooldown) with max-heap + queue/waiting counts. "
           "NeetCode 150 Heap: Task Scheduler and Last Stone Weight. "
           "TRANSFER (internal): Reorganize string so no adjacent same char — explain heap + counts greedy.",
           difficulty="advanced", order=0),
    ],
)

_add(
    "dsa-graph-representations",
    hours=1.0,
    objective="Build adjacency-list graph representations in Java before running graph algorithms.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Graph G = (V, E). Adjacency list: Map<Integer, List<Integer>> or List<List<Integer>> for 0..n-1 labels. "
        "Undirected: add edge u-v to both lists. Directed: add v to u's list only. "
        + CPP["map"] + " "
        "Implement adjacency list from scratch before BFS/DFS/Dijkstra — do not jump to algorithms without a representation."
    ),
    mastery=_m("Represent an undirected graph with adjacency lists in Java."),
    resources=[
        bari_primary("dsa-graph-representations", "Graph representation / adjacency list & matrix"),
        mit_dd("dsa-graph-representations", "MIT 6.006 — Breadth-First Search", MIT_L9),
        nccore("dsa-graph-representations", "Design Graph"),
        nc150("dsa-graph-representations", "Graphs"),
        lc_collection("dsa-graph-representations"),
    ],
    questions=[
        q("dsa-graph-representations-q1", "Adjacency list for undirected edge (2,5):",
          ["Add 5 to adj[2] only", "Add 5 to adj[2] and 2 to adj[5]",
           "Use matrix only", "Add to heap"],
          "Add 5 to adj[2] and 2 to adj[5]",
          "Undirected = both directions.", mastery=True),
        q("dsa-graph-representations-q2", "Space for sparse graph with n vertices, m edges (list):",
          ["O(n^2) always", "O(n + m)", "O(m^2)", "O(log n)"],
          "O(n + m)", "Lists store each edge twice if undirected.", "medium"),
        q("dsa-graph-representations-q3", "Adjacency matrix vs list for sparse social graph:",
          ["Matrix always better", "List better — matrix O(n^2) even when m << n^2",
           "Equal always", "List cannot represent sparse"],
          "List better — matrix O(n^2) even when m << n^2",
          "Interview default: list.", "medium"),
        q("dsa-graph-representations-q4", "List<List<Integer>> adj = new ArrayList<>(); for n nodes you:",
          ["Need n*n matrix", "Add n empty ArrayLists then add neighbors to adj.get(u)",
           "Cannot represent directed graphs", "Must use HashSet only"],
          "Add n empty ArrayLists then add neighbors to adj.get(u)",
          "Common Java pattern.", "easy"),
        q("dsa-graph-representations-q5", "Weighted graph in adjacency list:",
          ["Impossible", "Store List of edge pairs (neighbor, weight) or small Edge class",
           "Weights only in matrix", "Use BST only"],
          "Store List of edge pairs (neighbor, weight) or small Edge class",
          "Needed before Dijkstra.", "medium"),
        q("dsa-graph-representations-q6", "C++ vector<vector<int>> adj vs Java List<List<Integer>>:",
          ["Unrelated", "Same adjacency list idea; Java uses reference lists",
           "Java cannot have lists of lists", "C++ cannot do weighted"],
          "Same adjacency list idea; Java uses reference lists",
          "Parallel to C++ knowledge.", "easy"),
    ],
    exercises=[
        ex("dsa-graph-representations-ex1", "Design Graph from scratch",
           "Implement Graph with addUndirectedEdge, addDirectedEdge, neighbors(u). Build from edge list input. "
           "NeetCode Core Skills: Design Graph. "
           "NeetCode 150 Graphs: Clone Graph (adj list + BFS/DFS copy). "
           "TRANSFER (internal): Convert edge list to adj matrix on paper for n=4 — when is matrix acceptable?",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-graph-bfs",
    hours=1.25,
    objective="Traverse a graph with BFS using a queue after building an adjacency list.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "BFS: mark visited, enqueue start, while queue not empty dequeue u, relax neighbors v not visited, enqueue v. "
        "Unweighted shortest path distances from source via BFS levels. "
        "Use ArrayDeque. Choose BFS when you need shortest edge count or level-by-level expansion."
    ),
    mastery=_m("Implement BFS on adjacency list without copying."),
    resources=[
        bari_primary("dsa-graph-bfs", "Breadth-First Search on graphs"),
        mit_dd("dsa-graph-bfs", "MIT 6.006 — Breadth-First Search", MIT_L9),
        nccore("dsa-graph-bfs", "Matrix BFS / DFS"),
        nc150("dsa-graph-bfs", "Graphs"),
        lc_collection("dsa-graph-bfs"),
    ],
    questions=[
        q("dsa-graph-bfs-q1", "BFS on unweighted graph from s finds:",
          ["Any path", "Shortest path in number of edges from s to each reachable node",
           "Minimum weight path always", "Topological order"],
          "Shortest path in number of edges from s to each reachable node",
          "First visit is shortest in unweighted graph.", mastery=True),
        q("dsa-graph-bfs-q2",
          "boolean[] seen; Queue<Integer> q; q.add(s); seen[s]=true; while(!q.isEmpty()){ int u=q.remove(); "
          "for(int v: adj.get(u)) if(!seen[v]){ seen[v]=true; q.add(v);} } — v marked when:",
          ["Dequeued", "Enqueued (discovered)", "After DFS returns", "Never until end"],
          "Enqueued (discovered)", "Mark on discovery to avoid duplicate enqueue.", "medium"),
        q("dsa-graph-bfs-q3", "BFS vs DFS for shortest path in unweighted graph:",
          ["DFS always shortest", "BFS; DFS may find longer path first",
           "Neither works", "Dijkstra required always"],
          "BFS; DFS may find longer path first",
          "Layer-by-layer guarantees distance.", "medium"),
        q("dsa-graph-bfs-q4", "BFS time on graph with n vertices, m edges (adj list):",
          ["O(n^2)", "O(n + m)", "O(n log n)", "O(m^2)"],
          "O(n + m)", "Each vertex/edge constant work.", "easy"),
        q("dsa-graph-bfs-q5", "Multi-source BFS (rotting oranges):",
          ["Impossible", "Enqueue all sources initially with distance 0",
           "Requires Dijkstra", "Only on trees"],
          "Enqueue all sources initially with distance 0",
          "Super-source trick.", "medium"),
        q("dsa-graph-bfs-q6", "Grid BFS (Matrix BFS) differs from graph BFS:",
          ["Completely different algorithm", "Same BFS; neighbors are 4/8 grid cells; build implicit graph",
           "Must use DFS on grids", "Grids require Union-Find only"],
          "Same BFS; neighbors are 4/8 grid cells; build implicit graph",
          "Core Skills Matrix BFS/DFS is same pattern.", "medium"),
        q("dsa-graph-bfs-q7", "When to prefer BFS over DFS:",
          ["Need any path deep fast", "Need minimum edges / level order / shortest unweighted distance",
           "Detect cycle in directed graph only", "Always DFS"],
          "Need minimum edges / level order / shortest unweighted distance",
          "Selection rule for interviews.", "medium"),
    ],
    exercises=[
        ex("dsa-graph-bfs-ex1", "BFS distances + grid",
           "Implement bfsDist(adj, start) returning int[] dist (-1 unreachable). "
           "NeetCode Core Skills: Matrix BFS/DFS on a grid '1'/'0' island count or multi-source rot. "
           "NeetCode 150 Graphs: Number of Islands and Rotting Oranges. "
           "TRANSFER (internal): Word ladder as BFS on implicit graph — state what nodes/edges are.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-graph-dfs",
    hours=1.25,
    objective="Traverse a graph with DFS recursively or with an explicit stack.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "DFS: mark visited, visit u, recurse/stack push unvisited neighbors. "
        "Explores deeply before backtracking. "
        "Choose DFS for exhaustive search, path existence, cycle detection structure, or when stack depth acceptable. "
        "Not for unweighted shortest path."
    ),
    mastery=_m("Implement DFS on adjacency list."),
    resources=[
        bari_primary("dsa-graph-dfs", "Depth-First Search on graphs"),
        mit_dd("dsa-graph-dfs", "MIT 6.006 — Depth-First Search", MIT_L10),
        nccore("dsa-graph-dfs", "Matrix BFS / DFS"),
        nc150("dsa-graph-dfs", "Graphs"),
        lc_collection("dsa-graph-dfs"),
    ],
    questions=[
        q("dsa-graph-dfs-q1", "Recursive DFS base case / guard:",
          ["Never stop", "If u visited return; else mark visited then recurse neighbors",
           "Sort adjacency first always", "Must use queue"],
          "If u visited return; else mark visited then recurse neighbors",
          "Prevent infinite loops.", mastery=True),
        q("dsa-graph-dfs-q2", "Iterative DFS uses:",
          ["Queue FIFO", "Stack LIFO (ArrayDeque as stack push/pop)",
           "PriorityQueue only", "Heap sort"],
          "Stack LIFO (ArrayDeque as stack push/pop)",
          "Mirror recursive call stack.", "easy"),
        q("dsa-graph-dfs-q3", "DFS on disconnected graph requires:",
          ["Single call from node 0 only", "Loop all vertices; start DFS from each unvisited",
           "BFS cannot help", "Adjacency matrix only"],
          "Loop all vertices; start DFS from each unvisited",
          "Outer loop for components.", "medium"),
        q("dsa-graph-dfs-q4", "Time complexity DFS adjacency list:",
          ["O(n + m)", "O(n^2) always", "O(log n)", "O(n m)"],
          "O(n + m)", "Same as BFS.", "easy"),
        q("dsa-graph-dfs-q5", "When prefer DFS over BFS:",
          ["Shortest unweighted path", "Explore all paths / backtracking / some cycle/toposort setups",
           "Level-by-level", "Always BFS"],
          "Explore all paths / backtracking / some cycle/toposort setups",
          "Selection rule.", "medium"),
        q("dsa-graph-dfs-q6", "DFS recursion depth on chain graph with n nodes:",
          ["O(1)", "O(n) stack frames — may need iterative DFS for large n",
           "O(log n)", "O(n^2)"],
          "O(n) stack frames — may need iterative DFS for large n",
          "Stack overflow risk in Java on deep graphs.", "medium"),
        q("dsa-graph-dfs-q7", "Clone Graph via DFS:",
          ["Cannot clone", "Map old node -> new node while DFS copying neighbors",
           "Requires sorting", "Only BFS allowed"],
          "Map old node -> new node while DFS copying neighbors",
          "HashMap tracks cloned nodes.", "medium"),
    ],
    exercises=[
        ex("dsa-graph-dfs-ex1", "DFS + clone",
           "Implement dfsVisit and iterative dfsStack. "
           "NeetCode 150 Graphs: Clone Graph and Pacific Atlantic Water Flow (DFS from borders). "
           "TRANSFER (internal): Detect if path exists with target length k — DFS with depth limit.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-connected-components",
    hours=1.0,
    objective="Count or label connected components in undirected graphs with BFS/DFS.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Component: maximal set of nodes mutually reachable. "
        "Algorithm: count++, run BFS/DFS from each unvisited node. "
        "Union-Find also counts components online — see union-find topic."
    ),
    mastery=_m("Explain BFS/DFS from unvisited nodes to cover all components."),
    resources=[
        bari_primary("dsa-connected-components", "Connected components"),
        mit_dd("dsa-connected-components", "MIT 6.006 — Depth-First Search", MIT_L10),
        nc150("dsa-connected-components", "Graphs"),
        lc_collection("dsa-connected-components"),
    ],
    questions=[
        q("dsa-connected-components-q1", "Undirected graph with 3 isolated pairs (6 nodes, 3 edges total as 3 edges 0-1,2-3,4-5). Components:",
          ["1", "3", "6", "2"],
          "3", "Each edge pair is its own component.", mastery=True),
        q("dsa-connected-components-q2", "countComponents algorithm outline:",
          ["Sort edges", "For each unvisited v, run BFS/DFS marking all reachable; increment count",
           "Dijkstra from all nodes", "Heapify"],
          "For each unvisited v, run BFS/DFS marking all reachable; increment count",
          "Standard O(n+m).", "easy"),
        q("dsa-connected-components-q3", "Number of Provinces (cities) is:",
          ["Shortest path", "Connected components on implicit graph from adjacency matrix",
           "Topo sort", "BST validation"],
          "Connected components on implicit graph from adjacency matrix",
          "NeetCode graph CC pattern.", "medium"),
        q("dsa-connected-components-q4", "Union-Find component count after unioning all edges:",
          ["Always n", "n minus successful merges that united different sets",
           "m always", "Requires Dijkstra"],
          "n minus successful merges that united different sets",
          "Alternative to BFS/DFS count.", "medium"),
        q("dsa-connected-components-q5", "Labeling each node with component id:",
          ["Impossible", "During each BFS/DFS assign same id to all visited in that run",
           "Requires sorted edges", "Only with matrix"],
          "During each BFS/DFS assign same id to all visited in that run",
          "Same traversal, extra array.", "easy"),
        q("dsa-connected-components-q6", "Directed graph 'strongly connected components':",
          ["Same as undirected CC at V1", "Different concept (Kosaraju/Tarjan) — V1 names only; undirected CC is this topic",
           "Always one component", "Found by BFS only"],
          "Different concept (Kosaraju/Tarjan) — V1 names only; undirected CC is this topic",
          "Do not confuse with undirected CC.", "medium"),
    ],
    exercises=[
        ex("dsa-connected-components-ex1", "Count components",
           "Implement countComponents(adj). Trace on graph with 2 components. "
           "NeetCode 150 Graphs: Number of Provinces and Redundant Connection (Union-Find preview). "
           "TRANSFER (internal): Largest component size — modify traversal to track count per DFS.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-graph-cycle",
    hours=1.25,
    objective="Detect cycles in undirected and directed graphs at V1 depth.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Undirected: DFS/BFS; if edge to visited node that is not parent → cycle. "
        "Directed: three-color (white/gray/black) or recursion stack — back edge to gray node = cycle. "
        "Cycle detection prerequisite for topological sort."
    ),
    mastery=_m("Contrast parent-marked undirected cycle vs color-marked directed cycle."),
    resources=[
        bari_primary("dsa-graph-cycle", "Cycle detection in graphs"),
        mit_dd("dsa-graph-cycle", "MIT 6.006 — Depth-First Search", MIT_L10),
        nc150("dsa-graph-cycle", "Graphs"),
        lc_collection("dsa-graph-cycle"),
    ],
    questions=[
        q("dsa-graph-cycle-q1", "Undirected DFS at u sees neighbor v already visited and v is not parent of u:",
          ["Always a tree edge", "Indicates a cycle", "Impossible", "Requires weights"],
          "Indicates a cycle", "Non-tree back edge.", mastery=True),
        q("dsa-graph-cycle-q2", "Directed graph DFS: node in current recursion stack (GRAY) seen again:",
          ["No cycle", "Back edge → cycle exists", "Forward edge only", "Cross edge never cycle"],
          "Back edge → cycle exists", "Gray = on active path.", "medium"),
        q("dsa-graph-cycle-q3", "Course Schedule (can finish all) asks:",
          ["Shortest path", "Whether directed graph has cycle", "Bipartite check", "MST"],
          "Whether directed graph has cycle",
          "Cycle = deadlock in prerequisites.", "medium"),
        q("dsa-graph-cycle-q4", "Undirected graph with n nodes and n edges (connected):",
          ["Must be tree", "Must have at least one cycle", "Impossible", "Must be bipartite"],
          "Must have at least one cycle",
          "Tree has n-1 edges; extra edge creates cycle.", "medium"),
        q("dsa-graph-cycle-q5", "BFS cycle detection undirected:",
          ["Impossible", "Track parent; if visited neighbor not parent → cycle",
           "Only works directed", "Requires Dijkstra"],
          "Track parent; if visited neighbor not parent → cycle",
          "BFS variant exists.", "medium"),
        q("dsa-graph-cycle-q6", "Self-loop edge (u,u) in directed graph:",
          ["Ignored", "Is a cycle", "Only undirected cycle", "Requires negative weight"],
          "Is a cycle", "Length-1 cycle.", "easy"),
    ],
    exercises=[
        ex("dsa-graph-cycle-ex1", "Directed + undirected cycle checks",
           "Implement hasCycleUndirected(adj) and hasCycleDirected(adj) with colors. "
           "NeetCode 150 Graphs: Course Schedule (cycle detect). "
           "TRANSFER (internal): Detect cycle in linked list — relate to Floyd vs visited set.",
           difficulty="advanced", order=0),
    ],
)

_add(
    "dsa-bipartite",
    hours=1.0,
    objective="Check bipartiteness with two-color BFS or DFS.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Bipartite: vertices partition into two sets with every edge crossing sets. "
        "Equivalent to graph 2-colorable. "
        "BFS/DFS: assign colors 0/1; if neighbor has same color → not bipartite. "
        "Handle disconnected components separately."
    ),
    mastery=_m("Two-color a small graph or show it is not bipartite."),
    resources=[
        bari_primary("dsa-bipartite", "Bipartite graphs / graph coloring"),
        mit_dd("dsa-bipartite", "MIT 6.006 — Depth-First Search", MIT_L10),
        nc150("dsa-bipartite", "Graphs"),
        lc_collection("dsa-bipartite"),
    ],
    questions=[
        q("dsa-bipartite-q1", "Odd-length cycle in graph implies:",
          ["Must be bipartite", "Not bipartite", "Always bipartite if connected", "Requires weights"],
          "Not bipartite", "Odd cycle breaks 2-coloring.", mastery=True),
        q("dsa-bipartite-q2", "BFS coloring: start node color 0, neighbor gets:",
          ["Color 0 always", "Opposite color 1; conflict if already colored same",
           "Random color", "No coloring needed"],
          "Opposite color 1; conflict if already colored same",
          "Alternate colors along edges.", "easy"),
        q("dsa-bipartite-q3", "Tree (no cycles) with at least one edge:",
          ["Never bipartite", "Always bipartite", "Bipartite only if complete", "Requires heap"],
          "Always bipartite", "Trees are 2-colorable.", "medium"),
        q("dsa-bipartite-q4", "Graph with isolated single node:",
          ["Not bipartite", "Bipartite (vacuously one partition)", "Needs Dijkstra", "Needs three colors"],
          "Bipartite (vacuously one partition)", "No edges to violate.", "easy"),
        q("dsa-bipartite-q5", "Is Graph Bipartite? on NeetCode uses:",
          ["Dijkstra", "BFS/DFS coloring", "Topo sort", "Kruskal"],
          "BFS/DFS coloring", "Standard approach.", "easy"),
        q("dsa-bipartite-q6", "Complete graph K3 (triangle):",
          ["Bipartite", "Not bipartite (odd cycle length 3)", "Bipartite with 3 sets", "Unrelated"],
          "Not bipartite (odd cycle length 3)",
          "3-cycle odd.", "medium"),
    ],
    exercises=[
        ex("dsa-bipartite-ex1", "Two-color BFS",
           "Implement isBipartite(adj) handling disconnected graph. Trace on square vs triangle. "
           "NeetCode 150 Graphs: Is Graph Bipartite? "
           "TRANSFER (internal): Matching students to pairs — reduce to bipartite check in words.",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-topological-sort",
    hours=1.5,
    objective="Produce topological order of a DAG with Kahn's algorithm and DFS finishing order; detect cycles.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Topo sort exists only for DAG. "
        "Kahn: start with indegree 0 queue, remove u, decrement neighbor indegrees, enqueue new zeros. "
        "If processed count < n → cycle. "
        "DFS: postorder push finished nodes to stack/reverse list. "
        "Cycle forbids topo sort."
    ),
    mastery=_m("Explain why cycles forbid topo sort and outline Kahn + DFS approaches."),
    resources=[
        bari_primary("dsa-topological-sort", "Topological sorting"),
        mit_dd("dsa-topological-sort", "MIT 6.006 — Depth-First Search", MIT_L10),
        nccore("dsa-topological-sort", "Topological Sort"),
        nc150("dsa-topological-sort", "Graphs"),
        lc_collection("dsa-topological-sort"),
    ],
    questions=[
        q("dsa-topological-sort-q1", "Topological order of DAG means for every edge u→v:",
          ["u comes after v", "u comes before v in ordering", "u and v equal", "No constraint"],
          "u comes before v in ordering", "Edge direction respects order.", mastery=True),
        q("dsa-topological-sort-q2", "Graph with cycle:",
          ["Has unique topo sort", "Has no valid topological sort", "Has two topo sorts always", "Kahn still succeeds"],
          "Has no valid topological sort",
          "Cycle = circular dependency.", "easy"),
        q("dsa-topological-sort-q3", "Kahn algorithm uses:",
          ["Max-heap only", "Queue of indegree-zero nodes and indegree array",
           "Union-Find only", "BST inorder"],
          "Queue of indegree-zero nodes and indegree array",
          "Peel sources.", "medium"),
        q("dsa-topological-sort-q4", "Kahn finishes with processed < n nodes:",
          ["Success", "Cycle detected", "Graph disconnected only", "Needs Dijkstra"],
          "Cycle detected", "Nodes in cycle never reach indegree 0.", "medium"),
        q("dsa-topological-sort-q5", "DFS topo sort collects nodes:",
          ["On entry to DFS", "After finishing all descendants (postorder), reverse if needed",
           "In BFS order", "Sorted by weight"],
          "After finishing all descendants (postorder), reverse if needed",
          "Finishing time order.", "medium"),
        q("dsa-topological-sort-q6", "Course Schedule II returns:",
          ["Only boolean", "Actual topo ordering of courses if possible",
           "Shortest path", "MST"],
          "Actual topo ordering of courses if possible",
          "NeetCode II variant.", "easy"),
        q("dsa-topological-sort-q7", "Multiple valid topo orders for same DAG:",
          ["Impossible", "Possible — Kahn picks among indegree-zero choices",
           "Exactly one always", "Only DFS gives multiple"],
          "Possible — Kahn picks among indegree-zero choices",
          "Non-unique common.", "medium"),
    ],
    exercises=[
        ex("dsa-topological-sort-ex1", "Kahn + DFS topo",
           "Implement topoSortKahn and topoSortDFS. Verify both match on sample DAG. Show cycle failure. "
           "NeetCode Core Skills: Topological Sort. "
           "NeetCode 150 Graphs: Course Schedule and Course Schedule II. "
           "TRANSFER (internal): Alien dictionary — explain as topo sort on letter precedence graph.",
           difficulty="advanced", order=0),
    ],
)

_add(
    "dsa-union-find",
    hours=1.25,
    objective="Implement disjoint set union with path compression and union by rank.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "DSU maintains parent[] array. find(x) returns representative; path compression flattens parent pointers during find. "
        "union(a,b) attaches rank-smaller root under larger; union by rank keeps trees shallow. "
        "Near O(α(n)) amortized per operation. "
        "Use for dynamic connectivity, Kruskal preview, redundant connection."
    ),
    mastery=_m("Explain find and union with path compression and union by rank."),
    resources=[
        bari_primary("dsa-union-find", "Disjoint Set / Union-Find"),
        mit_dd("dsa-union-find", "MIT 6.006 — Depth-First Search", MIT_L10),
        nccore("dsa-union-find", "Design Disjoint Set"),
        nc150("dsa-union-find", "Graphs"),
        lc_collection("dsa-union-find"),
    ],
    questions=[
        q("dsa-union-find-q1", "Path compression in find(x):",
          ["Sorts the array", "Make nodes on path point directly to root during find",
           "Deletes x", "Only for BST"],
          "Make nodes on path point directly to root during find",
          "Flattens tree.", mastery=True),
        q("dsa-union-find-q2", "Union by rank attaches:",
          ["Larger rank root under smaller", "Smaller rank root under larger rank root (tie increment rank)",
           "Random root", "Always node 0 as root"],
          "Smaller rank root under larger rank root (tie increment rank)",
          "Keeps depth small.", "medium"),
        q("dsa-union-find-q3", "connected(a,b) before union:",
          ["Always false", "find(a) == find(b)", "a == b always", "Requires BFS each time O(n)"],
          "find(a) == find(b)", "Same set representative.", "easy"),
        q("dsa-union-find-q4", "Kruskal MST uses Union-Find to:",
          ["Sort nodes", "Reject edges that would create cycle in growing forest",
           "Run Dijkstra", "Topo sort"],
          "Reject edges that would create cycle in growing forest",
          "If find(u)==find(v) skip edge.", "medium"),
        q("dsa-union-find-q5", "Without path compression or rank, m unions can be:",
          ["O(1) always", "O(n) per find worst case — skewed chain",
           "O(log log n) always", "Impossible"],
          "O(n) per find worst case — skewed chain",
          "Why optimizations matter.", "medium"),
        q("dsa-union-find-q6", "Redundant Connection (first extra edge forming cycle):",
          ["Dijkstra", "Process edges with Union-Find; first union that connects already-connected nodes",
           "Topo sort", "Heap only"],
          "Process edges with Union-Find; first union that connects already-connected nodes",
          "Classic DSU application.", "medium"),
    ],
    exercises=[
        ex("dsa-union-find-ex1", "Design DSU from scratch",
           "Implement DSU with find (path compression), union (by rank), connected. Stress-test 10^5 ops. "
           "NeetCode Core Skills: Design Disjoint Set. "
           "NeetCode 150 Graphs: Redundant Connection and Min Cost to Connect All Points (MST preview). "
           "TRANSFER (internal): Number of islands with Union-Find on grid cells — outline union neighbors.",
           difficulty="advanced", order=0),
    ],
)

_add(
    "dsa-unweighted-shortest",
    hours=1.0,
    objective="Compute unweighted shortest paths with BFS and contrast with weighted Dijkstra.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Unweighted (or unit weight) shortest path = BFS from source recording dist[v] = dist[u]+1. "
        "Do not use Dijkstra when all edges cost 1 — BFS is simpler O(n+m). "
        "Weighted graphs need Dijkstra (non-negative) or Bellman-Ford (negative edges allowed)."
    ),
    mastery=_m("Contrast BFS distance vs Dijkstra on weighted graphs."),
    resources=[
        bari_primary("dsa-unweighted-shortest", "Shortest path — unweighted BFS"),
        mit_dd("dsa-unweighted-shortest", "MIT 6.006 — Weighted Shortest Paths", MIT_L11),
        nc150("dsa-unweighted-shortest", "Graphs"),
        lc_collection("dsa-unweighted-shortest"),
    ],
    questions=[
        q("dsa-unweighted-shortest-q1", "All edges weight 1. Shortest path from s best found by:",
          ["Dijkstra only", "BFS layering", "Bellman-Ford only", "BST search"],
          "BFS layering", "BFS is optimal for unit weights.", mastery=True),
        q("dsa-unweighted-shortest-q2", "BFS dist array initialized:",
          ["All 0", "INF/unreachable except dist[s]=0", "Random", "Only dist[0]"],
          "INF/unreachable except dist[s]=0", "Update on first discovery.", "easy"),
        q("dsa-unweighted-shortest-q3", "Weighted graph with varying positive weights — unweighted BFS:",
          ["Always correct", "May return non-minimum weight path", "Same as Dijkstra", "Handles negatives"],
          "May return non-minimum weight path",
          "Edge count ≠ weight sum.", "medium"),
        q("dsa-unweighted-shortest-q4", "Multi-source unweighted shortest to any rotten orange:",
          ["Run Dijkstra from each source", "Multi-source BFS enqueue all sources at distance 0",
           "Union-Find", "Topo sort"],
          "Multi-source BFS enqueue all sources at distance 0",
          "Super-source BFS.", "medium"),
        q("dsa-unweighted-shortest-q5", "Path reconstruction after BFS:",
          ["Impossible", "parent[v] recorded when setting dist[v]; walk parent from target",
           "Requires heap", "Only for trees"],
          "parent[v] recorded when setting dist[v]; walk parent from target",
          "Standard backtrack.", "medium"),
        q("dsa-unweighted-shortest-q6", "Time for single-source unweighted shortest paths:",
          ["O(n + m)", "O(n log n) required", "O(n^2) always", "O(m^2)"],
          "O(n + m)", "One BFS.", "easy"),
    ],
    exercises=[
        ex("dsa-unweighted-shortest-ex1", "BFS dist + path",
           "Implement shortestPath(adj, s, t) returning path list via parent[]. "
           "NeetCode 150 Graphs: Rotting Oranges (multi-source BFS time). "
           "TRANSFER (internal): Shortest path in binary matrix with 0/1 cells — when is it still BFS?",
           difficulty="intermediate", order=0),
    ],
)

_add(
    "dsa-dijkstra",
    hours=2.0,
    objective="Run Dijkstra's algorithm for non-negative weighted shortest paths with a min-heap.",
    explanation=(
        RELEARN + " " + JAVA_PRIMARY + " "
        "Dijkstra: maintain dist[s]=0, others INF; min-heap on (distance, node); pop smallest, relax edges if dist[u]+w < dist[v]. "
        "Requires non-negative edge weights — negative edges invalidate the greedy pop invariant. "
        + CPP["heap"] + " "
        "Use PriorityQueue as min-heap. "
        "Bellman-Ford handles negative edges (MIT L12 deep dive on why Dijkstra fails — not V1 implementation)."
    ),
    mastery=_m("Trace Dijkstra on a tiny weighted graph and state when it fails."),
    resources=[
        bari_primary("dsa-dijkstra", "Dijkstra's shortest path algorithm"),
        mit_dd("dsa-dijkstra", "MIT 6.006 — Dijkstra", MIT_L13),
        mit_dd("dsa-dijkstra", "MIT 6.006 — Bellman-Ford (why not Dijkstra with negative edges)", MIT_L12),
        mit_dd("dsa-dijkstra", "MIT 6.006 — Weighted Shortest Paths", MIT_L11),
        nccore("dsa-dijkstra", "Dijkstra"),
        nc150("dsa-dijkstra", "Graphs"),
        lc_collection("dsa-dijkstra"),
    ],
    questions=[
        q("dsa-dijkstra-q1", "Edge with negative weight in graph:",
          ["Dijkstra still optimal always", "Dijkstra may be wrong — use Bellman-Ford or reweighting",
           "Ignore the edge", "Switch to BFS only"],
          "Dijkstra may be wrong — use Bellman-Ford or reweighting",
          "Non-negative requirement is strict.", mastery=True),
        q("dsa-dijkstra-q2", "PriorityQueue stores (dist, node). First pop from source with dist 0:",
          ["Always wrong node", "Processes currently smallest tentative distance node",
           "Sorts all nodes once", "Is BFS"],
          "Processes currently smallest tentative distance node",
          "Greedy on non-negative weights.", "medium"),
        q("dsa-dijkstra-q3", "Relax edge u→v weight w when dist[u]=5 and dist[v]=10:",
          ["Keep dist[v]", "Update dist[v]=8 if 5+w=8 improves", "Reset all dist", "Run union-find"],
          "Update dist[v]=8 if 5+w=8 improves",
          "Relaxation step.", "easy"),
        q("dsa-dijkstra-q4", "Dijkstra with binary heap on n nodes, m edges:",
          ["O(n + m)", "O((n + m) log n) typical with lazy decrease-key via re-insert",
           "O(n^2) always wrong", "O(m) only"],
          "O((n + m) log n) typical with lazy decrease-key via re-insert",
          "Log factor from heap.", "medium"),
        q("dsa-dijkstra-q5", "Counterexample: nodes A--(-2)-->B--(3)-->C and A--(1)-->C. Dijkstra from A may pick:",
          ["Always AC weight 1", "May finalize A→C before considering A→B→C if negative breaks greedy",
           "BFS sufficient", "No path"],
          "May finalize A→C before considering A→B→C if negative breaks greedy",
          "Negative edge breaks greedy pop.", "hard"),
        q("dsa-dijkstra-q6", "Java PriorityQueue in Dijkstra should be:",
          ["Max-heap default without thought", "Min-heap (default PQ or Comparator.comparingInt on dist)",
           "Stack", "TreeMap only"],
          "Min-heap (default PQ or Comparator.comparingInt on dist)",
          "Extract smallest tentative distance.", "easy"),
        q("dsa-dijkstra-q7", "Network Delay Time (signal from node k to all):",
          ["Union-Find", "Dijkstra from k tracking max dist reached",
           "Topo sort only", "BST inorder"],
          "Dijkstra from k tracking max dist reached",
          "Single-source to all nodes.", "medium"),
        q("dsa-dijkstra-q8", "When BFS is enough instead of Dijkstra:",
          ["Always never", "All edge weights equal (unweighted / unit weight)",
           "Graph has negative edges", "Need MST"],
          "All edge weights equal (unweighted / unit weight)",
          "Use simpler BFS.", "medium"),
    ],
    exercises=[
        ex("dsa-dijkstra-ex1", "Implement Dijkstra from scratch",
           "Build weighted adj list. Implement dijkstra(adj, src) returning dist[]. "
           "Trace on 4-node graph on paper including heap order. "
           "NeetCode Core Skills: Dijkstra. "
           "NeetCode 150 Graphs: Network Delay Time. "
           "Explain on paper one graph where negative edge breaks Dijkstra (MIT L12 idea). "
           "TRANSFER (internal): Cheapest flights within K stops — why plain Dijkstra is insufficient (mention Bellman-Ford/layered BFS at high level).",
           difficulty="advanced", order=0),
    ],
)
