import { Page, PageTitle } from "@/components/study-ui";
import Link from "next/link";

export default function InterviewPage() {
  return (
    <Page wide>
      <PageTitle kicker="Interview" title="Interview readiness" description="Focused preparation across DSA, Java, system design, and ML/AI." />
      <div className="grid gap-6 lg:grid-cols-2">
        {[
          { title: "DSA", desc: "Patterns and problem solving", href: "/dsa" },
          { title: "Java", desc: "Core Java and OOP", href: "/tracks" },
          { title: "System design", desc: "AI Engineering + System Design phase", href: "/roadmap" },
          { title: "ML/AI", desc: "Model, evaluation, and GenAI", href: "/progress" },
        ].map((c) => (
          <section key={c.title} className="border border-[var(--border)] bg-[var(--card)] p-5"><h3 className="font-semibold">{c.title}</h3><p className="mt-1 text-sm text-[var(--muted)]">{c.desc}</p><Link href={c.href} className="mt-2 inline-block text-xs font-medium text-[var(--accent)] hover:underline">Open →</Link></section>
        ))}
      </div>
    </Page>
  );
}
