"""Reconcile mastery evidence onto current-evidence semantics.

Usage (from the backend directory):
    python scripts/reconcile_mastery.py --dry-run   # report only, no writes
    python scripts/reconcile_mastery.py --apply     # rebuild registers + mastery rows

Dry-run prints {topic, old score, new score, reason}. Apply never resets XP,
user progress, streaks, or curriculum data.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.migrate import ensure_optional_columns  # noqa: E402
from app.db.models import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.learning.reconcile import apply_reconciliation, plan_reconciliation  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="report planned changes only")
    group.add_argument("--apply", action="store_true", help="apply the reconciliation")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    ensure_optional_columns(engine)
    db = SessionLocal()
    try:
        report = plan_reconciliation(db)
        print(f"reconciliation plan: {len(report)} topic(s) change")
        for item in report:
            old = f"{item['old_score'] if item['old_score'] is not None else '—'} ({item['old_status']})"
            new = f"{item['new_score'] if item['new_score'] is not None else '—'} ({item['new_status']})"
            print(f"  {item['topic_name']:<42} {old:>14} -> {new:>14}  {'; '.join(item['reasons'])}")
        if args.apply and report:
            result = apply_reconciliation(db)
            db.commit()
            print(f"applied: {result['applied']} topic(s) rebuilt")
        else:
            print("no changes written (dry run)")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())