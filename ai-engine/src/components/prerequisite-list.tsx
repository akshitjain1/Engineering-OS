import type { PrerequisiteItem } from "@/lib/curriculum";

export function PrerequisiteList({
  items,
  message,
}: {
  items: PrerequisiteItem[];
  message?: string | null;
}) {
  if (!items.length) {
    return <p className="text-sm text-[var(--muted)]">No prerequisites.</p>;
  }
  return (
    <div>
      <p className="text-sm font-medium">Prerequisite status</p>
      <ul className="mt-2 space-y-1 text-sm">
        {items.map((item) => (
          <li key={item.name} className="flex gap-2">
            <span aria-hidden="true">{item.complete ? "✓" : "○"}</span>
            <span className={item.complete ? "" : "text-[var(--muted)]"}>
              {item.name}
              {!item.found ? " (missing from curriculum)" : ""}
            </span>
          </li>
        ))}
      </ul>
      {message ? <p className="mt-2 text-sm text-amber-900 dark:text-amber-100">{message}</p> : null}
    </div>
  );
}
