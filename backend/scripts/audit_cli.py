"""CLI for audit + infrastructure demo. Audit-only, no DB writes except additive columns."""
from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text

from app.content.audit import audit_demo_topics, audit_all
from app.content.verification import ensure_verification_columns
from app.db.session import SessionLocal, engine


def main():
    import argparse

    p = argparse.ArgumentParser(description="Engineering OS audit CLI")
    p.add_argument("--demo", action="store_true", help="demo 10 topics")
    p.add_argument("--all", action="store_true", help="audit all 222 topics (json)")
    p.add_argument("--ensure-columns", action="store_true", help="ensure additive columns exist")
    p.add_argument("--json", type=str, help="write json to file")
    args = p.parse_args()

    if args.ensure_columns:
        cols = ensure_verification_columns(engine)
        print(f"ensure_verification_columns: {cols}")

    db = SessionLocal()
    try:
        if args.demo:
            results = audit_demo_topics(db)
            # pretty table
            print(f"\n{'SLUG':<28} {'READINESS':<18} {'MISSING':<30} {'EXIST min':<9} {'CALC min':<9} VERIFICATION")
            print("-" * 120)
            for r in results:
                missing = ",".join(r.missing_required) if r.missing_required else "-"
                print(f"{r.topic_slug:<28} {r.readiness:<18} {missing:<30} {str(r.existing_time_minutes):<9} {str(r.calculated_time_minutes):<9} {r.verification_status}/{r.exactness}")
                if r.notes:
                    print(f"  notes: {r.notes}")
            if args.json:
                with open(args.json, "w", encoding="utf-8") as f:
                    json.dump([r.__dict__ for r in results], f, indent=2, default=str)
                print(f"\nwrote {args.json}")
        elif args.all:
            results = audit_all(db)
            counts = {}
            for r in results:
                counts[r.readiness] = counts.get(r.readiness, 0) + 1
            print(f"audited {len(results)} topics")
            for k, v in sorted(counts.items()):
                print(f"  {k}: {v}")
            if args.json:
                with open(args.json, "w", encoding="utf-8") as f:
                    json.dump([r.__dict__ for r in results], f, indent=2, default=str)
                print(f"wrote {args.json}")
        else:
            p.print_help()
    finally:
        db.close()


if __name__ == "__main__":
    main()
