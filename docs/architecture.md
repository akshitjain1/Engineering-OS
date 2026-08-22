# Architecture

## Overview

Two processes: Next.js frontend (port 3000) talking over HTTP/JSON to a FastAPI backend (port 8000). SQLite file `backend/dev.db` holds all data. Everything runs locally; no external services required.

```
Browser
  │
  ▼
Next.js 16 (App Router, client components fetch API)
  │  GET/POST http://127.0.0.1:8000/api/*
  ▼
FastAPI (app/main.py)
  │
  ▼
SQLAlchemy 2.0 ORM (app/db/models.py, single Base in app/db/session.py)
  │
  ▼
SQLite backend/dev.db  (schema is PostgreSQL-compatible; switch via DATABASE_URL)
```

## Decision notes

- **Single SQLAlchemy Base** — `app/db/session.py` defines `Base(DeclarativeBase)`. Models import that class. `app/db/base.py` re-exports it for compatibility. A previous split (`declarative_base()` vs `DeclarativeBase`) meant `create_all()` in `main.py` used empty metadata and would not create tables on a fresh install.
- **SQLAlchemy 2.0 portable columns** — Integer, String, Text, Float, Boolean, DateTime, JSON only, so PostgreSQL is a swap via `DATABASE_URL`.
- **Relative SQLite paths** — resolved against the `backend/` directory, not the process cwd.
- **SQLAlchemy models ≠ API models** — endpoints return dicts; Pydantic is used for request bodies (`DSATopicCreate`).
- **Single user "akshit"** — `user_id` default on progress/XP/revision. No auth.
- **CORS**: backend allows http://localhost:3000 and http://127.0.0.1:3000 only.
- **Resources are metadata** — URLs stored as rows; no media is downloaded.
- **Prerequisites** — JSON list of topic **slugs** (demo files) or legacy names. `app/curriculum.py` resolves either. A topic is complete only when it has at least one lesson and every lesson is `completed`/`mastered`/`fast_tracked`.
- **Curriculum import** — YAML/JSON manifests in `backend/content/curriculum/`, validated then upserted by slug (`python -m app.content.import_curriculum`). Content fields update; user progress is preserved.
- **Curriculum tree** — `GET /api/curriculum/tree` returns Track → Level → Subject → Module → Topic with lock/progress. `GET /api/topic/{id}` is the topic detail (distinct from legacy `GET /api/topics/{module_id}`).
- **Lesson UI states** — `not_started`, `in_progress`, `completed`. Legacy states (`learning`, `mastered`, …) map onto these. Completing a lesson awards 10 XP once.
- **Question attempts** — `POST /api/questions/{id}/attempt`. GET lesson does not include the answer key. `options` JSON is additive on `lesson_questions` (SQLite column patch + Alembic `8c1e4f2a9b70`).
- **create_all + Alembic** — startup `create_all` keeps local SQLite usable; `alembic/versions` holds the initial schema for Postgres/empty DBs. Do not `upgrade` over an already-created SQLite file; `stamp head` instead.

## Database schema (tables)

| Table                  | Purpose                                             |
| ---------------------- | --------------------------------------------------- |
| curriculum_tracks      | Top-level tracks                                    |
| curriculum_levels      | Levels within a track                               |
| curriculum_subjects    | Subjects                                            |
| curriculum_modules     | Modules within a subject                            |
| curriculum_topics      | Topics with `prerequisites` JSON + `fast_trackable` |
| curriculum_lessons     | Lessons with completion/mastery status, hours       |
| curriculum_resources   | Resource metadata                                   |
| lesson_questions       | Q&A bank per lesson                                 |
| lesson_exercises       | Practical exercises per lesson                      |
| dsa_topics             | DSA patterns/problems                               |
| user_progress          | Per-item progress; null-FK row is the overview/streak placeholder |
| user_xp                | One XP row per user (`user_id` unique)              |
| revision_schedules     | Spaced repetition queue                             |

Tables for projects, interviews, and journal are **not** created yet. Add them when those features are specified.

## Progress states (domain)

`not_started → learning → practicing → mastered / fast_tracked → needs_revision`

## Revision algorithm

Confidence 0–100 maps onto interval ladder `[1, 3, 7, 14, 30, 60]` days via `interval_index = min(max(int(confidence/20), 0), 5)`. Rescheduling an existing item recalculates `next_review`. Pending = `next_review` within the next 24 hours.

## XP

`GET /api/progress` reports `xp_earned` from `user_xp.total_xp`, not from a leftover progress row. Level = `total_xp // 100 + 1`. `sessions_completed` increments only when `activity` is `session` or `session_complete`.

## Testing notes

- `backend/tests/test_models.py` — shared Base + insert
- `backend/tests/test_api.py` — TestClient against in-memory SQLite (`StaticPool`)
- `npx next build` is the frontend verification gate
