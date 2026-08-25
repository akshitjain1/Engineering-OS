"""Capture before-state of AI/ML domain topic readiness for closure diff."""
import json
import sys

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.content.concept_contracts import load_contract_payload
from app.content.learner_visibility import is_learner_visible
from app.db.session import SessionLocal
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"

AI_PREFIXES = ("math-", "ml-", "ds-", "dl-", "cv-", "nlp-", "genai-", "ai-eng-", "mlops-")


def main() -> None:
    db = SessionLocal()
    try:
        contracts = load_contract_payload()["contracts"]
        lessons = db.query(CurriculumLesson).all()
        lesson_topic = {l.id: l.topic_id for l in lessons}
        prim_by_topic = {}
        for r in db.query(CurriculumResource).all():
            tid = lesson_topic.get(r.lesson_id)
            if tid is None or not is_learner_visible(r):
                continue
            if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN"):
                prim_by_topic.setdefault(tid, []).append(r)

        state = {}
        for t in db.query(CurriculumTopic).all():
            s = t.slug or ""
            if not s.startswith(AI_PREFIXES):
                continue
            req = [c["slug"] for c in ((contracts.get(s) or {}).get("required") or [])]
            prim = prim_by_topic.get(t.id, [])
            res = prim[0] if prim else None
            if not req:
                sts = [(r.verification_status or "").upper() for r in prim]
                status = "READY" if any(x == "VERIFIED_COVERAGE" for x in sts) else (
                    "NEEDS_REVIEW" if any(x == "NEEDS_REVIEW" for x in sts) else (
                        "NO_PRIMARY" if not sts else "PARTIAL"))
                covered = []
            else:
                covered_set = set()
                for r in prim:
                    covered_set |= set(r.required_concepts_covered or [])
                covered = sorted(covered_set)
                if req and all(c in covered_set for c in req):
                    status = "READY"
                elif covered_set:
                    status = "PARTIAL"
                else:
                    status = "RESOURCE_GAP"
            state[s] = {
                "status": status,
                "primary_url": res.url if res else None,
                "resource_slug": res.slug if res else None,
                "concepts_required": req,
                "concepts_covered": covered,
                "missing": [c for c in req if c not in set(covered)],
            }
        json.dump({"captured_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
            "topics": state},
            open(f"{REPORT_DIR}\\pre_content_closure_state.json", "w", encoding="utf-8"),
            indent=2)
        from collections import Counter
        print(json.dumps(dict(Counter(v["status"] for v in state.values())), indent=2))
        print("topics captured:", len(state))
    finally:
        db.close()


if __name__ == "__main__":
    main()
