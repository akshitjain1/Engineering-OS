"""Run full lockdown verification V2 across remaining NEEDS_REVIEW domains.

Does not mutate topic slugs, prereqs, next_topic, or user progress.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.content.audit import audit_all  # noqa: E402
from app.content.demote_weak_verification import demote_weak_verification  # noqa: E402
from app.content.lockdown_normalize import apply_lockdown_normalization  # noqa: E402
from app.content.lockdown_verify_v2 import verify_domains  # noqa: E402
from app.content.promote_exact_resources import promote_exact_resources  # noqa: E402
from app.db.migrate import ensure_optional_columns  # noqa: E402
from app.content.verification import ensure_verification_columns  # noqa: E402
from app.db.models import TopicMastery, UserProgress, UserXP  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402

DOMAIN_ORDER = [
    "java",
    "dsa",
    "software-engineering",
    "backend",
    "mathematics",
    "ml",
    "python",
    "web",
    "networking",
    "devops",
    "data-science",
    "deep-learning",
    "genai",
    "mlops",
    "system-design",
    "nlp",
    "ai-engineering",
]


def main() -> None:
    ensure_optional_columns(engine)
    ensure_verification_columns(engine)
    db = SessionLocal()
    before = {
        "UserProgress": db.query(UserProgress).count(),
        "TopicMastery": db.query(TopicMastery).count(),
        "UserXP": db.query(UserXP).count(),
    }
    print("PROGRESS_BEFORE", before)
    print("promote", promote_exact_resources(db))
    db.commit()

    # foundations already READY — skip unless passed
    domains = DOMAIN_ORDER
    if len(sys.argv) > 1:
        domains = sys.argv[1].split(",")

    for d in domains:
        print(f"=== VERIFY {d} ===")
        summary = verify_domains(db, domains=[d], workers=12)
        print(summary)
        db.commit()
        sc = Counter(a.readiness for a in audit_all(db) if a.domain_key == d)
        print("domain_score", dict(sc))

    print("normalize", apply_lockdown_normalization(db))
    print("demote", demote_weak_verification(db))
    db.commit()

    after = {
        "UserProgress": db.query(UserProgress).count(),
        "TopicMastery": db.query(TopicMastery).count(),
        "UserXP": db.query(UserXP).count(),
    }
    print("PROGRESS_AFTER", after)
    print("PROGRESS_UNCHANGED", before == after)

    results = audit_all(db)
    score = dict(Counter(r.readiness for r in results))
    print("SCORECARD", score)
    by = {}
    for r in results:
        by.setdefault(r.domain_key or "none", Counter())[r.readiness] += 1
    for d, c in sorted(by.items()):
        print(d, dict(c))

    # evidence dump
    evidence = []
    from app.db.models import CurriculumResource

    for row in db.query(CurriculumResource).all():
        if (row.role or "").upper() not in ("PRIMARY", "PRIMARY_LEARN"):
            continue
        if not row.verification_evidence:
            continue
        try:
            data = json.loads(row.verification_evidence)
        except Exception:
            continue
        evidence.append(
            {
                "resource_slug": row.slug,
                "url": row.url,
                "verification_status": row.verification_status,
                "exactness": row.exactness,
                "covered": row.required_concepts_covered,
                "evidence": data,
            }
        )
    out = ROOT / "reports" / "resource_evidence_final.json"
    out.write_text(json.dumps({"count": len(evidence), "resources": evidence}, indent=2), encoding="utf-8")
    print("Wrote", out)
    db.close()


if __name__ == "__main__":
    main()
