# Akshit Engineering OS

Copyright © 2026 **Akshit Jain** ([@akshitjain1](https://github.com/akshitjain1)) · Licensed under the [GNU AGPL-3.0](LICENSE) · First published 22 August 2026

Private, local-first personal learning platform: **Learn → Practice → Build → Test → Revise → Track → Interview**.

Built for exactly one user (Akshit). No multi-user, billing, social, or public features.

## Stack

| Layer    | Technology                                   |
| -------- | -------------------------------------------- |
| Frontend | Next.js 16 (App Router), TypeScript, Tailwind CSS 4 |
| Backend  | Python, FastAPI, SQLAlchemy 2.0              |
| Database | SQLite (dev) — PostgreSQL-compatible schema for later production |

## Structure

```
ai-engine/          Next.js frontend (dashboard + 11 section routes)
backend/            FastAPI app
  app/db/           SQLAlchemy models (single Base, portable types)
  app/main.py       API routes
  seed.py           Demo curriculum + 19 DSA patterns (idempotent)
  tests/            pytest API + model tests
  alembic/          Schema migrations (initial revision included)
docs/architecture.md
```

## Run it

Backend (port 8000):

```
cd backend
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python seed.py
backend\run.bat
```

Or:

```
backend\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend (port 3000):

```
cd ai-engine
npm install
npm run dev
```

Open http://localhost:3000 — root redirects to `/dashboard`.

## Environment

Copy `backend/.env.example` → `backend/.env` if you need a different `DATABASE_URL`.
Relative SQLite paths are resolved against the `backend/` directory, so the process working directory does not matter.

Frontend API URL is `NEXT_PUBLIC_API_URL` (default `http://127.0.0.1:8000`).

## Tests

```
cd backend
venv\Scripts\python -m pytest
```

Frontend verification gate:

```
cd ai-engine
npm run build
```

## Alembic

The app still calls `create_all` on startup for local SQLite convenience.

For a **new** database you can also run:

```
cd backend
venv\Scripts\python -m alembic upgrade head
```

If `dev.db` already exists from an earlier create_all, stamp instead of upgrading (upgrade would try to create tables that already exist):

```
venv\Scripts\python -m alembic stamp head
```

## Curriculum content

Content lives in `backend/content/curriculum/` as YAML/JSON manifests. See [docs/curriculum-manifest.md](docs/curriculum-manifest.md).

```
cd backend
python -m app.content.import_curriculum content/curriculum/demo/rest-apis.yaml
python seed.py   # demo manifest + DSA + user row
python -m app.content.import_curriculum content/curriculum/v1-index.yaml
```

`origin: demo` is the development fixture. Official V1 (Domains 0–2) is structure-only: resource URLs are not mapped yet.

### Keeping the resources honest

The curriculum promises *open exactly this page and study it*, so it is only as
good as its URLs. `audit_resource_links` fetches every one of them and reports
the four ways a mapping goes quietly wrong: the page is gone, it loads as
source text rather than a rendered page, it has moved, or the recorded
publisher is not the host serving it.

```
cd backend
python -m app.content.audit_resource_links      # -> reports/resource_link_audit.{json,md}
python -m app.content.repair_resource_links --dry-run
python -m app.content.repair_resource_links
```

The first live run found 57 links pointing at `raw.githubusercontent.com`,
which a browser renders as unreadable markdown source, concentrated in the AI
modules (29 of 32 deep-learning topics), plus 261 dead rows and 58 whose
recorded publisher was not the host serving the page. **158 rows were repaired**
against replacements that were each fetched and title-checked first. A full
re-audit now reports zero dead links, zero plain-text pages and zero provider
mismatches. See [docs/resource-link-integrity.md](docs/resource-link-integrity.md).

`--record` stamps `last_verified_at` and the observed status, landing URL and
page title onto every row, so the freshness of a mapping is visible. That is
kept separate from `verification_status`: a fetch proves a link works, not that
the page covers the topic's concepts.

Worth re-running periodically: publishers reorganise. That audit caught
GeeksforGeeks having moved its entire operating-systems and DSA sections behind
new path prefixes, the Hugging Face NLP course becoming the LLM course, and
LangChain funnelling every retrieval URL into its agent docs.

### Question banks

Self-check questions live in `backend/content/questions/`, one YAML file per
module, and are validated on import. The gates exist because generated
questions had failed twice: 94 read `Core idea of {TOPIC}?` with "A vague
buzzword" as a distractor, and one set of eleven dynamic-programming questions
was attached to all twelve DP topics, so the Knapsack page quizzed you on
memoisation. A prompt may no longer appear on two topics at all.

25 banks now cover **239 topics with 1,121 authored questions**. Together with
the hand-written Domain 0, Java and DSA questions that were already sound, the
database holds questions on every one of the 506 topics. `content_health`
reports the state, and every check that should read zero does:

```
cd backend
python -m app.content.content_health
```

| Check | Before | After |
| --- | --- | --- |
| Topics with no questions | 133 | 0 |
| Topics with fewer than 4 questions | 227 | 0 |
| Template-filler questions | 94 | 0 |
| Prompts used on more than one topic | 22 | 0 |

### Repairs have to be pushed back to source

Manifests under `backend/content/curriculum/` are the source of truth for the
topics they define, so a fix applied only to `dev.db` does not survive the next
`import_curriculum` — the first attempt at this silently restored all 94 filler
questions. Two rules follow:

- A topic with a bank in `content/questions/` has no `questions:` block in its
  manifest. Questions live in exactly one place.
- End a repair session with `python -m app.content.sync_manifests`, which
  copies the repaired resource fields and question text back into the
  manifests.

The check that it worked is that `content_health` reads the same before and
after a full index re-import.

### Curriculum coverage

The curriculum is now **506 topics**, up from 449. Ten subjects that were
missing were added with verified resources: Python tooling including `uv`,
reinforcement learning, cloud for AI workloads, AI/ML security, inference
performance, retrieval quality, data quality, gradient boosting, time series,
and CI/CD for ML. Four honest gaps are recorded in the topic descriptions
rather than filled with a weak link — see
[docs/resource-link-integrity.md](docs/resource-link-integrity.md).

```
cd backend
python -m app.content.question_briefs mod-cv     # topics + exact resource URLs to write against
python -m app.content.import_questions --dry-run
python -m app.content.import_questions
```

See [backend/content/questions/README.md](backend/content/questions/README.md).

## The day runner

Two rules that are easy to get backwards, so they are stated here as well as in
the code.

**The stopwatch stops only when you stop it.** Leaving the page, opening the
recall queue, following the resource link, refreshing, reopening the tab
later — none of those pause it. This is a reversal: the earlier rule discarded
any running window older than 15 seconds on the theory that the tab must have
died, which meant opening the recall queue from the Recall block silently threw
the time away. The trade is that a stopwatch left on overnight keeps counting,
so a window longer than four hours is flagged on the page with Reset next to
it. Told, not silently trimmed.

```
cd ai-engine
npm run check:timer     # behaviour checks for the stopwatch rules
```

**The day has no Reflect block.** It used to end with "Close the day", eight
planned minutes, instructing you to answer three prompts — and the finish
screen that appears when the last block is done *is* those three prompts. One
step charged twice, and a block you had to mark Done before the form it pointed
at would appear. The reflection is unchanged and still saves as you type; it
just lives only on the finish screen now. `ACTIVITY_REFLECT` stays defined so
days generated before the change still render.

## Backups

`dev.db` holds everything: the 506-topic curriculum and every completion, streak
and review date. It is gitignored, and so is `backups/`, so **pushing this repo
does not back up any of it.** Two mechanisms cover that, and they fail
differently.

### 1. Local snapshots — automatic

The launcher runs `scripts/backup_db.py` on every start, before anything can
write to the database. It writes `backend/backups/dev-YYYY-MM-DD.db` using the
SQLite online backup API rather than a file copy, so it is safe with the server
up. Keeps the 14 most recent; same-day runs overwrite that day's file.

Instant to restore, useless if the disk goes. Run it by hand any time:

```
cd backend
venv\Scripts\python scripts\backup_db.py
```

### 2. Off-machine snapshot — one double-click

`scripts/export_db.py` writes the entire database as JSON under
`backend/data/snapshot/`, which **is** committed. That is what makes `git push`
a real backup.

Double-click `launcher/Backup to GitHub.bat`: it exports, commits only
`backend/data/snapshot`, and pushes. Committing just that path means it is safe
to run mid-edit — nothing else you are working on is staged or touched.

The launcher prints a reminder on startup whenever the snapshot has uncommitted
changes, so a stale backup is visible rather than silent.

Layout, and why it is split:

| Path | Holds | Changes |
| --- | --- | --- |
| `data/snapshot/schema.sql` | `CREATE TABLE` / `CREATE INDEX` | rarely |
| `data/snapshot/manifest.json` | table -> row count, and which directory | daily |
| `data/snapshot/curriculum/` | topics, resources, questions, exercises | when a content script runs |
| `data/snapshot/progress/` | completions, streaks, plans, reviews | daily |

Rows are ordered by primary key and keys are sorted, so an unchanged table
produces a byte-identical file and an empty diff.

### Restoring

From a local snapshot — a plain file copy. Stop the server, replace
`backend/dev.db` with the chosen file from `backend/backups/`, restart.

From git, on a new machine or after losing the disk:

```
cd backend
venv\Scripts\python scripts\restore_db.py --db dev.db
```

It rebuilds the database from `data/snapshot/`, then runs `integrity_check`.
It refuses to overwrite an existing `dev.db` unless you pass `--force`, because
the day you reach for this is the day a wrong `--db` costs the most.

Dangling foreign keys are reported but never fatal: rows outlive the things they
point at, and a backup that declines to open is not a backup.

`tests/test_db_snapshot.py` runs a full export -> restore round trip on every
test run, including one against the snapshot actually committed here — so this
is checked continuously rather than on the day you need it.

## Current status

Stabilized foundation plus curriculum explorer:

- Roadmap shows Track → Level → Subject → Module → Topic with lock/progress
- Topic and lesson pages: resources, questions, exercises, explicit completion
- Prerequisites evaluated on the backend from topic names
- Demo REST API chain still used as fixture data only — not the final curriculum
- Curriculum manifests (YAML/JSON) with validation and idempotent import

Not implemented yet: daily learning engine, streaks, mastery diagnostics, curriculum UI wired to lessons, projects, journal, interviews.

## Licence and attribution

Engineering OS is the original work of **Akshit Jain**, first published on
22 August 2026 at <https://github.com/akshitjain1/Engineering-OS>.

It is licensed under the **GNU Affero General Public License v3.0** — see
[LICENSE](LICENSE) and [NOTICE](NOTICE). In short:

- You may read, run, study and modify it.
- Any distributed or **network-hosted** derivative must remain under the AGPL
  and must make its source available to its users.
- The copyright notice must be preserved, and modified versions must say that
  they are modified and when.

The curriculum links to material published by GeeksforGeeks, LeetCode, NeetCode,
CS50x, MIT OpenCourseWare and others. Those pages belong to their owners and are
referenced by URL, never redistributed. The selection, sequencing and the
rationale tying each source to a topic are original work and are covered by the
licence.
