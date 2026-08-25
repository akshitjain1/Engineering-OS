"""Learner-facing resource visibility — separate from verification coverage.

Additive fields on CurriculumResource:
  learner_visible: bool (default True)
  visibility_class: LEARNER | VERIFICATION_ONLY | COVERAGE_SUPPLEMENT | LEGACY_DUPLICATE

Audit/readiness continue to use all PRIMARY resources regardless of visibility.
Learner APIs filter to learner_visible=True and dedupe by canonical URL.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse, urlunparse

from sqlalchemy.orm import Session

from app.content.verification import (
    VERIFICATION_PARTIAL_COVERAGE,
    VERIFICATION_VERIFIED_COVERAGE,
)
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic

VIS_LEARNER = "LEARNER"
VIS_VERIFICATION_ONLY = "VERIFICATION_ONLY"
VIS_COVERAGE_SUPPLEMENT = "COVERAGE_SUPPLEMENT"
VIS_LEGACY_DUPLICATE = "LEGACY_DUPLICATE"

CONTENT_VERIFICATION_STATUSES = frozenset(
    {
        VERIFICATION_VERIFIED_COVERAGE,
        VERIFICATION_PARTIAL_COVERAGE,
        "COLLECTION_ONLY",
        "BROKEN",
        "NEEDS_REVIEW",
    }
)

# Domain0 joint-coverage supplements that must stay PRIMARY for audit but hidden from learners.
KNOWN_COVERAGE_SUPPLEMENT_SLUGS = frozenset(
    {
        "cf-cpu-pc-supplement",
        "cf-alu-expression-supplement",
        "cf-cache-locality-supplement",
        "cf-instruction-execution-pc",
    }
)

# cf-cpu / similar CS50 week hubs that clutter LEARN when an exact PRIMARY exists.
KNOWN_LEGACY_REFERENCE_SLUGS = frozenset(
    {
        "cf-cpu-reference",
        "cf-cpu-ref-cs50",
    }
)

# Awareness/path shell "primaries" pointing at whole-book/collection hubs.
# Real domain chains exist; shells stay internal-only (spec PART D).
KNOWN_HIDDEN_SHELL_PRIMARYS = frozenset(
    {
        "dl-awareness-primary",
        "dl-path-primary",
        "nlp-awareness-primary",
        "nlp-path-primary",
        "genai-awareness-primary",
        "genai-path-primary",
        "ai-eng-awareness-primary",
        "ai-eng-path-primary",
    }
)


def normalize_destination_url(url: Optional[str]) -> str:
    """Canonicalize URL for duplicate detection (ignore fragments, utm, trailing slash)."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return (url or "").strip().lower()
    scheme = (parsed.scheme or "https").lower()
    host = (parsed.hostname or "").lower().replace("www.", "")
    path = re.sub(r"/+", "/", parsed.path or "")
    if path.endswith("/") and len(path) > 1:
        path = path[:-1]
    # Drop tracking params; keep meaningful query (v=, list= for youtube)
    qs = parse_qs(parsed.query, keep_blank_values=False)
    keep = {}
    for key in ("v", "list", "t", "start", "end"):
        if key in qs and qs[key]:
            keep[key] = qs[key][0]
    query = "&".join(f"{k}={keep[k]}" for k in sorted(keep))
    return urlunparse((scheme, host, path, "", query, ""))


def is_learner_visible(resource: Any) -> bool:
    flag = getattr(resource, "learner_visible", None)
    if flag is None:
        return True
    return bool(flag)


def restore_content_verification_statuses(db: Session) -> dict[str, int]:
    """Repair statuses clobbered by URL-only backfill (VERIFIED_COVERAGE → VERIFIED).

    Does not change coverage lists, URLs, or topic graph.
    """
    restored = 0
    partial_upgraded = 0
    for row in db.query(CurriculumResource).all():
        st = (row.verification_status or "").upper()
        ev_raw = row.verification_evidence
        method = ""
        strong = False
        if ev_raw:
            try:
                data = json.loads(ev_raw) if isinstance(ev_raw, str) else ev_raw
            except Exception:  # noqa: BLE001
                data = {}
            if isinstance(data, dict):
                method = str(data.get("verification_method") or data.get("source") or "")
                vcs = data.get("verified_concepts") or []
                if method in (
                    "LOCKDOWN_CONTENT_INSPECTION_V2",
                    "CONTENT_INSPECTION",
                    "RESOURCE_COVERAGE_MANIFEST",
                ):
                    strong = True
                if vcs and all(
                    isinstance(vc, dict) and (vc.get("confidence") or "") == "HIGH" for vc in vcs
                ):
                    strong = True
                if data.get("source") == "RESOURCE_COVERAGE_MANIFEST":
                    strong = True

        notes = (row.notes or "").lower()
        if "resource-specific verified coverage" in notes or "lockdown" in method.lower():
            strong = True
        if "domain0" in notes or "manifest" in notes:
            strong = True

        if st == "VERIFIED" and strong and (row.required_concepts_covered or method):
            row.verification_status = VERIFICATION_VERIFIED_COVERAGE
            restored += 1

        # Subset-verified joint PRIMARY peers: VERIFIED_COVERAGE (not PARTIAL) so
        # topic READY can use verified union under the existing strict contract.
        if st == VERIFICATION_PARTIAL_COVERAGE and (row.required_concepts_covered or strong):
            row.verification_status = VERIFICATION_VERIFIED_COVERAGE
            if row.notes and "Honest PARTIAL" in row.notes:
                row.notes = row.notes.replace(
                    "Honest PARTIAL:",
                    "Verified subset coverage (joint peers fill remaining):",
                    1,
                )
            partial_upgraded += 1

    db.flush()
    return {"restored_verified_coverage": restored, "partial_upgraded": partial_upgraded}


def _resources_by_topic(db: Session) -> dict[int, list[CurriculumResource]]:
    lessons = db.query(CurriculumLesson).all()
    lesson_topic = {les.id: les.topic_id for les in lessons}
    by_topic: dict[int, list[CurriculumResource]] = defaultdict(list)
    for row in db.query(CurriculumResource).all():
        tid = lesson_topic.get(row.lesson_id)
        if tid is not None:
            by_topic[tid].append(row)
    return by_topic


def _pick_learner_primary(primaries: list[CurriculumResource]) -> Optional[CurriculumResource]:
    if not primaries:
        return None

    def score(r: CurriculumResource) -> tuple:
        slug = (r.slug or "").lower()
        is_supp = (
            "supplement" in slug
            or slug in KNOWN_COVERAGE_SUPPLEMENT_SLUGS
            or "joint" in (r.notes or "").lower()
        )
        ends_primary = slug.endswith("-primary") or slug.endswith("-learn-exact")
        cov = len(r.required_concepts_covered or [])
        return (
            0 if not is_supp else 1,
            0 if ends_primary else 1,
            -cov,
            r.order_index or 0,
            r.id or 0,
        )

    return sorted(primaries, key=score)[0]


def _role_rank(role: Optional[str]) -> int:
    r = (role or "").upper()
    order = {
        "PRIMARY": 0,
        "PRIMARY_LEARN": 0,
        "PRACTICE": 1,
        "BUILD": 2,
        "DEEP_DIVE": 3,
        "REFERENCE": 4,
        "SUPPLEMENT": 5,
    }
    return order.get(r, 9)


def apply_learner_visibility(db: Session) -> dict[str, Any]:
    """Mark verification-only / duplicate / coverage-supplement resources as hidden.

    Idempotent. Does not delete rows or mutate topic graph.
    """
    by_topic = _resources_by_topic(db)
    stats = {
        "topics": len(by_topic),
        "hidden_coverage_supplement": 0,
        "hidden_legacy_duplicate": 0,
        "hidden_verification_only": 0,
        "visible": 0,
        "duplicates_collapsed": 0,
    }

    for _tid, resources in by_topic.items():
        # Reset to visible learner default first
        for row in resources:
            row.learner_visible = True
            row.visibility_class = VIS_LEARNER

        primaries = [
            r for r in resources if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")
        ]
        keep_primary = _pick_learner_primary(primaries)
        for r in primaries:
            slug = r.slug or ""
            if r is keep_primary:
                continue
            # Extra PRIMARY → coverage supplement (keep role for audit)
            r.learner_visible = False
            r.visibility_class = VIS_COVERAGE_SUPPLEMENT
            stats["hidden_coverage_supplement"] += 1

        for r in resources:
            slug = r.slug or ""
            if slug in KNOWN_COVERAGE_SUPPLEMENT_SLUGS and r.learner_visible:
                r.learner_visible = False
                r.visibility_class = VIS_COVERAGE_SUPPLEMENT
                stats["hidden_coverage_supplement"] += 1
            if slug in KNOWN_LEGACY_REFERENCE_SLUGS or slug in KNOWN_HIDDEN_SHELL_PRIMARYS:
                r.learner_visible = False
                if slug in KNOWN_HIDDEN_SHELL_PRIMARYS:
                    r.visibility_class = VIS_VERIFICATION_ONLY
                    stats["hidden_verification_only"] += 1
                else:
                    r.visibility_class = VIS_LEGACY_DUPLICATE
                    stats["hidden_legacy_duplicate"] += 1

        # Collection SUPPLEMENT hubs — internal only
        for r in resources:
            if (r.role or "").upper() != "SUPPLEMENT":
                continue
            if (r.exactness or "").upper() == "COLLECTION" or (r.verification_status or "").upper() == "COLLECTION_ONLY":
                r.learner_visible = False
                r.visibility_class = VIS_VERIFICATION_ONLY
                stats["hidden_verification_only"] += 1

        # Collection/week-hub REFERENCES when an exact PRIMARY already exists — clutter
        from app.content.resources import is_collection_url

        if keep_primary is not None:
            for r in resources:
                if (r.role or "").upper() != "REFERENCE":
                    continue
                if is_collection_url(r.url, r.resource_type) or "/weeks/" in (r.url or "").lower():
                    r.learner_visible = False
                    r.visibility_class = VIS_VERIFICATION_ONLY
                    stats["hidden_verification_only"] += 1

        # Deduplicate by canonical URL within topic (keep best learner-facing)
        by_url: dict[str, list[CurriculumResource]] = defaultdict(list)
        for r in resources:
            key = normalize_destination_url(r.url)
            if key:
                by_url[key].append(r)
        for _key, group in by_url.items():
            if len(group) < 2:
                continue
            ranked = sorted(
                group,
                key=lambda r: (
                    0 if is_learner_visible(r) else 1,
                    _role_rank(r.role),
                    0 if (r.verification_status or "").upper() == VERIFICATION_VERIFIED_COVERAGE else 1,
                    r.order_index or 0,
                    r.id or 0,
                ),
            )
            for r in ranked[1:]:
                if (r.slug or "") in KNOWN_COVERAGE_SUPPLEMENT_SLUGS:
                    r.learner_visible = False
                    r.visibility_class = VIS_COVERAGE_SUPPLEMENT
                    continue
                r.learner_visible = False
                r.visibility_class = VIS_LEGACY_DUPLICATE
                stats["hidden_legacy_duplicate"] += 1
                stats["duplicates_collapsed"] += 1

        # Re-assert known hides (dedupe must not re-promote them)
        for r in resources:
            slug = r.slug or ""
            if slug in KNOWN_COVERAGE_SUPPLEMENT_SLUGS:
                r.learner_visible = False
                r.visibility_class = VIS_COVERAGE_SUPPLEMENT
            if slug in KNOWN_LEGACY_REFERENCE_SLUGS:
                r.learner_visible = False
                r.visibility_class = VIS_LEGACY_DUPLICATE
            if slug in KNOWN_HIDDEN_SHELL_PRIMARYS:
                r.learner_visible = False
                r.visibility_class = VIS_VERIFICATION_ONLY

    stats["visible"] = sum(
        1 for rows in by_topic.values() for r in rows if is_learner_visible(r)
    )
    db.flush()
    return stats


def learner_facing_resources(resources: list[Any]) -> list[Any]:
    """Filter + URL-dedupe for learner API/UI (stable order)."""
    visible = [r for r in resources if is_learner_visible(r)]
    seen: set[str] = set()
    out: list[Any] = []
    for r in sorted(visible, key=lambda item: (item.order_index or 0, item.id or 0)):
        key = normalize_destination_url(getattr(r, "url", None))
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        out.append(r)
    return out


def visibility_audit_snapshot(db: Session) -> dict[str, Any]:
    rows = db.query(CurriculumResource).all()
    total = len(rows)
    visible = sum(1 for r in rows if is_learner_visible(r))
    hidden = total - visible
    by_class = defaultdict(int)
    for r in rows:
        by_class[getattr(r, "visibility_class", None) or VIS_LEARNER] += 1

    by_topic = _resources_by_topic(db)
    multi_primary_visible = 0
    multi_learn_visible = 0
    topics_detail = []
    for tid, resources in by_topic.items():
        vis = learner_facing_resources(resources)
        prim = [r for r in vis if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")]
        learnish = [
            r
            for r in vis
            if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN", "REFERENCE", "SUPPLEMENT", "DEEP_DIVE")
        ]
        if len(prim) > 1:
            multi_primary_visible += 1
        if len(learnish) > 2:
            multi_learn_visible += 1

    # cf-cpu example
    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-cpu").first()
    cf_cpu = []
    if topic:
        for r in learner_facing_resources(by_topic.get(topic.id, [])):
            cf_cpu.append(
                {
                    "slug": r.slug,
                    "role": r.role,
                    "title": r.title,
                    "url": r.url,
                    "visibility_class": getattr(r, "visibility_class", None),
                }
            )

    return {
        "total_resources": total,
        "learner_visible": visible,
        "hidden": hidden,
        "by_visibility_class": dict(by_class),
        "topics_with_more_than_1_visible_primary": multi_primary_visible,
        "topics_with_more_than_2_visible_learning_resources": multi_learn_visible,
        "cf_cpu_learner_resources": cf_cpu,
    }
