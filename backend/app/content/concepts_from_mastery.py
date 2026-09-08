"""Give a topic a Focus list built from its own mastery criteria.

The topic page shows a **Focus** list, sourced from the concept contract
registry. A topic with no contract shows nothing there, which is the one place
a learner looks to answer "what am I meant to take from this page?".

The 57 topics added to close curriculum gaps had no contracts, so their Focus
panel was empty. They do, however, each carry two or three authored
``mastery_criteria`` — concrete, checkable statements written alongside the
resource:

    Mastery:
    - Point at the exact line in a script that leaks when a scaler is fit on
      the full dataset before splitting.
    - State the rule that prevents preprocessing leakage in one sentence, and
      name the scikit-learn construct that enforces it.

That is already the right content for a Focus list, and it is better than the
generated contracts elsewhere in the registry, which tend to read "Understand
X" and "Apply X in a small exercise". This turns those criteria into concepts.

What it does **not** do is claim coverage. ``evidence_terms`` are search terms
that let a later content inspection look for a concept on a page; recording
them asserts nothing about whether the page covers it. ``verification_status``
is untouched, so these topics stay at "link checked, content review pending"
rather than silently gaining a verification nobody performed.

Run:
    python -m app.content.concepts_from_mastery --dry-run
    python -m app.content.concepts_from_mastery
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND / "dev.db"
CONTRACTS = Path(__file__).resolve().parent / "data" / "concept_contracts.json"
REPORTS = BACKEND / "reports"

#: The bullet list under a "Mastery:" heading. The lookahead has to allow the
#: bullets themselves to start the line, so the block is matched as a run of
#: bullet lines rather than "everything up to the next non-indented line".
_MASTERY_BLOCK = re.compile(
    r"^Mastery:[ \t]*\r?\n(?P<body>(?:[ \t]*[-*][ \t]+[^\r\n]*\r?\n?)+)", re.M
)
_BULLET = re.compile(r"^[ \t]*[-*][ \t]+(?P<text>[^\r\n]+?)[ \t]*$", re.M)

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "as",
    "is", "are", "be", "by", "from", "that", "this", "you", "your", "it", "its",
    "one", "two", "at", "not", "into", "when", "which", "what", "why", "how",
    "say", "state", "name", "point", "explain", "give", "show", "write", "run",
    "can", "does", "do", "than", "then", "so", "if", "why", "same", "own",
}

#: Trim a concept slug to something readable but still unique per topic.
MAX_SLUG_WORDS = 5


def mastery_criteria(description: str | None) -> list[str]:
    """The bullets under a ``Mastery:`` heading in a topic description."""
    if not description:
        return []
    match = _MASTERY_BLOCK.search(description)
    if not match:
        return []
    out: list[str] = []
    for bullet in _BULLET.finditer(match.group("body")):
        text = re.sub(r"\s+", " ", bullet.group("text")).strip()
        if not text or _is_boilerplate(text):
            continue
        out.append(text)
    return out


#: Criteria that say nothing. "Explain <topic name> in your own words" is the
#: shape that made the old Focus lists useless, and promoting it into a concept
#: would put the filler straight back on the page. A topic whose only criteria
#: look like this gets no contract, which is the honest outcome: nobody has
#: written down what to take from it yet.
_BOILERPLATE = (
    re.compile(r"^explain .+ in your own words\.?$", re.I),
    re.compile(r"^score\s*>=?", re.I),
    re.compile(r"^complete the mapped", re.I),
    re.compile(r"^understand [^:]+$", re.I),
    re.compile(r"^apply .+ in a small exercise\.?$", re.I),
)


def _is_boilerplate(text: str) -> bool:
    return any(pattern.match(text) for pattern in _BOILERPLATE)


def concept_slug(topic_slug: str, text: str, taken: set[str]) -> str:
    words = [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]
    stem = "-".join(words[:MAX_SLUG_WORDS]) or "concept"
    base = f"{topic_slug}-{stem}"[:150]
    slug, suffix = base, 2
    while slug in taken:
        slug = f"{base}-{suffix}"
        suffix += 1
    taken.add(slug)
    return slug


def evidence_terms(text: str) -> list[str]:
    """Search terms for a future content inspection. Not a coverage claim."""
    words = [w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9_.+-]{1,}", text) if w.lower() not in STOPWORDS]
    seen, out = set(), []
    for word in words:
        low = word.lower()
        if low in seen or len(low) < 3:
            continue
        seen.add(low)
        out.append(low)
    return out[:12]


#: Ten topics whose authored mastery criteria are only the boilerplate filtered
#: out above ("Explain X in your own words"), so there was nothing to promote.
#: Written by hand rather than generated, because the point of a Focus list is
#: to say something a generator cannot: what specifically to take from the page.
#:
#: The eight awareness/path pairs are orientation topics. The split is
#: deliberate -- an awareness topic answers "what is this field and what is it
#: not", a path topic answers "in what order, and what depends on what" -- and
#: keeping them apart is what stops the pair asking the same thing twice.
HAND_WRITTEN: dict[str, tuple[str, ...]] = {
    "dl-awareness": (
        "Say what a differentiable layer is, and why stacking them lets a network learn features instead of being given them.",
        "Name one problem where deep learning is the wrong tool and a simpler model is the right one.",
    ),
    "dl-path": (
        "Order these and justify the order: linear models, gradient descent, backpropagation, CNNs, transformers.",
        "Say which part of the maths you need before backpropagation makes sense, and which parts can wait.",
    ),
    "nlp-awareness": (
        "Trace text through tokenisation to a vector, and say what is lost at each step.",
        "Name a task where word order changes the answer, and one where it does not.",
    ),
    "nlp-path": (
        "Order these and justify the order: bag of words, TF-IDF, embeddings, attention, transformers.",
        "Say why classical text representations are still worth learning after transformers exist.",
    ),
    "genai-awareness": (
        "Say what a generative model is doing at inference, in terms of a distribution over next tokens.",
        "Name a task where a generative model is the wrong choice because the answer must be exactly right.",
    ),
    "genai-path": (
        "Order these and justify the order: prompting, retrieval, evaluation, fine-tuning.",
        "Say why fine-tuning is usually the last thing to reach for rather than the first.",
    ),
    "ai-eng-awareness": (
        "Say what an AI engineer is responsible for that a model researcher is not.",
        "Name the two things that make an LLM feature shippable rather than a demo: evaluation, and knowing what it does when it fails.",
    ),
    "ai-eng-path": (
        "Order these and justify the order: prompting, structured output, tool calling, retrieval, evaluation, monitoring.",
        "Say which of those you can skip for a prototype and which you cannot skip for production.",
    ),
    "cv-efficientnet-awareness": (
        "Say what compound scaling scales together, and why scaling depth alone stops helping.",
        "Name the situation that makes reaching for an EfficientNet worthwhile over a ResNet.",
    ),
    "genai-next-token-prediction": (
        "Say what the training objective actually is, and why predicting the next token teaches so much.",
        "Explain why a model trained only to predict the next token can follow an instruction it never saw.",
    ),
}


def build(conn: sqlite3.Connection) -> tuple[dict, list[str]]:
    conn.row_factory = sqlite3.Row
    payload = json.loads(CONTRACTS.read_text(encoding="utf-8"))
    contracts = payload.setdefault("contracts", {})

    added: dict[str, dict] = {}
    skipped: list[str] = []

    rows = conn.execute(
        "SELECT slug, name, description FROM curriculum_topics WHERE slug IS NOT NULL"
    ).fetchall()

    for row in rows:
        slug = row["slug"]
        if slug in contracts:
            continue
        criteria = mastery_criteria(row["description"]) or list(HAND_WRITTEN.get(slug, ()))
        if not criteria:
            skipped.append(f"{slug}: no usable mastery criteria in its description")
            continue

        taken: set[str] = set()
        required = [
            {
                "slug": concept_slug(slug, text, taken),
                "description": text,
                "evidence_terms": evidence_terms(text),
            }
            for text in criteria
        ]
        added[slug] = {
            "topic_slug": slug,
            "learning_objective": _objective(row["description"]),
            "source": (
                "HAND_WRITTEN_FOCUS" if slug in HAND_WRITTEN and not mastery_criteria(row["description"])
                else "AUTHORED_MASTERY_CRITERIA"
            ),
            "required": required,
            "optional": [],
        }

    return {"payload": payload, "added": added, "skipped": skipped}, skipped


def _objective(description: str | None) -> str:
    if not description:
        return ""
    match = re.search(r"Objective:\s*(.+?)(?:\n|$)", description)
    return match.group(1).strip() if match else ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    result, skipped = build(conn)
    payload, added = result["payload"], result["added"]

    print(f"{len(added)} topic(s) gain a Focus list from their mastery criteria")
    for slug, contract in list(added.items())[:8]:
        print(f"  {slug}")
        for concept in contract["required"]:
            print(f"      - {concept['description'][:88]}")
    if len(added) > 8:
        print(f"  ... and {len(added) - 8} more")
    for note in skipped[:10]:
        print(f"  ! {note}")
    if len(skipped) > 10:
        print(f"  ! ... and {len(skipped) - 10} more without usable criteria")

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "concepts_from_mastery.json").write_text(
        json.dumps({"added": added, "skipped": skipped, "dry_run": args.dry_run}, indent=2),
        encoding="utf-8",
    )

    if args.dry_run:
        print("\ndry run — nothing written")
        return

    payload["contracts"].update(added)
    payload["topic_count"] = len(payload["contracts"])
    payload["generated_from_mastery"] = len(added)
    CONTRACTS.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {len(added)} contract(s) into {CONTRACTS.name}")


if __name__ == "__main__":
    main()
