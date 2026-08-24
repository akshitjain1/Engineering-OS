"""Generate learner resource visibility final report + run audits."""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))

from app.content.audit import audit_all  # noqa: E402
from app.content.learner_visibility import (  # noqa: E402
    apply_learner_visibility,
    learner_facing_resources,
    restore_content_verification_statuses,
    visibility_audit_snapshot,
)
from app.content.resources import group_resources_by_role  # noqa: E402
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
from app.content.verification import ensure_verification_columns  # noqa: E402


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    if cmd and cmd[0] == "npm" and sys.platform.startswith("win"):
        cmd = ["npm.cmd", *cmd[1:]]
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, shell=False)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def count_unmapped_visible(db) -> list[dict]:
    bad = []
    for topic in db.query(CurriculumTopic).all():
        lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
        resources = [r for les in lessons for r in les.resources]
        grouped = group_resources_by_role(resources, for_learner=True)
        for role, items in grouped.items():
            for item in items:
                status = (item.get("verification_status") or "").upper()
                if not item.get("url") or status in ("", "UNRESOLVED", "UNVERIFIED"):
                    bad.append({"topic": topic.slug, "role": role, "title": item.get("title"), "status": status})
    return bad


def main() -> int:
    ensure_optional_columns(engine)
    ensure_verification_columns(engine)
    db = SessionLocal()

    readiness_before = dict(Counter(a.readiness for a in audit_all(db)))
    # Capture cf-cpu before (all resources)
    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-cpu").first()
    lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).all()
    before_all = [
        {"slug": r.slug, "role": r.role, "title": r.title, "url": r.url}
        for les in lessons
        for r in sorted(les.resources, key=lambda x: (x.order_index or 0, x.id or 0))
    ]

    restore = restore_content_verification_statuses(db)
    visibility = apply_learner_visibility(db)
    db.commit()

    readiness_after = dict(Counter(a.readiness for a in audit_all(db)))
    snap = visibility_audit_snapshot(db)
    unmapped = count_unmapped_visible(db)

    after_visible = snap["cf_cpu_learner_resources"]
    progress = {
        "UserProgress": db.query(UserProgress).count(),
        "TopicMastery": db.query(TopicMastery).count(),
        "UserXP": db.query(UserXP).count(),
        "CurriculumTopic": db.query(CurriculumTopic).count(),
    }

    test_code, test_out = _run([sys.executable, "-m", "pytest", "-q", "--tb=line"], ROOT)
    passed = 0
    for line in test_out.splitlines():
        parts = line.strip().split()
        for i, p in enumerate(parts):
            if p == "passed":
                try:
                    passed = int(parts[i - 1])
                except Exception:
                    pass
    lint_code, _ = _run(["npm", "run", "lint"], REPO / "ai-engine")
    build_code, _ = _run(["npm", "run", "build"], REPO / "ai-engine")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_resources": snap["total_resources"],
        "learner_visible_resources": snap["learner_visible"],
        "hidden_verification_resources": snap["hidden"],
        "by_visibility_class": snap["by_visibility_class"],
        "duplicates_removed_from_learner_display": visibility.get("duplicates_collapsed", 0),
        "unmapped_visible_sources_remaining": len(unmapped),
        "unmapped_visible_sources": unmapped,
        "topics_with_more_than_1_PRIMARY_learner_resource": snap[
            "topics_with_more_than_1_visible_primary"
        ],
        "topics_with_more_than_2_learner_visible_learning_resources": snap[
            "topics_with_more_than_2_visible_learning_resources"
        ],
        "cf_cpu_before": before_all,
        "cf_cpu_after_learner": after_visible,
        "readiness_before": readiness_before,
        "readiness_after": readiness_after,
        "restore": restore,
        "visibility_apply": visibility,
        "progress": progress,
        "curriculum_progress_integrity": {
            "topic_count_316": progress["CurriculumTopic"] == 316,
            "readiness_316_ready": readiness_after.get("READY") == 316,
            "unmapped_zero": len(unmapped) == 0,
        },
        "tests": {"exit": test_code, "passed": passed},
        "lint": {"exit": lint_code, "pass": lint_code == 0},
        "build": {"exit": build_code, "pass": build_code == 0},
    }

    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "learner_resource_visibility_audit.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    md = [
        "# Learner Resource Visibility Audit",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Counts",
        f"- Total resources: {report['total_resources']}",
        f"- Learner-visible: {report['learner_visible_resources']}",
        f"- Hidden (verification/internal): {report['hidden_verification_resources']}",
        f"- By class: {json.dumps(report['by_visibility_class'])}",
        f"- Duplicates collapsed from learner display: {report['duplicates_removed_from_learner_display']}",
        f"- Unmapped visible sources remaining: {report['unmapped_visible_sources_remaining']}",
        f"- Topics with >1 visible PRIMARY: {report['topics_with_more_than_1_PRIMARY_learner_resource']}",
        f"- Topics with >2 visible learning resources: {report['topics_with_more_than_2_learner_visible_learning_resources']}",
        "",
        "## cf-cpu before → after",
        "### Before (all stored resources)",
    ]
    for r in before_all:
        md.append(f"- [{r['role']}] {r['slug']}: {r['title']}")
    md += ["", "### After (learner-facing)", ""]
    for r in after_visible:
        md.append(f"- [{r['role']}] {r['slug']}: {r['title']}")
    md += [
        "",
        "## Readiness",
        f"- Before: {json.dumps(readiness_before)}",
        f"- After: {json.dumps(readiness_after)}",
        "",
        "## Integrity",
        f"- Topics=316: {progress['CurriculumTopic'] == 316}",
        f"- Progress counts: {json.dumps(progress)}",
        f"- READY 316/316: {readiness_after.get('READY') == 316}",
        "",
        "## Commands",
        f"- pytest: exit={test_code} passed≈{passed}",
        f"- lint: {'PASS' if lint_code == 0 else 'FAIL'}",
        f"- build: {'PASS' if build_code == 0 else 'FAIL'}",
        "",
    ]
    (reports / "learner_resource_visibility_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("total_resources", "learner_visible_resources", "hidden_verification_resources", "unmapped_visible_sources_remaining", "readiness_after", "tests", "lint", "build")}, indent=2))
    db.close()
    ok = (
        readiness_after.get("READY") == 316
        and len(unmapped) == 0
        and test_code == 0
        and lint_code == 0
        and build_code == 0
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
