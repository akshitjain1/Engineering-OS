"""Learner resource visibility — hide verification clutter without breaking readiness."""
from __future__ import annotations

import json
from pathlib import Path

from app.content.audit import audit_topic
from app.content.domain0_repair import apply_domain0_repairs
from app.content.import_curriculum import expand_targets, import_path
from app.content.learner_visibility import (
    VIS_COVERAGE_SUPPLEMENT,
    apply_learner_visibility,
    is_learner_visible,
    learner_facing_resources,
    normalize_destination_url,
    restore_content_verification_statuses,
)
from app.content.resources import group_resources_by_role
from app.content.source_delivery import apply_source_delivery
from app.content.verification import (
    READINESS_READY,
    VERIFICATION_VERIFIED_COVERAGE,
)
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic
from app.db.models import TopicMastery, UserProgress, UserXP
from app.db.session import SessionLocal
from test_curriculum_v1 import V1_INDEX


def _seed_domain0(db):
    for target in expand_targets(V1_INDEX):
        import_path(target)
    apply_source_delivery(db)
    apply_domain0_repairs(db)
    restore_content_verification_statuses(db)
    apply_learner_visibility(db)
    db.flush()


def test_hidden_coverage_supplement_counts_for_readiness_not_learner_api(client):
    db = SessionLocal()
    try:
        _seed_domain0(db)

        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-cpu").first()
        assert topic
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        resources = [r for les in lessons for r in les.resources]
        pc = next(r for r in resources if r.slug == "cf-cpu-pc-supplement")
        primary = next(r for r in resources if r.slug == "cf-cpu-primary")

        assert is_learner_visible(primary) is True
        assert is_learner_visible(pc) is False
        assert pc.visibility_class == VIS_COVERAGE_SUPPLEMENT
        assert (pc.role or "").upper() == "PRIMARY"
        assert (pc.verification_status or "").upper() == VERIFICATION_VERIFIED_COVERAGE

        result = audit_topic(db, "cf-cpu")
        assert result.readiness == READINESS_READY
        assert "program-counter" in result.combined_coverage
        assert not result.missing_required

        grouped = group_resources_by_role(resources, for_learner=True)
        visible_urls = {r.get("url") for role_list in grouped.values() for r in role_list}
        assert primary.url in visible_urls
        assert pc.url not in visible_urls
    finally:
        db.rollback()
        db.close()


def test_cf_cpu_learner_list_is_minimal(client):
    db = SessionLocal()
    try:
        _seed_domain0(db)
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-cpu").first()
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        resources = [r for les in lessons for r in les.resources]
        visible = learner_facing_resources(resources)
        slugs = [r.slug for r in visible]
        assert "cf-cpu-primary" in slugs
        assert "cf-cpu-n2t" in slugs
        assert "cf-cpu-pc-supplement" not in slugs
        assert "cf-cpu-reference" not in slugs
        assert "cf-cpu-ref-cs50" not in slugs
        assert sum(1 for r in visible if (r.role or "").upper() == "PRIMARY") == 1
    finally:
        db.rollback()
        db.close()


def test_no_visible_resource_is_unmapped_source(client):
    db = SessionLocal()
    try:
        _seed_domain0(db)
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-cpu").first()
        tid = topic.id
        db.commit()
    finally:
        db.close()

    resp = client.get(f"/api/topic/{tid}")
    assert resp.status_code == 200
    body = resp.json()
    roles = body.get("resources_by_role") or {}
    for _role, items in roles.items():
        for item in items:
            assert item.get("url")
            status = (item.get("verification_status") or item.get("resource_status") or "").upper()
            assert status not in ("", "UNRESOLVED", "UNVERIFIED")


def test_duplicate_canonical_urls_not_shown_twice(client):
    db = SessionLocal()
    try:
        _seed_domain0(db)
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-cpu").first()
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        resources = [r for les in lessons for r in les.resources]
        visible = learner_facing_resources(resources)
        keys = [normalize_destination_url(r.url) for r in visible]
        assert len(keys) == len(set(keys))
    finally:
        db.rollback()
        db.close()


def test_joint_coverage_still_works_with_hidden_peer(client):
    db = SessionLocal()
    try:
        _seed_domain0(db)
        for slug in ("cf-cpu", "cf-alu", "cf-cache", "cf-instruction-execution"):
            result = audit_topic(db, slug)
            assert result.readiness == READINESS_READY, (slug, result.readiness, result.notes)
            assert not result.missing_required
    finally:
        db.rollback()
        db.close()


def test_spine_and_progress_unchanged_by_visibility(client):
    snap = Path(__file__).resolve().parents[1] / "reports" / "final_lockdown_prechange.json"
    assert snap.exists()
    data = json.loads(snap.read_text(encoding="utf-8"))
    spine = set(data.get("spine_slugs") or [])
    assert len(spine) == 222

    db = SessionLocal()
    try:
        _seed_domain0(db)
        before = {
            "topics": db.query(CurriculumTopic).count(),
            "progress": db.query(UserProgress).count(),
            "mastery": db.query(TopicMastery).count(),
            "xp": db.query(UserXP).count(),
        }
        prereq_sample = {}
        for slug in list(spine)[:40]:
            t = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
            if t is None:
                continue
            prereq_sample[slug] = list(t.prerequisites or [])

        apply_learner_visibility(db)
        db.flush()

        after = {
            "topics": db.query(CurriculumTopic).count(),
            "progress": db.query(UserProgress).count(),
            "mastery": db.query(TopicMastery).count(),
            "xp": db.query(UserXP).count(),
        }
        assert before == after
        for slug, prereqs in prereq_sample.items():
            t = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
            assert list(t.prerequisites or []) == prereqs
    finally:
        db.rollback()
        db.close()


def test_topic_api_hides_verification_resources(client):
    db = SessionLocal()
    try:
        _seed_domain0(db)
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-cpu").first()
        tid = topic.id
        db.commit()
    finally:
        db.close()

    body = client.get(f"/api/topic/{tid}").json()
    all_items = [r for items in (body.get("resources_by_role") or {}).values() for r in items]
    all_items += body.get("resources") or []
    titles = " ".join((r.get("title") or "") for r in all_items).lower()
    urls = " ".join((r.get("url") or "") for r in all_items).lower()
    assert "program counter" not in titles
    assert "wikipedia.org/wiki/program_counter" not in urls
    assert "cs50.harvard.edu/x/weeks/1" not in urls
    primaries = body.get("resources_by_role", {}).get("PRIMARY") or []
    assert len(primaries) == 1
    assert "cpu" in (primaries[0].get("title") or "").lower()
