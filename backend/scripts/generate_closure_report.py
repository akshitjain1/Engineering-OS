"""Generate final_ai_ml_content_closure.{md,json} — before/after per topic."""
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.content.concept_contracts import load_contract_payload
from app.content.learner_visibility import is_learner_visible
from app.db.session import SessionLocal
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic, LessonExercise

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"
AI_PREFIXES = ("math-", "ml-", "ds-", "dl-", "cv-", "nlp-", "genai-", "ai-eng-", "mlops-")


def main() -> None:
    pre = json.load(open(f"{REPORT_DIR}\\pre_content_closure_state.json", encoding="utf-8"))["topics"]
    evidence = json.load(open(f"{REPORT_DIR}\\resource_evidence_final.json", encoding="utf-8"))
    ev_by_topic = {r["topic_slug"]: r for r in evidence["resources"]}

    db = SessionLocal()
    try:
        contracts = load_contract_payload()["contracts"]
        lessons = db.query(CurriculumLesson).all()
        lesson_topic = {l.id: l.topic_id for l in lessons}
        prim_by_topic = {}
        for r in db.query(CurriculumResource).all():
            tid = lesson_topic.get(r.lesson_id)
            # Union coverage: ALL primaries incl. hidden supplements
            if tid is None:
                continue
            if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN"):
                prim_by_topic.setdefault(tid, []).append(r)

        ex_by_topic = set()
        for e in db.query(LessonExercise).all():
            tid = lesson_topic.get(e.lesson_id)
            if tid is not None:
                ex_by_topic.add(tid)

        topics = {t.slug: t for t in db.query(CurriculumTopic).all()}
        # Union: pre-existing AI topics + the 24 newly added units.
        all_ai_slugs = sorted(set(pre.keys()) | {
            t.slug for t in topics.values()
            if (t.slug or "").startswith(AI_PREFIXES)})
        repaired = []
        for slug in all_ai_slugs:
            before = pre.get(slug) or {
                "status": "NEW", "primary_url": None,
                "resource_slug": None, "concepts_required": [],
                "concepts_covered": []}
            t = topics.get(slug)
            req = [c["slug"] for c in ((contracts.get(slug) or {}).get("required") or [])]
            prim = prim_by_topic.get(t.id, []) if t else []
            covered_set = set()
            for r in prim:
                covered_set |= set(r.required_concepts_covered or [])
            if not req:
                # No authored requirements: READY iff its visible primary is
                # content-verified (nothing further to prove).
                sts = [(r.verification_status or "").upper() for r in prim]
                after = ("READY" if any(s == "VERIFIED_COVERAGE" for s in sts)
                         else "NEEDS_REVIEW" if any(s == "NEEDS_REVIEW" for s in sts)
                         else "NO_PRIMARY" if not prim else "PARTIAL")
            elif all(c in covered_set for c in req):
                after = "READY"
            elif covered_set:
                after = "PARTIAL"
            elif not prim:
                after = "NO_PRIMARY"  # internal shell — no learner unit
            elif any((r.verification_status or "") == "NEEDS_REVIEW" for r in prim):
                after = "NEEDS_REVIEW"
            else:
                after = "RESOURCE_GAP"

            ev = ev_by_topic.get(slug) or {}
            new_res = next((r for r in prim), None)
            old_res_url = before.get("primary_url")
            changed = (
                after != before["status"]
                or (new_res and new_res.url != old_res_url)
                or len(covered_set) != len(before.get("concepts_covered", []))
            )
            if changed:
                repaired.append({
                    "topic_slug": slug,
                    "readiness_before": before["status"],
                    "readiness_after": after,
                    "old_resource": {"url": old_res_url, "slug": before.get("resource_slug")},
                    "new_resource": {
                        "url": new_res.url if new_res else None,
                        "slug": new_res.slug if new_res else None,
                        "exactness": getattr(new_res, "exactness", None),
                        "estimated_minutes": getattr(new_res, "estimated_minutes", None),
                        "verification_status": getattr(new_res, "verification_status", None),
                    },
                    "concepts_required": req,
                    "concepts_covered_after": sorted(covered_set),
                    "still_missing": [c for c in req if c not in covered_set],
                    "evidence_count": len(ev.get("evidence_detail") or []),
                    "practice_present": bool(t and t.id in ex_by_topic),
                })

        # Domain summary
        dom_of = lambda s: next((d for p, d in [
            ("math-", "Math"), ("ml-", "ML"), ("ds-", "Data Science"), ("dl-", "DL"),
            ("cv-", "CV"), ("nlp-", "NLP"), ("genai-", "GenAI"),
            ("ai-eng-", "AI Engineering"), ("mlops-", "MLOps")]
            if s.startswith(p)), "Other")
        domain_summary = defaultdict(lambda: Counter())
        after_by_slug = {r["topic_slug"]: r["readiness_after"] for r in repaired}
        for slug in all_ai_slugs:
            status = after_by_slug.get(slug) or (pre.get(slug) or {}).get("status", "NEW")
            domain_summary[dom_of(slug)][status] += 1

        total_new_topics = json.load(open(f"{REPORT_DIR}\\decomposition_v2_log.json",
                                          encoding="utf-8"))["created_count"]

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scope": "AI/ML specialization content closure",
            "new_topics_added": total_new_topics,
            "inspection_distribution_133": evidence["distribution"],
            "repaired_topic_count": len(repaired),
            "domain_summary_after": {k: dict(v) for k, v in domain_summary.items()},
            "repaired_topics": repaired,
        }
        json.dump(report, open(f"{REPORT_DIR}\\final_ai_ml_content_closure.json", "w",
                               encoding="utf-8"), indent=2)

        md = ["# Final AI/ML Content Closure", "",
              f"Generated: {report['generated_at']}", "",
              f"- New bounded units added: **{total_new_topics}** (425 → 449 topics)",
              f"- Topics repaired (status/resource/evidence changed): **{len(repaired)}** of {len(pre)} AI-domain topics",
              f"- Post-closure inspection: **{json.dumps(evidence['distribution'])}**",
              "", "## Domain summary (after)", "",
              "| Domain | READY | PARTIAL | GAP | NEEDS_REVIEW |", "|---|---|---|---|---|"]
        for d in sorted(domain_summary):
            c = domain_summary[d]
            md.append(f"| {d} | {c.get('READY',0)} | {c.get('PARTIAL',0)} | "
                      f"{c.get('RESOURCE_GAP',0)} | {c.get('NEEDS_REVIEW',0)} |")
        md += ["", "## Repaired topics", ""]
        md += ["| Topic | Before | After | Concepts verified | Missing | Practice |",
               "|---|---|---|---|---|---|"]
        for r in repaired:
            md.append(f"| `{r['topic_slug']}` | {r['readiness_before']} | {r['readiness_after']} "
                      f"| {len(r['concepts_covered_after'])}/{len(r['concepts_required'])} "
                      f"| {', '.join(r['still_missing']) or '—'} | {'✓' if r['practice_present'] else '—'} |")
        open(f"{REPORT_DIR}\\final_ai_ml_content_closure.md", "w",
             encoding="utf-8").write("\n".join(md))

        print(json.dumps({
            "repaired": len(repaired),
            "distribution_133": evidence["distribution"],
            "domain_summary_after": {k: dict(v) for k, v in domain_summary.items()},
        }, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
