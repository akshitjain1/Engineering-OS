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
  groups?: {
    core?: PlanItem[];
    parallel?: PlanItem[];
    practice?: PlanItem[];
    build?: PlanItem[];
  };
  plan_date?: string;
};

const GROUP_META: { key: keyof NonNullable<DailyPlan["groups"]>; label: string }[] = [
  { key: "core", label: "CORE" },
  { key: "parallel", label: "PARALLEL" },
  { key: "practice", label: "PRACTICE" },
  { key: "build", label: "BUILD" },
];

function SourceAction({ item }: { item: PlanItem }) {
  const activity = item.activity_type || item.type;
  if (!["LEARN", "REFERENCE", "PRACTICE", "ALWAYS_ON"].includes(activity)) {
    return null;
  }
  if (item.resource_status === "BROKEN" || item.resource_status === "UNRESOLVED" || !item.resource_url) {
    if (!item.resource_url) {
      return <p className="mt-1 text-xs text-[var(--warn)]">Exact source unresolved — no URL invented.</p>;
    }
  }
  if (!item.resource_url) return null;
  const label = item.embeddable ? "Watch lecture" : item.is_playlist ? "Open playlist" : "Open source";
  return (
    <div className="mt-1">
      <p className="text-xs text-[var(--muted)]">
        {item.provider ? `${item.provider} — ` : ""}
        {item.resource_title || "Mapped source"}
        {item.lecture ? ` · ${item.lecture}` : ""}
      </p>
      <a href={item.resource_url} target="_blank" rel="noreferrer" className="text-xs underline hover:text-[var(--foreground)]">
        {label}
      </a>
    </div>
  );
}

export const TodayPlan = ({
  plan,
  onGenerate,
  busy,
}: {
  plan: DailyPlan | null;
  onGenerate: (minutes?: number) => void;
  busy?: boolean;
}) => {
  const groups = plan?.groups;
  const hasGroups = Boolean(
    groups && GROUP_META.some(({ key }) => (groups[key]?.length ?? 0) > 0),
  );

  return (
    <div className="glow-card p-5">
      <h2 className="text-sm font-semibold">Today’s blocks</h2>
      {plan ? (
        <p className="mb-3 text-xs text-[var(--muted)]">
          {plan.total_minutes} / {plan.budget_minutes} minutes
          {plan.mode ? ` · ${plan.mode}` : ""}
        </p>
      ) : (
        <p className="text-sm text-[var(--muted)]">No plan scheduled yet.</p>
      )}

      {hasGroups ? (
        <div className="space-y-5">
          {GROUP_META.map(({ key, label }) => {
            const items = groups?.[key] ?? [];
            if (!items.length) return null;
            const mins = items.reduce((sum, item) => sum + (item.minutes || 0), 0);
            return (
              <section key={key}>
                <div className="mb-2 flex items-baseline justify-between">
                  <h3 className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">{label}</h3>
                  <span className="text-xs text-[var(--muted)]">{mins}m</span>
                </div>
                <ol className="space-y-3 text-sm">
                  {items.map((item, index) => (
                    <PlanRow key={`${key}-${item.type}-${item.topic_slug ?? index}`} item={item} />
                  ))}
                </ol>
              </section>
            );
          })}
        </div>
      ) : (
        <ol className="space-y-4 text-sm">
          {(plan?.items ?? []).map((item, index) => (
            <PlanRow key={`${item.type}-${item.topic_slug ?? index}`} item={item} />
          ))}
        </ol>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        <button
          type="button"
          className="rounded-md bg-[var(--accent)] px-2.5 py-1 text-xs font-medium text-[var(--accent-fg)] disabled:opacity-50"
          disabled={busy}
          onClick={() => onGenerate()}
        >
          Use capacity
        </button>
        {[30, 60, 90, 120, 180].map((minutes) => (
          <button
            key={minutes}
            type="button"
            className="rounded-md border border-[var(--border)] px-2 py-1 text-xs transition-colors hover:border-[var(--accent)] hover:text-[var(--foreground)] disabled:opacity-50"
            disabled={busy}
            onClick={() => onGenerate(minutes)}
          >
            {minutes}m
          </button>
        ))}
      </div>
    </div>
  );
};

function PlanRow({ item }: { item: PlanItem }) {
  const [done, setDone] = useState(false);
  return (
    <li className="flex gap-3">
      <button
        type="button"
        aria-label={done ? "Mark not done" : "Mark done"}
        onClick={() => setDone((value) => !value)}
        className={cn("mt-0.5 shrink-0", done ? "text-[var(--ok)]" : "text-[var(--muted)] hover:text-[var(--foreground)]")}
      >
        {done ? <CheckCircle2 className="h-[18px] w-[18px]" /> : <Circle className="h-[18px] w-[18px]" />}
      </button>
      <div className={cn("min-w-0 border-l border-[var(--border)] pl-3", done && "opacity-60")}>
        <div className="flex flex-wrap items-center gap-x-2">
          <span className="text-xs font-medium uppercase tracking-[0.1em] text-[var(--accent)]">
            {item.activity_type || item.type}
          </span>
          <span className="text-xs text-[var(--muted)]">{item.minutes}m</span>
        </div>
        <div className={cn("font-medium", done && "line-through decoration-[var(--muted)]")}>
          {item.topic_title || item.title}
        </div>
        <p className="text-xs text-[var(--muted)]">{item.reason || item.why}</p>
        <SourceAction item={item} />
        {item.topic_id ? (
          <Link className="text-xs underline hover:text-[var(--foreground)]" href={`/learn/topic/${item.topic_id}`}>
            Open topic
          </Link>
        ) : null}
      </div>
    </li>
  );
}
