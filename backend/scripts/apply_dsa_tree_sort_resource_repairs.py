from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from app.content.dsa_tree_sort_resource_repairs import TARGETS, apply_dsa_tree_sort_repairs
from app.db.models import DiagnosticAnswer, DiagnosticSession, LearningActivity, MasteryEvidence, RevisionSchedule, TopicMastery, UserProgress, UserXP, XpEvent
from app.db.session import SessionLocal

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "dev.db"
LEARNER_TABLES = (UserProgress, TopicMastery, MasteryEvidence, UserXP, XpEvent, RevisionSchedule, DiagnosticSession, DiagnosticAnswer, LearningActivity)


def counts(db):
    return {model.__tablename__: db.query(model).count() for model in LEARNER_TABLES}


def main() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"dev.db.pre_dsa_tree_sort_resource_repairs_{timestamp}.bak"
    shutil.copy2(DB_PATH, backup)
    if not backup.exists() or backup.stat().st_size <= 0:
        raise RuntimeError("Database backup was not created or is empty")
    db = SessionLocal()
    try:
        before = counts(db)
        result = apply_dsa_tree_sort_repairs(db)
        after = counts(db)
        report = {"backup": str(backup), "backup_size": backup.stat().st_size, "learner_data_before": before, "learner_data_after": after, "learner_data_unchanged": before == after, **result}
        (ROOT / "reports" / "dsa_tree_sort_resource_repairs.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["# DSA Tree and Sorting Resource Repairs", "", f"Backup: `{backup}` ({backup.stat().st_size} bytes)", "", f"Topics updated: {result['updated']}", "", "| Topic | Old PRIMARY | New PRIMARY | Final URL | Final boundary |", "|---|---|---|---|---|"]
        for item in result["changed"]:
            old = item["old_primary"]
            new = item["new_primary"]
            lines.append(f"| `{item['topic_slug']}` | `{old['title']}` ({old['url']}) | `{new['title']}` | {new['url']} | {new['boundary']} |")
        lines.extend(["", "## Learner-data counts", "", f"Before: `{json.dumps(before, sort_keys=True)}`", "", f"After: `{json.dumps(after, sort_keys=True)}`", "", f"Unchanged: `{before == after}`"])
        (ROOT / "reports" / "dsa_tree_sort_resource_repairs.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json.dumps({"backup": str(backup), "backup_size": backup.stat().st_size, "topics_updated": result["updated"], "learner_data_unchanged": before == after}, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()