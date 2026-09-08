"""Authored question banks: the contract, and the gates that keep them honest.

Questions in this database went wrong in two specific ways, and both were
possible because nothing checked the content:

1. **Template filler.** 94 questions read "Core idea of {TOPIC}?" with the
   distractors "A vague buzzword", "Irrelevant outside interviews" and
   "Replaces prerequisites". The answer is whichever option is a real
   sentence, so the question tests nothing.

2. **Module-level questions on topic-level pages.** One set of eleven generic
   dynamic-programming questions was attached to all twelve DP topics, so the
   Knapsack page asked about memoisation versus tabulation. Studying a topic
   and being quizzed on its neighbour is what makes content feel unrelated.

So the gates below are not style preferences. Each one blocks a defect that
actually shipped:

- ``BANNED_PHRASES`` and ``TEMPLATE_PROMPTS`` reject filler by shape.
- ``duplicate prompt across topics`` rejects a question reused on a second
  topic, which is defect 2 stated directly.
- option length spread rejects questions answerable by picking the longest
  option without reading it.
- an explanation floor forces the author to say why the wrong answers are
  wrong, which is the part that teaches.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional

MIN_OPTIONS = 4
MIN_PROMPT_CHARS = 20
MIN_EXPLANATION_WORDS = 15
MIN_QUESTIONS_PER_TOPIC = 4
#: Beyond this, the answer is guessable from option length alone.
MAX_OPTION_LENGTH_RATIO = 3.0

DIFFICULTIES = {"beginner", "intermediate", "advanced"}

BANNED_PHRASES = (
    "core idea of",
    "a vague buzzword",
    "irrelevant outside interviews",
    "replaces prerequisites",
    "understand this topic",
    "apply in a small exercise",
    "none of the above",
    "all of the above",
    "todo",
    "tbd",
    "placeholder",
    "as an ai",
)

#: Prompt shapes that restate the topic name instead of asking something.
TEMPLATE_PROMPTS = (
    re.compile(r"^\s*(what is the\s+)?core idea of\b", re.I),
    re.compile(r"^\s*(what|which) (is|are) (a|an|the)?\s*\{?topic\}?\s*\??\s*$", re.I),
    re.compile(r"^\s*define\s+\S+\s*\??\s*$", re.I),
)

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_WORD = re.compile(r"[A-Za-z0-9_'/+.-]+")


def word_count(text: str) -> int:
    return len(_WORD.findall(text or ""))


@dataclass
class AuthoredQuestion:
    slug: str
    prompt: str
    options: list[str]
    answer: str
    explanation: str
    difficulty: str = "intermediate"
    mastery: bool = False


@dataclass
class TopicBank:
    topic_slug: str
    questions: list[AuthoredQuestion] = field(default_factory=list)


@dataclass
class QuestionBank:
    module_slug: Optional[str]
    topics: list[TopicBank] = field(default_factory=list)
    source_path: Optional[str] = None


def parse_bank(data: dict[str, Any], source_path: Optional[str] = None) -> QuestionBank:
    if not isinstance(data, dict):
        raise ValueError(f"{source_path or '<data>'}: question bank must be a mapping")
    if data.get("kind") != "question_bank":
        raise ValueError(f"{source_path or '<data>'}: 'kind' must be 'question_bank'")
    if data.get("schema_version") != 1:
        raise ValueError(f"{source_path or '<data>'}: 'schema_version' must be 1")

    topics: list[TopicBank] = []
    for entry in data.get("topics") or []:
        if not isinstance(entry, dict):
            raise ValueError(f"{source_path or '<data>'}: each topic entry must be a mapping")
        questions = []
        for raw in entry.get("questions") or []:
            if not isinstance(raw, dict):
                raise ValueError(f"{source_path or '<data>'}: each question must be a mapping")
            options = raw.get("options") or []
            if not isinstance(options, list):
                raise ValueError(f"{source_path or '<data>'}: 'options' must be a list")
            questions.append(
                AuthoredQuestion(
                    slug=str(raw.get("id") or "").strip(),
                    prompt=str(raw.get("prompt") or "").strip(),
                    options=[str(o).strip() for o in options],
                    answer=str(raw.get("answer") or "").strip(),
                    explanation=str(raw.get("explanation") or "").strip(),
                    difficulty=str(raw.get("difficulty") or "intermediate").strip().lower(),
                    mastery=bool(raw.get("mastery", False)),
                )
            )
        topics.append(TopicBank(topic_slug=str(entry.get("topic") or "").strip(), questions=questions))

    return QuestionBank(
        module_slug=(str(data["module"]).strip() if data.get("module") else None),
        topics=topics,
        source_path=source_path,
    )


def validate_bank(
    bank: QuestionBank,
    *,
    known_topics: Optional[set[str]] = None,
    prompts_elsewhere: Optional[dict[str, str]] = None,
) -> list[str]:
    """Every problem with this bank. Empty list means it is safe to import.

    ``prompts_elsewhere`` maps a normalised prompt to the topic that already
    uses it, so a question cannot be shared across topics.
    """
    errors: list[str] = []
    where = bank.source_path or bank.module_slug or "<bank>"
    seen_ids: set[str] = set()
    seen_prompts: dict[str, str] = {}

    for topic in bank.topics:
        if not topic.topic_slug:
            errors.append(f"{where}: a topic entry has no 'topic' slug")
            continue
        if known_topics is not None and topic.topic_slug not in known_topics:
            errors.append(f"{where}: topic {topic.topic_slug!r} does not exist in the curriculum")
            continue
        if len(topic.questions) < MIN_QUESTIONS_PER_TOPIC:
            errors.append(
                f"{where}: topic {topic.topic_slug!r} has {len(topic.questions)} questions; "
                f"needs at least {MIN_QUESTIONS_PER_TOPIC}"
            )

        for question in topic.questions:
            errors.extend(
                _validate_question(
                    question,
                    topic_slug=topic.topic_slug,
                    where=where,
                    seen_ids=seen_ids,
                    seen_prompts=seen_prompts,
                    prompts_elsewhere=prompts_elsewhere or {},
                )
            )
    return errors


def normalise_prompt(prompt: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", (prompt or "").lower()).strip()


def _validate_question(
    question: AuthoredQuestion,
    *,
    topic_slug: str,
    where: str,
    seen_ids: set[str],
    seen_prompts: dict[str, str],
    prompts_elsewhere: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    label = question.slug or (question.prompt[:40] or "<unnamed>")

    def bad(msg: str) -> None:
        errors.append(f"{where}: [{topic_slug}] {label}: {msg}")

    if not SLUG_RE.match(question.slug or ""):
        bad(f"id {question.slug!r} is not a lowercase-hyphen slug")
    elif question.slug in seen_ids:
        bad("duplicate question id in this bank")
    else:
        seen_ids.add(question.slug)

    if len(question.prompt) < MIN_PROMPT_CHARS:
        bad(f"prompt is {len(question.prompt)} characters; too short to ask anything real")
    for pattern in TEMPLATE_PROMPTS:
        if pattern.match(question.prompt):
            bad("prompt is a template that restates the topic name")
            break

    # The defect this whole module exists to prevent: one question, many topics.
    key = normalise_prompt(question.prompt)
    if key:
        if key in seen_prompts and seen_prompts[key] != topic_slug:
            bad(f"same prompt is already used by topic {seen_prompts[key]!r} in this bank")
        elif key in prompts_elsewhere and prompts_elsewhere[key] != topic_slug:
            bad(f"same prompt is already stored against topic {prompts_elsewhere[key]!r}")
        seen_prompts.setdefault(key, topic_slug)

    if len(question.options) < MIN_OPTIONS:
        bad(f"has {len(question.options)} options; needs {MIN_OPTIONS}")
    if len(set(question.options)) != len(question.options):
        bad("has duplicate options")
    if any(not o for o in question.options):
        bad("has a blank option")
    if question.answer not in question.options:
        bad("answer is not one of the options")

    lengths = [len(o) for o in question.options if o]
    if lengths and min(lengths) > 0 and max(lengths) / min(lengths) > MAX_OPTION_LENGTH_RATIO:
        bad(
            f"options differ {max(lengths) / min(lengths):.1f}x in length; "
            "the answer is guessable without reading them"
        )

    if word_count(question.explanation) < MIN_EXPLANATION_WORDS:
        bad(
            f"explanation is {word_count(question.explanation)} words; needs "
            f"{MIN_EXPLANATION_WORDS} and should say why the wrong options are wrong"
        )

    if question.difficulty not in DIFFICULTIES:
        bad(f"difficulty {question.difficulty!r} is not one of {sorted(DIFFICULTIES)}")

    haystack = " ".join([question.prompt, question.explanation, *question.options]).lower()
    for phrase in BANNED_PHRASES:
        if phrase in haystack:
            bad(f"contains banned filler phrasing {phrase!r}")

    return errors
