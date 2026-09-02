import type { Metadata } from "next";
import "./globals.css";

import { Geist, Geist_Mono } from "next/font/google";
import { AppShell } from "@/components/app-shell";
import { PomodoroProvider } from "@/components/pomodoro";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Engineering OS",
  description: "Personal learning navigator: the sequence, the source, practice, build, revise.",
};

/* `suppressHydrationWarning` on these two tags only.
 *
 * Browser extensions edit <html> and <body> before React hydrates -- Grammarly
 * stamps data-gr-ext-installed and data-new-gr-c-s-check-loaded onto <body>,
 * and password managers and theme extensions do the same kind of thing. The
 * server never sent those attributes, so React reports a mismatch that no
 * change to this app can prevent.
 *
 * The reason to silence it is not tidiness. An error that fires on every page
 * load teaches you to ignore the overlay, and a real hydration bug arrives
 * looking exactly like this one. A warning you always ignore is worse than no
 * warning.
 *
 * This is safe because it is narrow in two ways React guarantees: it applies
 * only to the element it is written on, never to descendants, and these two
 * elements carry nothing dynamic -- their className is a static string. There
 * is no mismatch of ours it could be hiding. Never put this on a component
 * that renders real data.
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body
        className="min-h-full bg-[var(--background)] font-sans text-[var(--foreground)]"
        suppressHydrationWarning
      >
        <PomodoroProvider>
          <AppShell>{children}</AppShell>
        </PomodoroProvider>
      </body>
    </html>
  );
}