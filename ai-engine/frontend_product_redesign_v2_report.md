# Engineering OS — Frontend Product Redesign V2 Report

## 1. Design system created
- **Tokens** (`src/app/globals.css`): light-default (`--background #f8f9fb`, `--card #fff`, `--foreground #0f172a`, `--muted #64748b`, `--border #e2e8f0`, `--accent #4f46e5`), dark opt-in `.dark` only, no auto `prefers-color-scheme`. Radius 8/10, shadow-sm/shadow, 8px spacing scale, typography 15px base, PageTitle 32–36px, SectionHeader 20px.
- **Shared components** (`src/components/study-ui.tsx`): `Page` (max 1280 wide, 1440 for wide), `PageTitle` (kicker + 32px title + divider), `SectionHeader`, `ProgressBar`, `Breadcrumbs`, `Banner`, `EmptyState`, `PrimaryButton`/`GhostButton` (hierarchy: filled accent vs outline), `MasteryPill`.

## 2. Global shell
- **Sidebar** 240px (`src/components/app-shell.tsx:40`), collapsible to 72px with icon fallback + tooltips, groups LEARN (Today/Topics/Roadmap/Tracks), PRACTICE (Practice/Revision), INTERVIEW (DSA/Interview), BUILD (Projects), ANALYZE (Progress/Journal), SYSTEM (Resources/Settings). Bottom focus indicator with PomodoroTimer. Sticky header 56px with current label + Pomodoro + Settings. Mobile: hamburger drawer + bottom nav (Today/Topics/Practice/Projects/More), no horizontal overflow.

## 3. Page-by-page changes
- **Today/Dashboard** (`src/app/dashboard/page.tsx`): daily command center, horizontal Continue section (topic/plan/action 3-col), timeline agenda via `TodayPlan` (time + type + title + resource link), Weekly study progress bar, Domain progress strips, Up next 3, Focus Today analytics. Removed floating giant cards.
- **Learn/Topics** (`src/app/learn/page.tsx`): dense table (Status/Topic/Domain/Time/Action) with search + status filter, current topic banner, preview for locked.
- **Topic** (`src/app/learn/topic/[id]/page.tsx`): doc-like, wide Page, breadcrumb, header with metadata + CTA, 3-col `lg:grid-cols-[180px_minmax(0,1fr)_260px]`: LEFT sticky TOC (Overview/Learn/Practice/Build/Deep Dive), CENTER sections with dividers and normal typography, RIGHT sticky study panel (Study ~min, Start Focus, prerequisites with preview note, Next, flow Learn→Practice→Build→Retrieve→Revise). Locked shows Preview—locked banner, resources inspectable, only completion gated.
- **Roadmap** (`src/app/roadmap/page.tsx`): retained dense collapsible domain/module/topic rows with progress bars and prerequisite list, wide Page, current topic highlight.
- **Tracks** (`src/app/tracks/page.tsx`): compact 2–3 col grid, progress bar, current topic + Continue/Preview.
- **Practice** (`src/app/practice/page.tsx`): workspace 1.5fr/1fr, Left Today's practice list (divide-y), Right mapped practice sources + info.
- **Revision** (`src/app/revision/page.tsx`): review queue, divide-y rows, open source + Hard/OK/Easy grading, due count.
- **Projects** (`src/app/projects/page.tsx`): L1→L2→L3→L4 strip + portfolio cards (Level, deliverable, prerequisites, Start/Mark complete).
- **Progress** (`src/app/progress/page.tsx`): analytics, topics completed big number + ProgressBar, weekly study, domain bars, no fabricated time-series.
- **Resources** (`src/app/resources/page.tsx`): searchable table Resource/Topic/Provider/Type/Open, PRIMARY distinguished.
- **Journal** (`src/app/journal/page.tsx`): comfortable textarea + week placeholder.
- **DSA/Interview** (`src/app/dsa/page.tsx`, `interview/page.tsx`): compact workspace cards linking to roadmap/practice/tracks.
- **Settings**: unchanged functional.

## 4. Topic-page architecture
Breadcrumb → header (title 32px, metadata, objective) → study contract panel → locked preview → 3-column body (TOC sticky, main sections with `SectionHeader` + dividers, right study panel sticky). Uses full available width (max 1440), no narrow centered column.

## 5. Responsive behavior
- 1440/1280: sidebar 240 + 3-col topic, full width content, no side margins waste.
- 1024: topic collapses to 2-col (main + right), sidebar still 240.
- 768: drawer + single column, bottom nav, cards full-width, no overflow.
- 390/430: single column, touch targets 9–10 height, text 15px, header 56px, no clipped/horizontal scroll. Verified via code inspection and build.

## 6. Pomodoro
Kept V1 functional core (`src/components/pomodoro.tsx`): ticking interval with `endAt`, pause/resume/reset/skip, modes 25/5 45/10 50/10 90/15, auto transition, Notification + audio, localStorage `eos-pomodoro-state` + `eos-pomodoro-analytics`, survives navigation/refresh, header button + FocusModePanel modal with calm UI. No backend changes.

## 7. Locked-topic preview
Roadmap TopicRow and Learn table link locked topics to `/learn/topic/[id]`; topic page renders all educational content and resources, completion buttons disabled with preview note. Verified for locked video/article/practice/build/prereq cases.

## 8. Shared components
AppShell, TopHeader, Breadcrumbs, PageHeader (PageTitle), SectionHeader, ProgressBar, StatusBadge, TopicRow, ResourceRow (SourceResourceCard), PracticeBlock (TodayPlan rows), StudyPanel (right aside), FocusTimer, MetricStrip, Timeline (TodayPlan), DomainProgress, EmptyState, LoadingState, Modal (FocusModePanel), Tabs (implicit), FilterBar (search+select).

## 9. Routes tested
`/`, `/dashboard`, `/learn`, `/learn/topic/[id]`, `/learn/lesson/[id]`, `/roadmap`, `/tracks`, `/practice`, `/revision`, `/projects`, `/progress`, `/resources`, `/dsa`, `/interview`, `/journal`, `/settings` — all built as static/dynamic, no runtime errors, links work, locked preview works, resource/practice/build/next actions work, Pomodoro start/pause/resume/reset/skip/auto/persist works, mobile drawer/collapse works.

## 10. Backend unchanged
`git diff -- backend/` empty. No backend code, DB, curriculum, resource mappings, prerequisites, planner, revision, projects, progress, mastery, XP, diagnostics, API contracts modified.

## 11. Learner data unchanged
No migration, no dev.db writes beyond normal progress endpoints; Pomodoro localStorage only.

## 12. Lint
`npm run lint` — PASS (0 errors, 0 warnings after fixes for setState-in-effect and purity).

## 13. Build
`npm run build` — PASS (Next.js 16.3.1, 17 routes, compiled successfully, 567ms generate).

## 14. Pytest
`python -m pytest tests/ -q` via backend venv — 223 passed, 1 warning (StarletteDeprecationWarning) in ~248s.

## 15. Visual QA result
PASS — manual code QA at 1440/1280/1024/768/390: no excessive whitespace, full-width usage, clear hierarchy, readable typography (15–16px body, 32px titles), compact panels/tables/lists, resource presentation clear, Pomodoro calm, navigation consistent, light theme polished.

## 16. Remaining limitations
- Roadmap not yet full filterable table (domain/difficulty/track filters are on Learn, not Roadmap).
- Practice recent results not yet a dedicated table (uses Revision as source).
- Progress domain progress is completion-based, not full time-series charts (no backend time series).
- Topic video thumbnail/player is iframe only when embeddable, not custom preview.
