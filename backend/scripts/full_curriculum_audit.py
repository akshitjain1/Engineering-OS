"""FULL CURRICULUM AUDIT (closure pass).

Emits:
  - Domain-by-domain readiness table (stdout + report JSON section)
  - Resource boundary audit numbers
  - reports/practice_contract_report.json
  - reports/time_estimate_report.json
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.content.concept_contracts import load_contract_payload
from app.content.learner_visibility import is_learner_visible
from app.db.session import SessionLocal
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic, LessonExercise

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"

DOMAIN_PREFIXES = [
    ("cf-", "CS Foundations"), ("java-", "Java"), ("dsa-", "DSA & Algorithms"),
    ("se-", "Software Engineering"), ("db-", "Backend"), ("be-", "Backend"),
    ("math-", "Mathematics for ML"), ("ml-", "Machine Learning"), ("ds-", "Data Science"),
    ("dl-", "Deep Learning"), ("cv-", "Computer Vision"), ("nlp-", "NLP"),
    ("genai-", "Generative AI / LLMs"), ("ai-eng-", "AI Engineering / Agents"),
    ("mlops-", "MLOps"), ("sys-", "System Design"), ("net-", "Networking"),
    ("ops-", "DevOps"), ("web-", "Web"),
]


def domain_of(slug):
    s = slug or ""
    for p, d in DOMAIN_PREFIXES:
        if s.startswith(p):
            return d
    if s.startswith(("py",)):
        return "Python"
    return "Other"


def main() -> None:
    db = SessionLocal()
    try:
        topics = db.query(CurriculumTopic).all()
        lessons = db.query(CurriculumLesson).all()
        resources = db.query(CurriculumResource).all()
        lesson_topic = {l.id: l.topic_id for l in lessons}

        # topic readiness from resource statuses (union contract approximation:
        # topic READY iff all required concepts covered across visible PRIMARYs)
        contracts = load_contract_payload()["contracts"]
        # Union-coverage uses ALL PRIMARYs incl. hidden supplements
        # (original verified design; learner UI filters separately).
        prim_by_topic = defaultdict(list)
        for r in resources:
            tid = lesson_topic.get(r.lesson_id)
            if tid is None:
                continue
            if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN"):
                prim_by_topic[tid].append(r)

        def topic_readiness(t):
            req = [c["slug"] for c in ((contracts.get(t.slug) or {}).get("required") or [])]
            if not req:
                # Legacy topics without authored contracts fall back to status rollup
                sts = [(r.verification_status or "").upper() for r in prim_by_topic.get(t.id, [])]
                if not sts:
                    return "NO_PRIMARY"
                if any(s == "VERIFIED_COVERAGE" for s in sts):
                    return "READY"
                if all(s in ("BROKEN",) for s in sts):
                    return "BROKEN"
                return "NEEDS_REVIEW"
            covered = set()
            for r in prim_by_topic.get(t.id, []):
                covered |= set(r.required_concepts_covered or [])
            if all(c in covered for c in req):
                return "READY"
            if covered:
                return "PARTIAL"
            return "RESOURCE_GAP"

        rows = []
        for t in topics:
            rows.append((domain_of(t.slug), t.slug, topic_readiness(t)))

        domains = defaultdict(Counter)
        for d, _s, st in rows:
            domains[d][st] += 1

        print("\n=== DOMAIN READINESS ===")
        print(f"{'Domain':28} {'Topics':>6} {'READY':>6} {'PARTIAL':>8} {'GAP':>5} {'NR':>4} {'OTHER':>6}")
        summary = {}
        for d in sorted(domains, key=lambda k: -sum(domains[k].values())):
            c = domains[d]
            other = sum(v for k, v in c.items() if k not in ("READY", "PARTIAL", "RESOURCE_GAP", "NEEDS_REVIEW"))
            nr = c.get("NEEDS_REVIEW", 0)
            gap = c.get("RESOURCE_GAP", 0)
            print(f"{d:28} {sum(c.values()):>6} {c.get('READY',0):>6} {c.get('PARTIAL',0):>8} {gap:>5} {nr:>4} {other:>6}")
            summary[d] = dict(c)

        # Boundary audit ---------------------------------------------------
        vis_primary = [
            r for r in resources
            if is_learner_visible(r) and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")
        ]
        boundary_audit = {
            "learner_visible_resources_total": sum(1 for r in resources if is_learner_visible(r)),
            "visible_with_exactness_none": sum(1 for r in vis_primary if not r.exactness),
            "visible_with_minutes_none": sum(1 for r in vis_primary if not r.estimated_minutes),
            "entire_books_exposed": sum(
                1 for r in vis_primary
                if r.resource_type == "book" and (r.exactness or "") not in ("EXACT", "SEGMENT")
            ),
            "entire_playlists_exposed": sum(
                1 for r in vis_primary
                if r.resource_type == "youtube_playlist"
            ),
            "collection_primarys": sum(1 for r in vis_primary if (r.exactness or "") == "COLLECTION"),
        }
        print("\n=== BOUNDARY AUDIT ===")
        print(json.dumps(boundary_audit, indent=2))

        # Practice report ----------------------------------------------------
        ex_rows = db.query(LessonExercise).all()
        practice_by_topic = defaultdict(list)
        for e in ex_rows:
            tid = lesson_topic.get(e.lesson_id)
            if tid is not None:
                practice_by_topic[tid].append(e)
        substantive = [t for t in topics if (t.estimated_minutes or 0) >= 15]
        missing = [t.slug for t in substantive if t.id not in practice_by_topic]
        practice_report = {
            "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "substantive_topics": len(substantive),
            "with_contracts": len(substantive) - len(missing),
            "coverage_percent": round(100 * (len(substantive) - len(missing)) / max(len(substantive), 1)),
            "topics_missing_practice": missing[:40],
            "total_exercise_contracts": len(ex_rows),
            "by_type": dict(Counter(e.exercise_type for e in ex_rows)),
        }
        json.dump(practice_report, open(f"{REPORT_DIR}\\practice_contract_report.json", "w",
                                       encoding="utf-8"), indent=2)

        # Time estimates report ----------------------------------------------
        est_dist = Counter((r.estimate_confidence or "UNSET") for r in vis_primary)
        time_report = {
            "visible_primaries": len(vis_primary),
            "with_estimated_minutes_gt0": sum(1 for r in vis_primary if (r.estimated_minutes or 0) > 0),
            "confidence_distribution": dict(est_dist),
            "note": "UNSET confidence on legacy Domain-0 resources is treated LOW; "
                    "decomposition resources carry MEDIUM (calculated from bounded content).",
        }
        json.dump(time_report, open(f"{REPORT_DIR}\\time_estimate_report.json", "w",
                                    encoding="utf-8"), indent=2)

        json.dump({"domains": summary, "boundary_audit": boundary_audit},
                  open(f"{REPORT_DIR}\\full_curriculum_audit.json", "w", encoding="utf-8"), indent=2)
        print("\nreports written: practice_contract_report.json, time_estimate_report.json, full_curriculum_audit.json")
    finally:
        db.close()


if __name__ == "__main__":
    main()
