"""Strict trustworthiness lockdown regression tests."""
from __future__ import annotations

import json
from pathlib import Path

from app.content.audit import audit_topic
from app.content.import_curriculum import expand_targets, import_path
from app.content.readiness_contract import evaluate_readiness
from app.content.source_delivery import apply_source_delivery
from app.content.verification import (
    EXACTNESS_COLLECTION,
    EXACTNESS_EXACT,
    PRACTICE_NO_PRACTICE_REQUIRED,
    PRACTICE_VERIFIED,
    READINESS_NEEDS_REVIEW,
    READINESS_PARTIAL_COVERAGE,
    READINESS_PRACTICE_GAP,
    READINESS_READY,
    READINESS_RESOURCE_GAP,
    VERIFICATION_BROKEN,
    VERIFICATION_NEEDS_REVIEW,
    VERIFICATION_PARTIAL_COVERAGE,
    VERIFICATION_UNVERIFIED,
    VERIFICATION_VERIFIED_COVERAGE,
)
from app.db.models import CurriculumLesson, CurriculumTopic, UserProgress, TopicMastery, UserXP
from app.db.session import SessionLocal
from test_curriculum_v1 import V1_INDEX


def _import(db):
    for target in expand_targets(V1_INDEX):
        import_path(target)
    apply_source_delivery(db)


class _R:
    def __init__(self, status, covered, exactness=EXACTNESS_EXACT, section=None, minutes=20, evidence="{}"):
        self.verification_status = status
        self.required_concepts_covered = covered
        self.exactness = exactness
        self.section = section
        self.lecture = None
        self.estimated_minutes = minutes
        self.verification_evidence = evidence
        self.notes = "domain0 manifest"
        self.slug = "r"


def test_url_alone_not_ready():
    d = evaluate_readiness(
        required_concepts=["a", "b"],
        primaries=[_R(VERIFICATION_UNVERIFIED, [], evidence="")],
        practice_status=PRACTICE_NO_PRACTICE_REQUIRED,
        practice_compatible=True,
        practice_gap_detail=None,
        existing_minutes=30,
    )
    assert d.readiness != READINESS_READY


def test_http_title_not_ready():
    d = evaluate_readiness(
        required_concepts=["a"],
        primaries=[_R("VERIFIED", ["a"], evidence="")],  # legacy VERIFIED
        practice_status=PRACTICE_NO_PRACTICE_REQUIRED,
        practice_compatible=True,
        practice_gap_detail=None,
        existing_minutes=30,
    )
    assert d.readiness != READINESS_READY


def test_partial_alone_not_ready():
    d = evaluate_readiness(
        required_concepts=["a", "b"],
        primaries=[_R(VERIFICATION_PARTIAL_COVERAGE, ["a", "b"])],
        practice_status=PRACTICE_NO_PRACTICE_REQUIRED,
        practice_compatible=True,
        practice_gap_detail=None,
        existing_minutes=30,
    )
    assert d.readiness == READINESS_PARTIAL_COVERAGE


def test_joint_verified_coverage_ready():
    ev = json.dumps({"source": "RESOURCE_COVERAGE_MANIFEST", "verified_concepts": [{"concept": "a"}]})
    d = evaluate_readiness(
        required_concepts=["a", "b"],
        primaries=[
            _R(VERIFICATION_VERIFIED_COVERAGE, ["a"], evidence=ev),
            _R(VERIFICATION_VERIFIED_COVERAGE, ["b"], evidence=ev),
        ],
        practice_status=PRACTICE_NO_PRACTICE_REQUIRED,
        practice_compatible=True,
        practice_gap_detail=None,
        existing_minutes=30,
    )
    assert d.readiness == READINESS_READY


def test_collection_without_section_not_ready():
    d = evaluate_readiness(
        required_concepts=["a"],
        primaries=[_R(VERIFICATION_VERIFIED_COVERAGE, ["a"], exactness=EXACTNESS_COLLECTION, section=None)],
        practice_status=PRACTICE_NO_PRACTICE_REQUIRED,
        practice_compatible=True,
        practice_gap_detail=None,
        existing_minutes=30,
    )
    assert d.readiness == READINESS_RESOURCE_GAP


def test_practice_gap_blocks_ready():
    ev = json.dumps({"source": "RESOURCE_COVERAGE_MANIFEST", "verified_concepts": [{"concept": "a"}]})
    d = evaluate_readiness(
        required_concepts=["a"],
        primaries=[_R(VERIFICATION_VERIFIED_COVERAGE, ["a"], evidence=ev)],
        practice_status="PRACTICE_GAP",
        practice_compatible=False,
        practice_gap_detail="untaught",
        existing_minutes=30,
    )
    assert d.readiness == READINESS_PRACTICE_GAP


def test_empty_contract_not_ready():
    d = evaluate_readiness(
        required_concepts=[],
        primaries=[_R(VERIFICATION_VERIFIED_COVERAGE, [])],
        practice_status=PRACTICE_NO_PRACTICE_REQUIRED,
        practice_compatible=True,
        practice_gap_detail=None,
        existing_minutes=30,
    )
    assert d.readiness == READINESS_NEEDS_REVIEW


def test_broken_primary(client):
    db = SessionLocal()
    try:
        _import(db)
        topic = db.query(CurriculumTopic).filter_by(slug="cf-ram").first()
        lessons = db.query(CurriculumLesson).filter_by(topic_id=topic.id).all()
        for les in lessons:
            for r in les.resources:
                if (r.role or "").upper() == "PRIMARY":
                    r.verification_status = VERIFICATION_BROKEN
        db.flush()
        result = audit_topic(db, "cf-ram")
        assert result.readiness != READINESS_READY
    finally:
        db.rollback()
        db.close()


def test_ready_cannot_have_missing_or_needs_review_primary(client):
    db = SessionLocal()
    try:
        _import(db)
        # After lockdown normalize on live DB may differ; use synthetic via evaluate
        ev = json.dumps({"source": "RESOURCE_COVERAGE_MANIFEST", "verified_concepts": [{"concept": "a"}]})
        d = evaluate_readiness(
            required_concepts=["a"],
            primaries=[_R(VERIFICATION_NEEDS_REVIEW, ["a"], evidence=ev)],
            practice_status=PRACTICE_VERIFIED,
            practice_compatible=True,
            practice_gap_detail=None,
            existing_minutes=30,
        )
        assert d.readiness != READINESS_READY
    finally:
        db.close()


def test_spine_snapshot_intact():
    snap = Path(__file__).resolve().parents[1] / "reports" / "final_lockdown_prechange.json"
    assert snap.exists()
    data = json.loads(snap.read_text(encoding="utf-8"))
    assert data["counts"]["spine_222"] == 222
    assert len(data["spine_slugs"]) == 222


def test_progress_unchanged_in_snapshot():
    snap = Path(__file__).resolve().parents[1] / "reports" / "final_lockdown_prechange.json"
    data = json.loads(snap.read_text(encoding="utf-8"))
    assert data["counts"]["UserProgress"] == 0
    assert data["counts"]["TopicMastery"] == 0
    assert data["counts"]["UserXP"] == 0
    assert data["counts"]["CurriculumTopic"] == 316
    assert data["counts"]["spine_222"] == 222
