from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from app.content.batch3_mit_shell_boundary_correction import CORRECTIONS, apply_boundary_corrections
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic, DiagnosticAnswer, DiagnosticSession, LearningActivity, MasteryEvidence, RevisionSchedule, TopicMastery, UserProgress, UserXP, XpEvent
from app.db.session import SessionLocal

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "dev.db"
LEARNER_TABLES = (UserProgress, TopicMastery, MasteryEvidence, UserXP, XpEvent, RevisionSchedule, DiagnosticSession, DiagnosticAnswer, LearningActivity)


def counts(db):
    return {model.__tablename__: db.query(model).count() for model in LEARNER_TABLES}


def graph(db):
    topics = db.query(CurriculumTopic).order_by(CurriculumTopic.id).all()
    return [(t.id, t.slug, t.name, tuple(t.prerequisites or [])) for t in topics]


def main() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"dev.db.pre_batch3_mit_shell_boundary_correction_{timestamp}.bak"
    shutil.copy2(DB_PATH, backup)
    if not backup.exists() or backup.stat().st_size <= 0:
        raise RuntimeError("Database backup was not created or is empty")
    db = SessionLocal()
    try:
        before_counts, before_graph = counts(db), graph(db)
        result = apply_boundary_corrections(db)
        after_counts, after_graph = counts(db), graph(db)
        report = {"backup": str(backup), "backup_size": backup.stat().st_size, "learner_data_before": before_counts, "learner_data_after": after_counts, "learner_data_unchanged": before_counts == after_counts, "curriculum_graph_unchanged": before_graph == after_graph, **result}
        (ROOT / "reports" / "batch3_mit_shell_boundary_correction.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"backup": str(backup), "backup_size": backup.stat().st_size, "topics_processed": result["processed"], "learner_data_unchanged": before_counts == after_counts, "curriculum_graph_unchanged": before_graph == after_graph}, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()