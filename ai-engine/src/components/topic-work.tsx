"use client";

import Link from "next/link";
import { Fragment, useCallback, useEffect, useMemo, useState } from "react";
import { ArrowRight, Check, Clipboard, ExternalLink, Lightbulb, Loader2 } from "lucide-react";
import { SourceResourceCard } from "@/components/source-resource";
import { GhostButton } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import type { ResourcePublic, TopicNode } from "@/lib/curriculum";
import { buildStuckPrompt } from "@/lib/stuck-prompt";
import { TopicQuestions } from "@/components/topic-questions";

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

export type WorkSection = "learn" | "practice" | "build" | "recall";

/** What a problem card needs to know about where it sits, so a stuck learner
 *  gets a prompt with real context rather than just a problem title. */
export type ProblemContext = {
  topicName: string;
  sourceTitle: string | null;
  sourceUrl: string | null;
};

/** The language the generated prompt asks for code in. */
export const PROMPT_LANGUAGE = "Java";

/** Whether a practice resource is an actual coding problem.
 *
 *  The stuck prompt asks for a brute force, a dry run and similar LeetCode
 *  numbers. That is meaningful for a problem and nonsense for a tutorial page,
 *  so PRACTICE resources that are not problems keep the plain source card.
 *  `resource_type` is the canonicalised value, where coding_problem becomes
 *  "problem" and an interactive tutorial becomes "course". */
export const isCodingProblem = (resource: ResourcePublic) =>
  resource.resource_type === "problem";

/** Minutes this one source is expected to take. */
function minutesFor(resource: ResourcePublic, fallback = 15): number {
  return resource.estimated_minutes ?? resource.duration ?? fallback;
}

/** A set of problems rather than one problem.
 *
 *  These need different arithmetic and different words. "NeetCode 150 -
 *  Arrays & Hashing" is nine problems and about 195 minutes; it cannot be
 *  finished inside a 65-minute block, and showing it as a single line item
 *  worth "~20 min" was the app quietly understating it by ten times. */
const isSet = (resource: ResourcePublic) => resource.is_collection === true;

/** "3 easy, 6 medium" -- only the difficulties that are actually present. */
function mixLabel(resource: ResourcePublic): string | null {
  const mix = resource.difficulty_mix;
  if (!mix) return null;
  const parts = (["easy", "medium", "hard"] as const)
    .map((key) => ({ key, n: mix[key] ?? 0 }))
    .filter(({ n }) => n > 0)
    .map(({ key, n }) => `${n} ${key}`);
  return parts.length > 0 ? parts.join(", ") : null;
}

function hoursAndMinutes(total: number): string {
  if (total < 90) return `${total} min`;
  const hours = Math.floor(total / 60);
  const minutes = total % 60;
  return minutes === 0 ? `${hours} h` : `${hours} h ${minutes} min`;
}

/** Roughly how many of a set's problems fit in the minutes left.
 *
 *  The average is crude on purpose: a set mixes easy and medium problems, and
 *  claiming to know which two you will pick would be a worse kind of guess
 *  than saying "about two". */
function howManyFit(resource: ResourcePublic, roomMinutes: number): number {
  const count = resource.item_count ?? 0;
  if (count <= 0 || roomMinutes <= 0) return 0;
  const average = Math.max(1, Math.round(minutesFor(resource) / count));
  return Math.min(count, Math.floor(roomMinutes / average));
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
      {/* Not a textarea. A fixed `rows` clipped the last line of the prompt in
          the narrower Today column -- the text wrapped past six rows and the
          rest was only reachable by scrolling inside a box that did not look
          scrollable. A <pre> is the whole prompt, always, at any width. */}
      <pre className="mt-3 w-full overflow-x-auto whitespace-pre-wrap break-words rounded-lg border border-[var(--border)] bg-[var(--card-2)] px-3 py-2 font-sans text-xs leading-relaxed text-[var(--foreground)]">
        {prompt}
      </pre>
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
 *  topic, and -- when you are stuck -- a prompt that teaches instead of
 *  answering. */
export function ProblemRow({
  resource,
  index,
  context,
  locked,
  busy,
  onToggle,
  roomMinutes,
}: {
  resource: ResourcePublic;
  index: number;
  context: ProblemContext;
  locked?: boolean;
  busy: boolean;
  onToggle: (id: number, completed: boolean) => void;
  /** Minutes left in this block once reading and the named problems are paid
   *  for. Used to say how much of a multi-problem set fits today. */
  roomMinutes?: number | null;
}) {
  const [stuck, setStuck] = useState(false);
  const [copied, setCopied] = useState(false);
  const tone =
    DIFFICULTY_TONE[(resource.difficulty || "").toLowerCase()] ??
    "text-[var(--muted)] border-[var(--border)]";

  const prompt = useMemo(
    () =>
      buildStuckPrompt({
        problemTitle: resource.title,
        problemUrl: resource.url,
        difficulty: resource.difficulty,
        technique: resource.notes ?? null,
        concepts: resource.required_concepts_covered ?? [],
        whyThisProblem: resource.description,
        topicName: context.topicName,
        sourceTitle: context.sourceTitle,
        sourceUrl: context.sourceUrl,
        language: PROMPT_LANGUAGE,
      }),
    [resource, context],
  );

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(prompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      /* clipboard unavailable -- the textarea below is still selectable */
    }
  };

  const shared = resource.also_in_topics ?? [];
  const items = resource.collection_items ?? [];

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
            {isSet(resource) && (resource.item_count ?? 0) > 1
              ? `${resource.item_count} problems · ~${hoursAndMinutes(minutesFor(resource))} total`
              : `~${minutesFor(resource)} min`}
          </span>
        </div>
      </div>

      {resource.description ? (
        <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">{resource.description}</p>
      ) : null}

      {/* A set is not a task you finish in this block, and the card used to
          imply it was: "NeetCode 150 - Arrays & Hashing" showed "~20 min" over
          nine problems that are three easy and six medium -- about 195
          minutes. Nothing is removed from the set; it is described honestly
          and sliced. */}
      {isSet(resource) && (resource.item_count ?? 0) > 1 ? (
        <p className="mt-2 text-xs text-[var(--muted)]">
          {/* The size and the difficulty spread are already in the
              description, which the server writes from the section's real
              contents. The only thing this line can add is how much of it
              today's block has room for -- and if the answer is none, say so
              rather than leaving the reader to divide 195 by 65. */}
          {roomMinutes == null ? (
            <>
              {mixLabel(resource) ? <>{mixLabel(resource)}. </> : null}A set, not a
              single sitting.
            </>
          ) : howManyFit(resource, roomMinutes) > 0 ? (
            <>
              About {howManyFit(resource, roomMinutes)} of these fit in the {roomMinutes} min
              left in this block — the rest carries over.
            </>
          ) : (
            <>
              Today&apos;s block has no room left for this one; it carries over to the next
              session.
            </>
          )}
          {resource.estimate_method === "unverified_default" ? (
            <> The minute figure is a default, not a measured one.</>
          ) : null}
        </p>
      ) : null}

      {/* The problems, each linking to its own page.
          The card used to offer one button to the whole 150-problem index and
          a sentence telling you to find the right section inside it. NeetCode
          publishes per-problem URLs -- with its own slugs, so "Contains
          Duplicate" is /problems/duplicate-integer/ -- and every one of these
          was fetched and checked against the title the page serves before it
          was written. The label is that served title, because sending you
          looking for "Rotting Oranges" on a page headed "Rotting Fruit" is its
          own small lie. */}
      {items.length > 0 ? (
        <ol className="mt-3 space-y-1">
          {items.map((item, i) => (
            <li key={item.url} className="flex items-baseline gap-2 text-sm">
              <span className="w-5 shrink-0 text-right text-xs text-[var(--muted)]">
                {i + 1}.
              </span>
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
                className="min-w-0 flex-1 truncate text-[var(--accent)] hover:underline"
              >
                {item.title}
              </a>
              {item.difficulty ? (
                <span
                  className={`shrink-0 rounded border px-1.5 py-0.5 text-[11px] font-medium ${
                    DIFFICULTY_TONE[item.difficulty.toLowerCase()] ??
                    "text-[var(--muted)] border-[var(--border)]"
                  }`}
                >
                  {item.difficulty}
                </span>
              ) : null}
              {item.minutes ? (
                <span className="shrink-0 text-xs text-[var(--muted)]">~{item.minutes}m</span>
              ) : null}
            </li>
          ))}
        </ol>
      ) : null}

      {/* The mapping pins 57 problems to more than one topic, and solving one
          counts everywhere it appears. Without saying so, a problem arriving
          already ticked just looks wrong -- and worse, you would skip the
          practice this topic wanted from it without knowing that is the
          choice you were making. */}
      {shared.length > 0 ? (
        <p className="mt-2 text-xs text-[var(--muted)]">
          {resource.completed ? "Solved already — this problem also belongs to " : "Also belongs to "}
          {shared.join(" · ")}
          {resource.completed
            ? ". Worth redoing here if you want it under this topic's angle."
            : ". Solving it once counts for all of them."}
        </p>
      ) : null}

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {resource.url ? (
          <a
            href={resource.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-md bg-[var(--accent)] px-3.5 py-2 text-sm font-medium text-[var(--accent-fg)] hover:bg-[var(--accent-hover)]"
          >
            {items.length > 0 ? "Open the list" : "Solve it"}{" "}
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        ) : null}
        <button
          type="button"
          aria-expanded={stuck}
          onClick={() => setStuck((v) => !v)}
          className="inline-flex items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card-2)] px-3 py-2 text-sm text-[var(--muted)] hover:border-[var(--border-strong)]"
        >
          <Lightbulb className="h-3.5 w-3.5" /> Stuck?
        </button>
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

      {stuck ? (
        <div className="mt-3 rounded-md border border-[var(--border)] bg-[var(--card-2)] p-3">
          <p className="text-sm font-medium">Ask for the reasoning, not the answer</p>
          <p className="mt-1 text-xs leading-relaxed text-[var(--muted)]">
            Paste this into any AI assistant. It asks for the reasoning that makes the technique
            obvious, then pseudocode and a dry run so you see how a plan becomes code — mostly as
            tables, with the {PROMPT_LANGUAGE} only near the end and a “remember this” after it.
            Attempt the problem yourself first.
          </p>
          <textarea
            readOnly
            value={prompt}
            rows={12}
            onFocus={(e) => e.currentTarget.select()}
            className="mt-3 w-full resize-y rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-2 font-mono text-[11px] leading-relaxed text-[var(--foreground)]"
          />
          <div className="mt-3">
            <GhostButton onClick={copy}>
              <Clipboard className="mr-2 h-4 w-4" />
              {copied ? "Copied" : "Copy prompt"}
            </GhostButton>
          </div>
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

  const problemContext = useMemo<ProblemContext>(() => {
    const source = learn[0];
    return {
      topicName: topic?.name ?? "",
      sourceTitle: source?.title ?? null,
      sourceUrl: source?.url ?? null,
    };
  }, [topic, learn]);

  // Problem 1, 2, 3... counts problems only, so a non-problem sitting among
  // them cannot shift the numbering.
  const problemIndex = useMemo(() => {
    const map = new Map<number, number>();
    practice.filter(isCodingProblem).forEach((r, i) => map.set(r.id, i));
    return map;
  }, [practice]);

  const plan = useMemo(() => {
    const readMinutes = learn.reduce((sum, r) => sum + minutesFor(r, 20), 0);
    const singles = practice.filter((r) => !isSet(r));
    const sets = practice.filter(isSet);
    const singleMinutes = singles.reduce((sum, r) => sum + minutesFor(r), 0);
    const setMinutes = sets.reduce((sum, r) => sum + minutesFor(r), 0);

    // A set is open-ended work you take a slice of, so it is charged at what
    // is left of the block rather than at its full size. Summing the full size
    // put every DSA day hours over budget: Arrays & Hashing alone is 195
    // minutes against a 65-minute block, and Trees is 345.
    //
    // With no block to fit into -- browsing a topic rather than working a day
    // -- there is no room to compute, so the honest number is the whole set.
    const room =
      blockMinutes != null ? Math.max(0, blockMinutes - readMinutes - singleMinutes) : null;
    const setSlice = room != null ? Math.min(room, setMinutes) : setMinutes;

    return {
      readMinutes,
      singles,
      sets,
      singleMinutes,
      setMinutes,
      room,
      solveMinutes: singleMinutes + setSlice,
      total: readMinutes + singleMinutes + setSlice,
    };
  }, [learn, practice, blockMinutes]);

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
  const questions = topic.questions ?? [];
  const showRecall = wants("recall") && questions.length > 0;
  const overBudget = blockMinutes != null && plan.total > blockMinutes;

  // `sections` is the running order, not just a filter. It used to be read as
  // a set and rendered in a hardcoded learn/practice/build/recall order, so a
  // block could not say "questions first, then the exercises" however it asked.
  // Numbered from the steps this block actually shows, so a practice-only
  // block starts at 1 rather than skipping to 2.
  // What to watch for while reading. The contract already carries it and the
  // topic page shows it under FOCUS; a block that only offered "Open source"
  // sent you to that page to find out what the reading was even for.
  const contract = (topic.study_contract ?? null) as {
    focus_concepts?: unknown;
    learn?: { instructions?: unknown } | null;
  } | null;
  const focusConcepts = Array.isArray(contract?.focus_concepts)
    ? (contract.focus_concepts as unknown[]).filter(
        (c): c is string => typeof c === "string" && c.trim().length > 0,
      )
    : [];

  const available: Record<WorkSection, boolean> = {
    learn: showLearn,
    practice: showPractice,
    build: showBuild,
    recall: showRecall,
  };
  const steps: WorkSection[] = sections.filter(
    (section, i) => sections.indexOf(section) === i && available[section],
  );
  const stepLabel = (section: WorkSection) => steps.indexOf(section) + 1;

  // One step's markup, looked up by name. Rendered through `steps`, so the
  // running order is whatever the block asked for rather than the order they
  // happen to sit in this file.
  const panel = (section: WorkSection) => {
    switch (section) {
      case "learn":
        return (
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
          {focusConcepts.length > 0 ? (
            <div className="mt-3 rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">
                Watch for these while you read
              </p>
              <ul className="mt-2 flex flex-wrap gap-1.5">
                {focusConcepts.map((concept) => (
                  <li
                    key={concept}
                    className="rounded-md border border-[var(--border)] bg-[var(--card-2)] px-2 py-0.5 text-xs"
                  >
                    {concept}
                  </li>
                ))}
              </ul>
              <p className="mt-2 text-xs text-[var(--muted)]">
                If you cannot explain each of these afterwards, you have not finished the reading.
              </p>
            </div>
          ) : null}
        </section>
        );
      case "practice":
        return (
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
              {practice.map((resource) =>
                isCodingProblem(resource) ? (
                  <ProblemRow
                    key={resource.id}
                    resource={resource}
                    index={problemIndex.get(resource.id) ?? 0}
                    context={problemContext}
                    locked={topic.locked}
                    busy={busy === `resource-${resource.id}`}
                    onToggle={toggleResource}
                    roomMinutes={plan.room}
                  />
                ) : (
                  <li key={resource.id}>
                    <SourceResourceCard
                      resource={resource}
                      locked={topic.locked}
                      onToggle={toggleResource}
                    />
                  </li>
                ),
              )}
            </ul>
          ) : topic.locked ? null : (
            <div className="mt-3">
              <PracticePrompt topic={topic} />
            </div>
          )}
        </section>
        );
      case "build":
        return (
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
        );
      case "recall":
        return (
        <section>
          <p className="text-sm font-semibold">
            {stepLabel("recall")}. Check you actually have it
            <span className="ml-2 text-xs font-normal text-[var(--muted)]">
              {questions.length} question{questions.length === 1 ? "" : "s"} · recall, not recognition
            </span>
          </p>
          <div className="mt-3">
            <TopicQuestions questions={questions} />
          </div>
        </section>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {error ? <p className="text-sm text-[var(--warn)]">{error}</p> : null}

      {showLearn && showPractice ? (
        <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">
            Plan for this block
          </p>
          {/* "solve 2 problems" counted a nine-problem set as one problem and
              charged it twenty minutes. Named problems and open-ended sets are
              now counted separately, because they are different promises: a
              problem you finish today, a set you make progress in. */}
          <p className="mt-1 text-sm">
            Read ~{plan.readMinutes} min
            {plan.singles.length > 0 ? (
              <>
                , then solve {plan.singles.length}{" "}
                {plan.singles.length === 1 ? "problem" : "problems"} ~{plan.singleMinutes} min
              </>
            ) : null}
            {plan.sets.length > 0 ? (
              <>
                . {plan.sets.length === 1 ? "There is also a problem set" : "There are also problem sets"}{" "}
                ({hoursAndMinutes(plan.setMinutes)} of work in all)
                {plan.room == null ? null : plan.room > 0 ? (
                  <> — about {plan.room} min of it fits after that</>
                ) : (
                  <> — the named problems already fill this block, so they carry over</>
                )}
              </>
            ) : null}
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

      {steps.map((section) => (
        <Fragment key={section}>{panel(section)}</Fragment>
      ))}


      <Link
        href={`/learn/topic/${topicId}`}
        className="inline-flex items-center gap-1.5 text-xs text-[var(--muted)] underline hover:text-[var(--foreground)]"
      >
        Open the full topic <ArrowRight className="h-3 w-3" />
      </Link>
    </div>
  );
}
