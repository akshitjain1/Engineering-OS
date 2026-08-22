"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Today" },
  { href: "/tracks", label: "Tracks" },
  { href: "/roadmap", label: "Roadmap" },
  { href: "/projects", label: "Projects" },
  { href: "/learn", label: "Learn" },
  { href: "/practice", label: "Practice" },
  { href: "/resources", label: "Resources" },
  { href: "/settings", label: "Settings" },
];

const MOBILE = [
  { href: "/dashboard", label: "Today" },
  { href: "/tracks", label: "Tracks" },
  { href: "/roadmap", label: "Roadmap" },
  { href: "/projects", label: "Projects" },
  { href: "/learn", label: "Learn" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const toggle = () => {
    setCollapsed((value) => {
      const next = !value;
      window.localStorage.setItem("eos-sidebar-collapsed", next ? "1" : "0");
      return next;
    });
  };

  return (
    <div className="min-h-full bg-[var(--background)] text-[var(--foreground)]">
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 hidden border-r border-[var(--border)] bg-[var(--card)] md:flex md:flex-col",
          collapsed ? "w-[72px]" : "w-56",
        )}
      >
        <div className="flex h-14 items-center justify-between px-3">
          <Link href="/dashboard" className="flex items-center gap-2 text-sm font-semibold tracking-tight">
            <span className="h-2 w-2 rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-2)]" />
            {collapsed ? "EOS" : "Engineering OS"}
          </Link>
          <button
            type="button"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="rounded-md p-1.5 text-[var(--muted)] hover:bg-[var(--card-2)] hover:text-[var(--foreground)]"
            onClick={toggle}
          >
            {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          </button>
        </div>
        <nav className="flex-1 space-y-0.5 overflow-y-auto px-2 pb-4" aria-label="Primary">
          {NAV.map((item) => {
            const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "block rounded-md px-2.5 py-2 text-sm transition-colors",
                  active
                    ? "bg-[var(--accent)] font-medium text-[var(--accent-fg)] shadow-[0_0_18px_-6px_var(--accent)]"
                    : "text-[var(--muted)] hover:bg-[var(--card-2)] hover:text-[var(--foreground)]",
                )}
              >
                {collapsed ? item.label.slice(0, 2) : item.label}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className={cn("flex min-h-full flex-col", collapsed ? "md:pl-[72px]" : "md:pl-56")}>
        <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-[var(--border)] bg-[var(--background)]/90 px-4 backdrop-blur md:px-6">
          <div className="flex items-center gap-2 md:hidden">
            <button
              type="button"
              aria-label="Open menu"
              className="rounded-md p-2"
              onClick={() => setMobileOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </button>
            <Link href="/dashboard" className="text-sm font-semibold">
              Engineering OS
            </Link>
          </div>
          <p className="hidden text-sm text-[var(--muted)] md:block">Personal learning navigator</p>
          <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
            <span className="hidden rounded-full bg-[var(--card-2)] px-2.5 py-1 sm:inline">Source-first · study navigator</span>
          </div>
        </header>

        {mobileOpen ? (
          <div className="fixed inset-0 z-50 md:hidden">
            <button
              type="button"
              className="absolute inset-0 bg-black/40"
              aria-label="Close menu"
              onClick={() => setMobileOpen(false)}
            />
            <div className="absolute inset-y-0 left-0 w-64 bg-[var(--card)] p-4 shadow-sm">
              <p className="mb-4 text-sm font-semibold">Engineering OS</p>
              <nav className="space-y-1" aria-label="Mobile">
                {NAV.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="block rounded-md px-2 py-2 text-sm"
                    onClick={() => setMobileOpen(false)}
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        ) : null}

        <main className="flex-1 pb-20 md:pb-8">{children}</main>

        <nav
          className="fixed inset-x-0 bottom-0 z-30 flex border-t border-[var(--border)] bg-[var(--card)] md:hidden"
          aria-label="Mobile primary"
        >
          {MOBILE.map((item) => {
            const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex-1 py-3 text-center text-xs",
                  active ? "font-semibold text-[var(--foreground)]" : "text-[var(--muted)]",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
