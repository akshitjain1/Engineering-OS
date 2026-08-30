"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Clock, Search } from "lucide-react";
import { StatusBadge } from "@/components/status-badge";
import { Banner, EmptyState, LoadingLine, Page, PageTitle } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import type { CurriculumTree } from "@/lib/curriculum";

type Snapshot = { focus?: { current: { topic_id: number; name: string; domain?: string; module_name?: string | null; status?: string; hours_estimated?: number } | null; upcoming: { topic_id: number; name: string; status?: string; locked?: boolean; hours_estimated?: number }[] } };

export default function LearnPage() {
  const [data, setData] = useState<Snapshot | null>(null);
  const [tree, setTree] = useState<CurriculumTree | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    api<Snapshot>("/api/dashboard").then((s) => setData(s)).catch((err) => setError(errorMessage(err)));
    api<CurriculumTree>("/api/curriculum/tree").then(setTree).catch(() => {});
  }, []);

  const all = tree?.tracks.flatMap((t) => t.levels.flatMap((l) => l.subjects.flatMap((s) => s.modules.flatMap((m) => m.topics)))) ?? [];
  const filtered = all.filter((t) => {
    if (q && !t.name.toLowerCase().includes(q.toLowerCase())) return false;
    if (filter === "completed" && t.status !== "completed") return false;
    if (filter === "locked" && !t.locked) return false;
    if (filter === "available" && (t.locked || t.status === "completed")) return false;
    return true;
  }).slice(0, 100);

  const current = data?.focus?.current;

  return (
    <Page wide>
      <PageTitle kicker="Learn" title="Topics" description="Dense catalog of all topics. Preview locked topics, continue the current one." />
      {error ? <Banner>{error}</Banner> : null}
      {!data && !error ? <LoadingLine /> : null}

      {current ? (
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3 border border-[var(--border)] bg-[var(--card)] px-4 py-3">
          <div><p className="text-xs uppercase tracking-widest text-[var(--muted)]">Current</p><p className="font-semibold">{current.name} <span className="text-xs font-normal text-[var(--muted)]">· {(current.domain || "").toUpperCase()} · ~{current.hours_estimated ? Math.round(current.hours_estimated*60) : 30} min</span></p></div>
          <Link href={`/learn/topic/${current.topic_id}`} className="inline-flex items-center gap-2 rounded-md bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[var(--accent-fg)]">Continue <ArrowRight className="h-4 w-4" /></Link>
        </div>
      ) : null}

      <div className="mb-4 flex flex-wrap gap-2">
        <div className="relative flex-1 min-w-[200px]"><Search className="absolute left-2.5 top-2.5 h-4 w-4 text-[var(--muted)]" /><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search topics…" className="w-full rounded-md border border-[var(--border)] bg-[var(--card)] py-2 pl-8 pr-3 text-sm" /></div>
        <select value={filter} onChange={(e) => setFilter(e.target.value)} className="rounded-md border border-[var(--border)] bg-[var(--card)] px-3 py-2 text-sm">
          <option value="all">All status</option><option value="available">Available</option><option value="completed">Completed</option><option value="locked">Locked</option>
        </select>
      </div>

      {filtered.length ? (
        <div className="overflow-x-auto border border-[var(--border)] bg-[var(--card)]">
          <table className="w-full text-sm">
            <thead className="bg-[var(--card-2)] text-xs uppercase tracking-widest text-[var(--muted)]"><tr><th className="px-3 py-2 text-left">Status</th><th className="px-3 py-2 text-left">Topic</th><th className="px-3 py-2 text-left hidden sm:table-cell">Domain</th><th className="px-3 py-2 text-left">Time</th><th className="px-3 py-2 text-left">Action</th></tr></thead>
            <tbody className="divide-y divide-[var(--border)]">
              {filtered.map((t) => (
                <tr key={t.id} className="hover:bg-[var(--card-2)]">
                  <td className="px-3 py-2"><StatusBadge status={t.locked ? "locked" : t.status} /></td>
                  <td className="px-3 py-2 font-medium">{t.name} <span className="block text-xs font-normal text-[var(--muted)] truncate max-w-[28ch]">{t.learning_objective ?? ""}</span></td>
                  <td className="px-3 py-2 hidden sm:table-cell text-[var(--muted)]">{(t.domain || t.slug || "").slice(0, 12)}</td>
                  <td className="px-3 py-2 text-xs"><span className="inline-flex items-center gap-1"><Clock className="h-3 w-3" />~{t.hours_estimated ? Math.round(t.hours_estimated*60) : 30}m</span></td>
                  <td className="px-3 py-2"><Link href={`/learn/topic/${t.id}`} className="text-xs font-medium text-[var(--accent)] hover:underline">{t.locked ? "Preview" : t.status === "completed" ? "Review" : "Continue"}</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : <EmptyState title="No topics match" body="Adjust search or filter." />}
    </Page>
  );
}
