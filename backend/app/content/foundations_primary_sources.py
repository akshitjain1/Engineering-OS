"""The page each foundations topic should open, and why.

Forty-nine of the sixty-four foundations topics did not have a page of their
own. One MIT lecture -- "Course Overview + Introduction to the Shell" -- was
the PRIMARY source for **fourteen** of them: Process, Processes, Filesystems,
Permissions, Command line, Filesystem navigation, Files, Pipes, Redirection,
grep, find, Permissions again, Processes again. A CS50 week page served four
more. That is why the same complaint kept arriving in different words: click
"Pipes", land on a general shell lecture; click "System calls", land on a
lecture about debugging.

Same shape as dsa_primary_sources: slug -> (url, why). Titles are never written
here -- apply_foundations_primary_sources reads the real title off the live
page, so a title in the database is always one that a server actually served.

Nothing in SOURCES is written unless the page's own <title> or <h1> names the
topic, judged by audit_topic_relevance. ACCEPTED is the pressure valve for the
handful where the right page genuinely does not say the topic's name in its
title, and each entry has to say why in prose. That list is meant to stay
short and to be read.
"""

from __future__ import annotations

G = "https://www.geeksforgeeks.org"

#: slug -> (url, why this page and not the one it replaces)
SOURCES: dict[str, tuple[str, str]] = {
    # ---- the reported case ------------------------------------------------
    "cf-system-calls": (
        f"{G}/operating-systems/introduction-of-system-call/",
        "Was MIT's Debugging and Profiling lecture, where system calls are one "
        "section out of twenty-two. This page is about nothing else.",
    ),

    # ---- the fourteen topics that shared one shell lecture ----------------
    "cf-process": (
        f"{G}/operating-systems/introduction-of-process-management/",
        "What a process is, before the shell commands that list them.",
    ),
    "cf-os-processes": (
        f"{G}/operating-systems/states-of-a-process-in-operating-systems/",
        "The lifecycle -- new, ready, running, waiting, terminated -- which is "
        "the part of 'Processes' the OS module is asking about.",
    ),
    "cf-linux-processes": (
        f"{G}/linux-unix/process-management-in-linux/",
        "The same idea from the shell side: ps, jobs, kill, background.",
    ),
    "cf-command-line": (
        "https://ubuntu.com/tutorials/command-line-for-beginners",
        "A first hour at a prompt, written for someone who has not used one.",
    ),
    "cf-linux-files": (
        f"{G}/linux-unix/linux-file-system/",
        "How files are laid out and typed on Linux -- 'everything is a file' "
        "made concrete.",
    ),
    "cf-filesystems": (
        f"{G}/operating-systems/file-systems-in-operating-system/",
        "How a filesystem is organised, rather than how to walk one.",
    ),
    "cf-pipes": (
        f"{G}/linux-unix/piping-in-unix-or-linux/",
        "One idea, one page: stdout of the left becomes stdin of the right.",
    ),
    "cf-redirection": (
        f"{G}/linux-unix/input-output-redirection-in-linux/",
        "The other half of the pipe story, and the one the shell lecture "
        "covers in two lines.",
    ),
    "cf-grep": (
        f"{G}/linux-unix/grep-command-in-unixlinux/",
        "grep with its flags, which is what a day on grep needs.",
    ),
    "cf-find": (
        f"{G}/linux-unix/find-command-in-linux-with-examples/",
        "find with worked examples; the shell lecture mentions it once.",
    ),
    "cf-os-permissions": (
        f"{G}/linux-unix/permissions-in-linux/",
        "rwx, owner/group/other, and the octal form.",
    ),
    # cf-linux-permissions and cf-os-permissions are two topics for one idea
    # (see DUPLICATES below), so they get the same correct page. Two topics
    # sharing a page written about exactly that subject is not the defect this
    # file exists to fix -- fourteen topics sharing a general lecture was.
    "cf-linux-permissions": (
        f"{G}/linux-unix/permissions-in-linux/",
        "rwx, owner/group/other, and the octal form.",
    ),

    # ---- the CS50 week pages ----------------------------------------------
    "cf-pseudocode": (
        f"{G}/dsa/what-is-pseudocode-a-complete-tutorial/",
        "Was CS50 Week 0, which is a whole week's lecture in Scratch.",
    ),
    "cf-algorithms": (
        f"{G}/dsa/introduction-to-algorithms/",
        "Was CS50 Week 0.",
    ),
    "cf-time-complexity-intro": (
        f"{G}/dsa/understanding-time-complexity-simple-examples/",
        "Was CS50 Week 0. Big-O by example, which is the right first pass.",
    ),
    "cf-problem-decomposition": (
        f"{G}/what-is-problem-decomposition/",
        "Was CS50 Week 0, a full week's lecture in Scratch.",
    ),
    "cf-compiler": (
        f"{G}/compiler-design/phases-of-a-compiler/",
        "Was CS50 Week 1 (C). The phases are the substance of the topic, and "
        "this also stops it duplicating cf-dev-compiler's page.",
    ),
    "cf-program": (
        f"{G}/computer-science-fundamentals/difference-between-program-and-process/",
        "Was CS50 Week 1. A program is best defined against a process, which "
        "is also the distinction the next module leans on.",
    ),
    "cf-machine-code": (
        "https://en.wikipedia.org/wiki/Machine_code",
        "Was CS50 Week 1. GeeksforGeeks files this under 'machine language'; "
        "this page is titled with the term the curriculum uses.",
    ),

    # ---- MIT command-line-environment, three topics -----------------------
    "cf-os-environment-variables": (
        f"{G}/linux-unix/environment-variables-in-linux-unix/",
        "What they are and how the shell passes them down.",
    ),
    # Also a duplicate pair; GeeksforGeeks has no separate "setting them" page.
    "cf-linux-environment-variables": (
        f"{G}/linux-unix/environment-variables-in-linux-unix/",
        "What they are and how the shell passes them down.",
    ),
    "cf-package-management": (
        f"{G}/linux-unix/package-management-commands-in-linux/",
        "apt/yum/dnf as commands you run.",
    ),
    "cf-dev-package-manager": (
        f"{G}/linux-unix/understanding-package-managers-and-systemctl/",
        "What a package manager is, before which one you type.",
    ),

    # ---- sources that could not be read at all ----------------------------
    # These were a YouTube watch page or a PDF: correct material, possibly, but
    # nothing about them can be verified, and three number-system topics shared
    # one video with no timestamps.
    "cf-bits-and-bytes": (
        "https://web.stanford.edu/class/cs101/bits-bytes.html",
        "Was one YouTube video shared by three topics with no timestamps.",
    ),
    "cf-binary": (
        f"{G}/digital-logic/binary-number-system/",
        "Was the same shared video.",
    ),
    "cf-hexadecimal": (
        f"{G}/digital-logic/hexadecimal-number-system/",
        "Was the same shared video.",
    ),
    "cf-interpreter": (
        f"{G}/compiler-design/introduction-to-interpreters/",
        "Was a YouTube video.",
    ),
    "cf-space-complexity-intro": (
        f"{G}/dsa/g-fact-86/",
        "Was a YouTube video.",
    ),
    "cf-virtual-memory-basics": (
        f"{G}/operating-systems/virtual-memory-in-operating-system/",
        "Was an OSTEP PDF chapter. The PDF stays as the deep dive.",
    ),
    "cf-edge-cases": (
        f"{G}/python/dont-forget-edge-cases/",
        "Was a CMU PDF handout.",
    ),

    # ---- other topics on a page about something larger --------------------
    "cf-storage": (
        f"{G}/computer-science-fundamentals/what-is-a-storage-device-definition-types-examples/",
        "Was the memory-hierarchy page, where storage is the bottom row.",
    ),
    "cf-instruction-execution": (
        f"{G}/operating-systems/instruction-execution-in-operating-system/",
        "Was the instruction-cycles page, which is a taxonomy of cycles.",
    ),
    "cf-debugger": (
        f"{G}/operating-systems/what-is-debuggers/",
        "Was VS Code's debugging docs -- one editor's UI, not the idea.",
    ),
    "cf-reset-revert": (
        f"{G}/git/git-difference-between-git-revert-checkout-and-reset/",
        "Was the Git book's 'Undoing Things', which covers six commands; the "
        "topic is specifically reset versus revert.",
    ),
    "cf-conflicts": (
        f"{G}/git/merge-conflicts-and-how-to-handle-them/",
        "Was the Git book's 'Basic Branching and Merging', seventeen sections "
        "of which conflicts are one. Shared its page with cf-merge.",
    ),
    "cf-ide": (
        f"{G}/blogs/what-is-ide/",
        "Was a VS Code tutorial, which teaches one IDE rather than the idea.",
    ),
}


#: slug -> why the existing page is right even though the audit will flag it.
#:
#: Every entry here is a case where the best available page does not put the
#: topic's name in its title. They are listed so the audit can stop reporting
#: them without the exemption being invisible, and so the reason survives.
ACCEPTED: dict[str, str] = {
    "cf-formatter":
        "MIT's Code Quality lecture is the right lesson on formatters, and "
        "GeeksforGeeks only has per-language Prettier setup guides. Flagged "
        "because the title says 'Code Quality'.",
    "cf-linter":
        "Same lecture, same reason. The alternatives are ESLint and ktlint "
        "pages, which teach one tool in one language.",
    "cf-build-system":
        "makefiletutorial.com is the best build-system material there is; its "
        "title is 'Makefile Tutorial By Example', which names the tool rather "
        "than the concept.",
    "cf-dry-runs":
        "The FutureLogic page is titled 'Trace Tables', which is exactly what "
        "a dry run is and is the term the syllabus it comes from uses.",
    "cf-filesystem-navigation":
        "Navigating a filesystem is cd, pwd and ls; the cd page teaches it. No "
        "page is titled 'filesystem navigation' because nobody writes that.",
    "cf-github-workflow":
        "GitHub's own Hello World walks the whole loop -- branch, commit, PR, "
        "merge -- and is titled 'Hello World'.",
    "cf-commits":
        "The Git book's 'Recording Changes to the Repository' is the chapter on "
        "committing. git-scm's git-commit man page has the word in the title "
        "and is a reference, not a lesson.",
    "cf-pull-push":
        "The Git book's 'Working with Remotes' is the chapter that teaches both "
        "halves. GeeksforGeeks splits them into a 'Git Push' page and a 'Git "
        "Pull' page, and a topic named 'Pull and push' wants the two together.",
    "cf-shell":
        "MIT's shell lecture is the correct page for the topic named 'Shell'. "
        "It stays; the other thirteen topics that pointed here do not.",
    "cf-debugging-thinking":
        "MIT's Debugging and Profiling lecture is the right page for a topic "
        "named 'Debugging'. It keeps this one and loses System calls.",
}


#: Topics that are the same topic twice, found while doing the above.
#:
#: Not fixed here, because merging or renaming curriculum topics changes the
#: shape of the plan and the progress already recorded against them -- that is
#: a decision, not a repair. Recorded so it is not rediscovered a third time.
DUPLICATES = (
    ("cf-process", "cf-os-processes", "cf-linux-processes"),   # three "Process(es)"
    ("cf-os-permissions", "cf-linux-permissions"),            # two "Permissions"
    ("cf-os-environment-variables", "cf-linux-environment-variables"),
    ("cf-compiler", "cf-dev-compiler"),                       # two "Compiler"
    ("cf-package-management", "cf-dev-package-manager"),
)
