import Link from "next/link";
import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

export function Page({ children, wide }: { children: ReactNode; wide?: boolean }) {
  return (
    <div className={cn("mx-auto w-full px-4 py-6 sm:px-6 lg:px-8", wide ? "max-w-[1440px]" : "max-w-[1280px]")}>
      {children}
    </div>
  );
}

export function PageTitle({ kicker, title, description }: { kicker?: string; title: string; description?: string }) {
  return (
    <header className="mb-8 border-b border-[var(--border)] pb-6">
      {kicker ? <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">{kicker}</p> : null}
      <h1 className="mt-2 text-[32px] font-bold tracking-tight leading-none sm:text-[36px]">{title}</h1>
      {description ? <p className="mt-3 max-w-3xl text-[15px] leading-relaxed text-[var(--muted)]">{description}</p> : null}
    </header>
  );
}

export function SectionHeader({ title, hint, action }: { title: string; hint?: string; action?: ReactNode }) {
  return (
    <div className="mb-4 flex items-start justify-between gap-4 border-b border-[var(--border)] pb-3">
      <div>
        <h2 className="text-[20px] font-semibold tracking-tight">{title}</h2>
        {hint ? <p className="mt-1 text-sm text-[var(--muted)]">{hint}</p> : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}

export function Banner({ tone = "error", children }: { tone?: "error" | "info"; children: ReactNode }) {
  return (
    <p role="status" className={cn("mb-6 rounded-lg border px-4 py-3 text-sm", tone === "error" ? "border-transparent bg-[var(--warn-soft)]" : "border-[var(--border)] bg-[var(--card-2)] text-[var(--muted)]")}>
      {children}
    </p>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-lg border border-dashed border-[var(--border)] bg-[var(--card)] px-6 py-10 text-center">
      <p className="font-semibold">{title}</p>
      <p className="mt-2 text-sm text-[var(--muted)]">{body}</p>
    </div>
  );
}

export function LoadingLine({ label = "Loading…" }: { label?: string }) {
  return <p className="text-sm text-[var(--muted)]">{label}</p>;
}

export function ProgressBar({ value, max = 100 }: { value: number; max?: number }) {
  const pct = max ? Math.round((value / max) * 100) : 0;
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--border)]">
      <div className="h-full rounded-full bg-[var(--accent)] transition-all" style={{ width: `${Math.min(100, Math.max(0, pct))}%` }} />
    </div>
  );
}

export function MasteryPill({ status, pace }: { status?: string | null; pace?: string | null }) {
  const label = status || "UNKNOWN";
  const tone: Record<string, string> = {
    MASTERED: "bg-[var(--ok-soft)] text-[var(--ok)]",
    FAMILIAR: "bg-[var(--accent-soft)] text-[var(--accent-2)]",
    LEARNING: "bg-[var(--accent-soft)] text-[var(--accent)]",
    NEEDS_REVIEW: "bg-[var(--warn-soft)] text-[var(--warn)]",
    LOCKED: "bg-[var(--card-2)] text-[var(--muted)]",
    UNKNOWN: "bg-[var(--card-2)] text-[var(--muted)]",
    CURRENT: "bg-[var(--accent)] text-[var(--accent-fg)]",
  };
  return (
    <span className="inline-flex flex-wrap items-center gap-1.5">
      <span className={cn("rounded-full px-2 py-0.5 text-[11px] font-medium tracking-wide", tone[label] || tone.UNKNOWN)}>{label.replace("_", " ")}</span>
      {pace ? <span className="rounded-full bg-[var(--card-2)] px-2 py-0.5 text-[11px] text-[var(--muted)]">{pace}</span> : null}
    </span>
  );
}

export function PrimaryButton({ href, children, onClick, disabled }: { href?: string; children: ReactNode; onClick?: () => void; disabled?: boolean }) {
  const className = "inline-flex h-9 items-center justify-center rounded-md bg-[var(--accent)] px-4 text-sm font-medium text-[var(--accent-fg)] hover:bg-[var(--accent-hover)] disabled:opacity-50 transition-colors";
  if (href?.startsWith("/") || href?.startsWith("#")) return <Link href={href} className={className}>{children}</Link>;
  if (href) return <a href={href} className={className} target="_blank" rel="noreferrer">{children}</a>;
  return <button type="button" className={className} onClick={onClick} disabled={disabled}>{children}</button>;
}

export function GhostButton({ href, children, onClick, disabled }: { href?: string; children: ReactNode; onClick?: () => void; disabled?: boolean }) {
  const className = "inline-flex h-9 items-center justify-center rounded-md border border-[var(--border)] bg-[var(--card)] px-4 text-sm font-medium hover:border-[var(--border-strong)] disabled:opacity-50 transition-colors";
  if (href?.startsWith("/") || href?.startsWith("#")) return <Link href={href} className={className}>{children}</Link>;
  if (href) return <a href={href} className={className} target="_blank" rel="noreferrer">{children}</a>;
  return <button type="button" className={className} onClick={onClick} disabled={disabled}>{children}</button>;
}

export function Breadcrumbs({ items }: { items: { label: string; href?: string }[] }) {
  return (
    <nav aria-label="Breadcrumb" className="text-sm text-[var(--muted)]">
      <ol className="flex flex-wrap items-center gap-1.5">
        {items.map((item, i) => (
          <li key={i} className="flex items-center gap-1.5">
            {i > 0 ? <span className="text-[var(--muted-2)]">/</span> : null}
            {item.href ? <Link href={item.href} className="hover:text-[var(--foreground)] hover:underline">{item.label}</Link> : <span className="text-[var(--foreground)]">{item.label}</span>}
          </li>
        ))}
      </ol>
    </nav>
  );
}
