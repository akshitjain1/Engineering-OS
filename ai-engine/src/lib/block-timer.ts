/* -------------------------------------------------------------------------
 * Stopwatch arithmetic and persistence for a day block.
 *
 * Kept apart from the component so the rules are stated once and can be
 * exercised without a browser. The invariant: time only ever accrues while
 * the stopwatch is running in a live tab. Wall-clock time you spent away from
 * the desk is never counted, which is what the previous started_at-based
 * version got wrong.
 * ---------------------------------------------------------------------- */

export type TimerRecord = {
  /** Seconds banked from windows that have already been closed. */
  accumulated: number;
  /** Epoch ms the current running window opened, or null when paused. */
  runningSince: number | null;
};

export const EMPTY_RECORD: TimerRecord = { accumulated: 0, runningSince: null };

/** While running, the open window is folded into the total this often, so a
 *  crash or a closed laptop costs at most this much. */
export const HEARTBEAT_MS = 5_000;

/** An open window older than this was never closed by a heartbeat, meaning the
 *  tab died rather than kept ticking. The gap is dropped, not counted. Must
 *  stay comfortably above HEARTBEAT_MS so an ordinary refresh still resumes. */
export const STALE_MS = 15_000;

export const TIMER_PREFIX = "eos-block-timer-";
export const timerKey = (itemId: number) => `${TIMER_PREFIX}${itemId}`;

export function elapsedOf(rec: TimerRecord, now: number = Date.now()): number {
  const open = rec.runningSince === null ? 0 : Math.max(0, (now - rec.runningSince) / 1000);
  return rec.accumulated + open;
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
    // Trust an open window only if a heartbeat wrote it recently. Anything
    // older means the tab was gone, so the gap is not work.
    const live = since !== null && now - since < STALE_MS && since <= now;
    return { accumulated, runningSince: live ? since : null };
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
