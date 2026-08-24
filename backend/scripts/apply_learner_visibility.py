"""Apply learner visibility cleanup + restore content verification statuses.

Does not mutate curriculum topology or user progress.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.content.audit import audit_all  # noqa: E402
from app.content.learner_visibility import (  # noqa: E402
    apply_learner_visibility,
    restore_content_verification_statuses,
    visibility_audit_snapshot,
)
from app.db.migrate import ensure_optional_columns  # noqa: E402
from app.db.models import CurriculumTopic, TopicMastery, UserProgress, UserXP  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.content.verification import ensure_verification_columns  # noqa: E402


def main() -> int:
    ensure_optional_columns(engine)
    ensure_verification_columns(engine)
    db = SessionLocal()

    before_readiness = dict(Counter(a.readiness for a in audit_all(db)))
    progress_before = {
        "UserProgress": db.query(UserProgress).count(),
        "TopicMastery": db.query(TopicMastery).count(),
        "UserXP": db.query(UserXP).count(),
        "CurriculumTopic": db.query(CurriculumTopic).count(),
    }

    restore = restore_content_verification_statuses(db)
    visibility = apply_learner_visibility(db)
    db.commit()

    after_readiness = dict(Counter(a.readiness for a in audit_all(db)))
    progress_after = {
        "UserProgress": db.query(UserProgress).count(),
        "TopicMastery": db.query(TopicMastery).count(),
        "UserXP": db.query(UserXP).count(),
        "CurriculumTopic": db.query(CurriculumTopic).count(),
    }
    snap = visibility_audit_snapshot(db)

    report = {
        "restore": restore,
        "visibility_apply": visibility,
        "readiness_before": before_readiness,
        "readiness_after": after_readiness,
        "progress_before": progress_before,
        "progress_after": progress_after,
        "progress_unchanged": progress_before == progress_after,
        "topic_count_unchanged": progress_before["CurriculumTopic"] == progress_after["CurriculumTopic"] == 316,
        "snapshot": snap,
    }
    out = ROOT / "reports" / "learner_resource_visibility_audit.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2)[:4000])
    db.close()
    return 0 if after_readiness.get("READY", 0) == 316 and report["progress_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
