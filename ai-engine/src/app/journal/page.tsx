import { Page, PageTitle } from "@/components/study-ui";

export default function JournalPage() {
  return (
    <Page wide>
      <PageTitle kicker="Journal" title="Learning journal" description="Capture what you learned today. Daily plan already includes a journal block." />
      <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
        <div className="border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-sm font-semibold">Today</h2>
          <textarea placeholder="What did you learn? What was hard? What will you do tomorrow?" rows={8} className="mt-3 w-full rounded-md border border-[var(--border)] bg-[var(--background)] p-3 text-sm" />
          <p className="mt-2 text-xs text-[var(--muted)]">Local draft — save in browser. Full persistence is future work.</p>
        </div>
        <div className="border border-[var(--border)] bg-[var(--card-2)] p-5 text-sm text-[var(--muted)]">
          <h3 className="font-semibold text-[var(--foreground)]">This week</h3>
          <p className="mt-2">Entries will appear here when journal storage is added. For now use Today&apos;s plan journal block.</p>
        </div>
      </div>
    </Page>
  );
}
