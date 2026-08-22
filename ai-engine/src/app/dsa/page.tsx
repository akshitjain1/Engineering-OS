import { EmptyState, Page, PageTitle } from "@/components/study-ui";

export default function DSAPage() {
  return (
    <Page>
      <PageTitle
        kicker="DSA"
        title="Patterns live on the official sequence"
        description="Domain 2 is 106 topics on the Engineering OS roadmap. Use Learn and Practice rather than a separate dump of NeetCode 150."
      />
      <EmptyState
        title="Use the DSA domain on the roadmap"
        body="Open Roadmap → Domain 2, or start from Today if the planner has reached DSA."
      />
    </Page>
  );
}
