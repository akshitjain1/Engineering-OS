"""Build unresolved topics report after lockdown classification."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.content.audit import audit_all  # noqa: E402
from app.content.verification import READINESS_READY  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402


def main() -> Path:
    db = SessionLocal()
    unresolved = []
    for a in audit_all(db):
        if a.readiness == READINESS_READY:
            continue
        primary = (a.primary_resources or [{}])[0]
        unresolved.append(
            {
                "slug": a.topic_slug,
                "name": a.topic_name,
                "domain": a.domain_key,
                "status": a.readiness,
                "missing_concepts": a.missing_required,
                "why_unresolved": a.notes,
                "best_attempted_resource": primary.get("url"),
                "resource_slug": primary.get("slug"),
                "resource_status": primary.get("verification_status"),
                "exactness": primary.get("exactness"),
                "section": primary.get("section"),
                "recommended_future_action": (
                    "Replace collection/hub with exact official page and store per-concept evidence"
                    if (primary.get("exactness") or "") == "COLLECTION"
                    else "Perform human content inspection; store resource-specific evidence snippets; then re-audit"
                ),
            }
        )
    out = ROOT / "reports" / "unresolved_topics.json"
    out.write_text(
        json.dumps(
            {"count": len(unresolved), "topics": unresolved},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {out} count={len(unresolved)}")
    db.close()
    return out


if __name__ == "__main__":
    main()
