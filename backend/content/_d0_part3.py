"""OS fundamentals topics."""

from __future__ import annotations

from _d0_helpers import CS50_W0, MIT_CLI, MIT_SHELL, WSL, ex, q, r
from _d0_part2 import CONTENT, _add

_add(
    "cf-kernel",
    hours=0.5,
    objective="Explain the kernel as the core of the operating system.",
    explanation=(
        "The kernel is the privileged program that manages hardware, processes, memory, and filesystems. "
        "User programs ask it for services via system calls. Missing Semester is not an OS course; this explanation is the lesson."
    ),
    mastery=["Explain kernel vs user programs without notes.", "Score >= 80%."],
    resources=[
        r("cf-kernel-reference", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "REFERENCE", "article", 0,
          "User-level programs run with OS support. Not a kernel-internals lecture."),
    ],
    questions=[
        q("cf-kernel-q1", "The kernel's role is closest to:",
          ["A text editor theme", "The privileged core that mediates hardware and processes", "A CSS color", "A Git alias"],
          "The privileged core that mediates hardware and processes", "User programs are not the kernel.", "easy", True),
        q("cf-kernel-q2", "Why don't ordinary apps talk to the disk controller directly?",
          ["Disks reject electricity.", "The kernel provides controlled access so programs cannot corrupt the machine at will.",
           "Compilers forbid files.", "Hexadecimal disk mode."],
          "The kernel provides controlled access so programs cannot corrupt the machine at will.", "Protection and sharing.", "medium", True),
        q("cf-kernel-q3", "A crash in a user process vs a kernel panic: which is usually worse for the whole machine?",
          ["User process crash always stops all other apps by hardware law",
           "Kernel failure can take down the system; a user crash is usually isolated", "They are identical", "Only Git panics"],
          "Kernel failure can take down the system; a user crash is usually isolated", "Privilege.", "medium"),
        q("cf-kernel-q4", "ls and bash are:",
          ["The kernel itself", "User programs that request kernel services", "CPU registers", "SSD firmware only"],
          "User programs that request kernel services", "Shell lecture programs.", "easy"),
    ],
    exercises=[
        ex("cf-kernel-ex1", "Kernel in one page",
           "Write a half-page: what the kernel does, what a user program does, and one example of something only the kernel should do "
           "(schedule processes, talk to devices, enforce permissions). Do not claim Missing Semester taught kernel internals."),
    ],
)

_add(
    "cf-os-processes",
    hours=0.5,
    objective="Describe how the OS manages processes.",
    explanation="The OS creates, schedules, and isolates processes. Each process has an identity and resources.",
    mastery=["Explain process creation at a high level.", "Contrast process and program.", "Score >= 80%."],
    resources=[
        r("cf-os-processes-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Commands run as processes. Pair with ps later."),
    ],
    questions=[
        q("cf-os-processes-q1", "Isolation between processes mainly means:",
          ["They share one PID", "One process's memory is not freely writable by another", "They cannot use the CPU", "They cannot be listed"],
          "One process's memory is not freely writable by another", "OS isolation.", "medium", True),
        q("cf-os-processes-q2", "A PID is:",
          ["A Git tag", "An identifier the OS assigns to a process", "A hex color", "A compiler flag required by CS50"],
          "An identifier the OS assigns to a process", "You'll see it in ps.", "easy", True),
        q("cf-os-processes-q3", "Scheduling means:",
          ["Deleting RAM", "The OS choosing which ready process runs on a CPU over time", "Compiling C", "Formatting disks nightly"],
          "The OS choosing which ready process runs on a CPU over time", "Time sharing.", "easy"),
        q("cf-os-processes-q4", "Starting ls from a shell typically:",
          ["Replaces the kernel", "Creates a process to run ls, then the shell waits or continues", "Writes a Git commit", "Changes the CPU vendor"],
          "Creates a process to run ls, then the shell waits or continues", "Fork/exec conceptually.", "medium"),
    ],
    exercises=[
        ex("cf-os-processes-ex1", "Inspect processes",
           f"{WSL} Run `ps -o pid,ppid,cmd` (or `ps aux | head`). Identify your shell's PID and one child command. Write three sentences: program vs process vs PID."),
    ],
)

_add(
    "cf-threads",
    hours=0.5,
    objective="Contrast threads with processes.",
    explanation=(
        "Threads are multiple execution paths inside one process and share that process's memory. "
        "CS50 Week 0 mentions threads in Scratch as a light analogy only."
    ),
    mastery=["Explain shared memory vs separate processes.", "State one reason programs use threads.", "Score >= 80%."],
    resources=[
        r("cf-threads-reference", "CS50x 2026 Week 0 (Scratch threads mention)", CS50_W0, "CS50x", "REFERENCE", "interactive_tutorial", 0,
          "Scratch events/threads are a metaphor, not an OS threads course."),
    ],
    questions=[
        q("cf-threads-q1", "Two threads in one process typically share:",
          ["Nothing, like two VMs", "The process address space, unlike two processes", "Two kernels", "Two physical computers only"],
          "The process address space, unlike two processes", "Shared memory.", "medium", True),
        q("cf-threads-q2", "A reason to use threads:",
          ["To avoid ever using RAM", "To overlap waiting (I/O) or use multiple cores inside one program", "To replace Git", "To make bits become decimal"],
          "To overlap waiting (I/O) or use multiple cores inside one program", "Concurrency inside a process.", "medium", True),
        q("cf-threads-q3", "A race condition is more likely when:",
          ["Threads share memory and update it without coordination", "Two processes never communicate", "The disk is an SSD", "You use hexadecimal"],
          "Threads share memory and update it without coordination", "Preview of later concurrency.", "medium"),
        q("cf-threads-q4", "Killing a process typically:",
          ["Leaves all its threads running independently forever", "Ends the threads that belonged to it", "Formats the SSD", "Uninstalls the kernel"],
          "Ends the threads that belonged to it", "Threads live in a process.", "easy"),
    ],
    exercises=[
        ex("cf-threads-ex1", "Process vs thread paragraph",
           "Write two short paragraphs: (1) when you would use threads vs processes; (2) one risk of shared memory. No code required."),
    ],
)

_add(
    "cf-system-calls",
    hours=0.5,
    objective="Explain system calls as the program–kernel interface.",
    explanation="A system call is how a user program asks the kernel to do privileged work such as reading a file or creating a process.",
    mastery=["Trace a simple system call conceptually (e.g. write to the terminal).", "Score >= 80%."],
    resources=[
        r("cf-system-calls-reference", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "REFERENCE", "article", 0,
          "Programs the shell runs perform I/O via the OS. Details are this lesson."),
    ],
    questions=[
        q("cf-system-calls-q1", "A system call crosses from:",
          ["RAM to SSD only", "User program into the kernel to request a service", "Git to GitHub only", "Hex to decimal"],
          "User program into the kernel to request a service", "The API of the OS.", "easy", True),
        q("cf-system-calls-q2", "Why is opening a file typically a syscall (or wraps one)?",
          ["Files live in the ALU", "Accessing the filesystem/devices is privileged and centralized in the kernel",
           "Compilers cannot name files", "Git requires it for hex"],
          "Accessing the filesystem/devices is privileged and centralized in the kernel", "Protection.", "medium", True),
        q("cf-system-calls-q3", "echo hello showing text involves:",
          ["No kernel, only the CPU cache", "The process eventually asking the kernel to write bytes to the terminal",
           "A Git merge", "RGB conversion"],
          "The process eventually asking the kernel to write bytes to the terminal", "write/syscall conceptually.", "medium"),
        q("cf-system-calls-q4", "User code that only adds two numbers in registers:",
          ["Must always syscall", "Can run in user mode without a syscall", "Always formats the disk", "Always creates a thread"],
          "Can run in user mode without a syscall", "Not every instruction is a syscall.", "easy"),
    ],
    exercises=[
        ex("cf-system-calls-ex1", "Trace echo",
           "Conceptually trace `echo hi`: shell, bytes, kernel write to the terminal. Five to eight sentences. "
           f"Optional: `{WSL}` `strace -e write echo hi`."),
    ],
)

_add(
    "cf-os-memory",
    hours=0.45,
    objective="Explain that the OS manages process memory.",
    explanation="Each process has an address space. The OS allocates pages and protects regions.",
    mastery=["Explain that process memory is an OS-managed address space.", "Score >= 80%."],
    resources=[],
    questions=[
        q("cf-os-memory-q1", "A process address space is:",
          ["The SSD model number", "The range of virtual addresses the process may use, mapped by the OS",
           "The Git remote URL", "The compiler version"],
          "The range of virtual addresses the process may use, mapped by the OS", "Leads into virtual memory.", "medium", True),
        q("cf-os-memory-q2", "If a process reads memory it does not own:",
          ["The ALU melts", "The OS typically kills it (segmentation fault) rather than allowing corruption of others",
           "Git auto-fixes it", "Hex becomes decimal"],
          "The OS typically kills it (segmentation fault) rather than allowing corruption of others", "Protection.", "medium", True),
        q("cf-os-memory-q3", "Stack vs heap at programmer level:",
          ["Both are disk partitions", "Stack holds call frames/locals; heap is for dynamic allocation",
           "Heap is only for Git objects", "Stack is only for SSDs"],
          "Stack holds call frames/locals; heap is for dynamic allocation", "Enough for Domain 0.", "easy"),
        q("cf-os-memory-q4", "Who decides which physical RAM page backs an address?",
          ["The CSS engine", "The OS (with hardware MMU help)", "The user typing hex", "GitHub Hello World"],
          "The OS (with hardware MMU help)", "Virtual memory next.", "easy"),
    ],
    exercises=[
        ex("cf-os-memory-ex1", "Address space sketch",
           "Sketch a process: code, stack, heap. Label which grows with function calls vs dynamic allocation. One figure plus four sentences."),
    ],
)

_add(
    "cf-virtual-memory-basics",
    hours=0.6,
    objective="Explain virtual vs physical addresses at a high level.",
    explanation="Virtual memory lets each process see its own address space. The OS maps virtual pages to physical frames or swap.",
    mastery=["Explain virtual vs physical addresses in one paragraph.", "Score >= 80%."],
    resources=[],
    questions=[
        q("cf-virtual-memory-basics-q1", "Virtual address means:",
          ["An address that does not exist", "An address in the process's view, translated to physical memory by OS/hardware",
           "Only IPv6", "A Git SHA"],
          "An address in the process's view, translated to physical memory by OS/hardware", "Translation.", "medium", True),
        q("cf-virtual-memory-basics-q2", "A benefit of per-process virtual spaces:",
          ["Processes can reuse similar pointer values without colliding in physical RAM", "Disks become registers",
           "Compilers become kernels", "Bits become analog"],
          "Processes can reuse similar pointer values without colliding in physical RAM", "Isolation plus convenience.", "medium", True),
        q("cf-virtual-memory-basics-q3", "Swap/paging when RAM is tight:",
          ["Deletes the kernel", "Moves idle pages to disk, which can slow the machine", "Converts programs to hex", "Disables the ALU"],
          "Moves idle pages to disk, which can slow the machine", "Capacity vs speed.", "easy"),
        q("cf-virtual-memory-basics-q4", "Physical address is:",
          ["The location in actual RAM (or device memory)", "Always equal to the Git blob id", "Only used by CSS", "A type of syscall name"],
          "The location in actual RAM (or device memory)", "Hardware address.", "easy"),
    ],
    exercises=[
        ex("cf-virtual-memory-basics-ex1", "Why the same number can be reused",
           "Explain in a paragraph why two processes can both have a pointer that looks like the same number without sharing the same physical bytes."),
    ],
)

_add(
    "cf-filesystems",
    hours=0.5,
    objective="Explain files and directories as OS abstractions.",
    explanation="A filesystem presents files and directories on storage. Paths name them. The kernel enforces structure and permissions.",
    mastery=["Explain file vs path at a high level.", "Score >= 80%."],
    resources=[
        r("cf-filesystems-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Directories, paths, and listing files."),
    ],
    questions=[
        q("cf-filesystems-q1", "A path is:",
          ["A CPU instruction", "A name that locates a file or directory in the filesystem tree",
           "A Git rebase option required for all commits", "An ALU mode"],
          "A name that locates a file or directory in the filesystem tree", "Absolute vs relative later.", "easy", True),
        q("cf-filesystems-q2", "Directories exist so that:",
          ["RAM can persist", "Files can be organized hierarchically", "Threads become processes", "Hex is banned"],
          "Files can be organized hierarchically", "Tree.", "easy", True),
        q("cf-filesystems-q3", "`/` at the start of a Unix path usually means:",
          ["Relative to the current directory", "An absolute path from the filesystem root", "A comment", "A Git remote"],
          "An absolute path from the filesystem root", "Unix paths.", "easy"),
        q("cf-filesystems-q4", "The kernel's job regarding files includes:",
          ["Choosing CSS colors", "Enforcing names, access, and the directory tree on storage", "Replacing Git", "Running only Scratch"],
          "Enforcing names, access, and the directory tree on storage", "OS abstraction.", "medium"),
    ],
    exercises=[
        ex("cf-filesystems-ex1", "Tree on paper",
           f"{WSL} Run `ls -l /` and `pwd`. Draw a tiny tree from `/` down to your home directory (3–6 levels). Label directories vs files."),
    ],
)

_add(
    "cf-os-permissions",
    hours=0.5,
    objective="Explain user/group/other permission bits conceptually.",
    explanation="Unix permission bits say who may read, write, or execute a file. The kernel enforces them.",
    mastery=["Read a simple rwx triplet.", "Score >= 80%."],
    resources=[
        r("cf-os-permissions-primary", "MIT Missing Semester 2026 shell lecture (ls -l exercise)", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Official exercise: what do the first 10 characters of ls -l / mean."),
        r("cf-os-permissions-reference", "chmod(1) Linux man page", "https://man7.org/linux/man-pages/man1/chmod.1.html", "man7.org", "REFERENCE", "documentation", 1,
          "Canonical chmod documentation. Skim modes; do not memorize every flag."),
    ],
    questions=[
        q("cf-os-permissions-q1", "In rwxr-xr--, what can others do?",
          ["read, write, execute", "read only", "execute only", "nothing"],
          "read only", "Last triplet r--.", "easy", True),
        q("cf-os-permissions-q2", "Why execute permission on a directory matters:",
          ["It compiles C", "It allows traversing/entering that directory", "It formats the disk", "It creates threads"],
          "It allows traversing/entering that directory", "Directory x = search/enter.", "medium", True),
        q("cf-os-permissions-q3", "Who enforces these bits?",
          ["The CSS engine", "The kernel when a process tries the operation", "GitHub Hello World", "The ALU"],
          "The kernel when a process tries the operation", "OS policy.", "easy"),
        q("cf-os-permissions-q4", "A script with content but no execute bit:",
          ["Always runs via ./script", "May still be run as bash script.sh but not as ./script.sh", "Deletes itself", "Becomes a process automatically"],
          "May still be run as bash script.sh but not as ./script.sh", "MIT chmod +x exercise.", "medium"),
    ],
    exercises=[
        ex("cf-os-permissions-ex1", "Decode ls -l",
           f"{WSL} Complete the Missing Semester prompt: run `ls -l /` and explain the first 10 characters of several lines. Source: {MIT_SHELL}"),
    ],
)

_add(
    "cf-os-environment-variables",
    hours=0.45,
    objective="Explain environment variables as process configuration.",
    explanation="Environment variables are key-value settings inherited by child processes (PATH, HOME).",
    mastery=["Give two examples of environment variables.", "Score >= 80%."],
    resources=[
        r("cf-os-environment-variables-primary", "MIT Missing Semester 2026 — Command-line Environment", MIT_CLI, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Dotfiles and environment configuration."),
        r("cf-os-environment-variables-reference", "environ(7) Linux man page", "https://man7.org/linux/man-pages/man7/environ.7.html", "man7.org", "REFERENCE", "documentation", 1,
          "Canonical description of the environment list."),
    ],
    questions=[
        q("cf-os-environment-variables-q1", "PATH is used to:",
          ["Store Git objects", "Find executables by name without a full path", "Color the CPU", "Replace RAM"],
          "Find executables by name without a full path", "Search path.", "easy", True),
        q("cf-os-environment-variables-q2", "Child processes typically:",
          ["Receive a copy of the parent's environment at start", "Never see PATH", "Share CPU registers with the parent", "Delete HOME"],
          "Receive a copy of the parent's environment at start", "Inheritance.", "medium", True),
        q("cf-os-environment-variables-q3", "export VAR=1 in bash:",
          ["Writes VAR into the kernel image", "Marks VAR to be passed to children", "Creates a Git branch", "Formats /tmp"],
          "Marks VAR to be passed to children", "Export vs shell-local.", "medium"),
        q("cf-os-environment-variables-q4", "HOME usually:",
          ["Is your home directory path", "Is the CPU model", "Is a hex color", "Is a syscall number"],
          "Is your home directory path", "Common example.", "easy"),
    ],
    exercises=[
        ex("cf-os-environment-variables-ex1", "Print PATH",
           f"{WSL} Run `echo $PATH` and `printenv | head`. Pick one PATH entry and explain what kinds of programs live there. Do not paste secrets."),
    ],
)
