"""Verification infrastructure - additive, backward-compatible.

Defines the rigorous resource contract without mutating the existing
222-topic curriculum graph, prerequisites, or user data.

Roles, verification_status, exactness, concept coverage, practice
contract, time contract, and readiness classifications live here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

# ── Resource Roles (ordered) ──────────────────────────────────
ROLE_PRIMARY_LEARN = "PRIMARY_LEARN"  # canonical PRIMARY
ROLE_SUPPLEMENT = "SUPPLEMENT"
ROLE_REFERENCE = "REFERENCE"
ROLE_PRACTICE = "PRACTICE"
ROLE_BUILD = "BUILD"
ROLE_DEEP_DIVE = "DEEP_DIVE"

# Backward-compatible aliases (existing DB values map to new roles)
ROLE_ALIASES: dict[str, str] = {
    "PRIMARY": ROLE_PRIMARY_LEARN,
    "PRIMARY_LEARN": ROLE_PRIMARY_LEARN,
    "SUPPLEMENT": ROLE_SUPPLEMENT,
    "REFERENCE": ROLE_REFERENCE,
    "PRACTICE": ROLE_PRACTICE,
    "BUILD": ROLE_BUILD,
    "DEEP_DIVE": ROLE_DEEP_DIVE,
}

ALL_ROLES = [
    ROLE_PRIMARY_LEARN,
    ROLE_SUPPLEMENT,
    ROLE_REFERENCE,
    ROLE_PRACTICE,
    ROLE_BUILD,
    ROLE_DEEP_DIVE,
]

# ── Verification Statuses ─────────────────────────────────────
VERIFICATION_UNVERIFIED = "UNVERIFIED"
VERIFICATION_VERIFIED_COVERAGE = "VERIFIED_COVERAGE"
VERIFICATION_PARTIAL_COVERAGE = "PARTIAL_COVERAGE"
VERIFICATION_COLLECTION_ONLY = "COLLECTION_ONLY"
VERIFICATION_BROKEN = "BROKEN"
VERIFICATION_NEEDS_REVIEW = "NEEDS_REVIEW"

ALL_VERIFICATION_STATUSES = [
    VERIFICATION_UNVERIFIED,
    VERIFICATION_VERIFIED_COVERAGE,
    VERIFICATION_PARTIAL_COVERAGE,
    VERIFICATION_COLLECTION_ONLY,
    VERIFICATION_BROKEN,
    VERIFICATION_NEEDS_REVIEW,
]

# ── Exactness ─────────────────────────────────────────────────
EXACTNESS_EXACT = "EXACT"
EXACTNESS_MULTI_TOPIC = "MULTI_TOPIC"
EXACTNESS_COLLECTION = "COLLECTION"

ALL_EXACTNESS = [EXACTNESS_EXACT, EXACTNESS_MULTI_TOPIC, EXACTNESS_COLLECTION]

# ── Readiness Classifications ─────────────────────────────────
READINESS_READY = "READY"
READINESS_PARTIALLY_READY = "PARTIALLY_READY"
READINESS_PARTIAL_COVERAGE = "PARTIAL_COVERAGE"
READINESS_RESOURCE_GAP = "RESOURCE_GAP"
READINESS_PRACTICE_GAP = "PRACTICE_GAP"
READINESS_PRACTICE_UNVERIFIED = "PRACTICE_UNVERIFIED"
READINESS_TIME_UNVERIFIED = "TIME_UNVERIFIED"
READINESS_NEEDS_REVIEW = "NEEDS_REVIEW"
READINESS_BROKEN = "BROKEN"

ALL_READINESS = [
    READINESS_READY,
    READINESS_PARTIALLY_READY,
    READINESS_PARTIAL_COVERAGE,
    READINESS_RESOURCE_GAP,
    READINESS_PRACTICE_GAP,
    READINESS_PRACTICE_UNVERIFIED,
    READINESS_TIME_UNVERIFIED,
    READINESS_NEEDS_REVIEW,
    READINESS_BROKEN,
]

# ── Practice statuses ─────────────────────────────────────────
PRACTICE_NO_PRACTICE_REQUIRED = "NO_PRACTICE_REQUIRED"
PRACTICE_VERIFIED = "PRACTICE_VERIFIED"
PRACTICE_UNVERIFIED = "PRACTICE_UNVERIFIED"
PRACTICE_GAP = "PRACTICE_GAP"

# ── Time estimate methods ─────────────────────────────────────
ESTIMATE_VIDEO_SEGMENT = "VIDEO_SEGMENT_DURATION"
ESTIMATE_VIDEO_PLUS_BUFFER = "VIDEO_DURATION_PLUS_BUFFER"
ESTIMATE_WORD_COUNT = "DOCUMENT_WORD_COUNT_ESTIMATE"
ESTIMATE_SECTION_LENGTH = "SECTION_LENGTH_ESTIMATE"
ESTIMATE_MEASURED_MANUAL = "MEASURED_MANUAL_ESTIMATE"
ESTIMATE_MULTI_RESOURCE = "MULTI_RESOURCE_TOTAL"
ESTIMATE_STANDARD_FALLBACK = "STANDARD_FALLBACK"

# ── Concept Model ─────────────────────────────────────────────

@dataclass(frozen=True)
class Concept:
    slug: str
    name: str
    importance: str = "REQUIRED"  # REQUIRED or OPTIONAL


@dataclass
class TopicConcepts:
    topic_slug: str
    required: list[Concept] = field(default_factory=list)
    optional: list[Concept] = field(default_factory=list)

    @property
    def all_required_slugs(self) -> set[str]:
        return {c.slug for c in self.required if c.importance == "REQUIRED"}


# ── Canonical 10-topic demonstration registry ──────────────────
# Each topic declares REQUIRED concepts that a valid PRIMARY learning
# path must jointly cover. OPTIONAL concepts are nice-to-have.
# This is the learning contract, not a title match.
# Extended to all 64 Domain 0 topics (Phase 2).

DEMO_CONCEPT_REGISTRY: dict[str, TopicConcepts] = {
    "cf-bits-and-bytes": TopicConcepts(
        topic_slug="cf-bits-and-bytes",
        required=[
            Concept("bit", "bit = binary digit 0/1"),
            Concept("byte", "byte = 8 bits, 256 patterns"),
            Concept("encoding", "meaning from encoding (ASCII/Unicode/RGB)"),
        ],
    ),
    "cf-binary": TopicConcepts(
        topic_slug="cf-binary",
        required=[
            Concept("binary-representation", "binary positional representation"),
            Concept("binary-decimal-conversion", "binary <-> decimal conversion"),
            Concept("place-value", "place value / powers of two"),
        ],
    ),
    "cf-hexadecimal": TopicConcepts(
        topic_slug="cf-hexadecimal",
        required=[
            Concept("hex-representation", "hexadecimal base-16 representation"),
            Concept("hex-binary-grouping", "4-bit nibble grouping binary<->hex"),
            Concept("hex-why", "why hex is preferred over long binary strings"),
        ],
    ),
    "cf-cpu": TopicConcepts(
        topic_slug="cf-cpu",
        required=[
            Concept("cpu-role", "what a CPU does (fetch-decode-execute)"),
            Concept("alu", "ALU role inside CPU"),
            Concept("registers", "registers as CPU's fastest storage"),
            Concept("program-counter", "Program Counter (PC)"),
            Concept("fetch-decode-execute", "fetch -> decode -> execute loop"),
            Concept("ram-interaction", "CPU<->RAM interaction while executing"),
        ],
    ),
    "cf-alu": TopicConcepts(
        topic_slug="cf-alu",
        required=[
            Concept("alu-role", "ALU as integer arithmetic + boolean logic unit"),
            Concept("alu-ops", "add/subtract AND/OR compare"),
            Concept("expression-to-alu", "high-level expression becomes ALU work"),
        ],
    ),
    "cf-registers": TopicConcepts(
        topic_slug="cf-registers",
        required=[
            Concept("registers-role", "registers as CPU's fastest working storage"),
            Concept("registers-count", "few in number"),
            Concept("registers-usage", "hold addresses and intermediate results"),
        ],
    ),
    "cf-ram": TopicConcepts(
        topic_slug="cf-ram",
        required=[
            Concept("ram-volatile", "RAM as volatile working memory"),
            Concept("ram-holds", "RAM holds running code and data"),
            Concept("ram-vs-registers-disk", "contrast with registers and persistent storage"),
        ],
    ),
    "cf-cache": TopicConcepts(
        topic_slug="cf-cache",
        required=[
            Concept("cache-role", "cache as small fast memory between CPU and RAM"),
            Concept("cache-locality", "exploits locality"),
        ],
    ),
    "cf-storage": TopicConcepts(
        topic_slug="cf-storage",
        required=[
            Concept("storage-persistent", "persistent storage vs RAM"),
            Concept("storage-types", "SSD/HDD distinction"),
            Concept("storage-files", "files and installed programs live on storage"),
        ],
    ),
    "cf-instruction-execution": TopicConcepts(
        topic_slug="cf-instruction-execution",
        required=[
            Concept("fetch-decode-execute-loop", "fetch-decode-execute loop"),
            Concept("assignment-to-instructions", "single assignment becomes several instructions"),
            Concept("pc-increment", "PC advances per instruction"),
        ],
        optional=[
            Concept("instruction-types", "instruction categories (optional depth)"),
        ],
    ),
    # ── Extended 54 Domain 0 topics ──
    "cf-machine-code": TopicConcepts(topic_slug="cf-machine-code", required=[Concept("machine-code-binary", "machine code is binary CPU-specific encoding"), Concept("machine-code-arch", "architecture-specific"), Concept("source-to-machine", "source compiled to runnable machine code")]),
    "cf-compiler": TopicConcepts(topic_slug="cf-compiler", required=[Concept("compiler-translate", "compiler translates source to machine code"), Concept("compile-vs-run", "compile time vs run time"), Concept("compiler-tool", "clang/make as example")]),
    "cf-interpreter": TopicConcepts(topic_slug="cf-interpreter", required=[Concept("interpreter-incremental", "interpreter executes incrementally"), Concept("interpreter-vs-compiler", "contrast with compiler"), Concept("interpreter-vm", "bytecode/VM example (Python)")]),
    "cf-program": TopicConcepts(topic_slug="cf-program", required=[Concept("program-artifact", "program is artifact on storage (source/compiled)"), Concept("program-vs-process", "program not yet running process")]),
    "cf-process": TopicConcepts(topic_slug="cf-process", required=[Concept("process-running", "process is OS running instance"), Concept("process-memory-pid", "own memory, open files, PID"), Concept("process-many", "same program many processes")]),
    "cf-kernel": TopicConcepts(topic_slug="cf-kernel", required=[Concept("kernel-privileged", "kernel is privileged program managing hardware"), Concept("kernel-services", "processes/memory/filesystems via syscalls")]),
    "cf-os-processes": TopicConcepts(topic_slug="cf-os-processes", required=[Concept("os-creates", "OS creates/schedules/isolates processes"), Concept("os-identity", "process identity and resources")]),
    "cf-threads": TopicConcepts(topic_slug="cf-threads", required=[Concept("threads-inside-process", "threads are execution paths inside one process"), Concept("threads-share-memory", "share process memory")]),
    "cf-system-calls": TopicConcepts(topic_slug="cf-system-calls", required=[Concept("syscall-privileged", "system call asks kernel for privileged work"), Concept("syscall-examples", "read file / create process as examples")]),
    "cf-os-memory": TopicConcepts(topic_slug="cf-os-memory", required=[Concept("address-space", "each process has address space"), Concept("os-pages-protect", "OS allocates pages and protects regions")]),
    "cf-virtual-memory-basics": TopicConcepts(topic_slug="cf-virtual-memory-basics", required=[Concept("virtual-address-space", "virtual memory per-process address space"), Concept("virtual-to-physical", "virtual pages mapped to physical/swap")]),
    "cf-filesystems": TopicConcepts(topic_slug="cf-filesystems", required=[Concept("filesystem-files-dirs", "filesystem presents files and directories"), Concept("filesystem-paths", "paths name them"), Concept("filesystem-kernel", "kernel enforces structure/permissions")]),
    "cf-os-permissions": TopicConcepts(topic_slug="cf-os-permissions", required=[Concept("unix-permission-bits", "read/write/execute bits"), Concept("kernel-enforces", "kernel enforces permissions")]),
    "cf-os-environment-variables": TopicConcepts(topic_slug="cf-os-environment-variables", required=[Concept("env-key-value", "environment variables are key-value settings"), Concept("env-inherited", "inherited by child processes (PATH/HOME)")]),
    "cf-shell": TopicConcepts(topic_slug="cf-shell", required=[Concept("shell-reads-commands", "shell reads commands and starts programs"), Concept("shell-bash-zsh", "bash/zsh, WSL for Windows")]),
    "cf-command-line": TopicConcepts(topic_slug="cf-command-line", required=[Concept("command-structure", "command name/args/flags stdin/stdout/stderr exit status"), Concept("command-quoting-exit", "quoting, exit codes, conditionals")]),
    "cf-filesystem-navigation": TopicConcepts(topic_slug="cf-filesystem-navigation", required=[Concept("pwd-ls-cd", "pwd, ls, cd as core navigation"), Concept("relative-absolute", "relative vs absolute paths")]),
    "cf-linux-files": TopicConcepts(topic_slug="cf-linux-files", required=[Concept("file-ops", "touch/cp/mv/rm/mkdir/rmdir"), Concept("file-rm-caution", "rm caution"), Concept("file-executable", "executable files and scripts")]),
    "cf-pipes": TopicConcepts(topic_slug="cf-pipes", required=[Concept("pipe-stdout-stdin", "pipe connects stdout to stdin"), Concept("pipe-pipeline", "pipelines as composition")]),
    "cf-redirection": TopicConcepts(topic_slug="cf-redirection", required=[Concept("redirect-operators", ">, >>, 2>, < attach files"), Concept("redirect-separate", "redirect stdout and stderr separately")]),
    "cf-grep": TopicConcepts(topic_slug="cf-grep", required=[Concept("grep-pattern", "grep finds lines matching pattern"), Concept("grep-pipeline", "grep in pipelines (curl|grep)")]),
    "cf-find": TopicConcepts(topic_slug="cf-find", required=[Concept("find-walks", "find walks tree"), Concept("find-combined", "find with globs/xargs/-mtime")]),
    "cf-linux-permissions": TopicConcepts(topic_slug="cf-linux-permissions", required=[Concept("ls-l-chmod", "ls -l, chmod, executable scripts"), Concept("perm-apply", "apply permission concepts at terminal")]),
    "cf-linux-processes": TopicConcepts(topic_slug="cf-linux-processes", required=[Concept("ps-lists", "ps lists processes"), Concept("ps-man", "man ps")]),
    "cf-package-management": TopicConcepts(topic_slug="cf-package-management", required=[Concept("os-package-manager", "OS package managers install/update with deps"), Concept("package-apt-brew", "apt/brew as examples")]),
    "cf-linux-environment-variables": TopicConcepts(topic_slug="cf-linux-environment-variables", required=[Concept("export-printenv-path", "export, printenv, PATH"), Concept("env-customize", "customization via CLI lecture")]),
    "cf-repository": TopicConcepts(topic_slug="cf-repository", required=[Concept("repo-snapshots", "repository stores snapshots in .git"), Concept("repo-init-clone", "git init / clone")]),
    "cf-commits": TopicConcepts(topic_slug="cf-commits", required=[Concept("staging-snapshot", "staging selects what goes into snapshot"), Concept("commits-record", "commits record snapshot"), Concept("staging-why", "why staging exists")]),
    "cf-branches": TopicConcepts(topic_slug="cf-branches", required=[Concept("branch-pointer", "branch is movable pointer to commit"), Concept("branch-parallel", "parallel lines of work")]),
    "cf-merge": TopicConcepts(topic_slug="cf-merge", required=[Concept("merge-join", "merge joins histories"), Concept("merge-ff-vs-commit", "fast-forward vs merge commit")]),
    "cf-rebase": TopicConcepts(topic_slug="cf-rebase", required=[Concept("rebase-replay", "rebase replays commits on new base"), Concept("rebase-not-shared", "do not rebase shared published branches")]),
    "cf-remote": TopicConcepts(topic_slug="cf-remote", required=[Concept("remote-origin", "origin is conventional remote name"), Concept("remote-list", "git remote -v")]),
    "cf-pull-push": TopicConcepts(topic_slug="cf-pull-push", required=[Concept("fetch-download", "fetch downloads"), Concept("pull-fetch-integrate", "pull is fetch+integrate"), Concept("push-sends", "push sends")]),
    "cf-conflicts": TopicConcepts(topic_slug="cf-conflicts", required=[Concept("conflict-same-lines", "conflicts when both edit same lines"), Concept("conflict-markers", "markers <<<<<< ====== >>>>>>"), Concept("conflict-progit", "Pro Git conflict section")]),
    "cf-reset-revert": TopicConcepts(topic_slug="cf-reset-revert", required=[Concept("reset-moves-pointer", "reset moves branch pointer"), Concept("revert-undo-commit", "revert adds undoing commit safe for published"), Concept("restore-files", "restore adjusts files")]),
    "cf-cherry-pick": TopicConcepts(topic_slug="cf-cherry-pick", required=[Concept("cherry-pick-copy", "cherry-pick copies a commit"), Concept("cherry-pick-doc", "git-cherry-pick(1)")]),
    "cf-stash": TopicConcepts(topic_slug="cf-stash", required=[Concept("stash-dirty", "stash saves dirty work and restores clean tree"), Concept("stash-book", "Pro Git stashing")]),
    "cf-github-workflow": TopicConcepts(topic_slug="cf-github-workflow", required=[Concept("github-fork-pr", "fork + PR workflow"), Concept("github-remote-workflow", "clone/branch/push/PR")]),
    "cf-ide": TopicConcepts(topic_slug="cf-ide", required=[Concept("ide-editor-debug", "IDE as editor + run/debug + project tools"), Concept("ide-vscode-example", "VS Code as example")]),
    "cf-dev-compiler": TopicConcepts(topic_slug="cf-dev-compiler", required=[Concept("dev-compiler-toolchain", "compiler toolchain compile-time vs run-time"), Concept("compiler-make-example", "make/clang example")]),
    "cf-debugger": TopicConcepts(topic_slug="cf-debugger", required=[Concept("debugger-breakpoints", "debugger breakpoints and inspection"), Concept("debugger-unix-gdb", "Unix/gdb strategies")]),
    "cf-formatter": TopicConcepts(topic_slug="cf-formatter", required=[Concept("formatter-style", "formatter as automatic style enforcer")]),
    "cf-linter": TopicConcepts(topic_slug="cf-linter", required=[Concept("linter-static-hint", "linter as static hint before execution")]),
    "cf-dev-package-manager": TopicConcepts(topic_slug="cf-dev-package-manager", required=[Concept("package-manager-language-vs-os", "language vs OS package managers"), Concept("package-manager-pip", "pip as example")]),
    "cf-build-system": TopicConcepts(topic_slug="cf-build-system", required=[Concept("build-repeatable", "build as repeatable compile/test/package pipeline")]),
    "cf-dependency-management": TopicConcepts(topic_slug="cf-dependency-management", required=[Concept("dependency-direct-transitive", "direct vs transitive dependencies and risks")]),
    "cf-problem-decomposition": TopicConcepts(topic_slug="cf-problem-decomposition", required=[Concept("decomposition-break-down", "break down problem into subproblems"), Concept("decomposition-steps", "steps and interfaces")]),
    "cf-pseudocode": TopicConcepts(topic_slug="cf-pseudocode", required=[Concept("pseudocode-plan", "pseudocode as plan before code"), Concept("pseudocode-readable", "readable steps not syntax")]),
    "cf-algorithms": TopicConcepts(topic_slug="cf-algorithms", required=[Concept("algorithm-steps", "algorithm as precise steps"), Concept("algorithm-correctness", "correctness and generality")]),
    "cf-dry-runs": TopicConcepts(topic_slug="cf-dry-runs", required=[Concept("dry-run-trace", "dry run as manual trace before trusting code"), Concept("dry-run-table", "step table with variables")]),
    "cf-edge-cases": TopicConcepts(topic_slug="cf-edge-cases", required=[Concept("edge-unusual-valid", "edge cases as unusual but valid inputs"), Concept("edge-empty-boundary", "empty and boundary inputs")]),
    "cf-debugging-thinking": TopicConcepts(topic_slug="cf-debugging-thinking", required=[Concept("debugging-systematic", "systematic debugging: reproduce, isolate, fix"), Concept("debugging-logic", "logic: hypothesis and check")]),
    "cf-time-complexity-intro": TopicConcepts(topic_slug="cf-time-complexity-intro", required=[Concept("time-complexity-bigO", "time complexity as growth, Big-O"), Concept("time-common", "common classes O(1) O(n) O(n log n)"), Concept("time-counting", "counting operations")]),
    "cf-space-complexity-intro": TopicConcepts(topic_slug="cf-space-complexity-intro", required=[Concept("space-complexity", "space complexity auxiliary vs input"), Concept("space-O-classes", "O(1) vs O(n)")]),
}

# ── Per-resource coverage manifest (resource-specific verification data) ─
# Each key is a CurriculumResource.slug. Value is the list of concept slugs
# that this *specific* resource was verified to teach. This is NOT derived
# from topic.required — it is stored per resource and can differ per resource.
# A topic is READY only when union of its ordered PRIMARY resources covers
# topic.required.

RESOURCE_COVERAGE_MANIFEST: dict[str, list[str]] = {
    # Computer fundamentals - CS50 lecture L0 is MULTI_TOPIC 1h55m, segment ~00:10:00-00:35:00 covers representation; treat as MULTI_TOPIC with timestamp
    "cf-bits-and-bytes-lecture0": ["bit", "byte", "encoding"],
    "cf-binary-lecture0": ["binary-representation", "binary-decimal-conversion", "place-value"],
    "cf-hexadecimal-lecture0": ["hex-representation", "hex-binary-grouping", "hex-why"],
    # Honest per-resource verification (webfetch 2026-08-22):
    # cf-cpu-primary GFG CPU: verified sections "CPU Components → ALU and Registers" + "Fetch-Decode-Execute-Store" + RAM reference. No Program Counter section → PARTIAL 5/6.
    "cf-cpu-primary": ["cpu-role", "alu", "registers", "fetch-decode-execute", "ram-interaction"],
    "cf-cpu-pc-supplement": ["program-counter"],
    "cf-alu-primary": ["alu-role", "alu-ops"],
    "cf-alu-expression-supplement": ["expression-to-alu"],
    "cf-registers-primary": ["registers-role", "registers-count", "registers-usage"],
    "cf-ram-primary": ["ram-volatile", "ram-holds", "ram-vs-registers-disk"],
    "cf-cache-primary": ["cache-role"],
    "cf-cache-locality-supplement": ["cache-locality"],
    "cf-storage-primary": ["storage-persistent", "storage-types", "storage-files"],
    "cf-instruction-execution-primary": ["fetch-decode-execute-loop", "assignment-to-instructions"],
    "cf-instruction-execution-pc": ["pc-increment"],
    "cf-machine-code-primary": ["machine-code-binary", "machine-code-arch", "source-to-machine"],
    "cf-compiler-primary": ["compiler-translate", "compile-vs-run", "compiler-tool"],
    "cf-interpreter-primary": ["interpreter-incremental", "interpreter-vs-compiler", "interpreter-vm"],
    "cf-program-primary": ["program-artifact", "program-vs-process"],
    "cf-process-primary": ["process-running", "process-memory-pid", "process-many"],
    "cf-kernel-primary": ["kernel-privileged", "kernel-services"],
    "cf-os-processes-primary": ["os-creates", "os-identity"],
    "cf-threads-primary": ["threads-inside-process", "threads-share-memory"],
    "cf-system-calls-primary": ["syscall-privileged", "syscall-examples"],
    "cf-os-memory-primary": ["address-space", "os-pages-protect"],
    "cf-virtual-memory-primary": ["virtual-address-space", "virtual-to-physical"],
    "cf-filesystems-primary": ["filesystem-files-dirs", "filesystem-paths", "filesystem-kernel"],
    "cf-os-permissions-primary": ["unix-permission-bits", "kernel-enforces"],
    "cf-os-environment-variables-primary": ["env-key-value", "env-inherited"],
    "cf-shell-primary": ["shell-reads-commands", "shell-bash-zsh"],
    "cf-command-line-primary": ["command-structure", "command-quoting-exit"],
    "cf-filesystem-navigation-primary": ["pwd-ls-cd", "relative-absolute"],
    "cf-linux-files-primary": ["file-ops", "file-rm-caution", "file-executable"],
    "cf-pipes-primary": ["pipe-stdout-stdin", "pipe-pipeline"],
    "cf-redirection-primary": ["redirect-operators", "redirect-separate"],
    "cf-grep-primary": ["grep-pattern", "grep-pipeline"],
    "cf-find-primary": ["find-walks", "find-combined"],
    "cf-linux-permissions-primary": ["ls-l-chmod", "perm-apply"],
    "cf-linux-processes-primary": ["ps-lists", "ps-man"],
    "cf-package-management-primary": ["os-package-manager", "package-apt-brew"],
    "cf-linux-environment-variables-primary": ["export-printenv-path", "env-customize"],
    "cf-repository-primary": ["repo-snapshots", "repo-init-clone"],
    "cf-commits-primary": ["staging-snapshot", "commits-record", "staging-why"],
    "cf-branches-primary": ["branch-pointer", "branch-parallel"],
    "cf-merge-primary": ["merge-join", "merge-ff-vs-commit"],
    "cf-rebase-primary": ["rebase-replay", "rebase-not-shared"],
    "cf-remote-primary": ["remote-origin", "remote-list"],
    "cf-pull-push-primary": ["fetch-download", "pull-fetch-integrate", "push-sends"],
    "cf-conflicts-primary": ["conflict-same-lines", "conflict-markers", "conflict-progit"],
    "cf-reset-revert-primary": ["reset-moves-pointer", "revert-undo-commit", "restore-files"],
    "cf-cherry-pick-primary": ["cherry-pick-copy", "cherry-pick-doc"],
    "cf-stash-primary": ["stash-dirty", "stash-book"],
    "cf-github-workflow-primary": ["github-fork-pr", "github-remote-workflow"],
    "cf-ide-primary": ["ide-editor-debug", "ide-vscode-example"],
    "cf-dev-compiler-primary": ["dev-compiler-toolchain", "compiler-make-example"],
    "cf-debugger-primary": ["debugger-breakpoints", "debugger-unix-gdb"],
    "cf-formatter-primary": ["formatter-style"],
    "cf-linter-primary": ["linter-static-hint"],
    "cf-dev-package-manager-primary": ["package-manager-language-vs-os", "package-manager-pip"],
    "cf-build-system-primary": ["build-repeatable"],
    "cf-dependency-management-primary": ["dependency-direct-transitive"],
    "cf-os-memory-primary-ostep": [],
    "cf-problem-decomposition-primary": ["decomposition-break-down", "decomposition-steps"],
    "cf-pseudocode-primary": ["pseudocode-plan", "pseudocode-readable"],
    "cf-algorithms-primary": ["algorithm-steps", "algorithm-correctness"],
    "cf-dry-runs-primary": ["dry-run-trace", "dry-run-table"],
    "cf-edge-cases-primary": ["edge-unusual-valid", "edge-empty-boundary"],
    "cf-debugging-thinking-primary": ["debugging-systematic", "debugging-logic"],
    "cf-time-complexity-intro-primary": ["time-complexity-bigO", "time-common", "time-counting"],
    "cf-space-complexity-intro-primary": ["space-complexity", "space-O-classes"],
}

# Per-resource estimated minutes + confidence (resource duration + pause/note buffer)
# Confidence: HIGH = measured video duration or known doc length, MEDIUM = reading estimate, LOW = fallback
# For MULTI_TOPIC videos, minutes is segment only, not full 115m lecture
RESOURCE_TIME_MANIFEST: dict[str, tuple[int, str]] = {
    "cf-bits-and-bytes-lecture0": (12, "HIGH"),  # MULTI_TOPIC: CS50 L0 00:10:00-00:22:00 representation segment ~12m + 8m pause/note = 20m total, but segment only 12m
    "cf-binary-lecture0": (12, "HIGH"),
    "cf-hexadecimal-lecture0": (12, "HIGH"),
    "cf-cpu-primary": (18, "MEDIUM"),  # MANUAL_READING_ESTIMATE ~1200 words
    "cf-alu-primary": (18, "MEDIUM"),
    "cf-registers-primary": (18, "MEDIUM"),
    "cf-ram-primary": (18, "MEDIUM"),
    "cf-cache-primary": (18, "MEDIUM"),
    "cf-storage-primary": (18, "MEDIUM"),
    "cf-instruction-execution-primary": (18, "MEDIUM"),
    "cf-machine-code-primary": (18, "MEDIUM"),
    "cf-compiler-primary": (18, "MEDIUM"),
    "cf-interpreter-primary": (18, "MEDIUM"),
    "cf-program-primary": (18, "MEDIUM"),
    "cf-process-primary": (18, "MEDIUM"),
    "cf-kernel-primary": (18, "MEDIUM"),
    "cf-os-processes-primary": (18, "MEDIUM"),
    "cf-threads-primary": (18, "MEDIUM"),
    "cf-system-calls-primary": (18, "MEDIUM"),
    "cf-os-memory-primary": (18, "MEDIUM"),
    "cf-virtual-memory-primary": (18, "MEDIUM"),
    "cf-filesystems-primary": (18, "MEDIUM"),
    "cf-os-permissions-primary": (18, "MEDIUM"),
    "cf-os-environment-variables-primary": (18, "MEDIUM"),
    "cf-shell-primary": (30, "MEDIUM"),  # MIT lecture page ~30m
    "cf-command-line-primary": (30, "MEDIUM"),
    "cf-filesystem-navigation-primary": (30, "MEDIUM"),
    "cf-linux-files-primary": (30, "MEDIUM"),
    "cf-pipes-primary": (30, "MEDIUM"),
    "cf-redirection-primary": (30, "MEDIUM"),
    "cf-grep-primary": (30, "MEDIUM"),
    "cf-find-primary": (30, "MEDIUM"),
    "cf-linux-permissions-primary": (30, "MEDIUM"),
    "cf-linux-processes-primary": (30, "MEDIUM"),
    "cf-package-management-primary": (30, "MEDIUM"),
    "cf-linux-environment-variables-primary": (30, "MEDIUM"),
    "cf-repository-primary": (25, "MEDIUM"),  # Pro Git page ~1500 words
    "cf-commits-primary": (25, "MEDIUM"),
    "cf-branches-primary": (25, "MEDIUM"),
    "cf-merge-primary": (25, "MEDIUM"),
    "cf-rebase-primary": (25, "MEDIUM"),
    "cf-remote-primary": (25, "MEDIUM"),
    "cf-pull-push-primary": (25, "MEDIUM"),
    "cf-conflicts-primary": (25, "MEDIUM"),
    "cf-reset-revert-primary": (25, "MEDIUM"),
    "cf-cherry-pick-primary": (25, "MEDIUM"),
    "cf-stash-primary": (25, "MEDIUM"),
    "cf-github-workflow-primary": (25, "MEDIUM"),
    "cf-ide-primary": (18, "MEDIUM"),
    "cf-dev-compiler-primary": (18, "MEDIUM"),
    "cf-debugger-primary": (18, "MEDIUM"),
    "cf-formatter-primary": (18, "MEDIUM"),
    "cf-linter-primary": (18, "MEDIUM"),
    "cf-dev-package-manager-primary": (18, "MEDIUM"),
    "cf-build-system-primary": (18, "MEDIUM"),
    "cf-dependency-management-primary": (18, "MEDIUM"),
    "cf-problem-decomposition-primary": (20, "LOW"),
    "cf-pseudocode-primary": (20, "LOW"),
    "cf-algorithms-primary": (20, "LOW"),
    "cf-dry-runs-primary": (18, "MEDIUM"),
    "cf-edge-cases-primary": (18, "MEDIUM"),
    "cf-debugging-thinking-primary": (20, "LOW"),
    "cf-time-complexity-intro-primary": (20, "MEDIUM"),
    "cf-space-complexity-intro-primary": (18, "MEDIUM"),
    # Collections
    "cf-bits-and-bytes-primary": (15, "LOW"),
    "cf-binary-primary": (15, "LOW"),
    "cf-hexadecimal-primary": (15, "LOW"),
}

# Alias for backward compatibility
DOMAIN0_CONCEPT_REGISTRY = DEMO_CONCEPT_REGISTRY


def get_required_concepts(topic_slug: str) -> Optional[TopicConcepts]:
    """Unified contract lookup (Domain 0 + generated contracts)."""
    try:
        from app.content.concept_contracts import get_topic_concepts

        return get_topic_concepts(topic_slug)
    except Exception:  # noqa: BLE001
        return DEMO_CONCEPT_REGISTRY.get(topic_slug)


# ── Time helpers ──────────────────────────────────────────────

def realistic_time_estimate(
    resources: list[dict[str, Any]],
    practice_minutes: int = 0,
    implementation_minutes: int = 0,
) -> int:
    """Sum ordered resource minutes + practice + implementation with realistic overhead."""
    total = 0
    for r in resources:
        mins = r.get("estimated_minutes")
        if mins is None:
            # fallback: duration field (float hours) or 20 min default
            dur = r.get("duration")
            if dur is not None:
                mins = int(float(dur) * 60)
            else:
                mins = 20
        total += int(mins)
    # Add reading/exploration overhead: 25% of resource time already baked into estimates,
    # but if resource lacks overhead we add minimal pause time here.
    # For this infra, keep it simple: resources + practice + implementation.
    total += practice_minutes + implementation_minutes
    return total


def canonical_role(role: Optional[str]) -> Optional[str]:
    if role is None:
        return None
    return ROLE_ALIASES.get(role.upper(), role)


def ensure_verification_columns(engine) -> dict[str, bool]:
    """Idempotently add additive columns to curriculum_resources if missing.

    Does not delete or rename anything. Safe to call repeatedly.
    Returns dict of column -> created?
    """
    from sqlalchemy import text

    cols = {
        "estimated_minutes": "INTEGER",
        "required_concepts_covered": "JSON",
        "exactness": "VARCHAR(20)",
        "notes": "TEXT",
        "estimate_confidence": "VARCHAR(10)",
        "estimate_method": "VARCHAR(40)",
        "verification_evidence": "TEXT",
        "last_verified_at": "VARCHAR(40)",
    }
    result: dict[str, bool] = {}
    with engine.begin() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(curriculum_resources)")).fetchall()}
        for col, coltype in cols.items():
            if col in existing:
                result[col] = False
            else:
                # SQLite: JSON stored as TEXT/JSON; use TEXT for compatibility
                sql_type = "TEXT" if coltype == "JSON" else coltype
                conn.execute(text(f"ALTER TABLE curriculum_resources ADD COLUMN {col} {sql_type}"))
                result[col] = True
    return result
