"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { Pause, Play, RotateCcw, SkipForward, X, Settings2 } from "lucide-react";

export type PomodoroMode = "25/5" | "45/10" | "50/10" | "90/15";

const DEFAULT_MODE: PomodoroMode = "50/10";

const MODES: Record<PomodoroMode, { focus: number; breakTime: number; label: string }> = {
  "25/5": { focus: 1500, breakTime: 300, label: "25 / 5" },
  "45/10": { focus: 2700, breakTime: 600, label: "45 / 10" },
  "50/10": { focus: 3000, breakTime: 600, label: "50 / 10" },
  "90/15": { focus: 5400, breakTime: 900, label: "90 / 15" },
};

type TimerState = {
  mode: PomodoroMode;
  isRunning: boolean;
  isFocus: boolean;
  timeRemaining: number;
  sessionsCompleted: number;
  endAt: number | null;
};

type Analytics = {
  sessionsStarted: number;
  sessionsCompleted: number;
  totalFocusMinutes: number;
  todayMinutes: number;
  todayDate: string;
};

const STORAGE_KEY = "eos-pomodoro-state";
const ANALYTICS_KEY = "eos-pomodoro-analytics";

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

function loadState(): TimerState {
  if (typeof window === "undefined") {
    return { mode: DEFAULT_MODE, isRunning: false, isFocus: true, timeRemaining: MODES[DEFAULT_MODE].focus, sessionsCompleted: 0, endAt: null };
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as TimerState;
      // validate mode
      if (!MODES[parsed.mode as PomodoroMode]) parsed.mode = DEFAULT_MODE;
      // hydrate endAt to recover elapsed during refresh
      if (parsed.isRunning && parsed.endAt) {
        const remaining = Math.max(0, Math.round((parsed.endAt - Date.now()) / 1000));
        if (remaining === 0) {
          return { ...parsed, timeRemaining: remaining, isRunning: false, endAt: null };
        }
        return { ...parsed, timeRemaining: remaining };
      }
      // ensure timeRemaining matches mode if inconsistent
      if (parsed.timeRemaining <= 0 || parsed.timeRemaining > 10000) {
        parsed.timeRemaining = parsed.isFocus ? MODES[parsed.mode].focus : MODES[parsed.mode].breakTime;
      }
      return { ...parsed, isRunning: false, endAt: null };
    }
  } catch {
    // ignore
  }
  return { mode: DEFAULT_MODE, isRunning: false, isFocus: true, timeRemaining: MODES[DEFAULT_MODE].focus, sessionsCompleted: 0, endAt: null };
}

function persistState(s: TimerState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  } catch {
    // ignore
  }
}

function loadAnalytics(): Analytics {
  try {
    const raw = localStorage.getItem(ANALYTICS_KEY);
    if (raw) {
      const a = JSON.parse(raw) as Analytics;
      if (a.todayDate !== todayKey()) return { sessionsStarted: 0, sessionsCompleted: 0, totalFocusMinutes: a.totalFocusMinutes ?? 0, todayMinutes: 0, todayDate: todayKey() };
      return a;
    }
  } catch {
    // ignore
  }
  return { sessionsStarted: 0, sessionsCompleted: 0, totalFocusMinutes: 0, todayMinutes: 0, todayDate: todayKey() };
}

function persistAnalytics(a: Analytics) {
  try {
    localStorage.setItem(ANALYTICS_KEY, JSON.stringify(a));
  } catch {
    // ignore
  }
}

function notify(title: string, body: string) {
  try {
    if (typeof window !== "undefined" && "Notification" in window && Notification.permission === "granted") {
      new Notification(title, { body });
    }
  } catch {
    // ignore
  }
  try {
    const ctx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.connect(g);
    g.connect(ctx.destination);
    o.frequency.value = 880;
    g.gain.value = 0.08;
    o.start();
    setTimeout(() => {
      try { o.stop(); ctx.close(); } catch { /* ignore */ }
    }, 250);
  } catch {
    // ignore
  }
}

function formatTime(s: number) {
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

type PomodoroContextValue = {
  state: TimerState;
  analytics: Analytics;
  start: () => void;
  pause: () => void;
  reset: () => void;
  skip: () => void;
  setMode: (m: PomodoroMode) => void;
  finish: () => void;
  stop: () => void;
};

const PomodoroContext = createContext<PomodoroContextValue | null>(null);

export function PomodoroProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<TimerState>(() => loadState());
  const [analytics, setAnalytics] = useState<Analytics>(() => loadAnalytics());
  const intervalRef = useRef<number | null>(null);

  const clearIntervalRef = useCallback(() => {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Single tick effect - only one interval globally
  useEffect(() => {
    clearIntervalRef();
    if (!state.isRunning || state.endAt == null) return;

    intervalRef.current = window.setInterval(() => {
      setState((prev) => {
        if (!prev.isRunning || prev.endAt == null) return prev;
        const remaining = Math.max(0, Math.round((prev.endAt - Date.now()) / 1000));
        if (remaining === 0) {
          const wasFocus = prev.isFocus;
          const nextIsFocus = !wasFocus;
          const nextDuration = nextIsFocus ? MODES[prev.mode].focus : MODES[prev.mode].breakTime;
          if (wasFocus) {
            setAnalytics((aPrev) => {
              const minutes = Math.round(MODES[prev.mode].focus / 60);
              const nextDate = todayKey();
              const base = aPrev.todayDate === nextDate ? aPrev : { ...aPrev, todayMinutes: 0, todayDate: nextDate };
              const updated: Analytics = {
                sessionsCompleted: base.sessionsCompleted + 1,
                sessionsStarted: base.sessionsStarted,
                totalFocusMinutes: base.totalFocusMinutes + minutes,
                todayMinutes: base.todayMinutes + minutes,
                todayDate: nextDate,
              };
              persistAnalytics(updated);
              return updated;
            });
          }
          notify(wasFocus ? "Focus complete" : "Break over", wasFocus ? "Time for a break" : "Back to focus");
          const next: TimerState = {
            ...prev,
            isFocus: nextIsFocus,
            isRunning: false,
            timeRemaining: nextDuration,
            endAt: null,
            sessionsCompleted: wasFocus ? prev.sessionsCompleted + 1 : prev.sessionsCompleted,
          };
          persistState(next);
          return next;
        }
        // still running - update remaining without creating new endAt
        return prev;
      });
    }, 250);

    return () => clearIntervalRef();
  }, [state.isRunning, state.endAt, state.mode, state.isFocus, clearIntervalRef]);

  // Derive display timeRemaining from endAt for smooth UI
  const liveState = useMemo(() => {
    if (state.isRunning && state.endAt) {
      // eslint-disable-next-line react-hooks/purity -- Date.now needed for live countdown, driven by forceTick
      const remaining = Math.max(0, Math.round((state.endAt - Date.now()) / 1000));
      return { ...state, timeRemaining: remaining };
    }
    return state;
  }, [state]);

  // Persist state changes (except high-frequency tick which we already handled)
  useEffect(() => {
    persistState(state);
  }, [state]);

  // Also persist analytics
  useEffect(() => {
    persistAnalytics(analytics);
  }, [analytics]);

  const liveStateRef = useRef(liveState);
  useEffect(() => { liveStateRef.current = liveState; }, [liveState]);

  // Sync display tick for live countdown without setState spam - force re-render every 250ms while running
  const [, forceTick] = useState(0);
  useEffect(() => {
    if (!state.isRunning) return;
    const id = window.setInterval(() => forceTick((x) => x + 1), 250);
    return () => window.clearInterval(id);
  }, [state.isRunning]);

  const start = useCallback(() => {
    const isFocusStart = liveStateRef.current?.isFocus ?? true;
    const wasRunning = liveStateRef.current?.isRunning ?? false;
    if (wasRunning) return;
    setState((prev) => {
      if (prev.isRunning) return prev;
      const endAt = Date.now() + prev.timeRemaining * 1000;
      const next: TimerState = { ...prev, isRunning: true, endAt };
      persistState(next);
      return next;
    });
    if (isFocusStart) {
      setAnalytics((aPrev) => {
        const nextDate = todayKey();
        const base = aPrev.todayDate === nextDate ? aPrev : { ...aPrev, todayMinutes: 0, todayDate: nextDate };
        const updated: Analytics = { ...base, sessionsStarted: base.sessionsStarted + 1 };
        persistAnalytics(updated);
        return updated;
      });
    }
    try {
      if (typeof window !== "undefined" && "Notification" in window && Notification.permission === "default") {
        void Notification.requestPermission().catch(() => {});
      }
    } catch {
      // ignore
    }
  }, []);

  const pause = useCallback(() => {
    clearIntervalRef();
    setState((prev) => {
      if (!prev.isRunning) return prev;
      const remaining = prev.endAt ? Math.max(0, Math.round((prev.endAt - Date.now()) / 1000)) : prev.timeRemaining;
      const next: TimerState = { ...prev, isRunning: false, timeRemaining: remaining, endAt: null };
      persistState(next);
      return next;
    });
  }, [clearIntervalRef]);

  const stop = useCallback(() => {
    clearIntervalRef();
    setState((prev) => {
      const next: TimerState = { ...prev, isRunning: false, endAt: null };
      persistState(next);
      return next;
    });
  }, [clearIntervalRef]);

  const reset = useCallback(() => {
    clearIntervalRef();
    setState((prev) => {
      const dur = prev.isFocus ? MODES[prev.mode].focus : MODES[prev.mode].breakTime;
      const next: TimerState = { ...prev, isRunning: false, timeRemaining: dur, endAt: null };
      persistState(next);
      return next;
    });
  }, [clearIntervalRef]);

  const skip = useCallback(() => {
    clearIntervalRef();
    setState((prev) => {
      const wasFocus = prev.isFocus;
      const nextIsFocus = !wasFocus;
      const dur = nextIsFocus ? MODES[prev.mode].focus : MODES[prev.mode].breakTime;
      const next: TimerState = {
        ...prev,
        isFocus: nextIsFocus,
        isRunning: false,
        timeRemaining: dur,
        endAt: null,
        sessionsCompleted: wasFocus ? prev.sessionsCompleted + 1 : prev.sessionsCompleted,
      };
      persistState(next);
      return next;
    });
  }, [clearIntervalRef]);

  const setMode = useCallback((mode: PomodoroMode) => {
    clearIntervalRef();
    setState(() => {
      const next: TimerState = { mode, isRunning: false, isFocus: true, timeRemaining: MODES[mode].focus, sessionsCompleted: 0, endAt: null };
      persistState(next);
      return next;
    });
  }, [clearIntervalRef]);

  const finish = useCallback(() => {
    clearIntervalRef();
    setState((prev) => {
      const wasFocus = prev.isFocus;
      const nextIsFocus = !wasFocus;
      const dur = nextIsFocus ? MODES[prev.mode].focus : MODES[prev.mode].breakTime;
      const next: TimerState = {
        mode: prev.mode,
        isRunning: false,
        isFocus: nextIsFocus,
        timeRemaining: dur,
        endAt: null,
        sessionsCompleted: wasFocus ? prev.sessionsCompleted + 1 : prev.sessionsCompleted,
      };
      persistState(next);
      return next;
    });
  }, [clearIntervalRef]);

  const value = useMemo<PomodoroContextValue>(() => ({
    state: liveState,
    analytics,
    start,
    pause,
    reset,
    skip,
    setMode,
    finish,
    stop,
  }), [liveState, analytics, start, pause, reset, skip, setMode, finish, stop]);

  return <PomodoroContext.Provider value={value}>{children}</PomodoroContext.Provider>;
}

export function usePomodoro(): PomodoroContextValue {
  const ctx = useContext(PomodoroContext);
  if (!ctx) throw new Error("usePomodoro must be used within PomodoroProvider");
  return ctx;
}

// Legacy wrapper for pages that relied on default hook behavior without provider - now just re-exports context hook
export function usePomodoroStore() {
  return usePomodoro();
}

export function PomodoroTimer({ compact = true }: { compact?: boolean }) {
  const { state, start, pause } = usePomodoro();
  const [open, setOpen] = useState(false);
  const display = useMemo(() => formatTime(state.timeRemaining), [state.timeRemaining]);

  return (
    <>
      <button
        type="button"
        aria-label={state.isRunning ? "Pause focus timer" : "Start focus timer"}
        onClick={() => {
          if (state.isRunning) pause();
          else start();
        }}
        className="inline-flex items-center gap-1.5 rounded-md border border-[var(--border)] bg-[var(--card)] px-2.5 py-1.5 text-xs font-medium hover:border-[var(--accent)]"
      >
        {state.isRunning ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
        <span className="font-mono">{display}</span>
        <span className="hidden sm:inline text-[var(--muted)]">{state.isFocus ? "Focus" : "Break"}</span>
      </button>
      <button
        type="button"
        aria-label="Open focus mode"
        onClick={() => setOpen(true)}
        className="rounded-md p-1.5 text-[var(--muted)] hover:bg-[var(--card-2)]"
      >
        <Settings2 className="h-4 w-4" />
      </button>
      {open ? <FocusModePanel onClose={() => setOpen(false)} /> : null}
      {!compact ? <div className="hidden" /> : null}
    </>
  );
}

export function FocusModePanel({ onClose }: { onClose?: () => void }) {
  const { state, analytics, start, pause, reset, skip, setMode } = usePomodoro();
  const display = useMemo(() => formatTime(state.timeRemaining), [state.timeRemaining]);
  const maxTime = state.isFocus ? MODES[state.mode].focus : MODES[state.mode].breakTime;
  const progress = Math.max(0, Math.min(1, 1 - state.timeRemaining / maxTime));

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-6 bg-[var(--background)]/95 backdrop-blur p-6">
      {onClose ? (
        <button type="button" aria-label="Close focus mode" onClick={onClose} className="absolute right-4 top-4 rounded-md p-2 hover:bg-[var(--card)]">
          <X className="h-5 w-5" />
        </button>
      ) : null}
      <div className="text-center">
        <p className="text-xs uppercase tracking-[0.14em] text-[var(--muted)]">{state.isFocus ? "Focus" : "Break"} · {MODES[state.mode].label}</p>
        <div className="mt-2 font-mono text-7xl font-bold tracking-tight text-[var(--foreground)] sm:text-8xl">{display}</div>
        <p className="mt-2 text-sm text-[var(--muted)]">Sessions completed: {state.sessionsCompleted} · Today: {analytics.todayMinutes} min · Total: {analytics.totalFocusMinutes} min</p>
        <p className="mt-1 text-xs text-[var(--muted)]">{state.isRunning ? "Running" : "Paused"} {state.isRunning ? "· end time persisted" : ""}</p>
      </div>

      <div className="h-1.5 w-72 max-w-full overflow-hidden rounded-full bg-[var(--border)]">
        <div className="h-full bg-[var(--accent)] transition-all" style={{ width: `${progress * 100}%` }} />
      </div>

      <div className="flex flex-wrap items-center justify-center gap-2">
        {(Object.keys(MODES) as PomodoroMode[]).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={`rounded-md border px-2.5 py-1 text-xs ${state.mode === m ? "border-[var(--accent)] bg-[var(--accent)] text-[var(--accent-fg)]" : "border-[var(--border)] bg-[var(--card)]"}`}
          >
            {m}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap gap-3">
        <button type="button" className="inline-flex items-center gap-2 rounded-lg bg-[var(--accent)] px-5 py-2.5 text-sm font-medium text-[var(--accent-fg)] hover:opacity-90" onClick={() => (state.isRunning ? pause() : start())}>
          {state.isRunning ? <><Pause className="h-4 w-4" /> Pause</> : <><Play className="h-4 w-4" /> {state.timeRemaining === maxTime ? "Start" : "Resume"}</>}
        </button>
        <button type="button" className="inline-flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2.5 text-sm" onClick={reset}>
          <RotateCcw className="h-4 w-4" /> Reset
        </button>
        <button type="button" className="inline-flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2.5 text-sm" onClick={skip}>
          <SkipForward className="h-4 w-4" /> Skip
        </button>
      </div>

      <p className="max-w-sm text-center text-xs text-[var(--muted)]">Timer persists across navigation/refresh via localStorage. Changing mode or pressing Reset fully stops the timer. Browser notification + beep on completion.</p>
    </div>
  );
}

export function FocusAnalyticsWidget() {
  const { analytics } = usePomodoro();
  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3">
      <p className="text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Focus today</p>
      <p className="mt-1 text-lg font-semibold">{analytics.todayMinutes} min · {analytics.sessionsCompleted} sessions</p>
      <p className="text-xs text-[var(--muted)]">Started {analytics.sessionsStarted} · Total {analytics.totalFocusMinutes} min</p>
    </div>
  );
}
