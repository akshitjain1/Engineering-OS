# Learner Database Reconciliation Report

Generated: 2026-08-26T13:44:25.570028+00:00

## Current Runtime DB

- **Path:** `backend/dev.db` (resolved: `D:/Akshit Personal OS/backend/dev.db`, `DATABASE_URL` default `sqlite:///./dev.db`)
- **Size:** 3,149,824 bytes, Modified: 2026-08-26 19:09:53
- **Topics:** 449, Learner units: 441, Domains: 20, Projects: 16, Resources: 921
- **User data:** 6 user_progress, 0 topic_mastery, 0 mastery_evidence, 0 XP (level 1), 0 revision, 0 diagnostics
- **Status:** **FRESH** — minimal progress, no mastery history

## Candidate Historical DBs

| Path | Size | Modified | Topics | user_progress | mastery | evidence | XP | Activities | Verdict |
|---|---|---|---|---|---|---|---|
| `dev.db` | 3,149,824 | 2026-08-26 19:09 | 449 | 6 | 0 | 0 | 0 (L1) | 0 | Fresh |
| `dev.db.20260819-194409.bak` | 1,499,136 | 2026-08-19 19:17 | 226 | 3 | 80 | 95 | 888 (L9) | 323 | **REAL HISTORY** |
| `dev.db.pre_curriculum...133804.bak` | 3,145,728 | 2026-08-26 18:42 | 449 | 6 | 0 | 0 | 0 | 0 | Fresh backup |
| `data.db` | 0 | 2026-08-23 | 0 | — | — | — | — | — | Empty |

## Analysis

**Real learner DB:** `backend/dev.db.20260819-194409.bak`

**Why:** It is the only candidate with non-trivial history: 80 topic_mastery, 95 mastery_evidence, 888 XP, 37 xp_events, 323 learning_activities, 76 diagnostic answers. All other candidates have 0 mastery/0 XP.

**Current DB is fresh:** 449 topics but 0 mastery — this is the expanded curriculum's clean state, not the learner's history.

**What must be preserved (from historical DB):**
- user_progress (3 rows)
- topic_mastery (80 rows)
- mastery_evidence (95 rows)
- user_xp (888 XP, level 9)
- xp_events (37)
- revision_schedules (2)
- diagnostic_sessions (1) + diagnostic_answers (76)
- learning_activities (323)

**Migration is safe:** 226 → 449 is additive; all 80 mastery slugs exist in the 449 set (spine intact); no XP should be regenerated.

## Source of Truth

**LEARNER DATABASE SOURCE OF TRUTH = UNAMBIGUOUS**

- Historical backup holds real learner data; current runtime DB is fresh.
- No uncertainty in identification — quantitative comparison is decisive.
- Open question is WHEN to migrate, not WHICH DB.

## Recommendation

**DO NOT overwrite the historical backup. DO NOT import the 449 curriculum into it yet without a migration script.**

For this verification pass, Part B proceeds against the **actual runtime DB (449-topic)** as the intended final curriculum's runtime state. Learner onboarding must include a dedicated migration of the 80 mastery / 888 XP history before the 12-month journey begins.

## Configuration

- `DATABASE_URL` env: **not set** (resolved to `sqlite:///./dev.db`)
- `.env` file: does not exist (uses default)
- `app/db/session.py` resolves relative `sqlite:///./dev.db` to `BACKEND_DIR/dev.db`

## Stop Condition

Part A is **COMPLETE and UNAMBIGUOUS** — proceeding to Part B per instructions (proceed only if source of truth unambiguous).
