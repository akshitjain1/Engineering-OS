"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Banner, LoadingLine, Page, PageTitle, ProgressBar } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import { getCompletedTopicCount, getDomainProgress } from "@/lib/analytics";
import type { CurriculumTree } from "@/lib/curriculum";

export default function ProgressPage() {
  const [tree, setTree] = useState<CurriculumTree | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { api<CurriculumTree>("/api/roadmap").then(setTree).catch((err) => setError(errorMessage(err))); }, []);
  if (!tree && !error) return <Page wide><LoadingLine label="Loading progress…" /></Page>;
  const { completed, total } = getCompletedTopicCount(tree);
  const domains = getDomainProgress(tree).filter((d) => d.total > 0);
  return (
    <Page wide>
      <PageTitle kicker="Progress" title="Completion analytics" description="Topics completed counts learnable topics only. No fabricated mastery scores." />
      {error ? <Banner>{error}</Banner> : null}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-[10px] border border-[var(--border)] bg-[var(--card)] p-6 shadow-[0_4px_12px_rgba(15,23,42,0.06)] lg:col-span-2">
          <p className="text-xs uppercase tracking-widest text-[var(--muted)]">Topics completed</p>
          <p className="mt-1 text-4xl font-bold tabular-nums">{completed}<span className="text-lg font-normal text-[var(--muted)]"> / {total}</span></p>
          <p className="text-xs text-[var(--muted)]">learnable topics · {total ? Math.round((completed/total)*100) : 0}%</p>
          <div className="mt-4"><ProgressBar value={completed} max={total} /></div>
          <dl className="mt-4 grid grid-cols-3 gap-3 text-sm">
            <div><dt className="text-xs uppercase tracking-widest text-[var(--muted)]">Current track</dt><dd className="font-medium">{tree?.next?.track_name ?? "—"}</dd></div>
            <div><dt className="text-xs uppercase tracking-widest text-[var(--muted)]">Current module</dt><dd className="font-medium">{tree?.next?.module_name ?? "—"}</dd></div>
            <div><dt className="text-xs uppercase tracking-widest text-[var(--muted)]">Next topic</dt><dd className="font-medium">{tree?.next?.topic_name ?? "—"}</dd></div>
          </dl>
          {tree?.next ? <Link href={`/learn/topic/${tree.next.topic_id}`} className="mt-4 inline-flex text-sm font-medium text-[var(--accent)] hover:underline">Continue → {tree.next.topic_name}</Link> : null}
        </div>
        <div className="space-y-4">
          <div className="rounded-[10px] border border-[var(--border)] bg-[var(--card)] p-5 shadow-sm"><p className="text-xs uppercase tracking-widest text-[var(--muted)]">Focus vs planned</p><p className="mt-2 text-sm text-[var(--muted)]">Weekly study shows <em>planned</em> vs capacity, not completed. Completed is topics above.</p><p className="mt-2 text-xs text-[var(--muted)]">Study minutes are derived from completed topics × hours_estimated when available.</p></div>
        </div>
      </div>
      <section className="mt-8">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-[var(--muted)]">By domain — completed / total</h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {domains.map((d) => (
            <div key={d.key} className="rounded-[10px] border border-[var(--border)] bg-[var(--card)] p-4 shadow-sm"><p className="text-sm font-medium">{d.label}</p><p className="mt-1 text-lg font-bold tabular-nums">{d.completed} <span className="text-xs font-normal text-[var(--muted)]">/ {d.total} · {d.percent}%</span></p><div className="mt-2 h-[6px] overflow-hidden rounded-full bg-[var(--border)]"><div className="h-full bg-[var(--accent)]" style={{ width: `${d.percent}%` }} /></div></div>
          ))}
        </div>
      </section>
    </Page>
  );
}
