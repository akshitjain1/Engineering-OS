"""Score a diagnostic response against a bank item."""

from __future__ import annotations

from typing import Any, Optional


def _norm(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _complexity_norm(value: str) -> str:
    return _norm(value).replace(" ", "")


def score_mcq(selected: str, answer: str) -> float:
    return 100.0 if _norm(selected) == _norm(answer) else 0.0


def score_short_answer(text: str, answer: str, keywords: Optional[list[str]] = None) -> float:
    body = _norm(text)
    if not body:
        return 0.0
    expected = _norm(answer)
    if expected and expected == body:
        return 100.0
    if keywords:
        hits = sum(1 for word in keywords if _norm(word) in body)
        return round(100.0 * hits / len(keywords), 2) if keywords else 0.0
    if expected and expected in body:
        return 80.0
    return 0.0


def score_implementation(
    payload: dict[str, Any],
    expected_complexity: Optional[str] = None,
) -> float:
    code = (payload.get("code") or "").strip()
    explanation = (payload.get("explanation") or "").strip()
    complexity = _complexity_norm(payload.get("complexity") or "")
    if not code:
        return 0.0
    score = 50.0
    if len(explanation) >= 20:
        score += 25.0
    if expected_complexity:
        expected = _complexity_norm(expected_complexity)
        if expected and (expected in complexity or complexity in expected):
            score += 25.0
    elif complexity:
        score += 15.0
    return min(100.0, score)


def score_response(question: dict[str, Any], payload: dict[str, Any]) -> float:
    qtype = question.get("type")
    if qtype in {"mcq", "tracing", "complexity"}:
        return score_mcq(str(payload.get("selected") or payload.get("answer") or ""), question["answer"])
    if qtype == "short_answer":
        return score_short_answer(
            str(payload.get("text") or payload.get("answer") or ""),
            question.get("answer") or "",
            question.get("keywords"),
        )
    if qtype == "implementation":
        return score_implementation(payload, question.get("expected_complexity"))
    return 0.0
