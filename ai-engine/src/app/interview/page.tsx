import { EmptyState, Page, PageTitle } from "@/components/study-ui";

export default function InterviewPage() {
  return (
    <Page>
      <PageTitle kicker="Interview" title="Not in this phase" description="No AI interviewer. Use topic assessments and transfer tasks until a later interview mode exists." />
      <EmptyState title="No interview sessions stored" body="Diagnostic and topic assessments are the current evidence path." />
    </Page>
  );
}
