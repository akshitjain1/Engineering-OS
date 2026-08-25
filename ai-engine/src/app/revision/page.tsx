"use client";

import { useEffect, useState } from "react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle, PrimaryButton } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import { cn } from "@/lib/utils";

type RevisionItem = {
  id: number;
  item_id: number;
  item_type: string;
  title?: string;
  topic_slug?: string | null;
  confidence: number;
  next_review: string | null;
  review_interval: number;
  retrieval_success_count?: number;
  retrieval_fail_count?: number;
  ease?: number;
};

// Active-recall grading feeds the adaptive scheduler (PART I):
// hard resets the interval, easy grows it via the ease multiplier.
const GRADES = [
  { label: "Hard", confidence: 25, hint: "Couldn't recall without notes" },
  { label: "OK", confidence: 60, hint: "Recalled with effort" },
  { label: "Easy", confidence: 95, hint: "Instant, confident recall" },
] as const;

export default function RevisionPage() {
  const [items, setItems] = useState<RevisionItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

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

  async function review(item: RevisionItem, confidence: number) {
    setBusyId(item.id);
    try {
      const query = new URLSearchParams({
        item_id: String(item.item_id),
        item_type: item.item_type,
        confidence: String(confidence),
      });
      await api(`/api/revision/schedule?${query.toString()}`, { method: "POST" });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <Page>
      <PageTitle
        kicker="Revision"
        title="Active recall queue"
        description="Retrieve from memory first — then grade honestly. Hard answers shorten the interval; easy ones lengthen it."
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
                <p className="mt-1 text-sm text-[var(--muted)]">
                  Recall prompt: explain <em>{item.title || "this topic"}</em> without notes — draw the mechanism,
                  give one concrete example, and state one common misconception.
                </p>
                {typeof item.ease === "number" ? (
                  <p className="mt-1 text-xs text-[var(--muted)]">
                    Interval {item.review_interval}d · ease {item.ease.toFixed(1)}
                    {item.retrieval_fail_count ? ` · ${item.retrieval_fail_count} misses` : ""}
                  </p>
                ) : null}
                <div className="mt-3 flex flex-wrap gap-2">
                  {item.item_type === "topic" ? (
                    <PrimaryButton href={`/learn/topic/${item.item_id}`}>Open source</PrimaryButton>
                  ) : null}
                  {GRADES.map((grade) => (
                    <button
                      key={grade.label}
                      type="button"
                      title={grade.hint}
                      disabled={busyId === item.id}
                      onClick={() => review(item, grade.confidence)}
                      className={cn(
                        "rounded-md border border-[var(--border)] px-3 py-1.5 text-xs font-medium",
                        busyId === item.id && "opacity-50",
                      )}
                    >
                      {grade.label}
                    </button>
                  ))}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </Page>
  );
}
