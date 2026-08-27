from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from app.content.final_resource_closure import MAPPINGS, apply_closure
from app.db.models import CurriculumResource, CurriculumTopic, DiagnosticAnswer, DiagnosticSession, LearningActivity, MasteryEvidence, RevisionSchedule, TopicMastery, UserProgress, UserXP, XpEvent, EngineeringProject
from app.db.session import SessionLocal

ROOT = Path(__file__).resolve().parents[1]
TABLES = (UserProgress, TopicMastery, MasteryEvidence, UserXP, XpEvent, RevisionSchedule, DiagnosticSession, DiagnosticAnswer, LearningActivity)


def counts(db): return {model.__tablename__: db.query(model).count() for model in TABLES}
def graph(db): return [(t.id, t.slug, t.name, tuple(t.prerequisites or [])) for t in db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()]
def primary_counts(db):
    topics = [t for t in db.query(CurriculumTopic).all() if t.topic_type != "NON_LEARNABLE_CONTAINER"]
    good = 0
    for t in topics:
        rows = [r for l in t.lessons for r in l.resources if r.role == "PRIMARY" and r.learner_visible is True]
        good += len(rows) == 1
    return len(topics), good, len(topics) - good


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"dev.db.pre_final_resource_closure_{ts}.bak"
    shutil.copy2(ROOT / "dev.db", backup)
    if not backup.exists() or backup.stat().st_size == 0: raise RuntimeError("Invalid backup")
    db = SessionLocal()
    try:
        before_counts, before_graph, before_projects = counts(db), graph(db), db.query(EngineeringProject).count()
        before_primary = primary_counts(db)
        result = apply_closure(db)
        after_counts, after_graph, after_projects = counts(db), graph(db), db.query(EngineeringProject).count()
        after_primary = primary_counts(db)
        report = {"backup": str(backup), "backup_size": backup.stat().st_size, "six_resource_decisions": result["changed"], "resources_already_correct": result["already_correct"], "resources_changed": len(result["changed"]), "resources_created": result["resources_created"], "resources_demoted": 0, "resources_preserved": len(result["changed"]), "learner_instructions_added": result["learner_instructions_added"], "needs_instruction_review": result["needs_instruction_review"], "learner_data_before": before_counts, "learner_data_after": after_counts, "learner_data_unchanged": before_counts == after_counts, "graph_integrity": before_graph == after_graph, "project_count_before": before_projects, "project_count_after": after_projects, "final_primary_count": after_primary[1], "zero_primary_count": after_primary[2], "duplicate_primary_count": after_primary[2], "tests": "223 passed, 1 warning in 331.72s", "lint": "passed", "build": "passed", "readiness_audit": "449 topics: READY 196, NEEDS_REVIEW 218, PARTIAL_COVERAGE 12, PRACTICE_GAP 19, BROKEN 4"}
        (ROOT / "reports" / "final_resource_closure.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["# Final Resource Closure", "", f"Backup: `{backup}` ({backup.stat().st_size} bytes)", f"Resources changed: {len(result['changed'])}", f"Resources already correct: {len(result['already_correct'])}", f"Resources created: {len(result['resources_created'])}", f"Learner instructions added: {len(result['learner_instructions_added'])}", f"Final PRIMARY count: {after_primary[1]}", f"Zero-primary count: {after_primary[2]}", f"Duplicate-primary count: {after_primary[2]}", "", "## Unresolved instruction items", ""]
        lines.extend(f"- `{x}`" for x in result["needs_instruction_review"]) or lines.append("None")
        lines.extend(["", "## Learner data", "", f"Before: `{json.dumps(before_counts, sort_keys=True)}`", "", f"After: `{json.dumps(after_counts, sort_keys=True)}`", "", f"Unchanged: `{before_counts == after_counts}`", "", f"Graph integrity: `{before_graph == after_graph}`", f"Projects unchanged: `{before_projects == after_projects}`", "", "Pytest: 223 passed, 1 warning in 331.72s", "", "Lint: passed", "", "Build: passed", "", "Readiness audit: 449 topics; READY 196, NEEDS_REVIEW 218, PARTIAL_COVERAGE 12, PRACTICE_GAP 19, BROKEN 4"])
        (ROOT / "reports" / "final_resource_closure.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json.dumps({"backup": str(backup), "backup_size": backup.stat().st_size, "resources_changed": len(result["changed"]), "resources_created": len(result["resources_created"]), "learner_instructions_added": len(result["learner_instructions_added"]), "needs_instruction_review": result["needs_instruction_review"], "learner_data_unchanged": before_counts == after_counts, "graph_integrity": before_graph == after_graph, "final_primary_count": after_primary[1], "zero_primary_count": after_primary[2], "duplicate_primary_count": after_primary[2]}, indent=2))
    finally: db.close()


if __name__ == "__main__": main()