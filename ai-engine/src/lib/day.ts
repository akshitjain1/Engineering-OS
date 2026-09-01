import { api } from "@/lib/api";

export type ActivityType =
  | "REVIEW"
  | "LEARN"
  | "PRACTICE"
  | "DSA"
  | "BUILD"
  | "REFLECT";

export type ItemStatus = "pending" | "active" | "done" | "skipped";

export type DayResource = {
  id: number | null;
  title: string | null;
  provider: string | null;
  url: string | null;
  kind: string | null;
};

export type DayItem = {
  id: number;
  position: number;
  activity_type: ActivityType;
  title: string;
  subtitle: string | null;
  why: string | null;
  how: string | null;
  topic_id: number | null;
  topic_slug: string | null;
  domain: string | null;
  resource: DayResource | null;
  planned_minutes: number;
  actual_minutes: number;
  status: ItemStatus;
  started_at: string | null;
  completed_at: string | null;
  note: string | null;
};

export type Day = {
  plan_date: string;
  mode: "weekday" | "weekend";
  items: DayItem[];
  current_item_id: number | null;
  totals: {
    planned_minutes: number;
    logged_minutes: number;
    items_total: number;
    items_done: number;
    complete: boolean;
  };
  journal: { learned: string | null; struggled: string | null; tomorrow: string | null } | null;
};

export type StepResult = { item: DayItem; next: DayItem | null };

export const getDay = () => api<Day>("/api/day");

export const generateDay = (minutes?: number, force = false) =>
  api<Day>("/api/day/generate", {
    method: "POST",
    body: JSON.stringify({ minutes: minutes ?? null, force }),
  });

export const startItem = (id: number) =>
  api<DayItem>(`/api/day/item/${id}/start`, { method: "POST" });

export const completeItem = (
  id: number,
  payload: { minutes?: number; note?: string; complete_topic?: boolean } = {},
) => api<StepResult>(`/api/day/item/${id}/complete`, { method: "POST", body: JSON.stringify(payload) });

export const skipItem = (id: number, reason?: string) =>
  api<StepResult>(`/api/day/item/${id}/skip`, {
    method: "POST",
    body: JSON.stringify({ reason: reason ?? null }),
  });

export const saveJournal = (payload: {
  learned?: string;
  struggled?: string;
  tomorrow?: string;
}) => api<unknown>("/api/day/journal", { method: "PUT", body: JSON.stringify(payload) });

/** Copy that explains each block in the user's own terms, not the system's. */
export const ACTIVITY_COPY: Record<ActivityType, { label: string; blurb: string }> = {
  REVIEW: { label: "Recall", blurb: "Retrieve older material before anything new" },
  LEARN: { label: "Learn", blurb: "New topic from your main track" },
  PRACTICE: { label: "Practice", blurb: "Use what you just learned" },
  DSA: { label: "DSA", blurb: "Runs every day on its own track" },
  BUILD: { label: "Build", blurb: "Ship something small that runs" },
  REFLECT: { label: "Reflect", blurb: "Close the day in writing" },
};

/** Minutes elapsed since the block was started, from the server timestamp so a
 *  page refresh does not reset the clock. */
export function elapsedMinutes(item: DayItem): number {
  if (!item.started_at) return 0;
  const started = new Date(item.started_at).getTime();
  if (Number.isNaN(started)) return 0;
  return Math.max(0, Math.round((Date.now() - started) / 60000));
}
