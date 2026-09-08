/* -------------------------------------------------------------------------
 * Stopwatch arithmetic and persistence for a day block.
 *
 * Kept apart from the component so the rules are stated once and can be
 * exercised without a browser.
 *
 * The invariant: **a running stopwatch stops only when you stop it.** Leaving
 * the page, opening the recall queue, following the resource link, refreshing,
 * reopening the tab later -- none of those pause it.
 *
 * This is a deliberate reversal. The previous rule was "time only accrues in a
 * live tab", implemented by discarding any open window older than 15 seconds
 * on the grounds that the tab must have died. In practice the tab had not
 * died: leaving the Recall block to look at the recall queue is *doing the
 * block*, and coming back to a stopwatch that had silently thrown the time
 * away made the clock useless for the one thing it is for.
 *
 * The cost of the reversal is that a stopwatch left running overnight keeps
 * counting. That is not hidden -- `looksLeftRunning` marks an implausibly long
 * open window so the UI can say so and offer Reset. Telling you is honest;
 * silently discarding your afternoon was not.
 * ---------------------------------------------------------------------- */

export type TimerRecord = {
  /** Seconds banked from windows that have already been closed. */
  accumulated: number;
  /** Epoch ms the current running window opened, or null when paused. */
  runningSince: number | null;
};

export const EMPTY_RECORD: TimerRecord = { accumulated: 0, runningSince: null };

/** While running, the open window is folded into the total this often. No
 *  longer load-bearing for correctness -- an open window is trusted however
 *  old it is -- but it keeps the stored total close to the truth. */
export const HEARTBEAT_MS = 5_000;

/** A single uninterrupted window longer than this is much more likely a timer
 *  left on overnight than four hours of unbroken study. It is still counted;
 *  the UI flags it so the choice to keep or reset it stays yours. */
export const LONG_RUN_WARN_S = 4 * 60 * 60;

export const TIMER_PREFIX = "eos-block-timer-";
export const timerKey = (itemId: number) => `${TIMER_PREFIX}${itemId}`;

/** Seconds in the window that is open right now, 0 when paused. */
export function openWindowOf(rec: TimerRecord, now: number = Date.now()): number {
  return rec.runningSince === null ? 0 : Math.max(0, (now - rec.runningSince) / 1000);
}

export function elapsedOf(rec: TimerRecord, now: number = Date.now()): number {
  return rec.accumulated + openWindowOf(rec, now);
}

/** True when the open window is long enough to be a forgotten timer.
 *
 *  Nothing is changed on the strength of this. It exists so the page can say
 *  "this has been running for nine hours" instead of either silently logging
 *  nine hours or silently deleting them. */
export function looksLeftRunning(rec: TimerRecord, now: number = Date.now()): boolean {
  return openWindowOf(rec, now) >= LONG_RUN_WARN_S;
}

export const isRunning = (rec: TimerRecord) => rec.runningSince !== null;

/** Open a running window without disturbing what is already banked. */
export function resume(rec: TimerRecord, now: number = Date.now()): TimerRecord {
  return isRunning(rec) ? rec : { accumulated: rec.accumulated, runningSince: now };
}

/** Bank the open window and stop. */
export function pause(rec: TimerRecord, now: number = Date.now()): TimerRecord {
  return isRunning(rec) ? { accumulated: elapsedOf(rec, now), runningSince: null } : rec;
}

/** Heartbeat: bank the open window and immediately open a new one. */
export function fold(rec: TimerRecord, now: number = Date.now()): TimerRecord {
  return isRunning(rec) ? { accumulated: elapsedOf(rec, now), runningSince: now } : rec;
}

/** Zero the total, staying in whatever run state it was already in. */
export function reset(rec: TimerRecord, now: number = Date.now()): TimerRecord {
  return { accumulated: 0, runningSince: isRunning(rec) ? now : null };
}

export const isUntouched = (rec: TimerRecord) => rec.accumulated === 0 && rec.runningSince === null;

export function parseRecord(raw: string | null, now: number = Date.now()): TimerRecord {
  if (!raw) return EMPTY_RECORD;
  try {
    const parsed = JSON.parse(raw) as Partial<TimerRecord>;
    const accumulated =
      typeof parsed.accumulated === "number" && Number.isFinite(parsed.accumulated)
        ? Math.max(0, parsed.accumulated)
        : 0;
    const since = typeof parsed.runningSince === "number" ? parsed.runningSince : null;
    // An open window is trusted however old it is. A running stopwatch stops
    // only when you stop it, so being away from the page is not a reason to
    // discard the time -- that discarding is exactly what made the clock
    // reset every time the recall queue was opened.
    //
    // The one thing still rejected is a start time in the future, which can
    // only come from a clock change or a corrupted record and would otherwise
    // read as negative elapsed time.
    const usable = since !== null && since <= now;
    return { accumulated, runningSince: usable ? since : null };
  } catch {
    return EMPTY_RECORD;
  }
}

export function readRecord(itemId: number, now: number = Date.now()): TimerRecord {
  try {
    return parseRecord(localStorage.getItem(timerKey(itemId)), now);
  } catch {
    return EMPTY_RECORD;
  }
}

export function writeRecord(itemId: number, rec: TimerRecord) {
  try {
    localStorage.setItem(timerKey(itemId), JSON.stringify(rec));
  } catch {
    // storage unavailable (private mode, quota) -- the timer still works for
    // this session, it just will not survive a refresh.
  }
}

export function clearRecord(itemId: number) {
  try {
    localStorage.removeItem(timerKey(itemId));
  } catch {
    // ignore
  }
}

/** Drop stored stopwatches for blocks that are no longer in the plan.
 *
 *  Not just housekeeping. daily_plan_items.id is a plain SQLite INTEGER
 *  PRIMARY KEY with no AUTOINCREMENT, so row ids are reused after a delete --
 *  and rebuilding the day deletes every open block. Without this a fresh block
 *  can be handed a deleted block's id, and would inherit its clock. */
export function pruneRecords(liveItemIds: Iterable<number>) {
  try {
    const keep = new Set<string>();
    for (const id of liveItemIds) keep.add(timerKey(id));
    const stale: string[] = [];
    for (let i = 0; i < localStorage.length; i += 1) {
      const key = localStorage.key(i);
      if (key && key.startsWith(TIMER_PREFIX) && !keep.has(key)) stale.push(key);
    }
    for (const key of stale) localStorage.removeItem(key);
    return stale.length;
  } catch {
    return 0;
  }
}
