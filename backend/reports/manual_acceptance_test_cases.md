# Manual Acceptance Test Cases — Final Closure Pass

Automated equivalents live in `backend/scripts/final_acceptance.py` (T1–T10,
all passing). Manual steps below cover what only a human/UI can confirm.

---

## TEST 1 — Absolute beginner (T1 automated)
**Input:** zero completed topics.
**Verify:** dashboard schedules CS-Foundations CORE + Java-runway parallel
items only; no ML/DL/CV model topics appear. `cf-bits-and-bytes` has no
prerequisites — no jump.

## TEST 2 — DSA parallel start (T2)
**Verify:** `dsa-algorithmic-thinking` gate = {cf-time-complexity-intro,
java-method-basics}. Deep-Java (streams/concurrency/JVM) NOT required.
Simulation shows DSA first scheduled day ~95 while deep Java arrives ~122.

## TEST 3 — ML beginner journey (T3)
**Chain:** ML awareness (day ~15) → just-in-time math bridge
(math-derivatives) → loss → gradient-descent intuition (serious ML, day ~25)
→ algorithms (logistic/trees/KNN…). Bridge endpoint returns minimal missing
set, never the whole math domain.

## TEST 4 — DL beginner (T4)
**Verify:** backprop chain enforces math-partial-derivatives + forward-prop +
loss before backprop-intuition; transformers gated on attention chain.

## TEST 5 — CV beginner (T5)
**Verify:** image representation units precede convolution-in-CV which itself
requires dl-feature-maps (CNN mechanics) — no giant "Learn Computer Vision"
topic exists (25 granular CV units).

## TEST 6 — Revision (T6)
**Steps:** schedule confidence=10 → interval 1d; then confidence=90 → 30d;
then confidence=20 → resets toward 1d, ease drops, fail-count increments.
UI offers Hard/OK/Easy retrieval grading, not "read it again".

## TEST 7 — Resource boundaries (T7 + boundary audit)
**Verify:** every learner-visible PRIMARY has exactness ∈ {EXACT, SEGMENT}
and estimated_minutes>0. Boundary audit reports **0** entire-books, **0**
entire-playlists, **0** collection PRIMARYs visible.

## TEST 8 — Practice exercises match concepts (T8)
**Verify:** all 109 decomposition practice contracts reference their own
topic slug in concepts_required; planner emits PRACTICE daily (30/30 days).

## TEST 9 — Broken PRIMARY cannot stay READY (T9)
**Steps:** flip one VERIFIED_COVERAGE primary to BROKEN inside a transaction;
`audit_topic` readiness becomes BROKEN; rollback restores. Automated proof:
PASS (cf-machine-code case).

## TEST 10 — Missing prerequisite blocks + bridge (T10)
**Steps:** request `/api/prerequisite-bridge/dl-nn-basics` with nothing
completed → blocked=true, 17-item ordered bridge with per-item minutes and
total; completing bridge items shrinks it until unblocked.
