"""Dev environment and problem-solving topics."""

from __future__ import annotations

from _d0_helpers import CS50_N0, CS50_W0, CS50_W1, MIT_CLI, MIT_DBG, MIT_DEV, MIT_QUALITY, MIT_SHIP, WSL, ex, q, r
from _d0_part5 import CONTENT, _add

VS_DOCS = "https://code.visualstudio.com/docs"
VS_UI = "https://code.visualstudio.com/docs/getstarted/userinterface"
VS_DEBUG = "https://code.visualstudio.com/docs/editor/debugging"
VS_BASICS = "https://code.visualstudio.com/docs/editor/codebasics"
VS_SETTINGS = "https://code.visualstudio.com/docs/configure/settings"

_add(
    "cf-ide",
    hours=0.75,
    objective="Use an IDE to open, edit, and run a small project.",
    explanation=(
        "An IDE combines editor, run/debug, and project tools. VS Code is what you use day to day, but the skill is using one well. "
        "PRIMARY structured course for this module is TBD — do not treat a random YouTube playlist as a substitute. "
        "MIT 2026 development-environment lecture is Vim-heavy; it still defines what a development environment is."
    ),
    mastery=["Open a project and run it from the editor you actually use.", "Score >= 80%."],
    resources=[
        r("cf-ide-reference", "Visual Studio Code documentation", VS_DOCS, "VS Code", "REFERENCE", "documentation", 0,
          "Official VS Code docs. PRIMARY course for this module is unresolved."),
        r("cf-ide-deep", "MIT Missing Semester 2026 — Development Environment and Tools", MIT_DEV, "MIT Missing Semester 2026", "DEEP_DIVE", "article", 1,
          "Defines IDE vs terminal workflows. Vim-centric; not a required Vim course."),
    ],
    questions=[
        q("cf-ide-q1", "An IDE is primarily:",
          ["The kernel", "An application that combines editing with run/debug/project tools", "A Git remote", "An apt mirror"],
          "An application that combines editing with run/debug/project tools", "Definition.", "easy", True),
        q("cf-ide-q2", "This curriculum's conceptual IDE topic:",
          ["Requires VS Code exclusively forever", "Uses VS Code for exercises because that is your editor, without making VS Code a conceptual dependency",
           "Forbids VS Code", "Requires Vim from MIT as the only editor"],
          "Uses VS Code for exercises because that is your editor, without making VS Code a conceptual dependency", "Policy.", "medium", True),
        q("cf-ide-q3", "The PRIMARY structured course for Development Environment is:",
          ["A random YouTube playlist we invented", "Still TBD; official VS Code/MIT pages are references", "CS50 Scratch only", "GitHub Hello World only"],
          "Still TBD; official VS Code/MIT pages are references", "Unresolved.", "easy"),
        q("cf-ide-q4", "A reason to use an IDE over Notepad:",
          ["Notepad cannot store bytes", "Navigation, diagnostics, and debugger integration reduce errors", "IDEs replace algorithms", "IDEs replace Git"],
          "Navigation, diagnostics, and debugger integration reduce errors", "Why tools.", "easy"),
    ],
    exercises=[
        ex("cf-ide-ex1", "Open and run",
           "In VS Code (or another IDE if you insist): open a folder, open a file, run a one-file program you already know (even a tiny script). "
           f"Skim {VS_UI}. Write the Run command you used. PRIMARY course remains TBD."),
    ],
)

_add(
    "cf-dev-compiler",
    hours=0.5,
    objective="Invoke a compiler from the environment you will use for Java.",
    explanation="Apply cf-compiler in a real toolchain. You may not have javac yet; recording versions of gcc/clang/python still counts. PRIMARY course TBD.",
    mastery=["Explain what the compile step produces.", "Inspect compiler/runtime versions.", "Score >= 80%."],
    resources=[
        r("cf-dev-compiler-reference", "CS50x 2026 Week 1 (compiler workflow)", CS50_W1, "CS50x", "REFERENCE", "interactive_tutorial", 0,
          "make/clang as a concrete compile loop. Not a Java course."),
    ],
    questions=[
        q("cf-dev-compiler-q1", "Checking `javac -version` or `clang --version` tells you:",
          ["Git remotes", "Which compiler/runtime is on PATH", "SSD model only", "GitHub stars"],
          "Which compiler/runtime is on PATH", "Toolchain awareness.", "easy", True),
        q("cf-dev-compiler-q2", "If the IDE run button works but the terminal says command not found:",
          ["The CPU is missing", "The IDE and your shell may be using different PATHs", "Git is broken", "Hex failed"],
          "The IDE and your shell may be using different PATHs", "Environment mismatch.", "medium", True),
        q("cf-dev-compiler-q3", "Compile step output is typically:",
          ["Only a PNG", "An executable or bytecode artifacts", "A pull request", "PATH itself"],
          "An executable or bytecode artifacts", "Same as Domain 0 compiler topic.", "easy"),
        q("cf-dev-compiler-q4", "PRIMARY course for this module:",
          ["Invented Udemy clone", "Still TBD", "Must be Vim", "Must be Scratch"],
          "Still TBD", "Unresolved.", "easy"),
    ],
    exercises=[
        ex("cf-dev-compiler-ex1", "Version inspection",
           f"{WSL} Run whatever exists: `clang --version`, `gcc --version`, `python3 --version`, later `javac -version`. Record outputs. "
           "State which command would compile a file in that language."),
    ],
)

_add(
    "cf-debugger",
    hours=1.25,
    objective="Set a breakpoint and inspect a variable.",
    explanation="Stepping beats printf-only debugging. VS Code debugger docs are official. MIT debugging lecture is Unix/gdb-oriented and useful as extra depth.",
    mastery=["Use a debugger on a trivial program.", "Inspect variables and the call stack.", "Score >= 80%."],
    resources=[
        r("cf-debugger-reference", "VS Code — Debug code", VS_DEBUG, "VS Code", "REFERENCE", "documentation", 0,
          "Breakpoints, step, variables, call stack. PRIMARY course TBD."),
        r("cf-debugger-deep", "MIT Missing Semester 2026 — Debugging and Profiling", MIT_DBG, "MIT Missing Semester 2026", "DEEP_DIVE", "article", 1,
          "Print vs debugger vs profilers. Optional depth; not required to finish every profiler exercise."),
    ],
    questions=[
        q("cf-debugger-q1", "A breakpoint:",
          ["Deletes the line", "Pauses execution at a line so you can inspect state", "Pushes Git", "Formats disk"],
          "Pauses execution at a line so you can inspect state", "VS Code docs.", "easy", True),
        q("cf-debugger-q2", "Step over vs step into:",
          ["Identical", "Over executes a call as one step; into follows the callee", "Over formats code", "Into commits"],
          "Over executes a call as one step; into follows the callee", "Toolbar actions.", "medium", True),
        q("cf-debugger-q3", "The call stack shows:",
          ["apt packages", "The chain of active function calls", "Git remotes", "RGB only"],
          "The chain of active function calls", "Where you are.", "easy", True),
        q("cf-debugger-q4", "printf debugging vs a debugger:",
          ["printf is the only professional method", "A debugger inspects live state without sprinkling permanent logs (both have uses)",
           "Debuggers replace algorithms", "Debuggers forbid WSL"],
          "A debugger inspects live state without sprinkling permanent logs (both have uses)", "MIT lecture.", "medium"),
    ],
    exercises=[
        ex("cf-debugger-ex1", "Breakpoint lab",
           f"In VS Code: write or open a tiny program with a function call, set a breakpoint, F5, inspect a variable and the call stack. "
           f"Follow {VS_DEBUG}. Language can be JS/Python/C—whatever your debugger extension supports. {WSL} if you debug a Linux binary."),
    ],
)

_add(
    "cf-formatter",
    hours=0.5,
    objective="Apply automatic formatting.",
    explanation="Formatters apply a consistent style. MIT Code Quality covers formatters. VS Code can format the current file.",
    mastery=["Explain why formatters exist.", "Configure or run a formatter once.", "Score >= 80%."],
    resources=[
        r("cf-formatter-reference", "MIT Missing Semester 2026 — Code Quality", MIT_QUALITY, "MIT Missing Semester 2026", "REFERENCE", "article", 0,
          "Formatters, linters, CI. PRIMARY course TBD."),
    ],
    questions=[
        q("cf-formatter-q1", "A formatter exists to:",
          ["Change program meaning always", "Apply consistent style so reviews are not about spaces", "Replace tests", "Compile kernels"],
          "Apply consistent style so reviews are not about spaces", "MIT code quality.", "easy", True),
        q("cf-formatter-q2", "Formatters vs linters:",
          ["Identical", "Formatters rewrite layout; linters warn about likely bugs/style beyond whitespace",
           "Linters only run on GitHub", "Formatters delete RAM"],
          "Formatters rewrite layout; linters warn about likely bugs/style beyond whitespace", "Split topics.", "medium", True),
        q("cf-formatter-q3", "Running format on save is useful because:",
          ["It replaces Git", "Style stays consistent without a debate on every save", "It disables the debugger", "It is required by the kernel"],
          "Style stays consistent without a debate on every save", "Workflow.", "easy"),
        q("cf-formatter-q4", "If format changes thousands of lines in an old file:",
          ["Always commit mixed with a bugfix", "Prefer a dedicated format commit so reviews stay readable", "Force-push main", "rm -rf .git"],
          "Prefer a dedicated format commit so reviews stay readable", "Hygiene.", "medium"),
    ],
    exercises=[
        ex("cf-formatter-ex1", "Format a file",
           f"In VS Code, Format Document on a messy file (you may paste uneven indentation). Note the command/setting. Skim {MIT_QUALITY} formatter paragraphs."),
    ],
)

_add(
    "cf-linter",
    hours=0.5,
    objective="Run a linter and interpret one warning.",
    explanation="Linters are static hints. MIT Code Quality. Not the same as a compiler error.",
    mastery=["Distinguish a linter finding from a compiler error.", "Score >= 80%."],
    resources=[
        r("cf-linter-reference", "MIT Missing Semester 2026 — Code Quality", MIT_QUALITY, "MIT Missing Semester 2026", "REFERENCE", "article", 0,
          "Linters and CI. PRIMARY TBD."),
    ],
    questions=[
        q("cf-linter-q1", "A linter typically runs:",
          ["Only after the CPU melts", "Without executing the full program, analyzing source", "Instead of Git", "Only on SSDs"],
          "Without executing the full program, analyzing source", "Static.", "easy", True),
        q("cf-linter-q2", "A compiler error vs a linter warning:",
          ["Always identical", "Compiler errors usually block a build; linters often warn and can be wrong",
           "Linters always block the kernel", "Compilers never fail"],
          "Compiler errors usually block a build; linters often warn and can be wrong", "Severity.", "medium", True),
        q("cf-linter-q3", "You should treat every linter warning as:",
          ["A hardware failure", "A hint to investigate, not automatically as truth", "A GitHub ban", "A reason to format /"],
          "A hint to investigate, not automatically as truth", "False positives exist.", "easy"),
        q("cf-linter-q4", "CI often runs linters to:",
          ["Replace developers", "Catch issues on every push/PR consistently", "Slow PATH", "Disable HTTPS"],
          "Catch issues on every push/PR consistently", "MIT CI paragraph.", "easy"),
    ],
    exercises=[
        ex("cf-linter-ex1", "One warning",
           "Enable or run a linter in VS Code for a language you have (even a JS/Python extension). Introduce a simple unused variable or similar, read the warning, fix it. "
           "Write the warning text and what it meant."),
    ],
)

_add(
    "cf-dev-package-manager",
    hours=0.6,
    objective="Explain application-level package managers vs OS packages.",
    explanation="npm/Maven/pip vs apt/brew. MIT shipping-code is the verified lecture for artifacts and language packages.",
    mastery=["Contrast language ecosystem dependencies with OS packages.", "Score >= 80%."],
    resources=[
        r("cf-dev-package-manager-reference", "MIT Missing Semester 2026 — Packaging and Shipping Code", MIT_SHIP, "MIT Missing Semester 2026", "REFERENCE", "article", 0,
          "Artifacts, pip/uv, project files. PRIMARY TBD."),
    ],
    questions=[
        q("cf-dev-package-manager-q1", "pip/npm vs apt:",
          ["Identical scopes", "Language libraries vs OS-level packages (different layers)", "pip replaces the kernel", "apt only installs GitHub"],
          "Language libraries vs OS-level packages (different layers)", "Two layers.", "medium", True),
        q("cf-dev-package-manager-q2", "A lockfile exists to:",
          ["Lock the SSD physically", "Pin resolved dependency versions for reproducible installs", "Replace Git", "Disable PATH"],
          "Pin resolved dependency versions for reproducible installs", "Reproducibility.", "medium", True),
        q("cf-dev-package-manager-q3", "Installing a library globally without a project env can:",
          ["Never cause issues", "Break unrelated projects via version conflicts", "Compile the CPU", "Create hex"],
          "Break unrelated projects via version conflicts", "Why virtualenvs exist.", "easy"),
        q("cf-dev-package-manager-q4", "An artifact in the shipping lecture is:",
          ["Only a podcast", "A packaged output others can install/run, distinct from source", "A Git stash", "A breakpoint"],
          "A packaged output others can install/run, distinct from source", "MIT shipping.", "easy"),
    ],
    exercises=[
        ex("cf-dev-package-manager-ex1", "Name two layers",
           "Write a table: OS package manager on your WSL distro vs one language manager you will use (Maven later). "
           "One command example each. Do not install random packages from blogs."),
    ],
)

_add(
    "cf-build-system",
    hours=0.6,
    objective="Explain why build tools exist.",
    explanation="Compile + test + package as a repeatable pipeline. make in CS50 Week 1; command runners in MIT Code Quality.",
    mastery=["Describe compile + test + package as a pipeline.", "Run a documented build or test command.", "Score >= 80%."],
    resources=[
        r("cf-build-system-reference", "CS50x 2026 Week 1 (make)", CS50_W1, "CS50x", "REFERENCE", "interactive_tutorial", 0,
          "make hello as a tiny build system."),
        r("cf-build-system-deep", "MIT Missing Semester 2026 — Code Quality", MIT_QUALITY, "MIT Missing Semester 2026", "DEEP_DIVE", "article", 1,
          "Command runners (just lint / just test). PRIMARY TBD."),
    ],
    questions=[
        q("cf-build-system-q1", "A build system exists to:",
          ["Randomize flags each run", "Repeat compile/test/package reliably", "Replace the debugger", "Host GitHub"],
          "Repeat compile/test/package reliably", "Repeatability.", "easy", True),
        q("cf-build-system-q2", "make hello in CS50 conceptually:",
          ["Downloads Ubuntu", "Turns a recipe into a built hello executable", "Creates a PR", "Sets a breakpoint"],
          "Turns a recipe into a built hello executable", "Week 1.", "easy", True),
        q("cf-build-system-q3", "Why not only click Run in the IDE forever:",
          ["IDEs cannot run code", "CI and other machines need a command-line recipe", "Git forbids IDEs", "WSL forbids IDEs"],
          "CI and other machines need a command-line recipe", "Portable builds.", "medium"),
        q("cf-build-system-q4", "`just test` in the MIT lecture is an example of:",
          ["A kernel syscall name", "A short command runner alias for a longer test invocation", "A Git remote", "A hex editor"],
          "A short command runner alias for a longer test invocation", "Code quality lecture.", "easy"),
    ],
    exercises=[
        ex("cf-build-system-ex1", "Run a recipe",
           "Run one real build or test command you already have (pytest, make, npm test) OR write a 5-line Makefile that echoes hello. "
           "Record the command and exit status."),
    ],
)

_add(
    "cf-dependency-management",
    hours=0.6,
    objective="Explain direct vs transitive dependencies conceptually.",
    explanation="Direct deps you declare; transitive come in with them. Risks: breakage, supply chain. MIT shipping lecture.",
    mastery=["State one risk of unmanaged dependencies.", "Score >= 80%."],
    resources=[
        r("cf-dependency-management-reference", "MIT Missing Semester 2026 — Packaging and Shipping Code", MIT_SHIP, "MIT Missing Semester 2026", "REFERENCE", "article", 0,
          "Dependencies, version tension, Dependabot mention. PRIMARY TBD."),
    ],
    questions=[
        q("cf-dependency-management-q1", "A transitive dependency is:",
          ["A Git tag", "A library you did not declare that arrives because something you declared needs it",
           "The kernel", "A CSS file only"],
          "A library you did not declare that arrives because something you declared needs it", "Graph.", "medium", True),
        q("cf-dependency-management-q2", "A supply-chain risk:",
          ["Too much RAM", "A malicious or broken package in your tree", "Using WSL", "Using man pages"],
          "A malicious or broken package in your tree", "Trust.", "medium", True),
        q("cf-dependency-management-q3", "Pinning versions helps:",
          ["Randomize builds", "Reproducible installs and controlled upgrades", "Delete Git", "Disable HTTPS"],
          "Reproducible installs and controlled upgrades", "Lockfiles.", "easy"),
        q("cf-dependency-management-q4", "Adding every library you find on a blog is risky because:",
          ["Blogs cannot use words", "You increase attack surface and coupling without need", "GitHub forbids libraries", "CPUs cannot add"],
          "You increase attack surface and coupling without need", "Minimal deps.", "easy"),
    ],
    exercises=[
        ex("cf-dependency-management-ex1", "Direct vs transitive",
           "Pick a real project (even a tiny Node/Python app) or a hypothetical Maven Java app. List 2 direct dependencies and guess 1 transitive. "
           "Write one risk if you never look at the lockfile."),
    ],
)

_add(
    "cf-problem-decomposition",
    hours=0.75,
    objective="Break a worded problem into smaller parts.",
    explanation="CS50 Week 0: inputs, outputs, computational thinking. Split before coding.",
    mastery=["Decompose a new problem into 3–6 subproblems on paper.", "Score >= 80%."],
    resources=[
        r("cf-problem-decomposition-primary", "CS50x 2026 Week 0 (computational thinking, I/O)", CS50_W0, "CS50x", "PRIMARY", "interactive_tutorial", 0,
          "Inputs/outputs and problem solving. Not the whole Scratch pset."),
        r("cf-problem-decomposition-reference", "CS50x 2026 Lecture 0 notes", CS50_N0, "CS50x", "REFERENCE", "documentation", 1,
          "Problem solving notes."),
    ],
    questions=[
        q("cf-problem-decomposition-q1", "First step for a worded problem is often:",
          ["Write optimized assembly", "Identify inputs, outputs, and constraints", "Push to main", "chmod +x the kernel"],
          "Identify inputs, outputs, and constraints", "CS50 I/O.", "easy", True),
        q("cf-problem-decomposition-q2", "Decomposition helps because:",
          ["It makes problems larger", "Smaller parts can be solved and tested independently", "It replaces testing", "It disables Git"],
          "Smaller parts can be solved and tested independently", "Split.", "easy", True),
        q("cf-problem-decomposition-q3", "If you cannot state the output, you:",
          ["Should start coding loops immediately", "Do not yet understand the problem", "Should rebase origin", "Should buy RAM"],
          "Do not yet understand the problem", "Clarity first.", "medium"),
        q("cf-problem-decomposition-q4", "A subproblem that still includes the whole original spec:",
          ["Is well decomposed", "Is not actually smaller; split again", "Is a Git concept", "Is a syscall"],
          "Is not actually smaller; split again", "True split.", "medium"),
    ],
    exercises=[
        ex("cf-problem-decomposition-ex1", "Inputs and outputs",
           "Exercise 1: Take 'notify me if a folder has files older than 30 days'. Write inputs, outputs, and 4 subproblems. Do not write code yet."),
    ],
)

_add(
    "cf-pseudocode",
    hours=0.6,
    objective="Write language-agnostic steps for a small algorithm.",
    explanation="CS50 Week 0 covers pseudocode. Syntax-free thinking.",
    mastery=["Produce pseudocode for a simple procedure.", "Score >= 80%."],
    resources=[
        r("cf-pseudocode-primary", "CS50x 2026 Week 0 (pseudocode)", CS50_W0, "CS50x", "PRIMARY", "interactive_tutorial", 0,
          "Pseudocode section."),
        r("cf-pseudocode-reference", "CS50x 2026 Lecture 0 notes (pseudocode)", CS50_N0, "CS50x", "REFERENCE", "documentation", 1,
          "Official notes."),
    ],
    questions=[
        q("cf-pseudocode-q1", "Pseudocode is useful because:",
          ["CPUs execute it directly always", "You can design steps without fighting syntax", "It replaces Git", "It is hexadecimal only"],
          "You can design steps without fighting syntax", "Week 0.", "easy", True),
        q("cf-pseudocode-q2", "Good pseudocode should:",
          ["Be ambiguous poetry", "Be unambiguous enough that another person could implement it", "Include only emojis", "Hide the output"],
          "Be unambiguous enough that another person could implement it", "Clarity.", "medium", True),
        q("cf-pseudocode-q3", "If/then and repeat in CS50-style pseudocode express:",
          ["Hardware voltages", "Control flow", "apt mirrors", "PRs"],
          "Control flow", "Week 0.", "easy"),
        q("cf-pseudocode-q4", "Translating pseudocode to Java later:",
          ["Should require inventing a new algorithm each time", "Should be mostly mechanical if the steps were clear",
           "Requires rebase", "Requires a new kernel"],
          "Should be mostly mechanical if the steps were clear", "That's the point.", "easy"),
    ],
    exercises=[
        ex("cf-pseudocode-ex1", "Write pseudocode",
           "Exercise 2: Pseudocode for finding the maximum of a list of numbers. Include a loop and a running best."),
    ],
)

_add(
    "cf-algorithms",
    hours=0.6,
    objective="Define an algorithm as a finite unambiguous procedure.",
    explanation="CS50 Week 0: algorithms and running times. Algorithm vs program.",
    mastery=["Give one example of an algorithm vs a program.", "Compare two simple algorithms.", "Score >= 80%."],
    resources=[
        r("cf-algorithms-primary", "CS50x 2026 Week 0 (algorithms, running times)", CS50_W0, "CS50x", "PRIMARY", "interactive_tutorial", 0,
          "Algorithms and running times. Not a full algorithms course."),
    ],
    questions=[
        q("cf-algorithms-q1", "An algorithm is:",
          ["Any Git repo", "A finite unambiguous procedure to solve a problem", "A brand of CPU", "A CSS file"],
          "A finite unambiguous procedure to solve a problem", "Week 0.", "easy", True),
        q("cf-algorithms-q2", "A program vs an algorithm:",
          ["Identical always", "A program is an implementation of (one or more) algorithms in a language/runtime",
           "Algorithms cannot be implemented", "Programs cannot follow steps"],
          "A program is an implementation of (one or more) algorithms in a language/runtime", "Artifact vs idea.", "medium", True),
        q("cf-algorithms-q3", "Two algorithms for the same task can differ in:",
          ["Whether bits exist", "Correctness, speed, and memory", "Whether Git exists", "Whether WSL exists"],
          "Correctness, speed, and memory", "Week 0 running times.", "easy"),
        q("cf-algorithms-q4", "Phone-book search jumping to the middle vs scanning from page 1 is:",
          ["Not an algorithm", "Two algorithms with different running times", "A syscall", "A formatter"],
          "Two algorithms with different running times", "CS50 classic.", "easy"),
    ],
    exercises=[
        ex("cf-algorithms-ex1", "Compare two algorithms",
           "Exercise 5: Describe linear search vs binary search (sorted list) in 8–12 sentences. When is binary search invalid?"),
    ],
)

_add(
    "cf-dry-runs",
    hours=0.6,
    objective="Trace an algorithm on a small input by hand.",
    explanation="Manual execution before trusting code. Table of variable values per step.",
    mastery=["Dry-run a loop on a 4-element input.", "Score >= 80%."],
    resources=[
        r("cf-dry-runs-reference", "CS50x 2026 Week 0 (algorithms)", CS50_W0, "CS50x", "REFERENCE", "interactive_tutorial", 0,
          "Use the algorithm examples as things you can trace by hand."),
    ],
    questions=[
        q("cf-dry-runs-q1", "A dry run is:",
          ["Deleting tests", "Executing the steps on paper with a tiny input", "Pushing to origin", "Formatting /"],
          "Executing the steps on paper with a tiny input", "Trace.", "easy", True),
        q("cf-dry-runs-q2", "Dry runs catch:",
          ["Only CSS bugs", "Off-by-one and wrong updates before you automate", "Only network outages", "Only Git conflicts"],
          "Off-by-one and wrong updates before you automate", "Cheap bugs.", "medium", True),
        q("cf-dry-runs-q3", "If the dry run disagrees with the code:",
          ["The paper is always wrong", "At least one of them is wrong; investigate", "Reboot", "chmod +x everything"],
          "At least one of them is wrong; investigate", "Don't trust blindly.", "easy"),
        q("cf-dry-runs-q4", "A 4-element array is a good dry-run size because:",
          ["It is infinite", "You can finish the table by hand and still see a pattern", "Git requires 4", "The ALU requires 4"],
          "You can finish the table by hand and still see a pattern", "Small but non-trivial.", "easy"),
    ],
    exercises=[
        ex("cf-dry-runs-ex1", "Trace a loop",
           "Exercise 3: Dry-run finding the max of [3, 9, 2, 9]. Table with columns step, index, current, best."),
    ],
)

_add(
    "cf-edge-cases",
    hours=0.5,
    objective="List empty, one-element, and extreme inputs.",
    explanation="Inputs that break naive solutions: empty, one element, duplicates, already sorted, huge.",
    mastery=["Name three edge cases for a list-processing task.", "Score >= 80%."],
    resources=[
        r("cf-edge-cases-reference", "CS50x 2026 Week 1 (correctness)", CS50_W1, "CS50x", "REFERENCE", "interactive_tutorial", 0,
          "Correctness includes thinking about cases, not only the happy path."),
    ],
    questions=[
        q("cf-edge-cases-q1", "An edge case is:",
          ["The median input only", "An unusual but valid input that often breaks naive code", "An invalid URL", "A Git tag"],
          "An unusual but valid input that often breaks naive code", "Boundaries.", "easy", True),
        q("cf-edge-cases-q2", "Empty list for 'find max':",
          ["Always returns 0", "Needs a defined behavior (error, optional, skip)", "Cannot happen in computers", "Is hexadecimal"],
          "Needs a defined behavior (error, optional, skip)", "Specify it.", "medium", True),
        q("cf-edge-cases-q3", "Testing only the example from the prompt:",
          ["Proves correctness", "Misses edges; examples are usually the happy path", "Replaces dry runs", "Fixes PATH"],
          "Misses edges; examples are usually the happy path", "Insufficient.", "easy"),
        q("cf-edge-cases-q4", "Integer overflow from CS50 Week 1 is an edge because:",
          ["Integers never wrap", "Values at the type's limit misbehave if ignored", "Git overflows", "WSL overflows PATH"],
          "Values at the type's limit misbehave if ignored", "Week 1 overflow.", "medium"),
    ],
    exercises=[
        ex("cf-edge-cases-ex1", "List edges",
           "Exercise 4: For 'average of a list of numbers', list 6 edge cases (empty, one element, negatives, huge n, duplicates, non-numbers if input is text)."),
    ],
)

_add(
    "cf-debugging-thinking",
    hours=0.75,
    objective="Use a hypothesis-driven debugging loop.",
    explanation="Observe, hypothesize, test. MIT debugging lecture + CS50 correctness. Do not randomly edit.",
    mastery=["State observe-hypothesize-test for a failing program.", "Debug a deliberately broken program.", "Score >= 80%."],
    resources=[
        r("cf-debugging-thinking-primary", "MIT Missing Semester 2026 — Debugging and Profiling", MIT_DBG, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Code does what you told it, not what you expected. Print vs debugger."),
        r("cf-debugging-thinking-reference", "CS50x 2026 Week 1 (correctness)", CS50_W1, "CS50x", "REFERENCE", "interactive_tutorial", 1,
          "Correctness mindset."),
    ],
    questions=[
        q("cf-debugging-thinking-q1", "The MIT golden rule quoted in the lecture is closest to:",
          ["Code does what you expect", "Code does what you told it to do", "Git always lies", "Kernels never fail"],
          "Code does what you told it to do", "Lecture intro.", "easy", True),
        q("cf-debugging-thinking-q2", "A hypothesis in debugging is:",
          ["A random rewrite of the whole file", "A testable guess about why the observed behavior happens", "A Git rebase", "A formatter"],
          "A testable guess about why the observed behavior happens", "Scientific loop.", "medium", True),
        q("cf-debugging-thinking-q3", "Changing three things at once is bad because:",
          ["Git forbids it", "You cannot tell which change mattered", "WSL crashes", "man pages disappear"],
          "You cannot tell which change mattered", "Isolate.", "easy"),
        q("cf-debugging-thinking-q4", "If a test fails, first you should:",
          ["Delete the test", "Reproduce it and observe actual vs expected", "Force-push", "Reinstall the OS"],
          "Reproduce it and observe actual vs expected", "Observe first.", "easy"),
    ],
    exercises=[
        ex("cf-debugging-thinking-ex1", "Broken program",
           "Exercise 8: Write a 10-line program with a deliberate bug (wrong loop bound or off-by-one). Debug it with observe/hypothesize/test. "
           "Write the hypothesis and the evidence. Use a debugger if you can."),
    ],
)

_add(
    "cf-time-complexity-intro",
    hours=0.75,
    objective="Explain big-O as growth rate, not a stopwatch.",
    explanation="CS50 Week 0 running times. O(n) vs O(n^2) as input grows. No recurrences.",
    mastery=["Compare O(n) vs O(n^2) on growing input size.", "Estimate time complexity of a simple loop.", "Score >= 80%."],
    resources=[
        r("cf-time-complexity-intro-primary", "CS50x 2026 Week 0 (running times)", CS50_W0, "CS50x", "PRIMARY", "interactive_tutorial", 0,
          "Running times / algorithms. First contact only."),
    ],
    questions=[
        q("cf-time-complexity-intro-q1", "Big-O in this intro is about:",
          ["Wall-clock on one laptop only", "How work grows as input size grows", "Git history size", "SSD brand"],
          "How work grows as input size grows", "Growth rate.", "easy", True),
        q("cf-time-complexity-intro-q2", "Nested loops over n typically:",
          ["O(1)", "O(n^2) in the simple case", "O(log n) always", "O(PATH)"],
          "O(n^2) in the simple case", "Intro only.", "easy", True),
        q("cf-time-complexity-intro-q3", "A faster CPU:",
          ["Changes O(n^2) into O(n) by magic", "Shifts the constant but not the growth class", "Deletes nested loops", "Rewrites Git"],
          "Shifts the constant but not the growth class", "Not a stopwatch.", "medium", True),
        q("cf-time-complexity-intro-q4", "Linear search vs binary search on sorted data:",
          ["Same growth", "Binary search grows much slower (logarithmic) if the list is sorted", "Linear is always faster for huge n", "Both are O(1)"],
          "Binary search grows much slower (logarithmic) if the list is sorted", "Week 0 phone book.", "medium"),
    ],
    exercises=[
        ex("cf-time-complexity-intro-ex1", "Estimate growth",
           "Exercise 6: For (a) one loop over n (b) nested i,j loops over n, state big-O and which wins at n=10 vs n=10,000 conceptually."),
    ],
)

_add(
    "cf-space-complexity-intro",
    hours=0.5,
    objective="Explain extra memory vs in-place use at a high level.",
    explanation="O(1) extra space vs O(n) extra arrays. First contact only.",
    mastery=["Give an example of O(1) extra space vs O(n).", "Estimate space for a simple approach.", "Score >= 80%."],
    resources=[
        r("cf-space-complexity-intro-reference", "CS50x 2026 Week 0 (algorithms as using resources)", CS50_W0, "CS50x", "REFERENCE", "interactive_tutorial", 0,
          "Week 0 emphasizes time; this lesson adds the memory counterpart as an internal explanation."),
    ],
    questions=[
        q("cf-space-complexity-intro-q1", "Extra space usually means:",
          ["The size of the SSD factory", "Additional memory beyond the input itself", "Git LFS", "CPU cache branding"],
          "Additional memory beyond the input itself", "Auxiliary space.", "easy", True),
        q("cf-space-complexity-intro-q2", "Copying an array of n elements to a new array is typically:",
          ["O(1) extra space", "O(n) extra space", "O(n^2) extra space always", "Zero bits"],
          "O(n) extra space", "New array.", "easy", True),
        q("cf-space-complexity-intro-q3", "Swapping two variables in place is typically:",
          ["O(n) extra", "O(1) extra", "O(n^2)", "Unbounded"],
          "O(1) extra", "Few registers/temps.", "easy", True),
        q("cf-space-complexity-intro-q4", "Time vs space:",
          ["Always identical", "You can sometimes use more memory to save time (and vice versa)", "Space never matters", "Only time exists"],
          "You can sometimes use more memory to save time (and vice versa)", "Tradeoff.", "medium"),
    ],
    exercises=[
        ex("cf-space-complexity-intro-ex1", "Estimate space",
           "Exercise 7: For reversing an array, contrast an in-place swap approach vs allocating a second array. State extra space for each."),
    ],
)
