"""Anti-false-READY regression tests for final product lockdown."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.content.audit import audit_topic, _combined_coverage
from app.content.content_inspector import inspect_resource
from app.content.import_curriculum import expand_targets, import_path
from app.content.source_delivery import apply_source_delivery
from app.content.verification import (
    DEMO_CONCEPT_REGISTRY,
    EXACTNESS_COLLECTION,
    EXACTNESS_EXACT,
    EXACTNESS_MULTI_TOPIC,
    READINESS_BROKEN,
    READINESS_NEEDS_REVIEW,
    READINESS_PARTIAL_COVERAGE,
    READINESS_PRACTICE_GAP,
    READINESS_READY,
    READINESS_RESOURCE_GAP,
    RESOURCE_COVERAGE_MANIFEST,
    VERIFICATION_BROKEN,
    VERIFICATION_PARTIAL_COVERAGE,
    VERIFICATION_UNVERIFIED,
    VERIFICATION_VERIFIED_COVERAGE,
    Concept,
    TopicConcepts,
)
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic
from app.db.session import SessionLocal
from test_curriculum_v1 import V1_INDEX


def _import_v1_and_delivery(db):
    for target in expand_targets(V1_INDEX):
        import_path(target)
    apply_source_delivery(db)


def test_1_title_match_insufficient_without_concept_coverage(client):
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-cpu").first()
        assert topic
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        primaries = [r for les in lessons for r in les.resources if (r.role or "").upper() == "PRIMARY"]
        assert primaries
        for r in primaries:
            r.required_concepts_covered = []
            r.verification_status = VERIFICATION_UNVERIFIED
        db.flush()
        result = audit_topic(db, "cf-cpu")
        assert result.readiness != READINESS_READY
        assert result.missing_required
    finally:
        db.rollback()
        db.close()


def test_2_http_live_irrelevant_content_fails():
    html = "<html><body><h1>Cooking Pasta</h1><p>Boil water add salt drain noodles.</p></body></html>"
    result = inspect_resource(
        resource_slug="fake-cpu",
        url="https://example.com/pasta",
        topic_slug="cf-cpu",
        title="CPU",
        html_override=html,
    )
    assert result.verification_status != VERIFICATION_VERIFIED_COVERAGE
    assert len(result.covered) < 6


def test_3_broken_url_status():
    result = inspect_resource(
        resource_slug="broken",
        url="https://httpstat.us/404",
        topic_slug="cf-alu",
        title="ALU",
    )
    assert result.broken or result.verification_status in (VERIFICATION_BROKEN, "NEEDS_REVIEW")


def test_4_partial_coverage_blocks_ready_without_joint_peer(client):
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-cpu").first()
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        primaries = [r for les in lessons for r in les.resources if (r.role or "").upper() == "PRIMARY"]
        for r in primaries:
            r.required_concepts_covered = ["cpu-role"]
            r.verification_status = VERIFICATION_PARTIAL_COVERAGE
            r.exactness = EXACTNESS_EXACT
        db.flush()
        result = audit_topic(db, "cf-cpu")
        assert result.readiness != READINESS_READY
        assert result.missing_required
        assert result.readiness in (
            READINESS_PARTIAL_COVERAGE,
            READINESS_RESOURCE_GAP,
            READINESS_NEEDS_REVIEW,
            "PARTIALLY_READY",
        )
    finally:
        db.rollback()
        db.close()


def test_5_joint_coverage_can_ready():
    class R:
        def __init__(self, c):
            self.required_concepts_covered = c

    required = {c.slug for c in DEMO_CONCEPT_REGISTRY["cf-cpu"].required}
    union = _combined_coverage(
        [
            R(["cpu-role", "alu", "registers"]),
            R(["program-counter", "fetch-decode-execute", "ram-interaction"]),
        ]
    )
    assert required <= union


def test_6_collection_without_section_not_exact_ready():
    html = "<html><body>" + (" algorithm data structure " * 2000) + "</body></html>"
    result = inspect_resource(
        resource_slug="hub",
        url="https://example.com/tags/algorithms",
        topic_slug="cf-algorithms",
        title="Algorithms playlist",
        html_override=html,
    )
    assert result.exactness in (EXACTNESS_COLLECTION, EXACTNESS_MULTI_TOPIC)


def test_7_multitopic_requires_section_for_clean_ready(client):
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-bits-and-bytes").first()
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        primaries = [r for les in lessons for r in les.resources if (r.role or "").upper() == "PRIMARY"]
        assert primaries
        for r in primaries:
            r.exactness = EXACTNESS_MULTI_TOPIC
            r.section = None
            r.lecture = None
            r.required_concepts_covered = list(
                RESOURCE_COVERAGE_MANIFEST.get(r.slug or "", ["bit", "byte", "encoding"])
            )
            r.verification_status = VERIFICATION_VERIFIED_COVERAGE
        db.flush()
        result = audit_topic(db, "cf-bits-and-bytes")
        assert result.readiness != READINESS_READY or any(p.get("section") for p in result.primary_resources)
    finally:
        db.rollback()
        db.close()


def test_8_practice_ahead_of_learning_gap(client):
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-alu").first()
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        for les in lessons:
            for r in les.resources:
                if (r.role or "").upper() == "PRIMARY":
                    r.required_concepts_covered = [c.slug for c in DEMO_CONCEPT_REGISTRY["cf-alu"].required]
                    r.verification_status = VERIFICATION_VERIFIED_COVERAGE
                    r.exactness = EXACTNESS_EXACT
                    r.notes = "domain0 manifest"
                    r.verification_evidence = (
                        '{"source":"RESOURCE_COVERAGE_MANIFEST","verified_concepts":'
                        '[{"concept":"alu-role","evidence":"DOMAIN0_MANIFEST_INSPECTION"}]}'
                    )
            for ex in les.exercises:
                ex.concepts_required = ["untought-quantum-alu"]
                ex.destination_type = "LEETCODE"
                ex.quantity = 3
        # If no exercises exist, add one
        if lessons and not lessons[0].exercises:
            from app.db.models import LessonExercise

            db.add(
                LessonExercise(
                    slug="cf-alu-gap-ex",
                    title="Gap practice",
                    description="gap",
                    lesson_id=lessons[0].id,
                    exercise_type="CODING",
                    destination_type="LEETCODE",
                    quantity=3,
                    concepts_required=["untought-quantum-alu"],
                )
            )
        for les in lessons:
            les.hours_estimated = 1.0
        db.flush()
        result = audit_topic(db, "cf-alu")
        assert result.readiness == READINESS_PRACTICE_GAP
        assert result.practice_compatible is False
    finally:
        db.rollback()
        db.close()


def test_9_empty_concept_registry_never_ready(client):
    from app.content import audit as audit_mod

    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        original = audit_mod.get_required_concepts

        def _none(_slug):
            return None

        audit_mod.get_required_concepts = _none
        result = audit_topic(db, "cf-cpu")
        assert result.readiness != READINESS_READY
        assert result.readiness == READINESS_NEEDS_REVIEW
    finally:
        audit_mod.get_required_concepts = original
        db.close()


def test_10_mechanical_copy_detection(client):
    import app.content.verification as v

    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        original = v.DEMO_CONCEPT_REGISTRY["cf-registers"]
        v.DEMO_CONCEPT_REGISTRY["cf-registers"] = TopicConcepts(
            topic_slug="cf-registers",
            required=list(original.required) + [Concept("register-renaming-exotic", "register renaming")],
        )
        # Ensure resources don't claim the exotic concept
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-registers").first()
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        for les in lessons:
            for r in les.resources:
                if (r.role or "").upper() == "PRIMARY":
                    r.required_concepts_covered = [c.slug for c in original.required]
                    r.verification_status = VERIFICATION_VERIFIED_COVERAGE
        db.flush()
        result = audit_topic(db, "cf-registers")
        assert "register-renaming-exotic" in result.missing_required
        assert result.readiness != READINESS_READY
    finally:
        v.DEMO_CONCEPT_REGISTRY["cf-registers"] = original
        db.rollback()
        db.close()


def test_11_broken_primary_removes_ready(client):
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-ram").first()
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        for les in lessons:
            for r in les.resources:
                if (r.role or "").upper() == "PRIMARY":
                    r.verification_status = VERIFICATION_BROKEN
                    r.url = "https://example.invalid/404-broken"
        db.flush()
        result = audit_topic(db, "cf-ram")
        assert result.readiness in (READINESS_BROKEN, READINESS_RESOURCE_GAP)
        assert result.readiness != READINESS_READY
    finally:
        db.rollback()
        db.close()


def test_12_graph_immutability_snapshot_exists(client):
    snap = Path(__file__).resolve().parents[1] / "reports" / "pre_final_lock_snapshot.json"
    assert snap.exists()
    data = json.loads(snap.read_text(encoding="utf-8"))
    assert data["counts"]["CurriculumTopic"] == 316
    assert data["dag"]["ok"] is True
    assert len(data.get("spine_slugs") or []) == 222
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        before = db.query(CurriculumTopic).count()
        # audit must not create/delete topics
        audit_topic(db, "cf-cpu")
        assert db.query(CurriculumTopic).count() == before
        # spine slugs from snapshot exist after import of v1 index (subset)
        for slug in list(data["spine_slugs"])[:30]:
            if slug.startswith("cf-"):
                assert db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
    finally:
        db.close()


def test_13_progress_immutability_counts(client):
    from app.db.models import TopicMastery, UserProgress, UserXP

    snap = Path(__file__).resolve().parents[1] / "reports" / "final_lockdown_prechange.json"
    assert snap.exists()
    data = json.loads(snap.read_text(encoding="utf-8"))
    assert data["counts"]["UserProgress"] == 0
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        before = {
            "UserProgress": db.query(UserProgress).count(),
            "TopicMastery": db.query(TopicMastery).count(),
            "UserXP": db.query(UserXP).count(),
        }
        audit_topic(db, "cf-cpu")
        after = {
            "UserProgress": db.query(UserProgress).count(),
            "TopicMastery": db.query(TopicMastery).count(),
            "UserXP": db.query(UserXP).count(),
        }
        assert before == after
    finally:
        db.close()


def test_14_tcp_only_page_cannot_cover_tcp_vs_udp():
    """Regression: TCP RFC must not verify TCP-vs-UDP without mentioning UDP."""
    from app.content.lockdown_verify_v2 import inspect_for_topic

    tcp_only_html = """
    <html><body>
    <h1>Transmission Control Protocol</h1>
    <p>TCP provides reliable stream communication between hosts.
    Datagrams are reassembled into an ordered byte stream with acknowledgements.</p>
    </body></html>
    """
    # inspect_for_topic fetches live URLs; use a synthetic path via monkeypatch of fetch
    import app.content.lockdown_verify_v2 as v2

    original = v2.fetch

    def fake_fetch(url, timeout=22.0):
        return 200, tcp_only_html, None

    v2.fetch = fake_fetch
    try:
        result = inspect_for_topic(
            resource_slug="tcp-only",
            url="https://example.com/tcp-only",
            topic_slug="net-tcp-udp",
            section="TCP",
        )
        assert "udp" not in tcp_only_html.lower()
        assert result["verification_status"] != VERIFICATION_VERIFIED_COVERAGE
        assert "net-tcp-udp-tcp-vs-udp" in result["missing"]
    finally:
        v2.fetch = original


def test_15_short_technical_heading_match_heap_sort():
    """Regression: headings like 'Heap Sort' must match short technical terms."""
    from app.content.lockdown_verify_v2 import _find_heading

    heading = _find_heading(
        ["Heap Sort", "Advantages of Heap Sort"],
        ["heap", "sort", "heapsort", "array"],
    )
    assert heading == "Heap Sort"


def test_16_empty_coverage_cannot_be_ready_even_if_verified_status(client):
    """Regression: VERIFIED_COVERAGE status with empty covered list must not READY."""
    from app.content.readiness_contract import evaluate_readiness
    from types import SimpleNamespace

    primary = SimpleNamespace(
        role="PRIMARY",
        verification_status=VERIFICATION_VERIFIED_COVERAGE,
        exactness=EXACTNESS_EXACT,
        required_concepts_covered=[],
        verification_evidence='{"verification_method":"LOCKDOWN_CONTENT_INSPECTION_V2","verified_concepts":[]}',
        url="https://example.com/x",
        section="x",
        notes="",
    )
    decision = evaluate_readiness(
        required_concepts=["concept-a", "concept-b"],
        primaries=[primary],
        practice_status="NO_PRACTICE_REQUIRED",
        practice_compatible=True,
        practice_gap_detail=None,
        existing_minutes=20,
    )
    assert decision.readiness != READINESS_READY

