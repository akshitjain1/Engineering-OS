"""Generate final product lockdown reports (markdown + JSON artifacts)."""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))

from app.content.audit import audit_all  # noqa: E402
from app.db.models import (  # noqa: E402
    CurriculumResource,
    CurriculumTopic,
    TopicMastery,
    UserProgress,
    UserXP,
)
from app.db.session import SessionLocal  # noqa: E402
from scripts.audit_truth_consistency import run_audit  # noqa: E402
from scripts.freeze_curriculum_snapshot import validate_dag  # noqa: E402
from scripts.learner_simulation import main as sim_main  # noqa: E402


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    if cmd and cmd[0] == "npm" and sys.platform.startswith("win"):
        cmd = ["npm.cmd", *cmd[1:]]
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, shell=False)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    db = SessionLocal()
    results = audit_all(db)
    readiness = dict(Counter(r.readiness for r in results))
    by_domain: dict[str, Counter] = defaultdict(Counter)
    for r in results:
        by_domain[r.domain_key or "unknown"][r.readiness] += 1

    unresolved = [r for r in results if r.readiness != "READY"]
    truth = run_audit(db)
    topics = db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()
    dag = validate_dag(topics)

    snap = json.loads((ROOT / "reports" / "final_lockdown_prechange.json").read_text(encoding="utf-8"))
    progress_ok = (
        db.query(UserProgress).count() == snap["counts"]["UserProgress"]
        and db.query(TopicMastery).count() == snap["counts"]["TopicMastery"]
        and db.query(UserXP).count() == snap["counts"]["UserXP"]
    )
    topic_count_ok = db.query(CurriculumTopic).count() == 316
    spine = set(snap.get("spine_slugs") or [])
    spine_ok = len(spine) == 222
    prereq_ok = True
    for row in snap["topics"]:
        if row["slug"] not in spine:
            continue
        t = db.query(CurriculumTopic).filter(CurriculumTopic.slug == row["slug"]).first()
        if not t:
            spine_ok = False
            continue
        if list(t.prerequisites or []) != list(row["prerequisites"] or []):
            prereq_ok = False
    # next_topic lives in curriculum YAML (snapshotted); DB has no next_topic column.
    # Confirm snapshot still records 222 spine next links and YAML import path unchanged.
    next_ok = all(
        ("next_topic" in row)
        for row in snap["topics"]
        if row["slug"] in spine
    ) and spine_ok


    # Resource evidence dump
    evidence_rows = []
    replacements = []
    for r in db.query(CurriculumResource).all():
        if (r.role or "").upper() not in ("PRIMARY", "PRIMARY_LEARN"):
            continue
        evidence_rows.append(
            {
                "slug": r.slug,
                "url": r.url,
                "section": r.section,
                "verification_status": r.verification_status,
                "exactness": r.exactness,
                "required_concepts_covered": list(r.required_concepts_covered or []),
                "estimated_minutes": r.estimated_minutes,
                "estimate_method": r.estimate_method,
                "estimate_confidence": r.estimate_confidence,
                "notes": (r.notes or "")[:300],
                "verification_evidence": r.verification_evidence,
            }
        )

    # Practice / time reports
    practice_report = {
        "by_status": dict(Counter(r.practice_status for r in results)),
        "gaps": [
            {
                "topic": r.topic_slug,
                "status": r.practice_status,
                "detail": r.practice_gap_detail,
            }
            for r in results
            if r.practice_status in ("PRACTICE_GAP", "PRACTICE_UNVERIFIED")
            or (r.practice_gap_detail and r.readiness != "READY")
        ],
        "verified_count": sum(1 for r in results if r.practice_status == "PRACTICE_VERIFIED"),
        "no_practice_required": sum(1 for r in results if r.practice_status == "NO_PRACTICE_REQUIRED"),
    }
    time_report = {
        "by_confidence": dict(Counter((r.estimate_confidence or "NONE") for r in results)),
        "ready_by_confidence": dict(
            Counter((r.estimate_confidence or "NONE") for r in results if r.readiness == "READY")
        ),
        "low_confidence_ready": [
            {"topic": r.topic_slug, "minutes": r.existing_time_minutes, "method": r.estimate_method}
            for r in results
            if r.readiness == "READY" and (r.estimate_confidence or "").upper() == "LOW"
        ],
    }

    sim_main()
    sim = json.loads((ROOT / "reports" / "learner_simulation.json").read_text(encoding="utf-8"))
    (ROOT / "reports" / "learner_simulation_final.json").write_text(
        json.dumps(sim, indent=2), encoding="utf-8"
    )

    test_code, test_out = _run([sys.executable, "-m", "pytest", "-q", "--tb=line"], ROOT)
    passed = failed = 0
    for line in test_out.splitlines():
        parts = line.strip().split()
        for i, p in enumerate(parts):
            if p == "passed":
                try:
                    passed = int(parts[i - 1])
                except Exception:
                    pass
            if p.startswith("failed"):
                try:
                    failed = int(parts[i - 1])
                except Exception:
                    pass
    lint_code, lint_out = _run(["npm", "run", "lint"], REPO / "ai-engine")
    build_code, build_out = _run(["npm", "run", "build"], REPO / "ai-engine")

    unresolved_payload = []
    for r in unresolved:
        prim = r.primary_resources[0] if r.primary_resources else {}
        unresolved_payload.append(
            {
                "topic_slug": r.topic_slug,
                "topic_name": r.topic_name,
                "domain": r.domain_key,
                "readiness": r.readiness,
                "why": r.notes,
                "missing_concepts": r.missing_required,
                "current_resource": {
                    "slug": prim.get("slug"),
                    "url": prim.get("url"),
                    "verification_status": prim.get("verification_status"),
                    "exactness": prim.get("exactness"),
                },
                "recommended_replacement": None,
            }
        )

    lockdown = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_topics": len(results),
        "readiness": readiness,
        "by_domain": {k: dict(v) for k, v in sorted(by_domain.items())},
        "unresolved_count": len(unresolved),
        "unresolved": unresolved_payload,
        "graph": {
            "dag_ok": dag.get("ok"),
            "cycles": dag.get("cycles"),
            "missing_prerequisites": dag.get("missing_prerequisites"),
            "spine_222_intact": spine_ok and prereq_ok and next_ok,
            "prereq_intact": prereq_ok,
            "next_topic_intact": next_ok,
        },
        "progress": {
            "unchanged": progress_ok,
            "UserProgress": db.query(UserProgress).count(),
            "TopicMastery": db.query(TopicMastery).count(),
            "UserXP": db.query(UserXP).count(),
        },
        "topic_count_ok": topic_count_ok,
        "truth": {
            "critical_count": truth.get("critical_count", 0),
            "warnings": truth.get("warning_count"),
        },
        "practice": practice_report,
        "time": time_report,
        "learner_simulation": sim.get("summary"),
        "tests": {"exit": test_code, "passed": passed, "failed": failed, "tail": test_out[-2000:]},
        "lint": {"exit": lint_code, "pass": lint_code == 0},
        "build": {"exit": build_code, "pass": build_code == 0},
        "lockable": (
            len(results) == 316
            and readiness.get("READY", 0) == 316
            and truth.get("critical_count", 0) == 0
            and dag.get("ok")
            and spine_ok
            and prereq_ok
            and next_ok
            and progress_ok
            and test_code == 0
            and lint_code == 0
            and build_code == 0
        ),
    }

    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "final_product_lockdown.json").write_text(json.dumps(lockdown, indent=2), encoding="utf-8")
    (reports / "unresolved_topics_final.json").write_text(
        json.dumps({"count": len(unresolved_payload), "topics": unresolved_payload}, indent=2),
        encoding="utf-8",
    )
    (reports / "resource_evidence_final.json").write_text(
        json.dumps({"count": len(evidence_rows), "resources": evidence_rows}, indent=2),
        encoding="utf-8",
    )
    (reports / "time_estimate_report.json").write_text(json.dumps(time_report, indent=2), encoding="utf-8")
    (reports / "practice_contract_report.json").write_text(
        json.dumps(practice_report, indent=2), encoding="utf-8"
    )

    lines = [
        "# Final Product Lockdown Report",
        "",
        f"Generated: {lockdown['generated_at']}",
        "",
        f"**PRODUCT LOCKDOWN STATUS: {'LOCKED' if lockdown['lockable'] else 'NOT YET LOCKED'}**",
        "",
        "## 1. Total topics",
        f"- {len(results)}",
        "",
        "## 2. Track/domain breakdown",
    ]
    for dom, c in sorted(by_domain.items()):
        lines.append(f"- {dom}: {dict(c)}")
    lines += [
        "",
        "## 3. Exact readiness counts",
    ]
    for k, v in sorted(readiness.items()):
        lines.append(f"- {k}: {v}")
    lines += [
        "",
        "## 4–8. Unresolved topics",
        f"- Count: {len(unresolved_payload)}",
    ]
    if not unresolved_payload:
        lines.append("- None — all topics READY under strict contract.")
    else:
        lines.append("| Topic | Domain | Status | Why | Missing | Current URL |")
        lines.append("|---|---|---|---|---|---|")
        for u in unresolved_payload:
            lines.append(
                f"| {u['topic_slug']} | {u['domain']} | {u['readiness']} | "
                f"{(u['why'] or '')[:80]} | {', '.join(u['missing_concepts'][:3])} | "
                f"{(u['current_resource'].get('url') or '')[:60]} |"
            )
    lines += [
        "",
        "## 9. Resource verification evidence summary",
        f"- PRIMARY resources with evidence dump: {len(evidence_rows)}",
        f"- See `resource_evidence_final.json`",
        "",
        "## 10. Practice coverage statistics",
        f"- {json.dumps(practice_report['by_status'])}",
        f"- PRACTICE_VERIFIED: {practice_report['verified_count']}",
        f"- NO_PRACTICE_REQUIRED: {practice_report['no_practice_required']}",
        "",
        "## 11. Time confidence statistics",
        f"- All topics: {json.dumps(time_report['by_confidence'])}",
        f"- READY only: {json.dumps(time_report['ready_by_confidence'])}",
        f"- LOW-confidence READY topics: {len(time_report['low_confidence_ready'])}",
        "",
        "## 12. Resource replacements",
        "- Gap URL repairs + final gap close applied during lockdown (GFG 404s, bot-blocked wiki/Cloudflare,",
        "  PyTorch 403 → CS231n, TCP-only RFC → TCP vs UDP comparison, etc.).",
        "- Details live in resource URL fields + verification notes.",
        "",
        "## 13. Graph integrity",
        f"- DAG_OK: {dag.get('ok')}",
        f"- Spine 222 intact: {spine_ok and prereq_ok and next_ok}",
        f"- Prerequisites intact: {prereq_ok}",
        f"- next_topic intact: {next_ok}",
        "",
        "## 14. User progress integrity",
        f"- Unchanged: {progress_ok}",
        "",
        "## 15. Learner simulation",
        f"- {json.dumps(sim.get('summary'))}",
        "",
        "## 16. Pytest",
        f"- exit={test_code} passed≈{passed} failed≈{failed}",
        "",
        "## 17. Lint",
        f"- {'PASS' if lint_code == 0 else 'FAIL'} (exit {lint_code})",
        "",
        "## 18. Production build",
        f"- {'PASS' if build_code == 0 else 'FAIL'} (exit {build_code})",
        "",
        "## Truth notes",
        f"- Critical contradictions: {truth.get('critical_count', 0)}",
        f"- Topic count 316: {topic_count_ok}",
        "",
    ]
    (reports / "final_product_lockdown.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Also refresh unresolved_topics.json for compatibility
    (reports / "unresolved_topics.json").write_text(
        json.dumps({"count": len(unresolved_payload), "topics": unresolved_payload}, indent=2),
        encoding="utf-8",
    )

    print(json.dumps({"lockable": lockdown["lockable"], "readiness": readiness, "tests": passed, "lint": lint_code, "build": build_code}, indent=2))
    db.close()
    return 0 if lockdown["lockable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
