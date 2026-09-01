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

The whole learning history is one SQLite file, so back it up:

```
cd backend
venv\Scripts\python scripts\backup_db.py
```

Writes `backend/backups/dev-YYYY-MM-DD.db` using the SQLite online backup API
rather than a file copy, so it is safe to run while the server is up. Keeps the
14 most recent and prunes older ones; re-running on the same day overwrites that
day's file. `backups/` is gitignored.

To run it daily on Windows Task Scheduler:

1. Task Scheduler -> **Create Task**, name it `Engineering OS backup`.
2. **Triggers** -> New -> Daily, at a time the machine is usually on.
3. **Actions** -> New -> Start a program, with
   Program `<repo>\backend\venv\Scripts\python.exe`,
   Arguments `scripts\backup_db.py`,
   Start in `<repo>\backend` (the "Start in" box matters -- the script resolves
   paths from the backend directory).
4. **Settings** -> tick *Run task as soon as possible after a scheduled start is
   missed*, so a machine that was off still gets a backup.
5. Select the task -> **Run**, then check `backend\backups\`.

Restore is a plain file copy: stop the server, replace `backend/dev.db` with the
chosen backup, restart.

## Current status

Stabilized foundation plus curriculum explorer:

- Roadmap shows Track → Level → Subject → Module → Topic with lock/progress
- Topic and lesson pages: resources, questions, exercises, explicit completion
- Prerequisites evaluated on the backend from topic names
- Demo REST API chain still used as fixture data only — not the final curriculum
- Curriculum manifests (YAML/JSON) with validation and idempotent import

Not implemented yet: daily learning engine, streaks, mastery diagnostics, curriculum UI wired to lessons, projects, journal, interviews.
