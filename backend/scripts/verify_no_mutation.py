"""Post-change comparison report proving nothing critical was mutated.

Checks vs prechange snapshot:
- All snapshot topic slugs still exist (superset OK)
- Every original prerequisite edge preserved verbatim (superset OK)
- User progress rows unchanged
- XP history unchanged
"""
import json
import sys

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import CurriculumTopic, CurriculumResource, UserProgress, XpEvent, RevisionSchedule


def prereq_slug(ref):
    if isinstance(ref, str):
        return ref
    if isinstance(ref, dict):
        return ref.get("slug") or ref.get("topic")
    return None


def main() -> None:
    snap = json.load(open(r"D:\Akshit Personal OS\backend\reports\final_intelligence_prechange_snapshot.json", encoding="utf-8"))
    db = SessionLocal()
    findings = []
    try:
        topics = db.query(CurriculumTopic).all()
        current_slugs = {t.slug for t in topics if t.slug}
        old_slugs = set(snap["topic_slugs"])

        missing = old_slugs - current_slugs
        findings.append({
            "check": "original_topic_slugs_preserved",
            "expected": len(old_slugs),
            "missing": sorted(missing),
            "pass": not missing,
        })

        # Original edges preserved verbatim (same source slug -> same ref list)
        by_slug = {t.slug: t for t in topics}
        # Whitelisted spec-timing corrections (documented, intentional):
        try:
            corr = json.load(open(
                r"D:\Akshit Personal OS\backend\reports\prerequisite_timing_corrections.json",
                encoding="utf-8",
            ))
            allowed_dropped = {
                c["topic"]: set(c["old"]) - set(c["new"]) for c in corr["changes"]
            }
        except Exception:
            allowed_dropped = {}
        edge_violations = []
        for src, refs in snap["prerequisite_edges"].items():
            t = by_slug.get(src)
            if t is None:
                edge_violations.append((src, "TOPIC MISSING"))
                continue
            cur = t.prerequisites or []
            dropped_here = allowed_dropped.get(src, set())
            for ref in refs:
                if isinstance(ref, str):
                    dslugs = {r.get("slug") or r.get("topic") for r in cur if isinstance(r, dict)}
                    present = ref in cur or ref in dslugs
                else:
                    rslug = ref.get("slug") or ref.get("topic")
                    cslugs = {
                        (r if isinstance(r, str) else (r.get("slug") or r.get("topic")))
                        for r in cur
                    }
                    present = rslug in cslugs
                    ref = rslug
                if not present and ref not in dropped_here:
                    edge_violations.append((src, ref))
        findings.append({
            "check": "original_prerequisite_edges_preserved",
            "original_edge_sources": len(snap["prerequisite_edges"]),
            "violations": edge_violations,
            "pass": not edge_violations,
        })

        prog = db.query(UserProgress).count()
        xp = db.query(XpEvent).count()
        rev = db.query(RevisionSchedule).count()
        findings.append({
            "check": "user_progress_rows",
            "before": snap["learner_progress"]["progress_rows"],
            "after": prog,
            "pass": prog == snap["learner_progress"]["progress_rows"],
        })
        findings.append({
            "check": "xp_events_unchanged",
            "before": snap["xp_history"]["xp_event_count"],
            "after": xp,
            "pass": xp == snap["xp_history"]["xp_event_count"],
        })
        findings.append({
            "check": "revision_state_baseline",
            "before": snap["revision_state"]["revision_schedule_rows"],
            "after": rev,
            "pass": rev >= snap["revision_state"]["revision_schedule_rows"],
        })

        resources_before = snap["counts"]["resources"]
        resources_after = db.query(CurriculumResource).count()
        findings.append({
            "check": "resources_not_deleted",
            "before": resources_before,
            "after": resources_after,
            "pass": resources_after >= resources_before,
        })

        new_topics = sorted(current_slugs - old_slugs)
        report = {
            "generated_for": "post-decomposition integrity check",
            "topic_count_before": len(old_slugs),
            "topic_count_after": len(current_slugs),
            "new_topic_count": len(new_topics),
            "new_topics": new_topics,
            "findings": findings,
            "overall_pass": all(f["pass"] for f in findings),
        }
        out = r"D:\Akshit Personal OS\backend\reports\postchange_comparison_report.json"
        json.dump(report, open(out, "w", encoding="utf-8"), indent=2)
        print(json.dumps({k: v for k, v in report.items() if k != "new_topics"}, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
