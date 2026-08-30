"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Banner, EmptyState, LoadingLine, Page, PageTitle, ProgressBar } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";

type TrackNext = { topic_id: number; slug: string; name: string; locked: boolean } | null;
type TrackRow = { key: string; label: string; total: number; complete: number; next: TrackNext };

export default function TracksPage() {
  const [tracks, setTracks] = useState<TrackRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { api<{ tracks: TrackRow[] }>("/api/study-tracks").then((p) => setTracks(p.tracks)).catch((err) => setError(errorMessage(err))); }, []);
  return (
    <Page wide>
      <PageTitle kicker="Tracks" title="Study lanes" description="Progress by lane — completion counts, not percentages." />
      {error ? <Banner>{error}</Banner> : null}
      {!tracks ? <LoadingLine /> : !tracks.length ? <EmptyState title="No tracks yet" body="Import curriculum to populate track progress." /> : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {tracks.map((track) => (
            <section key={track.key} className="border border-[var(--border)] bg-[var(--card)] p-5">
              <div className="flex items-baseline justify-between gap-2"><h2 className="text-sm font-bold">{track.label}</h2><p className="text-xs text-[var(--muted)]">{track.complete}/{track.total} complete</p></div>
              <div className="mt-3"><ProgressBar value={track.complete} max={track.total} /></div>
              <p className="mt-2 text-xs text-[var(--muted)]">{track.total ? Math.round((track.complete/track.total)*100) : 0}% · {track.total - track.complete} remaining</p>
              {track.next ? <div className="mt-4 border-t border-[var(--border)] pt-3"><p className="text-xs uppercase tracking-widest text-[var(--muted)]">Current</p><p className="mt-1 text-sm font-medium">{track.next.name}</p>{track.next.locked ? <p className="mt-1 text-xs text-[var(--warn)]">Locked — complete prerequisites</p> : <Link href={`/learn/topic/${track.next.topic_id}`} className="mt-2 inline-flex text-xs font-medium text-[var(--accent)] hover:underline">Continue →</Link>}</div> : <p className="mt-4 text-xs text-[var(--muted)]">Lane complete.</p>}
            </section>
          ))}
        </div>
      )}
    </Page>
  );
}
