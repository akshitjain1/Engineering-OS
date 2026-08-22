"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { PrerequisiteList } from "@/components/prerequisite-list";
import { SourceResourceCard } from "@/components/source-resource";
import { Banner, GhostButton, LoadingLine, Page, PrimaryButton } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import type { ExercisePublic, LessonDetail } from "@/lib/curriculum";

function ExerciseCard({
  exercise,
  locked,
  onToggle,
}: {
  exercise: ExercisePublic;
  locked: boolean;
  onToggle: (id: number, completed: boolean) => void;
}) {
  return (
    <article className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-medium">{exercise.title}</h3>
          <p className="text-xs text-[var(--muted)]">{exercise.difficulty || "exercise"}</p>
        </div>
        <span className="text-xs text-[var(--muted)]">{exercise.completed ? "Complete" : "Not started"}</span>
      </div>
      {exercise.description ? <p className="mt-2 text-sm text-[var(--muted)]">{exercise.description}</p> : null}
      <div className="mt-3">
        <GhostButton disabled={locked} onClick={() => onToggle(exercise.id, !exercise.completed)}>
          {exercise.completed ? "Mark exercise not done" : "Start exercise"}
        </GhostButton>
      </div>
    </article>
  );
}

export default function LessonDetailPage() {
  const params = useParams<{ id: string }>();
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = () => {
    if (!params.id) return;
    api<LessonDetail>(`/api/lesson/${params.id}`)
      .then((data) => {
        setLesson(data);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  const setLessonState = async (state: "not_started" | "in_progress" | "completed") => {
    if (!lesson) return;
    setBusy(true);
    try {
      await api(`/api/progress/lesson/${lesson.id}?state=${state}`, { method: "POST" });
      load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const toggleExercise = async (exerciseId: number, completed: boolean) => {
    try {
      if (completed) {
        await api(`/api/exercise/${exerciseId}/complete`, { method: "POST" });
      } else {
        await api(`/api/progress/exercise/${exerciseId}`, {
          method: "POST",
          body: JSON.stringify({ completed }),
        });
      }
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  return (
    <Page>
      <p className="text-sm text-[var(--muted)]">
        <Link href="/roadmap" className="underline">
          Back to Roadmap
        </Link>
        {lesson ? (
          <>
            {" · "}
            <Link href={`/learn/topic/${lesson.topic_id}`} className="underline">
              {lesson.breadcrumb.topic_name}
            </Link>
          </>
        ) : null}
      </p>

      {error ? <Banner>{error}</Banner> : null}
      {!lesson && !error ? <LoadingLine label="Loading lesson…" /> : null}

      {lesson ? (
        <>
          <header className="mt-5">
            <h1 className="text-2xl font-semibold tracking-tight">{lesson.title}</h1>
            <p className="mt-2 text-sm text-[var(--muted)]">
              {lesson.locked ? "LOCKED" : lesson.completion_status.replace("_", " ")}
              {lesson.hours_estimated ? ` · ~${Math.round(lesson.hours_estimated * 60)} min` : ""}
            </p>
          </header>
          {lesson.description ? <p className="mt-3 text-sm leading-relaxed text-[var(--muted)]">{lesson.description}</p> : null}

          {lesson.locked ? (
            <div className="mt-6 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
              <p className="font-medium">This lesson is locked.</p>
              <PrerequisiteList items={lesson.prerequisites} message={lesson.lock_message} />
            </div>
          ) : (
            <div className="mt-6 flex flex-wrap gap-2">
              <GhostButton disabled={busy} onClick={() => setLessonState("in_progress")}>
                Mark in progress
              </GhostButton>
              <PrimaryButton disabled={busy} onClick={() => setLessonState("completed")}>
                Mark lesson complete
              </PrimaryButton>
            </div>
          )}

          <section className="mt-10">
            <h2 className="text-sm font-semibold">Learn</h2>
            {lesson.resources.length === 0 ? (
              <p className="mt-3 text-sm text-[var(--muted)]">No resources yet.</p>
            ) : (
              <div className="mt-3 space-y-3">
                {lesson.resources.map((resource) => (
                  <SourceResourceCard
                    key={resource.id}
                    resource={resource}
                    locked={lesson.locked}
                    onToggle={async (id, completed) => {
                      try {
                        await api(`/api/progress/resource/${id}`, {
                          method: "POST",
                          body: JSON.stringify({ completed }),
                        });
                        load();
                      } catch (err) {
                        setError(errorMessage(err));
                      }
                    }}
                  />
                ))}
              </div>
            )}
          </section>

          <section className="mt-10">
            <h2 className="text-sm font-semibold">Implement</h2>
            {lesson.exercises.length === 0 ? (
              <p className="mt-3 text-sm text-[var(--muted)]">No exercises yet.</p>
            ) : (
              <div className="mt-3 space-y-3">
                {lesson.exercises.map((exercise) => (
                  <ExerciseCard
                    key={exercise.id}
                    exercise={exercise}
                    locked={lesson.locked}
                    onToggle={toggleExercise}
                  />
                ))}
              </div>
            )}
          </section>
        </>
      ) : null}
    </Page>
  );
}