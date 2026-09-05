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
  /** True when no plan exists yet. GET /api/day never writes, so only /today
   *  acts on this -- reading the day from anywhere else creates nothing. */
  needs_generation: boolean;
  items: DayItem[];
  current_item_id: number | null;
  totals: {
    planned_minutes: number;
    logged_minutes: number;
    items_total: number;
    items_done: number;
    complete: boolean;
  };
  journal: {
    learned: string | null;
    struggled: string | null;
    tomorrow: string | null;
    /** Project or job work done today; feeds the study log's projects section. */
    built: string | null;
  } | null;
};

export type StepResult = { item: DayItem; next: DayItem | null };

/** Day plus what the extend appended. first_new_item_id is null when the
 *  curriculum is exhausted, in which case message says so. */
export type ExtendResult = Day & {
  first_new_item_id: number | null;
  message: string | null;
};

export const getDay = () => api<Day>("/api/day");

export const generateDay = (minutes?: number, force = false) =>
  api<Day>("/api/day/generate", {
    method: "POST",
    body: JSON.stringify({ minutes: minutes ?? null, force }),
  });

/** Append one more cycle. Distinct from generateDay, which rebuilds. */
export const extendDay = (minutes: number) =>
  api<ExtendResult>("/api/day/extend", {
    method: "POST",
    body: JSON.stringify({ minutes }),
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
  built?: string;
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

