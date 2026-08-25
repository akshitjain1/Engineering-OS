"""PART I — spaced revision engine tests (adaptive scheduling).

Covers:
- Legacy seed contract: first schedule with high confidence lands on the
  confidence ladder (30d for 90+), preserving the historical API behavior.
- Failure resets interval to minimum and shortens subsequent intervals.
- Success streaks grow intervals via ease multiplier (bounded).
- Ease decreases on failure, increases on success.
- Priority scoring: overdue/failure/importance/centrality ordering.
- Active recall prompts are specific, never bare "Revise X".
"""
from datetime import datetime, timedelta

from app.learning.revision_engine import (
    active_recall_prompt,
    next_interval,
    priority_score,
    quality_from_confidence,
    RevisionPriorityInput,
    schedule_update,
    static_confidence_interval,
)


class FakeRecord:
    def __init__(self, interval=1, ease=2.5, success=0, fail=0):
        self.review_interval = interval
        self.ease = ease
        self.retrieval_success_count = success
        self.retrieval_fail_count = fail
        self.confidence = 0.0
        self.last_reviewed = None
        self.next_review = None


def test_quality_bands():
    assert quality_from_confidence(90) == "success"
    assert quality_from_confidence(80) == "success"
    assert quality_from_confidence(60) == "partial"
    assert quality_from_confidence(50) == "partial"
    assert quality_from_confidence(10) == "fail"


def test_first_success_seeds_from_confidence_ladder():
    # Historical contract: fail then 90-confidence -> 30 day interval.
    rec = FakeRecord(interval=1)
    schedule_update(rec, 10)
    assert rec.review_interval == 1
    assert rec.retrieval_fail_count == 1
    schedule_update(rec, 90)
    assert rec.review_interval == 30
    assert rec.retrieval_success_count == 1


def test_failure_resets_and_shortens():
    rec = FakeRecord(interval=14, ease=2.5, success=3)
    out = schedule_update(rec, 20)  # fail
    assert out["quality"] == "fail"
    assert rec.review_interval == 1
    assert rec.ease < 2.5


def test_success_streak_grows_with_cap():
    interval = 7
    ease = 2.5
    for i in range(6):
        rec = FakeRecord(interval=interval, ease=ease, success=i + 1)
        out = schedule_update(rec, 95)
        interval, ease = out["interval"], out["ease"]
        assert interval >= 7
    assert interval <= 60  # hard cap


def test_next_interval_bounds():
    small, _ = next_interval(previous_interval_days=1, success_count=5, ease=1.3, quality="success")
    assert small >= 1
    big, ease_big = next_interval(previous_interval_days=55, success_count=9, ease=3.4, quality="success")
    assert big <= 60
    assert ease_big <= 3.2


def test_partial_keeps_interval():
    rec = FakeRecord(interval=7, success=2)
    out = schedule_update(rec, 65)
    assert out["quality"] == "partial"
    assert rec.review_interval == 7


def test_priority_score_orders_sensibly():
    failing_overdue_central = priority_score(
        RevisionPriorityInput(overdue_days=10, fail_count=2, importance=2.0, centrality=8, upcoming_dependents=3)
    )
    fresh_leaf = priority_score(
        RevisionPriorityInput(overdue_days=0, fail_count=0, importance=1.0, centrality=0, upcoming_dependents=0)
    )
    assert failing_overdue_central > fresh_leaf


def test_static_ladder_matches_legacy_buckets():
    assert static_confidence_interval(100) == 60
    assert static_confidence_interval(95) == 30
    assert static_confidence_interval(70) == 14
    assert static_confidence_interval(45) == 7
    assert static_confidence_interval(15) == 1


def test_recall_prompt_is_active_not_lazy():
    prompt = active_recall_prompt("Gradient descent intuition")
    assert "Gradient descent intuition" in prompt
    lowered = prompt.lower()
    assert not lowered.startswith("revise ")
    assert any(v in lowered for v in ("explain", "draw", "give one concrete example"))
