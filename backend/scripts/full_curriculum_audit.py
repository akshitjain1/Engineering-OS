#!/usr/bin/env python3
"""Full curriculum audit — truthful readiness report.

Usage (from backend/):
  python scripts/full_curriculum_audit.py
  python scripts/full_curriculum_audit.py --json reports/audit.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.content.audit import audit_all  # noqa: E402
from app.content.domain0_repair import apply_domain0_repairs, snapshot_counts  # noqa: E402
from app.content.source_delivery import apply_source_delivery  # noqa: E402
from app.db.migrate import ensure_optional_columns  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.db.models import Base, CurriculumTopic  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair-domain0", action="store_true", help="Apply Domain 0 repairs first")
    parser.add_argument("--json", type=str, default="", help="Write JSON report path")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    ensure_optional_columns(engine)

    db = SessionLocal()
    try:
        before = snapshot_counts(db)
        if args.repair_domain0:
            apply_source_delivery(db)
            repair = apply_domain0_repairs(db)
            db.commit()
            print("DOMAIN0_REPAIR", repair)
        after = snapshot_counts(db)
        print("SNAPSHOT_BEFORE", before)
        print("SNAPSHOT_AFTER", after)
        print(
            "PROGRESS_UNCHANGED",
            before["UserProgress"] == after["UserProgress"]
            and before["TopicMastery"] == after["TopicMastery"]
            and before["UserXP"] == after["UserXP"],
        )

        results = audit_all(db)
        readiness = Counter(r.readiness for r in results)
        tracks = Counter()
        depths = Counter()
        for t in db.query(CurriculumTopic).all():
            tracks[t.learning_track or "CORE"] += 1
            depths[t.depth_target or "WORKING_KNOWLEDGE"] += 1

        domain0 = [r for r in results if (r.topic_slug or "").startswith("cf-")]
        java = [r for r in results if (r.topic_slug or "").startswith("java-")]
        dsa = [r for r in results if (r.topic_slug or "").startswith("dsa-")]

        def bucket(rows):
            return dict(Counter(r.readiness for r in rows))

        report = {
            "total_topics": len(results),
            "readiness": dict(readiness),
            "tracks": dict(tracks),
            "depths": dict(depths),
            "domain0": {"count": len(domain0), "readiness": bucket(domain0)},
            "java": {"count": len(java), "readiness": bucket(java)},
            "dsa": {"count": len(dsa), "readiness": bucket(dsa)},
            "broken_primary_urls": [
                {
                    "topic": r.topic_slug,
                    "resource": p.get("slug"),
                    "url": p.get("url"),
                }
                for r in results
                for p in r.primary_resources
                if (p.get("verification_status") or "").upper() == "BROKEN"
            ],
            "resource_gap_topics": [r.topic_slug for r in results if r.readiness == "RESOURCE_GAP"][:50],
            "ready_topics_sample": [r.topic_slug for r in results if r.readiness == "READY"][:30],
            "notes": "READY requires inspected resource-specific coverage filling required concepts; URL alone is never enough.",
        }

        print("\n=== FULL CURRICULUM AUDIT ===")
        print(f"TOTAL TOPICS: {report['total_topics']}")
        for k, v in sorted(readiness.items()):
            print(f"  {k}: {v}")
        print("\nTRACKS:", dict(tracks))
        print("DEPTHS:", dict(depths))
        print("\nDOMAIN 0:", report["domain0"])
        print("JAVA:", report["java"])
        print("DSA:", report["dsa"])
        print(f"BROKEN PRIMARY URLs: {len(report['broken_primary_urls'])}")

        if args.json:
            out = Path(args.json)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print("Wrote", out)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
