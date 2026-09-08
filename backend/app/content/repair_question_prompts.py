"""Repair individual questions whose prompt says nothing on its own.

A handful of questions predating the authored banks are substantively correct
-- the right answer and the distractors are genuinely about their topic -- but
their prompt is a bare fragment:

    Stable?
    Common bug?
    Common mistake?
    Stack vs heap at programmer level:

Two problems follow. The prompt does not say what is being asked, so reading it
in a revision queue away from the topic page tells you nothing. And because the
fragment carries no topic, the same four characters appear on four different
sorting topics, which is the cross-topic collision the authored banks now
forbid outright.

These topics also hold other, good questions, so the bank importer is the wrong
tool: it replaces every question on a topic it touches. This updates the
specific rows and leaves their neighbours alone.

While rewriting the prompts, two other faults in the same rows are fixed:
options that gave the answer away by being three times longer than the
distractors, and explanations too short to say why the wrong answers are wrong.
Each repair is run through the same validator the authored banks pass.

Run:
    python -m app.content.repair_question_prompts --dry-run
    python -m app.content.repair_question_prompts
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from app.content.question_bank import AuthoredQuestion, _validate_question

BACKEND = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND / "dev.db"
REPORTS = BACKEND / "reports"


#: resource id -> the replacement. Keyed by question id because the prompt being
#: replaced is not unique, which is the whole problem.
REPAIRS: dict[int, dict] = {
    842: {
        "topic": "dsa-binary-search-classic",
        "prompt": "In a classic binary search over a sorted array, which mistake most often causes an infinite loop?",
        "options": [
            "Updating lo or hi to mid instead of mid plus or minus one when the window stops shrinking",
            "Computing mid as lo plus hi minus lo over two rather than their plain average",
            "Searching an array that was sorted ascending rather than descending order",
            "Declaring mid as an int rather than a long on a very large input array",
        ],
        "answer": "Updating lo or hi to mid instead of mid plus or minus one when the window stops shrinking",
        "explanation": (
            "If the bound moves to mid and mid is already the bound, the window never narrows and "
            "the loop spins forever. The lo plus half-the-gap form is the overflow-safe idiom, not a "
            "bug. Sort direction changes the comparison but still terminates, and int versus long "
            "affects overflow rather than termination."
        ),
        "difficulty": "intermediate",
    },
    753: {
        "topic": "dsa-subsets",
        "prompt": "While collecting subsets during backtracking, what bug makes every stored subset come out identical?",
        "options": [
            "Storing the running path list itself, so all results alias one list that keeps mutating",
            "Storing a fresh copy of the path at each leaf, which duplicates memory unnecessarily",
            "Recursing before adding the current element rather than adding it before recursing",
            "Using an ArrayList for the path where a linked list would give cheaper appends",
        ],
        "answer": "Storing the running path list itself, so all results alias one list that keeps mutating",
        "explanation": (
            "Every result holds a reference to the same list, so backtracking's later removals show "
            "up in all of them; you need new ArrayList<>(path). Copying is the fix, not the bug. "
            "Recursion order changes which subsets appear when, and the list implementation only "
            "affects constant factors."
        ),
        "difficulty": "intermediate",
    },
    712: {
        "topic": "dsa-monotonic-stack",
        "prompt": "After a monotonic stack scan reaches the end of the array, which step is most often forgotten?",
        "options": [
            "Draining the indices still on the stack, which have no next greater element at all",
            "Clearing the stack before the scan starts so that stale indices cannot leak in",
            "Reversing the answer array, because the scan produced the results in the wrong order",
            "Pushing the final element onto the stack once the main loop has already finished",
        ],
        "answer": "Draining the indices still on the stack, which have no next greater element at all",
        "explanation": (
            "Anything left on the stack was never popped, which is exactly the evidence that no "
            "greater element follows it, so those positions need their default answer written. A "
            "fresh stack is already empty. The scan writes answers by index rather than in order, "
            "so no reversal is needed, and pushing after the loop achieves nothing."
        ),
        "difficulty": "intermediate",
    },
    873: {
        "topic": "dsa-rotated-arrays",
        "prompt": "When binary-searching a rotated sorted array, which part of each iteration is most often got wrong?",
        "options": [
            "Deciding which half is sorted, then testing the target against that half's closed interval",
            "Finding the rotation pivot first, since the search cannot begin without knowing it",
            "Comparing the middle element against the target before comparing it to the endpoints",
            "Halving the window, because a rotated array requires a third of the range each step",
        ],
        "answer": "Deciding which half is sorted, then testing the target against that half's closed interval",
        "explanation": (
            "One half is always sorted, and you discard it only if the target provably lies outside "
            "its inclusive bounds; a wrong endpoint comparison discards the half containing the "
            "answer. Locating the pivot first is a valid but different algorithm. Comparing mid to "
            "the target is fine, and the window still halves as normal."
        ),
        "difficulty": "advanced",
    },
    815: {
        "topic": "dsa-heap-sort",
        "prompt": "Is heap sort a stable sort, and what property of the algorithm decides that?",
        "options": [
            "No, because sift-down swaps elements across long distances and can reorder equal keys",
            "Yes, because the heap always removes the earliest of any two equal keys first",
            "Yes for primitive integers, where equal values are indistinguishable anyway",
            "Yes when built on a priority queue, which breaks ties by insertion order",
        ],
        "answer": "No, because sift-down swaps elements across long distances and can reorder equal keys",
        "explanation": (
            "Heapifying moves elements between distant positions, so two equal keys can end up in "
            "the opposite order they started in. The heap has no notion of which equal key arrived "
            "first. Stability is about equal keys with distinguishable payloads, so calling it "
            "stable for ints dodges the question, and a plain priority queue is not tie-stable."
        ),
        "difficulty": "intermediate",
    },
    792: {
        "topic": "dsa-insertion-sort",
        "prompt": "Is insertion sort a stable sort, and what property of the algorithm decides that?",
        "options": [
            "Yes, because the inserted element stops on reaching an equal key rather than passing it",
            "No, because shifting elements rightwards moves equal keys past one another every time",
            "Yes for primitive integers only, since equal values cannot be told apart in that case",
            "No, unless the input array happens to be nearly sorted before the algorithm starts",
        ],
        "answer": "Yes, because the inserted element stops on reaching an equal key rather than passing it",
        "explanation": (
            "The shift loop uses a strict comparison, so it halts at the first equal key and the "
            "earlier one keeps its position. Shifting only moves strictly greater elements. "
            "Stability holds for any payload, not just ints, and it is a property of the comparison "
            "rather than of how sorted the input already was."
        ),
        "difficulty": "intermediate",
    },
    799: {
        "topic": "dsa-merge-sort",
        "prompt": "Is merge sort a stable sort, and what property of the algorithm decides that?",
        "options": [
            "Yes, provided the merge step takes from the left run whenever the two keys are equal",
            "No, because the recursive split separates equal keys into different halves entirely",
            "Yes for primitive integers only, since equal values cannot be told apart in that case",
            "No, because the merge writes into a temporary buffer before copying results back",
        ],
        "answer": "Yes, provided the merge step takes from the left run whenever the two keys are equal",
        "explanation": (
            "Stability rests entirely on that tie-break: the left run holds the earlier elements, so "
            "preferring it preserves their order. Splitting does not reorder anything. Stability "
            "holds for any payload, and using a temporary buffer is an implementation detail with "
            "no bearing on tie order."
        ),
        "difficulty": "intermediate",
    },
    789: {
        "topic": "dsa-selection-sort",
        "prompt": "Is selection sort a stable sort, and what property of the algorithm decides that?",
        "options": [
            "No, because swapping the minimum into place can jump an equal key over another one",
            "Yes, because it always selects the leftmost of any two elements holding equal keys",
            "Yes when the implementation uses a queue rather than swapping array positions",
            "Yes for small inputs, where too few elements exist for equal keys to cross over",
        ],
        "answer": "No, because swapping the minimum into place can jump an equal key over another one",
        "explanation": (
            "The swap exchanges two arbitrary positions, so an element can leap past an equal key "
            "sitting between them. Selecting the leftmost minimum is not enough, because the "
            "element it displaces travels backwards. Stability is a property of the algorithm, not "
            "of the container or the input size."
        ),
        "difficulty": "intermediate",
    },
    79: {
        "topic": "cf-os-memory",
        "prompt": "At the level a programmer needs, what distinguishes the stack from the heap in a running process?",
        "options": [
            "The stack holds call frames and locals; the heap serves allocations that outlive a call",
            "The stack holds data read from disk; the heap holds data waiting to be written to disk",
            "The stack is memory on the CPU die; the heap is the memory sitting on the motherboard",
            "The stack stores small values and the heap stores large ones, decided by size alone",
        ],
        "answer": "The stack holds call frames and locals; the heap serves allocations that outlive a call",
        "explanation": (
            "The distinction is lifetime and who manages it: stack frames come and go with calls "
            "automatically, while heap allocations persist until freed. Neither region is about disk "
            "transfer. Both live in main memory rather than on the CPU, and size influences where "
            "you allocate but is not what defines the two regions."
        ),
        "difficulty": "beginner",
    },
    351: {
        "topic": "java-references",
        "prompt": "In Java, what does a reference variable held in a method frame actually point at?",
        "options": [
            "An object on the heap, while the reference itself sits in the frame on the call stack",
            "A copy of the object stored inside the frame, so each method gets its own instance",
            "A CPU register holding the object, which is why passing references is inexpensive",
            "A slot in the constant pool, which is where the runtime keeps every live object",
        ],
        "answer": "An object on the heap, while the reference itself sits in the frame on the call stack",
        "explanation": (
            "The variable is a handle on the stack; the object it names lives on the heap, which is "
            "why two references can see one another's mutations. Java never copies the object on "
            "assignment or on a call. Registers may cache a reference transiently, and the constant "
            "pool holds class literals rather than live objects."
        ),
        "difficulty": "intermediate",
    },
}


def collect(conn: sqlite3.Connection) -> tuple[list[dict], list[str]]:
    conn.row_factory = sqlite3.Row
    planned: list[dict] = []
    problems: list[str] = []

    for question_id, repair in REPAIRS.items():
        row = conn.execute(
            """
            SELECT q.id, q.question, q.slug, t.slug AS topic_slug
              FROM lesson_questions q
              JOIN curriculum_lessons l ON q.lesson_id = l.id
              JOIN curriculum_topics t ON l.topic_id = t.id
             WHERE q.id = ?
            """,
            (question_id,),
        ).fetchone()

        if row is None:
            problems.append(f"question id {question_id} no longer exists; skipping")
            continue
        if row["topic_slug"] != repair["topic"]:
            problems.append(
                f"question id {question_id} is on topic {row['topic_slug']!r}, "
                f"not {repair['topic']!r}; skipping rather than guessing"
            )
            continue

        # Hold the replacement to the same standard as an authored bank.
        candidate = AuthoredQuestion(
            slug=row["slug"] or f"legacy-{question_id}",
            prompt=repair["prompt"],
            options=repair["options"],
            answer=repair["answer"],
            explanation=repair["explanation"],
            difficulty=repair["difficulty"],
        )
        errors = _validate_question(
            candidate,
            topic_slug=repair["topic"],
            where="repair_question_prompts",
            seen_ids=set(),
            seen_prompts={},
            prompts_elsewhere={},
        )
        if errors:
            problems.extend(errors)
            continue

        planned.append({"id": question_id, "old_prompt": row["question"], **repair})

    return planned, problems


def apply(conn: sqlite3.Connection, planned: list[dict]) -> int:
    for plan in planned:
        conn.execute(
            """
            UPDATE lesson_questions
               SET question = ?, options = ?, answer = ?, explanation = ?, difficulty = ?
             WHERE id = ?
            """,
            (
                plan["prompt"],
                json.dumps(plan["options"]),
                plan["answer"],
                plan["explanation"],
                plan["difficulty"],
                plan["id"],
            ),
        )
    conn.commit()
    return len(planned)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    planned, problems = collect(conn)

    for problem in problems:
        print(f"  ! {problem}")
    print(f"{len(planned)} question(s) ready to repair")
    for plan in planned:
        print(f"  [{plan['topic']}] {plan['old_prompt']!r} -> {plan['prompt'][:64]}...")

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "question_prompt_repairs.json").write_text(
        json.dumps({"planned": planned, "problems": problems, "dry_run": args.dry_run}, indent=2),
        encoding="utf-8",
    )

    if args.dry_run:
        print("\ndry run — nothing written")
        return
    print(f"\nrepaired {apply(conn, planned)} question(s)")


if __name__ == "__main__":
    main()
