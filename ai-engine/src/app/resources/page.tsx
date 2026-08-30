"use client";

import { useEffect, useState } from "react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import type { CurriculumTree } from "@/lib/curriculum";
import Link from "next/link";

export default function ResourcesPage() {
  const [tree, setTree] = useState<CurriculumTree | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  useEffect(() => { api<CurriculumTree>("/api/curriculum/tree").then(setTree).catch((err) => setError(errorMessage(err))); }, []);
  const resources = tree?.tracks.flatMap((t) => t.levels.flatMap((l) => l.subjects.flatMap((s) => s.modules.flatMap((m) => m.topics.flatMap((topic) => (topic.resources_by_role?.PRIMARY ?? []).map((r) => ({ ...r, topicName: topic.name, topicId: topic.id }))))))) ?? [];
  const filtered = resources.filter((r) => !q || r.title.toLowerCase().includes(q.toLowerCase()) || (r.provider ?? "").toLowerCase().includes(q.toLowerCase())).slice(0, 100);
  return (
    <Page wide>
      <PageTitle kicker="Resources" title="Resource library" description="All PRIMARY sources indexed by topic. Search by title or provider." />
      {error ? <Banner>{error}</Banner> : null}
      {!tree ? <LoadingLine /> : (
        <>
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search resources…" className="mb-4 w-full max-w-md rounded-md border border-[var(--border)] bg-[var(--card)] px-3 py-2 text-sm" />
          {filtered.length ? (
            <div className="overflow-x-auto border border-[var(--border)] bg-[var(--card)]">
              <table className="w-full text-sm">
                <thead className="bg-[var(--card-2)] text-xs uppercase tracking-widest text-[var(--muted)]"><tr><th className="px-3 py-2 text-left">Resource</th><th className="px-3 py-2 text-left">Topic</th><th className="px-3 py-2 text-left">Provider</th><th className="px-3 py-2 text-left">Type</th><th className="px-3 py-2 text-left">Open</th></tr></thead>
                <tbody className="divide-y divide-[var(--border)]">
                  {filtered.map((r) => (
                    <tr key={`${r.id}-${r.topicId}`} className="hover:bg-[var(--card-2)]">
                      <td className="px-3 py-2 font-medium">{r.title}</td>
                      <td className="px-3 py-2"><Link href={`/learn/topic/${r.topicId}`} className="text-[var(--accent)] hover:underline">{r.topicName}</Link></td>
                      <td className="px-3 py-2 text-[var(--muted)]">{r.provider ?? "—"}</td>
                      <td className="px-3 py-2 text-xs">{r.resource_type}</td>
                      <td className="px-3 py-2">{r.url ? <a href={r.url} target="_blank" rel="noreferrer" className="text-xs font-medium text-[var(--accent)] hover:underline">Open</a> : <span className="text-xs text-[var(--muted)]">—</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <EmptyState title="No resources found" body="Adjust search or open topics directly." />}
        </>
      )}
    </Page>
  );
}
