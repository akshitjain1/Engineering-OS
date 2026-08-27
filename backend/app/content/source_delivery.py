"""Additive source-delivery mapping. Does not edit YAML, graph, XP, or mastery.

Rebuilt around the strict learning contract (2026-08-22):
- Every PRIMARY must teach the topic's required concepts before practice.
- No project-spec as PRIMARY, no broad course hub for a narrow topic.
- Curated pool prioritised: GFG for core CS, W3Schools/MDN/freeCodeCamp for web,
  OSTEP/MIT Missing Semester for deep OS/tooling, CS50 for representation.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from app.content.resources import metadata_from_spec
from app.content.final_resource_repairs import apply_final_resource_repairs
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic

CS50_L0 = "https://www.youtube.com/watch?v=UuIEbpQms8o"
CS50_L1 = "https://www.youtube.com/watch?v=SlqjA04_dpk"
N2T_P2 = "https://www.nand2tetris.org/project02"
N2T_P3 = "https://www.nand2tetris.org/project03"
N2T_P4 = "https://www.nand2tetris.org/project04"
N2T_P5 = "https://www.nand2tetris.org/project05"
OCW_6004 = "https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/"
OCW_6006 = "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/"
OSTEP_INTRO = "https://pages.cs.wisc.edu/~remzi/OSTEP/intro.pdf"
OSTEP_SYSCALL = "https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf"
OSTEP_THREADS = "https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf"
OSTEP_VM = "https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf"
OSTEP_FILES = "https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf"
PY_INTERP = "https://docs.python.org/3/tutorial/interpreter.html"
MIT_SHELL = "https://missing.csail.mit.edu/2026/course-shell/"
MIT_DBG = "https://missing.csail.mit.edu/2026/debugging-profiling/"
MIT_DEV = "https://missing.csail.mit.edu/2026/development-environment/"
MIT_QUALITY = "https://missing.csail.mit.edu/2026/code-quality/"
VSCODE = "https://code.visualstudio.com/docs"
PIP = "https://pip.pypa.io/en/stable/"
PIP_DEP = "https://pip.pypa.io/en/stable/topics/dependency-resolution/"
JLS17 = "https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html"

# Curated pool — exact pages (not hubs) for the V3 contract.
# Verified live 2026-08-22 via webfetch: CPU and RAM work, ALU/Registers/ICYCLE were 404 and replaced with live COA paths.
GFG_CPU = "https://www.geeksforgeeks.org/central-processing-unit-cpu/"
GFG_ALU = "https://www.geeksforgeeks.org/computer-organization-architecture/introduction-of-alu-and-data-path/"
GFG_REG = "https://www.geeksforgeeks.org/computer-organization-architecture/different-classes-of-cpu-registers/"
GFG_RAM = "https://www.geeksforgeeks.org/random-access-memory-ram/"
GFG_CACHE = "https://www.geeksforgeeks.org/cache-memory-in-computer-organization/"
GFG_STORAGE = "https://www.geeksforgeeks.org/storage-devices/"
GFG_ICYCLE = "https://www.geeksforgeeks.org/computer-organization-architecture/different-instruction-cycles/"
GFG_MACHINE = "https://www.geeksforgeeks.org/machine-language-in-computer-organization/"
GFG_COMPILER = "https://www.geeksforgeeks.org/introduction-of-compiler-design/"
GFG_INTERPRETER = "https://www.geeksforgeeks.org/interpreter-in-compiler-design/"
GFG_PROGRAM = "https://www.geeksforgeeks.org/program-and-its-types-in-operating-system/"
GFG_PROCESS = "https://www.geeksforgeeks.org/process-in-operating-system/"
GFG_KERNEL = "https://www.geeksforgeeks.org/kernel-in-operating-system/"
GFG_THREADS = "https://www.geeksforgeeks.org/thread-in-operating-system/"
GFG_SYSCALL = "https://www.geeksforgeeks.org/system-calls-in-operating-system/"
GFG_MEM = "https://www.geeksforgeeks.org/memory-management-in-operating-system/"
GFG_VM = "https://www.geeksforgeeks.org/virtual-memory-in-operating-system/"
GFG_FILESYS = "https://www.geeksforgeeks.org/file-system-in-operating-system/"
GFG_PERM = "https://www.geeksforgeeks.org/file-permissions-in-linux/"
GFG_IDE = "https://www.geeksforgeeks.org/introduction-to-integrated-development-environment/"
GFG_DEBUG = "https://www.geeksforgeeks.org/debugging-in-software-engineering/"
GFG_FORMAT = "https://www.geeksforgeeks.org/code-formatting-in-software-engineering/"
GFG_LINT = "https://www.geeksforgeeks.org/linting-in-software-development/"
GFG_PKG = "https://www.geeksforgeeks.org/package-manager-in-operating-system/"
GFG_BUILD = "https://www.geeksforgeeks.org/build-systems-in-software-engineering/"
GFG_COMP_INTRO = "https://www.geeksforgeeks.org/introduction-to-compilers/"
W3_GIT = "https://www.w3schools.com/git/"
MDN_HTTP = "https://developer.mozilla.org/en-US/docs/Web/HTTP"


def _p(
    topic: str,
    slug: str,
    title: str,
    url: str,
    provider: str,
    *,
    role: str = "PRIMARY",
    rtype: str = "documentation",
    order: int = 0,
    lecture: Optional[str] = None,
    section: Optional[str] = None,
    description: Optional[str] = None,
) -> dict[str, Any]:
    return {
        "topic_slug": topic,
        "slug": slug,
        "title": title,
        "url": url,
        "provider": provider,
        "role": role,
        "resource_type": rtype,
        "order": order,
        "lecture": lecture,
        "section": section,
        "description": description,
    }


# Additive patches. Existing resource slugs are updated in place; new slugs are inserted.
# CPU is the reference implementation — PRIMARY is GFG CPU fundamentals, not Nand2Tetris
# Project 5. N2T projects remain available as DEEP_DIVE for BUILD after the learner
# has completed the conceptual lesson (they are exercises, not the lesson).
SOURCE_PATCHES: list[dict[str, Any]] = [
    _p(
        "cf-bits-and-bytes",
        "cf-bits-and-bytes-lecture0",
        "CS50x 2026 — Lecture 0 (Scratch)",
        CS50_L0,
        "CS50",
        rtype="youtube_video",
        order=-1,
        lecture="Lecture 0",
        description="Official CS50 lecture (channel CS50). Representation (unary/binary/ASCII) is part of this lecture; the lecture also covers Scratch. No timestamp is stored because none was verified.",
    ),
    _p(
        "cf-binary",
        "cf-binary-lecture0",
        "CS50x 2026 — Lecture 0 (Scratch)",
        CS50_L0,
        "CS50",
        rtype="youtube_video",
        order=-1,
        lecture="Lecture 0",
        description="Official CS50 lecture. Binary/decimal representation is in this lecture; it is not only about binary.",
    ),
    _p(
        "cf-hexadecimal",
        "cf-hexadecimal-lecture0",
        "CS50x 2026 — Lecture 0 (Scratch)",
        CS50_L0,
        "CS50",
        rtype="youtube_video",
        order=-1,
        lecture="Lecture 0",
        description="Official CS50 lecture covering positional representation among other Week 0 topics.",
    ),
    # --- CPU learning contract (reference implementation) ---
    _p(
        "cf-cpu",
        "cf-cpu-primary",
        "GFG — Central Processing Unit (CPU)",
        GFG_CPU,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY learn: what a CPU is, ALU + registers + PC, fetch-decode-execute, and memory interaction. Covers required concepts before any Hack assembly or practice.",
    ),
    _p(
        "cf-cpu",
        "cf-cpu-ref-cs50",
        "CS50x — Source to machine code (reference)",
        "https://cs50.harvard.edu/x/weeks/1/",
        "CS50x",
        role="REFERENCE",
        rtype="documentation",
        order=1,
        description="Reference: source → machine code that the CPU eventually runs. Not a CPU microarchitecture lecture.",
    ),
    _p(
        "cf-cpu",
        "cf-cpu-n2t",
        "Nand2Tetris Project 5 — Computer Architecture (optional build)",
        N2T_P5,
        "Nand2Tetris",
        role="DEEP_DIVE",
        rtype="documentation",
        order=2,
        description="Optional BUILD after CPU fundamentals: Hack CPU construction. Do not use as PRIMARY before learning ALU/registers/PC.",
    ),
    _p(
        "cf-alu",
        "cf-alu-primary",
        "GFG — Arithmetic Logic Unit (ALU)",
        GFG_ALU,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: ALU purpose, integer arithmetic and boolean operations, how expressions become ALU work.",
    ),
    _p(
        "cf-alu",
        "cf-alu-n2t",
        "Nand2Tetris Project 2 — Boolean Arithmetic (optional build)",
        N2T_P2,
        "Nand2Tetris",
        role="DEEP_DIVE",
        rtype="documentation",
        order=1,
        description="Optional BUILD: implement a simplified ALU after the conceptual lesson.",
    ),
    _p(
        "cf-registers",
        "cf-registers-primary",
        "GFG — Registers in Computer Organization",
        GFG_REG,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: registers as the CPU's fastest working storage, few in number, hold addresses and intermediate results.",
    ),
    _p(
        "cf-registers",
        "cf-registers-n2t",
        "Nand2Tetris Project 3 — Memory (optional build)",
        N2T_P3,
        "Nand2Tetris",
        role="DEEP_DIVE",
        rtype="documentation",
        order=1,
        description="Optional BUILD: Hack registers/RAM construction after the conceptual lesson.",
    ),
    _p(
        "cf-ram",
        "cf-ram-primary",
        "GFG — Random Access Memory (RAM)",
        GFG_RAM,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: RAM as volatile working memory holding running code/data, contrasted with registers and disk.",
    ),
    _p(
        "cf-ram",
        "cf-ram-n2t",
        "Nand2Tetris Project 3 — Memory (optional build)",
        N2T_P3,
        "Nand2Tetris",
        role="DEEP_DIVE",
        rtype="documentation",
        order=1,
        description="Optional BUILD: Hack RAM after the conceptual lesson.",
    ),
    _p(
        "cf-cache",
        "cf-cache-primary",
        "GFG — Cache Memory in Computer Organization",
        GFG_CACHE,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: cache as small fast memory exploiting locality between CPU and RAM.",
    ),
    _p(
        "cf-storage",
        "cf-storage-primary",
        "GFG — Storage Devices (persistent storage)",
        GFG_STORAGE,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: persistent storage vs RAM, SSD/HDD, files and installed programs on storage.",
    ),
    _p(
        "cf-instruction-execution",
        "cf-instruction-execution-primary",
        "GFG — Instruction Cycle (Fetch-Decode-Execute)",
        GFG_ICYCLE,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: fetch-decode-execute loop, how a single assignment becomes several instructions.",
    ),
    _p(
        "cf-machine-code",
        "cf-machine-code-primary",
        "GFG — Machine Language",
        GFG_MACHINE,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: machine code as binary CPU-family-specific instructions, architecture-specific.",
    ),
    _p(
        "cf-machine-code",
        "cf-machine-code-lecture1",
        "CS50x 2026 — Lecture 1 (C)",
        CS50_L1,
        "CS50",
        role="REFERENCE",
        rtype="youtube_video",
        order=1,
        lecture="Lecture 1",
        description="Reference: source vs machine code in lecture context.",
    ),
    _p(
        "cf-compiler",
        "cf-compiler-primary",
        "GFG — Introduction of Compiler Design",
        GFG_COMPILER,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: compiler translates source to machine code before run, compile-time vs run-time.",
    ),
    _p(
        "cf-compiler",
        "cf-compiler-lecture1",
        "CS50x 2026 — Lecture 1 (C)",
        CS50_L1,
        "CS50",
        role="REFERENCE",
        rtype="youtube_video",
        order=1,
        lecture="Lecture 1",
        description="Reference: compilation of C source to machine code.",
    ),
    _p(
        "cf-interpreter",
        "cf-interpreter-primary",
        "GFG — Interpreter in Compiler Design",
        GFG_INTERPRETER,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: interpreter executes source directly, contrasted with compiler translation.",
    ),
    _p(
        "cf-interpreter",
        "cf-interpreter-python",
        "Python docs — Using the Python Interpreter",
        PY_INTERP,
        "Python Software Foundation",
        role="REFERENCE",
        rtype="documentation",
        order=1,
        description="Reference: CPython interpreter usage.",
    ),
    _p(
        "cf-program",
        "cf-program-primary",
        "GFG — Program and its Types in Operating System",
        GFG_PROGRAM,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: program as a set of instructions stored on disk before execution.",
    ),
    _p(
        "cf-program",
        "cf-program-lecture1",
        "CS50x 2026 — Lecture 1 (C)",
        CS50_L1,
        "CS50",
        role="REFERENCE",
        rtype="youtube_video",
        order=1,
        lecture="Lecture 1",
        description="Reference: source, compile, and run a program.",
    ),
    _p(
        "cf-process",
        "cf-process-primary",
        "GFG — Process in Operating System",
        GFG_PROCESS,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: process as a running program with code, data, and execution context.",
    ),
    _p("cf-kernel", "cf-kernel-primary", "GFG — Kernel in Operating System", GFG_KERNEL, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: kernel as the core OS component managing hardware and processes."),
    _p("cf-kernel", "cf-kernel-ostep", "OSTEP — Introduction to Operating Systems", OSTEP_INTRO, "OSTEP", role="DEEP_DIVE", rtype="documentation", order=1, description="Deep dive: OSTEP introduction."),
    _p("cf-os-processes", "cf-os-processes-primary", "GFG — Process Management in Operating System", GFG_PROCESS, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: OS process management, states, and scheduling."),
    _p("cf-threads", "cf-threads-primary", "GFG — Threads in Operating System", GFG_THREADS, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: thread as a lightweight process, sharing resources within a process."),
    _p("cf-threads", "cf-threads-ostep", "OSTEP — Thread API / threads intro", OSTEP_THREADS, "OSTEP", role="DEEP_DIVE", rtype="documentation", order=1, description="Deep dive: OSTEP thread introduction."),
    _p("cf-system-calls", "cf-system-calls-primary", "GFG — System Calls in Operating System", GFG_SYSCALL, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: system calls as the interface between user programs and the kernel."),
    _p("cf-system-calls", "cf-system-calls-ostep", "OSTEP — Limited Direct Execution (traps / syscalls)", OSTEP_SYSCALL, "OSTEP", role="DEEP_DIVE", rtype="documentation", order=1, description="Deep dive: traps and syscall mechanisms."),
    _p("cf-os-memory", "cf-os-memory-primary", "GFG — Memory Management in Operating System", GFG_MEM, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: OS memory management, allocation, and protection."),
    _p("cf-os-memory", "cf-os-memory-ostep", "OSTEP — Address Spaces", OSTEP_VM, "OSTEP", role="DEEP_DIVE", rtype="documentation", order=1, description="Deep dive: OSTEP address spaces."),
    _p("cf-virtual-memory-basics", "cf-virtual-memory-primary", "GFG — Virtual Memory in Operating System", GFG_VM, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: virtual memory abstraction, paging, and benefits."),
    _p("cf-virtual-memory-basics", "cf-virtual-memory-ostep", "OSTEP — Address Spaces", OSTEP_VM, "OSTEP", role="DEEP_DIVE", rtype="documentation", order=1, description="Deep dive: OSTEP address spaces."),
    _p("cf-filesystems", "cf-filesystems-primary", "GFG — File System in Operating System", GFG_FILESYS, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: filesystems, files and directories on persistent storage."),
    _p("cf-os-permissions", "cf-os-permissions-primary", "GFG — File Permissions in Linux", GFG_PERM, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: permissions as OS access control."),
    _p("cf-process", "cf-process-ostep", "OSTEP — Introduction (process appendix)", OSTEP_INTRO, "OSTEP", role="DEEP_DIVE", rtype="documentation", order=1, description="Deep dive for process context."),
    _p("cf-shell", "cf-shell-primary", "MIT Missing Semester — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", rtype="documentation", order=0, description="PRIMARY: shell fundamentals as the developer command interface."),
    _p("cf-ide", "cf-ide-primary", "GFG — Introduction to Integrated Development Environment", GFG_IDE, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: IDE as editor + run/debug + project tools."),
    _p("cf-ide", "cf-ide-vscode", "Visual Studio Code documentation", VSCODE, "Microsoft", role="REFERENCE", rtype="documentation", order=1, description="Reference: VS Code docs."),
    _p(
        "cf-dev-compiler",
        "cf-dev-compiler-primary",
        "GFG — Introduction to Compilers",
        GFG_COMP_INTRO,
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: compiler toolchain concept applied to the developer environment.",
    ),
    _p(
        "cf-dev-compiler",
        "cf-dev-compiler-lecture1",
        "CS50x 2026 — Lecture 1 (C)",
        CS50_L1,
        "CS50",
        role="REFERENCE",
        rtype="youtube_video",
        lecture="Lecture 1",
        order=1,
        description="Reference: compiler toolchain in CS50 context.",
    ),
    _p("cf-debugger", "cf-debugger-primary", "GFG — Debugging in Software Engineering", GFG_DEBUG, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: debugger use, breakpoints, and inspection."),
    _p("cf-debugger", "cf-debugger-mit", "MIT Missing Semester — Debugging and Profiling", MIT_DBG, "MIT Missing Semester 2026", role="REFERENCE", rtype="documentation", order=1, description="Reference: Unix/gdb-oriented debugging strategies."),
    _p("cf-formatter", "cf-formatter-primary", "GFG — Code Formatting in Software Engineering", GFG_FORMAT, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: formatter as automatic style enforcer."),
    _p("cf-formatter", "cf-formatter-mit", "MIT Missing Semester — Code Quality", MIT_QUALITY, "MIT Missing Semester 2026", role="REFERENCE", rtype="documentation", order=1, description="Reference: formatter and code quality."),
    _p("cf-linter", "cf-linter-primary", "GFG — Linting in Software Development", GFG_LINT, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: linter as static hint before execution."),
    _p("cf-linter", "cf-linter-mit", "MIT Missing Semester — Code Quality", MIT_QUALITY, "MIT Missing Semester 2026", role="REFERENCE", rtype="documentation", order=1, description="Reference: linting in workflow."),
    _p("cf-dev-package-manager", "cf-dev-package-manager-primary", "GFG — Package Manager in Operating System", GFG_PKG, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: language vs OS package managers."),
    _p("cf-dev-package-manager", "cf-dev-package-manager-pip", "pip documentation", PIP, "PyPA", role="REFERENCE", rtype="documentation", order=1, description="Reference: pip docs."),
    _p("cf-build-system", "cf-build-system-primary", "GFG — Build Systems in Software Engineering", GFG_BUILD, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: build tool as repeatable compile/test/package pipeline."),
    _p("cf-build-system", "cf-build-system-mit", "MIT Missing Semester — Development Environment", MIT_DEV, "MIT Missing Semester 2026", role="REFERENCE", rtype="documentation", order=1, description="Reference: build and environment tooling."),
    _p("cf-dependency-management", "cf-dependency-primary", "GFG — Dependency Management", GFG_PKG, "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: direct vs transitive dependencies and risks."),
    _p("cf-dependency-management", "cf-dependency-pip", "pip — Dependency Resolution", PIP_DEP, "PyPA", role="REFERENCE", rtype="documentation", order=1, description="Reference: pip dependency resolution."),
    _p(
        "cf-os-environment-variables",
        "cf-os-env-primary",
        "GFG — Environment Variables in Operating System",
        "https://www.geeksforgeeks.org/environment-variables-in-operating-system/",
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: environment variables as per-process configuration.",
    ),
    _p("cf-dry-runs", "cf-dry-runs-primary", "GFG — Dry Run in Software Engineering", "https://www.geeksforgeeks.org/dry-run-in-software-engineering/", "GeeksforGeeks", rtype="documentation", order=0, description="PRIMARY: dry run as manual trace before trusting code."),
    _p("cf-dry-runs", "cf-dry-runs-mit", "MIT Missing Semester — Code Quality", MIT_QUALITY, "MIT Missing Semester 2026", role="REFERENCE", rtype="documentation", order=1, description="Reference: quality and manual review."),
    _p(
        "cf-space-complexity-intro",
        "cf-space-complexity-primary",
        "GFG — Space Complexity",
        "https://www.geeksforgeeks.org/g-fact-86/",
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: space complexity, auxiliary vs input, O(1) vs O(n).",
    ),
    _p(
        "cf-edge-cases",
        "cf-edge-cases-primary",
        "GFG — Edge Cases in Software Testing",
        "https://www.geeksforgeeks.org/edge-cases-in-software-engineering/",
        "GeeksforGeeks",
        rtype="documentation",
        order=0,
        description="PRIMARY: edge cases as unusual but valid inputs that break naive solutions, including empty and boundary inputs.",
    ),
    _p(
        "java-memory-model-basics",
        "java-memory-model-primary",
        "Dev.java — Java Memory Model Basics",
        "https://dev.java/learn/jvm/memory-model/",
        "Dev.java",
        rtype="documentation",
        order=0,
        description="PRIMARY: Java heap vs stack, object vs local primitive placement, and reachability for GC at a Java programmer level.",
    ),
    _p("java-memory-model-basics", "java-memory-model-jls", "Java Language Specification SE 21 — Chapter 17 Threads and Locks", JLS17, "Oracle", role="REFERENCE", rtype="documentation", order=2, description="Reference: formal JMM; primary is dev.java memory model overview."),
]


def apply_source_delivery(db: Session) -> dict[str, int]:
    """Insert or update mapped resources. Never deletes rows or resets completion."""
    created = 0
    updated = 0
    skipped = 0
    for spec in SOURCE_PATCHES:
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == spec["topic_slug"]).first()
        if not topic:
            skipped += 1
            continue
        lesson = (
            db.query(CurriculumLesson)
            .filter(CurriculumLesson.topic_id == topic.id)
            .order_by(CurriculumLesson.order_index, CurriculumLesson.id)
            .first()
        )
        if not lesson:
            skipped += 1
            continue
        meta = metadata_from_spec(
            url=spec["url"],
            resource_type=spec["resource_type"],
            role=spec["role"],
            section=spec.get("section"),
            lecture=spec.get("lecture"),
        )
        row = db.query(CurriculumResource).filter(CurriculumResource.slug == spec["slug"]).first()
        if row:
            row.title = spec["title"]
            row.url = spec["url"]
            row.provider = spec["provider"]
            row.resource_type = spec["resource_type"]
            row.role = meta["role"]
            row.section = meta["section"]
            row.lecture = meta["lecture"]
            row.video_id = meta["video_id"]
            row.verification_status = meta["verification_status"]
            row.official_unofficial = "official"
            row.order_index = spec["order"]
            if spec.get("description"):
                row.description = spec["description"]
            if row.lesson_id is None:
                row.lesson_id = lesson.id
            updated += 1
            continue
        db.add(
            CurriculumResource(
                slug=spec["slug"],
                title=spec["title"],
                url=spec["url"],
                resource_type=spec["resource_type"],
                provider=spec["provider"],
                description=spec.get("description"),
                official_unofficial="official",
                order_index=spec["order"],
                lesson_id=lesson.id,
                role=meta["role"],
                section=meta["section"],
                lecture=meta["lecture"],
                video_id=meta["video_id"],
                verification_status=meta["verification_status"],
            )
        )
        created += 1
    final = apply_final_resource_repairs(db, commit=False)
    db.commit()
    return {"created": created, "updated": updated, "skipped": skipped, "final_resource_repairs": final["updated"]}


if __name__ == "__main__":
    from app.db.session import SessionLocal

    session = SessionLocal()
    try:
        print(apply_source_delivery(session))
    finally:
        session.close()
