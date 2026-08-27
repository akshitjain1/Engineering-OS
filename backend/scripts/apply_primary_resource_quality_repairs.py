from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from app.content.primary_resource_quality_repairs import TARGETS, apply_primary_resource_quality_repairs
from app.db.models import CurriculumResource
from app.db.session import SessionLocal

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "dev.db"


def main() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"dev.db.pre_primary_resource_quality_repairs_{timestamp}.bak"
    shutil.copy2(DB_PATH, backup)
    if not backup.exists() or backup.stat().st_size <= 0:
        raise RuntimeError("Database backup was not created or is empty")
    db = SessionLocal()
    try:
        learner_counts_before = {slug: db.query(CurriculumResource).filter(CurriculumResource.slug.like(slug + "%"), CurriculumResource.learner_visible.is_(True)).count() for slug in TARGETS}
        result = apply_primary_resource_quality_repairs(db)
        learner_counts_after = {slug: db.query(CurriculumResource).filter(CurriculumResource.slug.like(slug + "%"), CurriculumResource.learner_visible.is_(True)).count() for slug in TARGETS}
        report = {"backup": str(backup), "backup_size": backup.stat().st_size, "learner_counts_before": learner_counts_before, "learner_counts_after": learner_counts_after, **result}
        (ROOT / "reports" / "primary_resource_quality_repairs_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["# Primary Resource Quality Repairs", "", f"Backup: `{backup}` ({backup.stat().st_size} bytes)", "", f"Updated mappings: {result['updated']}", "", "| Topic | Resource |", "| --- | --- |"]
        lines.extend(f"| `{item['topic_slug']}` | `{item['resource_slug']}` |" for item in result["changed"])
        (ROOT / "reports" / "primary_resource_quality_repairs_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json.dumps({"backup": str(backup), "backup_size": backup.stat().st_size, "updated": result["updated"]}, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()