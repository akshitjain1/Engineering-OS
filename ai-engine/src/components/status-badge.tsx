import { cn } from "@/lib/utils";
import type { UiStatus } from "@/lib/curriculum";

const labels: Record<UiStatus, string> = {
  not_started: "Not started",
  in_progress: "In progress",
  completed: "Completed",
  locked: "Locked",
};

const styles: Record<UiStatus, string> = {
  not_started: "bg-[var(--card-2)] text-[var(--muted)]",
  in_progress: "bg-[var(--accent-soft)] text-[var(--accent)]",
  completed: "bg-[var(--ok-soft)] text-[var(--ok)]",
  locked: "bg-[var(--card-2)] text-[var(--muted)] opacity-70",
};

export function StatusBadge({ status }: { status: UiStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        styles[status],
      )}
    >
      {labels[status]}
    </span>
  );
}
