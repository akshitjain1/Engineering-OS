"""Generate curriculum_domain_blueprint.json + .md from REAL database state.

For every topic: domain, stage, slug, title, objective, prerequisites,
parallel eligibility, depth, why-it-exists, unlocks, practice requirement.
"""
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import CurriculumTopic, CurriculumModule, CurriculumSubject, CurriculumLesson, CurriculumResource

DOMAIN_PREFIXES = [
    ("cf-", "CS Foundations", "PHASE_1_ENGINEERING_FUNDAMENTALS"),
    ("java-", "Java", "PHASE_2_PROGRAMMING_DSA"),
    ("dsa-", "DSA & Algorithms", "PHASE_2_PROGRAMMING_DSA"),
    ("se-", "Software Engineering", "PHASE_3_ENGINEERING"),
    ("db-", "Backend & Databases", "PHASE_3_ENGINEERING"),
    ("be-", "Backend & Databases", "PHASE_3_ENGINEERING"),
    ("py-", "Python", "PHASE_3_PYTHON_MATH"),
    ("python-", "Python", "PHASE_3_PYTHON_MATH"),
    ("math-", "Mathematics for ML", "PHASE_5_JIT_MATH"),
    ("ml-", "Machine Learning", "PHASE_4_MACHINE_LEARNING"),
    ("ds-", "Data Science", "PHASE_4_MACHINE_LEARNING"),
    ("dl-", "Deep Learning", "PHASE_6_DEEP_LEARNING"),
    ("cv-", "Computer Vision", "PHASE_7_COMPUTER_VISION"),
    ("nlp-", "NLP", "PHASE_8_NLP"),
    ("genai-", "Generative AI / LLMs", "PHASE_9_GENAI_LLM"),
    ("ai-", "AI Engineering / Agents", "PHASE_10_AI_ENGINEERING"),
    ("mlops-", "MLOps", "PHASE_10_AI_ENGINEERING"),
    ("sd-", "System Design", "PHASE_10_SYSTEM_DESIGN"),
    ("sysdesign-", "System Design", "PHASE_10_SYSTEM_DESIGN"),
    ("net-", "Networking / DevOps", "PHASE_1_SUPPORTING"),
    ("devops-", "Networking / DevOps", "PHASE_1_SUPPORTING"),
]


def domain_for(slug: str) -> tuple[str, str]:
    for prefix, domain, stage in DOMAIN_PREFIXES:
        if slug.startswith(prefix):
            return domain, stage
    return "Other", "PHASE_UNSORTED"


def prereq_slug(ref) -> str | None:
    if isinstance(ref, str):
        return ref
    if isinstance(ref, dict):
        return ref.get("slug") or ref.get("topic")
    return None


def prereq_type(ref) -> str:
    if isinstance(ref, dict):
        return ref.get("type", "REQUIRED")
    return "REQUIRED"


def main() -> None:
    db = SessionLocal()
    try:
        subjects = {s.id: s.name for s in db.query(CurriculumSubject).all()}
        modules = {
            m.id: {"name": m.name, "subject": subjects.get(m.subject_id)}
            for m in db.query(CurriculumModule).all()
        }
        topics = db.query(CurriculumTopic).order_by(CurriculumTopic.module_id, CurriculumTopic.order_index).all()
        lessons_by_topic: dict[int, list] = defaultdict(list)
        resources_by_topic: dict[int, list] = defaultdict(list)
        lessons = db.query(CurriculumLesson).all()
        lesson_topic = {l.id: l.topic_id for l in lessons}
        for r in db.query(CurriculumResource).all():
            tid = lesson_topic.get(r.lesson_id)
            if tid is not None:
                resources_by_topic[tid].append(r)

        # reverse graph: what does each topic unlock
        unlocks: dict[str, set] = defaultdict(set)
        by_slug = {t.slug: t for t in topics if t.slug}
        for t in topics:
            for ref in t.prerequisites or []:
                p = prereq_slug(ref)
                if p and p in by_slug:
                    unlocks[p].add(t.slug)

        entries = []
        domain_counts: dict[str, int] = defaultdict(int)
        for t in topics:
            slug = t.slug or ""
            domain, stage = domain_for(slug)
            domain_counts[domain] += 1
            required = [prereq_slug(r) for r in (t.prerequisites or [])]
            required = [r for r in required if r]
            recommended = [
                prereq_slug(r) for r in (t.prerequisites or []) if prereq_type(r) == "RECOMMENDED"
            ]
            res = resources_by_topic.get(t.id, [])
            primary_count = sum(1 for r in res if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN"))
            practice_count = sum(1 for r in res if (r.role or "").upper() == "PRACTICE")
            entry = {
                "domain": domain,
                "stage": stage,
                "module": modules.get(t.module_id, {}).get("name"),
                "subject": modules.get(t.module_id, {}).get("subject"),
                "topic_slug": slug,
                "topic_title": t.name,
                "learning_objective": (t.description or "").split("\n")[0][:300],
                "required_prerequisites": required,
                "recommended_prerequisites": recommended,
                "parallel_eligible": bool(t.parallel_eligible),
                "learning_track": t.learning_track,
                "depth": t.depth_target,
                "estimated_minutes": t.estimated_minutes,
                "why_this_topic_exists": (t.description or "")[:500],
                "next_concepts_unlocked": sorted(unlocks.get(slug, set())),
                "practice_requirement": {
                    "primary_resources": primary_count,
                    "practice_resources": practice_count,
                    "has_check": practice_count > 0 or any(
                        e.slug and "-practice" in (e.slug or "") for l in [] for e in []
                    ),
                },
                "resource_count": len(res),
            }
            entries.append(entry)

        blueprint = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "REAL database state — generated from curriculum_topics table",
            "total_topics": len(entries),
            "domains": dict(domain_counts),
            "topics": entries,
        }

        out_json = r"D:\Akshit Personal OS\backend\reports\curriculum_domain_blueprint.json"
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(blueprint, f, indent=2)

        # Markdown summary grouped by stage then domain
        by_stage: dict[str, list] = defaultdict(list)
        for e in entries:
            by_stage[e["stage"]].append(e)

        md_lines = [
            "# Curriculum Domain Blueprint",
            "",
            f"Generated from real DB state on {datetime.now(timezone.utc).isoformat()}",
            "",
            f"Total topics: **{len(entries)}** across {len(domain_counts)} domains.",
            "",
        ]
        for stage in sorted(by_stage.keys()):
            md_lines.append(f"## {stage}")
            md_lines.append("")
            current_domain = None
            for e in by_stage[stage]:
                if e["domain"] != current_domain:
                    current_domain = e["domain"]
                    md_lines.append(f"### Domain: {current_domain}")
                    md_lines.append("")
                    md_lines.append("| Slug | Title | Prereqs | Unlocks | Track | Depth |")
                    md_lines.append("|------|-------|---------|---------|-------|-------|")
                prereqs = ", ".join(e["required_prerequisites"][:3]) + (
                    f" (+{len(e['required_prerequisites'])-3})" if len(e["required_prerequisites"]) > 3 else ""
                )
                unlock_list = e["next_concepts_unlocked"]
                unlocks_str = ", ".join(unlock_list[:3]) + (f" (+{len(unlock_list)-3})" if len(unlock_list) > 3 else "")
                md_lines.append(
                    f"| `{e['topic_slug']}` | {e['topic_title']} | {prereqs} | {unlocks_str} | {e['learning_track']} | {e['depth']} |"
                )
            md_lines.append("")

        out_md = r"D:\Akshit Personal OS\backend\reports\curriculum_domain_blueprint.md"
        with open(out_md, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        print("Blueprint written:")
        print(" ", out_json)
        print(" ", out_md)
        print("Domain counts:", json.dumps(dict(domain_counts), indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
