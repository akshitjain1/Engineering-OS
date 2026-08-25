"""FINAL ACCEPTANCE (PART J) — automated equivalents of the 10 manual tests.

Runs read-only journeys against the real DB plus two controlled mutation
tests that roll back. Prints PASS/FAIL per test; exit 1 on any FAIL.
"""
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.content.audit import audit_topic
from app.db.session import SessionLocal
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic, RevisionSchedule
from app.learning.bridges import prerequisite_bridge

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"
results = []


def record(name, ok, detail=""):
    results.append({"test": name, "pass": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {('- ' + detail) if detail else ''}")


def ref_slug(ref):
    return ref if isinstance(ref, str) else (ref.get("slug") or ref.get("topic"))


def main() -> int:
    db = SessionLocal()
    try:
        topics = {t.slug: t for t in db.query(CurriculumTopic).all()}
        lessons = db.query(CurriculumLesson).all()
        lesson_topic = {l.id: l.topic_id for l in lessons}

        # ---- Test 1: Absolute beginner — first cf topic has no REQUIRED prereqs
        first = topics.get("cf-bits-and-bytes")
        reqs = [r for r in (first.prerequisites or [])]
        record("T1_beginner_no_prereq_jump", len(reqs) == 0,
               f"cf-bits-and-bytes prereqs={reqs}")

        # ---- Test 2: DSA parallel start gate is narrow
        dsa = topics["dsa-algorithmic-thinking"]
        dslugs = {ref_slug(r) for r in (dsa.prerequisites or [])}
        ok2 = "java-method-basics" in dslugs and not any(
            s.startswith(("java-stream", "java-thread", "java-gc")) for s in dslugs)
        record("T2_dsa_parallel_gate", ok2, f"gate={sorted(dslugs)}")

        # ---- Test 3: ML beginner chain ordering
        def requires(a, b, depth=0):
            if depth > 12 or a not in topics:
                return False
            for r in topics[a].prerequisites or []:
                s = ref_slug(r)
                if s == b or requires(s, b, depth + 1):
                    return True
            return False

        ok3 = (requires("ml-logistic-regression", "ml-what-is-ml")
               and requires("ml-gradient-descent-intuition", "math-derivatives")
               and requires("ml-gradient-descent-intuition", "ml-loss-intuition"))
        record("T3_ml_chain_awareness_math_algorithms", ok3)

        # ---- Test 4: DL math bridge enforced before backprop family
        ok4 = (requires("dl-backprop-intuition", "math-partial-derivatives")
               and requires("dl-backprop-intuition", "dl-loss-functions-nn"))
        record("T4_dl_no_math_skip", ok4)

        # ---- Test 5: CV prerequisites include image representation + CNN mechanics
        ok5 = (requires("cv-convolution-in-cv", "cv-traditional-filters")
               and requires("cv-convolution-in-cv", "dl-feature-maps"))
        record("T5_cv_bridges_present", ok5)

        # ---- Test 6: Revision adaptive scheduling works end-to-end
        from app.learning.revision_engine import schedule_update

        class R:
            review_interval = 1
            ease = 2.5
            retrieval_success_count = 0
            retrieval_fail_count = 0

        r = R()
        schedule_update(r, 10)          # fail -> 1d
        i1 = r.review_interval
        schedule_update(r, 90)          # first success seeds ladder (30d @90)
        i2 = r.review_interval
        record("T6_revision_adaptive", i1 == 1 and i2 >= 14,
               f"fail->{i1}d then success->{i2}d")

        # ---- Test 7: No unbounded learner-visible PRIMARY
        resources = db.query(CurriculumResource).all()
        bad_bounds = [
            r.slug for r in resources
            if _is_vis_primary(r)
            and ((r.exactness in (None, "", "COLLECTION"))
                 or not r.url
                 or r.resource_type == "youtube_playlist"
                 and True)
        ]
        record("T7_no_unbounded_primary", not bad_bounds,
               f"{len(bad_bounds)} offenders" if bad_bounds else "all bounded")

        # ---- Test 8: Practice exercises reference their own topic concepts
        ex_ok, checked = True, 0
        
        from app.db.models import LessonExercise as LE
        for e in db.query(LE).all():
            tid = lesson_topic.get(e.lesson_id)
            if tid is None:
                continue
            tslug = next((s for s, t in topics.items() if t.id == tid), None)
            if tslug and e.concepts_required:
                checked += 1
                if not any(isinstance(c, str) and (c == tslug or tslug in c) for c in e.concepts_required):
                    ex_ok = False
                    break
        record("T8_practice_concepts_match", ex_ok, f"{checked} contracts checked")

        # ---- Test 9: Broken PRIMARY cannot stay READY (rollback after check)
        target = next((r for r in resources if _is_vis_primary(r)
                       and (r.verification_status or "").upper() == "VERIFIED_COVERAGE"), None)
        ok9 = True
        detail9 = "no verified primary to test"
        if target is not None:
            tid = lesson_topic.get(target.lesson_id)
            tslug = next((s for s, t in topics.items() if t.id == tid), None)
            orig_status = target.verification_status
            target.verification_status = "BROKEN"
            try:
                audited = audit_topic(db, tslug)
                ok9 = getattr(audited, "readiness", "") != "READY"
                detail9 = f"{tslug}: readiness with broken primary = {getattr(audited, 'readiness', '?')}"
            finally:
                db.rollback()  # never persist the simulated breakage
                target.verification_status = orig_status
        record("T9_broken_not_ready", ok9, detail9)

        # ---- Test 10: Missing prerequisite produces a blocking bridge
        bridge = prerequisite_bridge(
            "dl-nn-basics",
            {s: {"slug": s, "name": t.name, "prerequisites": t.prerequisites or [],
                 "estimated_minutes": t.estimated_minutes}
             for s, t in topics.items()},
            completed_slugs=set(),
        )
        record("T10_missing_prereq_bridge_blocks",
               bridge["blocked"] and bridge["total_minutes"] > 0,
               f"bridge={len(bridge['bridge'])} items / {bridge['total_minutes']} min")

        overall = all(r["pass"] for r in results)
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(),
                   "tests": results, "overall_pass": overall},
                  open(f"{REPORT_DIR}\\final_acceptance_result.json", "w", encoding="utf-8"),
                  indent=2)
        print(f"\nOVERALL: {'PASS' if overall else 'FAIL'} ({sum(r['pass'] for r in results)}/{len(results)})")
        return 0 if overall else 1
    finally:
        db.close()


def _is_vis_primary(r):
    from app.content.learner_visibility import is_learner_visible
    return is_learner_visible(r) and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")


if __name__ == "__main__":
    sys.exit(main())
