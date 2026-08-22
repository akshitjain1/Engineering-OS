import { EmptyState, Page, PageTitle } from "@/components/study-ui";

export default function JournalPage() {
  return (
    <Page>
      <PageTitle kicker="Journal" title="Learning journal" description="The daily plan already includes a journal block. A full journal database is not part of this polish pass." />
      <EmptyState title="No journal entries stored yet" body="Use the journal item in today’s plan, or wait for a later capture tool. Nothing is fabricated here." />
    </Page>
  );
}
