"""List non-READY topics with primary resources and audit reasons."""
from __future__ import annotations

from app.content.audit import audit_all
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    rows = [a for a in audit_all(db) if a.readiness != "READY"]
    print("count", len(rows))
    for a in sorted(rows, key=lambda x: (x.domain_key or "", x.readiness, x.topic_slug)):
        print(f"{a.readiness:18} {a.domain_key or '-':18} {a.topic_slug}")
        print("  missing:", a.missing_required[:10])
        print("  status/exactness:", a.verification_status, a.exactness)
        print("  practice:", a.practice_status, a.practice_gap_detail)
        if a.notes:
            print("  notes:", (a.notes or "")[:200])
        for p in a.primary_resources[:3]:
            print(
                "  P",
                p.get("slug"),
                p.get("verification_status"),
                p.get("exactness"),
                "covered=",
                p.get("required_concepts_covered"),
                "url=",
                (p.get("url") or "")[:90],
            )
    db.close()


if __name__ == "__main__":
    main()
