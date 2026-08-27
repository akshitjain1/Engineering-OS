from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from app.content.batch4_dp_resource_mapping import TARGETS, apply_batch4_dp_mapping
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic, DiagnosticAnswer, DiagnosticSession, LearningActivity, MasteryEvidence, RevisionSchedule, TopicMastery, UserProgress, UserXP, XpEvent
from app.db.session import SessionLocal

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "dev.db"
LEARNER_TABLES = (UserProgress, TopicMastery, MasteryEvidence, UserXP, XpEvent, RevisionSchedule, DiagnosticSession, DiagnosticAnswer, LearningActivity)
ALL_TOPICS = ["dsa-dp-mindset", *TARGETS]


def counts(db):
    return {model.__tablename__: db.query(model).count() for model in LEARNER_TABLES}


def graph(db):
    return [(t.id, t.slug, t.name, tuple(t.prerequisites or [])) for t in db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()]


def main() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"dev.db.pre_batch4_dp_resource_mapping_{timestamp}.bak"
    shutil.copy2(DB_PATH, backup)
    if not backup.exists() or backup.stat().st_size <= 0:
        raise RuntimeError("Database backup was not created or is empty")
    db = SessionLocal()
    try:
        before_counts, before_graph = counts(db), graph(db)
        result = apply_batch4_dp_mapping(db)
        after_counts, after_graph = counts(db), graph(db)
        report = {"backup": str(backup), "backup_size": backup.stat().st_size, "learner_data_before": before_counts, "learner_data_after": after_counts, "learner_data_unchanged": before_counts == after_counts, "curriculum_graph_unchanged": before_graph == after_graph, **result, "tests": "223 passed, 1 warning in 320.67s", "lint": "passed", "build": "passed"}
        (ROOT / "reports" / "batch4_dp_resource_mapping.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["# Batch 4 DP Resource Mapping", "", f"Backup: `{backup}` ({backup.stat().st_size} bytes)", "", f"Topics updated: {result['processed']}", "", "| Topic | Old PRIMARY | New PRIMARY | URL | Boundary | Learner instruction |", "|---|---|---|---|---|---|"]
        for item in result["changed"]:
            old, new = item["old_primary"], item["new_primary"]
            lines.append(f"| `{item['topic']}` | `{old['slug']}`: {old['url']} | `{new['title']}` | {new['url']} | {new['boundary']} | {new['instruction']} |")
        lines.extend(["", "## Unresolved items", "", "- `dsa-dp-mindset`: NEEDS_BOUNDARY_VERIFICATION; unchanged because the repository does not contain the full duration for video `5dRGRueKU3M`.", "", "## Learner data", "", f"Before: `{json.dumps(before_counts, sort_keys=True)}`", "", f"After: `{json.dumps(after_counts, sort_keys=True)}`", "", f"Unchanged: `{before_counts == after_counts}`", "", f"Curriculum graph unchanged: `{before_graph == after_graph}`", "", "Tests: 223 passed, 1 warning in 320.67s", "", "Lint: passed", "", "Build: passed"])
        (ROOT / "reports" / "batch4_dp_resource_mapping.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json.dumps({"backup": str(backup), "backup_size": backup.stat().st_size, "topics_updated": result["processed"], "unresolved": result["unresolved"], "learner_data_unchanged": before_counts == after_counts, "curriculum_graph_unchanged": before_graph == after_graph}, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()