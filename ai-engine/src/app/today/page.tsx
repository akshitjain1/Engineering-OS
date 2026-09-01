import { Page } from "@/components/study-ui";
import { DayRunner } from "@/components/day-runner";

export const metadata = { title: "Today — Engineering OS" };

export default function TodayPage() {
  return (
    <Page>
      <DayRunner />
    </Page>
  );
}
