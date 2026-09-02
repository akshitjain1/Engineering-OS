"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ArrowRight, Check, Clipboard, ExternalLink, Lightbulb, Loader2 } from "lucide-react";
import { SourceResourceCard } from "@/components/source-resource";
import { GhostButton } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import type { ResourcePublic, TopicNode } from "@/lib/curriculum";

/* -------------------------------------------------------------------------
 * A topic's work, in the order you are meant to do it, rendered wherever you
 * already are. Same endpoints as the topic page, so anything marked done here
 * is done there too.
 *
 * The point of this component is sequence. A DSA block used to show only the
 * problem it had picked, which asked the learner to solve something before
 * being shown what to read -- the reading was a page away on the topic. Read
 * first, then solve, with a time budget on each, is the whole idea.
 * ---------------------------------------------------------------------- */

export type WorkSection = "learn" | "practice" | "build";

/** Free community solutions for a LeetCode problem. Derived rather than
 *  stored: it is the problem URL plus a path segment, so there is nothing to
 *  keep in sync and nothing invented. Any other host returns null. */
export function solutionsUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  const match = /^https:\/\/leetcode\.com\/problems\/([a-z0-9-]+)\/?$/i.exec(url.trim());
  return match ? `https://leetcode.com/problems/${match[1]}/solutions/` : null;
}

/** Minutes this one source is expected to take. */
function minutesFor(resource: ResourcePublic, fallback = 15): number {
  return resource.estimated_minutes ?? resource.duration ?? fallback;
}

const DIFFICULTY_TONE: Record<string, string> = {
  easy: "text-[var(--ok)] border-[var(--ok)]",
  medium: "text-[var(--warn)] border-[var(--warn)]",
  hard: "text-[var(--danger)] border-[var(--danger)]",
};

/** Shown when no practice source is mapped. The app never invents problem
 *  URLs, so the fallback is a prompt you take elsewhere. */
export function PracticePrompt({ topic }: { topic: TopicNode }) {
  const [copied, setCopied] = useState(false);
  const source = (topic.resources_by_role?.PRIMARY || [])[0];
  const prompt = [
    `I am studying "${topic.name}".`,
    source
      ? `Primary source: ${source.title}${source.provider ? ` by ${source.provider}` : ""}${source.url ? ` (${source.url})` : ""}.`
      : "",
    `Give me a small set of practice exercises for ${topic.name}.`,
    "Prefer plain problems with worked solutions over multiple choice. Do not send me to any specific website or problem ID.",
    "I will attempt them on my own and come back with my code or answers for feedback.",
  ]
    .filter(Boolean)
    .join("\n");

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(prompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <div className="glow-card p-4">
      <p className="text-sm font-medium">No practice source is mapped yet.</p>
      <p className="mt-1 text-sm text-[var(--muted)]">
        Copy this prompt into any AI assistant or coding platform — the app does not track answers
        or call an LLM.
      </p>
      <textarea
        readOnly
        value={prompt}
        rows={6}
        className="mt-3 w-full resize-none rounded-lg border border-[var(--border)] bg-[var(--card-2)] px-3 py-2 text-xs leading-relaxed text-[var(--foreground)]"
      />
      <div className="mt-3">
        <GhostButton onClick={copy}>
          <Clipboard className="mr-2 h-4 w-4" />
          {copied ? "Copied" : "Copy prompt"}
        </GhostButton>
      </div>
    </div>
  );
}

/** One mapped problem: what it is, how long to give it, why it belongs to this
 *  topic, and a way out if you are stuck. */
function ProblemRow({
  resource,
  index,
  locked,
  busy,
  onToggle,
}: {
  resource: ResourcePublic;
  index: number;
  locked?: boolean;
  busy: boolean;
  onToggle: (id: number, completed: boolean) => void;
}) {
  const [showHint, setShowHint] = useState(false);
  const solutions = solutionsUrl(resource.url);
  const tone = DIFFICULTY_TONE[(resource.difficulty || "").toLowerCase()] ?? "text-[var(--muted)] border-[var(--border)]";

  return (
    <li className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs text-[var(--muted)]">
            Problem {index + 1} · {resource.provider ?? "LeetCode"}
          </p>
          <p className="mt-0.5 text-sm font-medium">{resource.title}</p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {resource.difficulty ? (
            <span className={`rounded border px-2 py-0.5 text-xs font-medium ${tone}`}>
              {resource.difficulty}
            </span>
          ) : null}
          <span className="rounded border border-[var(--border)] px-2 py-0.5 text-xs text-[var(--muted)]">
            ~{minutesFor(resource)} min
          </span>
        </div>
      </div>

      {resource.description ? (
        <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">{resource.description}</p>
      ) : null}

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {resource.url ? (
          <a
            href={resource.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-md bg-[var(--accent)] px-3.5 py-2 text-sm font-medium text-[var(--accent-fg)] hover:bg-[var(--accent-hover)]"
          >
            Solve it <ExternalLink className="h-3.5 w-3.5" />
          </a>
        ) : null}
        {solutions ? (
          <button
            type="button"
            onClick={() => setShowHint((v) => !v)}
            className="inline-flex items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card-2)] px-3 py-2 text-sm text-[var(--muted)] hover:border-[var(--border-strong)]"
          >
            <Lightbulb className="h-3.5 w-3.5" /> Stuck?
          </button>
        ) : null}
        {!locked ? (
          <button
            type="button"
            disabled={busy}
            onClick={() => onToggle(resource.id, !resource.completed)}
            className="inline-flex items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card-2)] px-3 py-2 text-sm hover:border-[var(--border-strong)] disabled:opacity-50"
          >
            {resource.completed ? (
              <>
                <Check className="h-3.5 w-3.5 text-[var(--ok)]" /> Solved
              </>
            ) : (
              "Mark solved"
            )}
          </button>
        ) : null}
      </div>

      {showHint && solutions ? (
        <div className="mt-3 rounded-md border border-[var(--border)] bg-[var(--card-2)] p-3">
          <p className="text-xs text-[var(--muted)]">
            Give it a genuine attempt first — a solution you read after trying sticks; one you read
            instead of trying does not.
          </p>
          <a
            href={solutions}
            target="_blank"
            rel="noreferrer"
            className="mt-2 inline-flex items-center gap-1.5 text-sm underline"
          >
            Community solutions on LeetCode <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      ) : null}
    </li>
  );
}

/** The whole plan for a topic: read, then solve, then build -- self-loading.
 *  `sections` decides which steps this block is responsible for. */
export function TopicWorkPanel({
  topicId,
  sections = ["practice", "build"],
  blockMinutes,
}: {
  topicId: number;
  sections?: WorkSection[];
  /** The block's planned minutes, so the plan can be checked against them. */
  blockMinutes?: number;
}) {
  const [topic, setTopic] = useState<TopicNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(() => {
    api<TopicNode>(`/api/topic/${topicId}`)
      .then((data) => {
        setTopic(data);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)));
  }, [topicId]);

  // No reset needed here: the panel is keyed on topicId by its parent, so a
  // different topic remounts rather than reusing this instance's state.
  useEffect(() => {
    load();
  }, [load]);

  const run = async (key: string, fn: () => Promise<unknown>) => {
    setBusy(key);
    try {
      await fn();
      load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(null);
    }
  };

  const toggleResource = (resourceId: number, completed: boolean) =>
    run(`resource-${resourceId}`, () =>
      api(`/api/progress/resource/${resourceId}`, {
        method: "POST",
        body: JSON.stringify({ completed }),
      }),
    );

  const learn = useMemo(() => topic?.resources_by_role?.PRIMARY ?? [], [topic]);
  const practice = useMemo(() => topic?.resources_by_role?.PRACTICE ?? [], [topic]);

  const plan = useMemo(() => {
    const readMinutes = learn.reduce((sum, r) => sum + minutesFor(r, 20), 0);
    const solveMinutes = practice.reduce((sum, r) => sum + minutesFor(r), 0);
    return { readMinutes, solveMinutes, total: readMinutes + solveMinutes };
  }, [learn, practice]);

  if (error && !topic) {
    return (
      <div className="rounded-lg border border-[var(--border)] bg-[var(--card-2)] p-4">
        <p className="text-sm text-[var(--warn)]">{error}</p>
        <Link
          href={`/learn/topic/${topicId}`}
          className="mt-3 inline-flex items-center gap-2 text-sm underline"
        >
          Open the topic instead <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    );
  }

  if (!topic) {
    return (
      <p className="inline-flex items-center gap-2 text-sm text-[var(--muted)]">
        <Loader2 className="h-3.5 w-3.5 animate-spin" /> Loading the work for this topic…
      </p>
    );
  }

  const build = topic.implement || topic.exercises || [];
  const wants = (section: WorkSection) => sections.includes(section);
  const showLearn = wants("learn") && learn.length > 0;
  const showPractice = wants("practice");
  const showBuild = wants("build") && build.length > 0;
  const overBudget = blockMinutes != null && plan.total > blockMinutes;

  // Numbered from the steps this block actually shows, so a practice-only
  // block starts at 1 rather than skipping to 2.
  const steps: WorkSection[] = [
    ...(showLearn ? (["learn"] as const) : []),
    ...(showPractice ? (["practice"] as const) : []),
    ...(showBuild ? (["build"] as const) : []),
  ];
  const stepLabel = (section: WorkSection) => steps.indexOf(section) + 1;

  return (
    <div className="space-y-6">
      {error ? <p className="text-sm text-[var(--warn)]">{error}</p> : null}

      {showLearn && showPractice ? (
        <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">
            Plan for this block
          </p>
          <p className="mt-1 text-sm">
            Read ~{plan.readMinutes} min, then solve {practice.length}{" "}
            {practice.length === 1 ? "problem" : "problems"} ~{plan.solveMinutes} min
            <span className="text-[var(--muted)]"> · {plan.total} min total</span>
          </p>
          {overBudget ? (
            <p className="mt-1 text-xs text-[var(--warn)]">
              That is {plan.total - (blockMinutes ?? 0)} min over the {blockMinutes} planned here.
              Read first and solve as far as you get — the timer logs what you actually spend.
            </p>
          ) : null}
        </div>
      ) : null}

      {showLearn ? (
        <section>
          <p className="text-sm font-semibold">
            {stepLabel("learn")}. Learn it first
            <span className="ml-2 text-xs font-normal text-[var(--muted)]">
              ~{plan.readMinutes} min · read before you attempt anything below
            </span>
          </p>
          <div className="mt-3 space-y-3">
            {learn.map((resource) => (
              <SourceResourceCard
                key={resource.id}
                resource={resource}
                locked={topic.locked}
                onToggle={toggleResource}
              />
            ))}
          </div>
        </section>
      ) : null}

      {showPractice ? (
        <section>
          <p className="text-sm font-semibold">
            {stepLabel("practice")}. Then solve these
            <span className="ml-2 text-xs font-normal text-[var(--muted)]">
              {practice.length > 0
                ? `~${plan.solveMinutes} min · mapped to this topic, in order`
                : "do the work on the official platform — not an in-app quiz"}
            </span>
          </p>
          {practice.length > 0 ? (
            <ul className="mt-3 space-y-3">
              {practice.map((resource, i) => (
                <ProblemRow
                  key={resource.id}
                  resource={resource}
                  index={i}
                  locked={topic.locked}
                  busy={busy === `resource-${resource.id}`}
                  onToggle={toggleResource}
                />
              ))}
            </ul>
          ) : topic.locked ? null : (
            <div className="mt-3">
              <PracticePrompt topic={topic} />
            </div>
          )}
        </section>
      ) : null}

      {showBuild ? (
        <section>
          <p className="text-sm font-semibold">
            {stepLabel("build")}. Build
            <span className="ml-2 text-xs font-normal text-[var(--muted)]">
              one concrete implementation action
            </span>
          </p>
          <div className="mt-3 space-y-3">
            {build.map((exercise) => (
              <div
                key={exercise.id}
                className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-sm font-medium">{exercise.title}</p>
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
        </section>
      ) : null}

      <Link
        href={`/learn/topic/${topicId}`}
        className="inline-flex items-center gap-1.5 text-xs text-[var(--muted)] underline hover:text-[var(--foreground)]"
      >
        Open the full topic <ArrowRight className="h-3 w-3" />
      </Link>
    </div>
  );
}
