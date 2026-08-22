"""Computer fundamentals: CPU through process."""

from __future__ import annotations

from _d0_helpers import CS50_N1, CS50_W1, MIT_SHELL, WSL, ex, q, r
from _d0_part1 import CONTENT, _add

_add(
    "cf-cpu",
    hours=0.5,
    objective="Describe what a CPU does in executing programs.",
    explanation=(
        "The CPU (central processing unit) fetches instructions and data, decodes them, and executes them. "
        "It is not the same as RAM (working memory) or disk (persistent storage). "
        "CS50 does not teach a full computer-architecture course; this lesson is the internal explanation. "
        "Week 1 still helps: source becomes machine code that a processor can run."
    ),
    mastery=[
        "Explain the CPU's role without notes.",
        "Contrast CPU with RAM and storage.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-cpu-reference", "CS50x 2026 Week 1 (source to machine code)", CS50_W1, "CS50x", "REFERENCE", "interactive_tutorial", 0,
          "Use source/machine code/compiler sections to see what the CPU eventually runs. Not a CPU microarchitecture lecture."),
    ],
    questions=[
        q("cf-cpu-q1", "What is the CPU's job relative to a stored program?",
          ["Hold files after you shut the machine down.",
           "Fetch, decode, and execute instructions.",
           "Replace the need for RAM.",
           "Only draw pixels on the screen."],
          "Fetch, decode, and execute instructions.",
          "Persistence is storage; the CPU executes.", "medium", True),
        q("cf-cpu-q2", "Why isn't a faster disk a substitute for a faster CPU?",
          ["Disks already execute instructions.",
           "They solve different bottlenecks: execution vs long-term storage/transfer.",
           "CPUs cannot wait for I/O.",
           "All programs live only on disk while running."],
          "They solve different bottlenecks: execution vs long-term storage/transfer.",
          "Running code needs the processor and RAM, not only disk speed.", "medium", True),
        q("cf-cpu-q3", "Where do programs sit while the CPU is executing them?",
          ["Only in the compiler's source file", "Typically in RAM, with instructions fed to the CPU",
           "Only on GitHub", "Only in cache forever after install"],
          "Typically in RAM, with instructions fed to the CPU",
          "The OS loads a program into memory; the CPU executes from there.", "easy"),
        q("cf-cpu-q4", "If two laptops have the same storage size, why might one feel faster?",
          ["Storage size is the only performance factor.",
           "CPU, RAM, and cache also affect how quickly instructions run.",
           "The slower one must be using decimal instead of binary.",
           "Faster always means more bytes on disk."],
          "CPU, RAM, and cache also affect how quickly instructions run.",
          "Capacity ≠ compute.", "easy"),
    ],
    exercises=[
        ex("cf-cpu-ex1", "Role comparison",
           "Write a 6–10 sentence explanation comparing CPU, registers, RAM, cache, and storage. "
           "For each, state what problem it solves (speed, capacity, persistence). No extra sources required."),
    ],
)

_add(
    "cf-alu",
    hours=0.4,
    objective="Explain the ALU's role in arithmetic and logic.",
    explanation=(
        "The ALU (arithmetic logic unit) is the part of the CPU that performs integer arithmetic and boolean operations "
        "(add, subtract, AND, OR, compare). High-level expressions like `x + 1` and `a && b` become ALU operations "
        "after compilation. This topic has no selected CS50 lecture that names the ALU; the lesson is the explanation."
    ),
    mastery=[
        "State what the ALU computes.",
        "Relate a simple program statement to ALU work.",
        "Score >= 80%.",
    ],
    resources=[],
    questions=[
        q("cf-alu-q1", "Which work belongs to the ALU rather than to a disk controller?",
          ["Spinning a hard drive", "Adding two integers and comparing them",
           "Keeping files after shutdown", "Drawing a window border"],
          "Adding two integers and comparing them",
          "ALU = arithmetic and logic on values in the CPU.", "easy", True),
        q("cf-alu-q2", "A program evaluates `score >= 10`. What is the CPU doing at ALU level?",
          ["Storing the source file on disk", "A comparison that produces a true/false result",
           "Opening a network socket", "Allocating a new hard drive partition"],
          "A comparison that produces a true/false result",
          "Comparisons are logic operations.", "medium", True),
        q("cf-alu-q3", "Why can one ALU serve many kinds of programs?",
          ["Every program uses a unique ALU chip.",
           "Different programs reduce to a small set of arithmetic/logic operations.",
           "The ALU stores the entire operating system.",
           "ALUs only run Scratch."],
          "Different programs reduce to a small set of arithmetic/logic operations.",
          "Instruction sets reuse add/compare/etc.", "medium"),
        q("cf-alu-q4", "Registers vs ALU: which statement is accurate?",
          ["The ALU stores all files; registers add numbers.",
           "Registers hold values; the ALU operates on values.",
           "They are two names for RAM.",
           "The ALU is only used for floating-point graphics."],
          "Registers hold values; the ALU operates on values.",
          "Data vs computation.", "easy"),
    ],
    exercises=[
        ex("cf-alu-ex1", "Statement to operations",
           "Take `total = price + tax` and `if total > 100`. List the ALU-level operations (add, compare) "
           "and which values must be available in registers or RAM first."),
    ],
)

_add(
    "cf-registers",
    hours=0.4,
    objective="Explain registers as the CPU's fastest working storage.",
    explanation=(
        "Registers are tiny, extremely fast storage locations inside the CPU. They hold the instruction being worked on, "
        "addresses, and intermediate results. There are few of them, so the CPU constantly moves data between registers and RAM. "
        "No CS50 week is a register-file course; this is an internal explanation."
    ),
    mastery=[
        "Explain why registers are small and fast.",
        "Give examples of what is stored in registers during execution.",
        "Score >= 80%.",
    ],
    resources=[],
    questions=[
        q("cf-registers-q1", "Why are CPU registers much smaller than RAM?",
          ["Registers are implemented in slower technology, so they must be tiny.",
           "Making huge ultra-fast storage as big as RAM is expensive; a few fast locations is the tradeoff.",
           "Programs are forbidden from using RAM.",
           "Registers only store the operating system kernel."],
          "Making huge ultra-fast storage as big as RAM is expensive; a few fast locations is the tradeoff.",
          "Memory hierarchy: speed vs size vs cost.", "medium", True),
        q("cf-registers-q2", "While adding two numbers, where do the operands typically sit immediately before the add?",
          ["Only on disk", "In CPU registers (loaded from RAM if needed)",
           "In the Git object database", "In DNS"],
          "In CPU registers (loaded from RAM if needed)",
          "Load into registers, then ALU.", "easy", True),
        q("cf-registers-q3", "If everything stayed in RAM and never in registers, what would mainly get worse?",
          ["File persistence after power off", "Latency of each arithmetic operation",
           "The number of bits in a byte", "Unicode support"],
          "Latency of each arithmetic operation",
          "RAM is slower than registers.", "medium"),
        q("cf-registers-q4", "Which is a register, not RAM?",
          ["A 16 GB DIMM module", "A named CPU location holding one word of data during an instruction",
           "An SSD partition", "A USB stick"],
          "A named CPU location holding one word of data during an instruction",
          "Registers live on the processor.", "easy"),
    ],
    exercises=[
        ex("cf-registers-ex1", "Trace a tiny add",
           "On paper, trace `a=3; b=4; c=a+b` as: values in RAM, copies into registers, ALU add, write-back. "
           "Label each step. This is conceptual, not assembly syntax."),
    ],
)

_add(
    "cf-ram",
    hours=0.5,
    objective="Explain RAM as volatile working memory.",
    explanation=(
        "RAM (main memory) holds the running program's code and data. It is volatile: contents disappear when power is gone. "
        "It is larger and slower than registers, smaller and faster than disk. A program on disk is not executing until loaded."
    ),
    mastery=[
        "Contrast RAM with registers and with disk.",
        "Explain volatility.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-ram-reference", "CS50x 2026 Week 1 (programs as compiled machine code)", CS50_W1, "CS50x", "REFERENCE", "interactive_tutorial", 0,
          "Compiled programs are loaded into memory to run. Not a DRAM-engineering lecture."),
    ],
    questions=[
        q("cf-ram-q1", "What does volatile mean for RAM?",
          ["It can catch fire easily.", "Data is lost when power is removed.",
           "It can only store videos.", "It is slower than magnetic tape."],
          "Data is lost when power is removed.",
          "Unlike disk/SSD persistence.", "easy", True),
        q("cf-ram-q2", "Why must a program be loaded into RAM to run?",
          ["The CPU executes from working memory, not by scanning the whole disk for each instruction.",
           "Disk cannot store machine code.",
           "RAM is the only place compilers exist.",
           "Git requires RAM to store remotes."],
          "The CPU executes from working memory, not by scanning the whole disk for each instruction.",
          "Load then execute.", "medium", True),
        q("cf-ram-q3", "You open a 2 GB file on a machine with 1 GB free RAM. What is a likely consequence?",
          ["The file becomes 1 GB on disk.",
           "The OS may use virtual memory/swapping and the machine can slow down.",
           "Registers expand to 2 GB.",
           "Hexadecimal conversion fails."],
          "The OS may use virtual memory/swapping and the machine can slow down.",
          "Preview of virtual memory; do not need kernel internals yet.", "medium"),
        q("cf-ram-q4", "Which comparison is correct?",
          ["RAM is typically faster than registers.",
           "RAM is typically faster than disk and slower than registers.",
           "RAM persists like an SSD.",
           "RAM and ALU are the same component."],
          "RAM is typically faster than disk and slower than registers.",
          "Hierarchy.", "easy"),
    ],
    exercises=[
        ex("cf-ram-ex1", "Volatility check",
           "Write three bullets: (1) what happens to unsaved editor buffers if power dies, "
           "(2) what happens to a saved file on disk, (3) why that difference exists (RAM vs storage)."),
    ],
)

_add(
    "cf-cache",
    hours=0.5,
    objective="Explain why caches exist between CPU and RAM.",
    explanation=(
        "A cache is a small fast memory that stores recently used data and instructions so the CPU does not wait on RAM every time. "
        "It works because programs reuse nearby data (locality). You do not need cache-coherence protocols at this level."
    ),
    mastery=[
        "Explain locality at a high level.",
        "Place cache in the memory hierarchy.",
        "Score >= 80%.",
    ],
    resources=[],
    questions=[
        q("cf-cache-q1", "What problem does cache exist to solve?",
          ["Making disks bigger", "Hiding RAM latency for the common case of reused data",
           "Replacing the ALU", "Encrypting every byte"],
          "Hiding RAM latency for the common case of reused data",
          "Cache sits between CPU and RAM for speed.", "medium", True),
        q("cf-cache-q2", "Why does looping over an array often hit cache well?",
          ["Arrays are stored on GitHub.",
           "Consecutive elements are nearby in memory (spatial locality).",
           "The ALU turns into RAM.",
           "Cache only works for strings."],
          "Consecutive elements are nearby in memory (spatial locality).",
          "Locality.", "medium", True),
        q("cf-cache-q3", "If cache is so fast, why not make all memory cache?",
          ["It would violate Unicode.",
           "That much ultra-fast memory is costly; hierarchy is the engineering compromise.",
           "Operating systems forbid it.",
           "Cache cannot store zeros."],
          "That much ultra-fast memory is costly; hierarchy is the engineering compromise.",
          "Same tradeoff as registers vs RAM.", "easy"),
        q("cf-cache-q4", "A cache miss means:",
          ["The program has a syntax error.",
           "The needed data was not in cache and must come from a slower level (e.g. RAM).",
           "The disk is full.",
           "Hex conversion failed."],
          "The needed data was not in cache and must come from a slower level (e.g. RAM).",
          "Miss = go slower.", "easy"),
    ],
    exercises=[
        ex("cf-cache-ex1", "Hierarchy diagram",
           "Draw (boxes) registers → cache → RAM → storage. Annotate each with relative speed, size, and persistence. "
           "Add one sentence on why looping an array is cache-friendly."),
    ],
)

_add(
    "cf-storage",
    hours=0.4,
    objective="Contrast persistent storage with RAM.",
    explanation=(
        "Storage (SSD/HDD) keeps data when power is off. It is slower than RAM. Files, installed programs, and Git repos live here. "
        "The OS copies needed pieces into RAM to run them."
    ),
    mastery=[
        "Explain persistence vs volatility.",
        "Give typical uses of disk/SSD vs RAM.",
        "Score >= 80%.",
    ],
    resources=[],
    questions=[
        q("cf-storage-q1", "What is the defining property of persistent storage vs RAM?",
          ["Storage is always faster than RAM.",
           "Storage retains data without power; RAM does not.",
           "Storage is inside the ALU.",
           "Storage can only hold pictures."],
          "Storage retains data without power; RAM does not.",
          "Persistence.", "easy", True),
        q("cf-storage-q2", "Why don't we execute every instruction directly off the SSD?",
          ["SSDs cannot store bytes.",
           "Random instruction fetch from storage is far slower than from RAM.",
           "Compilers refuse to write to SSD.",
           "SSDs only understand hexadecimal."],
          "Random instruction fetch from storage is far slower than from RAM.",
          "Load into RAM first.", "medium", True),
        q("cf-storage-q3", "A Git repository's `.git` directory lives primarily where when you are not running Git?",
          ["Only in CPU registers", "On persistent storage in the project folder",
           "Only in L1 cache", "Only in the compiler"],
          "On persistent storage in the project folder",
          "Later Git topics; conceptually it is files on disk.", "easy"),
        q("cf-storage-q4", "Saving a file in an editor typically means:",
          ["Copying RAM buffers to persistent storage",
           "Deleting RAM",
           "Changing the ALU model",
           "Creating a CPU core"],
          "Copying RAM buffers to persistent storage",
          "Save = persist.", "easy"),
    ],
    exercises=[
        ex("cf-storage-ex1", "Save vs run",
           "Describe the path of a `.c` or `.py` file from disk → editor (RAM) → save (disk) → run (load into RAM, CPU executes). "
           "Five to eight sentences."),
    ],
)

_add(
    "cf-instruction-execution",
    hours=0.5,
    objective="Describe fetch-decode-execute at a conceptual level.",
    explanation=(
        "The processor repeats: fetch the next instruction from memory, decode what it means, execute it (often with the ALU), "
        "then continue. A simple assignment becomes several instructions. CS50 Week 1 shows source becoming machine code; "
        "it does not walk microarchitecture pipelines."
    ),
    mastery=[
        "Walk through fetch-decode-execute without notes.",
        "Relate a simple statement to an instruction stream.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-instruction-execution-reference", "CS50x 2026 Week 1 (machine code)", CS50_W1, "CS50x", "REFERENCE", "interactive_tutorial", 0,
          "See that compiled programs are instruction streams. Pipeline detail is this lesson's explanation."),
    ],
    questions=[
        q("cf-instruction-execution-q1", "In fetch-decode-execute, what is fetched?",
          ["A random file from the internet", "The next instruction (and as needed its data) from memory",
           "The entire SSD", "Only environment variables"],
          "The next instruction (and as needed its data) from memory",
          "Fetch from memory into the CPU.", "easy", True),
        q("cf-instruction-execution-q2", "Decode means:",
          ["Delete the source file", "Interpret the bit pattern as an operation and operands",
           "Format the disk", "Open a pull request"],
          "Interpret the bit pattern as an operation and operands",
          "Instruction encoding.", "medium", True),
        q("cf-instruction-execution-q3", "Why is `x = x + 1` more than one hardware step?",
          ["High-level statements compile to multiple instructions (load, add, store).",
           "The ALU cannot add 1.",
           "RAM forbids plus.",
           "Hexadecimal cannot represent x."],
          "High-level statements compile to multiple instructions (load, add, store).",
          "One line ≠ one cycle necessarily.", "medium"),
        q("cf-instruction-execution-q4", "What happens after execute in the simple model?",
          ["The computer always shuts down.",
           "The CPU continues with the next instruction (unless a jump/branch).",
           "Git auto-commits.",
           "All cache is erased by law."],
          "The CPU continues with the next instruction (unless a jump/branch).",
          "Sequential execution plus branches.", "easy"),
    ],
    exercises=[
        ex("cf-instruction-execution-ex1", "Pipeline in words",
           "Explain fetch-decode-execute for `x = x + 1` in your own words. Include where RAM and registers appear. "
           "Half a page is enough."),
    ],
)

_add(
    "cf-machine-code",
    hours=0.5,
    objective="Explain machine code as the CPU's native language.",
    explanation=(
        "Machine code is the binary instruction encoding a CPU family can execute. It is architecture-specific. "
        "CS50 Week 1: source code is compiled to machine code you can run."
    ),
    mastery=[
        "Contrast machine code with a high-level language.",
        "Explain why machine code is architecture-specific.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-machine-code-primary", "CS50x 2026 Week 1 (source vs machine code)", CS50_W1, "CS50x", "PRIMARY", "interactive_tutorial", 0,
          "Source code, machine code, and compiler sections. You do not need to finish Problem Set 1."),
        r("cf-machine-code-reference", "CS50x 2026 Lecture 1 notes", CS50_N1, "CS50x", "REFERENCE", "documentation", 1,
          "Official notes on compiling source to a runnable program."),
    ],
    questions=[
        q("cf-machine-code-q1", "Machine code is best described as:",
          ["English comments in a README", "Binary instructions for a particular CPU family",
           "Only Python bytecode", "Git commit hashes"],
          "Binary instructions for a particular CPU family",
          "Week 1: compiler produces machine code.", "easy", True),
        q("cf-machine-code-q2", "Why might a Windows .exe fail to run on a phone CPU as-is?",
          ["Phones cannot store files.",
           "Instruction sets and OS ABIs differ; the bytes are not the same language.",
           "Hex is illegal on phones.",
           "Git is missing."],
          "Instruction sets and OS ABIs differ; the bytes are not the same language.",
          "Architecture + OS.", "medium", True),
        q("cf-machine-code-q3", "What does CS50's `make hello` step produce conceptually?",
          ["Only a PDF", "An executable (machine code) from C source",
           "A GitHub pull request", "A disk partition"],
          "An executable (machine code) from C source",
          "Week 1 walkthrough uses make/clang.", "easy"),
        q("cf-machine-code-q4", "High-level source is easier for humans because:",
          ["CPUs read C faster than binary.",
           "Names, structure, and abstraction hide instruction details.",
           "Machine code cannot represent loops.",
           "Compilers delete comments into RAM."],
          "Names, structure, and abstraction hide instruction details.",
          "Abstraction from Week 0/1.", "medium"),
    ],
    exercises=[
        ex("cf-machine-code-ex1", "Source to execution story",
           "After skimming CS50 Week 1's source/machine code/compiler sections, write the chain: "
           "source file → compiler → machine code → loader/RAM → CPU. Do not submit CS50 problem sets."),
    ],
)

_add(
    "cf-compiler",
    hours=0.75,
    objective="Explain what a compiler produces and when it runs.",
    explanation=(
        "A compiler translates source into machine code or bytecode before the program runs (compile time vs run time). "
        "CS50 Week 1 is the selected primary: clang/make turning .c into a runnable file."
    ),
    mastery=[
        "Explain compile-time vs run-time.",
        "Contrast compiling with interpreting.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-compiler-primary", "CS50x 2026 Week 1 (compiler)", CS50_W1, "CS50x", "PRIMARY", "interactive_tutorial", 0,
          "Compiler, correctness, and the make/clang workflow. Skip remaining Week 1 C syntax you do not need yet."),
        r("cf-compiler-reference", "CS50x 2026 Lecture 1 notes (compiler)", CS50_N1, "CS50x", "REFERENCE", "documentation", 1,
          "Notes describing compilation."),
    ],
    questions=[
        q("cf-compiler-q1", "When does a traditional C compiler run relative to the user running the program?",
          ["After every CPU fetch", "Before execution, producing an executable",
           "Only when the disk is full", "Instead of Git"],
          "Before execution, producing an executable",
          "Compile then run.", "easy", True),
        q("cf-compiler-q2", "A compiler error vs a runtime crash: which is compile-time?",
          ["Division by zero while the program is already running",
           "The compiler rejecting invalid source before an executable is produced",
           "The OS killing a process for using too much RAM",
           "A merge conflict"],
          "The compiler rejecting invalid source before an executable is produced",
          "Compile-time diagnostics.", "medium", True),
        q("cf-compiler-q3", "Why can compiled machine code run without the original .c file?",
          ["The CPU executes the generated instructions, not the C text.",
           "C files are copied into the ALU.",
           "Compilers delete RAM.",
           "Git stores C inside the CPU."],
          "The CPU executes the generated instructions, not the C text.",
          "Source is for humans and the compiler.", "easy"),
        q("cf-compiler-q4", "CS50 mentions correctness, design, and style. Which is closest to 'the program meets the spec'?",
          ["Style", "Correctness", "Syntax highlighting color", "The length of the file name"],
          "Correctness",
          "Week 1 lists correctness separately from style.", "easy"),
    ],
    exercises=[
        ex("cf-compiler-ex1", "Compile vs run",
           "Using CS50 Week 1 as reference (you may use any C toolchain you already have, or just write the steps): "
           "list compile-time vs run-time for a tiny program. Name one error that shows up at each time. "
           "You are not required to complete CS50 PSet 1."),
    ],
)

_add(
    "cf-interpreter",
    hours=0.5,
    objective="Explain how an interpreter executes source or bytecode.",
    explanation=(
        "An interpreter executes a program by analyzing and running it incrementally (or running bytecode on a VM). "
        "You often need the language runtime installed. CS50 Week 1 is compiler-centric; this lesson supplies the contrast. "
        "Python is a familiar interpreted/VM example you may already know from C++-adjacent tooling."
    ),
    mastery=[
        "Give one advantage and one cost of interpretation.",
        "Relate interpreters to virtual machines at a high level.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-interpreter-reference", "CS50x 2026 Week 1 (compiler contrast)", CS50_W1, "CS50x", "REFERENCE", "interactive_tutorial", 0,
          "Use as the compiled baseline to contrast with interpretation. Week 1 does not replace a Python VM course."),
    ],
    questions=[
        q("cf-interpreter-q1", "Compared with ahead-of-time compilation, interpretation typically:",
          ["Never needs a language runtime installed",
           "Can start running source with less of a separate compile step, often at a speed cost",
           "Produces a single .exe that never needs Python/Java installed",
           "Removes the need for algorithms"],
          "Can start running source with less of a separate compile step, often at a speed cost",
          "Tradeoff: convenience vs overhead.", "medium", True),
        q("cf-interpreter-q2", "A JVM running Java bytecode is closest to:",
          ["A disk formatter", "A virtual machine interpreting/JITing portable instructions",
           "A Git remote", "An SSD controller"],
          "A virtual machine interpreting/JITing portable instructions",
          "Preview for Domain 1 JVM; conceptual only.", "medium"),
        q("cf-interpreter-q3", "If you copy a `.py` file to a machine without Python, what fails?",
          ["The bits cannot be stored.",
           "There is no interpreter/runtime to execute it.",
           "Hexadecimal turns off.",
           "The CPU cannot add."],
          "There is no interpreter/runtime to execute it.",
          "Runtime dependency.", "easy", True),
        q("cf-interpreter-q4", "Compiling and interpreting can mix because:",
          ["Some languages compile to bytecode that a VM then runs.",
           "Interpreters delete compilers.",
           "CPUs refuse bytecode.",
           "Git merges them automatically."],
          "Some languages compile to bytecode that a VM then runs.",
          "Java/Python models.", "medium"),
    ],
    exercises=[
        ex("cf-interpreter-ex1", "Contrast table",
           "Make a 4-row table: C compiled with clang vs a Python script. Columns: when translation happens, "
           "what you distribute, what the user must install, one typical error timing. Use Week 1 as the C side."),
    ],
)

_add(
    "cf-program",
    hours=0.4,
    objective="Define a program as stored instructions plus data.",
    explanation=(
        "A program is an artifact: source, maybe compiled form, sitting on storage. It is not yet a running process. "
        "CS50 Week 1 treats .c and the executable as program forms."
    ),
    mastery=[
        "Distinguish a program on disk from a running process.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-program-primary", "CS50x 2026 Week 1 (source and executable)", CS50_W1, "CS50x", "PRIMARY", "interactive_tutorial", 0,
          "Treat hello.c and the compiled hello as two forms of a program."),
    ],
    questions=[
        q("cf-program-q1", "A `.exe` or ELF file on disk is:",
          ["A process", "A program (stored instructions), not yet running",
           "Always the kernel", "A Git branch"],
          "A program (stored instructions), not yet running",
          "Program vs process is the next topic.", "easy", True),
        q("cf-program-q2", "Two students each run the same compiled game. How many programs vs processes?",
          ["Two programs and one process", "One program file (copies exist) and two processes",
           "Zero programs", "Two kernels"],
          "One program file (copies exist) and two processes",
          "Same artifact, two executions.", "medium", True),
        q("cf-program-q3", "Source code is a program form because:",
          ["It is instructions (for humans and tools) that can become execution",
           "It is already scheduled by the kernel as a process",
           "It is RAM",
           "It is a CPU core"],
          "It is instructions (for humans and tools) that can become execution",
          "Still an artifact.", "easy"),
        q("cf-program-q4", "Deleting the source after compiling C typically:",
          ["Stops the already-built executable from being a program",
           "Does not remove the executable program from disk",
           "Erases the CPU",
           "Converts Git into RAM"],
          "Does not remove the executable program from disk",
          "Two artifacts.", "easy"),
    ],
    exercises=[
        ex("cf-program-ex1", "Artifact list",
           "Pick any small project you have (even a single script). List the artifacts that count as 'the program' "
           "(source, compiled output, scripts). State which are sufficient to run it on another machine."),
    ],
)

_add(
    "cf-process",
    hours=0.5,
    objective="Define a process as a running instance of a program.",
    explanation=(
        "A process is the OS's running instance of a program: its own memory space, open files, and identity (PID). "
        "The same program can have many processes. MIT Missing Semester's shell lecture shows the shell starting programs; "
        "it is not a full OS textbook."
    ),
    mastery=[
        "Explain program vs process without notes.",
        "List what a process typically owns (memory, files) at a high level.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-process-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "How a shell starts programs as executing commands. Pair with this lesson's program vs process explanation."),
        r("cf-process-reference", "CS50x 2026 Week 1 (running a compiled program)", CS50_W1, "CS50x", "REFERENCE", "interactive_tutorial", 1,
          "./hello is starting a process from a program."),
    ],
    questions=[
        q("cf-process-q1", "Program vs process: which pair is correct?",
          ["Process is the file on disk; program is the PID.",
           "Program is the stored artifact; process is a running instance with a PID.",
           "They are always identical.",
           "Processes exist only in Git."],
          "Program is the stored artifact; process is a running instance with a PID.",
          "Core OS distinction.", "easy", True),
        q("cf-process-q2", "Why can you run two terminals at once?",
          ["The CPU clones itself in hardware permanently.",
           "The OS can create multiple processes, even from the same shell program.",
           "RAM forbids a second window.",
           "Hexadecimal multiplexing."],
          "The OS can create multiple processes, even from the same shell program.",
          "Multiple instances.", "medium", True),
        q("cf-process-q3", "Which is owned by a process rather than by the program file on disk?",
          ["The original source bytes on SSD", "Its current stack, heap, and open file descriptors",
           "The compiler vendor's trademark", "The Git book chapter list"],
          "Its current stack, heap, and open file descriptors",
          "Runtime state.", "medium"),
        q("cf-process-q4", "When a process exits, the program file typically:",
          ["Is deleted from disk automatically", "Remains on disk; the instance is gone",
           "Becomes a CPU register", "Turns into a thread chip"],
          "Remains on disk; the instance is gone",
          "Artifact vs instance.", "easy"),
    ],
    exercises=[
        ex("cf-process-ex1", "Name two instances",
           f"{WSL} Open two shells. In each, run a command that lasts a few seconds (e.g. `sleep 20`). "
           "In a third shell run `ps` or `pgrep sleep` and record two PIDs. Write two sentences: same program, two processes."),
    ],
)
