"use client";

import { useCallback, useMemo, useState } from "react";
import { Check, RotateCcw, X } from "lucide-react";
import { api, errorMessage } from "@/lib/api";
import type { QuestionPublic } from "@/lib/curriculum";

/* -------------------------------------------------------------------------
 * Retrieval practice on the question bank.
 *
 * 1,355 questions with written explanations already sat in the database, and
 * the API already served them -- nothing rendered them, so not one had ever
 * been attempted. Reading a source and ticking "consumed" is recognition; it
 * is entirely possible to feel fluent about something you cannot produce. This
 * is the only place in the app that asks you to produce it.
 *
 * The answer is deliberately not in the page before you commit: the public
 * serializer withholds it, and it arrives in the response to the attempt. So
 * there is nothing to peek at in devtools, and the explanation lands at the
 * one moment it is worth reading -- straight after you have been wrong.
 * ---------------------------------------------------------------------- */

type Outcome = {
  correct: boolean;
  answer: string;
  explanation: string | null;
};

function QuestionCard({
  question,
  position,
  onOutcome,
}: {
  question: QuestionPublic;
  position: number;
  onOutcome: (id: number, correct: boolean) => void;
}) {
  const [picked, setPicked] = useState<string | null>(null);
  const [outcome, setOutcome] = useState<Outcome | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const attempt = async (option: string) => {
    if (busy || outcome) return;
    setPicked(option);
    setBusy(true);
    setError(null);
    try {
      const result = await api<Outcome>(`/api/questions/${question.id}/attempt`, {
        method: "POST",
        body: JSON.stringify({ selected: option }),
      });
      setOutcome(result);
      onOutcome(question.id, result.correct);
    } catch (err) {
      setPicked(null);
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const retry = () => {
    setPicked(null);
    setOutcome(null);
    setError(null);
  };

  const optionTone = (option: string) => {
    if (!outcome) {
      return picked === option
        ? "border-[var(--accent)] bg-[var(--accent-soft)]"
        : "border-[var(--border)] hover:border-[var(--border-strong)]";
    }
    if (option === outcome.answer) return "border-[var(--ok)] bg-[var(--ok-soft)]";
    if (option === picked) return "border-[var(--danger)] bg-[var(--warn-soft)]";
    return "border-[var(--border)] opacity-60";
  };

  return (
    <li className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-4">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium">
          <span className="text-[var(--muted)]">{position}. </span>
          {question.question}
        </p>
        {question.attempt_count > 0 && !outcome ? (
          <span className="shrink-0 rounded border border-[var(--border)] px-2 py-0.5 text-xs text-[var(--muted)]">
            {question.last_correct ? "got it last time" : "missed last time"}
          </span>
        ) : null}
      </div>

      <ul className="mt-3 space-y-2">
        {question.options.map((option) => (
          <li key={option}>
            <button
              type="button"
              disabled={busy || outcome !== null}
              onClick={() => attempt(option)}
              className={`flex w-full items-start gap-2 rounded-md border px-3 py-2 text-left text-sm transition-colors disabled:cursor-default ${optionTone(option)}`}
            >
              {outcome ? (
                option === outcome.answer ? (
                  <Check className="mt-0.5 h-4 w-4 shrink-0 text-[var(--ok)]" />
                ) : option === picked ? (
                  <X className="mt-0.5 h-4 w-4 shrink-0 text-[var(--danger)]" />
                ) : (
                  <span className="mt-0.5 h-4 w-4 shrink-0" />
                )
              ) : (
                <span className="mt-0.5 h-4 w-4 shrink-0" />
              )}
              <span>{option}</span>
            </button>
          </li>
        ))}
      </ul>

      {error ? <p className="mt-2 text-sm text-[var(--warn)]">{error}</p> : null}

      {outcome ? (
        <div className="mt-3 rounded-md border border-[var(--border)] bg-[var(--card-2)] p-3">
          <p className="text-sm font-medium">
            {outcome.correct ? "Correct." : "Not quite."}
          </p>
          {outcome.explanation ? (
            <p className="mt-1 text-sm leading-relaxed text-[var(--muted)]">
              {outcome.explanation}
            </p>
          ) : null}
          <button
            type="button"
            onClick={retry}
            className="mt-3 inline-flex items-center gap-1.5 text-xs text-[var(--muted)] underline hover:text-[var(--foreground)]"
          >
            <RotateCcw className="h-3 w-3" /> Try it again
          </button>
        </div>
      ) : null}
    </li>
  );
}

/** Retrieval practice for one topic. Renders nothing when the topic has no
 *  questions, so callers can place it unconditionally. */
export function TopicQuestions({ questions }: { questions: QuestionPublic[] }) {
  const [results, setResults] = useState<Record<number, boolean>>({});

  const onOutcome = useCallback((id: number, correct: boolean) => {
    setResults((prev) => ({ ...prev, [id]: correct }));
  }, []);

  const { answered, correct } = useMemo(() => {
    const values = Object.values(results);
    return { answered: values.length, correct: values.filter(Boolean).length };
  }, [results]);

  if (questions.length === 0) return null;

  return (
    <div>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p className="text-xs text-[var(--muted)]">
          Answer from memory before you look anything up — that attempt is what makes it stick.
        </p>
        {answered > 0 ? (
          <p className="text-xs font-medium tabular-nums">
            {correct} of {answered} correct
            {answered < questions.length ? ` · ${questions.length - answered} left` : ""}
          </p>
        ) : null}
      </div>
      <ul className="mt-3 space-y-3">
        {questions.map((question, i) => (
          <QuestionCard
            key={question.id}
            question={question}
            position={i + 1}
            onOutcome={onOutcome}
          />
        ))}
      </ul>
    </div>
  );
}
