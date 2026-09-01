"use client";

import { useEffect, useState } from "react";
import { Banner, LoadingLine, Page, PageTitle } from "@/components/study-ui";
import { api, errorMessage } from "@/lib/api";

type StudySettings = {
  weekday_capacity_minutes: number;
  weekend_capacity_minutes: number;
  timezone: string;
  revision_weighted: boolean;
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<StudySettings | null>(null);
  const [weekday, setWeekday] = useState(90);
  const [weekend, setWeekend] = useState(180);
  const [revisionWeighted, setRevisionWeighted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<StudySettings>("/api/study-settings")
      .then((payload) => {
        setSettings(payload);
        setWeekday(payload.weekday_capacity_minutes);
        setWeekend(payload.weekend_capacity_minutes);
        setRevisionWeighted(payload.revision_weighted);
      })
      .catch((err) => setError(errorMessage(err)));
  }, []);

  async function save() {
    setBusy(true);
    setSaved(false);
    try {
      const payload = await api<StudySettings>("/api/study-settings", {
        method: "PUT",
        body: JSON.stringify({
          weekday_capacity_minutes: weekday,
          weekend_capacity_minutes: weekend,
          revision_weighted: revisionWeighted,
        }),
      });
      setSettings(payload);
      setSaved(true);
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Page>
      <PageTitle
        kicker="Settings"
        title="Study capacity"
        description="Weekday and weekend minute budgets drive Today’s plan when you generate without picking a preset."
      />
      {error ? <Banner>{error}</Banner> : null}
      {!settings ? (
        <LoadingLine />
      ) : (
        <div className="max-w-md space-y-4 rounded-lg border border-[var(--border)] bg-[var(--card)] p-5">
          <label className="block text-sm">
            <span className="text-[var(--muted)]">Weekday minutes</span>
            <input
              type="number"
              min={15}
              max={360}
              value={weekday}
              onChange={(e) => setWeekday(Number(e.target.value))}
              className="mt-1 w-full rounded-md border border-[var(--border)] bg-[var(--background)] px-3 py-2"
            />
          </label>
          <label className="block text-sm">
            <span className="text-[var(--muted)]">Weekend minutes</span>
            <input
              type="number"
              min={15}
              max={480}
              value={weekend}
              onChange={(e) => setWeekend(Number(e.target.value))}
              className="mt-1 w-full rounded-md border border-[var(--border)] bg-[var(--background)] px-3 py-2"
            />
          </label>
          <div className="border-t border-[var(--border)] pt-4">
            <label className="flex cursor-pointer items-start gap-3 text-sm">
              <input
                type="checkbox"
                checked={revisionWeighted}
                onChange={(e) => setRevisionWeighted(e.target.checked)}
                className="mt-0.5 size-4 shrink-0 accent-[var(--accent)]"
              />
              <span>
                <span className="font-medium">Revision-weighted day</span>
                <span className="mt-1 block text-xs text-[var(--muted)]">
                  For re-covering material you already know. Shrinks the LEARN block to
                  about 60% and gives the surplus to DSA, which is first-time material.
                  Practice and reflection are unchanged.
                </span>
              </span>
            </label>
          </div>
          <p className="text-xs text-[var(--muted)]">Timezone: {settings.timezone}</p>
          <button
            type="button"
            disabled={busy}
            onClick={save}
            className="rounded-md bg-[var(--accent)] px-3 py-2 text-sm font-medium text-[var(--accent-fg)]"
          >
            Save settings
          </button>
          {saved ? <p className="text-xs text-[var(--muted)]">Saved.</p> : null}
        </div>
      )}
    </Page>
  );
}
