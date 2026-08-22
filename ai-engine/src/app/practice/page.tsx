"use client";

import { useEffect, useState } from "react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle, PrimaryButton } from "@/components/study-ui";
import { SourceResourceCard } from "@/components/source-resource";
import { api, errorMessage } from "@/lib/api";
import type { ResourcePublic, TopicNode } from "@/lib/curriculum";
import type { DailyPlan } from "@/components/today-plan";

type Snapshot = {
  today_plan: DailyPlan | null;
  focus?: { current: { topic_id: number; name: string } | null };
};

export default function PracticePage() {
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [topic, setTopic] = useState<TopicNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<Snapshot>("/api/dashboard")
      .then(async (data) => {
        setPlan(data.today_plan);
        const id = data.focus?.current?.topic_id;
        if (id) {
          const detail = await api<TopicNode>(`/api/topic/${id}`);
          setTopic(detail);
        }
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const recommended = plan?.items.filter((item) => item.type === "PRACTICE") ?? [];
  const resources: ResourcePublic[] = topic?.resources_by_role?.PRACTICE ?? [];

  return (
    <Page>
      <PageTitle
        kicker="Practice"
        title="Recommended work"
        description="Practice is tied to today’s plan and the current official topic. Exact NeetCode problem URLs are only shown when stored; collections stay labeled unresolved for the specific problem."
      />
      {error ? <Banner>{error}</Banner> : null}
      {loading ? <LoadingLine /> : null}

      <section>
        <h2 className="text-sm font-semibold">Current recommended practice</h2>
        {topic ? <p className="mt-1 text-sm text-[var(--muted)]">Topic: {topic.name}</p> : null}
        {recommended.length === 0 && resources.length === 0 && !loading ? (
          <div className="mt-3">
            <EmptyState
              title="No practice item yet"
              body="Generate a daily plan on Today, or open the current topic after the official curriculum is imported."
            />
          </div>
        ) : null}
        {recommended.map((item, index) => (
          <div key={`${item.topic_slug}-${index}`} className="mt-3 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
            <p className="text-xs uppercase tracking-wide text-[var(--muted)]">{item.minutes} min</p>
            <p className="mt-1 font-medium">{item.topic_title || item.title}</p>
            <p className="mt-1 text-sm text-[var(--muted)]">{item.reason || item.why}</p>
            {item.resource_url ? (
              <p className="mt-2 text-sm">
                {item.provider} — {item.resource_title}
                {item.exact === false ? " (collection; exact problem unresolved)" : ""}
              </p>
            ) : (
              <p className="mt-2 text-sm text-amber-800">Exact practice URL unresolved.</p>
            )}
            <div className="mt-3 flex gap-2">
              {item.resource_url ? (
                <a className="text-sm underline" href={item.resource_url} target="_blank" rel="noreferrer">
                  Open
                </a>
              ) : null}
              {item.topic_id ? <PrimaryButton href={`/learn/topic/${item.topic_id}#practice`}>Open topic</PrimaryButton> : null}
            </div>
          </div>
        ))}
      </section>

      {resources.length > 0 ? (
        <section className="mt-8">
          <h2 className="text-sm font-semibold">Mapped practice sources</h2>
          <div className="mt-3 space-y-3">
            {resources.map((resource) => (
              <SourceResourceCard key={resource.id} resource={resource} />
            ))}
          </div>
        </section>
      ) : null}
    </Page>
  );
}
