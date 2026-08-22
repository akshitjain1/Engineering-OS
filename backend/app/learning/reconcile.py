"""Reconciliation of mastery state onto current-evidence semantics.

Legacy behavior appended one evidence row per click, so mastery averaged
cumulative history (81 -> 81.2 -> ... -> 89.x) and old mistakes dragged on
forever. This module rebuilds each topic from its current evidence
registers:

- lesson / exercise registers: latest value kept per (source, category)
- diagnostic register: rebuilt from the LATEST completed diagnostic session
  (per topic per category session average)
- assessment register: rebuilt from the LATEST completed topic assessment
- legacy source="question" rows are dropped (they were the accumulation bug)

Dry-run mode reports {topic, old score, new score, reason} and changes
nothing. Apply mode performs the rebuild in a single transaction and never
resets XP, user progress, or curriculum data.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.learning import service
from app.learning.mastery import summarize_mastery
from app.learning.service import DEFAULT_USER, ordered_topics
from app.db.models import (
    AssessmentSession,
    CurriculumTopic,
    DiagnosticAnswer,
    DiagnosticSession,
    MasteryEvidence,
    TopicMastery,
)

EVIDENCE_SOURCES = {"lesson", "exercise", "diagnostic", "assessment"}


def _register_kept(rows: list[MasteryEvidence]) -> dict[tuple[str, str], MasteryEvidence]:
    kept: dict[tuple[str, str], MasteryEvidence] = {}
    for row in sorted(rows, key=lambda item: item.id):
        key = (row.source, row.category)
        if row.source in {"question", "legacy"}:
            continue
        kept[key] = row
    return kept


def _latest_diagnostic_categories(db: Session, user_id: str) -> dict[str, dict[str, float]]:
    """Per-topic per-category session averages from the latest completed session.

    Mirror of service.diagnostic_complete scoring; the latest session is the
    current truth for diagnostic evidence.
    """
    session = (
        db.query(DiagnosticSession)
        .filter(DiagnosticSession.user_id == user_id, DiagnosticSession.status == "completed")
        .order_by(DiagnosticSession.id.desc())
        .first()
    )
    if not session:
        return {}
    rows = db.query(DiagnosticAnswer).filter(DiagnosticAnswer.session_id == session.id).all()
    from app.learning.diagnostic_bank import questions_by_id

    bank = questions_by_id()
    per_topic: dict[str, dict[str, list[float]]] = {}
    for row in rows:
        question = bank.get(row.question_id)
        if not question:
            continue
        score = row.score if row.score is not None else 0.0
        for slug in list(question["topics"]) + list(question.get("secondary") or []):
            per_topic.setdefault(slug, {}).setdefault(question["category"], []).append(score)
    return {
        slug: {category: round(sum(values) / len(values), 2) for category, values in categories.items()}
        for slug, categories in per_topic.items()
    }


def _latest_assessment_categories(db: Session, user_id: str) -> dict[str, dict[str, float]]:
    """Per-topic per-category from the latest completed assessment session."""
    sessions = (
        db.query(AssessmentSession)
        .filter(AssessmentSession.user_id == user_id, AssessmentSession.status == "completed")
        .order_by(AssessmentSession.id.desc())
        .all()
    )
    result: dict[str, dict[str, float]] = {}
    seen: set[int] = set()
    for session in sessions:
        if session.topic_id in seen:
            continue
        seen.add(session.topic_id)
        topic = db.get(CurriculumTopic, session.topic_id)
        summary = session.summary or {}
        if topic and topic.slug and summary:
            result[topic.slug] = dict(summary.get("per_category") or {})
    return result


def plan_reconciliation(db: Session, user_id: str = DEFAULT_USER) -> list[dict[str, Any]]:
    diagnostic = _latest_diagnostic_categories(db, user_id)
    assessment = _latest_assessment_categories(db, user_id)
    rows_by_slug: dict[str, list[MasteryEvidence]] = {}
    for row in (
        db.query(MasteryEvidence)
        .filter(MasteryEvidence.user_id == user_id)
        .order_by(MasteryEvidence.id)
        .all()
    ):
        rows_by_slug.setdefault(row.topic_slug, []).append(row)

    slugs: set[str] = set(rows_by_slug) | set(diagnostic) | set(assessment)
    for topic in ordered_topics(db):
        slugs.add(topic.slug)

    plan = []
    for slug in sorted(slugs):
        if not slug:
            continue
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
        previous = (
            db.query(TopicMastery)
            .filter(TopicMastery.user_id == user_id, TopicMastery.topic_slug == slug)
            .first()
        )
        old_score = previous.mastery_score if previous else None
        old_status = previous.status if previous else "UNKNOWN"

        registers = _register_kept(rows_by_slug.get(slug, []))
        reasons: list[str] = []
        legacy_question_count = sum(
            1 for row in rows_by_slug.get(slug, []) if row.source in {"question", "legacy"}
        )
        if legacy_question_count:
            reasons.append(f"{legacy_question_count} legacy question evidence row(s) removed")

        evidence: list[dict[str, Any]] = []
        for (source, category), row in registers.items():
            evidence.append({"category": category, "score": row.score, "source": source, "payload": row.payload})
        for category, score in (diagnostic.get(slug) or {}).items():
            evidence.append({"category": category, "score": score, "source": "diagnostic", "payload": {"reconciled": True}})
            reasons.append("diagnostic register rebuilt from latest completed session")
        for category, score in (assessment.get(slug) or {}).items():
            evidence.append({"category": category, "score": score, "source": "assessment", "payload": {"reconciled": True}})
            reasons.append("assessment register kept from latest completed assessment")

        summary = summarize_mastery(slug, evidence)
        new_score = summary["mastery_score"]
        new_status = summary["status"]
        if not reasons and (new_score, new_status) == (old_score, old_status):
            continue
        if not reasons and previous is None:
            continue
        if not reasons:
            reasons.append("score recomputed from current evidence registers")
        plan.append(
            {
                "topic_slug": slug,
                "topic_name": topic.name if topic else slug,
                "old_score": old_score,
                "new_score": new_score,
                "old_status": old_status,
                "new_status": new_status,
                "reasons": reasons,
            }
        )
    return plan


def apply_reconciliation(db: Session, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    report = plan_reconciliation(db, user_id)
    diagnostic = _latest_diagnostic_categories(db, user_id)
    assessment = _latest_assessment_categories(db, user_id)

    all_rows = (
        db.query(MasteryEvidence)
        .filter(MasteryEvidence.user_id == user_id)
        .order_by(MasteryEvidence.id)
        .all()
    )
    rows_by_slug: dict[str, list[MasteryEvidence]] = {}
    for row in all_rows:
        rows_by_slug.setdefault(row.topic_slug, []).append(row)

    slugs = {item["topic_slug"] for item in report}
    for slug in slugs:
        for row in rows_by_slug.get(slug, []):
            if row.source in {"question", "legacy"}:
                db.delete(row)
    db.flush()

    for slug in slugs:
        registers = _register_kept(rows_by_slug.get(slug, []))
        for (source, category), row in registers.items():
            service.upsert_evidence(
                db,
                topic_slug=slug,
                source=source,
                category=category,
                score=row.score,
                payload=row.payload,
                user_id=user_id,
            )
        for category, score in (diagnostic.get(slug) or {}).items():
            service.upsert_evidence(
                db,
                topic_slug=slug,
                source="diagnostic",
                category=category,
                score=score,
                payload={"reconciled": True},
                user_id=user_id,
            )
        for category, score in (assessment.get(slug) or {}).items():
            service.upsert_evidence(
                db,
                topic_slug=slug,
                source="assessment",
                category=category,
                score=score,
                payload={"reconciled": True},
                user_id=user_id,
            )
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
        service.sync_mastery_row(
            db,
            slug,
            topic_id=topic.id if topic else None,
            attempt=False,
            award_bonus=False,
            sync_revision=False,
            user_id=user_id,
        )
    db.flush()
    return {"applied": len(report), "rows": report}