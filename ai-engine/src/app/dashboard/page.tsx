"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Clock, Play } from "lucide-react";
import { TodayPlan, type DailyPlan } from "@/components/today-plan";
import { StatusBadge } from "@/components/status-badge";
import { Banner, EmptyState, LoadingLine, Page, ProgressBar } from "@/components/study-ui";
import { FocusAnalyticsWidget } from "@/components/pomodoro";
import { api, errorMessage } from "@/lib/api";
import { getDomainProgress, getWeeklyStudyStats } from "@/lib/analytics";
import type { CurriculumTree } from "@/lib/curriculum";

type FocusTopic = {
  topic_id: number;
  slug: string;
  name: string;
  domain?: string;
  module_name?: string | null;
  locked?: boolean;
  status?: string;
  hours_estimated?: number;
  why?: string | null;
  primary?: { title: string; provider?: string | null; url?: string | null; resource_status?: string; exact?: boolean; is_playlist?: boolean; embeddable?: boolean; lecture?: string | null; video_id?: string | null } | null;
  resource_status?: string;
};

type DashboardSnapshot = {
  today_plan: DailyPlan | null;
  focus?: { current: FocusTopic | null; upcoming: FocusTopic[]; next?: FocusTopic | null };
  curriculum_position: { topic_id: number; name: string } | null;
  this_week?: { week_start: string; capacity_minutes: number; scheduled_minutes: number; remaining_minutes: number };
};

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

const KEY_DOMAIN_KEYS = ["foundations", "java", "dsa", "ml", "mathematics", "backend", "software-engineering"];

export default function Dashboard() {
  const [data, setData] = useState<DashboardSnapshot | null>(null);
  const [tree, setTree] = useState<CurriculumTree | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = () => api<DashboardSnapshot>("/api/dashboard").then((s) => { setData(s); setApiError(null); }).catch((err) => setApiError(errorMessage(err))).finally(() => setLoading(false));
  useEffect(() => { load(); api<CurriculumTree>("/api/curriculum/tree").then(setTree).catch(() => {}); }, []);
  async function generate(minutes?: number) {
    setBusy(true);
    try { await api("/api/daily-plan/generate", { method: "POST", body: JSON.stringify(minutes == null ? {} : { minutes }) }); await load(); }
    catch (err) { setApiError(errorMessage(err)); } finally { setBusy(false); }
  }

  const focus = data?.focus?.current;
  const upcoming = (data?.focus?.upcoming ?? []).slice(0, 3).filter((t) => t.status !== "completed");
  const minutes = data?.today_plan?.total_minutes;
  const week = getWeeklyStudyStats(data?.this_week);
  const today = new Date().toLocaleDateString("en-GB", { weekday: "long", day: "2-digit", month: "long" });
  const domainProgress = getDomainProgress(tree);
  const keyDomains = KEY_DOMAIN_KEYS.map((k) => domainProgress.find((d) => d.key === k)).filter(Boolean) as typeof domainProgress;

  return (
    <Page wide>
      <header className="mb-6 flex flex-wrap items-start justify-between gap-4 border-b border-[var(--border)] pb-6">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">{today}</p>
          <h1 className="mt-1 text-[32px] font-bold tracking-tight">{greeting()}, <span className="text-[var(--accent)]">Akshit</span>.</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">{minutes != null ? `${minutes} minutes planned today` : "Generate a plan from your capacity settings."}</p>
        </div>
        <div className="flex items-center gap-2">
          <Link href={focus ? `/learn/topic/${focus.topic_id}` : "/learn"} className="inline-flex items-center gap-2 rounded-md bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[var(--accent-fg)] hover:bg-[var(--accent-hover)]"><Play className="h-4 w-4" /> Start Focus</Link>
        </div>
      </header>

      {apiError ? <Banner>{apiError}. Start backend on port 8000 if not running.</Banner> : null}
      {loading ? <LoadingLine label="Loading today's workspace…" /> : null}

      {focus ? (
        <section className="mb-6 rounded-[10px] border border-[var(--border)] bg-[var(--card)] shadow-[0_4px_12px_rgba(15,23,42,0.06)]">
          <div className="grid gap-0 lg:grid-cols-[1.4fr_0.9fr_220px]">
            <div className="border-b p-6 lg:border-b-0 lg:border-r">
              <p className="text-xs font-semibold uppercase tracking-widest text-[var(--muted)]">Continue learning</p>
              <h2 className="mt-2 text-2xl font-bold">{focus.name}</h2>
              <p className="mt-1 text-sm text-[var(--muted)]">{(focus.domain || "foundations").toUpperCase()} {focus.module_name ? `· ${focus.module_name}` : ""} {focus.hours_estimated ? `· ~${Math.round(focus.hours_estimated * 60)} min` : ""} · <span className="capitalize">{focus.status ?? "not started"}</span></p>
              {focus.why ? <p className="mt-3 max-w-prose text-sm leading-relaxed">{focus.why}</p> : null}
              <div className="mt-4 flex flex-wrap items-center gap-2">
                {focus.primary?.url ? <a href={focus.primary.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-md bg-[var(--accent)] px-3 py-1.5 text-sm font-medium text-[var(--accent-fg)]">{focus.primary.embeddable ? "Watch source" : "Open source"} <ArrowRight className="h-4 w-4" /></a> : <span className="text-sm text-[var(--warn)]">Source not mapped yet</span>}
                <span className="text-xs text-[var(--muted)]">{focus.primary?.provider ? `${focus.primary.provider} — ` : ""}{focus.primary?.title ?? ""}</span>
              </div>
            </div>
            <div className="border-b p-6 lg:border-b-0 lg:border-r">
              <p className="text-xs font-semibold uppercase tracking-widest text-[var(--muted)]">Today&apos;s plan</p>
              <p className="mt-2 text-3xl font-bold">{minutes ?? 0}<span className="text-sm font-normal text-[var(--muted)]"> min planned</span></p>
              {week ? <p className="mt-2 text-xs text-[var(--muted)]">{week.planned} min planned · {week.capacity} min capacity · {week.available} min available</p> : null}
              <div className="mt-3"><FocusAnalyticsWidget /></div>
            </div>
            <div className="p-6">
              <p className="text-xs font-semibold uppercase tracking-widest text-[var(--muted)]">Action</p>
              <Link href={`/learn/topic/${focus.topic_id}`} className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card)] px-4 py-2.5 text-sm font-medium hover:border-[var(--border-strong)]">Open topic <ArrowRight className="h-4 w-4" /></Link>
              <p className="mt-2 text-xs text-[var(--muted)]">Then: Learn → Practice → Build</p>
            </div>
          </div>
        </section>
      ) : !loading ? <div className="mb-6"><EmptyState title="No topic is waiting" body="Mark current topic complete to unlock next, or open Tracks / Roadmap." /></div> : null}

      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
        <section className="rounded-[10px] border border-[var(--border)] bg-[var(--card)] shadow-sm">
          <div className="border-b border-[var(--border)] px-5 py-3"><h2 className="text-sm font-semibold uppercase tracking-widest text-[var(--muted)]">Today&apos;s plan — timeline</h2></div>
          <div className="p-5"><TodayPlan plan={data?.today_plan ?? null} onGenerate={generate} busy={busy} /></div>
        </section>

        <div className="space-y-6">
          <section className="rounded-[10px] border border-[var(--border)] bg-[var(--card)] p-5 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-[var(--muted)]">Weekly study</h2>
            {week ? (
              <div className="mt-3 space-y-2">
                <div className="flex justify-between text-sm"><span className="text-[var(--muted)]">{week.planned} min planned</span><span className="text-xs text-[var(--muted)]">{week.capacity} min capacity</span></div>
                <ProgressBar value={week.planned} max={week.capacity} />
                <div className="flex justify-between text-xs text-[var(--muted)]"><span>{week.available} min available</span><span>{week.planned} / {week.capacity}</span></div>
                <p className="text-xs text-[var(--muted)]">Planned ≠ completed. Completed is tracked via topic completion.</p>
              </div>
            ) : <p className="mt-2 text-sm text-[var(--muted)]">Not available</p>}
          </section>

          <section className="rounded-[10px] border border-[var(--border)] bg-[var(--card)] p-5 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-[var(--muted)]">Domain progress</h2>
            <ul className="mt-3 space-y-3">
              {keyDomains.map((d) => (
                <li key={d.key} className="space-y-1">
                  <div className="flex items-center justify-between gap-2"><span className="text-sm font-medium">{d.label}</span><span className="text-xs text-[var(--muted)]">{d.completed} / {d.total} · {d.percent}%</span></div>
                  <div className="h-[6px] overflow-hidden rounded-full bg-[var(--border)]"><div className="h-full rounded-full bg-[var(--accent)]" style={{ width: `${d.percent}%` }} /></div>
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs text-[var(--muted)]">completed / total learnable topics · {keyDomains.reduce((s,d)=>s+d.completed,0)} / {keyDomains.reduce((s,d)=>s+d.total,0)} overall</p>
          </section>

          {upcoming.length > 0 ? (
            <section className="rounded-[10px] border border-[var(--border)] bg-[var(--card)] p-5 shadow-sm">
              <h2 className="text-sm font-semibold uppercase tracking-widest text-[var(--muted)]">Up next</h2>
              <ul className="mt-3 space-y-2">
                {upcoming.map((t) => (
                  <li key={t.topic_id}><Link href={`/learn/topic/${t.topic_id}`} className="flex items-center justify-between gap-2 rounded-md border border-[var(--border)] px-3 py-2 hover:border-[var(--border-strong)]"><span className="truncate text-sm font-medium">{t.name}</span><span className="flex items-center gap-2 shrink-0"><span className="hidden text-xs text-[var(--muted)] sm:inline-flex items-center gap-1"><Clock className="h-3 w-3" />~{t.hours_estimated ? Math.round(t.hours_estimated*60) : 30}m</span><StatusBadge status={(t.locked ? "locked" : t.status || "not_started") as never} /></span></Link></li>
                ))}
              </ul>
            </section>
          ) : null}
        </div>
      </div>
    </Page>
  );
}
