# Question brief: Python environment and project tooling (`mod-py-tooling`)

Subject: Python for AI/ML
Topics: 6

For each topic below, write at least 4 self-check questions in
`content/questions/mod-py-tooling.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `pytool-virtual-environments` — Virtual environments

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Create and activate a per-project virtual environment and explain why global installs break projects.
- Context: How to create, activate and install into a per-project virtual environment, and what a venv physically is on disk.
- Resources:
  - **PRIMARY** Python Packaging — Install packages in a virtual environment using pip and venv
    https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
  - **REFERENCE** Python — venv — Creation of virtual environments
    https://docs.python.org/3/library/venv.html
- Currently has **no questions at all**.

## `pytool-uv-projects` — uv projects

- Depth target: STRONG  ·  Track: CORE
- Objective: Run a Python project end to end with uv, letting it manage the virtual environment and the lockfile.
- Context: The uv project workflow from uv init to uv run, and what uv means by project, workspace and environment.
- Resources:
  - **PRIMARY** Astral — Working on projects
    https://docs.astral.sh/uv/guides/projects/
  - **REFERENCE** Astral — Projects
    https://docs.astral.sh/uv/concepts/projects/
- Currently has **no questions at all**.

## `pytool-pyproject-toml` — pyproject.toml

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Read and write a pyproject.toml and know which fields are standard rather than tool-specific.
- Context: Field-by-field walkthrough of the [project] table - name, version, dependencies, optional-dependencies, entry points - plus the PEP that defines it normatively.
- Resources:
  - **PRIMARY** Python Packaging — Writing your pyproject.toml
    https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
  - **REFERENCE** Python — PEP 621 – Storing project metadata in pyproject.toml
    https://peps.python.org/pep-0621/
    exact part: "Specification"
- Currently has **no questions at all**.

## `pytool-dependency-pinning` — Declaring and constraining dependencies

- Depth target: STRONG  ·  Track: CORE
- Objective: Declare dependencies with the narrowest constraint that is still honest, and separate dev from runtime.
- Context: Version specifiers, dependency groups (dev versus runtime), and git, path and editable sources - plus what each specifier operator actually promises.
- Resources:
  - **PRIMARY** Astral — Managing dependencies
    https://docs.astral.sh/uv/concepts/projects/dependencies/
  - **REFERENCE** Python Packaging — Versioning
    https://packaging.python.org/en/latest/discussions/versioning/
- Currently has **no questions at all**.

## `pytool-lockfiles-reproducible` — Lockfiles and reproducible installs

- Depth target: STRONG  ·  Track: CORE
- Objective: Explain what a lockfile guarantees that a declared dependency range does not, and produce one.
- Context: The distinction the whole module exists to teach: a declared dependency range versus a locked resolution, and the requirements.txt path for repos that are not uv projects.
- Resources:
  - **PRIMARY** Astral — Locking and syncing
    https://docs.astral.sh/uv/concepts/projects/sync/
  - **REFERENCE** Astral — Locking environments
    https://docs.astral.sh/uv/pip/compile/
- Currently has **no questions at all**.

## `pytool-python-versions` — Pinning the Python interpreter

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Pin the interpreter version a project runs on, not just the packages it installs.
- Context: Pinning a Python interpreter version per project with .python-version and uv python install - the failure mode that pinning packages alone does not fix.
- Resources:
  - **PRIMARY** Astral — Installing and managing Python
    https://docs.astral.sh/uv/guides/install-python/
- Currently has **no questions at all**.

