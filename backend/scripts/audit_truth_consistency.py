"""Truth consistency audit — detect READY contradictions without mutating data.

Writes:
  reports/truth_consistency_audit.json
  reports/truth_consistency_audit.md
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.content.audit import audit_all, audit_topic  # noqa: E402
from app.content.verification import (  # noqa: E402
    EXACTNESS_COLLECTION,
    READINESS_READY,
    VERIFICATION_BROKEN,
    VERIFICATION_NEEDS_REVIEW,
    VERIFICATION_PARTIAL_COVERAGE,
    VERIFICATION_VERIFIED_COVERAGE,
)
from app.db.models import CurriculumTopic  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402


def _finding(severity, topic, resource_slug, current, expected, reason, repair):
    return {
        "severity": severity,
        "topic_slug": topic.topic_slug if hasattr(topic, "topic_slug") else topic.get("slug"),
        "topic_name": topic.topic_name if hasattr(topic, "topic_name") else topic.get("name"),
        "resource_slug": resource_slug,
        "current_state": current,
        "expected_state": expected,
        "exact_reason": reason,
        "recommended_repair": repair,
    }


def run_audit(db) -> dict:
    findings = []
    results = audit_all(db)
    for a in results:
        # A/B/C/D/Q READY contradictions
        if a.readiness == READINESS_READY:
            if a.missing_required:
                findings.append(
                    _finding(
                        "CRITICAL",
                        a,
                        None,
                        f"READY missing={a.missing_required}",
                        "RESOURCE_GAP or PARTIAL",
                        "READY topic has missing required concepts",
                        "Recompute readiness; do not mark READY until union covers all concepts",
                    )
                )
            for p in a.primary_resources:
                st = (p.get("verification_status") or "").upper()
                if st == VERIFICATION_PARTIAL_COVERAGE:
                    findings.append(
                        _finding(
                            "CRITICAL",
                            a,
                            p.get("slug"),
                            f"READY + primary {st}",
                            "PARTIAL_COVERAGE topic or upgrade resource to VERIFIED_COVERAGE",
                            "READY topic has PARTIAL_COVERAGE primary",
                            "Upgrade resource status if claims verified, else demote topic",
                        )
                    )
                if st in (VERIFICATION_NEEDS_REVIEW, "NEEDS_REVIEW", "VERIFIED", "TRUSTED"):
                    findings.append(
                        _finding(
                            "CRITICAL",
                            a,
                            p.get("slug"),
                            f"READY + primary {st}",
                            "NEEDS_REVIEW topic",
                            "READY topic has non-content-verified primary",
                            "Demote topic readiness",
                        )
                    )
                if st in (VERIFICATION_BROKEN, "BROKEN"):
                    findings.append(
                        _finding(
                            "CRITICAL",
                            a,
                            p.get("slug"),
                            "READY + BROKEN primary",
                            "BROKEN",
                            "READY topic has BROKEN primary",
                            "Replace URL or demote topic",
                        )
                    )
                if (p.get("exactness") or "").upper() == EXACTNESS_COLLECTION and not (
                    p.get("section") or p.get("lecture")
                ):
                    findings.append(
                        _finding(
                            "HIGH",
                            a,
                            p.get("slug"),
                            "READY + COLLECTION without nav",
                            "RESOURCE_GAP",
                            "Collection used as focused lesson",
                            "Add section/timestamp or replace with exact page",
                        )
                    )

        # E coverage_complete illusion via empty missing but empty required
        if a.readiness == READINESS_READY and not a.required_concepts:
            findings.append(
                _finding(
                    "CRITICAL",
                    a,
                    None,
                    "READY with empty concept contract",
                    "NEEDS_REVIEW",
                    "Empty required concepts cannot be READY",
                    "Add concept contract or mark AWARENESS_ONLY",
                )
            )

        # H/I practice
        if a.practice_status == "PRACTICE_VERIFIED":
            for pi in a.practice_items:
                if not pi.destination_type or not pi.quantity:
                    findings.append(
                        _finding(
                            "HIGH",
                            a,
                            None,
                            "PRACTICE_VERIFIED without destination/quantity",
                            "PRACTICE_UNVERIFIED",
                            "Practice marked verified with incomplete contract",
                            "Add destination_type and quantity",
                        )
                    )

        # J time
        if a.readiness == READINESS_READY and not a.existing_time_minutes and not any(
            p.get("estimated_minutes") for p in a.primary_resources
        ):
            findings.append(
                _finding(
                    "HIGH",
                    a,
                    None,
                    "READY without time estimate",
                    "TIME_UNVERIFIED",
                    "Missing time estimate",
                    "Add estimated_minutes",
                )
            )

        # L mechanical copy heuristic: covered == required exactly and no evidence note
        for p in a.primary_resources:
            cov = list(p.get("required_concepts_covered") or [])
            if cov and set(cov) == set(a.required_concepts) and len(cov) > 2:
                # Flag for review if notes lack inspection marker — not auto-fail
                notes = (p.get("notes") or "").lower()
                if "inspection" not in notes and "manifest" not in notes and "domain0" not in notes:
                    findings.append(
                        _finding(
                            "MEDIUM",
                            a,
                            p.get("slug"),
                            "coverage equals topic required exactly",
                            "resource-specific evidence",
                            "Possible mechanical copy of topic requirements into resource coverage",
                            "Confirm evidence snippets per concept",
                        )
                    )

    critical = sum(1 for f in findings if f["severity"] == "CRITICAL")
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "topic_count": len(results),
        "finding_count": len(findings),
        "critical_count": critical,
        "readiness": {k: sum(1 for r in results if r.readiness == k) for k in sorted({r.readiness for r in results})},
        "findings": findings,
    }


def main() -> None:
    db = SessionLocal()
    report = run_audit(db)
    out_j = ROOT / "reports" / "truth_consistency_audit.json"
    out_m = ROOT / "reports" / "truth_consistency_audit.md"
    out_j.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Truth Consistency Audit",
        "",
        f"Generated: {report['created_at']}",
        f"Topics: {report['topic_count']}",
        f"Findings: {report['finding_count']} (critical={report['critical_count']})",
        "",
        "## Readiness",
        "",
    ]
    for k, v in report["readiness"].items():
        lines.append(f"- {k}: {v}")
    lines += ["", "## Findings", ""]
    for f in report["findings"]:
        lines.append(f"### [{f['severity']}] {f['topic_slug']} — {f['exact_reason']}")
        lines.append(f"- Resource: {f['resource_slug']}")
        lines.append(f"- Current: {f['current_state']}")
        lines.append(f"- Expected: {f['expected_state']}")
        lines.append(f"- Repair: {f['recommended_repair']}")
        lines.append("")
    out_m.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_j}")
    print(f"Wrote {out_m}")
    print("critical", report["critical_count"], "total", report["finding_count"])
    print("readiness", report["readiness"])
    db.close()
    sys.exit(1 if report["critical_count"] else 0)


if __name__ == "__main__":
    main()
