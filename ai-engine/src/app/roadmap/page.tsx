"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { StatusBadge } from "@/components/status-badge";
import { PrerequisiteList } from "@/components/prerequisite-list";
import { Banner, EmptyState, LoadingLine, Page, PageTitle } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import type { CurriculumTree, ModuleNode, TopicNode, TrackNode } from "@/lib/curriculum";
import { cn } from "@/lib/utils";

function ProgressBar({ completed, total }: { completed: number; total: number }) {
  const percent = total ? Math.round((completed / total) * 100) : 0;
  return (
    <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
      <div className="h-1.5 w-20 overflow-hidden rounded-full bg-[var(--border)]">
        <div className="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-2)]" style={{ width: `${percent}%` }} />
      </div>
      <span className="tabular-nums">
        {completed}/{total}
      </span>
    </div>
  );
}

function statusGlyph(topic: TopicNode) {
  if (topic.locked) return <span className="text-sm text-[var(--muted)]" aria-hidden="true">○</span>;
  if (topic.status === "completed") return <span className="text-sm font-bold text-[var(--ok)]" aria-hidden="true">✓</span>;
  if (topic.status === "in_progress") return <span className="text-sm font-bold text-[var(--warn)]" aria-hidden="true">◐</span>;
  return <span className="text-sm text-[var(--muted)]" aria-hidden="true">·</span>;
}

function TopicRow({ topic, current }: { topic: TopicNode; current: boolean }) {
  const inner = (
    <div
      className={cn(
        "flex items-center justify-between gap-3 rounded-lg border px-3 py-2",
        topic.status === "completed" && !topic.locked ? "border-transparent bg-[var(--ok-soft)]" : "border-[var(--border)] bg-[var(--card)]",
        topic.locked ? "border-[var(--border)] opacity-70" : "",
        current && "ring-1 ring-[var(--accent)]",
      )}
    >
      <span className="flex min-w-0 items-center gap-2.5">
        {statusGlyph(topic)}
        <span className={cn("truncate text-sm font-medium", topic.locked && "text-[var(--muted)]")}>{topic.name}</span>
      </span>
      <span className="flex shrink-0 items-center gap-2">
        <StatusBadge status={topic.status} />
      </span>
    </div>
  );
  if (topic.locked) {
    return (
      <div>
        <Link href={`/learn/topic/${topic.id}`} className="block">
          {inner}
        </Link>
        <div className="mt-1 px-1">
          <PrerequisiteList items={topic.prerequisites} message={topic.lock_message} />
        </div>
      </div>
    );
  }
  return (
    <Link href={`/learn/topic/${topic.id}`} className="block">
      {inner}
    </Link>
  );
}

function ModuleBlock({
  module,
  defaultOpen,
  currentTopicId,
}: {
  module: ModuleNode;
  defaultOpen: boolean;
  currentTopicId?: number;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--card)]">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left"
      >
        <div>
          <p className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">Module</p>
          <h3 className="text-sm font-semibold">{module.name}</h3>
        </div>
        <ProgressBar completed={module.progress.completed} total={module.progress.total} />
      </button>
      {open ? (
        <div className="space-y-2 border-t border-[var(--border)] px-4 py-3">
          {module.topics.map((topic) => (
            <TopicRow key={topic.id} topic={topic} current={topic.id === currentTopicId} />
          ))}
        </div>
      ) : null}
    </div>
  );
}

function TrackCard({
  track,
  defaultOpen,
  currentTopicId,
}: {
  track: TrackNode;
  defaultOpen: boolean;
  currentTopicId?: number;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section className="rounded-2xl border border-[var(--border)] p-4">
      <button
        type="button"
        className="flex w-full flex-col gap-2 text-left sm:flex-row sm:items-center sm:justify-between"
        onClick={() => setOpen((value) => !value)}
      >
        <div>
          <p className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">Domain</p>
          <h2 className="text-lg font-semibold">{track.name}</h2>
        </div>
        <ProgressBar completed={track.progress.completed} total={track.progress.total} />
      </button>
      {open
        ? track.levels.map((level) => (
            <div key={level.id} className="mt-5">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">{level.name}</h3>
              {level.subjects.map((subject) => (
                <div key={subject.id} className="mt-3">
                  <div className="mb-2 flex items-center justify-between">
                    <h4 className="text-sm font-medium">{subject.name}</h4>
                    <ProgressBar completed={subject.progress.completed} total={subject.progress.total} />
                  </div>
                  <div className="space-y-3">
                    {subject.modules.map((module, index) => (
                      <ModuleBlock
                        key={module.id}
                        module={module}
                        defaultOpen={defaultOpen && index === 0}
                        currentTopicId={currentTopicId}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ))
        : null}
    </section>
  );
}

export default function RoadmapPage() {
  const [data, setData] = useState<CurriculumTree | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<CurriculumTree>("/api/curriculum/tree")
      .then((tree) => {
        setData(tree);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)));
  }, []);

  return (
    <Page wide>
      <PageTitle
        kicker="Roadmap"
        title="Official sequence"
        description="Collapsed by default so 222 topics are not dumped at once. Topics are completed or not — no mastery scores."
      />
      {error ? <Banner>{error}</Banner> : null}
      {!data && !error ? <LoadingLine label="Loading curriculum…" /> : null}
      {data && data.tracks.length === 0 ? (
        <EmptyState title="No curriculum loaded" body="Import official V1 on the backend, then refresh." />
      ) : null}
      {data && data.tracks.length > 0 ? (
        <div className="space-y-5">
          {data.next ? (
            <p className="text-sm">
              Current:{" "}
              <Link className="underline" href={`/learn/topic/${data.next.topic_id}`}>
                {data.next.topic_name}
              </Link>{" "}
              in {data.next.module_name}
            </p>
          ) : (
            <p className="text-sm text-[var(--muted)]">All currently unlocked topics are complete.</p>
          )}
          {data.tracks.map((track) => (
            <TrackCard
              key={track.id}
              track={track}
              defaultOpen={track.name === "Engineering OS"}
              currentTopicId={data.next?.topic_id}
            />
          ))}
        </div>
      ) : null}
    </Page>
  );
}
