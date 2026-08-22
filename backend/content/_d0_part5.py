"""Git topics."""

from __future__ import annotations

from _d0_helpers import MIT_GIT, WSL, ex, q, r
from _d0_part4 import CONTENT, _add

GIT_REPO = "https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository"
GIT_RECORD = "https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository"
GIT_LOG = "https://git-scm.com/book/en/v2/Git-Basics-Viewing-the-Commit-History"
GIT_UNDO = "https://git-scm.com/book/en/v2/Git-Basics-Undoing-Things"
GIT_REMOTE = "https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes"
GIT_BRANCH = "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell"
GIT_MERGE = "https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging"
GIT_BRMAN = "https://git-scm.com/book/en/v2/Git-Branching-Branch-Management"
GIT_REBASE = "https://git-scm.com/book/en/v2/Git-Branching-Rebasing"
GIT_STASH_BOOK = "https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning"
GH_HELLO = "https://docs.github.com/en/get-started/using-github/hello-world"
GH_PR = "https://docs.github.com/en/pull-requests/get-started/pull-request-quickstart"
GH_FLOW = "https://docs.github.com/en/get-started/using-github/github-flow"
GH_LEARN = "https://docs.github.com/en/get-started/start-your-journey/git-and-github-learning-resources"

_add(
    "cf-repository",
    hours=0.75,
    objective="Explain a Git repository as a project history.",
    explanation="A Git repository stores snapshots of a project in .git. git init or git clone. Pro Git 2.1 is canonical.",
    mastery=["Initialize or clone a repo and explain .git at a high level.", "Score >= 80%."],
    resources=[
        r("cf-repository-primary", "Pro Git — Getting a Git Repository", GIT_REPO, "Git", "PRIMARY", "book", 0,
          "git init vs git clone. Canonical book chapter."),
        r("cf-repository-reference", "MIT Missing Semester 2026 — Version Control and Git", MIT_GIT, "MIT Missing Semester 2026", "REFERENCE", "article", 1,
          "Git data model: snapshots and .git. Complements the book."),
    ],
    questions=[
        q("cf-repository-q1", "git init in a folder:",
          ["Uploads the folder to GitHub immediately", "Creates a .git directory so Git can track history",
           "Formats the disk", "Compiles C"],
          "Creates a .git directory so Git can track history", "Pro Git 2.1.", "easy", True),
        q("cf-repository-q2", "Why clone vs copy files with USB:",
          ["USB is illegal", "Clone gets history and a linked remote; a file copy may not", "Clone deletes .git", "Clone only works offline forever"],
          "Clone gets history and a linked remote; a file copy may not", "Full history.", "medium", True),
        q("cf-repository-q3", "The working tree is:",
          ["Only GitHub Issues", "The checked-out files you edit", "The ALU", "PATH"],
          "The checked-out files you edit", "Working tree vs .git.", "easy"),
        q("cf-repository-q4", "Deleting .git (not recommended) would:",
          ["Keep full history in RAM forever", "Remove Git history from that copy of the project", "Uninstall Linux", "Create a PR"],
          "Remove Git history from that copy of the project", "History lives in .git.", "medium"),
    ],
    exercises=[
        ex("cf-repository-ex1", "Initialize a repository",
           f"{WSL} Create ~/d0-git-lab, git init, create hello.txt, git status. Confirm .git exists. Do not use a work repo you care about. "
           "This is Exercise 1 start (stage/commit in the next topic)."),
    ],
)

_add(
    "cf-commits",
    hours=1.0,
    objective="Create commits with a clear message.",
    explanation="Staging selects what goes into the next snapshot. Commits record it. Why staging exists: craft the snapshot.",
    mastery=["Make a commit independently.", "Explain snapshot vs working tree.", "Inspect diff and log.", "Score >= 80%."],
    resources=[
        r("cf-commits-primary", "Pro Git — Recording Changes to the Repository", GIT_RECORD, "Git", "PRIMARY", "book", 0,
          "status, add, commit, diff. Canonical."),
        r("cf-commits-reference", "Pro Git — Viewing the Commit History", GIT_LOG, "Git", "REFERENCE", "book", 1,
          "git log."),
        r("cf-commits-practice", "MIT Missing Semester 2026 — Git CLI", MIT_GIT, "MIT Missing Semester 2026", "PRACTICE", "article", 2,
          "Practice add/commit/log/diff from the lecture's command list."),
    ],
    questions=[
        q("cf-commits-q1", "Why does staging exist between edit and commit?",
          ["Git cannot read files", "You choose which changes belong in the next snapshot", "Staging compiles C", "GitHub requires hex"],
          "You choose which changes belong in the next snapshot", "Not trivia: this is the point of the index.", "medium", True),
        q("cf-commits-q2", "git add file then git commit:",
          ["Only saves RAM", "Records a snapshot of the staged content with a message", "Pushes automatically always", "Creates a GitHub account"],
          "Records a snapshot of the staged content with a message", "Commit object.", "easy", True),
        q("cf-commits-q3", "git diff with no args typically shows:",
          ["Unstaged changes in the working tree vs index", "Only GitHub PRs", "CPU registers", "apt packages"],
          "Unstaged changes in the working tree vs index", "Pro Git diff.", "medium"),
        q("cf-commits-q4", "A good commit message should:",
          ["Be empty", "Describe why/what changed so future you can understand the history", "List every keystroke", "Be a hex dump"],
          "Describe why/what changed so future you can understand the history", "MIT lecture emphasizes messages.", "easy"),
    ],
    exercises=[
        ex("cf-commits-ex1", "Stage, commit, diff, log",
           f"{WSL} In d0-git-lab: stage hello.txt, commit. Modify it, git diff, stage, commit again, git log. "
           "Exercise 1 complete + Exercise 2 (modify, diff, commit)."),
    ],
)

_add(
    "cf-branches",
    hours=0.75,
    objective="Create and switch branches.",
    explanation="A branch is a movable pointer to a commit. Parallel lines of work.",
    mastery=["Create and switch branches.", "Explain a branch as a pointer to a commit.", "Score >= 80%."],
    resources=[
        r("cf-branches-primary", "Pro Git — Branches in a Nutshell", GIT_BRANCH, "Git", "PRIMARY", "book", 0,
          "What a branch is."),
        r("cf-branches-reference", "Pro Git — Branch Management", GIT_BRMAN, "Git", "REFERENCE", "book", 1,
          "Listing and deleting branches."),
    ],
    questions=[
        q("cf-branches-q1", "A Git branch is best described as:",
          ["A copy of the entire SSD", "A movable pointer to a commit", "A GitHub-only feature with no local meaning", "A compiler flag"],
          "A movable pointer to a commit", "Pro Git nutshell.", "easy", True),
        q("cf-branches-q2", "git switch -c feature:",
          ["Deletes main", "Creates feature and checks it out", "Pushes to origin always", "Rebases origin"],
          "Creates feature and checks it out", "Modern switch -c.", "easy", True),
        q("cf-branches-q3", "Why branch instead of copying the folder?",
          ["Folders cannot hold files", "Git can share history and merge; folder copies duplicate and diverge painfully",
           "Git forbids folders", "WSL cannot copy"],
          "Git can share history and merge; folder copies duplicate and diverge painfully", "Why VCS.", "medium"),
        q("cf-branches-q4", "HEAD typically points at:",
          ["apt", "The current branch (or detached commit)", "The kernel", "CSS"],
          "The current branch (or detached commit)", "Where you are.", "medium"),
    ],
    exercises=[
        ex("cf-branches-ex1", "Create a feature branch",
           f"{WSL} From main/master in d0-git-lab: git switch -c feature-note, make a change, commit. git log --oneline --graph --all. Exercise 3 starts here."),
    ],
)

_add(
    "cf-merge",
    hours=1.0,
    objective="Combine branches with merge.",
    explanation="Merge joins histories. Fast-forward vs merge commit. Canonical: Basic Branching and Merging.",
    mastery=["Merge a feature branch and explain the result.", "Score >= 80%."],
    resources=[
        r("cf-merge-primary", "Pro Git — Basic Branching and Merging", GIT_MERGE, "Git", "PRIMARY", "book", 0,
          "Fast-forward vs three-way merge. Conflict section is the next topic."),
    ],
    questions=[
        q("cf-merge-q1", "A fast-forward merge happens when:",
          ["Histories have diverged with unique commits on both sides", "The branch being merged is a straight descendant of current HEAD",
           "GitHub is down", "You use PowerShell"],
          "The branch being merged is a straight descendant of current HEAD", "Pro Git hotfix example.", "medium", True),
        q("cf-merge-q2", "A merge commit is created when:",
          ["Git always fast-forwards", "Two lines of development must be joined and a new commit with two parents is needed",
           "You run ls", "You chmod +x"],
          "Two lines of development must be joined and a new commit with two parents is needed", "Diverged histories.", "medium", True),
        q("cf-merge-q3", "After merging feature into main, deleting feature:",
          ["Deletes the commits' content from the repo if they were merged", "Is often safe because main now contains the work",
           "Uninstalls Git", "Wipes origin"],
          "Is often safe because main now contains the work", "Pro Git deletes iss53.", "easy"),
        q("cf-merge-q4", "git merge feature while on main:",
          ["Checks out feature and deletes main", "Brings feature's changes into main", "Pushes automatically", "Creates GitHub Issues"],
          "Brings feature's changes into main", "Direction matters.", "easy"),
    ],
    exercises=[
        ex("cf-merge-ex1", "Merge the feature branch",
           f"{WSL} switch to main, git merge feature-note, inspect log --graph. Exercise 3 complete."),
    ],
)

_add(
    "cf-rebase",
    hours=0.75,
    objective="Explain rebase vs merge conceptually.",
    explanation="Rebase replays commits on a new base. Do not rebase shared published branches. Practice only locally in V1.",
    mastery=["State when rebase is used and its risk on shared branches.", "Score >= 80%."],
    resources=[
        r("cf-rebase-primary", "Pro Git — Rebasing", GIT_REBASE, "Git", "PRIMARY", "book", 0,
          "Canonical rebase vs merge. Read the warning about public history."),
        r("cf-rebase-reference", "MIT Missing Semester 2026 — Git", MIT_GIT, "MIT Missing Semester 2026", "REFERENCE", "article", 1,
          "Mentions git rebase; book is authoritative for the warning."),
    ],
    questions=[
        q("cf-rebase-q1", "Rebase vs merge: rebase typically:",
          ["Creates a merge commit with two parents always", "Replays commits as new commits on another base, rewriting history",
           "Deletes .git", "Formats the disk"],
          "Replays commits as new commits on another base, rewriting history", "New hashes.", "medium", True),
        q("cf-rebase-q2", "Why not rebase commits already pushed to a shared branch?",
          ["GitHub forbids HTTPS", "Others may have based work on the old hashes; rewriting causes chaos",
           "Rebase cannot run on Linux", "It uninstalls WSL"],
          "Others may have based work on the old hashes; rewriting causes chaos", "Pro Git golden rule.", "medium", True),
        q("cf-rebase-q3", "A safe first rebase practice in this curriculum:",
          ["rebase origin/main on a local-only branch", "force-push main at work", "rebase the kernel", "rebase PATH"],
          "rebase origin/main on a local-only branch", "Local only.", "easy"),
        q("cf-rebase-q4", "After rebase, commit hashes of replayed commits typically:",
          ["Stay identical always", "Change", "Become PIDs", "Become RGB"],
          "Change", "New commit objects.", "easy"),
    ],
    exercises=[
        ex("cf-rebase-ex1", "Local rebase only",
           f"{WSL} Create branch tmp-rebase from main, add a commit, switch to main and add a different commit, switch back, "
           "git rebase main. If it is messy, abort with git rebase --abort. Do not force-push anywhere."),
    ],
)

_add(
    "cf-remote",
    hours=0.6,
    objective="Explain remotes as named copies of a repository.",
    explanation="origin is a conventional remote name. git remote -v lists URLs.",
    mastery=["List remotes and explain origin.", "Score >= 80%."],
    resources=[
        r("cf-remote-primary", "Pro Git — Working with Remotes", GIT_REMOTE, "Git", "PRIMARY", "book", 0,
          "Adding remotes, fetch vs the next topic's pull/push."),
    ],
    questions=[
        q("cf-remote-q1", "A remote is:",
          ["A CPU core", "A named URL Git uses to talk to another repository", "A chmod mode", "An apt package"],
          "A named URL Git uses to talk to another repository", "Pro Git remotes.", "easy", True),
        q("cf-remote-q2", "origin usually means:",
          ["The kernel", "The default remote you cloned from or first added", "A hex color", "WSL only"],
          "The default remote you cloned from or first added", "Convention.", "easy", True),
        q("cf-remote-q3", "git remote -v shows:",
          ["PIDs", "Remote names and URLs", "ALU status", "CSS"],
          "Remote names and URLs", "Inspection.", "easy"),
        q("cf-remote-q4", "You can have multiple remotes:",
          ["Never", "Yes; each has a name", "Only if you delete .git", "Only on macOS"],
          "Yes; each has a name", "upstream vs origin later.", "medium"),
    ],
    exercises=[
        ex("cf-remote-ex1", "Name origin",
           "If you already have any clone: git remote -v and write what origin points at. "
           "Otherwise skip until GitHub workflow; then record origin after you add the GitHub remote."),
    ],
)

_add(
    "cf-pull-push",
    hours=1.0,
    objective="Send and receive commits.",
    explanation="fetch downloads; merge/rebase integrates; pull is fetch+integrate. push sends. Use official docs, not blog search pages.",
    mastery=["Push and pull a branch independently.", "Explain fetch vs pull.", "Score >= 80%."],
    resources=[
        r("cf-pull-push-primary", "Pro Git — Working with Remotes", GIT_REMOTE, "Git", "PRIMARY", "book", 0,
          "fetch, pull, push in the remotes chapter."),
        r("cf-pull-push-reference", "git-fetch / git-pull / git-push documentation", "https://git-scm.com/docs/git-fetch", "Git", "REFERENCE", "documentation", 1,
          "Canonical git-fetch page; also read https://git-scm.com/docs/git-pull and https://git-scm.com/docs/git-push."),
    ],
    questions=[
        q("cf-pull-push-q1", "git fetch vs git pull:",
          ["They are identical", "fetch updates remote-tracking branches; pull also integrates into your current branch",
           "pull never uses the network", "fetch pushes"],
          "fetch updates remote-tracking branches; pull also integrates into your current branch", "Exercise 9.", "medium", True),
        q("cf-pull-push-q2", "git push origin main:",
          ["Deletes origin", "Sends your local main commits to origin's main (permissions allowing)", "Only runs ls", "Formats the SSD"],
          "Sends your local main commits to origin's main (permissions allowing)", "Publish.", "easy", True),
        q("cf-pull-push-q3", "A reason to fetch before merging:",
          ["To avoid seeing others' work", "To update your view of origin without mixing it into your files yet",
           "To compile C", "To chmod the kernel"],
          "To update your view of origin without mixing it into your files yet", "Inspect then integrate.", "medium"),
        q("cf-pull-push-q4", "If push is rejected because of new remote commits:",
          ["Delete .git", "Integrate remote work (pull/rebase) then push again", "Always --force on main", "Reinstall WSL"],
          "Integrate remote work (pull/rebase) then push again", "Do not force main.", "medium"),
    ],
    exercises=[
        ex("cf-pull-push-ex1", "Fetch vs pull",
           f"{WSL} After the GitHub repo exists: git fetch, git status, then git pull. Write three sentences on the difference. Exercise 9. "
           "Use a private repo you own."),
    ],
)

_add(
    "cf-conflicts",
    hours=1.25,
    objective="Recognize and resolve a simple merge conflict.",
    explanation="Conflicts happen when both sides edit the same lines. Markers <<<<<< ====== >>>>>>. Pro Git merge conflict section.",
    mastery=["Resolve a two-hunk conflict in a text file.", "Score >= 80%."],
    resources=[
        r("cf-conflicts-primary", "Pro Git — Basic Branching and Merging (conflicts)", GIT_MERGE, "Git", "PRIMARY", "book", 0,
          "The Basic Merge Conflicts section on this page."),
    ],
    questions=[
        q("cf-conflicts-q1", "A merge conflict means:",
          ["Git deleted Linux", "Git could not automatically combine overlapping edits", "The CPU overheated", "PATH is empty"],
          "Git could not automatically combine overlapping edits", "Same lines.", "easy", True),
        q("cf-conflicts-q2", "Conflict markers should:",
          ["Stay in the file forever", "Be removed after you choose/combine the final text", "Be committed as-is always", "Be emailed to apt"],
          "Be removed after you choose/combine the final text", "Then git add and commit.", "easy", True),
        q("cf-conflicts-q3", "git add after editing a conflicted file:",
          ["Marks the conflict resolved", "Pushes to GitHub", "Reboots", "Creates a remote"],
          "Marks the conflict resolved", "Pro Git.", "medium"),
        q("cf-conflicts-q4", "Deliberately causing a conflict is useful to:",
          ["Corrupt .git for fun", "Practice the resolution workflow in a throwaway repo", "Break WSL", "Uninstall Git"],
          "Practice the resolution workflow in a throwaway repo", "Exercise 5.", "easy"),
    ],
    exercises=[
        ex("cf-conflicts-ex1", "Deliberate merge conflict",
           f"{WSL} Exercise 5: two branches edit the same line of the same file differently, merge, resolve markers, commit. Throwaway repo only."),
    ],
)

_add(
    "cf-reset-revert",
    hours=1.0,
    objective="Contrast reset, revert, and restore.",
    explanation="reset moves a branch pointer; revert adds a new undoing commit (safe for published history); restore adjusts files. Canonical pages.",
    mastery=["Choose revert for published history in a simple scenario.", "Demonstrate reset vs revert vs restore.", "Score >= 80%."],
    resources=[
        r("cf-reset-revert-primary", "Pro Git — Undoing Things", GIT_UNDO, "Git", "PRIMARY", "book", 0,
          "reset, checkout/restore, amend. Pair with git-revert(1)."),
        r("cf-reset-revert-reference", "git-reset / git-revert / git-restore", "https://git-scm.com/docs/git-reset", "Git", "REFERENCE", "documentation", 1,
          "Also https://git-scm.com/docs/git-revert and https://git-scm.com/docs/git-restore."),
    ],
    questions=[
        q("cf-reset-revert-q1", "git revert on a published commit:",
          ["Deletes the commit from everyone's laptop magically", "Creates a new commit that undoes the change, preserving history",
           "Formats origin", "chmod -R /"],
          "Creates a new commit that undoes the change, preserving history", "Safe public undo.", "medium", True),
        q("cf-reset-revert-q2", "git reset --hard on a local unpushed commit:",
          ["Is always safe on origin/main", "Moves the branch and can discard commits you have not shared",
           "Only edits README on GitHub", "Installs apt"],
          "Moves the branch and can discard commits you have not shared", "Dangerous if shared.", "medium", True),
        q("cf-reset-revert-q3", "git restore file typically:",
          ["Creates a branch", "Discards or restores working-tree content from the index or a commit", "Pushes", "Merges remotes"],
          "Discards or restores working-tree content from the index or a commit", "File-level.", "medium"),
        q("cf-reset-revert-q4", "Exercise 6 asks you to demonstrate:",
          ["Only npm", "The difference between reset, revert, and restore", "Only Docker", "Only CSS"],
          "The difference between reset, revert, and restore", "Required lab.", "easy"),
    ],
    exercises=[
        ex("cf-reset-revert-ex1", "reset vs revert vs restore",
           f"{WSL} Exercise 6 in a throwaway repo: (1) restore a modified unstaged file, (2) reset a local unpushed commit with --hard after copying the hash, "
           "(3) revert a commit instead of resetting when you pretend it was published. Write a 6-line cheat sheet."),
    ],
)

_add(
    "cf-cherry-pick",
    hours=0.6,
    objective="Apply one commit onto another branch.",
    explanation="Cherry-pick copies a commit. Official git-cherry-pick(1).",
    mastery=["Explain cherry-pick vs merge.", "Apply one commit onto another branch.", "Score >= 80%."],
    resources=[
        r("cf-cherry-pick-primary", "git-cherry-pick documentation", "https://git-scm.com/docs/git-cherry-pick", "Git", "PRIMARY", "documentation", 0,
          "Canonical command page."),
        r("cf-cherry-pick-reference", "MIT Missing Semester 2026 — Git", MIT_GIT, "MIT Missing Semester 2026", "REFERENCE", "article", 1,
          "Lists cherry-pick among advanced commands; docs are the how-to."),
    ],
    questions=[
        q("cf-cherry-pick-q1", "Cherry-pick vs merge:",
          ["Cherry-pick applies a chosen commit; merge brings a whole branch history", "They are identical", "Cherry-pick deletes remotes", "Merge only works offline"],
          "Cherry-pick applies a chosen commit; merge brings a whole branch history", "Scope of history.", "medium", True),
        q("cf-cherry-pick-q2", "Cherry-pick creates:",
          ["No new object", "A new commit with a new hash (usually) applying the same patch", "A GitHub Issue", "A kernel module"],
          "A new commit with a new hash (usually) applying the same patch", "Copy of change.", "easy", True),
        q("cf-cherry-pick-q3", "A good use:",
          ["Rewrite all of origin/main daily", "Bring one bugfix commit onto a release branch", "Replace PATH", "Format /"],
          "Bring one bugfix commit onto a release branch", "Classic use.", "easy"),
        q("cf-cherry-pick-q4", "If cherry-pick conflicts:",
          ["Git always force-pushes", "You resolve like a merge, then continue", "WSL uninstalls", "The ALU stops"],
          "You resolve like a merge, then continue", "Same markers.", "medium"),
    ],
    exercises=[
        ex("cf-cherry-pick-ex1", "Move one commit",
           f"{WSL} Exercise 8: two branches; commit on A; cherry-pick that hash onto B; show log on both."),
    ],
)

_add(
    "cf-stash",
    hours=0.6,
    objective="Temporarily shelf uncommitted work.",
    explanation="stash saves dirty work and restores a clean tree. Book + git-stash(1).",
    mastery=["Stash, switch branch, and restore.", "Score >= 80%."],
    resources=[
        r("cf-stash-primary", "Pro Git — Stashing and Cleaning", GIT_STASH_BOOK, "Git", "PRIMARY", "book", 0,
          "Canonical stash workflow."),
        r("cf-stash-reference", "git-stash documentation", "https://git-scm.com/docs/git-stash", "Git", "REFERENCE", "documentation", 1,
          "Command reference."),
    ],
    questions=[
        q("cf-stash-q1", "git stash is for:",
          ["Publishing to GitHub Pages", "Saving uncommitted work to get a clean working tree", "Compiling C", "chmod recursive /"],
          "Saving uncommitted work to get a clean working tree", "WIP shelf.", "easy", True),
        q("cf-stash-q2", "stash pop vs apply:",
          ["pop applies and drops the stash entry if successful; apply keeps it", "They both delete .git", "pop pushes remotes", "apply formats disks"],
          "pop applies and drops the stash entry if successful; apply keeps it", "git-stash(1).", "medium", True),
        q("cf-stash-q3", "Stash is not a backup of published history because:",
          ["It is local and easy to drop", "It is replicated to all remotes always", "GitHub stores all stashes", "It replaces commits on origin"],
          "It is local and easy to drop", "Don't stash instead of committing important work.", "medium"),
        q("cf-stash-q4", "A typical stash workflow:",
          ["stash, switch branch, work, switch back, stash pop", "stash instead of ever committing", "stash the kernel", "stash PATH"],
          "stash, switch branch, work, switch back, stash pop", "Exercise 7.", "easy"),
    ],
    exercises=[
        ex("cf-stash-ex1", "Stash and recover",
           f"{WSL} Exercise 7: dirty a file, stash, switch branch, switch back, stash pop, confirm the edit returned."),
    ],
)

_add(
    "cf-github-workflow",
    hours=1.5,
    objective="Use clone, branch, pull request conceptually.",
    explanation="GitHub Hello World: repository → branch → commit → pull request → merge. Use a private repo you own.",
    mastery=["Describe a PR-based workflow without notes.", "Complete Hello World on your own private repository.", "Score >= 80%."],
    resources=[
        r("cf-github-workflow-primary", "GitHub Docs — Hello World", GH_HELLO, "GitHub", "PRIMARY", "documentation", 0,
          "Official hands-on: repo, branch, commit, PR, merge."),
        r("cf-github-workflow-reference", "GitHub Docs — Pull request quickstart", GH_PR, "GitHub", "REFERENCE", "documentation", 1,
          "PR flow."),
        r("cf-github-workflow-practice", "GitHub Docs — GitHub flow", GH_FLOW, "GitHub", "PRACTICE", "documentation", 2,
          "Named workflow. Also https://docs.github.com/en/get-started/start-your-journey/git-and-github-learning-resources"),
    ],
    questions=[
        q("cf-github-workflow-q1", "Hello World on GitHub teaches this order:",
          ["merge → repo → branch", "repository → branch → commit → pull request → merge", "rebase → format disk → PR", "apt → chmod → PR"],
          "repository → branch → commit → pull request → merge", "Official tutorial.", "easy", True),
        q("cf-github-workflow-q2", "A pull request is:",
          ["A CPU interrupt", "A proposal to merge one branch into another with discussion", "A kernel panic", "An apt mirror"],
          "A proposal to merge one branch into another with discussion", "Collaboration.", "easy", True),
        q("cf-github-workflow-q3", "You should practice on:",
          ["Someone else's production repo without permission", "A private repository you own", "The Linux kernel by force-push", "Random forks you do not understand"],
          "A private repository you own", "Curriculum rule.", "easy", True),
        q("cf-github-workflow-q4", "Review before merge exists to:",
          ["Slow you for no reason always", "Catch mistakes and share context before changing the default branch", "Replace Git", "Disable HTTPS"],
          "Catch mistakes and share context before changing the default branch", "Even solo, PRs record intent.", "medium"),
        q("cf-github-workflow-q5", "Git vs GitHub:",
          ["Identical products", "Git is the VCS; GitHub is a hosting/collaboration service", "GitHub replaces git commit", "Git is only a website"],
          "Git is the VCS; GitHub is a hosting/collaboration service", "Don't conflate.", "easy"),
    ],
    exercises=[
        ex("cf-github-workflow-ex1", "Hello World on your private repo",
           f"Exercise 4: Follow {GH_HELLO} on a private repository you own (you may name it d0-hello instead of hello-world). "
           "Complete branch → commit → pull request → merge. Then clone it in WSL, set origin, and push a second small commit from the CLI."),
    ],
)
