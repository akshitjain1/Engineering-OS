"use client";

import { useEffect, useState } from "react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";
import { cn } from "@/lib/utils";

type Project = {
  id: number;
  slug: string;
  title: string;
  goal?: string | null;
  level: number;
  difficulty: string;
  estimated_hours: number;
  prerequisites: string[];
  milestones: string[];
  deliverable?: string | null;
  state: string;
};

type ProjectBuckets = {
  available: Project[];
  locked: Project[];
  in_progress: Project[];
  completed: Project[];
};

const SECTIONS: { key: keyof ProjectBuckets; label: string }[] = [
  { key: "in_progress", label: "In progress" },
  { key: "available", label: "Available" },
  { key: "locked", label: "Locked" },
  { key: "completed", label: "Completed" },
];

export default function ProjectsPage() {
  const [data, setData] = useState<ProjectBuckets | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<number | null>(null);

  const load = () =>
    api<ProjectBuckets>("/api/projects")
      .then((payload) => {
        setData(payload);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)));

  useEffect(() => {
    load();
  }, []);

  async function act(id: number, action: "start" | "complete") {
    setBusy(id);
    try {
      await api(`/api/projects/${id}/${action}`, { method: "POST" });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(null);
    }
  }

  return (
    <Page>
      <PageTitle
        kicker="Projects"
        title="Build when unlocked"
        description="Projects open after prerequisite topics are lesson-complete. Start with small L1 builds, then level up."
      />
      <div className="mb-6 flex items-center gap-2 text-xs font-medium tracking-wider text-[var(--muted)]">
        <span className="rounded bg-[var(--card-2)] px-2 py-1">L1</span> → <span className="rounded bg-[var(--card-2)] px-2 py-1">L2</span> → <span className="rounded bg-[var(--card-2)] px-2 py-1">L3</span> → <span className="rounded bg-[var(--card-2)] px-2 py-1">L4</span>
      </div>
      {error ? <Banner>{error}</Banner> : null}
      {!data ? (
        <LoadingLine />
      ) : (
        <div className="space-y-8">
          {SECTIONS.map(({ key, label }) => {
            const rows = data[key] ?? [];
            if (!rows.length && key !== "available") return null;
            return (
              <section key={key} className="space-y-3">
                <h2 className="text-sm font-semibold tracking-tight">
                  {label}
                  <span className="ml-2 font-normal text-[var(--muted)]">{rows.length}</span>
                </h2>
                {!rows.length ? (
                  <EmptyState title="None yet" body="Complete topic lessons to unlock the first builds." />
                ) : (
                  <ul className="space-y-3">
                    {rows.map((project) => (
                      <li
                        key={project.id}
                        className={cn(
                          "rounded-lg border border-[var(--border)] bg-[var(--card)] p-4",
                          key === "locked" && "opacity-70",
                        )}
                      >
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <p className="text-sm font-medium">
                              L{project.level} · {project.title}
                            </p>
                            <p className="mt-1 text-sm text-[var(--muted)]">{project.goal}</p>
                            <p className="mt-2 text-xs text-[var(--muted)]">
                              ~{project.estimated_hours}h · {project.difficulty}
                              {project.prerequisites?.length
                                ? ` · needs ${project.prerequisites.join(", ")}`
                                : ""}
                            </p>
                            {project.deliverable ? (
                              <p className="mt-1 text-xs text-[var(--muted)]">Deliverable: {project.deliverable}</p>
                            ) : null}
                          </div>
                          <div className="flex gap-2">
                            {key === "available" ? (
                              <button
                                type="button"
                                disabled={busy === project.id}
                                className="rounded-md bg-[var(--accent)] px-3 py-1.5 text-xs font-medium text-[var(--accent-fg)]"
                                onClick={() => act(project.id, "start")}
                              >
                                Start
                              </button>
                            ) : null}
                            {key === "in_progress" ? (
                              <button
                                type="button"
                                disabled={busy === project.id}
                                className="rounded-md border border-[var(--border)] px-3 py-1.5 text-xs"
                                onClick={() => act(project.id, "complete")}
                              >
                                Mark complete
                              </button>
                            ) : null}
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            );
          })}
        </div>
      )}
    </Page>
  );
}
