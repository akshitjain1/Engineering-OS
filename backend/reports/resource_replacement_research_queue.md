# Resource Replacement Research Queue

Generated: 2026-08-26T14:35:57.765272+00:00

**Total items: 66**

## Priority Summary

- **P0** (learner reaches soon / important prerequisite): 19
- **P1** (core domain / downstream impact): 41
- **P2** (later specialist topic): 6

## Domain Breakdown

| Domain | Count |
|--------|-------|
| Foundations | 18 |
| Java | 1 |
| DSA | 30 |
| ML | 6 |
| GenAI | 3 |
| Backend | 6 |
| SE | 2 |

## Foundations (18)

### [P0] `cf-alu`

**Topic:** ALU

**Learning objective:** The ALU (arithmetic logic unit) is the part of the CPU that performs integer arithmetic and boolean operations (add, subtract, AND, OR, compare). High-level expressions like `x + 1` and `a && b` become ALU operations after compilation. This topic has no selected CS50 lecture that names the ALU; the lesson is the explanation.

Objective: Explain the ALU's role in arithmetic and logic.

Mastery:
- State what the ALU computes.
- Relate a simple program statement to ALU work.
- Score >= 80%.

Next topic: cf-registers

**Required concepts:** alu-role, alu-ops

**Current resource:** GFG — Introduction of ALU and Data Path
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/computer-organization-architecture/introduction-of-alu-and-data-path/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-cpu
**Downstream dependents:** cf-registers
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: The ALU (arithmetic logic unit) is the part of the CPU that performs integer arithmetic and boolean operations (add, subtract, AND, OR, compare). High-level expressions like `x + 1` and `a && b` become ALU operations after compilation. This topic has no selected CS50 lecture that names the ALU; the lesson is the explanation.

Objective: Explain the ALU's role in arithmetic and logic.

Mastery:
- State what the ALU computes.
- Relate a simple program statement to ALU work.
- Score >= 80%.

Next topic: cf-registers
- Must cover concepts: alu-role, alu-ops
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-build-system`

**Topic:** Build system

**Learning objective:** Compile + test + package as a repeatable pipeline. make in CS50 Week 1; command runners in MIT Code Quality.

Objective: Explain why build tools exist.

Mastery:
- Describe compile + test + package as a pipeline.
- Run a documented build or test command.
- Score >= 80%.

Next topic: cf-dependency-management

**Required concepts:** build-repeatable

**Current resource:** GFG — Build Systems in Software Engineering
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/build-systems-in-software-engineering/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** ALWAYS_ON | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-dev-package-manager
**Downstream dependents:** cf-dependency-management
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: Compile + test + package as a repeatable pipeline. make in CS50 Week 1; command runners in MIT Code Quality.

Objective: Explain why build tools exist.

Mastery:
- Describe compile + test + package as a pipeline.
- Run a documented build or test command.
- Score >= 80%.

Next topic: cf-dependency-management
- Must cover concepts: build-repeatable
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-debugger`

**Topic:** Debugger

**Learning objective:** Stepping beats printf-only debugging. VS Code debugger docs are official. MIT debugging lecture is Unix/gdb-oriented and useful as extra depth.

Objective: Set a breakpoint and inspect a variable.

Mastery:
- Use a debugger on a trivial program.
- Inspect variables and the call stack.
- Score >= 80%.

Next topic: cf-formatter

**Required concepts:** debugger-breakpoints, debugger-unix-gdb

**Current resource:** GFG — Debugging in Software Engineering
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/debugging-in-software-engineering/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** ALWAYS_ON | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-dev-compiler
**Downstream dependents:** cf-formatter
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: Stepping beats printf-only debugging. VS Code debugger docs are official. MIT debugging lecture is Unix/gdb-oriented and useful as extra depth.

Objective: Set a breakpoint and inspect a variable.

Mastery:
- Use a debugger on a trivial program.
- Inspect variables and the call stack.
- Score >= 80%.

Next topic: cf-formatter
- Must cover concepts: debugger-breakpoints, debugger-unix-gdb
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-dev-package-manager`

**Topic:** Package manager

**Learning objective:** npm/Maven/pip vs apt/brew. MIT shipping-code is the verified lecture for artifacts and language packages.

Objective: Explain application-level package managers vs OS packages.

Mastery:
- Contrast language ecosystem dependencies with OS packages.
- Score >= 80%.

Next topic: cf-build-system

**Required concepts:** package-manager-language-vs-os, package-manager-pip

**Current resource:** GFG — Package Manager in Operating System
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/package-manager-in-operating-system/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** ALWAYS_ON | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-linter
**Downstream dependents:** cf-build-system
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: npm/Maven/pip vs apt/brew. MIT shipping-code is the verified lecture for artifacts and language packages.

Objective: Explain application-level package managers vs OS packages.

Mastery:
- Contrast language ecosystem dependencies with OS packages.
- Score >= 80%.

Next topic: cf-build-system
- Must cover concepts: package-manager-language-vs-os, package-manager-pip
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-dry-runs`

**Topic:** Dry runs

**Learning objective:** Manual execution before trusting code. Table of variable values per step.

Objective: Trace an algorithm on a small input by hand.

Mastery:
- Dry-run a loop on a 4-element input.
- Score >= 80%.

Next topic: cf-edge-cases

**Required concepts:** dry-run-trace, dry-run-table

**Current resource:** GFG — Dry Run in Software Engineering
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dry-run-in-software-engineering/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-algorithms
**Downstream dependents:** cf-edge-cases
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: Manual execution before trusting code. Table of variable values per step.

Objective: Trace an algorithm on a small input by hand.

Mastery:
- Dry-run a loop on a 4-element input.
- Score >= 80%.

Next topic: cf-edge-cases
- Must cover concepts: dry-run-trace, dry-run-table
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-edge-cases`

**Topic:** Edge cases

**Learning objective:** Inputs that break naive solutions: empty, one element, duplicates, already sorted, huge.

Objective: List empty, one-element, and extreme inputs.

Mastery:
- Name three edge cases for a list-processing task.
- Score >= 80%.

Next topic: cf-debugging-thinking

**Required concepts:** edge-unusual-valid, edge-empty-boundary

**Current resource:** GFG — Edge Cases in Software Testing
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/edge-cases-in-software-engineering/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-dry-runs
**Downstream dependents:** cf-debugging-thinking
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: Inputs that break naive solutions: empty, one element, duplicates, already sorted, huge.

Objective: List empty, one-element, and extreme inputs.

Mastery:
- Name three edge cases for a list-processing task.
- Score >= 80%.

Next topic: cf-debugging-thinking
- Must cover concepts: edge-unusual-valid, edge-empty-boundary
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-filesystems`

**Topic:** Filesystems

**Learning objective:** A filesystem presents files and directories on storage. Paths name them. The kernel enforces structure and permissions.

Objective: Explain files and directories as OS abstractions.

Mastery:
- Explain file vs path at a high level.
- Score >= 80%.

Next topic: cf-os-permissions

**Required concepts:** filesystem-files-dirs, filesystem-paths, filesystem-kernel

**Current resource:** GFG — File System in Operating System
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/file-system-in-operating-system/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-virtual-memory-basics
**Downstream dependents:** cf-os-permissions
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: A filesystem presents files and directories on storage. Paths name them. The kernel enforces structure and permissions.

Objective: Explain files and directories as OS abstractions.

Mastery:
- Explain file vs path at a high level.
- Score >= 80%.

Next topic: cf-os-permissions
- Must cover concepts: filesystem-files-dirs, filesystem-paths, filesystem-kernel
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-formatter`

**Topic:** Formatter

**Learning objective:** Formatters apply a consistent style. MIT Code Quality covers formatters. VS Code can format the current file.

Objective: Apply automatic formatting.

Mastery:
- Explain why formatters exist.
- Configure or run a formatter once.
- Score >= 80%.

Next topic: cf-linter

**Required concepts:** formatter-style

**Current resource:** GFG — Code Formatting in Software Engineering
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/code-formatting-in-software-engineering/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** ALWAYS_ON | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-debugger
**Downstream dependents:** cf-linter
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: Formatters apply a consistent style. MIT Code Quality covers formatters. VS Code can format the current file.

Objective: Apply automatic formatting.

Mastery:
- Explain why formatters exist.
- Configure or run a formatter once.
- Score >= 80%.

Next topic: cf-linter
- Must cover concepts: formatter-style
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-ide`

**Topic:** IDE

**Learning objective:** An IDE combines editor, run/debug, and project tools. VS Code is what you use day to day, but the skill is using one well. PRIMARY structured course for this module is TBD — do not treat a random YouTube playlist as a substitute. MIT 2026 development-environment lecture is Vim-heavy; it still defines what a development environment is.

Objective: Use an IDE to open, edit, and run a small project.

Mastery:
- Open a project and run it from the editor you actually use.
- Score >= 80%.

Next topic: cf-dev-compiler

**Required concepts:** ide-editor-debug, ide-vscode-example

**Current resource:** GFG — Introduction to Integrated Development Environment
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/introduction-to-integrated-development-environment/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** ALWAYS_ON | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-github-workflow, cf-compiler
**Downstream dependents:** cf-dev-compiler
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: An IDE combines editor, run/debug, and project tools. VS Code is what you use day to day, but the skill is using one well. PRIMARY structured course for this module is TBD — do not treat a random YouTube playlist as a substitute. MIT 2026 development-environment lecture is Vim-heavy; it still defines what a development environment is.

Objective: Use an IDE to open, edit, and run a small project.

Mastery:
- Open a project and run it from the editor you actually use.
- Score >= 80%.

Next topic: cf-dev-compiler
- Must cover concepts: ide-editor-debug, ide-vscode-example
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-instruction-execution`

**Topic:** Instruction execution

**Learning objective:** The processor repeats: fetch the next instruction from memory, decode what it means, execute it (often with the ALU), then continue. A simple assignment becomes several instructions. CS50 Week 1 shows source becoming machine code; it does not walk microarchitecture pipelines.

Objective: Describe fetch-decode-execute at a conceptual level.

Mastery:
- Walk through fetch-decode-execute without notes.
- Relate a simple statement to an instruction stream.
- Score >= 80%.

Next topic: cf-machine-code

**Required concepts:** fetch-decode-execute-loop, assignment-to-instructions

**Current resource:** GFG — Different Instruction Cycles
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/computer-organization-architecture/different-instruction-cycles/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-storage
**Downstream dependents:** cf-machine-code
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: The processor repeats: fetch the next instruction from memory, decode what it means, execute it (often with the ALU), then continue. A simple assignment becomes several instructions. CS50 Week 1 shows source becoming machine code; it does not walk microarchitecture pipelines.

Objective: Describe fetch-decode-execute at a conceptual level.

Mastery:
- Walk through fetch-decode-execute without notes.
- Relate a simple statement to an instruction stream.
- Score >= 80%.

Next topic: cf-machine-code
- Must cover concepts: fetch-decode-execute-loop, assignment-to-instructions
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-interpreter`

**Topic:** Interpreter

**Learning objective:** An interpreter executes a program by analyzing and running it incrementally (or running bytecode on a VM). You often need the language runtime installed. CS50 Week 1 is compiler-centric; this lesson supplies the contrast. Python is a familiar interpreted/VM example you may already know from C++-adjacent tooling.

Objective: Explain how an interpreter executes source or bytecode.

Mastery:
- Give one advantage and one cost of interpretation.
- Relate interpreters to virtual machines at a high level.
- Score >= 80%.

Next topic: cf-program

**Required concepts:** interpreter-incremental, interpreter-vs-compiler, interpreter-vm

**Current resource:** GFG — Interpreter in Compiler Design
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/interpreter-in-compiler-design/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-compiler
**Downstream dependents:** cf-program
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: An interpreter executes a program by analyzing and running it incrementally (or running bytecode on a VM). You often need the language runtime installed. CS50 Week 1 is compiler-centric; this lesson supplies the contrast. Python is a familiar interpreted/VM example you may already know from C++-adjacent tooling.

Objective: Explain how an interpreter executes source or bytecode.

Mastery:
- Give one advantage and one cost of interpretation.
- Relate interpreters to virtual machines at a high level.
- Score >= 80%.

Next topic: cf-program
- Must cover concepts: interpreter-incremental, interpreter-vs-compiler, interpreter-vm
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-linter`

**Topic:** Linter

**Learning objective:** Linters are static hints. MIT Code Quality. Not the same as a compiler error.

Objective: Run a linter and interpret one warning.

Mastery:
- Distinguish a linter finding from a compiler error.
- Score >= 80%.

Next topic: cf-dev-package-manager

**Required concepts:** linter-static-hint

**Current resource:** GFG — Linting in Software Development
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/linting-in-software-development/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** ALWAYS_ON | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-formatter
**Downstream dependents:** cf-dev-package-manager
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: Linters are static hints. MIT Code Quality. Not the same as a compiler error.

Objective: Run a linter and interpret one warning.

Mastery:
- Distinguish a linter finding from a compiler error.
- Score >= 80%.

Next topic: cf-dev-package-manager
- Must cover concepts: linter-static-hint
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-machine-code`

**Topic:** Machine code

**Learning objective:** Machine code is the binary instruction encoding a CPU family can execute. It is architecture-specific. CS50 Week 1: source code is compiled to machine code you can run.

Objective: Explain machine code as the CPU's native language.

Mastery:
- Contrast machine code with a high-level language.
- Explain why machine code is architecture-specific.
- Score >= 80%.

Next topic: cf-compiler

**Required concepts:** machine-code-binary, machine-code-arch, source-to-machine

**Current resource:** GFG — Machine Language
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/machine-language-in-computer-organization/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-instruction-execution
**Downstream dependents:** cf-compiler
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: Machine code is the binary instruction encoding a CPU family can execute. It is architecture-specific. CS50 Week 1: source code is compiled to machine code you can run.

Objective: Explain machine code as the CPU's native language.

Mastery:
- Contrast machine code with a high-level language.
- Explain why machine code is architecture-specific.
- Score >= 80%.

Next topic: cf-compiler
- Must cover concepts: machine-code-binary, machine-code-arch, source-to-machine
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-os-permissions`

**Topic:** Permissions

**Learning objective:** Unix permission bits say who may read, write, or execute a file. The kernel enforces them.

Objective: Explain user/group/other permission bits conceptually.

Mastery:
- Read a simple rwx triplet.
- Score >= 80%.

Next topic: cf-os-environment-variables

**Required concepts:** unix-permission-bits, kernel-enforces

**Current resource:** GFG — File Permissions in Linux
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/file-permissions-in-linux/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-filesystems
**Downstream dependents:** cf-os-environment-variables
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: Unix permission bits say who may read, write, or execute a file. The kernel enforces them.

Objective: Explain user/group/other permission bits conceptually.

Mastery:
- Read a simple rwx triplet.
- Score >= 80%.

Next topic: cf-os-environment-variables
- Must cover concepts: unix-permission-bits, kernel-enforces
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-program`

**Topic:** Program

**Learning objective:** A program is an artifact: source, maybe compiled form, sitting on storage. It is not yet a running process. CS50 Week 1 treats .c and the executable as program forms.

Objective: Define a program as stored instructions plus data.

Mastery:
- Distinguish a program on disk from a running process.
- Score >= 80%.

Next topic: cf-process

**Required concepts:** program-artifact, program-vs-process

**Current resource:** GFG — Program and its Types in Operating System
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/program-and-its-types-in-operating-system/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-interpreter
**Downstream dependents:** cf-process
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: A program is an artifact: source, maybe compiled form, sitting on storage. It is not yet a running process. CS50 Week 1 treats .c and the executable as program forms.

Objective: Define a program as stored instructions plus data.

Mastery:
- Distinguish a program on disk from a running process.
- Score >= 80%.

Next topic: cf-process
- Must cover concepts: program-artifact, program-vs-process
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-space-complexity`

**Topic:** cf-space-complexity

**Learning objective:** Understand cf-space-complexity

**Required concepts:** space-complexity, space-O-classes

**Current resource:** Space Complexity
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/gfact-51-space-complexity/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: cf-space-complexity
- Must cover concepts: space-complexity, space-O-classes
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-storage`

**Topic:** Storage

**Learning objective:** Storage (SSD/HDD) keeps data when power is off. It is slower than RAM. Files, installed programs, and Git repos live here. The OS copies needed pieces into RAM to run them.

Objective: Contrast persistent storage with RAM.

Mastery:
- Explain persistence vs volatility.
- Give typical uses of disk/SSD vs RAM.
- Score >= 80%.

Next topic: cf-instruction-execution

**Required concepts:** storage-persistent, storage-types, storage-files

**Current resource:** GFG — Storage Devices (persistent storage)
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/storage-devices/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-cache
**Downstream dependents:** cf-instruction-execution
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: Storage (SSD/HDD) keeps data when power is off. It is slower than RAM. Files, installed programs, and Git repos live here. The OS copies needed pieces into RAM to run them.

Objective: Contrast persistent storage with RAM.

Mastery:
- Explain persistence vs volatility.
- Give typical uses of disk/SSD vs RAM.
- Score >= 80%.

Next topic: cf-instruction-execution
- Must cover concepts: storage-persistent, storage-types, storage-files
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P0] `cf-system-calls`

**Topic:** System calls

**Learning objective:** A system call is how a user program asks the kernel to do privileged work such as reading a file or creating a process.

Objective: Explain system calls as the program–kernel interface.

Mastery:
- Trace a simple system call conceptually (e.g. write to the terminal).
- Score >= 80%.

Next topic: cf-os-memory

**Required concepts:** syscall-privileged, syscall-examples

**Current resource:** GFG — System Calls in Operating System
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/system-calls-in-operating-system/
- Failure: DEAD HTTP 404
- Evidence: HTTP 404

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 18

**Prerequisites:** cf-threads
**Downstream dependents:** cf-os-memory
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: A system call is how a user program asks the kernel to do privileged work such as reading a file or creating a process.

Objective: Explain system calls as the program–kernel interface.

Mastery:
- Trace a simple system call conceptually (e.g. write to the terminal).
- Score >= 80%.

Next topic: cf-os-memory
- Must cover concepts: syscall-privileged, syscall-examples
- Current resource failure: HTTP 404 (page removed)
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

## Java (1)

### [P0] `java-priority-queue`

**Topic:** PriorityQueue

**Learning objective:** PriorityQueue is a heap: poll gives the least element by natural or Comparator order (head is the smallest by default). It is not a sorted list — only the head is cheap. ArrayDeque is the usual queue/stack (C++ deque). C++ priority_queue is the analogue of PriorityQueue (and is a max-heap by default — Java's is min-heap by Comparable). DSA connection: heaps in Domain 2 use PriorityQueue plus Comparable/Comparator. C++ analogue: priority_queue. Streams are not required.

Objective: Use PriorityQueue for ordered retrieval and connect it to Comparable/Comparator and heaps.

Mastery:
- Offer/poll a PriorityQueue and explain min-heap default.
- Contrast ArrayDeque vs PriorityQueue vs List.
- Score >= 80% on the topic questions.

Next topic: java-generic-types

**Required concepts:** java-priority-queue-priorityqueue, java-priority-queue-priorityqueue-for-ordered-retrieval-and

**Current resource:** Stacks and queues
- Provider: Dev.java
- URL: https://dev.java/learn/api/collections-framework/stacks-queues/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** STRONG
**Estimated minutes:** 13

**Prerequisites:** java-iteration
**Downstream dependents:** java-generic-types, dsa-heap-structure, dsa-unweighted-shortest
**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: PriorityQueue is a heap: poll gives the least element by natural or Comparator order (head is the smallest by default). It is not a sorted list — only the head is cheap. ArrayDeque is the usual queue/stack (C++ deque). C++ priority_queue is the analogue of PriorityQueue (and is a max-heap by default — Java's is min-heap by Comparable). DSA connection: heaps in Domain 2 use PriorityQueue plus Comparable/Comparator. C++ analogue: priority_queue. Streams are not required.

Objective: Use PriorityQueue for ordered retrieval and connect it to Comparable/Comparator and heaps.

Mastery:
- Offer/poll a PriorityQueue and explain min-heap default.
- Contrast ArrayDeque vs PriorityQueue vs List.
- Score >= 80% on the topic questions.

Next topic: java-generic-types
- Must cover concepts: java-priority-queue-priorityqueue, java-priority-queue-priorityqueue-for-ordered-retrieval-and
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

## DSA (30)

### [P1] `dsa-advanced-dp-learn-exact`

**Topic:** dsa-advanced-dp-learn-exact

**Learning objective:** Understand dsa-advanced-dp-learn-exact

**Required concepts:** dsa-advanced-dp-advanced-dp, dsa-advanced-dp-recognize-digit-dp-tree-dp-bitmask-dp-by

**Current resource:** Learn: Advanced DP
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/bitmasking-and-dynamic-programming-set-1-count-ways-to-assign-unique-cap-to-every-person/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 45

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-advanced-dp-learn-exact
- Must cover concepts: dsa-advanced-dp-advanced-dp, dsa-advanced-dp-recognize-digit-dp-tree-dp-bitmask-dp-by
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-array-frequency-learn-exact`

**Topic:** dsa-array-frequency-learn-exact

**Learning objective:** Understand dsa-array-frequency-learn-exact

**Required concepts:** dsa-array-frequency-frequency-counting, dsa-array-frequency-count-values-with-a-fixed-size-array-whe

**Current resource:** Learn: Frequency counting
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/counting-frequencies-of-array-elements/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 24

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-array-frequency-learn-exact
- Must cover concepts: dsa-array-frequency-frequency-counting, dsa-array-frequency-count-values-with-a-fixed-size-array-whe
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-array-patterns-learn-exact`

**Topic:** dsa-array-patterns-learn-exact

**Learning objective:** Understand dsa-array-patterns-learn-exact

**Required concepts:** dsa-array-patterns-array-patterns, dsa-array-patterns-recognize-in-place-scans-and-bridge-patt

**Current resource:** Learn: Array patterns
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/two-pointers-technique/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 23

**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: dsa-array-patterns-learn-exact
- Must cover concepts: dsa-array-patterns-array-patterns, dsa-array-patterns-recognize-in-place-scans-and-bridge-patt
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-best-worst-average-learn-exact`

**Topic:** dsa-best-worst-average-learn-exact

**Learning objective:** Understand dsa-best-worst-average-learn-exact

**Required concepts:** dsa-best-worst-average-best-worst-average, dsa-best-worst-average-distinguish-best-worst-and-average-case

**Current resource:** Learn: Best, worst, average
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/worst-average-and-best-case-analysis-of-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 19

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-best-worst-average-learn-exact
- Must cover concepts: dsa-best-worst-average-best-worst-average, dsa-best-worst-average-distinguish-best-worst-and-average-case
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-bst-validate-learn-exact`

**Topic:** dsa-bst-validate-learn-exact

**Learning objective:** Understand dsa-bst-validate-learn-exact

**Required concepts:** dsa-bst-validate-bst-validation, dsa-bst-validate-validate-bst-property-with-global-min-ma

**Current resource:** Learn: BST validation
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/a-program-to-check-if-a-binary-tree-is-bst-or-not/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 38

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-bst-validate-learn-exact
- Must cover concepts: dsa-bst-validate-bst-validation, dsa-bst-validate-validate-bst-property-with-global-min-ma
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-character-processing-learn-exact`

**Topic:** dsa-character-processing-learn-exact

**Learning objective:** Understand dsa-character-processing-learn-exact

**Required concepts:** dsa-character-processing-character-processing, dsa-character-processing-classify-and-map-characters-case-digits

**Current resource:** Learn: Character processing
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-character-processing-learn-exact
- Must cover concepts: dsa-character-processing-character-processing, dsa-character-processing-classify-and-map-characters-case-digits
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-combinations-learn-exact`

**Topic:** dsa-combinations-learn-exact

**Learning objective:** Understand dsa-combinations-learn-exact

**Required concepts:** dsa-combinations-combinations, dsa-combinations-generate-combinations-with-an-index-curs

**Current resource:** Learn: Combinations
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-combinations-learn-exact
- Must cover concepts: dsa-combinations-combinations, dsa-combinations-generate-combinations-with-an-index-curs
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-connected-components-learn-exact`

**Topic:** dsa-connected-components-learn-exact

**Learning objective:** Understand dsa-connected-components-learn-exact

**Required concepts:** dsa-connected-components-connected-components, dsa-connected-components-count-or-label-connected-components-in-u

**Current resource:** Learn: Connected components
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-connected-components-learn-exact
- Must cover concepts: dsa-connected-components-connected-components, dsa-connected-components-count-or-label-connected-components-in-u
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-cycle-detection-learn-exact`

**Topic:** dsa-cycle-detection-learn-exact

**Learning objective:** Understand dsa-cycle-detection-learn-exact

**Required concepts:** dsa-cycle-detection-cycle-detection, dsa-cycle-detection-detect-a-cycle-with-floyd-s-fast-slow-al

**Current resource:** Learn: Cycle detection
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-cycle-detection-learn-exact
- Must cover concepts: dsa-cycle-detection-cycle-detection, dsa-cycle-detection-detect-a-cycle-with-floyd-s-fast-slow-al
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-dijkstra-learn-exact`

**Topic:** dsa-dijkstra-learn-exact

**Learning objective:** Understand dsa-dijkstra-learn-exact

**Required concepts:** dsa-dijkstra-dijkstra, dsa-dijkstra-run-dijkstra-s-algorithm-for-non-negativ

**Current resource:** Learn: Dijkstra
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-dijkstra-learn-exact
- Must cover concepts: dsa-dijkstra-dijkstra, dsa-dijkstra-run-dijkstra-s-algorithm-for-non-negativ
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-dp-1d-learn-exact`

**Topic:** dsa-dp-1d-learn-exact

**Learning objective:** Understand dsa-dp-1d-learn-exact

**Required concepts:** dsa-dp-1d-1d-dp, dsa-dp-1d-solve-linear-1d-dp-families-in-java

**Current resource:** Learn: 1D DP
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/introduction-to-dynamic-programming-data-structures-and-algorithm-tutorials/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 27

**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: dsa-dp-1d-learn-exact
- Must cover concepts: dsa-dp-1d-1d-dp, dsa-dp-1d-solve-linear-1d-dp-families-in-java
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-dp-2d-learn-exact`

**Topic:** dsa-dp-2d-learn-exact

**Learning objective:** Understand dsa-dp-2d-learn-exact

**Required concepts:** dsa-dp-2d-2d-dp, dsa-dp-2d-fill-dp-tables-over-two-indices

**Current resource:** Learn: 2D DP
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/category/dsa/algorithm/dynamic-programming/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 10

**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: dsa-dp-2d-learn-exact
- Must cover concepts: dsa-dp-2d-2d-dp, dsa-dp-2d-fill-dp-tables-over-two-indices
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-fast-slow-learn-exact`

**Topic:** dsa-fast-slow-learn-exact

**Learning objective:** Understand dsa-fast-slow-learn-exact

**Required concepts:** dsa-fast-slow-fast-and-slow-pointers, dsa-fast-slow-slow-1-and-fast-2-pointers-on-linked-lis

**Current resource:** Learn: Fast and slow pointers
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-fast-slow-learn-exact
- Must cover concepts: dsa-fast-slow-fast-and-slow-pointers, dsa-fast-slow-slow-1-and-fast-2-pointers-on-linked-lis
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-first-last-occurrence-learn-exact`

**Topic:** dsa-first-last-occurrence-learn-exact

**Learning objective:** Understand dsa-first-last-occurrence-learn-exact

**Required concepts:** dsa-first-last-occurrence-first-and-last-occurrence, dsa-first-last-occurrence-find-leftmost-or-rightmost-match

**Current resource:** Learn: First and last occurrence
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-first-last-occurrence-learn-exact
- Must cover concepts: dsa-first-last-occurrence-first-and-last-occurrence, dsa-first-last-occurrence-find-leftmost-or-rightmost-match
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-frequency-maps-learn-exact`

**Topic:** dsa-frequency-maps-learn-exact

**Learning objective:** Understand dsa-frequency-maps-learn-exact

**Required concepts:** dsa-frequency-maps-frequency-maps, dsa-frequency-maps-count-with-hashmap-when-alphabet-is-larg

**Current resource:** Learn: Frequency maps
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-frequency-maps-learn-exact
- Must cover concepts: dsa-frequency-maps-frequency-maps, dsa-frequency-maps-count-with-hashmap-when-alphabet-is-larg
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-heapify-learn-exact`

**Topic:** dsa-heapify-learn-exact

**Learning objective:** Understand dsa-heapify-learn-exact

**Required concepts:** dsa-heapify-heapify, dsa-heapify-a-heap-with-sift-up-insert-and-sift-down

**Current resource:** Learn: Heapify
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/heap-sort/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-heapify-learn-exact
- Must cover concepts: dsa-heapify-heapify, dsa-heapify-a-heap-with-sift-up-insert-and-sift-down
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-interval-problems-learn-exact`

**Topic:** dsa-interval-problems-learn-exact

**Learning objective:** Understand dsa-interval-problems-learn-exact

**Required concepts:** dsa-interval-problems-interval-problems, dsa-interval-problems-solve-interval-overlap-and-merging-with

**Current resource:** Learn: Interval problems
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-interval-problems-learn-exact
- Must cover concepts: dsa-interval-problems-interval-problems, dsa-interval-problems-solve-interval-overlap-and-merging-with
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-list-merge-learn-exact`

**Topic:** dsa-list-merge-learn-exact

**Learning objective:** Understand dsa-list-merge-learn-exact

**Required concepts:** dsa-list-merge-merge-patterns, dsa-list-merge-merge-two-sorted-lists-and-apply-merge-p

**Current resource:** Learn: Merge patterns
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-list-merge-learn-exact
- Must cover concepts: dsa-list-merge-merge-patterns, dsa-list-merge-merge-two-sorted-lists-and-apply-merge-p
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-list-operations-learn-exact`

**Topic:** dsa-list-operations-learn-exact

**Learning objective:** Understand dsa-list-operations-learn-exact

**Required concepts:** dsa-list-operations-list-operations, dsa-list-operations-insert-delete-and-find-by-walking-next-p

**Current resource:** Learn: List operations
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-list-operations-learn-exact
- Must cover concepts: dsa-list-operations-list-operations, dsa-list-operations-insert-delete-and-find-by-walking-next-p
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-list-reversal-learn-exact`

**Topic:** dsa-list-reversal-learn-exact

**Learning objective:** Understand dsa-list-reversal-learn-exact

**Required concepts:** dsa-list-reversal-reversal, dsa-list-reversal-reverse-a-singly-linked-list-iteratively

**Current resource:** Learn: Reversal
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-list-reversal-learn-exact
- Must cover concepts: dsa-list-reversal-reversal, dsa-list-reversal-reverse-a-singly-linked-list-iteratively
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-mst-learn-exact`

**Topic:** dsa-mst-learn-exact

**Learning objective:** Understand dsa-mst-learn-exact

**Required concepts:** dsa-mst-mst, dsa-mst-a-minimum-spanning-tree-and-contrast-kru

**Current resource:** Learn: MST
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-mst-learn-exact
- Must cover concepts: dsa-mst-mst, dsa-mst-a-minimum-spanning-tree-and-contrast-kru
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-pattern-selection-learn-exact`

**Topic:** dsa-pattern-selection-learn-exact

**Learning objective:** Understand dsa-pattern-selection-learn-exact

**Required concepts:** dsa-pattern-selection-pattern-selection, dsa-pattern-selection-classify-unseen-prompts-hash-two-pointer

**Current resource:** Learn: Pattern selection
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-pattern-selection-learn-exact
- Must cover concepts: dsa-pattern-selection-pattern-selection, dsa-pattern-selection-classify-unseen-prompts-hash-two-pointer
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-singly-linked-list-learn-exact`

**Topic:** dsa-singly-linked-list-learn-exact

**Learning objective:** Understand dsa-singly-linked-list-learn-exact

**Required concepts:** dsa-singly-linked-list-singly-linked-list, dsa-singly-linked-list-represent-a-singly-linked-list-with-node

**Current resource:** Learn: Singly linked list
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/what-is-linked-list/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 10

**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: dsa-singly-linked-list-learn-exact
- Must cover concepts: dsa-singly-linked-list-singly-linked-list, dsa-singly-linked-list-represent-a-singly-linked-list-with-node
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-subsets-learn-exact`

**Topic:** dsa-subsets-learn-exact

**Learning objective:** Understand dsa-subsets-learn-exact

**Required concepts:** dsa-subsets-subsets, dsa-subsets-generate-subsets-by-choose-skip

**Current resource:** Learn: Subsets
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-subsets-learn-exact
- Must cover concepts: dsa-subsets-subsets, dsa-subsets-generate-subsets-by-choose-skip
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-tabulation-learn-exact`

**Topic:** dsa-tabulation-learn-exact

**Learning objective:** Understand dsa-tabulation-learn-exact

**Required concepts:** dsa-tabulation-tabulation, dsa-tabulation-fill-a-dp-table-bottom-up-with-correct-i

**Current resource:** Learn: Tabulation
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-tabulation-learn-exact
- Must cover concepts: dsa-tabulation-tabulation, dsa-tabulation-fill-a-dp-table-bottom-up-with-correct-i
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-top-k-learn-exact`

**Topic:** dsa-top-k-learn-exact

**Learning objective:** Understand dsa-top-k-learn-exact

**Required concepts:** dsa-top-k-top-k, dsa-top-k-select-top-k-elements-with-a-size-k-heap

**Current resource:** Learn: Top-K
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/k-largestor-smallest-elements-in-an-array/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 34

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-top-k-learn-exact
- Must cover concepts: dsa-top-k-top-k, dsa-top-k-select-top-k-elements-with-a-size-k-heap
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-unweighted-shortest-learn-exact`

**Topic:** dsa-unweighted-shortest-learn-exact

**Learning objective:** Understand dsa-unweighted-shortest-learn-exact

**Required concepts:** dsa-unweighted-shortest-unweighted-shortest-paths, dsa-unweighted-shortest-compute-unweighted-shortest-paths-with-b

**Current resource:** Learn: Unweighted shortest paths
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-unweighted-shortest-learn-exact
- Must cover concepts: dsa-unweighted-shortest-unweighted-shortest-paths, dsa-unweighted-shortest-compute-unweighted-shortest-paths-with-b
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-window-fixed-learn-exact`

**Topic:** dsa-window-fixed-learn-exact

**Learning objective:** Understand dsa-window-fixed-learn-exact

**Required concepts:** dsa-window-fixed-fixed-window, dsa-window-fixed-maintain-a-window-of-fixed-length-k-whil

**Current resource:** Learn: Fixed window
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-window-fixed-learn-exact
- Must cover concepts: dsa-window-fixed-fixed-window, dsa-window-fixed-maintain-a-window-of-fixed-length-k-whil
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-window-frequency-learn-exact`

**Topic:** dsa-window-frequency-learn-exact

**Learning objective:** Understand dsa-window-frequency-learn-exact

**Required concepts:** dsa-window-frequency-frequency-window-state, dsa-window-frequency-track-counts-or-distinct-values-inside-a

**Current resource:** Learn: Frequency window state
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-window-frequency-learn-exact
- Must cover concepts: dsa-window-frequency-frequency-window-state, dsa-window-frequency-track-counts-or-distinct-values-inside-a
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `dsa-window-variable-learn-exact`

**Topic:** dsa-window-variable-learn-exact

**Learning objective:** Understand dsa-window-variable-learn-exact

**Required concepts:** dsa-window-variable-variable-window, dsa-window-variable-grow-and-shrink-window-to-satisfy-at-mos

**Current resource:** Learn: Variable window
- Provider: GeeksforGeeks
- URL: https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 20

**Practice contract:** 1 exercises (SELF_REFLECTION)

**Research brief:**
```
- Must teach: dsa-window-variable-learn-exact
- Must cover concepts: dsa-window-variable-variable-window, dsa-window-variable-grow-and-shrink-window-to-satisfy-at-mos
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

## ML (6)

### [P1] `ml-kmeans`

**Topic:** K-means clustering

**Learning objective:** Iterative centroid assignment; elbow/silhouette choice of k.

Objective: Iterative centroid assignment; elbow/silhouette choice of k

Mastery:
- Explain k-means clustering without notes.
- Work one concrete micro-example.
- State one common misconception.

**Required concepts:** centroid-iteration, inertia-elbow

**Current resource:** Clustering — K-means
- Provider: scikit-learn
- URL: https://scikit-learn.org/stable/modules/clustering.html
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** MECHANICS
**Estimated minutes:** 25

**Prerequisites:** ml-feature-scaling
**Downstream dependents:** ml-hierarchical-dbscan, ml-anomaly-awareness
**Practice contract:** 1 exercises (TRACE)

**Research brief:**
```
- Must teach: Iterative centroid assignment; elbow/silhouette choice of k.

Objective: Iterative centroid assignment; elbow/silhouette choice of k

Mastery:
- Explain k-means clustering without notes.
- Work one concrete micro-example.
- State one common misconception.
- Must cover concepts: centroid-iteration, inertia-elbow
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P2] `ml-anomaly-awareness`

**Topic:** Anomaly detection awareness

**Learning objective:** Novelty vs outlier detection settings; when unsupervised flags fail.

Objective: Novelty vs outlier detection settings; when unsupervised flags fail

Mastery:
- Explain anomaly detection awareness without notes.
- Work one concrete micro-example.
- State one common misconception.

**Required concepts:** novelty-outlier

**Current resource:** Novelty & Outlier Detection
- Provider: scikit-learn
- URL: https://scikit-learn.org/stable/modules/neighbors.html
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** MECHANICS
**Estimated minutes:** 20

**Prerequisites:** ml-kmeans
**Practice contract:** 1 exercises (TRACE)

**Research brief:**
```
- Must teach: Novelty vs outlier detection settings; when unsupervised flags fail.

Objective: Novelty vs outlier detection settings; when unsupervised flags fail

Mastery:
- Explain anomaly detection awareness without notes.
- Work one concrete micro-example.
- State one common misconception.
- Must cover concepts: novelty-outlier
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P2] `ml-hierarchical-dbscan`

**Topic:** Hierarchical clustering & DBSCAN

**Learning objective:** Dendrograms vs density reachability; noise handling without fixed k.

Objective: Dendrograms vs density reachability; noise handling without fixed k

Mastery:
- Explain hierarchical clustering & dbscan without notes.
- Work one concrete micro-example.
- State one common misconception.

**Required concepts:** agglomerative-linkage, dbscan-density, silhouette

**Current resource:** Clustering — Hierarchical & DBSCAN
- Provider: scikit-learn
- URL: https://scikit-learn.org/stable/modules/clustering.html
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** MECHANICS
**Estimated minutes:** 25

**Prerequisites:** ml-kmeans
**Practice contract:** 1 exercises (TRACE)

**Research brief:**
```
- Must teach: Dendrograms vs density reachability; noise handling without fixed k.

Objective: Dendrograms vs density reachability; noise handling without fixed k

Mastery:
- Explain hierarchical clustering & dbscan without notes.
- Work one concrete micro-example.
- State one common misconception.
- Must cover concepts: agglomerative-linkage, dbscan-density, silhouette
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P2] `ml-pca`

**Topic:** Principal component analysis

**Learning objective:** Project onto top-variance directions; explained variance & whitening.

Objective: Project onto top-variance directions; explained variance & whitening

Mastery:
- Explain principal component analysis without notes.
- Work one concrete micro-example.
- State one common misconception.

**Required concepts:** variance-directions, projection-reconstruction

**Current resource:** Decompositions — PCA
- Provider: scikit-learn
- URL: https://scikit-learn.org/stable/modules/decomposition.html
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** MECHANICS
**Estimated minutes:** 30

**Prerequisites:** ml-feature-scaling, math-matrices
**Practice contract:** 1 exercises (TRACE)

**Research brief:**
```
- Must teach: Project onto top-variance directions; explained variance & whitening.

Objective: Project onto top-variance directions; explained variance & whitening

Mastery:
- Explain principal component analysis without notes.
- Work one concrete micro-example.
- State one common misconception.
- Must cover concepts: variance-directions, projection-reconstruction
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P2] `ml-regression-metrics`

**Topic:** Regression metrics

**Learning objective:** Interpret MAE vs MSE vs RMSE vs R² and when each misleads.

Objective: Interpret MAE vs MSE vs RMSE vs R² and when each misleads

Mastery:
- Explain regression metrics without notes.
- Work one concrete micro-example.
- State one common misconception.

**Required concepts:** mae-mse-rmse, r2-score

**Current resource:** Model Evaluation — Regression metrics
- Provider: scikit-learn
- URL: https://scikit-learn.org/stable/modules/model_evaluation.html
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** MECHANICS
**Estimated minutes:** 20

**Prerequisites:** ml-loss-intuition
**Practice contract:** 1 exercises (TRACE)

**Research brief:**
```
- Must teach: Interpret MAE vs MSE vs RMSE vs R² and when each misleads.

Objective: Interpret MAE vs MSE vs RMSE vs R² and when each misleads

Mastery:
- Explain regression metrics without notes.
- Work one concrete micro-example.
- State one common misconception.
- Must cover concepts: mae-mse-rmse, r2-score
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P2] `ml-roc-auc`

**Topic:** ROC curves & AUC

**Learning objective:** Read TPR/FPR across thresholds; compare models with AUC and PR curves.

Objective: Read TPR/FPR across thresholds; compare models with AUC and PR curves

Mastery:
- Explain roc curves & auc without notes.
- Work one concrete micro-example.
- State one common misconception.

**Required concepts:** roc-curve, auc-score

**Current resource:** Model Evaluation — ROC/AUC
- Provider: scikit-learn
- URL: https://scikit-learn.org/stable/modules/model_evaluation.html
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** MECHANICS
**Estimated minutes:** 25

**Prerequisites:** ml-confusion-matrix
**Practice contract:** 1 exercises (TRACE)

**Research brief:**
```
- Must teach: Read TPR/FPR across thresholds; compare models with AUC and PR curves.

Objective: Read TPR/FPR across thresholds; compare models with AUC and PR curves

Mastery:
- Explain roc curves & auc without notes.
- Work one concrete micro-example.
- State one common misconception.
- Must cover concepts: roc-curve, auc-score
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

## GenAI (3)

### [P1] `genai-context-windows`

**Topic:** Context windows

**Learning objective:** Finite attention span economics; truncation strategies.

Objective: Finite attention span economics; truncation strategies

Mastery:
- Explain context windows without notes.
- Work one concrete micro-example.
- State one common misconception.

**Required concepts:** finite-span

**Current resource:** Context windows guidance
- Provider: Anthropic
- URL: https://platform.claude.com/docs/en/build-with-claude/context-windows
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** MECHANICS
**Estimated minutes:** 15

**Prerequisites:** genai-tokenization-llm
**Downstream dependents:** genai-prompt-engineering
**Practice contract:** 1 exercises (TRACE)

**Research brief:**
```
- Must teach: Finite attention span economics; truncation strategies.

Objective: Finite attention span economics; truncation strategies

Mastery:
- Explain context windows without notes.
- Work one concrete micro-example.
- State one common misconception.
- Must cover concepts: finite-span
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `genai-rag`

**Topic:** RAG systems

**Learning objective:** Retrieve context and ground LLM answers.

Objective: Retrieve context and ground LLM answers.

Mastery:
- Explain RAG systems.
- Complete mapped practice with stated quantity.

**Required concepts:** genai-rag-rag-systems, genai-rag-retrieve-context-and-ground-llm-answers

**Current resource:** DeepLearning.AI: RAG systems
- Provider: DeepLearning.AI
- URL: https://docs.langchain.com/oss/python/langchain/overview
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** advanced | **Track:** SPECIALIZATION | **Depth:** DEEP
**Estimated minutes:** 14

**Prerequisites:** genai-embeddings, be-fastapi-intro, genai-chunking-retrieval
**Downstream dependents:** genai-agents, genai-eval, genai-hallucinations-guardrails
**Project links:** rag-mini-app
**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: Retrieve context and ground LLM answers.

Objective: Retrieve context and ground LLM answers.

Mastery:
- Explain RAG systems.
- Complete mapped practice with stated quantity.
- Must cover concepts: genai-rag-rag-systems, genai-rag-retrieve-context-and-ground-llm-answers
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P2] `genai-lora-peft`

**Topic:** LoRA & parameter-efficient fine-tuning

**Learning objective:** Train low-rank adapters instead of full weights; memory tradeoffs.

Objective: Train low-rank adapters instead of full weights; memory tradeoffs

Mastery:
- Explain lora & parameter-efficient fine-tuning without notes.
- Work one concrete micro-example.
- State one common misconception.

**Required concepts:** low-rank-adapters, memory-tradeoffs

**Current resource:** PEFT / LoRA documentation
- Provider: Hugging Face
- URL: https://huggingface.co/docs/peft/index
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** CORE | **Depth:** MECHANICS
**Estimated minutes:** 25

**Prerequisites:** genai-pretraining-finetuning
**Practice contract:** 1 exercises (TRACE)

**Research brief:**
```
- Must teach: Train low-rank adapters instead of full weights; memory tradeoffs.

Objective: Train low-rank adapters instead of full weights; memory tradeoffs

Mastery:
- Explain lora & parameter-efficient fine-tuning without notes.
- Work one concrete micro-example.
- State one common misconception.
- Must cover concepts: low-rank-adapters, memory-tradeoffs
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

## Backend (6)

### [P1] `db-sql-joins`

**Topic:** SQL JOINs

**Learning objective:** Combine tables with INNER/LEFT joins correctly.

Objective: Combine tables with INNER/LEFT joins correctly.

Mastery:
- Explain SQL JOINs in your own words.
- Complete the mapped practice checklist.

**Required concepts:** db-sql-joins-sql-joins, db-sql-joins-combine-tables-with-inner-left-joins-cor

**Current resource:** SQLite: SQL JOINs
- Provider: SQLite
- URL: https://www.sqlite.org/lang_select.html
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 53

**Prerequisites:** db-sql-select
**Downstream dependents:** db-schema-design
**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: Combine tables with INNER/LEFT joins correctly.

Objective: Combine tables with INNER/LEFT joins correctly.

Mastery:
- Explain SQL JOINs in your own words.
- Complete the mapped practice checklist.
- Must cover concepts: db-sql-joins-sql-joins, db-sql-joins-combine-tables-with-inner-left-joins-cor
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `db-sql-select`

**Topic:** SQL SELECT

**Learning objective:** Query rows with SELECT, WHERE, ORDER BY.

Objective: Query rows with SELECT, WHERE, ORDER BY.

Mastery:
- Explain SQL SELECT in your own words.
- Complete the mapped practice checklist.

**Required concepts:** db-sql-select-sql-select, db-sql-select-query-rows-with-select-where-order-by

**Current resource:** SQLite: SQL SELECT
- Provider: SQLite
- URL: https://www.sqlite.org/lang_select.html
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 53

**Downstream dependents:** db-sql-joins, db-indexes, db-transactions, be-persistence, ds-sql-analytics
**Project links:** sql-crud-app
**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: Query rows with SELECT, WHERE, ORDER BY.

Objective: Query rows with SELECT, WHERE, ORDER BY.

Mastery:
- Explain SQL SELECT in your own words.
- Complete the mapped practice checklist.
- Must cover concepts: db-sql-select-sql-select, db-sql-select-query-rows-with-select-where-order-by
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `db-transactions`

**Topic:** Transactions

**Learning objective:** Use BEGIN/COMMIT/ROLLBACK for atomic updates.

Objective: Use BEGIN/COMMIT/ROLLBACK for atomic updates.

Mastery:
- Explain Transactions in your own words.
- Complete the mapped practice checklist.

**Required concepts:** db-transactions-transactions, db-transactions-begin-commit-rollback-for-atomic-updates

**Current resource:** SQLite: Transactions
- Provider: SQLite
- URL: https://www.sqlite.org/lang_transaction.html
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 13

**Prerequisites:** db-sql-select
**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: Use BEGIN/COMMIT/ROLLBACK for atomic updates.

Objective: Use BEGIN/COMMIT/ROLLBACK for atomic updates.

Mastery:
- Explain Transactions in your own words.
- Complete the mapped practice checklist.
- Must cover concepts: db-transactions-transactions, db-transactions-begin-commit-rollback-for-atomic-updates
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `devops-path`

**Topic:** DevOps learning path

**Learning objective:** Sketch a personal learning path into DevOps after core ML/backend.

Objective: Sketch a personal learning path into DevOps after core ML/backend.

Mastery:
- Explain DevOps learning path in your own words.
- Complete the mapped practice checklist.

**Required concepts:** devops-path-devops-learning-path, devops-path-sketch-a-personal-learning-path-into-dev

**Current resource:** 12-Factor: DevOps learning path
- Provider: 12-Factor
- URL: https://12factor.net/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** OPTIONAL | **Depth:** AWARENESS
**Estimated minutes:** 10

**Prerequisites:** devops-awareness
**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: Sketch a personal learning path into DevOps after core ML/backend.

Objective: Sketch a personal learning path into DevOps after core ML/backend.

Mastery:
- Explain DevOps learning path in your own words.
- Complete the mapped practice checklist.
- Must cover concepts: devops-path-devops-learning-path, devops-path-sketch-a-personal-learning-path-into-dev
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `ops-linux-services`

**Topic:** Linux services basics

**Learning objective:** Manage long-running services and logs.

Objective: Manage long-running services and logs.

Mastery:
- Explain Linux services basics.
- Complete mapped practice with stated quantity.

**Required concepts:** ops-linux-services-linux-services-basics, ops-linux-services-manage-long-running-services-and-logs

**Current resource:** man7: Linux services basics
- Provider: man7
- URL: https://man7.org/linux/man-pages/man1/systemctl.1.html
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** intermediate | **Track:** SPECIALIZATION | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 75

**Prerequisites:** cf-linux-processes
**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: Manage long-running services and logs.

Objective: Manage long-running services and logs.

Mastery:
- Explain Linux services basics.
- Complete mapped practice with stated quantity.
- Must cover concepts: ops-linux-services-linux-services-basics, ops-linux-services-manage-long-running-services-and-logs
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `sys-queues`

**Topic:** Message queues

**Learning objective:** Decouple producers/consumers with queues.

Objective: Decouple producers/consumers with queues.

Mastery:
- Explain Message queues.
- Complete mapped practice with stated quantity.

**Required concepts:** sys-queues-message-queues, sys-queues-decouple-producers-consumers-with-queues

**Current resource:** System Design Primer: Message queues
- Provider: System Design Primer
- URL: https://github.com/donnemartin/system-design-primer#asynchronous-processing-with-message-queues
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** beginner | **Track:** SPECIALIZATION | **Depth:** STRONG
**Estimated minutes:** 67

**Prerequisites:** sys-scalability
**Practice contract:** 2 exercises (SELF_REFLECTION, ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: Decouple producers/consumers with queues.

Objective: Decouple producers/consumers with queues.

Mastery:
- Explain Message queues.
- Complete mapped practice with stated quantity.
- Must cover concepts: sys-queues-message-queues, sys-queues-decouple-producers-consumers-with-queues
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

## SE (2)

### [P1] `se-api-design`

**Topic:** API design basics

**Learning objective:** Design resource-oriented HTTP APIs with clear errors.

Objective: Design resource-oriented HTTP APIs with clear errors.

Mastery:
- Explain API design basics in your own words.
- Complete the mapped practice checklist.

**Required concepts:** se-api-design-api-design-basics, se-api-design-design-resource-oriented-http-apis-with

**Current resource:** restfulapi.net: API design basics
- Provider: restfulapi.net
- URL: https://restfulapi.net/
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 16

**Prerequisites:** se-requirements
**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: Design resource-oriented HTTP APIs with clear errors.

Objective: Design resource-oriented HTTP APIs with clear errors.

Mastery:
- Explain API design basics in your own words.
- Complete the mapped practice checklist.
- Must cover concepts: se-api-design-api-design-basics, se-api-design-design-resource-oriented-http-apis-with
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---

### [P1] `se-sdlc`

**Topic:** SDLC overview

**Learning objective:** Describe the software development lifecycle phases and why they exist.

Objective: Describe the software development lifecycle phases and why they exist.

Mastery:
- Explain SDLC overview in your own words.
- Complete the mapped practice checklist.

**Required concepts:** se-sdlc-sdlc-overview, se-sdlc-describe-the-software-development-lifecy

**Current resource:** Software Development Lifecycle (IBM)
- Provider: IBM
- URL: https://www.ibm.com/think/topics
- Failure: SECTION_NOT_FOUND -> CONTENT_LOST
- Evidence: Declared section not found and content mismatch

**Difficulty:** intermediate | **Track:** CORE | **Depth:** WORKING_KNOWLEDGE
**Estimated minutes:** 22

**Downstream dependents:** se-requirements, se-versioning, se-solid-srp, se-testing-pyramid
**Practice contract:** 1 exercises (ACTION_CHECKLIST)

**Research brief:**
```
- Must teach: Describe the software development lifecycle phases and why they exist.

Objective: Describe the software development lifecycle phases and why they exist.

Mastery:
- Explain SDLC overview in your own words.
- Complete the mapped practice checklist.
- Must cover concepts: se-sdlc-sdlc-overview, se-sdlc-describe-the-software-development-lifecy
- Current resource failure: Content no longer covers the learning objective
- Preferably a bounded instructional lesson (article, tutorial, or video)
- Must be freely accessible
- Must be from a reputable provider
```

---
