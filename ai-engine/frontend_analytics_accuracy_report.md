# Analytics Accuracy + Visual Depth Report

## 1. Root cause of domain-progress inaccuracy
Dashboard Domain Progress used synthetic values: `20 + (i*7)%40` per label (`src/app/dashboard/page.tsx:126` before), not derived from topic completion. No filtering of learnable topics, no mapping between display label and backend `domain` key, hardcoded 8 labels.

## 2. Formula before
```ts
// dashboard before
["Foundations","Java","DSA","ML","DL","CV","NLP","GenAI"].map((d,i)=>
  <div style={{width: `${20 + (i*7)%40}%`}} />)
// implies arbitrary 20–55% with no data source
```

## 3. Formula after
```ts
// lib/analytics.ts
percent = total ? Math.round(completed/total*100) : 0
where completed = topics.filter(t=>t.status==="completed").length
      total = topics.filter(isLearnable).length
      grouped by normalizeDomainKey(t.domain)
```
Central helper `getDomainProgress(tree)` groups by canonical key, filters learnable (slug present), counts actual status. Same denominator used everywhere.

## 4. Centralized analytics helpers created
`src/lib/analytics.ts`:
- `DOMAIN_CONFIG` + `CANONICAL_MAP` (foundations/java/dsa/ml/mathematics/backend/software-engineering + future dl/cv/nlp/genai)
- `normalizeDomainKey()`, `getAllTopics()`, `getCompletedTopicCount()`, `getDomainProgress()`, `getTrackProgress()`, `getWeeklyStudyStats()`
All derived calculations live in one place; dashboard/progress/tracks/roadmap now import same helpers.

## 5. Dashboard metrics audited
- Domain progress: now `completed/total · percent` per domain from `getDomainProgress` (key domains: foundations, java, dsa, ml, mathematics, backend, software-engineering). Visual: `h-[6px]` bar, `completed / total · percent`.
- Weekly study: uses `getWeeklyStudyStats` with accurate labels: `X min planned`, `Y min capacity`, `Z min available` and note "Planned ≠ completed".
- Up Next: filtered `t.status !== "completed"`, status via real `t.locked`/`t.status`.
- Continue: `focus.status` from backend, `hours_estimated` actual, PRIMARY actual.
- Today's timeline: duration = planner `item.minutes` preserved.
- Focus analytics: uses `FocusAnalyticsWidget` (Pomodoro localStorage), not planned minutes.

## 6. Progress metrics audited
`src/app/progress/page.tsx` now uses `getCompletedTopicCount` → `completed / total learnable` (actual 6/449) with percent, domain bars via `getDomainProgress` filtered `total>0`.

## 7. Track metrics audited
Tracks page keeps backend `/api/study-tracks` (already tracks real topic counts) but now consistent with same denominator definition (learnable topics). No resource/module count used.

## 8. Roadmap metrics audited
Roadmap `ModuleBlock`/`TrackCard` progress uses backend `module.progress`/`track.progress` which are derived from `topic.status==="completed"` counts (verified in `app/curriculum.py:ratio`).

## 9. Visual depth changes
Kept current light layout; added subtle hierarchy without redesign:
- Page bg `#f8f9fb`, surface `#fff`, border `#e2e8f0`, shadow `0 1px 3px rgba(15,23,42,0.06)` and level-2 `0 4px 12px rgba(15,23,42,0.06)` on Continue panel
- Panels: `rounded-[10px] border shadow-sm` (or shadow on elevated Continue)
- Domain bars: 6–8px thick, accent only, no rainbow
- No heavy shadows, no layout change, no sidebar/typography change

## 10. Backend unchanged
`git diff -- backend/` empty.

## 11. Learner data unchanged
No DB writes; Pomodoro localStorage only.

## 12. Pytest
223 passed (backend venv, ~276s)

## 13. Lint
pass

## 14. Build
pass (Next 16.3.1, 17 routes)

## 15. Responsive QA
1440/1280/1024/768/430/390 checked: no overflow, borders visible, bars aligned, shadows subtle, numbers readable.

---

### Domain progress — actual current data (from `/api/curriculum/tree`)

| Domain | Completed | Total | Percent |
|---|---|---|---|
| Backend | 0 | 12 | 0% |
| DSA | 0 | 106 | 0% |
| Foundations | 6 | 219 | 3% |
| Java | 0 | 52 | 0% |
| Machine Learning | 0 | 35 | 0% |
| Mathematics | 0 | 15 | 0% |
| Software Engineering | 0 | 10 | 0% |
| **Overall** | **6** | **449** | **1%** |

Configured future keys (dl/cv/nlp/genai/ai-engineering) show 0/0 → 0% until curriculum adds topics.
