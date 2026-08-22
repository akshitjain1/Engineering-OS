"""Terminal and Linux topics."""

from __future__ import annotations

from _d0_helpers import MIT_CLI, MIT_SHELL, MIT_SHIP, WSL, ex, q, r
from _d0_part3 import CONTENT, _add

_add(
    "cf-shell",
    hours=0.75,
    objective="Explain the shell as a command interpreter.",
    explanation=(
        "The shell reads commands and starts programs. Bash/Zsh are Unix shells. "
        "Windows users must use WSL or a Linux VM. PowerShell is a different ecosystem, not the target."
    ),
    mastery=[
        "Start a Unix shell and state what it does.",
        "Complete the official shell-identification check from Missing Semester.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-shell-primary", "MIT Missing Semester 2026 — Course Overview + Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Entire lecture plus official exercises at the bottom. Use WSL on Windows."),
        r("cf-shell-practice", "Official Missing Semester 2026 shell exercises", MIT_SHELL, "MIT Missing Semester 2026", "PRACTICE", "exercise", 1,
          "Work the official exercises on that page. Do not copy them into notes as if they were original."),
    ],
    questions=[
        q("cf-shell-q1", "The shell is:",
          ["The kernel", "A program that interprets commands and starts other programs", "A type of SSD", "GitHub itself"],
          "A program that interprets commands and starts other programs", "Lecture 1.", "easy", True),
        q("cf-shell-q2", "Why must cd be a shell builtin?",
          ["Disks cannot store cd", "A child process cannot change the parent's working directory",
           "Kernels forbid directories", "Hexadecimal paths"],
          "A child process cannot change the parent's working directory", "Official MIT exercise prompt.", "hard", True),
        q("cf-shell-q3", "On Windows for this curriculum you should use:",
          ["PowerShell as a full substitute for Bash", "WSL or a Linux VM for a Unix shell", "Only File Explorer", "Only cmd.exe"],
          "WSL or a Linux VM for a Unix shell", "Course requirement.", "easy", True),
        q("cf-shell-q4", "echo $SHELL showing /bin/bash means:",
          ["You are in PowerShell", "You are likely in a Unix-style shell suitable for this module", "Git is broken", "The CPU is 32-bit"],
          "You are likely in a Unix-style shell suitable for this module", "MIT setup check.", "easy"),
    ],
    exercises=[
        ex("cf-shell-ex1", "Verify Unix shell",
           f"{WSL} Follow Missing Semester: run `echo $SHELL`. Confirm bash or zsh. Then explain in two sentences what the shell did when you ran that command. Source: {MIT_SHELL}"),
    ],
)

_add(
    "cf-command-line",
    hours=1.0,
    objective="Issue basic commands with arguments.",
    explanation=(
        "Commands have a name, arguments, flags, stdin/stdout/stderr, and an exit status. "
        "Official MIT exercises cover quoting, exit codes, and conditionals."
    ),
    mastery=[
        "Explain command, arguments, and exit status.",
        "Use quoting correctly in a small example.",
        "Score >= 80%.",
    ],
    resources=[
        r("cf-command-line-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Arguments, programs, and the official quoting/exit-status exercises."),
        r("cf-command-line-reference", "Bash manual — Quoting", "https://www.gnu.org/software/bash/manual/html_node/Quoting.html", "GNU Bash", "REFERENCE", "documentation", 1,
          "Canonical quoting rules referenced by the MIT exercise."),
    ],
    questions=[
        q("cf-command-line-q1", "Exit status 0 conventionally means:",
          ["Crash", "Success", "File not found always", "Need sudo"],
          "Success", "$? and MIT exercise.", "easy", True),
        q("cf-command-line-q2", "Single quotes vs double quotes in bash:",
          ["They are identical", "Single quotes take the string literally; double quotes still expand $ variables",
           "Double quotes disable everything including spaces", "Quotes only work in PowerShell"],
          "Single quotes take the string literally; double quotes still expand $ variables", "MIT quoting exercise.", "medium", True),
        q("cf-command-line-q3", "`&&` runs the next command when:",
          ["The previous failed", "The previous succeeded (exit 0)", "Always in parallel", "Never"],
          "The previous succeeded (exit 0)", "MIT && / || exercise.", "easy"),
        q("cf-command-line-q4", "A flag like -l is:",
          ["A kernel panic", "An argument that changes command behavior", "A Git commit", "A CPU register"],
          "An argument that changes command behavior", "ls -l.", "easy"),
    ],
    exercises=[
        ex("cf-command-line-ex1", "Quoting and exit status",
           f"{WSL} Do the official MIT exercises on quoting, `$?`, and `&&`/`||` (including creating `/tmp/mydir` only if missing). Source: {MIT_SHELL}"),
    ],
)

_add(
    "cf-filesystem-navigation",
    hours=0.75,
    objective="Move around the filesystem with pwd, ls, and cd.",
    explanation="pwd, ls, and cd are the core navigation tools. Relative vs absolute paths. MIT shell lecture is primary.",
    mastery=["Navigate to a nested directory without a GUI.", "Score >= 80%."],
    resources=[
        r("cf-filesystem-navigation-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "cd, pwd, ls, paths. Official glob exercise is related."),
    ],
    questions=[
        q("cf-filesystem-navigation-q1", "pwd prints:",
          ["The kernel version", "The current working directory", "Git remotes", "CPU temperature"],
          "The current working directory", "Working directory.", "easy", True),
        q("cf-filesystem-navigation-q2", "cd .. means:",
          ["Go to root always", "Go to the parent directory", "Delete the directory", "Compile C"],
          "Go to the parent directory", "Relative path.", "easy", True),
        q("cf-filesystem-navigation-q3", "ls vs ls /tmp:",
          ["Identical always", "ls lists the current directory; ls /tmp lists that path", "ls only works in Git", "ls formats disks"],
          "ls lists the current directory; ls /tmp lists that path", "Argument is a path.", "easy"),
        q("cf-filesystem-navigation-q4", "A glob like *.txt is:",
          ["A Git SHA", "A pattern the shell expands to matching filenames", "A syscall", "An ALU opcode"],
          "A pattern the shell expands to matching filenames", "MIT glob exercise.", "medium", True),
    ],
    exercises=[
        ex("cf-filesystem-navigation-ex1", "Navigate and globs",
           f"{WSL} From home, `mkdir -p d0-nav/a/b`, `cd` into b, `pwd`, `cd ~`. Then do the official MIT glob experiment "
           f"(test directory, ls *.txt, file?.txt, {{a,b,c}}.txt). Source: {MIT_SHELL}"),
    ],
)

_add(
    "cf-linux-files",
    hours=0.75,
    objective="Create, copy, move, and delete files from the terminal.",
    explanation="touch, cp, mv, rm, mkdir, rmdir. Be careful with rm. Official MIT exercises include executable files and scripts.",
    mastery=["Use core file commands independently.", "Score >= 80%."],
    resources=[
        r("cf-linux-files-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Files as named bytes; later exercises save scripts to disk."),
    ],
    questions=[
        q("cf-linux-files-q1", "cp a b when b does not exist typically:",
          ["Deletes a", "Copies a's content to a new file named b", "Creates a Git commit", "Formats /"],
          "Copies a's content to a new file named b", "Copy.", "easy", True),
        q("cf-linux-files-q2", "mv is used to:",
          ["Only change permissions", "Rename or move a file", "Compile C", "Start the kernel"],
          "Rename or move a file", "Move/rename.", "easy", True),
        q("cf-linux-files-q3", "Why is rm without trash dangerous?",
          ["It always fails", "It unlinks the name immediately; recovery is not guaranteed", "It only works in PowerShell", "It creates threads"],
          "It unlinks the name immediately; recovery is not guaranteed", "No recycle bin by default.", "medium"),
        q("cf-linux-files-q4", "touch file typically:",
          ["Always deletes file", "Creates file if missing and updates timestamps", "Reboots", "Pushes to GitHub"],
          "Creates file if missing and updates timestamps", "Common idiom.", "easy"),
    ],
    exercises=[
        ex("cf-linux-files-ex1", "Create copy move delete",
           f"{WSL} In a throwaway directory: create notes.txt, copy to notes.bak, rename to notes.old, delete notes.old. "
           "Record the exact commands. Never run rm -rf /."),
    ],
)

_add(
    "cf-pipes",
    hours=0.75,
    objective="Connect command output to another command with pipes.",
    explanation="A pipe connects stdout of one process to stdin of the next. MIT lecture introduces pipes; official exercises include pipelines.",
    mastery=["Write a two-command pipeline.", "Score >= 80%."],
    resources=[
        r("cf-pipes-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Pipes section and the official pipeline exercises (most common extensions, xargs, history)."),
        r("cf-pipes-reference", "GNU Bash manual — Pipelines", "https://www.gnu.org/software/bash/manual/html_node/Pipelines.html", "GNU Bash", "REFERENCE", "documentation", 1,
          "Canonical pipeline semantics."),
    ],
    questions=[
        q("cf-pipes-q1", "cmd1 | cmd2 means:",
          ["Run cmd2 first", "stdout of cmd1 becomes stdin of cmd2", "Merge two Git branches", "Format both as hex"],
          "stdout of cmd1 becomes stdin of cmd2", "Composition.", "easy", True),
        q("cf-pipes-q2", "Why pipes beat temporary files for many tasks:",
          ["They are slower always", "Data can stream between programs without you managing a temp file", "They replace RAM", "They compile C"],
          "Data can stream between programs without you managing a temp file", "Unix philosophy.", "medium", True),
        q("cf-pipes-q3", "xargs is used to:",
          ["Start the kernel", "Turn stdin lines into command arguments", "Color the prompt only", "Create SSDs"],
          "Turn stdin lines into command arguments", "MIT xargs exercise.", "medium"),
        q("cf-pipes-q4", "If cmd1 fails in a pipe, by default bash may still:",
          ["Always abort the script without pipefail", "Report success if cmd2 succeeds, unless pipefail is set", "Reboot", "Delete PATH"],
          "Report success if cmd2 succeeds, unless pipefail is set", "Lecture mentions pipefail.", "hard"),
    ],
    exercises=[
        ex("cf-pipes-ex1", "Official pipeline exercises",
           f"{WSL} Do the MIT exercises: 5 most common extensions in your home directory; find+xargs on .sh files; "
           f"optional SSH-history style pipeline on ~/.bash_history. Source: {MIT_SHELL}"),
    ],
)

_add(
    "cf-redirection",
    hours=0.75,
    objective="Redirect stdin, stdout, and stderr.",
    explanation=">, >>, 2>, < attach files to standard streams. Official MIT exercise: redirect stdout and stderr separately.",
    mastery=["Redirect stdout and stderr in a documented way.", "Score >= 80%."],
    resources=[
        r("cf-redirection-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Official stdin/stdout/stderr exercise."),
        r("cf-redirection-reference", "GNU Bash manual — Redirections", "https://www.gnu.org/software/bash/manual/html_node/Redirections.html", "GNU Bash", "REFERENCE", "documentation", 1,
          "Canonical redirection syntax."),
    ],
    questions=[
        q("cf-redirection-q1", "stdout and stderr are:",
          ["The same stream always", "Two standard streams (1 and 2) so errors can be separated from normal output",
           "Git remotes", "CPU caches"],
          "Two standard streams (1 and 2) so errors can be separated from normal output", "MIT exercise.", "easy", True),
        q("cf-redirection-q2", "ls /nonexistent /tmp >out 2>err :",
          ["Merges both into out", "Puts successful listing in out and the error in err", "Deletes /tmp", "Pushes to GitHub"],
          "Puts successful listing in out and the error in err", "Official exercise shape.", "medium", True),
        q("cf-redirection-q3", ">> vs > :",
          ["Identical", ">> appends; > truncates/overwrites", "> appends only", "Neither writes files"],
          ">> appends; > truncates/overwrites", "Common footgun.", "easy"),
        q("cf-redirection-q4", "2>&1 means:",
          ["Ignore errors", "Send stderr to the same place as stdout", "Start two shells", "chmod +x"],
          "Send stderr to the same place as stdout", "MIT 'both to the same file' question.", "medium"),
    ],
    exercises=[
        ex("cf-redirection-ex1", "Split streams",
           f"{WSL} Run `ls /nonexistent /tmp`, redirect stdout to one file and stderr to another, then both to the same file. "
           f"Source: {MIT_SHELL} and the Bash redirections page."),
    ],
)

_add(
    "cf-grep",
    hours=0.75,
    objective="Search file contents with grep.",
    explanation="grep finds lines matching a pattern. MIT lecture uses grep in pipelines (curl | grep). man grep is the reference.",
    mastery=["Find matching lines in files or pipelines.", "Score >= 80%."],
    resources=[
        r("cf-grep-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Official curl|grep exercise counting lectures."),
        r("cf-grep-reference", "grep(1) Linux man page", "https://man7.org/linux/man-pages/man1/grep.1.html", "man7.org", "REFERENCE", "documentation", 1,
          "Canonical grep documentation. Learn a few options (i, n, r) by need, not trivia."),
    ],
    questions=[
        q("cf-grep-q1", "grep pattern file prints:",
          ["The kernel log always", "Lines in file that match pattern", "Git blame", "Hex dumps of RAM"],
          "Lines in file that match pattern", "Search.", "easy", True),
        q("cf-grep-q2", "grep in a pipeline typically reads:",
          ["Only Git objects", "stdin from the previous command", "The ALU", "DNS"],
          "stdin from the previous command", "curl | grep.", "easy", True),
        q("cf-grep-q3", "A reason not to memorize every grep flag:",
          ["grep is illegal", "A few flags plus man grep beat trivia; matching well matters more", "man pages are unofficial", "grep cannot read files"],
          "A few flags plus man grep beat trivia; matching well matters more", "Curriculum policy.", "easy"),
        q("cf-grep-q4", "Case-insensitive search is commonly:",
          ["grep -i", "grep --kernel", "chmod +x", "git merge"],
          "grep -i", "Operationally useful flag.", "easy"),
    ],
    exercises=[
        ex("cf-grep-ex1", "curl and grep",
           f"{WSL} Official MIT exercise: `curl -s https://missing.csail.mit.edu/` piped to grep to count listed lectures. "
           f"Then grep a local file you created for a word you chose. Source: {MIT_SHELL}"),
    ],
)

_add(
    "cf-find",
    hours=0.75,
    objective="Locate files by name or type.",
    explanation="find walks a tree. Official MIT exercises combine find with globs, xargs, and -mtime.",
    mastery=["Find files under a directory by name.", "Score >= 80%."],
    resources=[
        r("cf-find-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Official find example and find|xargs exercises."),
        r("cf-find-reference", "find(1) Linux man page", "https://man7.org/linux/man-pages/man1/find.1.html", "man7.org", "REFERENCE", "documentation", 1,
          "Canonical find(1)."),
    ],
    questions=[
        q("cf-find-q1", "find ~/Downloads -name '*.zip' looks for:",
          ["Git branches named zip", "Files under Downloads whose names match the pattern", "CPU caches", "Only empty dirs"],
          "Files under Downloads whose names match the pattern", "MIT example.", "easy", True),
        q("cf-find-q2", "find vs ls -R for 'all .py files':",
          ["ls -R is always safer for huge trees with filters", "find is built to filter by name/type/time while walking",
           "find cannot look at names", "They are identical to grep"],
          "find is built to filter by name/type/time while walking", "Right tool.", "medium", True),
        q("cf-find-q3", "find -type f means:",
          ["Only directories", "Only regular files", "Only symlinks to RAM", "Only Git objects"],
          "Only regular files", "Type filter.", "easy"),
        q("cf-find-q4", "Pairing find with xargs is useful to:",
          ["Reboot", "Run a command on each found path", "Compile the kernel from hex", "Replace chmod"],
          "Run a command on each found path", "MIT xargs exercise.", "medium"),
    ],
    exercises=[
        ex("cf-find-ex1", "find and xargs",
           f"{WSL} Official MIT: find .sh files and wc -l via xargs (bonus: spaces with -print0/-0). Also try the Downloads zip -mtime example if you have that folder. Source: {MIT_SHELL}"),
    ],
)

_add(
    "cf-linux-permissions",
    hours=0.75,
    objective="Inspect and reason about Unix permission bits.",
    explanation="Apply OS permission concepts at the terminal: ls -l, chmod, executable scripts. Official MIT chmod exercise.",
    mastery=["Interpret ls -l permission columns.", "Make a script executable and run it.", "Score >= 80%."],
    resources=[
        r("cf-linux-permissions-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Official ls -l and chmod +x script exercises."),
        r("cf-linux-permissions-reference", "chmod(1)", "https://man7.org/linux/man-pages/man1/chmod.1.html", "man7.org", "REFERENCE", "documentation", 1,
          "Canonical chmod(1)."),
    ],
    questions=[
        q("cf-linux-permissions-q1", "chmod +x check.sh is needed for ./check.sh because:",
          ["The kernel refuses to execute a file without execute permission", "Git requires it", "Hexadecimal shebangs", "RAM is full"],
          "The kernel refuses to execute a file without execute permission", "MIT exercise.", "easy", True),
        q("cf-linux-permissions-q2", "ls -l first character d means:",
          ["Device RAM", "Directory", "Deleted", "Debian only"],
          "Directory", "File type bit.", "easy"),
        q("cf-linux-permissions-q3", "chmod 755 is:",
          ["rwx for owner, r-x for group and others", "no permissions", "rwxrwxrwx", "always sticky"],
          "rwx for owner, r-x for group and others", "Common mode.", "medium", True),
        q("cf-linux-permissions-q4", "Changing permissions of a file you do not own typically:",
          ["Always works", "Fails unless you are root or the owner", "Reboots WSL", "Pushes Git"],
          "Fails unless you are root or the owner", "Enforcement.", "easy"),
    ],
    exercises=[
        ex("cf-linux-permissions-ex1", "Script execute bit",
           f"{WSL} Official MIT: write check.sh taking $1, test -f, different messages; run ./check.sh before and after chmod +x; explain. Source: {MIT_SHELL}"),
    ],
)

_add(
    "cf-linux-processes",
    hours=0.6,
    objective="List and interpret running processes.",
    explanation="ps lists processes. You already used it conceptually; now do it as a skill. man ps is the reference.",
    mastery=["Identify a process and its PID.", "Score >= 80%."],
    resources=[
        r("cf-linux-processes-primary", "MIT Missing Semester 2026 — Introduction to the Shell", MIT_SHELL, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Programs you launch are processes; inspect them with ps."),
        r("cf-linux-processes-reference", "ps(1) Linux man page", "https://man7.org/linux/man-pages/man1/ps.1.html", "man7.org", "REFERENCE", "documentation", 1,
          "Canonical ps(1). Skim; do not memorize every option."),
    ],
    questions=[
        q("cf-linux-processes-q1", "ps is for:",
          ["Packaging Python wheels", "Listing processes", "Formatting code", "Merging Git"],
          "Listing processes", "Inspection.", "easy", True),
        q("cf-linux-processes-q2", "PPID is typically:",
          ["Python PID", "Parent process ID", "Package ID", "Page privilege ID"],
          "Parent process ID", "Process tree.", "easy", True),
        q("cf-linux-processes-q3", "A long-running sleep you started should:",
          ["Have no PID", "Show up in ps until it exits", "Become the kernel", "Wipe PATH"],
          "Show up in ps until it exits", "Observable instance.", "easy"),
        q("cf-linux-processes-q4", "This module does not require you to:",
          ["Read a PID", "Become a professional sysadmin or tune CFS", "Know program vs process", "Use WSL on Windows"],
          "Become a professional sysadmin or tune CFS", "Scope.", "easy"),
    ],
    exercises=[
        ex("cf-linux-processes-ex1", "ps lab",
           f"{WSL} Start `sleep 60 &`, run `ps -o pid,ppid,stat,cmd`, find sleep, then `kill` it. Record PIDs. Do not kill system processes you do not recognize."),
    ],
)

_add(
    "cf-package-management",
    hours=0.6,
    objective="Explain why package managers exist.",
    explanation="OS package managers install/update software with dependency tracking. MIT command-line lecture names apt/brew; shipping lecture goes deeper on language packaging.",
    mastery=["Describe install vs compile-from-source at a high level.", "Score >= 80%."],
    resources=[
        r("cf-package-management-primary", "MIT Missing Semester 2026 — Command-line Environment", MIT_CLI, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Package managers section (apt/brew/etc.). Distro commands depend on your WSL distribution."),
        r("cf-package-management-reference", "MIT Missing Semester 2026 — Packaging and Shipping Code", MIT_SHIP, "MIT Missing Semester 2026", "REFERENCE", "article", 1,
          "Source vs artifacts; deeper packaging. OS packages vs language packages."),
    ],
    questions=[
        q("cf-package-management-q1", "A package manager exists to:",
          ["Replace the kernel with CSS", "Install, upgrade, and track software and its dependencies", "Draw sprites", "Compile only hex"],
          "Install, upgrade, and track software and its dependencies", "Why not random .tar dumps.", "easy", True),
        q("cf-package-management-q2", "apt vs compiling from source:",
          ["apt is always slower", "apt installs a distro-built artifact; source build compiles on your machine",
           "They are identical", "apt only works in PowerShell"],
          "apt installs a distro-built artifact; source build compiles on your machine", "High level.", "medium", True),
        q("cf-package-management-q3", "You should not blindly copy install commands from random blogs because:",
          ["Blogs cannot use HTTPS", "Wrong distro, outdated packages, or untrusted scripts can break the system",
           "apt forbids updates", "WSL cannot run Unix"],
          "Wrong distro, outdated packages, or untrusted scripts can break the system", "Operational caution.", "easy"),
        q("cf-package-management-q4", "Language package managers (pip/npm/Maven) differ from apt mainly by:",
          ["Managing language libraries vs OS-level packages", "Using no dependencies", "Replacing Git", "Being unofficial always"],
          "Managing language libraries vs OS-level packages", "Next module expands this.", "medium"),
    ],
    exercises=[
        ex("cf-package-management-ex1", "Identify your manager",
           f"{WSL} Run `cat /etc/os-release` and identify the package manager (apt, dnf, ...). "
           "`apt search curl` or equivalent; do not mass-upgrade the system in this exercise. Note the command you would use to install curl if missing."),
    ],
)

_add(
    "cf-linux-environment-variables",
    hours=0.6,
    objective="Read and set environment variables in the shell.",
    explanation="export, printenv, PATH. Builds on OS environment variables with hands-on shell skill. MIT CLI lecture covers customization.",
    mastery=["Print PATH and explain one entry.", "Set a variable and see it in a child process.", "Score >= 80%."],
    resources=[
        r("cf-linux-environment-variables-primary", "MIT Missing Semester 2026 — Command-line Environment", MIT_CLI, "MIT Missing Semester 2026", "PRIMARY", "article", 0,
          "Environment, aliases, and dotfiles."),
        r("cf-linux-environment-variables-reference", "environ(7)", "https://man7.org/linux/man-pages/man7/environ.7.html", "man7.org", "REFERENCE", "documentation", 1,
          "Canonical environment list."),
    ],
    questions=[
        q("cf-linux-environment-variables-q1", "printenv PATH vs echo $PATH:",
          ["They cannot both show PATH", "Both can show PATH; printenv dumps the environment", "Only PowerShell has PATH", "PATH is not an environment variable"],
          "Both can show PATH; printenv dumps the environment", "Inspection.", "easy", True),
        q("cf-linux-environment-variables-q2", "VAR=1 ./prog vs export VAR=1 then ./prog:",
          ["Identical always to unexported VAR in the same shell later",
           "The first sets VAR only for that command; export persists in the shell for later children",
           "Neither passes VAR", "Both reboot"],
          "The first sets VAR only for that command; export persists in the shell for later children", "Scope.", "medium", True),
        q("cf-linux-environment-variables-q3", "Putting secrets in exported variables in a shared screenshot is risky because:",
          ["Hex fails", "Child processes and logs may leak them", "Kernels forbid PATH", "Git cannot exist"],
          "Child processes and logs may leak them", "Hygiene.", "easy"),
        q("cf-linux-environment-variables-q4", "Dotfiles like ~/.bashrc are used to:",
          ["Replace the SSD", "Set up your environment whenever the shell starts", "Compile the kernel", "Host GitHub"],
          "Set up your environment whenever the shell starts", "MIT dotfiles.", "easy"),
    ],
    exercises=[
        ex("cf-linux-environment-variables-ex1", "Export and child",
           f"{WSL} `export D0_LAB=1` then `bash -c 'echo $D0_LAB'`. Then start a new login shell and see if it persists without a dotfile. Write what you observed."),
    ],
)
