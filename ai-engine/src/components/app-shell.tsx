"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Menu, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { cn } from "@/lib/utils";
import { PomodoroTimer } from "./pomodoro";

// Five destinations, not thirteen.
//
// The old menu listed Practice, Revision, Interview, Journal, Tracks and
// Resources as top-level routes, but four of them were static link pages and
// the other two are views of data you already reach from Today or Learn.
// Everything that is actually a step in the day now happens inside /today.
const NAV_GROUPS = [
  {
    label: "Do",
    items: [
      { href: "/today", label: "Today" },
      { href: "/dsa", label: "DSA" },
    ],
  },
  {
    label: "Browse",
    items: [
      { href: "/learn", label: "Topics" },
      { href: "/roadmap", label: "Roadmap" },
    ],
  },
  {
    label: "Review",
    items: [
      // Grading a recall is what moves its next review date, and this page is
      // the only place that grading exists. It was reachable only by typing the
      // URL, which meant a REVIEW block could ask you to grade yourself with
      // nowhere to do it -- and an ungraded item just comes back unchanged.
      { href: "/revision", label: "Review queue" },
      { href: "/progress", label: "Progress" },
      { href: "/settings", label: "Settings" },
    ],
  },
];

const MOBILE_PRIMARY = [
  { href: "/today", label: "Today" },
  { href: "/dsa", label: "DSA" },
  { href: "/learn", label: "Topics" },
  { href: "/roadmap", label: "Roadmap" },
  { href: "/progress", label: "Progress" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    let next = false;
    try {
      const v = localStorage.getItem("eos-sidebar-collapsed");
      next = v === "1";
    } catch { /* ignore */ }
    if (next) {
      // defer to avoid setState-in-effect lint rule while preserving hydration correctness
      const t = window.setTimeout(() => setCollapsed(true), 0);
      return () => window.clearTimeout(t);
    }
  }, []);

  const toggle = () => {
    setCollapsed((value) => {
      const next = !value;
      try { localStorage.setItem("eos-sidebar-collapsed", next ? "1" : "0"); } catch { /* ignore */ }
      return next;
    });
  };

  const currentLabel = (() => {
    for (const g of NAV_GROUPS) for (const it of g.items) if (pathname === it.href || (it.href !== "/today" && pathname.startsWith(it.href))) return it.label;
    return "Engineering OS";
  })();

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <aside className={cn("fixed inset-y-0 left-0 z-40 hidden border-r border-[var(--border)] bg-[var(--card)] md:flex md:flex-col", collapsed ? "w-[72px]" : "w-[240px]")}>
        <div className="flex h-[56px] items-center justify-between border-b border-[var(--border)] px-3">
          <Link href="/today" className="flex items-center gap-2 text-sm font-bold tracking-tight">
            <span className="h-2.5 w-2.5 rounded-full bg-[var(--accent)]" />
            {collapsed ? "EOS" : "Engineering OS"}
          </Link>
          <button type="button" aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"} className="rounded-md p-1.5 text-[var(--muted)] hover:bg-[var(--card-2)]" onClick={toggle}>
            {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          </button>
        </div>
        <nav className="flex-1 overflow-y-auto px-2 py-3" aria-label="Primary">
          {NAV_GROUPS.map((group) => (
            <div key={group.label} className="mb-4">
              {!collapsed && <p className="px-2 py-1 text-[11px] font-semibold uppercase tracking-widest text-[var(--muted)]">{group.label}</p>}
              <ul className="space-y-0.5">
                {group.items.map((item) => {
                  const active = pathname === item.href || (item.href !== "/today" && pathname.startsWith(item.href));
                  return (
                    <li key={item.href}>
                      <Link href={item.href} title={item.label} className={cn("flex items-center rounded-md px-2.5 py-2 text-sm transition-colors", active ? "bg-[var(--accent)] font-medium text-[var(--accent-fg)]" : "text-[var(--muted)] hover:bg-[var(--card-2)] hover:text-[var(--foreground)]")}>
                        {collapsed ? item.label.slice(0, 2) : item.label}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>
        <div className="border-t border-[var(--border)] p-3">
          {!collapsed ? (
            <div className="rounded-md bg-[var(--card-2)] px-3 py-2">
              <p className="text-xs font-medium">Focus</p>
              <div className="mt-1"><PomodoroTimer /></div>
            </div>
          ) : (
            <div className="flex justify-center"><PomodoroTimer /></div>
          )}
        </div>
      </aside>

      <div className={cn("flex min-h-screen flex-col", collapsed ? "md:pl-[72px]" : "md:pl-[240px]")}>
        <header className="sticky top-0 z-30 flex h-[56px] items-center justify-between border-b border-[var(--border)] bg-[var(--card)]/95 px-4 backdrop-blur md:px-6">
          <div className="flex items-center gap-3">
            <button type="button" aria-label="Open menu" className="rounded-md p-2 md:hidden" onClick={() => setMobileOpen(true)}><Menu className="h-5 w-5" /></button>
            <span className="hidden text-sm font-medium text-[var(--muted)] md:block">{currentLabel}</span>
            <span className="text-sm font-semibold md:hidden">Engineering OS</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex"><PomodoroTimer /></div>
            <Link href="/settings" className="rounded-md border border-[var(--border)] px-3 py-1.5 text-xs font-medium hover:bg-[var(--card-2)]">Settings</Link>
          </div>
        </header>

        {mobileOpen ? (
          <div className="fixed inset-0 z-50 md:hidden">
            <button type="button" className="absolute inset-0 bg-black/30" aria-label="Close menu" onClick={() => setMobileOpen(false)} />
            <div className="absolute inset-y-0 left-0 w-64 bg-[var(--card)] p-4 shadow-lg">
              <p className="mb-4 text-sm font-bold">Engineering OS</p>
              <nav className="space-y-3" aria-label="Mobile">
                {NAV_GROUPS.map((group) => (
                  <div key={group.label}>
                    <p className="px-2 py-1 text-xs font-semibold uppercase tracking-widest text-[var(--muted)]">{group.label}</p>
                    {group.items.map((item) => (
                      <Link key={item.href} href={item.href} className="block rounded-md px-2 py-2 text-sm hover:bg-[var(--card-2)]" onClick={() => setMobileOpen(false)}>{item.label}</Link>
                    ))}
                  </div>
                ))}
              </nav>
            </div>
          </div>
        ) : null}

        <main className="flex-1 pb-20 md:pb-6">{children}</main>

        <nav className="fixed inset-x-0 bottom-0 z-30 flex border-t border-[var(--border)] bg-[var(--card)] md:hidden" aria-label="Mobile primary">
          {MOBILE_PRIMARY.map((item) => {
            const active = pathname === item.href || (item.href !== "/today" && pathname.startsWith(item.href));
            return <Link key={item.href} href={item.href} className={cn("flex-1 py-3 text-center text-xs", active ? "font-semibold text-[var(--foreground)]" : "text-[var(--muted)]")}>{item.label}</Link>;
          })}
        </nav>
      </div>
    </div>
  );
}
