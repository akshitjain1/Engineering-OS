# V3 Simplification — Report

Engineering OS as a **personal learning navigator**: WHAT (objective) → WHERE (exact source) → DO (practice) → BUILD (exercise) → DONE. Assessment, mastery, XP, and streaks are no longer part of the product. Curriculum graph is frozen at 222 topics.

## 1. Removed from the product (no longer surfaced anywhere)
- Diagnostic: `/diagnostic` route deleted; `navigation.tsx` nav entry removed from `app-shell.tsx`.
- Assessment quiz: `assessment-quiz.tsx` deleted; topic/lesson pages show no quizzes or scored questions.
- Topic stepper: `topic-stepper.tsx` deleted.
- Exercise answer/self-grading UI: `exercise-answer.tsx` deleted; exercises are now a plain "implement → mark done" checklist.
- XP / streak / level: header chips removed from `app-shell.tsx`; XP/streak fetch removed; dashboard shows no `+30 XP` or streak text.
- Mastery display: `MasteryPill`/mastery panels, mastery percentage on roadmap rows, `pace_mode` tags removed from dashboard/today's plan/practice.
- `/api/mastery` progress page: `/progress` now counts completed topics only (replaces the mastery-status page).
- Orphan components deleted: `assessment-quiz`, `exercise-answer`, `topic-stepper`, `curriculum-progress`, `weekly-progress`, `recent-achievements`, `time-estimate`, `dsa-progress`, `navigation`.

## 2. Remains (by design, on purpose)
- Source-first machinery (`app/content/resources.py`): canonical source types/types/`youtube_video_id`, roles, `verify_source`/`resolve_source` chains — is the delivery vehicle for "WHERE".
- Curriculum sequence + locks: `app/curriculum.py` triple-state helpers (`evaluate_prerequisites`, `is_lesson_complete`, `lesson_ui_status`, `ratio`, `STATE_ALIASES`) — reused unchanged.
- DB tables and old backend endpoints (`/api/diagnostic/*`, `/api/mastery*`, `/api/xp`, `/api/streak`, question/answer endpoints): left in place and unused. `sync_mastery_row(award_bonus=True, sync_revision=True)` remains, but is never triggered by the V3 flows.
- Revision: `/api/revision/*` stays; the product keeps a lightweight "Add to review / I reviewed it" flow (confidence is accepted as a fixed neutral `50` by the UI; no confidence slider).
- `topic-stepper`/questions removed from UI but `QuestionPublic`/`Assessment*` types remain in `lib/curriculum.ts` (harmless, unused).

## 3. Database changes
- No schema changes; no migration. Reused `UserProgress`, `LessonExercise`, `CurriculumResource` (with role), `DailyPlan`, `RevisionSchedule`.
- **New write semantics** (through code, existing tables):
  - `POST /api/topic/{id}/complete` writes a topic-level `UserProgress` row (`lesson_id = NULL`, `topic_id` set, `progress_state = "completed"`) + marks the topic's lessons and exercises complete. Idempotent. **No XP, no `MasteryEvidence`, no `TopicMastery`, no revision writes.**
  - `POST /api/exercise/{id}/complete` marks one exercise complete. No XP/evidence.
- Backend deactivations only: no `content` edits, no curriculum YAML edits, no new tables.
- V3 tests just verify these invariants against the existing schema.

## 4. Backend changes
- `app/learning/planner.py` — **rewritten**:
  - Item types: `LEARN (35)`, `PRACTICE (20)`, `BUILD (25)`, `REVIEW (15)`; `MIN_TAIL_MINUTES = 20`.
  - `TopicView` reduced to `{id, slug, name, locked, lessons_complete, domain, prerequisite_slugs, unfinished_exercises, practice_pending}`.
  - `build_daily_plan(budget_minutes, topics, overdue_revisions, goal)` order: overdue `REVIEW`s → cursor `LEARN` → cursor `PRACTICE` (when `practice_pending`) → cursor `BUILD` (when `unfinished_exercises`) → follow-on `LEARN` (next unlocked incomplete topic after cursor) only if ≥ `MIN_TAIL_MINUTES` remain.
  - why-texts: "Next topic in the curriculum sequence." / "Work the mapped practice sources for the current topic." / "Complete the implementation task for the current topic." / "You added this topic to your review queue." / "Next topic after the current one, when time remains."
  - Output includes `cursor_topic_slug`; asserts `total_minutes <= budget_minutes`.
- `app/learning/service.py`:
  - `topic_completion_state`/`topic_completion_index`: first check a forced topic-level `UserProgress` row (`lesson_id IS NULL`, `progress_state='completed'`); add a `forced` short-circuit set so a V3-completed topic counts fully complete.
  - `build_topic_views`: no `TopicMastery` read; adds `practice_pending` (`_practice_pending_count`) and reuses `_unfinished_exercise_count`.
  - New `complete_topic()` and `mark_exercise_complete()` (see §3).
  - `serialize_focus_topic` simplified: status = `locked | completed | in_progress`; dashboard `curriculum_position` is now `{topic_id, topic_slug, name}`.
- `app/main.py`:
  - `GET /api/roadmap` — exact alias of `GET /api/curriculum/tree`, factored to `_curriculum_tree_payload(db)`.
  - `POST /api/topic/{topic_id}/complete` (404 + `_assert_topic_unlocked` guard).
  - `POST /api/exercise/{exercise_id}/complete` (404 + unlock check via the lesson's topic).

## 5. Frontend changes
- `app-shell.tsx`: header chips (XP/streak/Lv) removed → "Personal learning navigator" + "Source-first · 222 topics"; nav has no Diagnostic.
- `layout.tsx`: metadata description = "Personal learning navigator: the sequence, the source, practice, build, revise."
- `dashboard/page.tsx`: greeting, Continue hero (primary source button "Watch source"/"Open source" or warn when unverified, plus Open-topic link), Today's goal + `TodayPlan` (generate 30/60/90/120/180), Up next list with `StatusBadge`, `EmptyState` when no focus.
- `learn/page.tsx`: "Continue the sequence" with current topic card (no MasteryPill).
- `learn/topic/[id]/page.tsx`: **rebuilt as the V3 topic view** — breadcrumb, objective, lock card, "What to do" checklist (Learn from the source / Practice / Build / optional Deep dive with tick states), Learn From (PRIMARY via `SourceResourceCard`), Practice (mapped sources **or** copyable GPT-prompt block when unmapped + unlocked), Build (exercise list + "Mark implementation complete" → `POST /api/exercise/{id}/complete`), optional Deep dive, done-state → Next topic from `next_in_sequence`; "Mark topic complete" → `POST /api/topic/{id}/complete`; "Add to review" → `POST /api/revision/schedule?…&confidence=50`.
- `learn/lesson/[id]/page.tsx`: removed the whole "Assess" (questions) section and `QuestionCard`; exercises route through `POST /api/exercise/{id}/complete` for completion.
- `progress/page.tsx`: **rewritten** — "Topics completed / 222" + continue card + per-domain bars. No mastery.
- `revision/page.tsx`: **rewritten** — read-only queue, "Start revision" / "Mark reviewed" (`confidence=50`).
- `roadmap/page.tsx`: mastery percentage removed from topic rows; copy now says "Topics are completed or not — no mastery scores."
- `practice/page.tsx`: `pace_mode` tag removed; copy keeps "exact problem URLs only shown when stored".
- `settings/page.tsx`: copy no longer mentions mastery/XP.
- Type additions confirmed present in `lib/curriculum.ts`: `TopicNode.resources_by_role` (incl. `DEEP_DIVE`, `OTHER`), `.implement`, `.learning_objective`, `.breadcrumb.module_name`, `.next_in_sequence`, `.hours_estimated`, `.lock_message`, `.domain`.

## 6. Planner behavior (verified)
- Cursor = first unlocked incomplete topic in sequence (domains in order Foundations → Java → DSA).
- Completed topics never produce LEARN items; locked topics never appear.
- Review items come first, then Learn, then Practice, then Build, then follow-on Learn when the tail (≥20m) exists.
- No item text references mastery, diagnostic, or pace; the plan is fully derivable from completion state alone.

## 7. Tests
- `backend/tests/test_learning_engine.py`: planner tests rewritten to V3 semantics (`/api/curriculum/tree` views, budget/tail behavior, cursor sequencing, no-mastery no-diagnostic why-texts).
- `backend/tests/test_v3_simplification.py` (new, 8 tests, seed: SE-V3/Bits → cf-bits-and-bytes + cf-binary with prerequisite):
  1–2. `complete` topic is idempotent, writes exactly one topic-level `UserProgress('completed')`, completes lesson+exercise, **no** `MasteryEvidence`/`TopicMastery`/`RevisionSchedule`, `/api/xp` stays 0.
  3. Completing unlocks the next topic (roadmap + topic detail, `prerequisites[0].complete`).
  4. Locked topic → 403 "locked".
  5. `POST /api/exercise/{id}/complete` completes the exercise with no XP/evidence/UserProgress.
  6. `/api/roadmap` mirrors `/api/curriculum/tree` (same next + node).
  7–8. Planner emits only LEARN/PRACTICE/BUILD/REVIEW; completed bits is never a LEARN item afterward.
- Full backend suite: **132 passed, 1 warning in 107.29s** (warning: StarletteDeprecationWarning — httpx vs `starlette.testclient`, benign). Log: `%TEMP%\eos-pytest.log`.

## 8. Build / lint
- `npm run lint` — clean (0 errors; fixed an unused-import warning).
- `npm run build` — passes under Next.js 16.3.1 (Turbopack): 16 routes, no TS errors. (Deleted the stale `.next/dev/types` referencing the removed `diagnostic` route before rebuilding.)
- `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload` restarted to load the new backend; endpoints verified live:
  - `GET /api/roadmap` → 2 tracks, next = Bits and bytes.
  - `GET /api/dashboard` → focus + `curriculum_position{topic_slug}` + regenerated **LEARN-only** plan (stale V2 plan types ASSESSMENT/TRANSFER/JOURNAL were rebuilt by `POST /api/daily-plan/generate {minutes:60}`), `total 35 ≤ 60`.
  - `GET /api/topic/5` → `not_started`, objective set, PRIMARY=2, implement=1.

## 9. Limitations / notes
- Old endpoints and tables remain live and writable; nothing deletes or migrates them. A future V4 could drop them.
- `confidence` is still a required parameter of `/api/revision/schedule`; the UI sends a fixed `50`.
- `TOPIC` completion is a one-way operation: there is no un-complete endpoint at topic level (matching "completed or not").
- `practice_pending` counts PRACTICE-role resources that are not complete across a topic's lessons; it does not inspect problem-level exactness.
- The dashboard reads today's stored `DailyPlan` row; any plan generated before the V3 backend upgrade will show legacy item types until regenerated.
- Live checks intentionally avoided mutating the real DB beyond regenerating today's plan (topic/exercise completion semantics are covered by pytest).