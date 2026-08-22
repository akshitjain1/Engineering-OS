"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";

type TrackNext = {
  topic_id: number;
  slug: string;
  name: string;
  locked: boolean;
} | null;

type TrackRow = {
  key: string;
  label: string;
  total: number;
  complete: number;
  next: TrackNext;
};

export default function TracksPage() {
  const [tracks, setTracks] = useState<TrackRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<{ tracks: TrackRow[] }>("/api/study-tracks")
      .then((payload) => {
        setTracks(payload.tracks);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)));
  }, []);

  return (
    <Page>
      <PageTitle
        kicker="Tracks"
        title="Study lanes"
        description="Core spine, specialization, always-on skills, and build work — completion counts, not mastery percentages."
      />
      {error ? <Banner>{error}</Banner> : null}
      {!tracks ? (
        <LoadingLine />
      ) : !tracks.length ? (
        <EmptyState title="No tracks yet" body="Import curriculum to populate track progress." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {tracks.map((track) => (
            <section key={track.key} className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-4">
              <div className="flex items-baseline justify-between gap-2">
                <h2 className="text-sm font-semibold">{track.label}</h2>
                <p className="text-xs text-[var(--muted)]">
                  {track.complete}/{track.total} complete
                </p>
              </div>
              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-[var(--card-2)]">
                <div
                  className="h-full rounded-full bg-[var(--accent)]"
                  style={{
                    width: `${track.total ? Math.round((track.complete / track.total) * 100) : 0}%`,
                  }}
                />
              </div>
              {track.next ? (
                <div className="mt-4">
                  <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Next</p>
                  <p className="mt-1 text-sm">{track.next.name}</p>
                  {track.next.locked ? (
                    <p className="mt-1 text-xs text-[var(--warn)]">Locked until prerequisites complete</p>
                  ) : (
                    <Link
                      href={`/learn/topic/${track.next.topic_id}`}
                      className="mt-2 inline-block text-xs underline"
                    >
                      Open topic
                    </Link>
                  )}
                </div>
              ) : (
                <p className="mt-4 text-xs text-[var(--muted)]">Lane complete for now.</p>
              )}
            </section>
          ))}
        </div>
      )}
    </Page>
  );
}
