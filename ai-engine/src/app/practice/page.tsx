"use client";

import { useEffect, useState } from "react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle, SectionHeader } from "@/components/study-ui";
import { SourceResourceCard } from "@/components/source-resource";
import { api, errorMessage } from "@/lib/api";
import type { ResourcePublic, TopicNode } from "@/lib/curriculum";
import type { DailyPlan } from "@/components/today-plan";

type Snapshot = { today_plan: DailyPlan | null; focus?: { current: { topic_id: number; name: string } | null } };

export default function PracticePage() {
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [topic, setTopic] = useState<TopicNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<Snapshot>("/api/dashboard").then(async (data) => {
      setPlan(data.today_plan);
      const id = data.focus?.current?.topic_id;
      if (id) { const detail = await api<TopicNode>(`/api/topic/${id}`); setTopic(detail); }
      setError(null);
    }).catch((err) => setError(errorMessage(err))).finally(() => setLoading(false));
  }, []);

  const recommended = plan?.items.filter((i) => i.type === "PRACTICE") ?? [];
  const resources: ResourcePublic[] = topic?.resources_by_role?.PRACTICE ?? [];

  return (
    <Page wide>
      <PageTitle kicker="Practice" title="Practice workspace" description="Today's practice, due revision, and mapped sources for the current topic." />
      {error ? <Banner>{error}</Banner> : null}
      {loading ? <LoadingLine /> : null}

      <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
        <section className="border border-[var(--border)] bg-[var(--card)]">
          <div className="border-b border-[var(--border)] px-5 py-3"><SectionHeader title="Today's practice" hint={`${recommended.length} items`} /></div>
          <div className="p-5">
            {topic ? <p className="mb-3 text-sm text-[var(--muted)]">Current topic: <span className="font-medium text-[var(--foreground)]">{topic.name}</span></p> : null}
            {recommended.length === 0 && resources.length === 0 && !loading ? <EmptyState title="No practice item yet" body="Generate a daily plan on Today, or open the current topic." /> : null}
            <ul className="divide-y divide-[var(--border)] border-y border-[var(--border)]">
              {recommended.map((item, idx) => (
                <li key={idx} className="flex items-center justify-between gap-3 py-3">
                  <div><p className="text-sm font-medium">{item.topic_title || item.title}</p><p className="text-xs text-[var(--muted)]">{item.minutes} min · {item.reason || item.why}</p></div>
                  <div className="flex items-center gap-2">{item.resource_url ? <a href={item.resource_url} target="_blank" rel="noreferrer" className="text-xs font-medium text-[var(--accent)] hover:underline">Open</a> : <span className="text-xs text-[var(--warn)]">No URL</span>}{item.topic_id ? <a href={`/learn/topic/${item.topic_id}#practice`} className="rounded-md border border-[var(--border)] px-2 py-1 text-xs">Open topic</a> : null}</div>
                </li>
              ))}
            </ul>
          </div>
        </section>
        <div className="space-y-6">
          <section className="border border-[var(--border)] bg-[var(--card)] p-5">
            <SectionHeader title="Mapped practice sources" hint={`${resources.length} sources`} />
            {resources.length ? <div className="mt-3 space-y-3">{resources.map((r) => <SourceResourceCard key={r.id} resource={r} />)}</div> : <p className="text-sm text-[var(--muted)]">No mapped practice for current topic.</p>}
          </section>
          <section className="border border-[var(--border)] bg-[var(--card-2)] p-4 text-sm text-[var(--muted)]">Recent results and due revision are in Revision. Practice completion is tracked via resource consumed + build tasks.</section>
        </div>
      </div>
    </Page>
  );
}
