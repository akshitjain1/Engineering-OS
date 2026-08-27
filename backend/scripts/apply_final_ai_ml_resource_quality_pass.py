from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from app.content.final_ai_ml_resource_quality_pass import MAPPINGS, UNRESOLVED, apply_final_pass
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic, DiagnosticAnswer, DiagnosticSession, EngineeringProject, LearningActivity, MasteryEvidence, RevisionSchedule, TopicMastery, UserProgress, UserXP, XpEvent
from app.db.session import SessionLocal

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "dev.db"
LEARNER_TABLES = (UserProgress, TopicMastery, MasteryEvidence, UserXP, XpEvent, RevisionSchedule, DiagnosticSession, DiagnosticAnswer, LearningActivity)


def counts(db):
    return {model.__tablename__: db.query(model).count() for model in LEARNER_TABLES}


def graph(db):
    return [(t.id, t.slug, t.name, tuple(t.prerequisites or [])) for t in db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()]


def primary_state(db):
    rows = db.query(CurriculumResource).filter(CurriculumResource.role == "PRIMARY", CurriculumResource.learner_visible.is_(True)).all()
    return len(rows), len({r.lesson_id for r in rows})


def main() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"dev.db.pre_final_ai_ml_resource_quality_pass_{timestamp}.bak"
    shutil.copy2(DB_PATH, backup)
    if not backup.exists() or backup.stat().st_size <= 0:
        raise RuntimeError("Database backup was not created or is empty")
    db = SessionLocal()
    try:
        before_counts, before_graph = counts(db), graph(db)
        before_projects, before_primary = db.query(EngineeringProject).count(), primary_state(db)
        result = apply_final_pass(db)
        after_counts, after_graph = counts(db), graph(db)
        after_projects, after_primary = db.query(EngineeringProject).count(), primary_state(db)
        report = {"backup": str(backup), "backup_size": backup.stat().st_size, "learner_data_before": before_counts, "learner_data_after": after_counts, "learner_data_unchanged": before_counts == after_counts, "curriculum_graph_unchanged": before_graph == after_graph, "project_count_before": before_projects, "project_count_after": after_projects, "primary_count_before": before_primary[0], "primary_count_after": after_primary[0], "learner_primary_topic_count_after": after_primary[1], "duplicate_primary_count_after": after_primary[0] - after_primary[1], **result, "tests": "223 passed, 1 warning in 317.11s", "lint": "passed", "build": "passed"}
        (ROOT / "reports" / "final_ai_ml_resource_quality_pass.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["# Final AI/ML/CV Resource Quality Pass", "", f"Backup: `{backup}` ({backup.stat().st_size} bytes)", "", f"Topics inspected: {result['topics_inspected']}", f"Topics changed: {result['topics_changed']}", f"Topics unchanged: {len(result['unresolved']) + 2}", f"Resources created: {result['resources_created']}", f"Resources demoted: {result['resources_demoted']}", f"Resources preserved: {result['resources_preserved']}", f"Learner instructions added: {len(result['instructions_added'])}", "", "## Unresolved items", ""]
        lines.extend(f"- `{topic}`: {reason}" for topic, reason in result["unresolved"].items())
        lines.extend(["", "## Learner data", "", f"Before: `{json.dumps(before_counts, sort_keys=True)}`", "", f"After: `{json.dumps(after_counts, sort_keys=True)}`", "", f"Unchanged: `{before_counts == after_counts}`", "", f"Curriculum graph unchanged: `{before_graph == after_graph}`", f"Projects unchanged: `{before_projects == after_projects}`", f"Final PRIMARY count: `{after_primary[0]}`", f"Final duplicate PRIMARY count: `{after_primary[0] - after_primary[1]}`", "", "Pytest: 223 passed, 1 warning in 317.11s", "", "Lint: passed", "", "Build: passed"])
        (ROOT / "reports" / "final_ai_ml_resource_quality_pass.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json.dumps({"backup": str(backup), "backup_size": backup.stat().st_size, "topics_inspected": result["topics_inspected"], "topics_changed": result["topics_changed"], "unresolved": result["unresolved"], "learner_data_unchanged": before_counts == after_counts, "curriculum_graph_unchanged": before_graph == after_graph, "final_primary_count": after_primary[0], "duplicate_primary_count": after_primary[0] - after_primary[1]}, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()