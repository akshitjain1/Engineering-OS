"""Adaptive spaced-revision engine (spec PART I).

Replaces the static confidence→bucket mapping while keeping the existing
API contract. SM-2-inspired:

- confidence >= 80 → successful retrieval: interval *= ease, ease += 0.05
- 50 <= confidence < 80 → partial: interval grows slowly (×1.2, at least +1 day)
- confidence < 50 → failure: interval resets to 1 day, ease -= 0.2

Initial ladder stays approximately +1/+3/+7/+14/+30 days via the ease
multiplier starting at 2.5 and clamped intervals [1, 60].

Priority scoring for the pending queue considers:
overdue days, failure history, topic importance, prerequisite centrality.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional


INITIAL_INTERVAL_DAYS = 1
MIN_INTERVAL_DAYS = 1
MAX_INTERVAL_DAYS = 60
DEFAULT_EASE = 2.5
#: Growth applied to a partial recall. Small enough that "recalled with effort"
#: is clearly worse than "instant", large enough that it still moves -- see
#: next_interval for why "unchanged" was not a safe answer.
PARTIAL_GROWTH = 1.2
EASE_MIN = 1.3
EASE_MAX = 3.2
LADDER_CAPS = (1, 3, 7, 14, 30)
# Legacy confidence ladder kept as the SEED for early retrievals (no history yet).
CONFIDENCE_LADDER = (1, 3, 7, 14, 30, 60)


def static_confidence_interval(confidence: float) -> int:
    """Legacy bucket mapping — used only to seed records without retrieval history."""
    index = min(max(int(confidence / 20), 0), len(CONFIDENCE_LADDER) - 1)
    return CONFIDENCE_LADDER[index]


def quality_from_confidence(confidence: float) -> str:
    """Classify a retrieval attempt from self-reported confidence (0-100)."""
    if confidence >= 80:
        return "success"
    if confidence >= 50:
        return "partial"
    return "fail"


def next_interval(
    *,
    previous_interval_days: int,
    success_count: int,
    ease: float,
    quality: str,
) -> tuple[int, float]:
    """Return (new_interval_days, new_ease) after one retrieval attempt."""
    new_ease = ease
    if quality == "success":
        new_ease = min(EASE_MAX, ease + 0.05)
        if success_count <= 0:
            # First successful retrieval advances along the classic ladder.
            idx = LADDER_CAPS.index(min(LADDER_CAPS, key=lambda c: abs(c - previous_interval_days)))
            nxt = LADDER_CAPS[min(idx + 1, len(LADDER_CAPS) - 1)]
        else:
            nxt = int(round(previous_interval_days * new_ease))
    elif quality == "partial":
        # A partial recall must still move the date out -- slowly, but out.
        #
        # This used to return the interval unchanged. Because a new item is
        # seeded at one day, anything graded "OK" came back tomorrow, and
        # again the next day, for ever. Simulating four months of honest daily
        # grading grew the queue to 228 items inside a fifteen-minute block --
        # three seconds an item. Only ever pressing "Easy" kept it bounded, so
        # the schedule quietly punished honest grading, which is the one thing
        # spaced repetition depends on.
        #
        # The +1 floor matters as much as the ratio: round(1 * 1.2) is 1, so a
        # bare multiplier would leave every new item pinned at a single day and
        # change nothing.
        nxt = max(previous_interval_days + 1,
                  int(round(previous_interval_days * PARTIAL_GROWTH)))
    else:  # fail
        new_ease = max(EASE_MIN, ease - 0.2)
        nxt = MIN_INTERVAL_DAYS
    return max(MIN_INTERVAL_DAYS, min(MAX_INTERVAL_DAYS, nxt)), new_ease


def schedule_update(record: Any, confidence: float, *, now: Optional[datetime] = None) -> dict[str, Any]:
    """Apply one retrieval attempt to a RevisionSchedule row (mutates in place)."""
    now = now or datetime.now(timezone.utc)
    quality = quality_from_confidence(confidence)
    prev_interval = record.review_interval or INITIAL_INTERVAL_DAYS
    prior_successes = int(getattr(record, "retrieval_success_count", 0) or 0)

    if quality == "success" and prior_successes == 0:
        # First successful retrieval: no established retrieval history yet, so
        # trust the self-reported confidence ladder as the seed interval.
        interval = max(prev_interval, static_confidence_interval(confidence))
        ease = float(getattr(record, "ease", DEFAULT_EASE))
    else:
        interval, ease = next_interval(
            previous_interval_days=prev_interval,
            success_count=prior_successes,
            ease=float(getattr(record, "ease", DEFAULT_EASE)),
            quality=quality,
        )

    record.confidence = confidence
    record.last_reviewed = now
    record.review_interval = interval
    record.next_review = now + timedelta(days=interval)
    record.ease = ease
    if quality == "success":
        record.retrieval_success_count = prior_successes + 1
    elif quality == "fail":
        record.retrieval_fail_count = int(getattr(record, "retrieval_fail_count", 0) or 0) + 1
    return {
        "quality": quality,
        "interval": interval,
        "ease": round(ease, 2),
        "next_review": record.next_review,
    }


@dataclass(frozen=True)
class RevisionPriorityInput:
    overdue_days: float
    fail_count: int
    importance: float          # topic importance weight (default 1.0)
    centrality: int            # number of topics that unlock downstream
    upcoming_dependents: int   # dependents scheduled within ~7 days


def priority_score(p: RevisionPriorityInput) -> float:
    """Higher score = revise first."""
    return (
        p.overdue_days * 1.5
        + p.fail_count * 8.0
        + p.importance * 4.0
        + p.centrality * 2.0
        + p.upcoming_dependents * 3.0
    )


RECALL_PROMPTS = (
    "Explain {topic} without looking anything up.",
    "Draw or describe the pipeline/mechanism behind {topic}.",
    "Give one concrete example where {topic} matters.",
)


def active_recall_prompt(topic_name: str) -> str:
    """Deterministic recall prompt — never just 'Revise X'."""
    return RECALL_PROMPTS[hash(topic_name) % len(RECALL_PROMPTS)].format(topic=topic_name)
