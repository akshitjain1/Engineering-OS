"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Layers } from "lucide-react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import type { CurriculumTree } from "@/lib/curriculum";

export default function ProgressPage() {
  const [tree, setTree] = useState<CurriculumTree | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<CurriculumTree>("/api/roadmap")
      .then((data) => {
        setTree(data);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)));
  }, []);

  if (!tree && !error) {
    return (
      <Page>
        <LoadingLine label="Loading progress…" />
      </Page>
    );
  }

  const all = tree?.tracks.flatMap((track) =>
    track.levels.flatMap((level) =>
      level.subjects.flatMap((subject) => subject.modules.flatMap((module) => module.topics)),
    ),
  ) ?? [];
  const completed = all.filter((topic) => topic.status === "completed").length;
  const inProgress = all.filter((topic) => topic.status === "in_progress").length;
  const total = all.length;

  const byDomain = {
    Foundations: all.filter((topic) => (topic.slug || "").startsWith("cf-")),
    Java: all.filter((topic) => (topic.slug || "").startsWith("java-")),
    DSA: all.filter((topic) => (topic.slug || "").startsWith("dsa-")),
  };

  return (
    <Page>
      <PageTitle
        kicker="Progress"
        title="Completion"
        description="How much of the 222-topic sequence is done. No mastery scores — a topic is either completed or it is not."
      />
      {error ? <Banner>{error}</Banner> : null}

      <section className="glow-card p-5">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.14em] text-[var(--muted)]">Topics completed</p>
            <p className="mt-1 text-4xl font-semibold tabular-nums">
              {completed}
              <span className="text-lg font-normal text-[var(--muted)]"> / {total}</span>
            </p>
          </div>
          {inProgress > 0 ? (
            <p className="text-sm text-[var(--muted)]">{inProgress} in progress now</p>
          ) : null}
        </div>
        <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-[var(--border)]">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-2)]"
            style={{ width: `${total ? Math.round((completed / total) * 100) : 0}%` }}
          />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">Continue</h2>
        {tree?.next ? (
          <Link
            href={`/learn/topic/${tree.next.topic_id}`}
            className="glow-card mt-3 flex items-center justify-between gap-3 px-4 py-3"
          >
            <div>
              <p className="font-medium">{tree.next.topic_name}</p>
              <p className="mt-0.5 text-xs text-[var(--muted)]">
                {tree.next.module_name} · {tree.next.track_name}
              </p>
            </div>
            <span className="text-sm font-medium text-[var(--accent)]">Open →</span>
          </Link>
        ) : (
          <p className="mt-3 text-sm text-[var(--muted)]">All unlocked topics are complete.</p>
        )}
      </section>

      <section className="mt-8">
        <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">
          <Layers className="h-4 w-4" /> By domain
        </h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          {Object.entries(byDomain).map(([name, list]) => {
            const done = list.filter((topic) => topic.status === "completed").length;
            const pct = list.length ? Math.round((done / list.length) * 100) : 0;
            return (
              <div key={name} className="glow-card p-4">
                <p className="text-sm font-medium">{name}</p>
                <p className="mt-1 text-2xl font-semibold tabular-nums">
                  {done}
                  <span className="text-xs font-normal text-[var(--muted)]"> / {list.length}</span>
                </p>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-[var(--border)]">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-2)]"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {total === 0 ? (
        <div className="mt-8">
          <EmptyState title="No curriculum loaded" body="Import the official curriculum on the backend, then refresh." />
        </div>
      ) : null}
    </Page>
  );
}