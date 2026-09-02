/* -------------------------------------------------------------------------
 * The prompt you hand an AI when a problem has you stuck.
 *
 * This replaces a link to LeetCode's community solutions. That link answered
 * the wrong question: it shows you *an* answer, and reading an answer you did
 * not reach yourself teaches almost nothing. What is missing when you are stuck
 * is the reasoning that makes the technique the obvious move.
 *
 * Three things are load-bearing, and the first two pull against each other:
 *
 *   Order. Concepts, problem, approaches, insight, plan, pseudocode, dry run,
 *   then code. A tutor that opens with code has skipped everything worth
 *   having, so real code is pinned to one late section.
 *
 *   Brevity. The first version of this asked for depth and got a wall -- a
 *   reply that explained what an array and an index are to someone who writes
 *   Java, then buried the one useful paragraph inside it. Length is not
 *   thoroughness; it is what you get when nothing is budgeted. So every section
 *   now has a hard cap, most are tables rather than prose, and exactly one
 *   section is allowed to be prose, because that is the section doing the
 *   teaching. Anything a working programmer already knows is cut by
 *   instruction, not left to taste.
 *
 *   The bridge. Knowing the answer and being able to write it are different
 *   skills, and a reply that jumps from a paragraph of insight straight to
 *   finished code teaches only the first. Pseudocode and a dry run sit in
 *   between: one shows how the plan becomes structure, the other shows what
 *   that structure actually does on the input that is hard. The dry run traces
 *   the pseudocode rather than the code, so it validates the plan before any
 *   syntax exists to hide behind.
 * ---------------------------------------------------------------------- */

export type StuckContext = {
  /** Canonical LeetCode title, e.g. "125. Valid Palindrome". */
  problemTitle: string;
  problemUrl: string | null;
  difficulty: string | null;
  /** The technique the topic teaches, from the mapping. */
  technique: string | null;
  /** Verified concept tags this problem was matched on. */
  concepts: string[];
  /** Why this problem was chosen for this topic. */
  whyThisProblem: string | null;
  topicName: string;
  sourceTitle: string | null;
  sourceUrl: string | null;
  /** Language for the code section. */
  language: string;
};

const line = (label: string, value: string | null | undefined) =>
  value ? `  ${label}: ${value}` : null;

export function buildStuckPrompt(ctx: StuckContext): string {
  const lang = ctx.language || "Java";

  const context = [
    line("Problem", `${ctx.problemTitle}${ctx.difficulty ? ` (${ctx.difficulty})` : ""}`),
    line("Link", ctx.problemUrl),
    line("Topic", ctx.topicName),
    line("Technique it teaches", ctx.technique),
    line("Tagged concepts", ctx.concepts.length ? ctx.concepts.join(", ") : null),
    line("What I just read", ctx.sourceUrl ? `${ctx.sourceTitle ?? "my source"} — ${ctx.sourceUrl}` : ctx.sourceTitle),
    line("Why it was picked for this topic", ctx.whyThisProblem),
  ].filter(Boolean).join("\n");

  return `I am stuck on the problem below. Teach me the reasoning. Do not open with the answer.

CONTEXT
${context}

RULES — these matter as much as the content
- Follow the structure below exactly. Do not add, merge, or reorder sections.
- Under 800 words total, not counting the two code blocks. Shorter is better.
- Use markdown tables where specified. Section 4 is the ONLY prose section.
- I already write ${lang}. Never explain arrays, loops, indexing, classes or syntax.
- Delete any row a working programmer would already know. Three sharp rows beat
  eight obvious ones. Row limits are maximums, not targets.
- One line means one line. No sub-bullets inside table cells.
- No preamble, no closing summary, no encouragement, no restating these rules.

1. CONCEPTS — table, max 4 rows
| Concept | In one line | Why this problem needs it |
Only ideas specific to this technique. If two suffice, give two.

2. PROBLEM — max 2 lines
The real input, the real output, and the one constraint that decides the approach.

3. APPROACHES — table, 2-3 rows
| Approach | Idea in one line | Time | Space | Verdict |
Include the brute force and the intended approach. Verdict says why it is
rejected or chosen — not what it does.

4. THE KEY INSIGHT — prose, 120 words max, the only prose in your reply
The single realisation that turns the brute force into the intended approach.
Show the step that makes it inevitable, so I can re-derive it on a problem I
have never seen. Naming ${ctx.technique ? `"${ctx.technique}"` : "the technique"} is not an insight — what forces it?

5. PLAN — numbered steps, max 8 lines
The approach in plain words, before any syntax. Then one final line beginning
"INVARIANT:" stating what stays true on every iteration.

6. PSEUDOCODE — a code block, max 15 lines
Language-neutral: no ${lang} types, no library calls, no imports. Name the
variables you would actually use, so this is the thing I could translate into
${lang} myself. This is the bridge between the plan and real code — it must be
complete enough to run in my head, and that is what section 7 does to it.

7. DRY RUN — table, max 8 rows
| Step | <state variables from the pseudocode> | What happens |
Trace the PSEUDOCODE above, not the ${lang}. Use the input that actually
exercises the difficulty — never the trivial case that finishes on step one.
State the chosen input on the line above the table, and the returned value on
the line below it.

8. EDGE CASES — table, max 4 rows
| Case | What goes wrong | How the algorithm handles it |
Only cases that actually bite here.

9. ${lang.toUpperCase()} — the only real code in your reply
Idiomatic ${lang}, a direct translation of the pseudocode. Comment a line only
where it encodes an idea, never syntax.

10. REMEMBER — exactly 3 bullets, max 15 words each
- Trigger: when I see <signal in the problem>, reach for <technique>
- Invariant: <the one line that keeps it correct>
- Cost: <time and space>
Then one line beginning "RECALL:" — a question I should be able to answer from
memory tomorrow without re-reading any of this. Not a definition; something that
only means anything if I understood the insight.

11. NEXT — table, exactly 3 rows
| Problem | LeetCode # | What it changes |`;
}
