import { EmptyState, Page, PageTitle } from "@/components/study-ui";

export default function ResourcesPage() {
  return (
    <Page>
      <PageTitle kicker="Resources" title="Sources live on topics" description="Open a topic to see PRIMARY, REFERENCE, and PRACTICE. A global library dump would recreate search friction." />
      <EmptyState title="Use the topic workspace" body="Start from Today or Learn. Exact URLs are stored per topic, not as a giant table." />
    </Page>
  );
}
