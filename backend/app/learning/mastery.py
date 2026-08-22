"""Topic mastery scoring, status, and learning intensity (pace).

Status is a pure function of mastery_score:

  90–100 MASTERED
  75–89  FAMILIAR
  50–74  LEARNING
  0–49   NEEDS_REVIEW
  None   UNKNOWN

Diagnostic MASTERED is evidence that sets FAST pace. It does not skip
curriculum topics. Implementation evidence is recorded separately and does
not cap status below the score threshold.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

CATEGORIES = ("conceptual", "implementation", "problem_solving", "explanation")
DEFAULT_WEIGHTS = {
    "conceptual": 0.30,
    "implementation": 0.30,
    "problem_solving": 0.30,
    "explanation": 0.10,
}

STATUS_UNKNOWN = "UNKNOWN"
STATUS_LEARNING = "LEARNING"
STATUS_FAMILIAR = "FAMILIAR"
STATUS_MASTERED = "MASTERED"
STATUS_NEEDS_REVIEW = "NEEDS_REVIEW"

PACE_FOUNDATION = "FOUNDATION"
PACE_NORMAL = "NORMAL"
PACE_FAST = "FAST"
PACE_DEEP = "DEEP"
PACE_REMEDIAL = "REMEDIAL"

CONCEPTUAL_DSA_SLUGS = frozenset(
    {
        "dsa-algorithmic-thinking",
        "dsa-big-o",
        "dsa-best-worst-average",
        "dsa-sort-complexity",
        "dsa-sort-stability",
        "dsa-tree-terminology",
        "dsa-dp-mindset",
        "dsa-dp-state",
        "dsa-dp-transition",
        "dsa-pattern-selection",
        "dsa-interview-hygiene",
        "dsa-greedy-reasoning",
        "dsa-greedy-exchange",
        "dsa-greedy-patterns",
    }
)


def redistribute_weights(available: Iterable[str]) -> dict[str, float]:
    present = [key for key in CATEGORIES if key in set(available)]
    if not present:
        return {}
    total = sum(DEFAULT_WEIGHTS[key] for key in present)
    return {key: DEFAULT_WEIGHTS[key] / total for key in present}


def average_category_scores(evidence: Iterable[Mapping]) -> dict[str, float]:
    buckets: dict[str, list[float]] = {key: [] for key in CATEGORIES}
    for item in evidence:
        category = item.get("category")
        if category not in buckets:
            continue
        try:
            buckets[category].append(float(item["score"]))
        except (KeyError, TypeError, ValueError):
            continue
    return {key: sum(values) / len(values) for key, values in buckets.items() if values}


def mastery_score(evidence: Iterable[Mapping]) -> Optional[float]:
    by_category = average_category_scores(evidence)
    weights = redistribute_weights(by_category.keys())
    if not weights:
        return None
    return round(sum(by_category[key] * weights[key] for key in weights), 2)


def topic_requires_implementation(slug: str) -> bool:
    if not slug:
        return False
    if slug.startswith("dsa-") and slug not in CONCEPTUAL_DSA_SLUGS:
        return True
    return slug in {
        "java-arrays",
        "java-strings",
        "java-stringbuilder",
        "java-list",
        "java-map",
        "java-set",
        "java-loops",
        "java-method-basics",
        "java-priority-queue",
    }


def status_from_score(score: Optional[float], **__policies: object) -> str:
    if score is None:
        return STATUS_UNKNOWN
    if score < 50:
        return STATUS_NEEDS_REVIEW
    if score < 75:
        return STATUS_LEARNING
    if score < 90:
        return STATUS_FAMILIAR
    return STATUS_MASTERED


def apply_implementation_cap(status: str, *, requires_implementation: bool, has_impl: bool) -> str:
    """Implementation topics cannot reach MASTERED on MCQ/reading evidence alone."""
    if status == STATUS_MASTERED and requires_implementation and not has_impl:
        return STATUS_FAMILIAR
    return status


def pace_from_score(score: Optional[float]) -> str:
    if score is None:
        return PACE_FOUNDATION
    if score < 50:
        return PACE_REMEDIAL
    if score < 75:
        return PACE_DEEP
    if score < 90:
        return PACE_NORMAL
    return PACE_FAST


def has_implementation_evidence(evidence: Iterable[Mapping]) -> bool:
    return any(
        item.get("category") == "implementation" and float(item.get("score") or 0) >= 50
        for item in evidence
    )


def summarize_mastery(slug: str, evidence: Iterable[Mapping]) -> dict:
    items = list(evidence)
    score = mastery_score(items)
    impl = has_implementation_evidence(items)
    required = topic_requires_implementation(slug)
    return {
        "topic_slug": slug,
        "mastery_score": score,
        "status": apply_implementation_cap(status_from_score(score), requires_implementation=required, has_impl=impl),
        "pace_mode": pace_from_score(score),
        "has_implementation_evidence": impl,
        "implementation_required": required,
    }


def labels_from_score(score: Optional[float]) -> tuple[str, str]:
    return status_from_score(score), pace_from_score(score)
