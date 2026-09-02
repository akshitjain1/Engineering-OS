/* -------------------------------------------------------------------------
 * The prompt you hand an AI when a problem has you stuck.
 *
 * This replaces a link to LeetCode's community solutions. That link answered
 * the wrong question: it shows you *an* answer, and reading an answer you did
 * not reach yourself teaches almost nothing. What is actually missing when you
 * are stuck is the chain of reasoning that makes the technique the obvious move
 * -- and that is what this asks for, in that order, with the code last.
 *
 * Ordering is the whole design. Concepts, then the problem in plain words, then
 * the brute force and why it falls short, then the derivation, then the code.
 * A tutor that opens with the code has skipped everything worth having.
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

const bullet = (label: string, value: string | null | undefined) =>
  value ? `  ${label}: ${value}` : null;

export function buildStuckPrompt(ctx: StuckContext): string {
  const lang = ctx.language || "Java";

  const context = [
    bullet("Problem", `${ctx.problemTitle}${ctx.difficulty ? ` (${ctx.difficulty})` : ""}`),
    bullet("Link", ctx.problemUrl),
    bullet("Topic I am studying", ctx.topicName),
    bullet("The technique this topic teaches", ctx.technique),
    bullet("Concepts this problem is tagged with", ctx.concepts.length ? ctx.concepts.join(", ") : null),
    bullet("What I just read", ctx.sourceUrl ? `${ctx.sourceTitle ?? "my source"} — ${ctx.sourceUrl}` : ctx.sourceTitle),
    bullet("Why this problem was picked for this topic", ctx.whyThisProblem),
  ].filter(Boolean).join("\n");

  return `I am learning data structures and algorithms and I am stuck on the problem below.
Teach it to me. Do not open with the answer.

WHERE I AM
${context}

WHAT I WANT BACK
One single reply containing all eight sections, in this exact order. Do not
reorder them, and do not put code anywhere except section 7.

1. CONCEPTS I NEED FIRST
   Every concept required before this problem can make sense. For each one: what
   it is, why it exists, and the single sentence worth remembering. Assume I know
   ${lang} syntax but not this technique. Do not skip a concept for being obvious.

2. THE PROBLEM IN PLAIN WORDS
   Restate it without the puzzle framing. What is the input really, what is the
   output really, and which constraint is the one that actually decides the
   approach?

3. THE OBVIOUS ATTEMPT, AND WHERE IT BREAKS
   The brute force I would reach for first, written as steps. Its time and space
   cost, and the specific reason it is not good enough here — or that it is fine,
   if it genuinely is.

4. THE REASONING THAT LEADS TO THE REAL APPROACH
   This is the section I care about most. Walk me from the brute force to the
   intended technique as a chain of reasoning: what do you notice about the
   input, what question does that raise, and what makes this technique the
   natural answer rather than a trick someone memorised? Do not just assert
   "use ${ctx.technique ? ctx.technique.toLowerCase() : "the technique"}" — show me the
   step that makes it inevitable, so I can re-derive it on a problem I have never
   seen.

5. THE APPROACH AS STEPS
   The algorithm in plain words or pseudocode. State the invariant — the thing
   that stays true on every iteration — and list the edge cases most people get
   wrong here.

6. COMPLEXITY
   Time and space, with the reasoning that produces them, not just the letters.

7. ${lang.toUpperCase()} CODE — LAST, AFTER EVERYTHING ABOVE
   Clean, idiomatic ${lang}. Comment the lines that encode an idea; leave the
   lines that are only syntax uncommented.

8. WHETHER IT STUCK
   Two or three other problems that use the same technique — name and LeetCode
   number — and one sentence each on what they change. Then one question about
   this problem I should be able to answer if I actually understood it.

Be direct and concise. No encouragement, no filler, no restating this prompt.`;
}
