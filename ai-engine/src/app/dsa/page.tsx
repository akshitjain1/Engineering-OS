"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, errorMessage } from "@/lib/api";
import { cn } from "@/lib/utils";
import {
  Banner,
  EmptyState,
  LoadingLine,
  Page,
  PageTitle,
  ProgressBar,
} from "@/components/study-ui";

type Practice = { title: string; provider: string | null; url: string };

type BoardTopic = {
  topic_id: number;
  slug: string | null;
  name: string;
  completed: boolean;
  estimated_minutes: number;
  question_count: number;
  exercise_count: number;
  practice: Practice | null;
};

type BoardModule = {
  id: number;
  name: string;
  order_index: number;
  topics: BoardTopic[];
};

type Board = {
  cursor: { topic_id: number; name: string; slug: string | null } | null;
  totals: { topics: number; completed: number; questions: number; exercises: number };
  modules: BoardModule[];
};

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">{label}</p>
      <p className="mt-1 text-[22px] font-bold leading-none tabular-nums">{value}</p>
    </div>
  );
}

function TopicRow({ topic, isCursor }: { topic: BoardTopic; isCursor: boolean }) {
  return (
    <li
      className={cn(
        "flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-[var(--border)] px-4 py-2.5 text-sm",
        isCursor && "bg-[var(--accent-soft)]",
      )}
    >
      <span
        aria-hidden
        className={cn(
          "size-2 shrink-0 rounded-full",
          topic.completed ? "bg-[var(--ok)]" : "bg-[var(--border-strong)]",
        )}
      />
      <Link
        href={`/learn/topic/${topic.topic_id}`}
        className={cn(
          "min-w-0 flex-1 truncate font-medium hover:text-[var(--accent)] hover:underline",
          topic.completed && "text-[var(--muted)]",
        )}
      >
        {topic.name}
      </Link>

      {isCursor ? (
        <span className="rounded-full bg-[var(--accent)] px-2 py-0.5 text-[11px] font-semibold text-[var(--accent-fg)]">
          Next
        </span>
      ) : null}
      {topic.completed ? (
        <span className="rounded-full bg-[var(--ok-soft)] px-2 py-0.5 text-[11px] font-semibold text-[var(--ok)]">
          Done
        </span>
      ) : null}

      <span className="tabular-nums text-xs text-[var(--muted)]">{topic.estimated_minutes} min</span>
      <span className="tabular-nums text-xs text-[var(--muted)]">
        {topic.question_count} Q{topic.exercise_count ? ` · ${topic.exercise_count} ex` : ""}
      </span>

      {topic.practice ? (
        <a
          href={topic.practice.url}
          target="_blank"
          rel="noopener noreferrer"
          title={topic.practice.title}
          className="text-xs font-medium text-[var(--accent)] hover:underline"
        >
          {topic.practice.provider || "Practice"} &#8599;
        </a>
      ) : (
        <span className="text-xs text-[var(--muted-2)]">no practice link</span>
      )}
    </li>
  );
}

function ModuleGroup({
  module,
  cursorId,
  open,
  onToggle,
}: {
  module: BoardModule;
  cursorId: number | null;
  open: boolean;
  onToggle: () => void;
}) {
  const done = module.topics.filter((t) => t.completed).length;
  const total = module.topics.length;

  return (
    <section className="overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--card)]">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-[var(--card-2)]"
      >
        <span aria-hidden className="text-xs text-[var(--muted)]">
          {open ? "▾" : "▸"}
        </span>
        <h3 className="min-w-0 flex-1 truncate text-sm font-bold">{module.name}</h3>
        <span className="tabular-nums text-xs font-medium text-[var(--muted)]">
          {done}/{total}
        </span>
        <span className="w-24 shrink-0">
          <ProgressBar value={done} max={total} />
        </span>
      </button>
      {open ? (
        <ul>
          {module.topics.map((topic) => (
            <TopicRow key={topic.topic_id} topic={topic} isCursor={topic.topic_id === cursorId} />
          ))}
        </ul>
      ) : null}
    </section>
  );
}

export default function DSAPage() {
  const [board, setBoard] = useState<Board | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openIds, setOpenIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    api<Board>("/api/dsa/board")
      .then((data) => {
        setBoard(data);
        // Open the module holding the cursor so the next problem is visible on load.
        const cursorId = data.cursor?.topic_id ?? null;
        const owner = data.modules.find((m) => m.topics.some((t) => t.topic_id === cursorId));
        setOpenIds(new Set(owner ? [owner.id] : []));
      })
      .catch((err) => setError(errorMessage(err)));
  }, []);

  const toggle = (id: number) =>
    setOpenIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const allOpen = board ? openIds.size === board.modules.length : false;

  return (
    <Page wide>
      <PageTitle
        kicker="DSA"
        title="Pattern board"
        description="Every DSA topic on the roadmap, grouped by pattern. One DSA block also lands in today's session automatically — this board is for looking ahead and jumping straight to a problem."
      />

      {error ? <Banner>{error}</Banner> : null}
      {!board && !error ? <LoadingLine label="Loading board…" /> : null}

      {board ? (
        <>
          <section className="mb-6 rounded-lg border border-[var(--border)] bg-[var(--card)] p-5">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">
                  Continue
                </p>
                {board.cursor ? (
                  <>
                    <Link
                      href={`/learn/topic/${board.cursor.topic_id}`}
                      className="mt-2 block truncate text-[22px] font-bold leading-tight hover:text-[var(--accent)] hover:underline"
                    >
                      {board.cursor.name}
                    </Link>
                    <p className="mt-2 text-sm text-[var(--muted)]">
                      Next incomplete DSA topic. It also appears as today&apos;s DSA block —{" "}
                      <Link href="/today" className="font-medium text-[var(--accent)] hover:underline">
                        open the session
                      </Link>
                      .
                    </p>
                  </>
                ) : (
                  <p className="mt-2 text-[22px] font-bold leading-tight">All DSA topics complete</p>
                )}
              </div>
              <div className="flex shrink-0 gap-8">
                <Stat label="Topics" value={`${board.totals.completed}/${board.totals.topics}`} />
                <Stat label="Questions" value={board.totals.questions} />
                <Stat label="Exercises" value={board.totals.exercises} />
              </div>
            </div>
            <div className="mt-4">
              <ProgressBar value={board.totals.completed} max={board.totals.topics} />
            </div>
          </section>

          <div className="mb-3 flex justify-end">
            <button
              type="button"
              onClick={() =>
                setOpenIds(allOpen ? new Set() : new Set(board.modules.map((m) => m.id)))
              }
              className="text-sm font-medium text-[var(--accent)] hover:underline"
            >
              {allOpen ? "Collapse all" : "Expand all"}
            </button>
          </div>

          {board.modules.length ? (
            <div className="space-y-2">
              {board.modules.map((module) => (
                <ModuleGroup
                  key={module.id}
                  module={module}
                  cursorId={board.cursor?.topic_id ?? null}
                  open={openIds.has(module.id)}
                  onToggle={() => toggle(module.id)}
                />
              ))}
            </div>
          ) : (
            <EmptyState title="No DSA topics" body="The curriculum has no topics in the DSA domain." />
          )}
        </>
      ) : null}
    </Page>
  );
}
