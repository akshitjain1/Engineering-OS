"use client";

import { useEffect, useState } from "react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle, PrimaryButton } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";

type RevisionItem = {
  id: number;
  item_id: number;
  item_type: string;
  title?: string;
  topic_slug?: string | null;
  confidence: number;
  next_review: string | null;
  review_interval: number;
};

export default function RevisionPage() {
  const [items, setItems] = useState<RevisionItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () =>
    api<RevisionItem[]>("/api/revision/pending")
      .then((data) => {
        setItems(data);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)));

  useEffect(() => {
    load();
  }, []);

  async function review(item: RevisionItem) {
    try {
      const query = new URLSearchParams({
        item_id: String(item.item_id),
        item_type: item.item_type,
        confidence: "50",
      });
      await api(`/api/revision/schedule?${query.toString()}`, { method: "POST" });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <Page>
      <PageTitle
        kicker="Revision"
        title="Review queue"
        description="Topics you added from a topic page. Open the source and rework it — then mark it reviewed when done."
      />
      {error ? <Banner>{error}</Banner> : null}
      {items === null && !error ? <LoadingLine /> : null}

      <section className="mt-8">
        <h2 className="text-sm font-semibold">Due now</h2>
        {items && items.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="Nothing is due"
              body='Open any topic and use "Add to review" when you want to revisit it later.'
            />
          </div>
        ) : (
          <ul className="mt-3 space-y-3">
            {(items || []).map((item) => (
              <li key={item.id} className="rounded-xl border border-[var(--border)] bg-[var(--card)] px-4 py-3">
                <p className="font-medium">{item.title || `${item.item_type} #${item.item_id}`}</p>
                <p className="mt-1 text-xs text-[var(--muted)]">
                  Added to your review queue. Next due: {item.next_review ? new Date(item.next_review).toLocaleDateString() : "—"}.
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {item.item_type === "topic" ? (
                    <PrimaryButton href={`/learn/topic/${item.item_id}`}>Start revision</PrimaryButton>
                  ) : null}
                  <button type="button" className="text-sm underline" onClick={() => review(item)}>
                    Mark reviewed
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </Page>
  );
}