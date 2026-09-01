"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Check, ChevronRight, Clock, Loader2, Lock } from "lucide-react";
import { PrerequisiteList } from "@/components/prerequisite-list";
import { SourceResourceCard } from "@/components/source-resource";
import { PracticePrompt } from "@/components/topic-work";
import { StatusBadge } from "@/components/status-badge";
import { Banner, GhostButton, LoadingLine, Page, PrimaryButton } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import type { ResourcePublic, TopicNode } from "@/lib/curriculum";
import { cn } from "@/lib/utils";

type StudyContract = {
  why_now?: string | null;
  learn?: {
    title?: string | null;
    provider?: string | null;
    url?: string | null;
    section?: string | null;
    lecture?: string | null;
    verification_status?: string | null;
    exactness?: string | null;
    estimated_minutes?: number | null;
    estimate_confidence?: string | null;
  };
  focus_concepts?: string[];
  practice?: {
    title?: string | null;
    instructions?: string | null;
    destination_type?: string | null;
    destination_url?: string | null;
    quantity?: number | null;
  };
  build?: { title?: string | null; instructions?: string | null };
  done_when?: string[];
  next?: { id: number; slug?: string | null; name: string } | null;
  readiness?: string | null;
  missing_concepts?: string[];
  resource_notes?: string | null;
};

function StudyContractPanel({ contract }: { contract: StudyContract }) {
  const learn = contract.learn;
  const readiness = (contract.readiness || "").toUpperCase();
  const readinessLabel =
    readiness === "READY"
      ? "Verified READY"
      : readiness === "PARTIAL_COVERAGE"
        ? "Partially verified"
        : readiness === "RESOURCE_GAP"
          ? "Verified learning resource still missing"
          : readiness === "NEEDS_REVIEW"
            ? "Needs review — not learner-verified"
            : readiness === "PRACTICE_GAP" || readiness === "PRACTICE_UNVERIFIED"
              ? "Practice contract incomplete"
              : readiness === "TIME_UNVERIFIED"
                ? "Time estimate approximate"
                : readiness === "BROKEN"
                  ? "Broken primary resource"
                  : readiness || "Unknown";
  const readinessWarn = readiness && readiness !== "READY";
  return (
    <section className="mt-6 space-y-4 rounded-lg border border-[var(--border)] bg-[var(--card)] p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-semibold tracking-tight">Study contract</h2>
        <span
          className={
            readinessWarn
              ? "rounded border border-[var(--warn)] px-2 py-0.5 text-xs text-[var(--warn)]"
              : "rounded border border-[var(--border)] px-2 py-0.5 text-xs text-[var(--muted)]"
          }
        >
          {readinessLabel}
        </span>
      </div>
      {readiness === "PARTIAL_COVERAGE" && (contract.missing_concepts?.length ?? 0) > 0 ? (
        <p className="text-sm text-[var(--warn)]">
          Missing verified concepts: {(contract.missing_concepts || []).join(", ")}
        </p>
      ) : null}
      {readiness === "RESOURCE_GAP" ? (
        <p className="text-sm text-[var(--warn)]">
          Do not treat this as a normal study recommendation until an exact verified resource is mapped.
        </p>
      ) : null}
      {readiness === "NEEDS_REVIEW" ? (
        <p className="text-sm text-[var(--warn)]">
          Resource exists but content verification is not trusted yet. Prefer READY topics for daily study.
        </p>
      ) : null}
      {contract.why_now ? (
        <div>
          <p className="text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Why now</p>
          <p className="mt-1 text-sm leading-relaxed">{contract.why_now}</p>
        </div>
      ) : null}
      {learn?.url || learn?.title ? (
        <div>
          <p className="text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Learn — open exactly this</p>
          <p className="mt-1 text-sm">
            {learn.provider ? `${learn.provider} — ` : ""}
            {learn.title}
          </p>
          {learn.section || learn.lecture ? (
            <p className="text-xs font-medium text-[var(--foreground)]">
              Exact section: {learn.lecture ? `${learn.lecture} · ` : ""}
              {learn.section}
            </p>
          ) : learn.exactness === "COLLECTION" || learn.exactness === "MULTI_TOPIC" ? (
            <p className="text-xs text-[var(--warn)]">
              Multi-topic/collection — section/timestamp missing; do not consume the whole resource blindly.
            </p>
          ) : null}
          <p className="text-xs text-[var(--muted)]">
            ~{learn.estimated_minutes ?? "?"} min
            {learn.estimate_confidence ? ` · ${learn.estimate_confidence} confidence` : ""}
            {learn.verification_status ? ` · ${learn.verification_status}` : ""}
            {learn.exactness ? ` · ${learn.exactness}` : ""}
          </p>
          {learn.url ? (
            <a href={learn.url} target="_blank" rel="noreferrer" className="text-xs underline">
              Open exact source
            </a>
          ) : null}
        </div>
      ) : null}
      {contract.focus_concepts && contract.focus_concepts.length > 0 ? (
        <div>
          <p className="text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Focus</p>
          <ul className="mt-1 list-disc space-y-0.5 pl-4 text-sm">
            {contract.focus_concepts.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {contract.practice?.instructions ? (
        <div>
          <p className="text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Practice</p>
          <p className="mt-1 whitespace-pre-wrap text-sm">{contract.practice.instructions}</p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            {contract.practice.destination_type || "DESTINATION"}
            {contract.practice.quantity != null ? ` · quantity ${contract.practice.quantity}` : ""}
          </p>
          {contract.practice.destination_url ? (
            <a href={contract.practice.destination_url} target="_blank" rel="noreferrer" className="text-xs underline">
              Open practice destination
            </a>
          ) : null}
        </div>
      ) : null}
      {contract.build?.instructions ? (
        <div>
          <p className="text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Build</p>
          <p className="mt-1 text-sm">{contract.build.instructions}</p>
        </div>
      ) : null}
      {contract.done_when?.length ? (
        <div>
          <p className="text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Done when</p>
          <ul className="mt-1 list-disc space-y-0.5 pl-4 text-sm">
            {contract.done_when.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {contract.next ? (
        <div>
          <p className="text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Next</p>
          <Link href={`/learn/topic/${contract.next.id}`} className="mt-1 inline-block text-sm underline">
            {contract.next.name}
          </Link>
        </div>
      ) : null}
      {contract.resource_notes ? (
        <p className="text-xs text-[var(--warn)]">{contract.resource_notes}</p>
      ) : null}
    </section>
  );
}

export default function TopicDetailPage() {
  const params = useParams<{ id: string }>();
  const [topic, setTopic] = useState<TopicNode | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    if (!params.id) return;
    api<TopicNode>(`/api/topic/${params.id}`)
      .then((data) => {
        setTopic(data);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  const toggleResource = async (resourceId: number, completed: boolean) => {
    await api(`/api/progress/resource/${resourceId}`, {
      method: "POST",
      body: JSON.stringify({ completed }),
    });
    load();
  };

  if (error) {
    return (
      <Page>
        <Banner>{error}</Banner>
      </Page>
    );
  }
  if (!topic) {
    return (
      <Page>
        <LoadingLine label="Loading topic…" />
      </Page>
    );
  }
  return <TopicView topic={topic} onToggleResource={toggleResource} onReload={load} />;
}

function TopicView({
  topic,
  onToggleResource,
  onReload,
}: {
  topic: TopicNode;
  onToggleResource: (id: number, completed: boolean) => Promise<void>;
  onReload: () => void;
}) {
  const roles = topic.resources_by_role || { PRIMARY: [], REFERENCE: [], PRACTICE: [], DEEP_DIVE: [] };
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [reviewed, setReviewed] = useState(false);

  const primary = roles.PRIMARY || [];
  const reference = roles.REFERENCE || [];
  const practice = roles.PRACTICE || [];
  const deepDive = roles.DEEP_DIVE || [];
  const build = topic.implement || [];
  const practiceMapped = practice.length > 0;
  const practiceDone = practice.every((r) => r.completed);
  const buildDone = build.length === 0 || build.every((e) => e.completed);
  const learnDone = primary.length === 0 || primary.some((r) => r.completed);

  const done = topic.status === "completed";

  const minutes = () => {
    const hours = topic.hours_estimated || 0;
    return hours > 0 ? Math.max(30, Math.round(hours * 60)) : 30;
  };

  const run = async (key: string, fn: () => Promise<unknown>) => {
    setBusy(key);
    setActionError(null);
    try {
      await fn();
      onReload();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(null);
    }
  };

  const addToReview = () =>
    run("review", () => {
      const query = new URLSearchParams({
        item_id: String(topic.id),
        item_type: "topic",
        confidence: "50",
      });
      return api(`/api/revision/schedule?${query.toString()}`, { method: "POST" }).then(() =>
        setReviewed(true),
      );
    });

  const markComplete = () =>
    run("complete", () => api(`/api/topic/${topic.id}/complete`, { method: "POST" }));

  return (
    <Page wide>
      <p className="text-sm text-[var(--muted)]">
        <Link href="/roadmap" className="underline hover:text-[var(--foreground)]">
          Roadmap
        </Link>
        {topic.breadcrumb?.module_name ? (
          <>
            {" "}
            <ChevronRight className="inline h-3 w-3" /> {topic.breadcrumb.module_name}
          </>
        ) : null}
      </p>

      <header className="mt-4">
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-[var(--muted)]">
          {(topic.domain || "foundations").toUpperCase()}
          {topic.breadcrumb?.module_name ? ` · ${topic.breadcrumb.module_name}` : ""}
        </p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight sm:text-3xl">{topic.name}</h1>
        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
          <StatusBadge status={topic.status} />
          <span className="inline-flex items-center gap-1 text-[var(--muted)]">
            <Clock className="h-3.5 w-3.5" /> ~{minutes()} min
          </span>
        </div>
        {topic.learning_objective ? (
          <p className="mt-3 max-w-prose text-sm leading-relaxed text-[var(--muted)]">{topic.learning_objective}</p>
        ) : null}
      </header>

      {(topic as unknown as { study_contract?: StudyContract }).study_contract ? (
        <StudyContractPanel
          contract={(topic as unknown as { study_contract: StudyContract }).study_contract}
        />
      ) : null}

      {actionError ? (
        <div className="mt-6">
          <Banner>{actionError}</Banner>
        </div>
      ) : null}

      {topic.locked ? (
        <div className="glow-card mt-6 p-5">
          <p className="flex items-center gap-2 text-sm font-medium">
            <Lock className="h-4 w-4 text-[var(--warn)]" /> Preview — locked
          </p>
          <p className="mt-1 text-sm text-[var(--muted)]">
            {topic.lock_message || "Complete the prerequisites to unlock progression. You can still inspect resources."}
          </p>
          <div className="mt-4">
            <PrerequisiteList items={topic.prerequisites} message={topic.lock_message} />
          </div>
        </div>
      ) : null}

      <div className="mt-8 grid gap-6 lg:grid-cols-[180px_minmax(0,1fr)_260px]">
        {/* LEFT: mini TOC */}
        <nav className="hidden lg:block" aria-label="Topic sections">
          <div className="sticky top-16 rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 text-sm">
            <p className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">On this topic</p>
            <ul className="mt-2 space-y-1">
              {[
                ["what-to-do", "Overview"],
                ["learn", "Learn"],
                ["practice", "Practice"],
                ["build", "Build"],
                ["deep-dive", "Deep Dive"],
              ].map(([id, label]) => (
                <li key={id}><a href={`#${id}`} className="block rounded px-2 py-1 hover:bg-[var(--card-2)]">{label}</a></li>
              ))}
            </ul>
          </div>
        </nav>

        {/* CENTER */}
        <div>
      <section id="what-to-do" className="scroll-mt-20">
        <SectionTitle step="1" title="What to do" hint="A short working plan for this topic." />
        <ul className="mt-3 space-y-2">
          <WhatToDoRow
            label="Learn from the source"
            detail={`${minutes()} min · the primary source below`}
            done={learnDone}
          />
          <WhatToDoRow
            label="Practice"
            detail={practiceMapped ? `${Math.round(practice.length * 20)} min · mapped practice sources` : "20 min · take the prompt below to any AI or platform"}
            done={practiceDone}
          />
          <WhatToDoRow
            label="Build"
            detail={build.length ? `${build.length * 25} min · implementation task` : "No implementation task mapped"}
            done={buildDone}
          />
          {deepDive.length > 0 ? (
            <WhatToDoRow
              label="Optional deep dive"
              detail={`${deepDive.length * 15} min · extra sources`}
              done={deepDive.every((r) => r.completed)}
              optional
            />
          ) : null}
        </ul>
      </section>

      <section id="learn" className="mt-10 scroll-mt-20">
        <SectionTitle step="2" title="Learn from" hint="The primary source — watch or read it." />
        {primary.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--warn)]">
            SOURCE NOT MAPPED YET. Engineering OS does not invent URLs. Verified sources appear here when mapped.
          </p>
        ) : (
          <div className="mt-3 space-y-3">
            {primary.map((resource) => (
              <div key={resource.id}>
                <SourceLabel resource={resource} />
                <div className="mt-2">
                  <SourceResourceCard resource={resource} locked={topic.locked} onToggle={onToggleResource} />
                </div>
              </div>
            ))}
          </div>
        )}

        {reference.length > 0 ? (
          <div className="mt-5">
            <h3 className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">Reference</h3>
            <div className="mt-2 space-y-3">
              {reference.map((resource) => (
                <SourceResourceCard key={resource.id} resource={resource} locked={topic.locked} onToggle={onToggleResource} />
              ))}
            </div>
          </div>
        ) : null}
      </section>

      <section id="practice" className="mt-10 scroll-mt-20">
        <SectionTitle step="3" title="Practice" hint="Do the work on the official platform — not an in-app quiz." />
        {practiceMapped ? (
          <div className="mt-3 space-y-3">
            {practice.map((resource) => (
              <SourceResourceCard key={resource.id} resource={resource} locked={topic.locked} onToggle={onToggleResource} />
            ))}
          </div>
        ) : topic.locked ? null : (
          <div className="mt-3">
            <PracticePrompt topic={topic} />
          </div>
        )}
      </section>

      <section id="build" className="mt-10 scroll-mt-20">
        <SectionTitle step="4" title="Build" hint="One concrete implementation action — then mark it done." />
        {build.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--muted)]">No implementation task is mapped for this topic yet.</p>
        ) : (
          <div className="mt-3 space-y-3">
            {build.map((exercise) => (
              <div key={exercise.id} className="glow-card p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">{exercise.title}</p>
                    {exercise.description ? (
                      <p className="mt-1 text-sm text-[var(--muted)]">{exercise.description}</p>
                    ) : null}
                  </div>
                  {exercise.completed ? (
                    <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-[var(--ok-soft)] px-2.5 py-0.5 text-xs font-medium text-[var(--ok)]">
                      <Check className="h-3 w-3" /> Done
                    </span>
                  ) : null}
                </div>
                {!exercise.completed && !topic.locked ? (
                  <div className="mt-3">
                    <GhostButton
                      disabled={busy === `build-${exercise.id}`}
                      onClick={() =>
                        run(`build-${exercise.id}`, () =>
                          api(`/api/exercise/${exercise.id}/complete`, { method: "POST" }),
                        )
                      }
                    >
                      {busy === `build-${exercise.id}` ? "Saving…" : "Mark implementation complete"}
                    </GhostButton>
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </section>

      {deepDive.length > 0 ? (
        <section id="deep-dive" className="mt-10 scroll-mt-20">
          <SectionTitle step="5" title="Optional deep dive" hint="Extra context — only if you want more." />
          <div className="mt-3 space-y-3">
            {deepDive.map((resource) => (
              <SourceResourceCard key={resource.id} resource={resource} locked={topic.locked} onToggle={onToggleResource} />
            ))}
          </div>
        </section>
      ) : null}

      <section className="mt-10 border-t border-[var(--border)] pt-6">
        {done ? (
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="flex items-center gap-2 text-sm font-semibold text-[var(--ok)]">
                <Check className="h-4 w-4" /> Topic complete
              </p>
              <p className="mt-1 text-sm text-[var(--muted)]">Marking it done unlocked the next topic.</p>
            </div>
            {topic.next_in_sequence?.id ? (
              <PrimaryButton href={`/learn/topic/${topic.next_in_sequence.id}`}>Next topic</PrimaryButton>
            ) : (
              <p className="text-sm text-[var(--muted)]">This is the last official topic in sequence.</p>
            )}
          </div>
        ) : topic.locked ? (
          <p className="text-sm text-[var(--muted)]">Locked — inspect resources, then complete prerequisites to mark done.</p>
        ) : (
          <div className="flex flex-wrap items-center gap-3">
            <PrimaryButton onClick={markComplete} disabled={busy === "complete"}>
              {busy === "complete" ? (
                <span className="inline-flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" /> Saving…
                </span>
              ) : (
                "Mark topic complete"
              )}
            </PrimaryButton>
            <GhostButton onClick={addToReview} disabled={busy === "review"}>
              {reviewed ? "In review queue" : "Add to review"}
            </GhostButton>
          </div>
        )}
      </section>
        </div>

        {/* RIGHT: study context */}
        <aside className="space-y-4">
          <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">Study</p>
            <p className="mt-2 text-sm"><span className="font-semibold">~{minutes()} min</span> estimated</p>
            <StatusBadge status={topic.status} />
            <div className="mt-3">
              <a href="#learn" className="block w-full rounded-md bg-[var(--accent)] px-3 py-2 text-center text-sm font-medium text-[var(--accent-fg)] hover:opacity-90">Start Focus</a>
            </div>
            {topic.next_in_sequence ? (
              <div className="mt-4 border-t border-[var(--border)] pt-3">
                <p className="text-xs uppercase tracking-wider text-[var(--muted)]">Next</p>
                <p className="mt-1 text-sm font-medium">{topic.next_in_sequence.name}</p>
                <Link href={`/learn/topic/${topic.next_in_sequence.id}`} className="mt-1 inline-block text-xs underline">Open next →</Link>
              </div>
            ) : null}
          </div>
          <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">Prerequisites</p>
            <div className="mt-2">
              <PrerequisiteList items={topic.prerequisites} message={topic.lock_message} />
            </div>
            <p className="mt-2 text-xs text-[var(--muted)]">You can preview the topic even when locked.</p>
          </div>
          <div className="rounded-lg border border-[var(--border)] bg-[var(--card-2)] p-3 text-xs text-[var(--muted)]">
            Flow: Open → Read/Watch Primary → Mark Learn → Practice → Build → Review → Next
          </div>
        </aside>
      </div>
    </Page>
  );
}

function SectionTitle({ step, title, hint }: { step: string; title: string; hint: string }) {
  return (
    <div className="flex flex-wrap items-baseline gap-3">
      <span className="text-gradient text-sm font-bold tabular-nums">{step}</span>
      <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
      <span className="hidden text-xs text-[var(--muted)] sm:inline">{hint}</span>
    </div>
  );
}

function WhatToDoRow({
  label,
  detail,
  done,
  optional,
}: {
  label: string;
  detail: string;
  done: boolean;
  optional?: boolean;
}) {
  return (
    <li
      className={cn(
        "flex items-center gap-3 rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-2.5",
        done && "opacity-70",
      )}
    >
      <span
        className={cn(
          "flex h-4 w-4 shrink-0 items-center justify-center rounded-full",
          done ? "bg-[var(--ok-soft)] text-[var(--ok)]" : "border border-[var(--border)]",
        )}
      >
        {done ? <Check className="h-2.5 w-2.5" /> : null}
      </span>
      <span className="text-sm font-medium">{label}</span>
      <span className={cn("ml-auto text-right text-xs", optional ? "italic text-[var(--muted)]" : "text-[var(--muted)]")}>
        {detail}
      </span>
    </li>
  );
}

function SourceLabel({ resource }: { resource: ResourcePublic }) {
  const label = sourceLabel(resource);
  const unresolved = label === "SOURCE NOT MAPPED YET";
  return (
    <p
      className={cn(
        "text-[11px] font-semibold uppercase tracking-[0.12em]",
        unresolved ? "text-[var(--warn)]" : "text-[var(--accent-2)]",
      )}
    >
      {label}
    </p>
  );
}

function sourceLabel(resource: ResourcePublic): string {
  const status = (resource.verification_status || resource.resource_status || "").toUpperCase();
  const mapped =
    Boolean(resource.url) &&
    !["", "UNRESOLVED", "UNVERIFIED", "BROKEN"].includes(status);
  if (!resource.url || !mapped) return "SOURCE NOT MAPPED YET";
  if (resource.is_playlist) return "PLAYLIST";
  if (resource.embeddable && resource.exact) return "EXACT LECTURE";
  if (resource.resource_type === "lecture") return "EXACT LECTURE";
  if (resource.resource_type === "documentation") return "OFFICIAL DOCUMENTATION";
  if (resource.resource_type === "course") return "COURSE";
  if (resource.resource_type === "problem" || resource.resource_type === "exercise") return "PRACTICE COLLECTION";
  return resource.exact === false ? "COLLECTION" : "OFFICIAL RESOURCE";
}
