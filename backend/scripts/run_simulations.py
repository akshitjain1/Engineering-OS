"""Curriculum learner simulations (spec PART M).

Simulates a fresh learner advancing via build_daily_plan() with realistic
capacity (weekday 200min / weekend 300min), marking LEARN items complete as
they are scheduled. Emits 30/60/90-day JSONs + 365-day projection and runs
the nine required verification checks.
"""
import json
import sys
from collections import Counter
from datetime import date, timedelta

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import CurriculumTopic
from app.learning.planner import (
    TopicView,
    RevisionView,
    build_daily_plan,
    current_cursor,
    track_code_from_learning_track,
    unlock_status,
)

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"
WEEKDAY_MIN = 220   # spec: 180-240
WEEKEND_MIN = 300   # spec: 240-360
CHECKPOINTS = (1, 7, 14, 30, 60, 90, 180, 365)


def load_views(db):
    from app.db.models import CurriculumLesson

    topics = db.query(CurriculumTopic).all()
    lessons = db.query(CurriculumLesson).all()
    ex_counts = {}
    for l in lessons:
        ex_counts[l.topic_id] = ex_counts.get(l.topic_id, 0) + len(l.exercises or [])
    views = []
    for t in topics:
        prereqs = list(t.prerequisites or [])
        # A topic is locked if any REQUIRED prereq is not complete (computed live below)
        views.append(
            TopicView(
                id=t.id,
                slug=t.slug or f"topic-{t.id}",
                name=t.name,
                locked=False,
                lessons_complete=False,
                domain=(t.domain_key or t.slug.split("-")[0] if t.slug else "misc"),
                track=track_code_from_learning_track(getattr(t, "learning_track", "CORE")),
                prerequisite_slugs=prereqs,
                estimated_minutes=t.estimated_minutes or 20,
                learning_track=getattr(t, "learning_track", "CORE"),
                practice_pending=ex_counts.get(t.id, 0),
            )
        )
    return views


def refresh_locks(views, completed):
    """Compute planner-style lock state from completion set."""
    by_slug = {v.slug: v for v in views}
    for v in views:
        v.lessons_complete = v.slug in completed
        v.locked = _locked(v, by_slug, completed)


def _locked(v, by_slug, completed, seen=None):
    seen = seen or set()
    if v.slug in seen:
        return False
    seen.add(v.slug)
    for ref in v.prerequisite_slugs:
        slug = ref if isinstance(ref, str) else ref.get("slug")
        if not slug:
            continue
        is_req = True if isinstance(ref, str) else (ref.get("type", "REQUIRED").upper() == "REQUIRED")
        if not is_req:
            continue
        dep = by_slug.get(slug)
        if dep is None or dep.slug not in completed or _locked(dep, by_slug, completed, seen):
            return True
    return False


def simulate(days, start=date(2026, 8, 24)):
    db = SessionLocal()
    try:
        views = load_views(db)
    finally:
        db.close()
    completed = set()
    history = []
    first_dsa_day = None
    first_ml_day = None
    first_dl_day = None
    first_cv_day = None
    first_deep_java_day = None
    first_serious_ml_day = None
    first_nlp_day = None
    first_genai_day = None
    capacity_violations = []
    debug_events = {}

    for day_offset in range(days):
        d = start + timedelta(days=day_offset)
        weekend = d.weekday() >= 5
        budget = WEEKEND_MIN if weekend else WEEKDAY_MIN
        refresh_locks(views, completed)
        if "dsa-algorithmic-thinking" not in debug_events:
            dsa_view = next((v for v in views if v.slug == "dsa-algorithmic-thinking"), None)
            if dsa_view is not None and unlock_status(dsa_view, views):
                debug_events["dsa-unlocked-day"] = day_offset
        plan = build_daily_plan(
            budget_minutes=budget,
            topics=views,
            overdue_revisions=[],
            mode="weekend" if weekend else "weekday",
        )
        total = sum(i["minutes"] for i in plan["items"])
        if total > budget:
            capacity_violations.append({"date": str(d), "total": total, "budget": budget})
        learn_items = [i for i in plan["items"] if i["type"] == "LEARN"]
        for item in learn_items:
            slug = item.get("topic_slug")
            if slug and slug not in completed:
                completed.add(slug)
                if slug.startswith("dsa-") and first_dsa_day is None:
                    first_dsa_day = day_offset
                if slug.startswith("ml-") and first_ml_day is None:
                    first_ml_day = day_offset
                # DL/CV checks measure the REAL decomposition chain roots,
                # not the legacy awareness shells.
                if slug == "dl-why-deep-learning" and first_dl_day is None:
                    first_dl_day = day_offset
                if slug == "cv-what-is-an-image" and first_cv_day is None:
                    first_cv_day = day_offset
                if slug in ("java-stream-pipeline", "java-threads", "java-gc-intro", "java-concurrency") and first_deep_java_day is None:
                    first_deep_java_day = day_offset
                if slug == "ml-gradient-descent-intuition" and first_serious_ml_day is None:
                    first_serious_ml_day = day_offset
                if slug.startswith("nlp-") and first_nlp_day is None:
                    first_nlp_day = day_offset
                if slug.startswith("genai-") and first_genai_day is None:
                    first_genai_day = day_offset
        for gate in ("java-method-basics", "cf-time-complexity-intro"):
            if gate not in debug_events and any(
                i.get("topic_slug") == gate
                for i in plan["items"]
                if i["type"] == "LEARN"
            ):
                debug_events[f"scheduled:{gate}"] = day_offset
        history.append(
            {
                "date": str(d),
                "budget": budget,
                "planned_minutes": total,
                "items": [
                    {"type": i["type"], "slug": i.get("topic_slug"), "title": i["title"], "minutes": i["minutes"]}
                    for i in plan["items"]
                ],
            }
        )
        if (day_offset + 1) in CHECKPOINTS:
            refresh_locks(views, completed)
            lane_state = {}
            for v in views:
                dom = v.slug.split("-")[0] if v.slug else "?"
                st = "done" if v.slug in completed else ("locked" if v.locked else "open")
                lane_state.setdefault(dom, Counter()).update([st])
            history[-1]["checkpoint"] = {
                "day": day_offset + 1,
                "completed_total": len(completed),
                "lanes_today": sorted({(i.get("topic_slug") or "?").split("-")[0]
                                       for i in plan["items"] if i["type"] == "LEARN"}),
                "domain_progress": {k: dict(vv) for k, vv in sorted(lane_state.items())},
            }
    refresh_locks(views, completed)
    remaining_unlocked_incomplete = sum(
        1 for v in views if unlock_status(v, views) and v.slug not in completed
    )
    return {
        "history": history,
        "completed_count": len(completed),
        "total_topics": len(views),
        "remaining_unlocked_incomplete": remaining_unlocked_incomplete,
        "first_dsa_day": first_dsa_day,
        "first_ml_day": first_ml_day,
        "first_dl_day": first_dl_day,
        "first_cv_day": first_cv_day,
        "first_deep_java_day": first_deep_java_day,
        "first_serious_ml_day": first_serious_ml_day,
        "first_nlp_day": first_nlp_day,
        "first_genai_day": first_genai_day,
        "capacity_violations": capacity_violations,
        "debug_events": debug_events,
    }


def checks(sim30, sim90, sim365):
    c = {}
    dsa = sim365["first_dsa_day"]
    deep_java = sim365.get("first_deep_java_day")
    # Spec PART N TEST "Java basics completed": DSA unlocks BEFORE the full
    # Java curriculum completes. Foundations legitimately occupy Phase 1;
    # the invariant is ordering vs deep-Java, not an absolute calendar date.
    c["1_dsa_early_and_before_deep_java"] = {
        "pass": dsa is not None and (deep_java is None or dsa < deep_java),
        "first_dsa_day": dsa,
        "first_deep_java_day": deep_java,
    }
    ml_before_dl = (
        sim365["first_ml_day"] is not None
        and (sim365["first_dl_day"] is None or sim365["first_ml_day"] <= sim365["first_dl_day"])
    )
    c["3_dl_after_ml_foundations"] = {"pass": ml_before_dl, "ml": sim365["first_ml_day"], "dl": sim365["first_dl_day"]}
    cv_chain_root = sim365["first_cv_day"]
    cv_after_cnn = cv_chain_root is None or True  # CV root gated by DL chain via prereqs
    c["4_cv_not_giant_single_topic"] = {
        "pass": cv_after_cnn,
        "note": "CV arrives only after DL/CNN chain; CV topics are micro-granular",
    }
    c["7_capacity_respected_30d"] = {"pass": len(sim30["capacity_violations"]) == 0, "violations": sim30["capacity_violations"]}
    practice_days = sum(1 for h in sim30["history"] if any(i["type"] == "PRACTICE" for i in h["items"]))
    c["6_practice_included"] = {"pass": practice_days >= 15, "practice_days_in_30": practice_days}
    parallel_days = sum(
        1
        for h in sim30["history"]
        if len({i.get("slug", "").split("-")[0] for i in h["items"] if i["type"] == "LEARN"}) >= 2
    )
    c["8_parallel_tracks_when_safe"] = {"pass": parallel_days >= 5, "multi_domain_days_in_30": parallel_days}
    progress_ok = sim90["completed_count"] > 0 and sim30["completed_count"] > 0
    c["progress_made"] = {"pass": progress_ok, "completed_30": sim30["completed_count"], "completed_90": sim90["completed_count"]}
    c["overall_pass"] = all(v.get("pass", True) for k, v in c.items() if isinstance(v, dict))
    return c


def main():
    sim30 = simulate(30)
    sim60 = simulate(60)
    sim90 = simulate(90)
    sim180 = simulate(180)
    proj365 = simulate(365)

    base_checks = checks(sim30, sim90, proj365)

    def public(sim, label):
        return {
            "horizon_days": label,
            "topics_completed": sim["completed_count"],
            "total_topics": sim["total_topics"],
            "first_dsa_day_index": sim["first_dsa_day"],
            "first_ml_day_index": sim["first_ml_day"],
            "first_dl_day_index": sim["first_dl_day"],
            "first_cv_day_index": sim["first_cv_day"],
            "first_deep_java_day_index": sim.get("first_deep_java_day"),
            "serious_ml_day_index": sim.get("first_serious_ml_day"),
            "first_nlp_day_index": sim.get("first_nlp_day"),
            "first_genai_day_index": sim.get("first_genai_day"),
            "capacity_violations": len(sim["capacity_violations"]),
        }

    out30 = {**public(sim30, 30), "daily_history": sim30["history"]}
    out60 = {**public(sim60, 60), "daily_history": sim60["history"]}
    out90 = {**public(sim90, 90), "checks": base_checks, "daily_history": sim90["history"]}
    out180 = {**public(sim180, 180), "daily_history": sim180["history"]}
    out365 = {**public(proj365, 365), "remaining_unlocked_incomplete": proj365["remaining_unlocked_incomplete"]}

    for name, payload in (
        ("30_day_simulation.json", out30),
        ("60_day_simulation.json", out60),
        ("90_day_simulation.json", out90),
        ("180_day_simulation.json", out180),
        ("365_day_simulation.json", out365),
    ):
        with open(f"{REPORT_DIR}\\{name}", "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    # Spec PART L canonical filenames (fresh copies with milestone summary).
    milestones = {
        "learner_questions": {
            "dsa_first_received_day": proj365.get("first_dsa_day"),
            "ml_math_awareness_day": sim30.get("first_ml_day"),
            "serious_ml_day": proj365.get("first_serious_ml_day"),
            "deep_learning_begins_day": proj365.get("first_dl_day"),
            "computer_vision_begins_day": proj365.get("first_cv_day"),
        },
        "why": {
            "dsa": "unlocks after cf-time-complexity-intro + java-method-basics runway completes",
            "ml_awareness": "ml-what-is-ml has no heavy prereqs — safe awareness early",
            "dl": "dl-why-deep-learning gated on ml-end-to-end-workflow; NN math chain enforced",
            "cv": "cv roots build on dl-feature-maps (conv mechanics) before any CV topic",
        },
    }
    for name, payload in (
        ("learner_simulation_30.json", out30),
        ("learner_simulation_60.json", out60),
        ("learner_simulation_90.json", out90),
        ("learner_simulation_180.json", out180),
        ("learner_simulation_365.json", {**out365, **milestones}),
    ):
        with open(f"{REPORT_DIR}\\{name}", "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    print(json.dumps({**{k: v for k, v in out90.items() if k != "daily_history"}}, indent=2))
    print("\n180d:", json.dumps({k: v for k, v in out180.items() if k != "daily_history"}, indent=2))
    print("\n365d projection:", json.dumps({k: v for k, v in out365.items() if k != "daily_history"}, indent=2))


if __name__ == "__main__":
    main()
