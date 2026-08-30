import { Page, PageTitle } from "@/components/study-ui";
import Link from "next/link";

export default function DSAPage() {
  return (
    <Page wide>
      <PageTitle kicker="DSA" title="DSA workspace" description="Patterns, problems, and progress from the Engineering OS roadmap Domain 2." />
      <div className="grid gap-6 lg:grid-cols-3">
        <section className="border border-[var(--border)] bg-[var(--card)] p-5"><h3 className="text-sm font-bold">DSA progress</h3><p className="mt-2 text-sm text-[var(--muted)]">106 topics on roadmap. Track completion in Progress and Roadmap → Domain 2.</p><Link href="/roadmap" className="mt-3 inline-block text-sm font-medium text-[var(--accent)] hover:underline">Open Roadmap →</Link></section>
        <section className="border border-[var(--border)] bg-[var(--card)] p-5"><h3 className="text-sm font-bold">Today&apos;s problems</h3><p className="mt-2 text-sm text-[var(--muted)]">Mapped PRACTICE resources appear on the current topic and Practice page.</p><Link href="/practice" className="mt-3 inline-block text-sm font-medium text-[var(--accent)] hover:underline">Open Practice →</Link></section>
        <section className="border border-[var(--border)] bg-[var(--card)] p-5"><h3 className="text-sm font-bold">Continue DSA</h3><p className="mt-2 text-sm text-[var(--muted)]">Open the current DSA topic from Learn.</p><Link href="/learn" className="mt-3 inline-block text-sm font-medium text-[var(--accent)] hover:underline">Open Topics →</Link></section>
      </div>
    </Page>
  );
}
