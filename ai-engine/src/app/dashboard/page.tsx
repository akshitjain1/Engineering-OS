"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Clock } from "lucide-react";
import { TodayPlan, type DailyPlan } from "@/components/today-plan";
import { StatusBadge } from "@/components/status-badge";
import { Banner, EmptyState, LoadingLine, Page } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";

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
  primary?: {
    title: string;
    provider?: string | null;
    url?: string | null;
    resource_status?: string;
    exact?: boolean;
    is_playlist?: boolean;
    embeddable?: boolean;
    lecture?: string | null;
    video_id?: string | null;
  } | null;
  resource_status?: string;
};

type DashboardSnapshot = {
  today_plan: DailyPlan | null;
  focus?: { current: FocusTopic | null; upcoming: FocusTopic[]; next?: FocusTopic | null };
  curriculum_position: { topic_id: number; name: string } | null;
  this_week?: {
    week_start: string;
    capacity_minutes: number;
    scheduled_minutes: number;
    remaining_minutes: number;
  };
};

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

function nextAction(plan: DailyPlan | null, position: DashboardSnapshot["curriculum_position"]) {
  const item = plan?.items?.[0];
  if (item?.topic_id) return `/learn/topic/${item.topic_id}`;
  if (position?.topic_id) return `/learn/topic/${position.topic_id}`;
  return "/learn";
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardSnapshot | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = () =>
    api<DashboardSnapshot>("/api/dashboard")
      .then((snapshot) => {
        setData(snapshot);
        setApiError(null);
      })
      .catch((err) => setApiError(errorMessage(err)))
      .finally(() => setLoading(false));

  useEffect(() => {
    load();
  }, []);

  async function generate(minutes?: number) {
    setBusy(true);
    try {
      const body = minutes == null ? {} : { minutes };
      await api("/api/daily-plan/generate", {
        method: "POST",
        body: JSON.stringify(body),
      });
      await load();
    } catch (err) {
      setApiError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const focus = data?.focus?.current;
  const upcoming = (data?.focus?.upcoming ?? []).slice(0, 3);
  const minutes = data?.today_plan?.total_minutes;
  const week = data?.this_week;
  const today = (() => {
    const d = new Date();
    const weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const months = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];
    return `${weekdays[d.getDay()]} ${d.getDate()} ${months[d.getMonth()]}`;
  })();

  return (
    <Page>
      <header className="mb-6">
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-[var(--muted)]">{today}</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight sm:text-3xl">
          {greeting()}, <span className="text-gradient">Akshit</span>.
        </h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          {minutes != null ? `${minutes} minutes planned today.` : "Generate a plan from your capacity settings."}
        </p>
      </header>

      {apiError ? <Banner>{apiError}. Start the backend on port 8000 if it is not running.</Banner> : null}
      {loading ? <LoadingLine label="Loading today’s workspace…" /> : null}

      {week ? (
        <section className="mb-6 rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3 text-sm">
          <p className="text-xs uppercase tracking-[0.14em] text-[var(--muted)]">This week</p>
          <p className="mt-1">
            {week.scheduled_minutes}m scheduled · {week.capacity_minutes}m capacity · {week.remaining_minutes}m left
          </p>
        </section>
      ) : null}

      {focus ? (
        <section className="glow-card mt-2 overflow-hidden">
          <div className="h-1 w-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-2)]" />
          <div className="p-5 sm:p-6">
            <p className="text-xs font-medium uppercase tracking-[0.16em] text-[var(--muted)]">Continue</p>
            <h2 className="mt-1.5 text-xl font-semibold tracking-tight sm:text-2xl">{focus.name}</h2>
            <p className="mt-1 text-sm text-[var(--muted)]">
              {(focus.domain || "foundations").toUpperCase()}
              {focus.module_name ? ` · ${focus.module_name}` : ""}
              {focus.hours_estimated ? ` · ~${Math.round(focus.hours_estimated * 60)} min` : ""}
            </p>
            {focus.why ? <p className="mt-3 max-w-prose text-sm leading-relaxed">{focus.why}</p> : null}

            {focus.primary?.url ? (
              <div className="mt-4 flex flex-wrap items-center gap-3">
                <Link
                  href={focus.primary.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex h-10 items-center gap-2 rounded-lg bg-[var(--accent)] px-4 text-sm font-medium text-[var(--accent-fg)] transition-opacity hover:opacity-90"
                >
                  {focus.primary.embeddable ? "Watch source" : "Open source"}
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <span className="text-xs text-[var(--muted)]">
                  {focus.primary.provider ? `${focus.primary.provider} — ` : ""}
                  {focus.primary.title}
                </span>
              </div>
            ) : (
              <p className="mt-3 text-sm text-[var(--warn)]">
                Source not mapped yet — no URL is invented. Open the topic to see readiness.
              </p>
            )}

            <div className="mt-5">
              <Link
                href={nextAction(data?.today_plan ?? null, data?.curriculum_position ?? null)}
                className="inline-flex items-center gap-2 rounded-lg px-2 py-1 text-sm font-medium text-[var(--accent)] hover:text-[var(--foreground)]"
              >
                Open topic <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>
      ) : !loading ? (
        <div className="mt-6">
          <EmptyState
            title="No topic is waiting"
            body="Mark the current topic complete to unlock the next one, or open Tracks / Roadmap."
          />
        </div>
      ) : null}

      <section className="mt-8">
        <TodayPlan plan={data?.today_plan ?? null} onGenerate={generate} busy={busy} />
      </section>

      {upcoming.length > 0 ? (
        <section className="mt-8">
          <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">Up next</h2>
          <ul className="mt-3 space-y-2">
            {upcoming.map((topic) => (
              <li key={topic.topic_id}>
                <Link
                  href={topic.locked ? "#" : `/learn/topic/${topic.topic_id}`}
                  className="flex items-center justify-between gap-3 rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-2.5 transition-colors hover:border-[var(--accent)]"
                >
                  <span className="truncate text-sm font-medium">{topic.name}</span>
                  <span className="flex shrink-0 items-center gap-2">
                    {topic.hours_estimated ? (
                      <span className="inline-flex items-center gap-1 text-xs text-[var(--muted)]">
                        <Clock className="h-3 w-3" /> ~{Math.round(topic.hours_estimated * 60)} min
                      </span>
                    ) : null}
                    <StatusBadge status={(topic.locked ? "locked" : topic.status || "not_started") as "locked"} />
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </Page>
  );
}
