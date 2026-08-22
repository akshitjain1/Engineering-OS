import Link from "next/link";
import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

export function Page({
  children,
  wide,
}: {
  children: ReactNode;
  wide?: boolean;
}) {
  return (
    <div className={cn("mx-auto w-full px-4 py-8 sm:px-6", wide ? "max-w-3xl" : "max-w-[42rem]")}>
      {children}
    </div>
  );
}

export function PageTitle({
  kicker,
  title,
  description,
}: {
  kicker?: string;
  title: string;
  description?: string;
}) {
  return (
    <header className="mb-8">
      {kicker ? <p className="text-xs font-medium uppercase tracking-[0.14em] text-[var(--muted)]">{kicker}</p> : null}
      <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[var(--foreground)]">{title}</h1>
      {description ? <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">{description}</p> : null}
    </header>
  );
}

export function Banner({
  tone = "error",
  children,
}: {
  tone?: "error" | "info";
  children: ReactNode;
}) {
  return (
    <p
      role="status"
      className={cn(
        "mb-6 rounded-lg border px-4 py-3 text-sm",
        tone === "error"
          ? "border-transparent bg-[var(--warn-soft)] text-[var(--foreground)]"
          : "border-[var(--border)] bg-[var(--card-2)] text-[var(--muted)]",
      )}
    >
      {children}
    </p>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-xl border border-dashed border-[var(--border)] px-6 py-10 text-center">
      <p className="font-medium">{title}</p>
      <p className="mt-2 text-sm text-[var(--muted)]">{body}</p>
    </div>
  );
}

export function LoadingLine({ label = "Loading…" }: { label?: string }) {
  return <p className="text-sm text-[var(--muted)]">{label}</p>;
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
      <span className={cn("rounded-full px-2 py-0.5 text-[11px] font-medium tracking-wide", tone[label] || tone.UNKNOWN)}>
        {label.replace("_", " ")}
      </span>
      {pace ? <span className="rounded-full bg-[var(--card-2)] px-2 py-0.5 text-[11px] text-[var(--muted)]">{pace}</span> : null}
    </span>
  );
}

export function PrimaryButton({
  href,
  children,
  onClick,
  disabled,
}: {
  href?: string;
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}) {
  const className =
    "inline-flex h-10 items-center justify-center rounded-lg bg-[var(--accent)] px-4 text-sm font-medium text-[var(--accent-fg)] transition-colors hover:opacity-90 disabled:opacity-50";
  if (href?.startsWith("/") || href?.startsWith("#")) {
    return (
      <Link href={href} className={className}>
        {children}
      </Link>
    );
  }
  if (href) {
    return (
      <a href={href} className={className} target="_blank" rel="noreferrer">
        {children}
      </a>
    );
  }
  return (
    <button type="button" className={className} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

export function GhostButton({
  href,
  children,
  onClick,
  disabled,
}: {
  href?: string;
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}) {
  const className =
    "inline-flex h-10 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 text-sm font-medium transition-colors hover:border-[var(--accent)] hover:text-[var(--foreground)] disabled:opacity-50";
  if (href?.startsWith("/") || href?.startsWith("#")) {
    return (
      <Link href={href} className={className}>
        {children}
      </Link>
    );
  }
  if (href) {
    return (
      <a href={href} className={className} target="_blank" rel="noreferrer">
        {children}
      </a>
    );
  }
  return (
    <button type="button" className={className} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}
