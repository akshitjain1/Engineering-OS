"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight, Check, Clipboard, Loader2 } from "lucide-react";
import { SourceResourceCard } from "@/components/source-resource";
import { GhostButton } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import type { TopicNode } from "@/lib/curriculum";

/* -------------------------------------------------------------------------
 * The Practice and Build work for a topic, rendered wherever you already are.
 * Same endpoints as the topic page, so anything marked done here is done
 * there too. Lives in its own file because both the topic page and the day
 * runner render it.
 * ---------------------------------------------------------------------- */

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

/** Practice sources and build exercises for one topic, self-loading. Renders
 *  nothing but a loading line until the topic arrives. */
export function TopicWorkPanel({
  topicId,
  show = "both",
}: {
  topicId: number;
  /** Practice blocks want practice first; build blocks only want the build. */
  show?: "both" | "practice" | "build";
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

  const practice = topic.resources_by_role?.PRACTICE || [];
  const build = topic.implement || topic.exercises || [];
  const wantPractice = show !== "build";
  const wantBuild = show !== "practice";

  return (
    <div className="space-y-5">
      {error ? <p className="text-sm text-[var(--warn)]">{error}</p> : null}

      {wantPractice ? (
        <section>
          <p className="text-sm font-semibold">Practice</p>
          <p className="mt-0.5 text-xs text-[var(--muted)]">
            Do the work on the official platform — not an in-app quiz.
          </p>
          {practice.length > 0 ? (
            <div className="mt-3 space-y-3">
              {practice.map((resource) => (
                <SourceResourceCard
                  key={resource.id}
                  resource={resource}
                  locked={topic.locked}
                  onToggle={toggleResource}
                />
              ))}
            </div>
          ) : topic.locked ? null : (
            <div className="mt-3">
              <PracticePrompt topic={topic} />
            </div>
          )}
        </section>
      ) : null}

      {wantBuild ? (
        <section>
          <p className="text-sm font-semibold">Build</p>
          <p className="mt-0.5 text-xs text-[var(--muted)]">
            One concrete implementation action — then mark it done.
          </p>
          {build.length === 0 ? (
            <p className="mt-2 text-sm text-[var(--muted)]">
              No implementation task is mapped for this topic yet.
            </p>
          ) : (
            <div className="mt-3 space-y-3">
              {build.map((exercise) => (
                <div
                  key={exercise.id}
                  className="rounded-lg border border-[var(--border)] bg-[var(--card-2)] p-4"
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
          )}
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
