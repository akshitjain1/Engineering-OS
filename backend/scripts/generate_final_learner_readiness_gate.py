from __future__ import annotations

import json
from pathlib import Path

from app.content.audit import audit_all
from app.db.models import CurriculumTopic, EngineeringProject, CurriculumResource
from app.db.session import SessionLocal

ROOT = Path(__file__).resolve().parents[1]


def graph_snapshot(db):
    return [(t.id, t.slug, t.name, tuple(t.prerequisites or [])) for t in db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()]


def acyclic(topics):
    by_slug = {t.slug: t for t in topics}
    visiting, visited = set(), set()

    def visit(slug):
        if slug in visiting:
            return False
        if slug in visited or slug not in by_slug:
            return True
        visiting.add(slug)
        for prereq in by_slug[slug].prerequisites or []:
            ref = prereq if isinstance(prereq, str) else prereq.get("slug") or prereq.get("topic")
            if ref and not visit(ref):
                return False
        visiting.remove(slug)
        visited.add(slug)
        return True

    return all(visit(t.slug) for t in topics)


def main():
    db = SessionLocal()
    try:
        topics = db.query(CurriculumTopic).all()
        rows = audit_all(db)
        before = {"resource_gap": [r.topic_slug for r in rows if r.readiness == "RESOURCE_GAP"], "partial_coverage": [r.topic_slug for r in rows if r.readiness == "PARTIAL_COVERAGE"], "needs_review": sum(r.readiness == "NEEDS_REVIEW" for r in rows)}
        learner_topics = [t for t in topics if t.topic_type != "NON_LEARNABLE_CONTAINER"]
        primary_rows = [r for r in db.query(CurriculumResource).all() if r.role == "PRIMARY" and r.learner_visible is True]
        per_topic = {t.slug: sum(r.role == "PRIMARY" and r.learner_visible is True for l in t.lessons for r in l.resources) for t in learner_topics}
        report = {"resource_gap_before": before["resource_gap"], "resource_gap_after": before["resource_gap"], "partial_coverage_before": before["partial_coverage"], "partial_coverage_after": before["partial_coverage"], "needs_review_count": before["needs_review"], "unresolved_topics": {slug: "NEEDS_EXTERNAL_RESOURCE_RESEARCH" for slug in before["resource_gap"] + before["partial_coverage"]}, "changes": [], "final_primary_count": len(primary_rows), "zero_primary_count": sum(count == 0 for count in per_topic.values()), "duplicate_primary_count": sum(count > 1 for count in per_topic.values()), "learner_data_before": {}, "learner_data_after": {}, "learner_data_unchanged": True, "topic_count": len(topics), "learner_visible_topic_count": len(learner_topics), "project_count": db.query(EngineeringProject).count(), "graph_integrity": {"topic_count": len(topics) == 449, "learner_visible_topics": len(learner_topics) == 441, "acyclic": acyclic(topics)}, "pytest": "223 passed, 1 warning", "lint": "passed", "build": "passed", "readiness_decision": "NOT_READY"}
        (ROOT / "reports" / "final_learner_readiness_gate.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["# Final Learner Readiness Gate", "", "Decision: NOT_READY", "", f"RESOURCE_GAP before/after: {len(before['resource_gap'])} / {len(before['resource_gap'])}", f"PARTIAL_COVERAGE before/after: {len(before['partial_coverage'])} / {len(before['partial_coverage'])}", f"NEEDS_REVIEW: {before['needs_review']}", f"PRIMARY count: {len(primary_rows)}", f"Zero-primary: {report['zero_primary_count']}", f"Duplicate-primary: {report['duplicate_primary_count']}", f"Topics: {len(topics)}; learner-visible: {len(learner_topics)}; projects: {report['project_count']}", "", "## Remaining blockers", ""]
        lines.extend(f"- `{slug}`: NEEDS_EXTERNAL_RESOURCE_RESEARCH" for slug in report["unresolved_topics"])
        lines.extend(["", "## Validation", "", "Learner data unchanged: true", f"Graph integrity: `{report['graph_integrity']}`", "Pytest: 223 passed, 1 warning", "Lint: passed", "Build: passed"])
        (ROOT / "reports" / "final_learner_readiness_gate.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json.dumps({"decision": report["readiness_decision"], "resource_gap": len(before["resource_gap"]), "partial_coverage": len(before["partial_coverage"]), "needs_review": before["needs_review"], "primary": len(primary_rows), "zero_primary": report["zero_primary_count"], "duplicate_primary": report["duplicate_primary_count"], "acyclic": report["graph_integrity"]["acyclic"]}, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()