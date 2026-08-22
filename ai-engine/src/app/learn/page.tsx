"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Clock } from "lucide-react";
import { StatusBadge } from "@/components/status-badge";
import { Banner, EmptyState, LoadingLine, Page } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";

type FocusTopic = {
  topic_id: number;
  name: string;
  domain?: string;
  module_name?: string | null;
  locked?: boolean;
  status?: string;
  hours_estimated?: number;
  why?: string | null;
};

type Snapshot = {
  focus?: { current: FocusTopic | null; upcoming: FocusTopic[] };
};

export default function LearnPage() {
  const [data, setData] = useState<Snapshot | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Snapshot>("/api/dashboard")
      .then((snapshot) => {
        setData(snapshot);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)));
  }, []);

  const current = data?.focus?.current;
  const upcoming = data?.focus?.upcoming ?? [];

  return (
    <Page>
      <header className="mb-8">
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-[var(--muted)]">Learn</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight">Continue the sequence</h1>
        <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">
          The official curriculum in order. Complete a topic to unlock the next one.
        </p>
      </header>
      {error ? <Banner>{error}</Banner> : null}
      {!data && !error ? <LoadingLine /> : null}

      {current ? (
        <section className="glow-card overflow-hidden">
          <div className="h-1 w-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-2)]" />
          <div className="p-5">
            <p className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">Current</p>
            <h2 className="mt-1.5 text-xl font-semibold tracking-tight">{current.name}</h2>
            <p className="mt-1 text-sm text-[var(--muted)]">
              {(current.domain || "").toUpperCase()}
              {current.module_name ? ` · ${current.module_name}` : ""}
              {current.hours_estimated ? ` · ~${Math.round(current.hours_estimated * 60)} min` : ""}
            </p>
            <div className="mt-3">
              <StatusBadge status={(current.status || "in_progress") as "in_progress"} />
            </div>
            {current.why ? <p className="mt-3 max-w-prose text-sm leading-relaxed">{current.why}</p> : null}
            <div className="mt-4">
              <Link
                href={`/learn/topic/${current.topic_id}`}
                className="inline-flex items-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2.5 text-sm font-medium text-[var(--accent-fg)] transition-opacity hover:opacity-90"
              >
                Open topic <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>
      ) : data ? (
        <EmptyState title="Nothing is queued" body="Open the roadmap if the official curriculum is complete or still locked." />
      ) : null}

      <section className="mt-10">
        <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">Up next</h2>
        {upcoming.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--muted)]">No further official topics after the current one.</p>
        ) : (
          <ul className="mt-3 space-y-2">
            {upcoming.map((topic) => (
              <li key={topic.topic_id}>
                <Link
                  href={topic.locked ? "#" : `/learn/topic/${topic.topic_id}`}
                  className="glow-card group flex items-center justify-between gap-3 px-4 py-3 transition-colors hover:border-[var(--accent)]"
                >
                  <div>
                    <p className="font-medium">{topic.name}</p>
                    <div className="mt-1.5 flex flex-wrap items-center gap-2">
                      <StatusBadge status={(topic.locked ? "locked" : topic.status || "not_started") as "locked"} />
                      {topic.hours_estimated ? (
                        <span className="inline-flex items-center gap-1 text-xs text-[var(--muted)]">
                          <Clock className="h-3 w-3" /> ~{Math.round(topic.hours_estimated * 60)} min
                        </span>
                      ) : null}
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 shrink-0 text-[var(--muted)] transition-colors group-hover:text-[var(--accent)]" />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </Page>
  );
}