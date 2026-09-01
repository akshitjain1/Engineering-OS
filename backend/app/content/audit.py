"""Curriculum audit system - reports readiness without mutating curriculum graph.

For every topic reports:
1. topic slug
2. topic name
3. learning objective
4. required concepts
5. PRIMARY learning resources (ordered)
6. combined concept coverage
7. missing required concepts
8. resource verification status
9. practice compatibility
10. existing time estimate
11. calculated time estimate
12. resource readiness classification

Readiness:
  READY
  PARTIALLY_READY
  RESOURCE_GAP
  PRACTICE_GAP
  TIME_UNVERIFIED
  NEEDS_REVIEW
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from sqlalchemy.orm import Session, selectinload

from app.content.readiness_contract import evaluate_readiness
from app.content.resources import serialize_resource
from app.content.verification import (
    DEMO_CONCEPT_REGISTRY,
    EXACTNESS_COLLECTION,
    EXACTNESS_EXACT,
    EXACTNESS_MULTI_TOPIC,
    PRACTICE_GAP,
    PRACTICE_NO_PRACTICE_REQUIRED,
    PRACTICE_UNVERIFIED,
    PRACTICE_VERIFIED,
    READINESS_BROKEN,
    READINESS_NEEDS_REVIEW,
    READINESS_PARTIAL_COVERAGE,
    READINESS_PARTIALLY_READY,
    READINESS_PRACTICE_GAP,
    READINESS_PRACTICE_UNVERIFIED,
    READINESS_READY,
    READINESS_RESOURCE_GAP,
    READINESS_TIME_UNVERIFIED,
    VERIFICATION_BROKEN,
    VERIFICATION_COLLECTION_ONLY,
    VERIFICATION_NEEDS_REVIEW,
    VERIFICATION_PARTIAL_COVERAGE,
    VERIFICATION_UNVERIFIED,
    VERIFICATION_VERIFIED_COVERAGE,
    get_required_concepts,
    realistic_time_estimate,
)
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic


@dataclass
class PracticeItem:
    type: str  # e.g. SELF_REFLECTION, CODING, CHATGPT
    destination: str
    instructions: str
    estimated_minutes: int
    concepts_required: list[str] = field(default_factory=list)
    quantity: Optional[int] = None
    destination_type: Optional[str] = None


@dataclass
class AuditResult:
    topic_slug: str
    topic_name: str
    learning_objective: str
    required_concepts: list[str]
    primary_resources: list[dict[str, Any]]
    combined_coverage: list[str]
    missing_required: list[str]
    verification_status: str
    exactness: str
    practice_items: list[PracticeItem]
    practice_compatible: bool
    practice_gap_detail: Optional[str]
    practice_status: str
    existing_time_minutes: Optional[int]
    calculated_time_minutes: Optional[int]
    readiness: str
    notes: Optional[str] = None
    domain_key: Optional[str] = None
    learning_track: Optional[str] = None
    depth_target: Optional[str] = None
    estimate_confidence: Optional[str] = None
    estimate_method: Optional[str] = None


@dataclass
class AuditIndex:
    """Whole-curriculum prefetch so a sweep of audit_topic is not N+1.

    audit_topic issues ~7 queries per topic on its own (a lesson query per
    helper, plus a lazy load per lesson for resources and exercises). Over 449
    topics that is ~2.2k queries. Passing an index built by build_audit_index
    collapses that to three, and every audit_topic result is byte-identical --
    the ordering here is the same (order_index, id) the per-topic query used.
    """

    topics_by_slug: dict[str, CurriculumTopic] = field(default_factory=dict)
    lessons_by_topic: dict[int, list[CurriculumLesson]] = field(default_factory=dict)


def build_audit_index(db: Session) -> AuditIndex:
    topics = db.query(CurriculumTopic).all()
    lessons = (
        db.query(CurriculumLesson)
        .options(
            selectinload(CurriculumLesson.resources),
            selectinload(CurriculumLesson.exercises),
        )
        .order_by(CurriculumLesson.order_index, CurriculumLesson.id)
        .all()
    )
    index = AuditIndex()
    for topic in topics:
        if topic.slug:
            index.topics_by_slug[topic.slug] = topic
    for lesson in lessons:
        index.lessons_by_topic.setdefault(lesson.topic_id, []).append(lesson)
    return index


def _topic_lessons(
    db: Session, topic: CurriculumTopic, index: Optional[AuditIndex] = None
) -> list[CurriculumLesson]:
    if index is not None:
        return index.lessons_by_topic.get(topic.id, [])
    return (
        db.query(CurriculumLesson)
        .filter(CurriculumLesson.topic_id == topic.id)
        .order_by(CurriculumLesson.order_index, CurriculumLesson.id)
        .all()
    )


def _all_resources_for_topic(
    db: Session, topic: CurriculumTopic, index: Optional[AuditIndex] = None
) -> list[CurriculumResource]:
    lessons = _topic_lessons(db, topic, index)
    out: list[CurriculumResource] = []
    for les in lessons:
        out.extend(sorted(les.resources, key=lambda r: (r.order_index or 0, r.id or 0)))
    return out


def _ordered_primary_resources(resources: list[CurriculumResource]) -> list[CurriculumResource]:
    primaries = [r for r in resources if (r.role or "").upper() == "PRIMARY"]
    # Also accept PRIMARY_LEARN alias if data uses new role; but current DB uses PRIMARY
    if not primaries:
        primaries = [r for r in resources if (r.role or "").upper() == "PRIMARY_LEARN"]
    primaries.sort(key=lambda r: (r.order_index or 0, r.id or 0))
    return primaries


def _collect_practice_items(
    db: Session, topic: CurriculumTopic, index: Optional[AuditIndex] = None
) -> list[PracticeItem]:
    lessons = _topic_lessons(db, topic, index)
    items: list[PracticeItem] = []
    for les in lessons:
        for ex in les.exercises:
            concepts_required: list[str] = list(ex.concepts_required or [])
            dest = ex.destination_type or ex.exercise_type or "SELF_REFLECTION"
            dest_url = ex.destination_url or ""
            qty = ex.quantity
            instructions = (ex.practice_instructions or ex.description or ex.title or "")[:500]
            items.append(
                PracticeItem(
                    type=dest,
                    destination=dest_url or dest,
                    instructions=instructions,
                    estimated_minutes=20,
                    concepts_required=concepts_required,
                    quantity=qty,
                    destination_type=ex.destination_type,
                )
            )
    for r in _all_resources_for_topic(db, topic, index):
        if (r.role or "").upper() == "PRACTICE":
            items.append(
                PracticeItem(
                    type="RESOURCE_PRACTICE",
                    destination=r.url or "unknown",
                    instructions=r.title,
                    estimated_minutes=int(r.estimated_minutes or (r.duration * 60 if r.duration else 20)),
                    concepts_required=list(r.required_concepts_covered or []),
                    quantity=None,
                    destination_type="RESOURCE_URL",
                )
            )
    return items


def _combined_coverage(primary_resources: list[CurriculumResource]) -> set[str]:
    covered: set[str] = set()
    for r in primary_resources:
        if r.required_concepts_covered:
            for c in r.required_concepts_covered:
                covered.add(str(c).strip())
        # notes/exactness not used for coverage; only required_concepts_covered field
    return covered


def _verification_for_primaries(primaries: list[CurriculumResource]) -> tuple[str, str]:
    """Return (verification_status, exactness) aggregated over ordered PRIMARY resources.

    Rules:
    - No PRIMARY -> UNVERIFIED / COLLECTION (gap)
    - Any BROKEN url -> BROKEN
    - All VERIFIED_COVERAGE and EXACT -> VERIFIED_COVERAGE / EXACT
    - Mix of VERIFIED and PARTIAL -> PARTIAL_COVERAGE
    - Collection-only URLs -> COLLECTION_ONLY
    - Otherwise UNVERIFIED
    """
    if not primaries:
        return VERIFICATION_UNVERIFIED, EXACTNESS_COLLECTION
    statuses = [(r.verification_status or VERIFICATION_UNVERIFIED) for r in primaries]
    exactnesses = [(r.exactness or ("EXACT" if getattr(r, "exact", None) else "COLLECTION") if hasattr(r, "exactness") else "COLLECTION") for r in primaries]
    # Also handle explicit exactness column if set, else derive from serialize_resource exact flag
    # Normalize legacy VERIFIED/UNRESOLVED to new taxonomy for audit display
    norm_statuses: list[str] = []
    for s in statuses:
        if s == "VERIFIED":
            # Legacy HTTPS/title verification — NOT content inspection
            norm_statuses.append(VERIFICATION_NEEDS_REVIEW)
        elif s == "TRUSTED":
            # TRUSTED = reputable provider, not content-inspected
            norm_statuses.append(VERIFICATION_NEEDS_REVIEW)
        elif s == "UNRESOLVED":
            norm_statuses.append(VERIFICATION_UNVERIFIED)
        elif s in (
            VERIFICATION_VERIFIED_COVERAGE,
            VERIFICATION_PARTIAL_COVERAGE,
            VERIFICATION_COLLECTION_ONLY,
            VERIFICATION_BROKEN,
            VERIFICATION_NEEDS_REVIEW,
            VERIFICATION_UNVERIFIED,
        ):
            norm_statuses.append(s)
        else:
            norm_statuses.append(VERIFICATION_UNVERIFIED)
    if any(s == VERIFICATION_BROKEN for s in norm_statuses):
        return VERIFICATION_BROKEN, EXACTNESS_COLLECTION
    if any(s == VERIFICATION_COLLECTION_ONLY for s in norm_statuses):
        return VERIFICATION_COLLECTION_ONLY, EXACTNESS_COLLECTION
    if all(s == VERIFICATION_VERIFIED_COVERAGE for s in norm_statuses):
        if all(e == EXACTNESS_EXACT for e in exactnesses):
            return VERIFICATION_VERIFIED_COVERAGE, EXACTNESS_EXACT
        if any(e == EXACTNESS_MULTI_TOPIC for e in exactnesses):
            return VERIFICATION_VERIFIED_COVERAGE, EXACTNESS_MULTI_TOPIC
        return VERIFICATION_VERIFIED_COVERAGE, EXACTNESS_COLLECTION
    if any(s == VERIFICATION_PARTIAL_COVERAGE for s in norm_statuses):
        # Prefer PARTIAL aggregate when any primary is partial (joint coverage may still fill gaps)
        return VERIFICATION_PARTIAL_COVERAGE, EXACTNESS_EXACT
    if all(s == VERIFICATION_UNVERIFIED for s in norm_statuses):
        return VERIFICATION_UNVERIFIED, EXACTNESS_COLLECTION
    if any(s == VERIFICATION_NEEDS_REVIEW for s in norm_statuses) and all(
        s in (VERIFICATION_NEEDS_REVIEW, VERIFICATION_VERIFIED_COVERAGE, VERIFICATION_PARTIAL_COVERAGE)
        for s in norm_statuses
    ):
        # Mix of TRUSTED/NEEDS_REVIEW with verified peers — escalate only if no verified content
        if any(s == VERIFICATION_VERIFIED_COVERAGE for s in norm_statuses):
            return VERIFICATION_VERIFIED_COVERAGE, EXACTNESS_EXACT
        return VERIFICATION_NEEDS_REVIEW, EXACTNESS_COLLECTION
    return VERIFICATION_NEEDS_REVIEW, EXACTNESS_COLLECTION


def audit_topic(
    db: Session, topic_slug: str, index: Optional[AuditIndex] = None
) -> Optional[AuditResult]:
    topic: Optional[CurriculumTopic]
    if index is not None:
        topic = index.topics_by_slug.get(topic_slug)
    else:
        topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == topic_slug).first()
    if not topic:
        return None
    lessons = _topic_lessons(db, topic, index)
    resources = _all_resources_for_topic(db, topic, index)
    primaries = _ordered_primary_resources(resources)

    lo = ""
    if lessons and lessons[0].description:
        lo = lessons[0].description
    elif topic.description:
        lo = topic.description

    registry_entry = get_required_concepts(topic_slug)
    required_concepts = [c.slug for c in registry_entry.required] if registry_entry else []
    required_set = set(required_concepts)

    combined = _combined_coverage(primaries)
    missing = sorted(required_set - combined)

    verification_status, exactness = _verification_for_primaries(primaries)

    # If any primary has inspected coverage stored, treat aggregation via coverage first
    inspected = [r for r in primaries if r.required_concepts_covered]
    if inspected and required_set:
        # Prefer coverage-driven status when evidence exists
        if not missing and all(
            (r.verification_status or "")
            in (VERIFICATION_VERIFIED_COVERAGE, VERIFICATION_PARTIAL_COVERAGE, "VERIFIED")
            or (r.required_concepts_covered)
            for r in inspected
        ):
            # Require at least one VERIFIED_COVERAGE or PARTIAL among primaries contributing coverage
            statuses = {(r.verification_status or "") for r in primaries}
            if VERIFICATION_BROKEN in statuses or "BROKEN" in statuses:
                verification_status = VERIFICATION_BROKEN
            elif VERIFICATION_COLLECTION_ONLY in statuses and not any(
                (r.exactness or "") in (EXACTNESS_EXACT, EXACTNESS_MULTI_TOPIC) and (r.section or r.lecture)
                for r in primaries
            ):
                # collection-only primary without navigation still blocks unless joint EXACT peers cover
                if all((r.exactness or "") == EXACTNESS_COLLECTION for r in primaries):
                    verification_status = VERIFICATION_COLLECTION_ONLY
                elif not missing:
                    verification_status = VERIFICATION_VERIFIED_COVERAGE
            elif not missing:
                if any((r.verification_status or "") == VERIFICATION_PARTIAL_COVERAGE for r in primaries) and any(
                    (r.verification_status or "") == VERIFICATION_VERIFIED_COVERAGE for r in primaries
                ):
                    verification_status = VERIFICATION_PARTIAL_COVERAGE  # joint
                elif not missing:
                    verification_status = VERIFICATION_VERIFIED_COVERAGE
            else:
                verification_status = VERIFICATION_PARTIAL_COVERAGE

    practice_items = _collect_practice_items(db, topic, index)
    practice_concepts: set[str] = set()
    for pi in practice_items:
        for c in pi.concepts_required:
            practice_concepts.add(c)

    # Prereq refs may be legacy strings or enhanced {"slug","type"} dicts.
    prereq_slugs = {
        p if isinstance(p, str) else (p.get("slug") or p.get("topic"))
        for p in (topic.prerequisites or [])
    }
    prereq_slugs.discard(None)
    prereq_concepts: set[str] = set()
    for ps in prereq_slugs:
        rc = get_required_concepts(ps)
        if rc:
            prereq_concepts.update(c.slug for c in rc.required)

    allowed = required_set | prereq_concepts | combined
    gap_concepts = sorted(practice_concepts - allowed)
    practice_compatible = len(gap_concepts) == 0
    gap_detail = f"practice requires {gap_concepts} not in topic+prereqs" if gap_concepts else None

    # Practice status classification
    domain = topic.domain_key or ""
    practice_oriented = domain in ("dsa", "java", "python", "web", "backend", "ml", "data-science") or (
        topic_slug or ""
    ).startswith(("dsa-", "java-"))
    has_concrete = any(
        (pi.destination_type and pi.quantity)
        for pi in practice_items
    )
    if practice_concepts and gap_concepts:
        practice_status = PRACTICE_GAP
    elif not practice_oriented:
        # Foundations / career / soft tracks: reflection exercises do not block READY
        practice_status = PRACTICE_NO_PRACTICE_REQUIRED
    elif has_concrete and practice_compatible:
        practice_status = PRACTICE_VERIFIED
    elif practice_items and all((pi.type or "") == "SELF_REFLECTION" for pi in practice_items):
        practice_status = PRACTICE_UNVERIFIED
    elif not practice_items:
        practice_status = PRACTICE_UNVERIFIED
    else:
        practice_status = PRACTICE_UNVERIFIED

    existing_minutes: Optional[int] = None
    if lessons:
        total_hours = sum(float(les.hours_estimated or 0) for les in lessons)
        existing_minutes = int(total_hours * 60) if total_hours else None

    primary_dicts = []
    confidences = []
    methods = []
    for r in primaries:
        primary_dicts.append(
            {
                "estimated_minutes": r.estimated_minutes,
                "duration": r.duration,
                "title": r.title,
            }
        )
        if r.estimate_confidence:
            confidences.append(r.estimate_confidence)
        if getattr(r, "estimate_method", None):
            methods.append(r.estimate_method)

    practice_minutes = sum(pi.estimated_minutes for pi in practice_items) if practice_items else 0
    build_minutes = 0
    for r in resources:
        if (r.role or "").upper() == "BUILD":
            build_minutes += int(r.estimated_minutes or 25)

    calculated_minutes = realistic_time_estimate(
        primary_dicts, practice_minutes=practice_minutes, implementation_minutes=build_minutes
    )
    if not primaries and not practice_items and build_minutes == 0:
        calculated_minutes = 0

    estimate_confidence = None
    if confidences:
        if all(c == "HIGH" for c in confidences):
            estimate_confidence = "HIGH"
        elif any(c == "LOW" for c in confidences):
            estimate_confidence = "LOW"
        else:
            estimate_confidence = "MEDIUM"
    estimate_method = methods[0] if methods else None

    awareness_only = (topic.depth_target or "").upper() == "AWARENESS"

    decision = evaluate_readiness(
        required_concepts=required_concepts,
        primaries=primaries,
        practice_status=practice_status,
        practice_compatible=practice_compatible,
        practice_gap_detail=gap_detail,
        existing_minutes=existing_minutes,
        awareness_only=awareness_only,
    )
    readiness = decision.readiness
    notes = decision.notes
    if decision.contradictions:
        notes = (notes or "") + " | contradictions: " + "; ".join(decision.contradictions)

    primary_payloads: list[dict[str, Any]] = []
    for r in primaries:
        ser = serialize_resource(r)
        primary_payloads.append(
            {
                "slug": r.slug,
                "title": r.title,
                "provider": r.provider,
                "url": r.url,
                "resource_type": r.resource_type,
                "role": r.role,
                "order": r.order_index,
                "estimated_minutes": r.estimated_minutes,
                "estimate_confidence": r.estimate_confidence,
                "estimate_method": getattr(r, "estimate_method", None),
                "duration": r.duration,
                "section": r.section,
                "lecture": r.lecture,
                "required_concepts_covered": list(r.required_concepts_covered or []),
                "verification_status": r.verification_status,
                "exactness": r.exactness,
                "notes": r.notes,
                "serialized_exact": ser.get("exact"),
                "serialized_exactness": ser.get("exactness"),
            }
        )

    return AuditResult(
        topic_slug=topic_slug,
        topic_name=topic.name,
        learning_objective=lo[:500],
        required_concepts=required_concepts,
        primary_resources=primary_payloads,
        combined_coverage=sorted(combined),
        missing_required=missing,
        verification_status=verification_status,
        exactness=exactness,
        practice_items=practice_items,
        practice_compatible=practice_compatible,
        practice_gap_detail=gap_detail,
        practice_status=practice_status,
        existing_time_minutes=existing_minutes,
        calculated_time_minutes=calculated_minutes,
        readiness=readiness,
        notes=notes,
        domain_key=topic.domain_key,
        learning_track=topic.learning_track,
        depth_target=topic.depth_target,
        estimate_confidence=estimate_confidence,
        estimate_method=estimate_method,
    )


def audit_all(db: Session) -> list[AuditResult]:
    topics = db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()
    results: list[AuditResult] = []
    for t in topics:
        r = audit_topic(db, t.slug)
        if r:
            results.append(r)
    return results


def audit_demo_topics(db: Session) -> list[AuditResult]:
    demo_slugs = [
        "cf-bits-and-bytes",
        "cf-binary",
        "cf-hexadecimal",
        "cf-cpu",
        "cf-alu",
        "cf-registers",
        "cf-ram",
        "cf-cache",
        "cf-storage",
        "cf-instruction-execution",
    ]
    out: list[AuditResult] = []
    for slug in demo_slugs:
        r = audit_topic(db, slug)
        if r:
            out.append(r)
    return out
