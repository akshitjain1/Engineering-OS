"""Emit Curriculum V1 official manifests (structure only; no invented URLs)."""

from __future__ import annotations

from pathlib import Path

import yaml

from v1_specs import dsa_spec, java_spec

ROOT = Path(__file__).resolve().parents[1] / "content" / "curriculum"
TRACK = {
    "slug": "engineering-os-v1",
    "name": "Engineering OS",
    "description": "Curriculum V1: Computer & Developer Foundations, Java, and Data Structures & Algorithms.",
    "order": 0,
}


def topic(
    slug: str,
    name: str,
    order: int,
    prereqs: list[str],
    objective: str,
    mastery: list[str],
    next_slug: str | None,
    blurb: str,
    planned_resources: list[dict] | None = None,
    extra_lessons: list[dict] | None = None,
) -> dict:
    lesson = {
        "slug": f"{slug}-core",
        "title": name,
        "description": blurb,
        "order": 0,
        "hours_estimated": 1.0,
        "resources": planned_resources or [],
        "questions": [],
        "exercises": [],
    }
    lessons = [lesson]
    if extra_lessons:
        lessons.extend(extra_lessons)
    return {
        "slug": slug,
        "name": name,
        "description": blurb,
        "order": order,
        "prerequisites": prereqs,
        "learning_objective": objective,
        "mastery_criteria": mastery,
        "next_topic": next_slug,
        "fast_trackable": True,
        "lessons": lessons,
    }


def chain(items: list[tuple], prefix_prereq: list[str] | None = None) -> list[dict]:
    """items: (slug, name, objective, mastery_list, blurb, planned_resources?)"""
    out = []
    prev = list(prefix_prereq or [])
    for i, item in enumerate(items):
        slug, name, objective, mastery, blurb = item[:5]
        planned = item[5] if len(item) > 5 else []
        nxt = items[i + 1][0] if i + 1 < len(items) else None
        prereqs = prev[:] if i == 0 else [items[i - 1][0]]
        # first topic keeps prefix prereqs; later topics depend on immediate predecessor
        out.append(topic(slug, name, i, prereqs, objective, mastery, nxt, blurb, planned))
        prev = [slug]
    return out


def conceptual(*skills: str) -> list[str]:
    return list(skills)


def dsa_mastery(*skills: str) -> list[str]:
    items = list(skills)
    for extra in (
        "State time and space complexity of a correct approach.",
        "Name one common mistake for this topic.",
    ):
        if extra not in items:
            items.append(extra)
    return items


def fill_resource_slugs(topics: list[dict]) -> None:
    for t in topics:
        for lesson in t["lessons"]:
            for i, res in enumerate(lesson["resources"]):
                if not res.get("slug"):
                    res["slug"] = f"{t['slug']}-res-{i}-{res['role'].lower().replace('_', '-')}"


def slot(topic_slug: str, key: str, title: str, provider: str | None, role: str, order: int, rtype: str = "other") -> dict:
    item = {
        "slug": f"{topic_slug}-{key}",
        "title": title,
        "type": rtype,
        "role": role,
        "description": "Exact URL not mapped in this phase. Do not invent links.",
        "order": order,
    }
    if provider:
        item["provider"] = provider
    return item


def set_lesson_resources(topics: list[dict], resources_for) -> None:
    for topic in topics:
        topic["lessons"][0]["resources"] = resources_for(topic["slug"])


def assemble_modules(
    modules_spec: list[tuple],
    first_prefix: list[str],
) -> list[dict]:
    """Build modules with sequential next_topic and optional extra prereqs on the first topic.

    Row: (module_slug, module_name, topic_tuples, extra_prereqs_on_first?)
    extra_prereqs are merged onto the first topic (minimum Java for a DSA unit).
    Last topic of the last module has next_topic None (no forced jump to another domain).
    """
    yaml_modules: list[dict] = []
    prev_last: str | None = None
    for mi, row in enumerate(modules_spec):
        mslug, mname, topics = row[0], row[1], row[2]
        extra = list(row[3]) if len(row) > 3 else []
        prefix = list(first_prefix) if mi == 0 else []
        built = chain([(a, b, c, d, e) for a, b, c, d, e in topics], prefix_prereq=prefix)
        if mi == 0:
            built[0]["prerequisites"] = list(dict.fromkeys(list(first_prefix) + extra))
        else:
            built[0]["prerequisites"] = list(dict.fromkeys([prev_last] + extra if prev_last else extra))
        prev_last = built[-1]["slug"]
        if mi + 1 < len(modules_spec):
            built[-1]["next_topic"] = modules_spec[mi + 1][2][0][0]
        else:
            built[-1]["next_topic"] = None
        yaml_modules.append({"slug": f"mod-{mslug}", "name": mname, "order": mi, "topics": built})
    return yaml_modules


def iter_module_topics(yaml_modules: list[dict]) -> list[dict]:
    topics: list[dict] = []
    for module in yaml_modules:
        topics.extend(module["topics"])
    return topics


def dump(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def domain0() -> dict:
    cf = chain(
        [
            ("cf-bits-and-bytes", "Bits and bytes",
             "Explain how information is measured in bits and bytes.",
             conceptual("Explain bits vs bytes without notes.", "Convert a small quantity between bits and bytes.", "Score >= 80% on a short conceptual check."),
             "Units of digital information and why they matter for storage and communication."),
            ("cf-binary", "Binary",
             "Read and convert small binary values.",
             conceptual("Convert between binary and decimal for values up to 8 bits without copying.", "Explain why computers use binary.", "Score >= 80%."),
             "Base-2 representation used by digital hardware."),
            ("cf-hexadecimal", "Hexadecimal",
             "Use hexadecimal as a compact view of binary.",
             conceptual("Convert between binary, hex, and decimal for small values.", "Explain why hex is used in debugging and memory dumps.", "Score >= 80%."),
             "Base-16 notation as a human-friendly encoding of binary."),
            ("cf-cpu", "CPU",
             "Describe what a CPU does in executing programs.",
             conceptual("Explain the CPU's role in a computer without notes.", "Contrast CPU with memory and storage.", "Score >= 80%."),
             "The processor as the engine that executes instructions."),
            ("cf-alu", "ALU",
             "Explain the ALU's role in arithmetic and logic.",
             conceptual("State what the ALU computes.", "Relate ALU operations to simple program statements.", "Score >= 80%."),
             "Arithmetic Logic Unit: integer arithmetic and boolean operations."),
            ("cf-registers", "Registers",
             "Explain registers as the CPU's fastest working storage.",
             conceptual("Explain why registers are small and fast.", "Give examples of what is stored in registers during execution.", "Score >= 80%."),
             "Tiny, fast storage inside the CPU used during instruction execution."),
            ("cf-ram", "RAM",
             "Explain RAM as volatile working memory.",
             conceptual("Contrast RAM with registers and with disk.", "Explain volatility.", "Score >= 80%."),
             "Main memory that holds running programs and data."),
            ("cf-cache", "Cache",
             "Explain why caches exist between CPU and RAM.",
             conceptual("Explain the idea of locality at a high level.", "Place cache in the memory hierarchy.", "Score >= 80%."),
             "Small faster memory that hides RAM latency. Depth without cache-coherence protocols."),
            ("cf-storage", "Storage",
             "Contrast persistent storage with RAM.",
             conceptual("Explain persistence vs volatility.", "Give typical uses of disk/SSD vs RAM.", "Score >= 80%."),
             "Long-term storage devices and why programs must be loaded into memory to run."),
            ("cf-instruction-execution", "Instruction execution",
             "Describe fetch-decode-execute at a conceptual level.",
             conceptual("Walk through fetch-decode-execute without notes.", "Relate a simple statement to an instruction stream.", "Score >= 80%."),
             "How a processor carries out one instruction after another."),
            ("cf-machine-code", "Machine code",
             "Explain machine code as the CPU's native language.",
             conceptual("Contrast machine code with a high-level language.", "Explain why machine code is architecture-specific.", "Score >= 80%."),
             "Binary instructions a particular CPU family can execute."),
            ("cf-compiler", "Compiler",
             "Explain what a compiler produces and when it runs.",
             conceptual("Explain compile-time vs run-time.", "Contrast compiling with interpreting.", "Score >= 80%."),
             "Translating source code to machine code or bytecode ahead of execution."),
            ("cf-interpreter", "Interpreter",
             "Explain how an interpreter executes source or bytecode.",
             conceptual("Give one advantage and one cost of interpretation.", "Relate interpreters to virtual machines at a high level.", "Score >= 80%."),
             "Executing a program by analyzing and running it incrementally."),
            ("cf-program", "Program",
             "Define a program as stored instructions plus data.",
             conceptual("Distinguish a program on disk from a running process.", "Score >= 80%."),
             "A program as an artifact: source, compiled form, and what it represents."),
            ("cf-process", "Process",
             "Define a process as a running instance of a program.",
             conceptual("Explain program vs process without notes.", "List what a process typically owns (memory, files) at a high level.", "Score >= 80%."),
             "A process as the OS abstraction for a running program."),
        ]
    )

    os_mod = chain(
        [
            ("cf-kernel", "Kernel",
             "Explain the kernel as the core of the operating system.",
             conceptual("Explain kernel vs user programs without notes.", "Score >= 80%."),
             "The privileged program that manages hardware and processes."),
            ("cf-os-processes", "Processes",
             "Describe how the OS manages processes.",
             conceptual("Explain process creation at a high level.", "Contrast process and program.", "Score >= 80%."),
             "OS view of processes: isolation, identity, and lifecycle. Builds on cf-process."),
            ("cf-threads", "Threads",
             "Contrast threads with processes.",
             conceptual("Explain shared memory vs separate processes.", "State one reason programs use threads.", "Score >= 80%."),
             "Multiple execution contexts inside a process."),
            ("cf-system-calls", "System calls",
             "Explain system calls as the program-to-kernel interface.",
             conceptual("Give two examples of system-call categories (I/O, process).", "Score >= 80%."),
             "Controlled entry points from user programs into the kernel."),
            ("cf-os-memory", "Memory",
             "Describe how the OS is involved in process memory.",
             conceptual("Relate process memory to RAM.", "Score >= 80%."),
             "OS-managed memory for processes, at a conceptual level."),
            ("cf-virtual-memory-basics", "Virtual memory basics",
             "Explain why virtual memory exists, without paging algorithms.",
             conceptual("Explain virtual vs physical addresses in one paragraph.", "Score >= 80%."),
             "Each process seeing its own address space. No OS internals exam."),
            ("cf-filesystems", "Filesystems",
             "Explain files and directories as OS abstractions.",
             conceptual("Explain file vs inode/path at a high level.", "Score >= 80%."),
             "Hierarchical storage of files."),
            ("cf-os-permissions", "Permissions",
             "Explain user/group/other permission bits conceptually.",
             conceptual("Read a simple rwx triplet.", "Score >= 80%."),
             "Who may read, write, or execute a file."),
            ("cf-os-environment-variables", "Environment variables",
             "Explain environment variables as process configuration.",
             conceptual("Give two examples of environment variables.", "Score >= 80%."),
             "Key-value settings inherited by processes."),
        ],
        prefix_prereq=["cf-process"],
    )
    os_mod[0]["prerequisites"] = ["cf-process"]

    linux = chain(
        [
            ("cf-shell", "Shell",
             "Explain the shell as a command interpreter.",
             conceptual("Start a shell and state what it does.", "Score >= 80%."),
             "The program that reads commands and starts other programs."),
            ("cf-command-line", "Command line",
             "Issue basic commands with arguments.",
             conceptual("Explain command, arguments, and exit status.", "Run a simple command independently.", "Score >= 80%."),
             "Syntax of commands in a terminal."),
            ("cf-filesystem-navigation", "Filesystem navigation",
             "Move around the filesystem with pwd, ls, and cd.",
             conceptual("Navigate to a nested directory without a GUI.", "Score >= 80%."),
             "Paths, working directory, and listing files."),
            ("cf-linux-files", "Files",
             "Create, copy, move, and delete files from the terminal.",
             conceptual("Use core file commands independently.", "Score >= 80%."),
             "Everyday file operations in a Unix-like system."),
            ("cf-pipes", "Pipes",
             "Connect command output to another command with pipes.",
             conceptual("Write a two-command pipeline.", "Score >= 80%."),
             "Stdout of one process as stdin of the next."),
            ("cf-redirection", "Redirection",
             "Redirect stdin/stdout/stderr to files.",
             conceptual("Save command output to a file.", "Score >= 80%."),
             "Connecting process streams to files."),
            ("cf-grep", "grep",
             "Search file contents with grep.",
             conceptual("Find lines matching a pattern in a file.", "Score >= 80%."),
             "Pattern search over text."),
            ("cf-find", "find",
             "Locate files by name or type.",
             conceptual("Find files under a directory by name.", "Score >= 80%."),
             "Filesystem search."),
            ("cf-linux-permissions", "Permissions",
             "Inspect and reason about Unix permission bits.",
             conceptual("Interpret ls -l permission columns.", "Score >= 80%."),
             "Applying OS permission concepts at the terminal."),
            ("cf-linux-processes", "Processes",
             "List and interpret running processes.",
             conceptual("Identify a process and its PID.", "Score >= 80%."),
             "ps/jobs at a basic level. No sysadmin specialization."),
            ("cf-package-management", "Package management",
             "Explain why package managers exist.",
             conceptual("Describe install vs compile-from-source at a high level.", "Score >= 80%."),
             "Installing software through the distribution's tool. Exact distro commands left to the environment."),
            ("cf-linux-environment-variables", "Environment variables",
             "Read and set environment variables in the shell.",
             conceptual("Print PATH and explain one entry.", "Score >= 80%."),
             "export and PATH. Builds on OS environment variables."),
        ],
        prefix_prereq=["cf-os-environment-variables"],
    )

    git = chain(
        [
            ("cf-repository", "Repository",
             "Explain a Git repository as a project history.",
             conceptual("Initialize or clone a repo and explain .git at a high level.", "Score >= 80%."),
             "What a repo is and why it exists."),
            ("cf-commits", "Commits",
             "Create commits with a clear message.",
             conceptual("Make a commit independently.", "Explain snapshot vs working tree.", "Score >= 80%."),
             "Atomic recorded changes."),
            ("cf-branches", "Branches",
             "Create and switch branches.",
             conceptual("Explain a branch as a movable pointer to a commit.", "Score >= 80%."),
             "Parallel lines of work."),
            ("cf-merge", "Merge",
             "Combine branches with merge.",
             conceptual("Merge a feature branch and explain the result.", "Score >= 80%."),
             "Joining histories."),
            ("cf-rebase", "Rebase",
             "Explain rebase vs merge conceptually.",
             conceptual("State when rebase is used and its risk on shared branches.", "Score >= 80%."),
             "Replaying commits. Practice only on local branches in V1."),
            ("cf-remote", "Remote",
             "Explain remotes as named copies of a repository.",
             conceptual("List remotes and explain origin.", "Score >= 80%."),
             "Connecting a local repo to another copy."),
            ("cf-pull-push", "Pull and push",
             "Send and receive commits.",
             conceptual("Push and pull a branch independently.", "Score >= 80%."),
             "Synchronizing with a remote."),
            ("cf-conflicts", "Conflicts",
             "Recognize and resolve a simple merge conflict.",
             conceptual("Resolve a two-hunk conflict in a text file.", "Score >= 80%."),
             "When two changes edit the same lines."),
            ("cf-reset-revert", "Reset and revert",
             "Contrast reset and revert.",
             conceptual("Choose revert for published history in a simple scenario.", "Score >= 80%."),
             "Undoing changes safely."),
            ("cf-cherry-pick", "Cherry-pick",
             "Apply one commit onto another branch.",
             conceptual("Explain cherry-pick vs merge.", "Score >= 80%."),
             "Copying an individual commit."),
            ("cf-stash", "Stash",
             "Temporarily shelf uncommitted work.",
             conceptual("Stash, switch branch, and restore.", "Score >= 80%."),
             "Dirty working tree vs a clean checkout."),
            ("cf-github-workflow", "GitHub workflow",
             "Use clone, branch, pull request conceptually.",
             conceptual("Describe a PR-based workflow without notes.", "Score >= 80%."),
             "Hosting and review on GitHub. Exact UI steps left to official GitHub docs later."),
        ],
        prefix_prereq=["cf-linux-environment-variables"],
    )

    devenv = chain(
        [
            ("cf-ide", "IDE",
             "Use an IDE to open, edit, and run a small project.",
             conceptual("Open a project and run it from the IDE.", "Score >= 80%."),
             "Editor plus project tools. Choice of IDE is personal; the skill is using one well."),
            ("cf-dev-compiler", "Compiler",
             "Invoke a compiler from the environment you will use for Java.",
             conceptual("Explain what the compile step produces.", "Score >= 80%."),
             "Applying cf-compiler in a real toolchain."),
            ("cf-debugger", "Debugger",
             "Set a breakpoint and inspect a variable.",
             conceptual("Use a debugger on a trivial program.", "Score >= 80%."),
             "Stepping through execution instead of only printing."),
            ("cf-formatter", "Formatter",
             "Apply automatic formatting.",
             conceptual("Explain why formatters exist.", "Score >= 80%."),
             "Consistent style without manual debate."),
            ("cf-linter", "Linter",
             "Run a linter and interpret one warning.",
             conceptual("Distinguish a linter finding from a compiler error.", "Score >= 80%."),
             "Static hints before runtime."),
            ("cf-dev-package-manager", "Package manager",
             "Explain application-level package managers vs OS packages.",
             conceptual("Contrast npm/Maven/pip with apt/brew at a high level.", "Score >= 80%."),
             "Language ecosystem dependencies."),
            ("cf-build-system", "Build system",
             "Explain why build tools exist.",
             conceptual("Describe compile + test + package as a pipeline.", "Score >= 80%."),
             "Repeatable builds. Exact Maven/Gradle usage comes with Java."),
            ("cf-dependency-management", "Dependency management",
             "Explain direct vs transitive dependencies conceptually.",
             conceptual("State one risk of unmanaged dependencies.", "Score >= 80%."),
             "Locking and versioning libraries."),
        ],
        prefix_prereq=["cf-github-workflow", "cf-compiler"],
    )

    thinking = chain(
        [
            ("cf-problem-decomposition", "Problem decomposition",
             "Break a worded problem into smaller parts.",
             conceptual("Decompose a new problem into 3–6 subproblems on paper.", "Score >= 80%."),
             "The habit of splitting work before coding."),
            ("cf-pseudocode", "Pseudocode",
             "Write language-agnostic steps for a small algorithm.",
             conceptual("Produce pseudocode for a simple procedure.", "Score >= 80%."),
             "Thinking in steps without syntax."),
            ("cf-algorithms", "Algorithms",
             "Define an algorithm as a finite unambiguous procedure.",
             conceptual("Give one example of an algorithm vs a program.", "Score >= 80%."),
             "What counts as an algorithm."),
            ("cf-dry-runs", "Dry runs",
             "Trace an algorithm on a small input by hand.",
             conceptual("Dry-run a loop on a 4-element input.", "Score >= 80%."),
             "Manual execution before trusting code."),
            ("cf-edge-cases", "Edge cases",
             "List empty, one-element, and extreme inputs.",
             conceptual("Name three edge cases for a list-processing task.", "Score >= 80%."),
             "Inputs that break naive solutions."),
            ("cf-debugging-thinking", "Debugging",
             "Use a hypothesis-driven debugging loop.",
             conceptual("State observe-hypothesize-test for a failing program.", "Score >= 80%."),
             "Debugging as a process, not random edits."),
            ("cf-time-complexity-intro", "Time complexity introduction",
             "Explain big-O as growth rate, not a stopwatch.",
             conceptual("Compare O(n) vs O(n^2) on growing input size.", "Score >= 80%."),
             "First contact with asymptotic time. No recurrences."),
            ("cf-space-complexity-intro", "Space complexity introduction",
             "Explain extra memory vs in-place use at a high level.",
             conceptual("Give an example of O(1) extra space vs O(n).", "Score >= 80%."),
             "First contact with memory as a resource."),
        ],
        prefix_prereq=["cf-dependency-management"],
    )

    # Cross-link next_topic across modules
    def link_modules(a: list[dict], b: list[dict]) -> None:
        a[-1]["next_topic"] = b[0]["slug"]

    link_modules(cf, os_mod)
    link_modules(os_mod, linux)
    link_modules(linux, git)
    link_modules(git, devenv)
    link_modules(devenv, thinking)
    thinking[-1]["next_topic"] = None

    for group in (cf, os_mod, linux, git, devenv, thinking):
        fill_resource_slugs(group)

    set_lesson_resources(
        cf,
        lambda s: [
            slot(s, "primary", "CS50x selected material (mapping pending)", "CS50x", "PRIMARY", 0),
        ],
    )
    set_lesson_resources(
        os_mod + linux,
        lambda s: [
            slot(s, "primary", "MIT Missing Semester 2026 selected material (mapping pending)", "MIT Missing Semester 2026", "PRIMARY", 0),
            slot(s, "reference", "CS50x selected material (mapping pending)", "CS50x", "REFERENCE", 1),
        ],
    )
    set_lesson_resources(
        git,
        lambda s: [
            slot(s, "primary", "Official Git documentation (mapping pending)", "Git", "PRIMARY", 0, "documentation"),
            slot(s, "reference", "Official GitHub documentation (mapping pending)", "GitHub", "REFERENCE", 1, "documentation"),
        ],
    )
    set_lesson_resources(
        devenv,
        lambda s: [
            slot(s, "primary", "Primary toolchain resource (TBD — unresolved)", None, "PRIMARY", 0),
            slot(s, "reference", "Dev.java / official tooling documentation (mapping pending)", "Dev.java", "REFERENCE", 1, "documentation"),
        ],
    )
    set_lesson_resources(
        thinking,
        lambda s: [
            slot(s, "primary", "CS50x selected material (mapping pending)", "CS50x", "PRIMARY", 0),
        ],
    )

    return {
        "schema_version": 1,
        "kind": "curriculum_manifest",
        "origin": "official",
        "track": {
            **TRACK,
            "levels": [
                {
                    "slug": "domain-0",
                    "name": "Domain 0 Foundations",
                    "description": "Computer and developer foundations before Java and DSA.",
                    "order": 0,
                    "subjects": [
                        {
                            "slug": "computer-developer-foundations",
                            "name": "Computer & Developer Foundations",
                            "description": "Hardware/OS literacy, terminal, Git, tooling, and problem-solving habits.",
                            "order": 0,
                            "modules": [
                                {"slug": "mod-cf-computer-fundamentals", "name": "Computer Fundamentals", "order": 0, "topics": cf},
                                {"slug": "mod-cf-operating-systems", "name": "Operating System Fundamentals", "order": 1, "topics": os_mod},
                                {"slug": "mod-cf-terminal-linux", "name": "Terminal & Linux", "order": 2, "topics": linux},
                                {"slug": "mod-cf-git", "name": "Git & Version Control", "order": 3, "topics": git},
                                {"slug": "mod-cf-dev-environment", "name": "Development Environment", "order": 4, "topics": devenv},
                                {"slug": "mod-cf-programming-thinking", "name": "Programming & Problem-Solving Fundamentals", "order": 5, "topics": thinking},
                            ],
                        }
                    ],
                }
            ],
        },
    }


def domain1() -> dict:
    yaml_modules = assemble_modules(
        java_spec(),
        first_prefix=["cf-space-complexity-intro", "cf-dependency-management"],
    )
    topics = iter_module_topics(yaml_modules)
    fill_resource_slugs(topics)
    set_lesson_resources(
        topics,
        lambda s: [
            slot(
                s,
                "primary",
                "University of Helsinki Java Programming I/II (mapping pending)",
                "University of Helsinki",
                "PRIMARY",
                0,
                "interactive_tutorial",
            ),
            slot(
                s,
                "reference",
                "Dev.java official documentation — authoritative modern Java reference (mapping pending)",
                "Dev.java",
                "REFERENCE",
                1,
                "documentation",
            ),
        ],
    )
    for topic in topics:
        for res in topic["lessons"][0]["resources"]:
            if res["role"] == "PRIMARY":
                res["description"] = (
                    "Exercise-heavy learning resource. Legacy/unmaintained; not the authoritative "
                    "modern Java reference. Exact part URLs not mapped in this phase."
                )
            elif res["role"] == "REFERENCE":
                res["description"] = (
                    "Authoritative modern Java reference. Exact page URLs not mapped in this phase."
                )

    return {
        "schema_version": 1,
        "kind": "curriculum_manifest",
        "origin": "official",
        "track": {
            **TRACK,
            "levels": [
                {
                    "slug": "domain-1",
                    "name": "Domain 1 Java",
                    "description": "Java programming. Helsinki I/II for exercises; Dev.java for modern reference. Parallel with DSA after fundamentals.",
                    "order": 1,
                    "subjects": [
                        {
                            "slug": "java-programming",
                            "name": "Java Programming",
                            "description": "A structured Java sequence. Streams, concurrency, and JVM are not DSA gates. Records/modules/virtual threads are later/reference.",
                            "order": 0,
                            "modules": yaml_modules,
                        }
                    ],
                }
            ],
        },
    }


DSA_DEEP_DIVE = {
    "dsa-big-o",
    "dsa-merge-sort",
    "dsa-heap-structure",
    "dsa-graph-representations",
    "dsa-dijkstra",
    "dsa-mst",
    "dsa-dp-mindset",
    "dsa-union-find",
}


def dsa_resource_slots(slug: str) -> list[dict]:
    items = [
        slot(slug, "primary", "Abdul Bari conceptual lecture (mapping pending)", "Abdul Bari", "PRIMARY", 0, "youtube_video"),
        slot(slug, "impl-java", "Java implementation (mapping pending)", None, "REFERENCE", 1),
        slot(slug, "impl-cpp", "C++ equivalence / reference (mapping pending)", None, "REFERENCE", 2),
        slot(slug, "practice-core-skills", "NeetCode Core Skills (mapping pending)", "NeetCode", "PRACTICE", 3),
        slot(slug, "practice-nc150", "NeetCode 150 (mapping pending)", "NeetCode", "PRACTICE", 4),
        slot(slug, "practice-leetcode", "LeetCode Study Plan practice (mapping pending)", "LeetCode", "PRACTICE", 5, "coding_problem"),
    ]
    if slug in DSA_DEEP_DIVE:
        items.append(slot(slug, "deep-dive", "MIT 6.006 reference (mapping pending)", "MIT 6.006", "DEEP_DIVE", 6))
    return items


def domain2() -> dict:
    yaml_modules = assemble_modules(
        dsa_spec(),
        first_prefix=["cf-time-complexity-intro", "java-method-basics"],
    )
    topics = iter_module_topics(yaml_modules)
    fill_resource_slugs(topics)
    set_lesson_resources(topics, dsa_resource_slots)

    return {
        "schema_version": 1,
        "kind": "curriculum_manifest",
        "origin": "official",
        "track": {
            **TRACK,
            "levels": [
                {
                    "slug": "domain-2",
                    "name": "Domain 2 DSA",
                    "description": "Language-independent DSA. Java is the primary implementation language; C++ is existing knowledge, not a second curriculum.",
                    "order": 2,
                    "subjects": [
                        {
                            "slug": "data-structures-algorithms",
                            "name": "Data Structures & Algorithms",
                            "description": "Minimum Java per unit. Not gated on streams, concurrency, or JVM. Problem URLs come later.",
                            "order": 0,
                            "modules": yaml_modules,
                        }
                    ],
                }
            ],
        },
    }


def main() -> None:
    d0 = domain0()
    d1 = domain1()
    d2 = domain2()
    print("Skipping Domain 0 YAML overwrite (authored via content/d0_populate.py)")
    print("Skipping Domain 1 YAML overwrite (authored via content/d1_populate.py)")
    print("Skipping Domain 2 YAML overwrite (authored via content/d2_populate.py)")
    dump(
        ROOT / "v1-index.yaml",
        {
            "schema_version": 1,
            "kind": "curriculum_index",
            "origin": "official",
            "files": [
                "foundation/00-computer-developer-foundations.yaml",
                "programming/01-java-programming.yaml",
                "dsa/02-data-structures-algorithms.yaml",
            ],
        },
    )
    def count(doc):
        n_mod = n_top = 0
        for level in doc["track"]["levels"]:
            for subject in level["subjects"]:
                n_mod += len(subject["modules"])
                for module in subject["modules"]:
                    n_top += len(module["topics"])
        return n_mod, n_top
    print("D0", count(d0), "D1", count(d1), "D2", count(d2))
    print("wrote", ROOT)


if __name__ == "__main__":
    main()
