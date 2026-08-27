from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "dev.db"


def _set(obj: Any, name: str, value: Any) -> None:
    if hasattr(obj, name):
        setattr(obj, name, value)


def _update_metadata(row: CurriculumResource, **values: Any) -> None:
    for k, v in values.items():
        _set(row, k, v)


def _find_topic_lesson(db: Session, slug: str) -> tuple[CurriculumTopic, CurriculumLesson] | None:
    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
    if not topic:
        return None
    lesson = (
        db.query(CurriculumLesson)
        .filter(CurriculumLesson.topic_id == topic.id)
        .order_by(CurriculumLesson.order_index, CurriculumLesson.id)
        .first()
    )
    if not lesson:
        return None
    return topic, lesson


def _resources_for_topic(db: Session, topic_slug: str) -> list[CurriculumResource]:
    found = _find_topic_lesson(db, topic_slug)
    if not found:
        return []
    _, lesson = found
    return db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id).all()


def _ensure_resource(
    db: Session,
    *,
    topic_slug: str,
    slug: str,
    title: str,
    url: str,
    provider: str,
    resource_type: str,
    role: str,
    order: int,
    description: str,
    estimated_minutes: int,
    estimate_confidence: str,
    exactness: str,
    verification_status: str = "NEEDS_REVIEW",
    boundary_type: str | None = None,
    start_boundary: str | None = None,
    end_boundary: str | None = None,
    start_timestamp: str | None = None,
    end_timestamp: str | None = None,
    video_id: str | None = None,
    visibility_class: str = "LEARNER",
    learner_visible: bool = True,
    note: str | None = None,
) -> tuple[CurriculumResource | None, bool]:
    found = _find_topic_lesson(db, topic_slug)
    if not found:
        return None, False
    _, lesson = found
    row = db.query(CurriculumResource).filter(CurriculumResource.slug == slug).first()
    created = False
    if row is None:
        row = CurriculumResource(
            slug=slug,
            title=title,
            url=url,
            resource_type=resource_type,
            provider=provider,
            description=description,
            official_unofficial="official",
            order_index=order,
            lesson_id=lesson.id,
            role=role,
            section=start_boundary,
            lecture=None,
            video_id=video_id,
            verification_status=verification_status,
        )
        db.add(row)
        created = True
    _update_metadata(
        row,
        title=title,
        url=url,
        provider=provider,
        resource_type=resource_type,
        role=role,
        order_index=order,
        description=description,
        official_unofficial="official",
        lesson_id=lesson.id,
        section=start_boundary,
        lecture=None,
        video_id=video_id,
        verification_status=verification_status,
        estimated_minutes=estimated_minutes,
        estimate_confidence=estimate_confidence,
        estimate_method="CONTENT_FIT_RESEARCH",
        exactness=exactness,
        boundary_type=boundary_type,
        start_boundary=start_boundary,
        end_boundary=end_boundary,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        learner_visible=learner_visible,
        visibility_class=visibility_class,
        notes=note,
    )
    return row, created


def _demote(row: CurriculumResource, reason: str) -> None:
    _update_metadata(
        row,
        role="REFERENCE",
        notes=reason,
        learner_visible=True,
        visibility_class="LEARNER",
    )


def _backup_db() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"dev.db.pre_content_fit_repairs_{stamp}.bak"
    shutil.copy2(DB_PATH, backup)
    return backup


def _match(row: CurriculumResource, *needles: str) -> bool:
    hay = " ".join(
        str(getattr(row, k, "") or "") for k in ("slug", "title", "url", "description")
    ).lower()
    return any(n.lower() in hay for n in needles)


def apply_content_fit_repairs(db: Session, commit: bool = True) -> dict[str, Any]:
    backup = _backup_db()
    created = 0
    updated = 0
    demoted = 0
    missing: list[str] = []
    changes: list[dict[str, Any]] = []

    def record(topic: str, action: str, resource: str, detail: str) -> None:
        changes.append({"topic": topic, "action": action, "resource": resource, "detail": detail})

    # 1) ML Ridge/Lasso: pedagogical primary becomes the dedicated Vizuara intuition lesson;
    #    scikit-learn remains a reference implementation.
    topic = "ml-ridge-lasso"
    rows = _resources_for_topic(db, topic)
    old_primary = next((r for r in rows if r.slug == "ml-ridge-lasso-primary"), None)
    if old_primary is None:
        missing.append(topic)
    else:
        if str(old_primary.role).upper() == "PRIMARY":
            old_primary.role = "REFERENCE"
            _set(old_primary, "notes", "Reference implementation/API; Vizuara is the teaching primary.")
            demoted += 1
            record(topic, "DEMOTE", old_primary.slug, "scikit-learn remains implementation/reference")
        row, was_created = _ensure_resource(
            db,
            topic_slug=topic,
            slug="ml-ridge-lasso-vizuara-primary",
            title="Vizuara — Ridge Regression fundamentals and intuition",
            url="https://www.youtube.com/watch?v=-2Dbj1IzZm4",
            provider="Vizuara",
            resource_type="youtube_video",
            role="PRIMARY",
            order=0,
            description="PRIMARY teaching: L2 regularization, Ridge intuition, overfitting control, validation, and implementation intuition.",
            estimated_minutes=37,
            estimate_confidence="HIGH",
            exactness="EXACT",
            verification_status="NEEDS_REVIEW",
            boundary_type="VIDEO_TIMESTAMP",
            start_timestamp="00:00",
            end_timestamp="37:15",
            video_id="-2Dbj1IzZm4",
            note="Content-fit research selection; re-verify live before promoting to VERIFIED_COVERAGE.",
        )
        created += int(was_created)
        updated += int(not was_created)
        record(topic, "PRIMARY", row.slug if row else "missing", "Vizuara Ridge Regression 00:00-37:15")

    # 2) AI Engineering observability/security: separate observability from security.
    topic = "ai-eng-observability-security"
    rows = _resources_for_topic(db, topic)
    old = next((r for r in rows if r.slug == "ai-eng-observability-security-primary"), None)
    if old is None:
        missing.append(topic)
    else:
        old_url = str(old.url or "")
        if "owasp.org/www-project-top-10-for-large-language-model-applications" in old_url:
            # Preserve OWASP as a reference resource.
            ref_slug = "ai-eng-observability-security-owasp-reference"
            ref, was_created = _ensure_resource(
                db,
                topic_slug=topic,
                slug=ref_slug,
                title="OWASP Top 10 for LLM Applications",
                url=old_url,
                provider="OWASP",
                resource_type="documentation",
                role="REFERENCE",
                order=10,
                description="Reference: LLM security risks and mitigations, especially prompt injection and related application threats.",
                estimated_minutes=20,
                estimate_confidence="MEDIUM",
                exactness="EXACT",
                verification_status="NEEDS_REVIEW",
                boundary_type="FULL_SINGLE_PAGE",
                note="Preserved from former observability/security PRIMARY; now security reference.",
            )
            created += int(was_created)
            updated += int(not was_created)
            old.role = "REFERENCE"
            _set(old, "notes", "Demoted: security reference only; does not serve as the primary observability lesson.")
            demoted += 1
            record(topic, "DEMOTE", old.slug, "OWASP retained as security reference")
        row, was_created = _ensure_resource(
            db,
            topic_slug=topic,
            slug="ai-eng-observability-security-primary",
            title="Microsoft Learn — Observability for Generative AI and agentic AI systems",
            url="https://learn.microsoft.com/en-us/security/zero-trust/sfi/observability-ai-systems",
            provider="Microsoft Learn",
            resource_type="documentation",
            role="PRIMARY",
            order=0,
            description="PRIMARY: AI-native logs, metrics, traces, tool-call telemetry, latency/cost signals, evaluation, behavioral baselines, monitoring, and security/abuse visibility.",
            estimated_minutes=20,
            estimate_confidence="MEDIUM",
            exactness="EXACT",
            verification_status="NEEDS_REVIEW",
            boundary_type="FULL_SINGLE_PAGE",
            note="Content-fit research selection. Live page explicitly covers AI-native logs/metrics/traces, monitoring, evaluation, and security/abuse telemetry.",
        )
        created += int(was_created)
        updated += int(not was_created)
        record(topic, "PRIMARY", row.slug if row else "missing", "Microsoft Learn observability page")

    # 3) Backend JSON APIs: MDN is the teaching primary; JSON.org stays reference.
    topic = "be-json"
    rows = _resources_for_topic(db, topic)
    old = next((r for r in rows if r.slug == "be-json-primary"), None)
    if old is None:
        missing.append(topic)
    else:
        old_url = str(old.url or "")
        if "json.org" in old_url:
            ref_slug = "be-json-json-org-reference"
            ref, was_created = _ensure_resource(
                db,
                topic_slug=topic,
                slug=ref_slug,
                title="JSON.org — JSON specification",
                url=old_url,
                provider="JSON.org",
                resource_type="documentation",
                role="REFERENCE",
                order=10,
                description="Reference: JSON syntax/specification.",
                estimated_minutes=8,
                estimate_confidence="MEDIUM",
                exactness="EXACT",
                verification_status="NEEDS_REVIEW",
                boundary_type="FULL_SINGLE_PAGE",
                note="Preserved as specification reference; not the primary API-learning resource.",
            )
            created += int(was_created)
            updated += int(not was_created)
            old.role = "REFERENCE"
            _set(old, "notes", "Demoted: JSON format/specification reference; MDN better matches JSON API usage objective.")
            demoted += 1
            record(topic, "DEMOTE", old.slug, "JSON.org retained as spec reference")
        row, was_created = _ensure_resource(
            db,
            topic_slug=topic,
            slug="be-json-primary",
            title="MDN — Working with JSON",
            url="https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/JSON",
            provider="MDN",
            resource_type="documentation",
            role="PRIMARY",
            order=0,
            description="PRIMARY: JSON structure, serialization/deserialization, JSON.parse/stringify, array/object access, and JSON in web APIs.",
            estimated_minutes=15,
            estimate_confidence="MEDIUM",
            exactness="EXACT",
            verification_status="NEEDS_REVIEW",
            boundary_type="FULL_SINGLE_PAGE",
            note="Content-fit research selection; MDN directly teaches JSON serialization and web API usage.",
        )
        created += int(was_created)
        updated += int(not was_created)
        record(topic, "PRIMARY", row.slug if row else "missing", "MDN Working with JSON")

    # 4) Correct wrong Vizuara duplicate PRIMARYs by repurposing them as accurate supplements.
    #    D2L/CS231n/HF remain the core primaries for these exact mechanics.
    transformations = [
        (
            "dl-convolution-op",
            ("qFMpq46hEjE", "dense layer"),
            {
                "slug": "dl-convolution-vizuara-supplement",
                "title": "Vizuara — Filters in 1D and Convolution Operation",
                "url": "https://www.youtube.com/watch?v=P6d8NbTlEpU",
                "provider": "Vizuara",
                "video_id": "P6d8NbTlEpU",
                "start_timestamp": "00:00",
                "end_timestamp": "16:15",
                "description": "SUPPLEMENT: intuitive filters and convolution walkthrough from scratch.",
                "estimated_minutes": 17,
            },
        ),
        (
            "dl-pooling",
            ("rtFpq608aEo", "broadcasting"),
            {
                "slug": "dl-pooling-vizuara-supplement",
                "title": "Vizuara — What is Max Pooling in CNNs?",
                "url": "https://www.youtube.com/watch?v=nc46EtxUvD4",
                "provider": "Vizuara",
                "video_id": "nc46EtxUvD4",
                "start_timestamp": "00:00",
                "end_timestamp": "09:42",
                "description": "SUPPLEMENT: intuitive max-pooling explanation and animation.",
                "estimated_minutes": 10,
            },
        ),
        (
            "genai-tokenization-llm",
            ("7CNElr-TAQw", "positional encoding"),
            {
                "slug": "genai-tokenization-position-encoding-reference",
                "title": "Vizuara — Positional Encoding",
                "url": "https://www.youtube.com/watch?v=7CNElr-TAQw",
                "provider": "Vizuara",
                "video_id": "7CNElr-TAQw",
                "start_timestamp": "00:00",
                "end_timestamp": "13:57",
                "description": "REFERENCE: positional encoding; relevant only after tokenization fundamentals.",
                "estimated_minutes": 14,
            },
        ),
        (
            "cv-convolution-in-cv",
            ("9KvngtchNww", "u-net evolution"),
            {
                "slug": "cv-convolution-vizuara-supplement",
                "title": "Vizuara — Filters in 1D and Convolution Operation",
                "url": "https://www.youtube.com/watch?v=P6d8NbTlEpU",
                "provider": "Vizuara",
                "video_id": "P6d8NbTlEpU",
                "start_timestamp": "00:00",
                "end_timestamp": "16:15",
                "description": "SUPPLEMENT: visual/conceptual convolution refresher before image-grid mechanics.",
                "estimated_minutes": 17,
            },
        ),
        (
            "cv-what-is-an-image",
            ("Tu11SMJGGIA", "computer vision from scratch"),
            {
                "slug": "cv-what-is-an-image-vizuara-reference",
                "title": "Vizuara — Computer Vision from Scratch Intro",
                "url": "https://www.youtube.com/watch?v=Tu11SMJGGIA",
                "provider": "Vizuara",
                "video_id": "Tu11SMJGGIA",
                "start_timestamp": "00:00",
                "end_timestamp": "28:43",
                "description": "REFERENCE: beginner CV orientation; the scikit-image page remains the exact image-representation primary.",
                "estimated_minutes": 29,
            },
        ),
    ]

    for topic, needles, target in transformations:
        candidates = _resources_for_topic(db, topic)
        matched = [r for r in candidates if _match(r, *needles)]
        for row in matched:
            # If it is already the desired resource/role, make it idempotently consistent.
            if row.role == "PRIMARY":
                row.role = "SUPPLEMENT" if "reference" not in target["slug"] else "REFERENCE"
                demoted += 1
                record(topic, "DEMOTE", row.slug, "Wrong concept was mapped as PRIMARY")
            # Reuse the same row to avoid duplicates.
            _update_metadata(
                row,
                slug=target["slug"],
                title=target["title"],
                url=target["url"],
                provider=target["provider"],
                resource_type="youtube_video",
                role="SUPPLEMENT" if "reference" not in target["slug"] else "REFERENCE",
                section=None,
                lecture=None,
                video_id=target["video_id"],
                verification_status="NEEDS_REVIEW",
                estimated_minutes=target["estimated_minutes"],
                estimate_confidence="HIGH",
                estimate_method="VIDEO_DURATION",
                exactness="EXACT",
                boundary_type="VIDEO_TIMESTAMP",
                start_timestamp=target["start_timestamp"],
                end_timestamp=target["end_timestamp"],
                learner_visible=True,
                visibility_class="LEARNER",
                description=target["description"],
                notes="Repurposed from an incorrectly mapped learning resource; exact concept role corrected.",
            )
            updated += 1
            record(topic, "REPURPOSE", row.slug, target["title"])

    # 5) GenAI language-model and next-token mappings have misleading provider/title metadata.
    for topic_slug, slug, title, url, provider, section in [
        (
            "genai-what-is-lm",
            "genai-what-is-lm-primary",
            "D2L.ai — Language Modeling",
            "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_recurrent-neural-networks/language-model.md",
            "D2L.ai",
            "Language modeling overview",
        ),
        (
            "genai-next-token-prediction",
            "genai-next-token-prediction-primary",
            "D2L.ai — Language Modeling: Pretraining Objective",
            "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_recurrent-neural-networks/language-model.md",
            "D2L.ai",
            "Pretraining objective",
        ),
    ]:
        row = next((r for r in _resources_for_topic(db, topic_slug) if r.slug == slug), None)
        if row:
            _update_metadata(
                row,
                title=title,
                url=url,
                provider=provider,
                section=section,
                notes="Corrected provider/title metadata: URL is D2L.ai, not Hugging Face."
            )
            updated += 1
            record(topic_slug, "METADATA", slug, "Corrected provider/title to match URL")

    # 6) CV image representation provider was mislabeled as Stanford CS231n while URL is scikit-image.
    row = next((r for r in _resources_for_topic(db, "cv-what-is-an-image") if r.slug == "cv-what-is-an-image-primary"), None)
    if row and "scikit-image.org" in str(row.url):
        _update_metadata(
            row,
            title="scikit-image — Image data representation with NumPy",
            provider="scikit-image",
            notes="Corrected provider/title metadata to match scikit-image URL."
        )
        updated += 1
        record("cv-what-is-an-image", "METADATA", row.slug, "Provider corrected from Stanford CS231n to scikit-image")

    if commit:
        db.commit()

    report = {
        "backup": str(backup),
        "created": created,
        "updated": updated,
        "demoted_or_repurposed": demoted,
        "missing_topics": sorted(set(missing)),
        "changes": changes,
    }
    report_path = ROOT / "reports" / "content_fit_repair_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    from app.db.session import SessionLocal

    session = SessionLocal()
    try:
        print(json.dumps(apply_content_fit_repairs(session), indent=2))
    finally:
        session.close()
