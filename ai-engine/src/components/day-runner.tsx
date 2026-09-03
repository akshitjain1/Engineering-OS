"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  Check,
  ExternalLink,
  Pause,
  Play,
  RotateCcw,
  SkipForward,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { errorMessage } from "@/lib/api";
import { TopicWorkPanel, type WorkSection } from "@/components/topic-work";
import {
  EMPTY_RECORD,
  HEARTBEAT_MS,
  clearRecord,
  pruneRecords,
  elapsedOf,
  fold,
  isRunning,
  isUntouched,
  pause,
  readRecord,
  reset as resetRecord,
  resume,
  writeRecord,
  type TimerRecord,
} from "@/lib/block-timer";
import {
  ACTIVITY_COPY,
  completeItem,
  extendDay,
  generateDay,
  getDay,
  saveJournal,
  skipItem,
  startItem,
  type Day,
  type DayItem,
} from "@/lib/day";

/* -------------------------------------------------------------------------
 * The day rail. Shows the whole day in one line so the focus card can stay
 * uncluttered. Clicking a block jumps to it — the only navigation you need.
 * ---------------------------------------------------------------------- */

function DayRail({
  items,
  activeId,
  onJump,
}: {
  items: DayItem[];
  activeId: number | null;
  onJump: (id: number) => void;
}) {
  return (
    <ol className="flex items-stretch gap-1.5" aria-label="Blocks in today's session">
      {items.map((item) => {
        const settled = item.status === "done" || item.status === "skipped";
        const isActive = item.id === activeId;
        return (
          <li key={item.id} className="min-w-0 flex-1" style={{ flexGrow: item.planned_minutes }}>
            <button
              type="button"
              onClick={() => onJump(item.id)}
              aria-current={isActive ? "step" : undefined}
              title={`${item.title} — ${item.planned_minutes} min`}
              className="group block w-full text-left"
            >
              <span
                className={cn(
                  "block h-1.5 w-full rounded-full transition-colors",
                  item.status === "done" && "bg-[var(--ok)]",
                  item.status === "skipped" && "bg-[var(--border-strong)]",
                  !settled && isActive && "bg-[var(--accent)]",
                  !settled && !isActive && "bg-[var(--border)] group-hover:bg-[var(--border-strong)]",
                )}
              />
              <span
                className={cn(
                  "mt-1.5 block truncate text-[11px] font-medium tracking-wide",
                  isActive ? "text-[var(--foreground)]" : "text-[var(--muted)]",
                  item.status === "skipped" && "line-through",
                )}
              >
                {ACTIVITY_COPY[item.activity_type]?.label ?? item.activity_type}
              </span>
            </button>
          </li>
        );
      })}
    </ol>
  );
}

/* -------------------------------------------------------------------------
 * Timer. A real stopwatch: it accumulates only while it is actually running,
 * survives a refresh, and never bills you for wall-clock time you spent away
 * from the desk. The old version derived elapsed from the server's started_at,
 * which meant Pause did nothing and an hour-old block read an hour of "work".
 * ---------------------------------------------------------------------- */

function useBlockTimer(item: DayItem | null) {
  const itemId = item?.id ?? null;
  const status = item?.status ?? null;
  const isActive = status === "active";
  // Once a block is closed the server owns its number. Showing a local
  // stopwatch for it would let the card disagree with the logged total.
  const settled = status === "done" || status === "skipped";
  const loggedMinutes = item?.actual_minutes ?? 0;
  const recordRef = useRef<TimerRecord>(EMPTY_RECORD);
  // Starts at a constant so the server render and the hydration render agree;
  // storage is only ever read from an effect.
  const [seconds, setSeconds] = useState(0);
  const [running, setRunningState] = useState(false);

  const commit = useCallback((itemId: number, rec: TimerRecord) => {
    recordRef.current = rec;
    writeRecord(itemId, rec);
    setSeconds(Math.floor(elapsedOf(rec)));
    setRunningState(isRunning(rec));
  }, []);

  // Keyed on the id alone. The old effect also depended on the item object, so
  // any background refetch handed it a fresh reference and silently restarted
  // the clock from started_at, undoing a pause.
  /* eslint-disable react-hooks/set-state-in-effect -- reading the persisted
     stopwatch has to happen after the hydration render; doing it during render
     would make the server and client disagree. Runs once per block. */
  useEffect(() => {
    if (itemId == null) {
      recordRef.current = EMPTY_RECORD;
      setSeconds(0);
      setRunningState(false);
      return;
    }
    if (settled) {
      recordRef.current = EMPTY_RECORD;
      setSeconds(loggedMinutes * 60);
      setRunningState(false);
      return;
    }
    const stored = readRecord(itemId);
    // A block you have just moved onto starts counting on its own; one you are
    // coming back to resumes exactly where you left it.
    commit(itemId, isUntouched(stored) && isActive ? resume(stored) : stored);
  }, [itemId, isActive, settled, loggedMinutes, commit]);
  /* eslint-enable react-hooks/set-state-in-effect */

  // Display tick. Derived from timestamps rather than incremented, so a
  // throttled background tab still shows the right total on return.
  useEffect(() => {
    if (!running) return;
    const id = window.setInterval(() => setSeconds(Math.floor(elapsedOf(recordRef.current))), 1000);
    return () => window.clearInterval(id);
  }, [running]);

  useEffect(() => {
    if (!running || itemId == null) return;
    const id = window.setInterval(() => {
      const rec = recordRef.current;
      if (!isRunning(rec)) return;
      const folded: TimerRecord = fold(rec);
      recordRef.current = folded;
      writeRecord(itemId, folded);
    }, HEARTBEAT_MS);
    return () => window.clearInterval(id);
  }, [running, itemId]);

  const setRunning = useCallback(
    (next: boolean | ((prev: boolean) => boolean)) => {
      if (itemId == null) return;
      const rec = recordRef.current;
      const want = typeof next === "function" ? next(isRunning(rec)) : next;
      if (want === isRunning(rec)) return;
      commit(itemId, want ? resume(rec) : pause(rec));
    },
    [itemId, commit],
  );

  const reset = useCallback(() => {
    if (itemId == null) return;
    // Zero the total but keep running if it was running -- a stopwatch reset,
    // not a stop.
    commit(itemId, resetRecord(recordRef.current));
  }, [itemId, commit]);

  const minutes = Math.max(1, Math.round(seconds / 60));
  return { seconds, minutes, running, settled, setRunning, reset };
}

function clock(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

/* -------------------------------------------------------------------------
 * Where the rest of this topic's day is.
 *
 * A topic is split across more than one block -- Storage is a 47-minute LEARN
 * and a 20-minute PRACTICE -- and from inside the first one there was nothing
 * saying the second existed. The exercises and the questions looked absent
 * from Today rather than one step along, which is exactly the kind of thing
 * that sends you off to hunt through the topic page mid-session.
 * ---------------------------------------------------------------------- */

const SECTION_SUMMARY: Record<string, string> = {
  LEARN: "read the source",
  PRACTICE: "the questions, the exercises and the build task",
  DSA: "the pattern and its problems",
  BUILD: "the implementation task",
  REVIEW: "spaced recall",
  REFLECT: "close the day",
};

function TopicHandoff({
  current,
  siblings,
  onJump,
}: {
  current: DayItem;
  siblings: DayItem[];
  onJump: (id: number) => void;
}) {
  if (siblings.length === 0) return null;

  // Where a sibling sits relative to this block, not just whether it is
  // finished. Keying only off status called the unfinished LEARN block sitting
  // above this one "Next", which points you backwards.
  const relation = (sibling: DayItem) => {
    if (sibling.status === "done") return "Done";
    if (sibling.status === "skipped") return "Skipped";
    return sibling.position < current.position ? "Earlier" : "Next";
  };
  return (
    <div className="rounded-lg border border-dashed border-[var(--border)] bg-[var(--card-2)] p-4">
      <p className="text-sm font-medium">The rest of this topic today</p>
      <ul className="mt-2 space-y-2">
        {siblings.map((sibling) => (
          <li key={sibling.id} className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
            <span className="text-[var(--muted)]">{relation(sibling)} —</span>
            <button
              type="button"
              onClick={() => onJump(sibling.id)}
              className="font-medium underline underline-offset-2 hover:text-[var(--accent)]"
            >
              {sibling.title}
            </button>
            <span className="text-[var(--muted)]">
              {sibling.planned_minutes} min · {SECTION_SUMMARY[sibling.activity_type] ?? "more work"}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/* -------------------------------------------------------------------------
 * Focus card — one block, everything needed to do it, nothing else.
 * ---------------------------------------------------------------------- */

function FocusCard({
  item,
  siblings,
  onJump,
  onDone,
  onSkip,
  busy,
}: {
  item: DayItem;
  /** Today's other blocks for the same topic, in day order. */
  siblings: DayItem[];
  onJump: (id: number) => void;
  onDone: (minutes: number, completeTopic: boolean) => void;
  onSkip: () => void;
  busy: boolean;
}) {
  const timer = useBlockTimer(item);
  const copy = ACTIVITY_COPY[item.activity_type];
  // A finished block is never "running over" -- it is just its logged number.
  const over = !timer.settled && timer.seconds > item.planned_minutes * 60;
  const isLearnLike = item.activity_type === "LEARN" || item.activity_type === "DSA";
  // Blocks whose work lives on the topic render it here, in order, so the block
  // is self-contained instead of a link away.
  //
  // DSA is read-then-solve in one block: showing only the problem it picked
  // asked for a solution before showing what to read, with the reading a page
  // away. So DSA pulls in the learn step and drops the single-resource card
  // below, which would otherwise repeat one of the problems.
  const workSections: WorkSection[] | null =
    item.topic_id === null
      ? null
      : item.activity_type === "DSA"
        ? ["learn", "practice", "recall"]
        : item.activity_type === "PRACTICE"
          ? // Everything this block already claims to be. Its subtitle reads
            // "Questions and exercises for the topic you just studied" and it
            // tells you to answer the questions from memory first -- and it
            // showed no questions at all. They were rendered one block earlier,
            // under LEARN, whose own instructions never mention them.
            //
            // So each block contradicted itself, and the exercises looked
            // missing from Today entirely when you were still on LEARN. Recall
            // leads here because that is the order the block asks for.
            ["recall", "practice", "build"]
          : item.activity_type === "BUILD"
            ? ["build"]
            : // A LEARN block is the reading, and its instructions say exactly
              // that: read once at normal speed, then write the idea in your own
              // words. The work that follows belongs to the PRACTICE block, and
              // TopicHandoff below says so rather than leaving you to find it.
              null;
  const inlineWork = workSections !== null;
  // The sequence already opens with the source, so a second copy is noise.
  const showResourceCard = Boolean(item.resource?.url) && item.activity_type !== "DSA";
  // Checked by default. The cursor only advances when a topic is marked
  // finished, so defaulting this off silently serves the same topic every day
  // and leaves the DSA board reading zero however much work you did.
  //
  // That is exactly what happened: an effect here reset this to false on mount
  // and on every item change, so the state initialiser below never survived and
  // the box was permanently unchecked -- the precise failure the comment above
  // was written to prevent. FocusCard is now keyed on the item id by its
  // parent, so React remounts it per block and the default holds.
  const [alsoComplete, setAlsoComplete] = useState(true);

  return (
    <article className="rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-[var(--shadow)]">
      <div className="border-b border-[var(--border)] px-6 py-5 sm:px-8">
        <p className="text-sm font-medium text-[var(--accent)]">
          {copy?.label ?? item.activity_type}
          <span className="ml-2 font-normal text-[var(--muted)]">
            {item.planned_minutes} minutes · {copy?.blurb}
          </span>
        </p>
        <h1 className="mt-2 text-[30px] font-bold leading-tight tracking-tight sm:text-[34px]">
          {item.title}
        </h1>
        {item.subtitle ? (
          <p className="mt-1 text-sm text-[var(--muted)]">{item.subtitle}</p>
        ) : null}
      </div>

      <div className="grid gap-0 lg:grid-cols-[1.4fr_1fr]">
        <div className="space-y-5 border-b border-[var(--border)] px-6 py-6 sm:px-8 lg:border-b-0 lg:border-r">
          {item.why ? (
            <div>
              <p className="text-sm font-semibold">Why this now</p>
              <p className="mt-1 max-w-[68ch] text-[15px] leading-relaxed text-[var(--muted)]">
                {item.why}
              </p>
            </div>
          ) : null}
          {item.how ? (
            <div>
              <p className="text-sm font-semibold">How to work through it</p>
              <p className="mt-1 max-w-[68ch] text-[15px] leading-relaxed text-[var(--muted)]">
                {item.how}
              </p>
            </div>
          ) : null}

          {showResourceCard && item.resource?.url ? (
            <div className="rounded-lg border border-[var(--border)] bg-[var(--card-2)] p-4">
              <p className="text-xs font-medium text-[var(--muted)]">
                {item.resource.provider ?? "Source"}
              </p>
              <p className="mt-0.5 text-sm font-medium">{item.resource.title}</p>
              <a
                href={item.resource.url}
                target="_blank"
                rel="noreferrer"
                className="mt-3 inline-flex items-center gap-2 rounded-md bg-[var(--accent)] px-3.5 py-2 text-sm font-medium text-[var(--accent-fg)] hover:bg-[var(--accent-hover)]"
              >
                Open source <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </div>
          ) : null}

          {inlineWork && item.topic_id ? (
            <div className="rounded-lg border border-[var(--border)] bg-[var(--card-2)] p-4">
              <TopicWorkPanel
                key={item.topic_id}
                topicId={item.topic_id}
                sections={workSections ?? undefined}
                blockMinutes={item.planned_minutes}
              />
            </div>
          ) : item.activity_type === "REVIEW" ? (
            // A REVIEW block covers several due items at once, so it carries no
            // topic_id and none of the inline work above applies. It tells you
            // to grade yourself Hard / OK / Easy -- and the only place that
            // grading exists is the review queue. Without this link the block
            // asks for something the page gives you no way to do, and the
            // schedule never advances.
            <div className="rounded-lg border border-dashed border-[var(--border)] bg-[var(--card-2)] p-4">
              <p className="text-sm font-medium">Grade each one after you recall it</p>
              <p className="mt-1 text-sm text-[var(--muted)]">
                Say the explanation out loud first. Grading is what moves the next review
                date — an ungraded item comes back tomorrow unchanged.
              </p>
              <Link
                href="/revision"
                className="mt-3 inline-flex items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card)] px-3.5 py-2 text-sm font-medium hover:border-[var(--border-strong)]"
              >
                Open the review queue <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          ) : null}

          <TopicHandoff current={item} siblings={siblings} onJump={onJump} />

          {!inlineWork && !showResourceCard && item.topic_id ? (
            <div className="rounded-lg border border-dashed border-[var(--border)] bg-[var(--card-2)] p-4">
              <p className="text-sm font-medium">Work inside the topic</p>
              <p className="mt-1 text-sm text-[var(--muted)]">
                No separate source is mapped for this block. Use the topic&apos;s own questions
                and exercises.
              </p>
              <Link
                href={`/learn/topic/${item.topic_id}`}
                className="mt-3 inline-flex items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card)] px-3.5 py-2 text-sm font-medium hover:border-[var(--border-strong)]"
              >
                Open topic <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          ) : null}
        </div>

        <div className="px-6 py-6 sm:px-8">
          <p className="text-sm font-semibold">Time on this block</p>
          <p
            className={cn(
              "mt-2 font-mono text-[44px] font-semibold leading-none tabular-nums",
              over ? "text-[var(--warn)]" : "text-[var(--foreground)]",
            )}
          >
            {clock(timer.seconds)}
          </p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            {timer.settled
              ? `Logged ${item.actual_minutes} of ${item.planned_minutes} planned minutes.`
              : over
              ? `Past the ${item.planned_minutes} minute estimate. That is fine — the number logged is what you actually spent.`
              : `Planned ${item.planned_minutes} minutes`}
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              disabled={timer.settled}
              onClick={() => timer.setRunning((r) => !r)}
              className="inline-flex items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card)] px-3 py-1.5 text-sm font-medium hover:border-[var(--border-strong)] disabled:opacity-50"
            >
              {timer.running ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
              {timer.running ? "Pause" : "Start timer"}
            </button>
            <button
              type="button"
              disabled={timer.settled}
              onClick={timer.reset}
              className="inline-flex items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card)] px-3 py-1.5 text-sm text-[var(--muted)] hover:border-[var(--border-strong)] disabled:opacity-50"
            >
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </button>
          </div>

          {isLearnLike && item.topic_id ? (
            <label className="mt-5 flex cursor-pointer items-start gap-2 text-sm">
              <input
                type="checkbox"
                checked={alsoComplete}
                onChange={(e) => setAlsoComplete(e.target.checked)}
                className="mt-0.5 h-4 w-4 accent-[var(--accent)]"
              />
              <span>
                Finished this topic — move to the next one
                <span className="block text-xs text-[var(--muted)]">
                  Uncheck if you want the same topic again tomorrow.
                </span>
              </span>
            </label>
          ) : null}

          <div className="mt-6 space-y-2 border-t border-[var(--border)] pt-5">
            <button
              type="button"
              disabled={busy}
              onClick={() => onDone(timer.minutes, alsoComplete)}
              className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-[var(--accent-fg)] hover:bg-[var(--accent-hover)] disabled:opacity-50"
            >
              <Check className="h-4 w-4" /> Done — next block
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={onSkip}
              className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-[var(--border)] bg-[var(--card)] px-4 py-2 text-sm text-[var(--muted)] hover:border-[var(--border-strong)] disabled:opacity-50"
            >
              <SkipForward className="h-3.5 w-3.5" /> Skip today
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}

/* -------------------------------------------------------------------------
 * End of day. The only screen that is allowed to be a dead end.
 * ---------------------------------------------------------------------- */

function DayComplete({
  day,
  onExtend,
  busy,
  exhaustedMessage,
}: {
  day: Day;
  onExtend: (minutes: number) => void;
  busy: boolean;
  exhaustedMessage: string | null;
}) {
  const [form, setForm] = useState({
    learned: day.journal?.learned ?? "",
    struggled: day.journal?.struggled ?? "",
    tomorrow: day.journal?.tomorrow ?? "",
  });
  const [saved, setSaved] = useState<"idle" | "saving" | "saved">("idle");

  const persist = useCallback(async (next: typeof form) => {
    setSaved("saving");
    try {
      await saveJournal(next);
      setSaved("saved");
    } catch {
      setSaved("idle");
    }
  }, []);

  const field = (
    key: keyof typeof form,
    label: string,
    placeholder: string,
  ) => (
    <label className="block">
      <span className="text-sm font-semibold">{label}</span>
      <textarea
        rows={3}
        value={form[key]}
        placeholder={placeholder}
        onChange={(e) => {
          const next = { ...form, [key]: e.target.value };
          setForm(next);
          setSaved("idle");
        }}
        onBlur={() => persist(form)}
        className="mt-1.5 w-full rounded-md border border-[var(--border)] bg-[var(--background)] p-3 text-sm leading-relaxed"
      />
    </label>
  );

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-[var(--shadow)] sm:p-8">
      <p className="text-sm font-medium text-[var(--ok)]">Session finished</p>
      <h1 className="mt-2 text-[30px] font-bold tracking-tight">
        {day.totals.logged_minutes} minutes logged across {day.totals.items_done} blocks
      </h1>
      <p className="mt-2 max-w-[62ch] text-[15px] leading-relaxed text-[var(--muted)]">
        Two minutes of writing now is what turns today into something you can still use next
        month. It saves as you go.
      </p>
      <div className="mt-6 grid gap-5 lg:grid-cols-3">
        {field("learned", "What I learned", "The idea in my own words…")}
        {field("struggled", "Where I got stuck", "The part I could not explain…")}
        {field("tomorrow", "First thing tomorrow", "Concrete and small…")}
      </div>
      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={() => persist(form)}
          className="rounded-md bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[var(--accent-fg)] hover:bg-[var(--accent-hover)]"
        >
          Save notes
        </button>
        <span className="text-xs text-[var(--muted)]">
          {saved === "saving" ? "Saving…" : saved === "saved" ? "Saved" : ""}
        </span>
      </div>

      <div className="mt-6 border-t border-[var(--border)] pt-5">
        {exhaustedMessage ? (
          <p className="text-sm font-medium">{exhaustedMessage}</p>
        ) : (
          <>
            <p className="text-sm font-medium">Add more time today</p>
            <p className="mt-1 text-sm text-[var(--muted)]">
              Appends another Learn, Practice and DSA block on the next topics. Nothing
              you have already finished is touched.
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {[30, 60, 90].map((m) => (
                <button
                  key={m}
                  type="button"
                  disabled={busy}
                  onClick={() => onExtend(m)}
                  className="rounded-md border border-[var(--border)] bg-[var(--card)] px-3 py-2 text-sm font-medium hover:border-[var(--border-strong)] disabled:opacity-50"
                >
                  +{m} min
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------
 * Runner
 * ---------------------------------------------------------------------- */

export function DayRunner() {
  const [day, setDay] = useState<Day | null>(null);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [exhausted, setExhausted] = useState<string | null>(null);
  // Distinct from `error`, which replaces the whole day. A background sync
  // failure should be visible without throwing away what is on screen.
  const [notice, setNotice] = useState<string | null>(null);
  const topRef = useRef<HTMLDivElement | null>(null);

  const load = useCallback(async () => {
    try {
      // GET /api/day is read-only. /today is the one surface allowed to build a
      // day, so it generates when the read comes back empty.
      let next = await getDay();
      if (next.needs_generation) next = await generateDay();
      setDay(next);
      // Row ids are reused after a rebuild, so stopwatches for blocks that no
      // longer exist have to go before one of them is mistaken for a new block.
      pruneRecords(next.items.map((i) => i.id));
      setActiveId((current) => current ?? next.current_item_id);
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    }
  }, []);

  // Fetching the day on mount is what an effect is for, and nothing is set
  // synchronously here: `load` is async and its first statement awaits, so
  // every setState inside it lands in a later tick. The rule cannot see through
  // the async boundary, so it is silenced rather than the code contorted.
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  const activeItem =
    day?.items.find((i) => i.id === activeId) ??
    day?.items.find((i) => i.id === day.current_item_id) ??
    null;

  // Today's other blocks for the same topic, in day order. A topic is normally
  // split across two of them, and the second one is where the exercises live.
  const siblingBlocks =
    activeItem?.topic_id == null
      ? []
      : (day?.items ?? []).filter(
          (i) => i.topic_id === activeItem.topic_id && i.id !== activeItem.id,
        );

  // Marking the block started on the server. Fires once per block: the old
  // version also depended on the item object, so every refetch handed it a new
  // reference and it re-POSTed. Failures used to be swallowed whole, which left
  // the server thinking the block never began with nothing on screen to say so.
  const activeItemId = activeItem?.id ?? null;
  const activeItemStatus = activeItem?.status ?? null;
  const startedRef = useRef<Set<number>>(new Set());
  useEffect(() => {
    if (activeItemId == null || activeItemStatus !== "pending") return;
    if (startedRef.current.has(activeItemId)) return;
    startedRef.current.add(activeItemId);
    startItem(activeItemId)
      .then(load)
      .catch((err) => {
        // Let it be retried rather than stranding the block as pending.
        startedRef.current.delete(activeItemId);
        setNotice(`Could not mark this block started: ${errorMessage(err)}`);
      });
  }, [activeItemId, activeItemStatus, load]);

  const advance = useCallback(
    (next: DayItem | null) => {
      setActiveId(next ? next.id : null);
      topRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    },
    [],
  );

  async function handleDone(minutes: number, completeTopic: boolean) {
    if (!activeItem) return;
    setBusy(true);
    try {
      const result = await completeItem(activeItem.id, {
        minutes,
        complete_topic: completeTopic,
      });
      // The minutes are banked server-side now; the local stopwatch would only
      // be a second, drifting copy of them.
      clearRecord(activeItem.id);
      advance(result.next);
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function handleSkip() {
    if (!activeItem) return;
    setBusy(true);
    try {
      const result = await skipItem(activeItem.id);
      clearRecord(activeItem.id);
      advance(result.next);
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  /** Append one more cycle and jump straight into it. */
  async function handleExtend(minutes: number) {
    setBusy(true);
    try {
      const next = await extendDay(minutes);
      setDay(next);
      if (next.first_new_item_id != null) {
        setActiveId(next.first_new_item_id);
        setExhausted(null);
        topRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      } else {
        // Nothing left to schedule -- say so instead of doing nothing visible.
        setExhausted(next.message ?? "Nothing left to schedule.");
      }
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  /** Rebuild today at a different budget. Finished blocks are kept. */
  async function handleRebuild(minutes: number) {
    setBusy(true);
    try {
      const next = await generateDay(minutes, true);
      setDay(next);
      setActiveId(next.current_item_id);
      setExhausted(null);
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  if (error) {
    return (
      <div className="rounded-lg border border-[var(--border)] bg-[var(--warn-soft)] px-5 py-4">
        <p className="text-sm font-medium">Today&apos;s session did not load.</p>
        <p className="mt-1 text-sm text-[var(--muted)]">{error}</p>
        <button
          type="button"
          onClick={load}
          className="mt-3 rounded-md border border-[var(--border)] bg-[var(--card)] px-3 py-1.5 text-sm font-medium"
        >
          Try again
        </button>
      </div>
    );
  }

  if (!day) {
    return <p className="text-sm text-[var(--muted)]">Building today&apos;s session…</p>;
  }

  const remaining = day.totals.planned_minutes - day.totals.logged_minutes;

  return (
    <div ref={topRef} className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-sm font-medium text-[var(--muted)]">
            {new Date(day.plan_date).toLocaleDateString("en-GB", {
              weekday: "long",
              day: "numeric",
              month: "long",
            })}
          </h2>
          <p className="mt-0.5 text-[15px]">
            {day.totals.items_done} of {day.totals.items_total} blocks done ·{" "}
            {day.totals.logged_minutes} of {day.totals.planned_minutes} minutes logged
            {remaining > 0 ? ` · about ${remaining} left` : ""}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-[var(--muted)]">Rebuild at</span>
          {[60, 90, 120, 180, 240].map((m) => (
            <button
              key={m}
              type="button"
              disabled={busy}
              onClick={() => handleRebuild(m)}
              className="rounded-md border border-[var(--border)] bg-[var(--card)] px-2.5 py-1.5 text-xs font-medium hover:border-[var(--border-strong)] disabled:opacity-50"
              title={`Rebuild today for ${m} minutes. Finished blocks are kept, open blocks are replaced.`}
            >
              {m}m
            </button>
          ))}
        </div>
      </header>

      {notice ? (
        <div className="flex items-start justify-between gap-3 rounded-lg border border-[var(--warn)] bg-[var(--warn-soft)] px-4 py-2.5">
          <p className="text-sm">{notice}</p>
          <button
            type="button"
            onClick={() => setNotice(null)}
            className="shrink-0 text-sm text-[var(--muted)] underline"
          >
            Dismiss
          </button>
        </div>
      ) : null}

      <DayRail items={day.items} activeId={activeItem?.id ?? null} onJump={setActiveId} />

      {activeItem ? (
        <FocusCard
          key={activeItem.id}
          item={activeItem}
          siblings={siblingBlocks}
          onJump={setActiveId}
          onDone={handleDone}
          onSkip={handleSkip}
          busy={busy}
        />
      ) : (
        <DayComplete
          day={day}
          onExtend={handleExtend}
          busy={busy}
          exhaustedMessage={exhausted}
        />
      )}
    </div>
  );
}
