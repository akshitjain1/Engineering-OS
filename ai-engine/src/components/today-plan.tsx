"use client";

import Link from "next/link";
import { useState } from "react";
import { Circle, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

export type PlanItem = {
  type: string;
  activity_type?: string;
  title: string;
  topic_title?: string | null;
  minutes: number;
  why: string;
  reason?: string | null;
  topic_id?: number | null;
  topic_slug?: string | null;
  domain?: string | null;
  group?: string | null;
  provider?: string | null;
  resource_title?: string | null;
  resource_type?: string | null;
  resource_url?: string | null;
  section?: string | null;
  lecture?: string | null;
  video_id?: string | null;
  verification_status?: string | null;
  resource_status?: string | null;
  is_playlist?: boolean;
  exact?: boolean;
  embeddable?: boolean;
};

export type DailyPlan = {
  budget_minutes: number;
  total_minutes: number;
  goal?: string;
  mode?: string;
  items: PlanItem[];
  groups?: { core?: PlanItem[]; parallel?: PlanItem[]; practice?: PlanItem[]; build?: PlanItem[] };
  plan_date?: string;
};

const GROUP_META: { key: keyof NonNullable<DailyPlan["groups"]>; label: string }[] = [
  { key: "core", label: "Core" },
  { key: "parallel", label: "Parallel" },
  { key: "practice", label: "Practice" },
  { key: "build", label: "Build" },
];

export const TodayPlan = ({ plan, onGenerate, busy }: { plan: DailyPlan | null; onGenerate: (minutes?: number) => void; busy?: boolean }) => {
  const groups = plan?.groups;
  const hasGroups = Boolean(groups && GROUP_META.some(({ key }) => (groups[key]?.length ?? 0) > 0));
  return (
    <div>
      {plan ? <p className="mb-3 text-xs text-[var(--muted)]">{plan.total_minutes} / {plan.budget_minutes} min {plan.mode ? `· ${plan.mode}` : ""}</p> : <p className="text-sm text-[var(--muted)]">No plan scheduled yet.</p>}
      {hasGroups ? (
        <div className="space-y-6">
          {GROUP_META.map(({ key, label }) => {
            const items = groups?.[key] ?? [];
            if (!items.length) return null;
            return (
              <section key={key}>
                <h3 className="text-xs font-semibold uppercase tracking-widest text-[var(--accent)]">{label} · {items.reduce((s, i) => s + (i.minutes || 0), 0)}m</h3>
                <ol className="mt-2 divide-y divide-[var(--border)] border-y border-[var(--border)]">
                  {items.map((item, idx) => <PlanRow key={`${key}-${idx}`} item={item} time={`${String(9 + idx).padStart(2, "0")}:00`} />)}
                </ol>
              </section>
            );
          })}
        </div>
      ) : (
        <ol className="divide-y divide-[var(--border)] border-y border-[var(--border)]">
          {(plan?.items ?? []).map((item, idx) => <PlanRow key={idx} item={item} time={`${String(9 + idx).padStart(2, "0")}:00`} />)}
        </ol>
      )}
      <div className="mt-4 flex flex-wrap gap-2">
        <button type="button" className="rounded-md bg-[var(--accent)] px-3 py-1.5 text-xs font-medium text-[var(--accent-fg)] disabled:opacity-50" disabled={busy} onClick={() => onGenerate()}>Use capacity</button>
        {[30, 60, 90, 120, 180].map((m) => <button key={m} type="button" className="rounded-md border border-[var(--border)] px-2.5 py-1.5 text-xs hover:border-[var(--border-strong)] disabled:opacity-50" disabled={busy} onClick={() => onGenerate(m)}>{m}m</button>)}
      </div>
    </div>
  );
};

function PlanRow({ item, time }: { item: PlanItem; time: string }) {
  const [done, setDone] = useState(false);
  const type = (item.activity_type || item.type || "").toUpperCase();
  const color = type === "LEARN" ? "text-[var(--accent)]" : type === "PRACTICE" ? "text-[var(--ok)]" : type === "BUILD" ? "text-[var(--warn)]" : "text-[var(--muted)]";
  return (
    <li className="flex gap-3 py-3">
      <span className="w-12 shrink-0 text-xs font-mono text-[var(--muted)]">{time}</span>
      <button type="button" aria-label={done ? "Mark not done" : "Mark done"} onClick={() => setDone((v) => !v)} className={cn("mt-0.5 shrink-0", done ? "text-[var(--ok)]" : "text-[var(--muted)] hover:text-[var(--foreground)]")}>
        {done ? <CheckCircle2 className="h-4 w-4" /> : <Circle className="h-4 w-4" />}
      </button>
      <div className={cn("min-w-0 flex-1", done && "opacity-60")}>
        <div className="flex flex-wrap items-center gap-2">
          <span className={cn("text-xs font-semibold tracking-widest", color)}>{type}</span>
          <span className="text-xs text-[var(--muted)]">{item.minutes}m</span>
          <span className="text-xs text-[var(--muted)]">· {item.topic_title || item.title}</span>
        </div>
        <p className="text-sm font-medium">{item.topic_title || item.title}</p>
        <p className="text-xs text-[var(--muted)]">{item.reason || item.why}</p>
        {item.resource_url ? <a href={item.resource_url} target="_blank" rel="noreferrer" className="text-xs font-medium text-[var(--accent)] hover:underline">{item.embeddable ? "Watch" : "Open"} source →</a> : null}
        {item.topic_id ? <Link href={`/learn/topic/${item.topic_id}`} className="ml-2 text-xs underline">Open topic</Link> : null}
      </div>
    </li>
  );
}
