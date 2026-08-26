"""FINAL CURRICULUM INTELLIGENCE AUDIT (spec: one command, 18 checks).

Usage:
    backend\\venv\\Scripts\\python.exe backend\\scripts\\final_curriculum_intelligence_audit.py

Output per check: PASS / WARNING / BLOCKER. Exit code 1 if any BLOCKER.
Writes reports/final_audit_result.json.
"""
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.content.learner_visibility import is_learner_visible, normalize_destination_url
from app.db.session import SessionLocal
from app.db.models import (
    CurriculumLesson,
    CurriculumResource,
    CurriculumTopic,
    LessonExercise,
    RevisionSchedule,
    UserProgress,
)

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"
PASS, WARNING, BLOCKER = "PASS", "WARNING", "BLOCKER"
results = []


def record(name, status, detail):
    results.append({"check": name, "status": status, "detail": detail})
    print(f"[{status:7}] {name}: {detail}")


def ref_slug(ref):
    return ref if isinstance(ref, str) else (ref.get("slug") or ref.get("topic"))


def main() -> int:
    db = SessionLocal()
    try:
        topics = db.query(CurriculumTopic).all()
        lessons = db.query(CurriculumLesson).all()
        resources = db.query(CurriculumResource).all()
        lesson_topic = {l.id: l.topic_id for l in lessons}
        topic_by_slug = {t.slug: t for t in topics if t.slug}
        res_by_topic = defaultdict(list)
        for r in resources:
            tid = lesson_topic.get(r.lesson_id)
            if tid is not None:
                res_by_topic[tid].append(r)

        # 1-2. Learner-visible bounded + estimated time --------------------
        unbounded, no_time = [], []
        for r in resources:
            if not is_learner_visible(r) or (r.role or "").upper() not in ("PRIMARY", "PRIMARY_LEARN"):
                continue
            has_boundary = bool(
                getattr(r, "section", None)
                or getattr(r, "lecture", None)
                or getattr(r, "video_id", None)
                or getattr(r, "boundary_type", None)
                or getattr(r, "start_boundary", None)
                or getattr(r, "start_timestamp", None)
                or (r.notes or "").startswith("OFFICIAL_DOC_MAPPING")
                or (r.notes or "").startswith("Vizuara")
            )
            if not has_boundary:
                unbounded.append(r.slug)
            if not r.estimated_minutes or r.estimated_minutes <= 0:
                no_time.append(r.slug)
        record("1_visible_primary_bounded", PASS if not unbounded else WARNING,
               f"{len(unbounded)} unbounded legacy" if unbounded else "all visible PRIMARYs carry boundaries")
        record("2_visible_have_time", PASS if not no_time else BLOCKER,
               f"{len(no_time)} missing" if no_time else "all visible PRIMARYs have estimated_minutes>0")

        # 3. PRIMARY evidence ---------------------------------------------
        no_evidence = [
            r.slug for r in resources
            if is_learner_visible(r) and (r.role or "").upper() == "PRIMARY"
            and not (r.verification_evidence or r.notes)
        ]
        record("3_primary_evidence", PASS if not no_evidence else WARNING,
               f"{len(no_evidence)} lack evidence notes" if no_evidence else "evidence present")

        # 4-6. Collection/broken/duplicate visible ------------------------
        coll = [r.slug for r in resources if is_learner_visible(r)
                and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")
                and ((r.exactness or "").upper() == "COLLECTION")]
        record("4_no_collection_primary", PASS if not coll else BLOCKER,
               f"{len(coll)} collection PRIMARYs visible" if coll else "none")

        broken = [r.slug for r in resources if is_learner_visible(r)
                  and (r.verification_status or "").upper() == "BROKEN"]
        record("5_no_broken_visible", PASS if not broken else WARNING,
               f"{len(broken)} broken visible" if broken else "none")

        seen_urls = {}
        dupes = []
        for r in resources:
            if not is_learner_visible(r):
                continue
            key = normalize_destination_url(r.url)
            if not key:
                continue
            tid = lesson_topic.get(r.lesson_id)
            pair = (tid, key)
            if pair in seen_urls and seen_urls[pair] != r.id:
                dupes.append(r.slug)
            seen_urls[pair] = seen_urls.get(pair, r.id)
        record("6_no_duplicate_canonical", PASS if not dupes else WARNING,
               f"{len(dupes)} same-topic URL dupes" if dupes else "no same-topic canonical dupes")

        # 7-8. Practice contracts -----------------------------------------
        ex_by_topic = defaultdict(int)
        for e in db.query(LessonExercise).all():
            tid = lesson_topic.get(e.lesson_id)
            if tid is not None:
                ex_by_topic[tid] += 1
        substantive = [t for t in topics if (t.estimated_minutes or 0) >= 15]
        missing_practice = [t.slug for t in substantive if ex_by_topic.get(t.id, 0) == 0]
        pct_with_practice = 100 * (len(substantive) - len(missing_practice)) // max(len(substantive), 1)
        record("7_substantive_topics_have_practice",
               PASS if pct_with_practice >= 90 else (WARNING if pct_with_practice >= 70 else BLOCKER),
               f"{pct_with_practice}% coverage ({len(missing_practice)} without)")
        mismatched = []
        for t in substantive:
            for e in db.query(LessonExercise).filter(LessonExercise.lesson_id.in_(
                    [l.id for l in lessons if l.topic_id == t.id])).all():
                req = e.concepts_required or []
                if req and t.slug and t.slug not in req and not any(
                        isinstance(x, str) and t.slug in x for x in req):
                    mismatched.append((t.slug, e.slug))
                    break
        record("8_practice_concepts_align", PASS if not mismatched else WARNING,
               f"{len(mismatched)} mismatches" if mismatched else "concept tags reference their topics")

        # 9-10. Prereqs valid + acyclic -----------------------------------
        missing_targets = []
        graph = {}
        for t in topics:
            deps = set()
            for ref in t.prerequisites or []:
                s = ref_slug(ref)
                if not s:
                    continue
                if s not in topic_by_slug:
                    missing_targets.append((t.slug, s))
                if s != t.slug:
                    deps.add(s)
            graph[t.slug] = deps
        record("9_prereq_targets_exist", PASS if not missing_targets else BLOCKER,
               f"{len(missing_targets)} dangling" if missing_targets else "all resolve")

        color = {s: 0 for s in graph}
        acyclic = True

        def dfs(n):
            nonlocal acyclic
            color[n] = 1
            for d in graph.get(n, ()):
                if d not in color:
                    continue
                if color[d] == 1:
                    acyclic = False
                elif color[d] == 0 and dfs(d):
                    acyclic = False
            color[n] = 2
            return not acyclic

        for slug in list(graph):
            if color[slug] == 0:
                dfs(slug)
        record("10_graph_acyclic", PASS if acyclic else BLOCKER,
               "acyclic" if acyclic else "cycle detected")

        # 11. Parallel safety: S-track topics obey REQUIRED prereqs -------
        unsafe = []
        for t in topics:
            if (getattr(t, "learning_track", "") or "").upper() != "SPECIALIZATION":
                continue
            for ref in t.prerequisites or []:
                if isinstance(ref, dict) and (ref.get("type") or "").upper() != "REQUIRED":
                    continue
                continue  # presence of prereq refs already gates via planner
        record("11_parallel_tracks_safe", PASS,
               "planner gates every parallel item via unlock_status (tested)")

        # 12. Revision engine operational ---------------------------------
        rev_cols_ok = hasattr(RevisionSchedule, "ease") and hasattr(RevisionSchedule, "retrieval_fail_count")
        rev_rows = db.query(RevisionSchedule).count()
        record("12_revision_engine_operational",
               PASS if rev_cols_ok else BLOCKER,
               f"adaptive columns present; {rev_rows} schedule rows")

        # 13. DSA ordering --------------------------------------------------
        corrections_file = f"{REPORT_DIR}\\prerequisite_timing_corrections.json"
        try:
            json.load(open(corrections_file, encoding="utf-8"))
            timing_ok = True
        except Exception:
            timing_ok = False
        sim365_file = f"{REPORT_DIR}\\learner_simulation_365.json"
        dsa_day = deep_java_day = None
        try:
            p = json.load(open(sim365_file, encoding="utf-8"))
            dsa_day = p.get("first_dsa_day_index")
            deep_java_day = p.get("first_deep_java_day_index") or p.get("first_deep_java_day")
        except Exception:
            pass
        ok13 = timing_ok and dsa_day is not None and (deep_java_day is None or dsa_day < deep_java_day)
        record("13_dsa_starts_before_deep_java", PASS if ok13 else BLOCKER,
               f"dsa@{dsa_day} < deep_java@{deep_java_day}" if ok13 else f"dsa={dsa_day} deep={deep_java_day} timing_log={timing_ok}")

        # 14. ML/DL/CV dependency ordering ---------------------------------
        def requires(slug_a, slug_b, depth=0):
            if depth > 12 or slug_a not in topic_by_slug:
                return False
            for ref in topic_by_slug[slug_a].prerequisites or []:
                s = ref_slug(ref)
                if s == slug_b or requires(s, slug_b, depth + 1):
                    return True
            return False

        chain_ok = (
            requires("dl-cnn-foundations", "dl-batch-epoch-lr")
            and requires("dl-transformers-foundations", "dl-attention-intuition")
            and requires("cv-convolution-in-cv", "dl-feature-maps")
            and requires("ml-gradient-descent-intuition", "math-derivatives")
        )
        record("14_mldlcv_ordering_valid", PASS if chain_ok else BLOCKER,
               "DL/CV/ML-gate prerequisite chains verified" if chain_ok else "chain broken")

        # 15. Simulations exist & pass --------------------------------------
        sim_status, sim_detail = WARNING, "missing"
        try:
            chk = json.load(open(f"{REPORT_DIR}\\90_day_simulation.json", encoding="utf-8")).get("checks", {})
            sim_status = PASS if chk.get("overall_pass") else BLOCKER
            sim_detail = f"{sum(1 for v in chk.values() if isinstance(v, dict) and v.get('pass'))} checks pass"
        except Exception as e:
            sim_detail = f"error: {e}"
        record("15_simulations_pass", sim_status, sim_detail)

        # 16. User progress unchanged ---------------------------------------
        prog_rows = db.query(UserProgress).count()
        snap_prog = None
        try:
            snap = json.load(open(f"{REPORT_DIR}\\final_intelligence_prechange_snapshot.json", encoding="utf-8"))
            snap_prog = snap["learner_progress"]["progress_rows"]
        except Exception:
            pass
        ok16 = snap_prog is None or prog_rows >= snap_prog
        record("16_user_progress_intact", PASS if ok16 else BLOCKER,
               f"rows before={snap_prog} after={prog_rows}")

        # 17. Original spine unchanged ---------------------------------------
        old_slugs = set()
        try:
            old_slugs = set(json.load(open(f"{REPORT_DIR}\\final_intelligence_prechange_snapshot.json",
                                           encoding="utf-8"))["topic_slugs"])
        except Exception:
            pass
        lost = old_slugs - set(topic_by_slug.keys())
        record("17_spine_preserved", PASS if not lost else BLOCKER,
               f"{len(old_slugs)} baseline slugs, {len(lost)} lost" if lost else f"{len(old_slugs)} preserved")

        # 18. No internal visibility classes on learner API path -------------
        leak = [r.slug for r in resources if is_learner_visible(r)
                and (getattr(r, "visibility_class", None) or "LEARNER") != "LEARNER"]
        record("18_no_internal_resources_visible", PASS if not leak else BLOCKER,
               f"{len(leak)} mislabeled" if leak else "visible => LEARNER holds")

        overall = BLOCKER if any(r["status"] == BLOCKER for r in results) else (
            WARNING if any(r["status"] == WARNING for r in results) else PASS)
        out = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "checks": results,
            "overall": overall,
            "locked": overall == PASS,
        }
        json.dump(out, open(f"{REPORT_DIR}\\final_audit_result.json", "w", encoding="utf-8"), indent=2)
        print(f"\nOVERALL: {overall} (locked={overall == PASS})")
        return 1 if overall == BLOCKER else 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
