"use client";

import { GhostButton, PrimaryButton } from "@/components/study-ui";
import type { ResourcePublic } from "@/lib/curriculum";

export function SourceResourceCard({
  resource,
  locked,
  onToggle,
}: {
  resource: ResourcePublic;
  locked?: boolean;
  onToggle?: (id: number, completed: boolean) => void;
}) {
  const url = resource.url;
  const playlist = resource.is_playlist;
  const embeddable = Boolean(resource.embeddable && resource.video_id && !playlist);
  void (resource.exactness || playlist);

  // Where "Watch on YouTube" actually goes. It used to reuse `url`, which is
  // the row's own page and is not always the video: one resource embeds a
  // YouTube lecture but carries a GeeksforGeeks article as its url, so both
  // buttons opened GFG and the one promising YouTube was simply false.
  const watchUrl = resource.video_id
    ? `https://www.youtube.com/watch?v=${resource.video_id}`
    : null;
  // On the other 45 video rows the url IS the video, so a separate button for
  // it was the same destination twice under two different labels.
  const pageIsTheVideo = Boolean(url && resource.video_id && url.includes(resource.video_id));
  const hostLabel = (() => {
    if (!url) return null;
    try {
      return new URL(url).hostname.replace(/^www\./, "");
    } catch {
      return null;
    }
  })();

  const boundary = resource.lecture || resource.section ? `${resource.lecture ? resource.lecture : ""}${resource.lecture && resource.section ? " · " : ""}${resource.section ?? ""}` : null;
  const minutes = resource.duration ? Math.round(resource.duration * 60) : null;
  return (
    <article className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium uppercase tracking-[0.12em] text-[var(--muted)]">
            {resource.role || "RESOURCE"}
            {resource.provider ? ` · ${resource.provider}` : ""}
            {resource.resource_type ? ` · ${resource.resource_type}` : ""}
            {minutes ? ` · ~${minutes} min` : ""}
          </p>
          <h3 className="mt-1 font-medium leading-tight">{resource.title}</h3>
          {boundary ? <p className="mt-1 text-xs font-medium text-[var(--foreground)]">Focus: {boundary}</p> : null}
          {/* The boundary is already on the "Focus:" line above; repeating it
              here printed the same section twice under the title. */}
          <p className="mt-1 text-xs text-[var(--muted)]">
            {resource.provider || "Official source"}
            {minutes ? ` · ${minutes} min` : ""}
          </p>
        </div>
        <span className="shrink-0 text-xs text-[var(--muted)]">{resource.completed ? "Consumed" : "Not consumed"}</span>
      </div>

      {resource.role === "PRACTICE" && url && resource.exact === false ? (
        <p className="mt-2 text-sm text-[var(--muted)]">Practice collection — exact problem mapping not verified.</p>
      ) : null}

      {!url ? (
        <p className="mt-3 text-sm text-[var(--warn)]">
          Exact source is unresolved. Engineering OS will not invent a URL.
        </p>
      ) : null}

      {embeddable ? (
        <div className="mt-3 aspect-video overflow-hidden rounded-lg bg-black">
          <iframe
            title={resource.title}
            className="h-full w-full"
            src={`https://www.youtube.com/embed/${resource.video_id}`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      ) : null}

      {embeddable && watchUrl ? (
        <div className="mt-3 flex flex-wrap gap-2">
          <PrimaryButton href={watchUrl}>Watch on YouTube</PrimaryButton>
          {/* A second button only when it is a second destination, named by its
              host -- the provider on a row like this one is the YouTube channel
              and would mislabel the page it points at. */}
          {url && !pageIsTheVideo ? (
            <GhostButton href={url}>Open {hostLabel ?? "the source page"}</GhostButton>
          ) : null}
        </div>
      ) : url ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {playlist ? (
            <GhostButton href={url}>Open playlist</GhostButton>
          ) : (
            <PrimaryButton href={url}>Open official resource</PrimaryButton>
          )}
        </div>
      ) : null}

      {onToggle ? (
        <div className="mt-3">
          <GhostButton disabled={locked} onClick={() => onToggle(resource.id, !resource.completed)}>
            {resource.completed ? "Mark source not consumed" : "Mark source consumed"}
          </GhostButton>
          {locked ? <p className="mt-1 text-xs text-[var(--muted)]">Locked — complete prerequisites first.</p> : null}
          <p className="mt-1 text-xs text-[var(--muted)]">Consuming a source is evidence only — not mastery.</p>
        </div>
      ) : null}
    </article>
  );
}
