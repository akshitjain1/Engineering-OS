"""Verification infrastructure tests - audit-only, no curriculum mutation."""
from __future__ import annotations

from app.content.audit import audit_topic, audit_all
from app.content.import_curriculum import expand_targets, import_path
from app.content.source_delivery import apply_source_delivery
from app.content.verification import (
    DEMO_CONCEPT_REGISTRY,
    EXACTNESS_COLLECTION,
    EXACTNESS_EXACT,
    READINESS_NEEDS_REVIEW,
    READINESS_PRACTICE_GAP,
    READINESS_READY,
    READINESS_RESOURCE_GAP,
    VERIFICATION_PARTIAL_COVERAGE,
    VERIFICATION_UNVERIFIED,
    VERIFICATION_VERIFIED_COVERAGE,
    realistic_time_estimate,
)
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic
from app.db.session import SessionLocal
from test_curriculum_v1 import V1_INDEX


def _import_v1_and_delivery(db):
    for target in expand_targets(V1_INDEX):
        import_path(target)
    apply_source_delivery(db)


def _get_demo_topic(db, slug: str):
    return db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()


def test_a_url_alone_does_not_make_ready(client):
    """A URL alone (UNVERIFIED, no concept coverage) must NOT be READY."""
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        result = audit_topic(db, "cf-cpu")
        assert result is not None
        # cf-cpu has a URL (GFG) but required_concepts_covered is empty -> not READY
        # Honest audit must detect missing concepts
        assert result.readiness != READINESS_READY
        assert result.readiness in (READINESS_RESOURCE_GAP, READINESS_NEEDS_REVIEW)
        assert len(result.missing_required) > 0
    finally:
        db.close()


def test_partial_resource_coverage_is_detected(client):
    """If only subset of required concepts covered, audit reports missing and PARTIALLY_READY or RESOURCE_GAP."""
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        # Simulate partial coverage by temporarily setting required_concepts_covered on primaries
        topic = _get_demo_topic(db, "cf-cpu")
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        primaries = [r for les in lessons for r in les.resources if (r.role or "").upper() == "PRIMARY"]
        assert primaries, "cf-cpu should have PRIMARY"
        # Save originals
        originals = [(r.id, r.required_concepts_covered, r.verification_status, r.exactness) for r in primaries]
        # Set partial: only 2 of 6 required concepts
        primaries[0].required_concepts_covered = ["cpu-role", "alu"]
        primaries[0].verification_status = VERIFICATION_PARTIAL_COVERAGE
        primaries[0].exactness = EXACTNESS_COLLECTION
        db.flush()
        result = audit_topic(db, "cf-cpu")
        assert result.missing_required, "partial coverage should leave missing"
        assert result.readiness in (READINESS_RESOURCE_GAP, READINESS_NEEDS_REVIEW, "PARTIALLY_READY", "PARTIAL_COVERAGE")
        # restore
        for rid, cov, vs, ex in originals:
            r = db.query(CurriculumResource).filter(CurriculumResource.id == rid).first()
            r.required_concepts_covered = cov
            r.verification_status = vs
            r.exactness = ex
        db.flush()
    finally:
        db.rollback()
        db.close()


def test_multiple_resources_can_jointly_satisfy(client):
    """Ordered PRIMARY resources can jointly cover all REQUIRED concepts -> READY."""
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        topic = _get_demo_topic(db, "cf-cpu")
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        primaries = [r for les in lessons for r in les.resources if (r.role or "").upper() == "PRIMARY"]
        # Need at least 2 primaries to test joint coverage; if only 1, create a second ordering illusion
        # For cf-cpu there is 1 PRIMARY (GFG). We simulate joint by splitting coverage across 2 virtual entries:
        # Instead, test the pure function: realistic combined coverage logic
        from app.content.audit import _combined_coverage

        # Create in-memory mock resources with required_concepts_covered
        class FakeR:
            def __init__(self, cov):
                self.required_concepts_covered = cov

        r1 = FakeR(["cpu-role", "alu", "registers"])
        r2 = FakeR(["program-counter", "fetch-decode-execute", "ram-interaction"])
        combined = _combined_coverage([r1, r2])  # type: ignore
        required = {c.slug for c in DEMO_CONCEPT_REGISTRY["cf-cpu"].required}
        assert required.issubset(combined), f"joint {combined} should cover {required}"
        assert required - combined == set()

        # Now simulate DB with joint coverage leading to READY
        originals = [(r.id, r.required_concepts_covered, r.verification_status, r.exactness) for r in primaries]
        # Use first primary to hold all 6 (simulating joint via ordered list would also work)
        # To truly test joint, add a second PRIMARY temporarily
        second = CurriculumResource(
            slug="cf-cpu-joint-test",
            title="Joint second part",
            url="https://example.com/joint",
            resource_type="documentation",
            provider="test",
            role="PRIMARY",
            order_index=1,
            lesson_id=lessons[0].id,
            verification_status=VERIFICATION_VERIFIED_COVERAGE,
            exactness=EXACTNESS_EXACT,
            required_concepts_covered=["program-counter", "fetch-decode-execute", "ram-interaction"],
            notes="domain0 manifest",
            verification_evidence='{"source":"RESOURCE_COVERAGE_MANIFEST","verified_concepts":[{"concept":"program-counter","evidence":"DOMAIN0_MANIFEST_INSPECTION"}]}',
        )
        db.add(second)
        db.flush()
        primaries[0].required_concepts_covered = ["cpu-role", "alu", "registers"]
        primaries[0].verification_status = VERIFICATION_VERIFIED_COVERAGE
        primaries[0].exactness = EXACTNESS_EXACT
        primaries[0].notes = "domain0 manifest"
        primaries[0].verification_evidence = '{"source":"RESOURCE_COVERAGE_MANIFEST","verified_concepts":[{"concept":"cpu-role","evidence":"DOMAIN0_MANIFEST_INSPECTION"}]}'
        second.required_concepts_covered = ["program-counter", "fetch-decode-execute", "ram-interaction"]
        db.flush()
        db.expire_all()
        result = audit_topic(db, "cf-cpu")
        assert result.missing_required == [], f"joint should have no missing, got {result.missing_required}"
        assert result.readiness == READINESS_READY
        # cleanup
        db.delete(second)
        for rid, cov, vs, ex in originals:
            r = db.query(CurriculumResource).filter(CurriculumResource.id == rid).first()
            if r:
                r.required_concepts_covered = cov
                r.verification_status = vs
                r.exactness = ex
        db.flush()
    finally:
        db.rollback()
        db.close()


def test_missing_required_concepts_produce_gap(client):
    """Missing REQUIRED concepts must produce RESOURCE_GAP or NEEDS_REVIEW (not READY)."""
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        topic = _get_demo_topic(db, "cf-instruction-execution")
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        for les in lessons:
            for r in les.resources:
                if (r.role or "").upper() == "PRIMARY":
                    r.required_concepts_covered = []
                    r.verification_status = VERIFICATION_UNVERIFIED
                    r.verification_evidence = None
        db.flush()
        result = audit_topic(db, "cf-instruction-execution")
        assert result.readiness != READINESS_READY
        assert result.readiness in (READINESS_RESOURCE_GAP, READINESS_NEEDS_REVIEW)
    finally:
        db.rollback()
        db.close()


def test_practice_requiring_untaught_concepts_is_detected(client):
    """Practice that requires a concept not in topic+prereqs is a PRACTICE_GAP."""
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        topic = _get_demo_topic(db, "cf-alu")
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        primaries = [r for les in lessons for r in les.resources if (r.role or "").upper() == "PRIMARY"]
        # Make primaries READY so readiness would be READY unless practice gap
        originals = [(r.id, r.required_concepts_covered, r.verification_status, r.exactness) for r in primaries]
        required_slugs = [c.slug for c in DEMO_CONCEPT_REGISTRY["cf-alu"].required]
        for r in primaries:
            r.required_concepts_covered = required_slugs
            r.verification_status = VERIFICATION_VERIFIED_COVERAGE
            r.exactness = EXACTNESS_EXACT
            r.notes = "domain0 manifest"
            r.verification_evidence = (
                '{"source":"RESOURCE_COVERAGE_MANIFEST","verified_concepts":'
                '[{"concept":"alu-role","evidence":"DOMAIN0_MANIFEST_INSPECTION"}]}'
            )
        # Also ensure existing hours present
        for les in lessons:
            les.hours_estimated = 1.0
        db.flush()
        baseline = audit_topic(db, "cf-alu")
        assert baseline.readiness == READINESS_READY

        # Now add a PRACTICE resource that requires an untaught concept
        practice = CurriculumResource(
            slug="cf-alu-practice-gap-test",
            title="Practice requiring untaught concept",
            url="https://example.com/practice",
            resource_type="exercise",
            provider="test",
            role="PRACTICE",
            order_index=99,
            lesson_id=lessons[0].id,
            verification_status=VERIFICATION_VERIFIED_COVERAGE,
            exactness=EXACTNESS_EXACT,
            required_concepts_covered=["hack-assembly-M-ram"],  # not in cf-alu required nor its prereqs
        )
        db.add(practice)
        db.flush()
        db.expire_all()
        result = audit_topic(db, "cf-alu")
        assert result.practice_compatible is False
        assert result.readiness == READINESS_PRACTICE_GAP
        # cleanup
        db.delete(practice)
        for rid, cov, vs, ex in originals:
            r = db.query(CurriculumResource).filter(CurriculumResource.id == rid).first()
            if r:
                r.required_concepts_covered = cov
                r.verification_status = vs
                r.exactness = ex
        db.flush()
    finally:
        db.rollback()
        db.close()


def test_calculated_time_works(client):
    """realistic_time_estimate sums ordered resources + practice + build."""
    assert realistic_time_estimate([{"estimated_minutes": 20}, {"estimated_minutes": 30}], practice_minutes=30, implementation_minutes=45) == 125
    assert realistic_time_estimate([{"duration": 0.5}], practice_minutes=0) == 30  # 0.5h -> 30 min fallback
    assert realistic_time_estimate([], practice_minutes=0, implementation_minutes=0) == 0
    # via audit: cf-bits-and-bytes existing 30 vs calculated from primaries
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        # set estimated_minutes on primary to make calculated deterministic
        topic = _get_demo_topic(db, "cf-bits-and-bytes")
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        primaries = [r for les in lessons for r in les.resources if (r.role or "").upper() == "PRIMARY"]
        originals = [(r.id, r.estimated_minutes) for r in primaries]
        for r in primaries:
            r.estimated_minutes = 20
        db.flush()
        result = audit_topic(db, "cf-bits-and-bytes")
        # calculated should be at least 20 + practice (exercises exist -> +20) = 40+
        assert result.calculated_time_minutes is not None and result.calculated_time_minutes >= 20
        for rid, em in originals:
            r = db.query(CurriculumResource).filter(CurriculumResource.id == rid).first()
            if r:
                r.estimated_minutes = em
        db.flush()
    finally:
        db.rollback()
        db.close()


def test_existing_curriculum_graph_remains_unchanged(client):
    """Audit must not mutate curriculum graph: original 222 spine preserved."""
    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        before_count = db.query(CurriculumTopic).count()
        before_slugs = sorted(t.slug for t in db.query(CurriculumTopic).all())
        original = [s for s in before_slugs if s and s.startswith(("cf-", "java-", "dsa-"))]
        assert len(original) == 222
        results = audit_all(db)
        after_count = db.query(CurriculumTopic).count()
        after_slugs = sorted(t.slug for t in db.query(CurriculumTopic).all())
        assert before_count == after_count
        assert before_slugs == after_slugs
        assert len(results) == before_count
        db.rollback()
        bits = db.query(CurriculumTopic).filter_by(slug="cf-bits-and-bytes").one()
        binary = db.query(CurriculumTopic).filter_by(slug="cf-binary").one()
        assert binary.prerequisites == ["cf-bits-and-bytes"]
        assert bits.name == "Bits and bytes"
    finally:
        db.close()


def test_existing_user_progress_unchanged(client):
    """Audit must not change user progress / mastery / XP tables."""
    from app.db.models import UserProgress, TopicMastery, UserXP, LessonQuestion, LessonExercise

    db = SessionLocal()
    try:
        _import_v1_and_delivery(db)
        before_progress = db.query(UserProgress).count()
        before_mastery = db.query(TopicMastery).count()
        before_xp = db.query(UserXP).count()
        # audit
        audit_all(db)
        # Simulate what audit_cli does - only reads
        after_progress = db.query(UserProgress).count()
        after_mastery = db.query(TopicMastery).count()
        after_xp = db.query(UserXP).count()
        assert before_progress == after_progress
        assert before_mastery == after_mastery
        assert before_xp == after_xp
        db.rollback()
    finally:
        db.close()
