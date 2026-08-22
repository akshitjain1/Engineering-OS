"""Final curriculum content verification pass across all topics.

Rules:
- Does not mutate topic slugs, names, prereqs, next_topic, or user progress.
- Domain 0 RESOURCE_COVERAGE_MANIFEST stays authoritative (prior content inspection).
- Other PRIMARY resources: accessibility + content inspection → independent coverage.
- Never copies topic.required into resource.covered.

Usage:
  python scripts/run_final_verification.py
  python scripts/run_final_verification.py --domain foundations
  python scripts/run_final_verification.py --limit 20
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.content.audit import audit_all, audit_topic  # noqa: E402
from app.content.concept_contracts import get_topic_concepts, load_contract_payload  # noqa: E402
from app.content.content_inspector import inspect_resource  # noqa: E402
from app.content.domain0_repair import apply_domain0_repairs  # noqa: E402
from app.content.dsa_practice import enrich_dsa_practice  # noqa: E402
from app.content.final_lock_repairs import apply_url_repairs  # noqa: E402
from app.content.promote_exact_resources import promote_exact_resources  # noqa: E402
from app.content.java_practice import enrich_java_practice  # noqa: E402
from app.content.verification import (  # noqa: E402
    RESOURCE_COVERAGE_MANIFEST,
    RESOURCE_TIME_MANIFEST,
    VERIFICATION_BROKEN,
    VERIFICATION_COLLECTION_ONLY,
    VERIFICATION_NEEDS_REVIEW,
    VERIFICATION_PARTIAL_COVERAGE,
    VERIFICATION_VERIFIED_COVERAGE,
    ensure_verification_columns,
)
from app.db.migrate import ensure_optional_columns  # noqa: E402
from app.db.models import (  # noqa: E402
    CurriculumLesson,
    CurriculumResource,
    CurriculumTopic,
    TopicMastery,
    UserProgress,
    UserXP,
)
from app.db.session import SessionLocal, engine  # noqa: E402

DOMAIN_ORDER = [
    "foundations",
    "java",
    "dsa",
    "software-engineering",
    "backend",
    "mathematics",
    "python",
    "ml",
    "data-science",
    "deep-learning",
    "nlp",
    "genai",
    "ai-engineering",
    "mlops",
    "web",
    "networking",
    "devops",
    "system-design",
]


def _progress_counts(db) -> dict:
    return {
        "UserProgress": db.query(UserProgress).count(),
        "TopicMastery": db.query(TopicMastery).count(),
        "UserXP": db.query(UserXP).count(),
        "CurriculumTopic": db.query(CurriculumTopic).count(),
    }


def _primaries_for_topic(db, topic: CurriculumTopic) -> list[CurriculumResource]:
    lessons = (
        db.query(CurriculumLesson)
        .filter(CurriculumLesson.topic_id == topic.id)
        .order_by(CurriculumLesson.order_index)
        .all()
    )
    out: list[CurriculumResource] = []
    for les in lessons:
        for r in sorted(les.resources, key=lambda x: (x.order_index or 0, x.id or 0)):
            if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN"):
                out.append(r)
    return out


def _apply_domain0_manifest_row(row: CurriculumResource) -> None:
    slug = row.slug or ""
    if slug not in RESOURCE_COVERAGE_MANIFEST:
        return
    cov = list(RESOURCE_COVERAGE_MANIFEST[slug])
    row.required_concepts_covered = cov
    if slug in RESOURCE_TIME_MANIFEST:
        mins, conf = RESOURCE_TIME_MANIFEST[slug]
        row.estimated_minutes = mins
        row.estimate_confidence = conf
        row.estimate_method = "MEASURED_MANUAL_ESTIMATE" if conf == "HIGH" else "SECTION_LENGTH_ESTIMATE"
    if cov:
        # partial vs full decided at topic level; mark partial if known partials
        partial_slugs = {
            "cf-cpu-primary",
            "cf-alu-primary",
            "cf-cache-primary",
            "cf-instruction-execution-primary",
        }
        row.verification_status = (
            VERIFICATION_PARTIAL_COVERAGE if slug in partial_slugs else VERIFICATION_VERIFIED_COVERAGE
        )
    else:
        row.verification_status = VERIFICATION_NEEDS_REVIEW
    row.last_verified_at = datetime.now(timezone.utc).isoformat()
    evidence = {
        "resource_slug": slug,
        "verified_concepts": [{"concept": c, "evidence": "DOMAIN0_MANIFEST_INSPECTION"} for c in cov],
        "inspected_at": row.last_verified_at,
        "verification_method": "CONTENT_INSPECTION",
        "source": "RESOURCE_COVERAGE_MANIFEST",
    }
    row.verification_evidence = json.dumps(evidence)


def _inspect_job(payload: dict) -> dict:
    try:
        result = inspect_resource(
            resource_slug=payload["slug"],
            url=payload["url"],
            topic_slug=payload["topic_slug"],
            title=payload.get("title") or "",
            section=payload.get("section"),
            resource_type=payload.get("resource_type"),
        )
        return {
            "ok": True,
            "resource_id": payload["resource_id"],
            "result": result,
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "resource_id": payload["resource_id"], "error": str(exc)}


def verify_domain(db, domain: str, workers: int = 8, limit: int | None = None) -> dict:
    q = db.query(CurriculumTopic).filter(CurriculumTopic.domain_key == domain)
    topics = q.order_by(CurriculumTopic.order_index, CurriculumTopic.id).all()
    if limit:
        topics = topics[:limit]

    jobs = []
    domain0_kept = 0
    for topic in topics:
        if not get_topic_concepts(topic.slug or ""):
            continue
        for r in _primaries_for_topic(db, topic):
            if (r.slug or "") in RESOURCE_COVERAGE_MANIFEST:
                _apply_domain0_manifest_row(r)
                domain0_kept += 1
                continue
            jobs.append(
                {
                    "resource_id": r.id,
                    "slug": r.slug,
                    "url": r.url,
                    "topic_slug": topic.slug,
                    "title": r.title,
                    "section": r.section,
                    "resource_type": r.resource_type,
                }
            )

    results_by_id: dict[int, object] = {}
    errors = 0
    if jobs:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futs = [pool.submit(_inspect_job, j) for j in jobs]
            for fut in as_completed(futs):
                data = fut.result()
                if not data.get("ok"):
                    errors += 1
                    continue
                results_by_id[data["resource_id"]] = data["result"]

    applied = 0
    for rid, result in results_by_id.items():
        row = db.query(CurriculumResource).filter(CurriculumResource.id == rid).first()
        if not row:
            continue
        row.required_concepts_covered = list(result.covered)
        row.verification_status = result.verification_status
        row.exactness = result.exactness
        row.estimated_minutes = result.estimated_minutes
        row.estimate_confidence = result.estimate_confidence
        row.estimate_method = result.estimate_method
        row.notes = (result.notes or "")[:500]
        row.last_verified_at = result.inspected_at
        row.verification_evidence = json.dumps(
            {
                "resource_slug": result.resource_slug,
                "verified_concepts": [
                    {"concept": e.concept, "evidence": e.evidence, "matched_terms": e.matched_terms}
                    for e in result.evidence
                ],
                "missing": result.missing,
                "inspected_at": result.inspected_at,
                "verification_method": result.verification_method,
                "http_status": result.http_status,
                "word_count": result.word_count,
            }
        )
        applied += 1

    db.flush()
    return {
        "domain": domain,
        "topics": len(topics),
        "inspected": applied,
        "domain0_manifest_kept": domain0_kept,
        "errors": errors,
    }


def write_final_reports(db) -> tuple[Path, Path]:
    results = audit_all(db)
    by_ready = Counter(r.readiness for r in results)
    by_domain: dict[str, Counter] = {}
    for r in results:
        d = r.domain_key or "none"
        by_domain.setdefault(d, Counter())[r.readiness] += 1

    topics_out = []
    for r in results:
        topics_out.append(
            {
                "slug": r.topic_slug,
                "name": r.topic_name,
                "domain": r.domain_key,
                "track": r.learning_track,
                "depth": r.depth_target,
                "learning_objective": r.learning_objective,
                "required_concepts": r.required_concepts,
                "PRIMARY": r.primary_resources,
                "combined_coverage": r.combined_coverage,
                "missing_concepts": r.missing_required,
                "verification_status": r.verification_status,
                "exactness": r.exactness,
                "practice_status": r.practice_status,
                "practice": [
                    {
                        "type": p.type,
                        "destination": p.destination,
                        "destination_type": p.destination_type,
                        "quantity": p.quantity,
                        "concepts_required": p.concepts_required,
                        "instructions": p.instructions,
                    }
                    for p in r.practice_items
                ],
                "estimated_minutes": r.calculated_time_minutes,
                "existing_time_minutes": r.existing_time_minutes,
                "estimate_method": r.estimate_method,
                "estimate_confidence": r.estimate_confidence,
                "final_readiness": r.readiness,
                "notes": r.notes,
            }
        )

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_topics": len(results),
        "scorecard": dict(by_ready),
        "by_domain": {k: dict(v) for k, v in by_domain.items()},
        "contract_count": len((load_contract_payload().get("contracts") or {})),
        "topics": topics_out,
    }
    reports = ROOT / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    jpath = reports / "final_curriculum_verification.json"
    mpath = reports / "final_curriculum_verification.md"
    jpath.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Final Curriculum Verification",
        "",
        f"Generated: {payload['created_at']}",
        "",
        "## Scorecard",
        "",
        f"- TOTAL TOPICS: {payload['total_topics']}",
    ]
    for k in sorted(by_ready.keys()):
        lines.append(f"- {k}: {by_ready[k]}")
    lines += ["", "## By domain", ""]
    for d in DOMAIN_ORDER + sorted(set(by_domain) - set(DOMAIN_ORDER)):
        if d not in by_domain:
            continue
        c = by_domain[d]
        total = sum(c.values())
        ready = c.get("READY", 0)
        lines.append(f"### {d}: {ready}/{total} READY")
        for k, v in sorted(c.items()):
            if k != "READY":
                lines.append(f"- {k}: {v}")
        lines.append("")

    lines += ["## Topic detail (failures first)", ""]
    ordered = sorted(results, key=lambda x: (0 if x.readiness == "READY" else 1, x.domain_key or "", x.topic_slug))
    for r in ordered:
        if r.readiness == "READY":
            continue
        lines.append(f"### {r.topic_slug} — {r.readiness}")
        lines.append(f"- Topic: {r.topic_name}")
        lines.append(f"- Reason: {r.notes}")
        if r.primary_resources:
            p0 = r.primary_resources[0]
            lines.append(f"- Resource: {p0.get('slug')} | {p0.get('url')}")
            lines.append(f"- Resource status: {p0.get('verification_status')} exactness={p0.get('exactness')}")
        lines.append(f"- Missing concepts: {r.missing_required}")
        lines.append(f"- Covered: {r.combined_coverage}")
        lines.append(f"- Practice status: {r.practice_status}")
        lines.append("")

    mpath.write_text("\n".join(lines), encoding="utf-8")
    return jpath, mpath


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--skip-inspect", action="store_true")
    args = parser.parse_args()

    ensure_optional_columns(engine)
    ensure_verification_columns(engine)

    db = SessionLocal()
    before = _progress_counts(db)
    print("PROGRESS_BEFORE", before)

    # Preserve Domain 0 repairs
    print("domain0_repair", apply_domain0_repairs(db))
    print("url_repairs", apply_url_repairs(db))
    print("promote_exact", promote_exact_resources(db))
    try:
        print("dsa_practice", enrich_dsa_practice(db))
    except Exception as exc:  # noqa: BLE001
        print("dsa_practice_skip", exc)
    try:
        print("java_practice", enrich_java_practice(db))
    except Exception as exc:  # noqa: BLE001
        print("java_practice_skip", exc)
    db.commit()

    domains = [args.domain] if args.domain else list(DOMAIN_ORDER)
    # include any remaining domains
    if not args.domain:
        present = {t.domain_key for t in db.query(CurriculumTopic.domain_key).distinct()}
        for d in sorted(present):
            if d and d not in domains:
                domains.append(d)

    summaries = []
    if not args.skip_inspect:
        for d in domains:
            if not d:
                continue
            print(f"=== VERIFY DOMAIN {d} ===")
            try:
                summary = verify_domain(db, d, workers=args.workers, limit=args.limit)
                summaries.append(summary)
                print(summary)
                db.commit()
            except Exception:
                db.rollback()
                traceback.print_exc()
                raise

    after = _progress_counts(db)
    print("PROGRESS_AFTER", after)
    print("PROGRESS_UNCHANGED", before == after)

    jpath, mpath = write_final_reports(db)
    print("Wrote", jpath)
    print("Wrote", mpath)

    # print scorecard
    results = audit_all(db)
    print("SCORECARD", dict(Counter(r.readiness for r in results)))
    db.close()


if __name__ == "__main__":
    main()
