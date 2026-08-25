"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Layers } from "lucide-react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import type { CurriculumTree } from "@/lib/curriculum";

type BridgeItem = {
  slug: string;
  name: string;
  minutes: number;
};

type Bridge = {
  topic_slug: string;
  topic_name?: string;
  blocked: boolean;
  bridge: BridgeItem[];
  total_minutes: number;
  advisory: { slug: string; name: string }[];
};
// Client-side phase mapping from the canonical domain blueprint stages.
function phaseForSlug(slug: string | null | undefined): string {
  if (!slug) return "—";
  if (slug.startsWith("cf-")) return "Phase 1 · Engineering Fundamentals";
  if (slug.startsWith("java-") || slug.startsWith("dsa-")) return "Phase 2 · Programming + DSA";
  if (["py-", "python-", "se-", "db-", "be-", "web-"].some((p) => slug.startsWith(p)))
    return "Phase 3 · Python + Math + Engineering";
  if (slug.startsWith("ml-") || slug.startsWith("ds-")) return "Phase 4–5 · ML + Just-in-time Math";
  if (slug.startsWith("dl-")) return "Phase 6 · Deep Learning";
  if (slug.startsWith("cv-")) return "Phase 7 · Computer Vision";
  if (slug.startsWith("nlp-")) return "Phase 8 · NLP";
  if (slug.startsWith("genai-")) return "Phase 9 · Generative AI / LLMs";
  if (slug.startsWith("ai-eng-") || slug.startsWith("mlops-") || slug.startsWith("sys-"))
    return "Phase 10 · AI Engineering + System Design";
  return "Foundations track";
}

export default function ProgressPage() {
  const [tree, setTree] = useState<CurriculumTree | null>(null);
  const [bridge, setBridge] = useState<Bridge | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<CurriculumTree>("/api/roadmap")
      .then((data) => {
        setTree(data);
        setError(null);
        const nextSlug = data.next ? null : null;
        void nextSlug;
        // Fetch the just-in-time prerequisite bridge for the current position.
        if (data.next?.topic_id) {
          api<{ slug?: string }>(`/api/topic/${data.next.topic_id}`)
            .then((topic) => {
              if (topic.slug) {
                return api<Bridge>(`/api/prerequisite-bridge/${topic.slug}`);
              }
              return null;
            })
            .then((b) => {
              if (b) setBridge(b);
            })
            .catch(() => setBridge(null));
        }
      })
      .catch((err) => setError(errorMessage(err)));
  }, []);

  if (!tree && !error) {
    return (
      <Page>
        <LoadingLine label="Loading progress…" />
      </Page>
    );
  }

  const all = tree?.tracks.flatMap((track) =>
    track.levels.flatMap((level) =>
      level.subjects.flatMap((subject) => subject.modules.flatMap((module) => module.topics)),
    ),
  ) ?? [];
  const completed = all.filter((topic) => topic.status === "completed").length;
  const inProgress = all.filter((topic) => topic.status === "in_progress").length;
  const total = all.length;
  const nextTopicId = tree?.next?.topic_id ?? null;

  // Current position's domain breakdown for "current track".
  const currentTrackName = tree?.next?.track_name ?? null;
  const currentModuleName = tree?.next?.module_name ?? null;
  const currentPhase = phaseForSlug(
    all.find((t) => t.id === nextTopicId)?.slug ?? null,
  );

  const byDomain = {
    Foundations: all.filter((topic) => (topic.slug || "").startsWith("cf-")),
    Java: all.filter((topic) => (topic.slug || "").startsWith("java-")),
    DSA: all.filter((topic) => (topic.slug || "").startsWith("dsa-")),
  };

  return (
    <Page>
      <PageTitle
        kicker="Progress"
        title="Completion"
        description="How much of the sequence is done. No mastery scores — a topic is either completed or it is not."
      />
      {error ? <Banner>{error}</Banner> : null}

      <section className="glow-card p-5">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.14em] text-[var(--muted)]">Topics completed</p>
            <p className="mt-1 text-4xl font-semibold tabular-nums">
              {completed}
              <span className="text-lg font-normal text-[var(--muted)]"> / {total}</span>
            </p>
          </div>
          {inProgress > 0 ? (
            <p className="text-sm text-[var(--muted)]">{inProgress} in progress now</p>
          ) : null}
        </div>
        <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-[var(--border)]">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-2)]"
            style={{ width: `${total ? Math.round((completed / total) * 100) : 0}%` }}
          />
        </div>
        <dl className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
          <div>
            <dt className="text-xs uppercase tracking-[0.14em] text-[var(--muted)]">Current track</dt>
            <dd className="mt-0.5 font-medium">{currentTrackName ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-[0.14em] text-[var(--muted)]">Current module</dt>
            <dd className="mt-0.5 font-medium">{currentModuleName ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-[0.14em] text-[var(--muted)]">Current phase</dt>
            <dd className="mt-0.5 font-medium">{currentPhase}</dd>
          </div>
        </dl>
      </section>

      {bridge && bridge.blocked && bridge.bridge.length > 0 ? (
        <section className="mt-8">
          <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">
            Upcoming prerequisites
          </h2>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Before <strong>{bridge.topic_name ?? "your next topic"}</strong>, complete this bridge
            {" "}({bridge.total_minutes} min):
          </p>
          <ol className="mt-3 space-y-2">
            {bridge.bridge.map((item, index) => (
              <li
                key={item.slug}
                className="flex items-center justify-between gap-3 rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-2"
              >
                <span className="text-sm">
                  {index + 1}. {item.name}
                </span>
                <span className="shrink-0 text-xs text-[var(--muted)]">{item.minutes} min</span>
              </li>
            ))}
          </ol>
        </section>
      ) : null}

      <section className="mt-8">
        <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">Continue</h2>
        {tree?.next ? (
          <Link
            href={`/learn/topic/${tree.next.topic_id}`}
            className="glow-card mt-3 flex items-center justify-between gap-3 px-4 py-3"
          >
            <div>
              <p className="font-medium">{tree.next.topic_name}</p>
              <p className="mt-0.5 text-xs text-[var(--muted)]">
                {tree.next.module_name} · {tree.next.track_name}
              </p>
            </div>
            <span className="text-sm font-medium text-[var(--accent)]">Open →</span>
          </Link>
        ) : (
          <p className="mt-3 text-sm text-[var(--muted)]">All unlocked topics are complete.</p>
        )}
      </section>

      <section className="mt-8">
        <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">
          <Layers className="h-4 w-4" /> By domain
        </h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          {Object.entries(byDomain).map(([name, list]) => {
            const done = list.filter((topic) => topic.status === "completed").length;
            const pct = list.length ? Math.round((done / list.length) * 100) : 0;
            return (
              <div key={name} className="glow-card p-4">
                <p className="text-sm font-medium">{name}</p>
                <p className="mt-1 text-2xl font-semibold tabular-nums">
                  {done}
                  <span className="text-xs font-normal text-[var(--muted)]"> / {list.length}</span>
                </p>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-[var(--border)]">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-2)]"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {total === 0 ? (
        <div className="mt-8">
          <EmptyState title="No curriculum loaded" body="Import the official curriculum on the backend, then refresh." />
        </div>
      ) : null}
    </Page>
  );
}
