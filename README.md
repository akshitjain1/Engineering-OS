# Akshit Engineering OS

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

## Backups

`dev.db` holds everything: the 449-topic curriculum and every completion, streak
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
