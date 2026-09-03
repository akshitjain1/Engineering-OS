"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import { cn } from "@/lib/utils";

type RevisionItem = { id: number; item_id: number; item_type: string; title?: string; topic_slug?: string | null; confidence: number; next_review: string | null; review_interval: number; retrieval_success_count?: number; retrieval_fail_count?: number; ease?: number };

const GRADES = [
  { label: "Hard", confidence: 25, hint: "Couldn't recall" },
  { label: "OK", confidence: 60, hint: "Recalled with effort" },
  { label: "Easy", confidence: 95, hint: "Instant recall" },
] as const;

export default function RevisionPage() {
  const [items, setItems] = useState<RevisionItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const load = () => api<RevisionItem[]>("/api/revision/pending").then((d) => { setItems(d); setError(null); }).catch((err) => setError(errorMessage(err)));
  useEffect(() => { load(); }, []);
  async function review(item: RevisionItem, confidence: number) {
    setBusyId(item.id);
    try { await api(`/api/revision/schedule?item_id=${item.item_id}&item_type=${item.item_type}&confidence=${confidence}`, { method: "POST" }); await load(); }
    catch (err) { setError(errorMessage(err)); } finally { setBusyId(null); }
  }
  return (
    <Page wide>
      <PageTitle kicker="Revision" title="Review queue" description="Retrieve from memory first — then grade honestly. Hard shortens interval, easy lengthens it." />
      {error ? <Banner>{error}</Banner> : null}
      {items === null && !error ? <LoadingLine /> : null}
      <div className="mb-4 flex items-center justify-between"><h2 className="text-sm font-semibold">{items ? `${items.length} due today` : "Due now"}</h2><span className="text-xs text-[var(--muted)]">Active recall</span></div>
      {items && items.length === 0 ? <EmptyState title="Nothing is due" body='Open any topic and use "Add to review" when you want to revisit later.' /> : (
        <ul className="divide-y divide-[var(--border)] border-y border-[var(--border)] bg-[var(--card)]">
          {(items || []).map((item) => (
            <li key={item.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-4">
              <div className="min-w-0 flex-1"><p className="font-medium">{item.title || `${item.item_type} #${item.item_id}`}</p><p className="mt-1 text-sm text-[var(--muted)]">Explain <em>{item.title || "this topic"}</em> without notes — mechanism, example, misconception.</p><p className="mt-1 text-xs text-[var(--muted)]">{item.review_interval}d interval {typeof item.ease === "number" ? `· ease ${item.ease.toFixed(1)}` : ""} {item.retrieval_fail_count ? `· ${item.retrieval_fail_count} misses` : ""}</p></div>
              <div className="flex flex-wrap gap-2">
                {/* Says what it does. It read "Open source" and went to the topic page,
                    not to any source -- and as a plain <a> to an internal route it
                    reloaded the whole app instead of navigating. */}
                {item.item_type === "topic" ? <Link href={`/learn/topic/${item.item_id}`} className="rounded-md border border-[var(--border)] px-3 py-1.5 text-xs">Open topic</Link> : null}
                {GRADES.map((g) => <button key={g.label} type="button" title={g.hint} disabled={busyId === item.id} onClick={() => review(item, g.confidence)} className={cn("rounded-md border px-3 py-1.5 text-xs font-medium hover:border-[var(--border-strong)]", busyId === item.id && "opacity-50")}>{g.label}</button>)}
              </div>
            </li>
          ))}
        </ul>
      )}
    </Page>
  );
}
