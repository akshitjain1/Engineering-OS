"""Generate the exact 66-item resource replacement research queue.

Reads resource_repair_queue.json + live database to produce:
- reports/resource_replacement_research_queue.json
- reports/resource_replacement_research_queue.md

For every resource includes all required fields, domain grouping,
replacement priority, and a research brief describing WHAT the new
resource must teach (no candidate URLs).
"""
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import (
    CurriculumLesson,
    CurriculumModule,
    CurriculumResource,
    CurriculumSubject,
    CurriculumTopic,
    CurriculumTrack,
    EngineeringProject,
    LessonExercise,
)

REPORT_DIR = Path(r"D:\Akshit Personal OS\backend\reports")
REPAIR_QUEUE = json.loads(
    (REPORT_DIR / "resource_repair_queue.json").read_text(encoding="utf-8")
)


# ── Domain classification ──────────────────────────────────────────
DOMAIN_MAP = {
    "cf": "Foundations",
    "java": "Java",
    "dsa": "DSA",
    "ml": "ML",
    "dl": "Deep Learning",
    "cv": "Computer Vision",
    "nlp": "NLP",
    "genai": "GenAI",
    "ai-eng": "AI Engineering",
    "math": "Math",
    "mlops": "MLOps",
    "be": "Backend",
    "db": "Backend",
    "net": "Backend",
    "sys": "Backend",
    "ops": "Backend",
    "devops": "Backend",
    "se": "SE",
    "ds": "ML",       # data science → ML bucket
}


def classify_domain(topic_slug: str) -> str:
    """Determine domain from topic slug prefix."""
    if not topic_slug:
        return "other"
    # Try longest prefix first (e.g. ai-eng before ai)
    for prefix in sorted(DOMAIN_MAP, key=len, reverse=True):
        if topic_slug.startswith(prefix + "-"):
            return DOMAIN_MAP[prefix]
    return "other"


def classify_priority(domain: str, topic_slug: str, has_dependents: bool) -> str:
    """Assign replacement priority P0/P1/P2."""
    # P0 = learner reaches soon / important prerequisite
    if domain == "Foundations":
        return "P0"
    if domain == "Java" and has_dependents:
        return "P0"
    # P1 = core domain / downstream impact
    if domain in ("Java", "DSA", "SE", "Backend"):
        return "P1"
    if has_dependents:
        return "P1"
    # P2 = later specialist topics
    return "P2"


def build_research_brief(topic_name, topic_desc, required_concepts, failure_type, resource_title):
    """Build a human-readable research brief for what the replacement must teach."""
    brief_lines = []
    # What must be taught
    if topic_desc:
        brief_lines.append(f"- Must teach: {topic_desc}")
    else:
        brief_lines.append(f"- Must teach: {topic_name}")
    # Required concepts
    if required_concepts:
        brief_lines.append(f"- Must cover concepts: {', '.join(required_concepts)}")
    # Why current failed
    if "404" in failure_type or "DEAD" in failure_type:
        brief_lines.append(f"- Current resource failure: HTTP 404 (page removed)")
    elif "CONTENT_LOST" in failure_type:
        brief_lines.append(f"- Current resource failure: Content no longer covers the learning objective")
    else:
        brief_lines.append(f"- Current resource failure: {failure_type}")
    # Requirements for replacement
    brief_lines.append("- Preferably a bounded instructional lesson (article, tutorial, or video)")
    brief_lines.append("- Must be freely accessible")
    brief_lines.append("- Must be from a reputable provider")
    return "\n".join(brief_lines)


def main():
    db = SessionLocal()
    try:
        # Load all topics, lessons, resources
        topics = {t.slug: t for t in db.query(CurriculumTopic).all() if t.slug}
        lessons = {l.id: l for l in db.query(CurriculumLesson).all()}
        modules = {m.id: m for m in db.query(CurriculumModule).all()}
        subjects = {s.id: s for s in db.query(CurriculumSubject).all()}
        tracks = {t.id: t for t in db.query(CurriculumTrack).all()}
        projects = db.query(EngineeringProject).all()

        # Build downstream dependency map: topic_slug → [dependent slugs]
        downstream = defaultdict(list)
        for t in topics.values():
            prereqs = t.prerequisites or []
            for p in prereqs:
                pslug = p if isinstance(p, str) else (p.get("slug") or p.get("topic") or "")
                if pslug:
                    downstream[pslug].append(t.slug)

        # Build project links: topic_slug → [project slugs]
        project_links_map = defaultdict(list)
        for proj in projects:
            for prereq in (proj.prerequisites or []):
                ps = prereq if isinstance(prereq, str) else (prereq.get("slug") or "")
                if ps:
                    project_links_map[ps].append(proj.slug)

        # Process the 66 replacement-required resources
        replacement_items = REPAIR_QUEUE.get("RESOURCE_REPLACEMENT_REQUIRED", [])
        print(f"Processing {len(replacement_items)} replacement-required resources")

        queue = []
        domain_counts = defaultdict(int)

        for item in replacement_items:
            topic_slug = item["topic"]
            resource_slug = item["resource"]
            
            # Look up resource in DB
            resource = db.query(CurriculumResource).filter_by(slug=resource_slug).first()
            if not resource:
                print(f"  WARN: Resource {resource_slug} not found in DB")
                continue

            # Look up topic
            topic = topics.get(topic_slug)
            if not topic:
                # Try to find topic from the resource's lesson
                lesson = lessons.get(resource.lesson_id)
                if lesson:
                    topic = topics.get(lesson.slug)

            # Build lesson/topic chain
            lesson = lessons.get(resource.lesson_id)
            topic_obj = None
            module_name = ""
            subject_name = ""
            track_name = ""
            topic_name = topic_slug
            topic_desc = ""
            topic_prereqs = []
            topic_track = "CORE"
            topic_depth = "WORKING_KNOWLEDGE"
            topic_difficulty = "beginner"
            topic_est_min = None
            topic_domain_key = None

            if topic:
                topic_obj = topic
                topic_name = topic.name or topic_slug
                topic_desc = topic.description or ""
                topic_prereqs = topic.prerequisites or []
                topic_track = topic.learning_track or "CORE"
                topic_depth = topic.depth_target or "WORKING_KNOWLEDGE"
                topic_est_min = topic.estimated_minutes
                topic_domain_key = topic.domain_key
                mod = modules.get(topic.module_id)
                if mod:
                    module_name = mod.name or ""
                    sub = subjects.get(mod.subject_id)
                    if sub:
                        subject_name = sub.name or ""
                        trk = tracks.get(sub.track_id)
                        if trk:
                            track_name = trk.name or ""

            # Determine difficulty from resource or topic
            diff = resource.difficulty or topic_difficulty
            if topic_obj:
                # Infer from depth_target
                dt = (topic_obj.depth_target or "").upper()
                if "AWARENESS" in dt:
                    diff = "beginner"
                elif "WORKING" in dt:
                    diff = "intermediate"
                elif "MASTERY" in dt or "DEEP" in dt:
                    diff = "advanced"

            # Domain classification
            domain = classify_domain(topic_slug)
            domain_counts[domain] += 1

            # Downstream dependents
            dependents = downstream.get(topic_slug, [])
            has_dependents = len(dependents) > 0

            # Practice contract
            practice_contract = None
            if lesson:
                exercises = db.query(LessonExercise).filter_by(lesson_id=lesson.id).all()
                if exercises:
                    practice_contract = {
                        "count": len(exercises),
                        "types": list(set(e.exercise_type for e in exercises if e.exercise_type)),
                        "destinations": list(set(e.destination_url for e in exercises if e.destination_url)),
                    }

            # Project links for this topic
            proj_links = project_links_map.get(topic_slug, [])

            # Required concepts from resource
            req_concepts = resource.required_concepts_covered or []

            # Prerequisite slugs
            prereq_slugs = []
            for p in topic_prereqs:
                if isinstance(p, str):
                    prereq_slugs.append(p)
                elif isinstance(p, dict):
                    prereq_slugs.append(p.get("slug") or p.get("topic") or "")

            # Priority
            priority = classify_priority(domain, topic_slug, has_dependents)

            # Existing boundary info
            existing_boundary = {
                "boundary_type": resource.boundary_type,
                "start_boundary": resource.start_boundary,
                "end_boundary": resource.end_boundary,
            }

            # Evidence
            ev_raw = resource.verification_evidence
            verification_evidence = None
            if ev_raw:
                try:
                    verification_evidence = json.loads(ev_raw) if isinstance(ev_raw, str) else ev_raw
                except Exception:
                    verification_evidence = str(ev_raw)

            # Build research brief
            failure_type = item.get("issue", "UNKNOWN")
            research_brief = build_research_brief(
                topic_name, topic_desc, req_concepts, failure_type, resource.title
            )

            entry = {
                "domain": domain,
                "topic_slug": topic_slug,
                "topic_title": topic_name,
                "learning_unit_id": resource.lesson_id,
                "learning_objective": topic_desc or f"Understand {topic_name}",
                "required_concepts": req_concepts,
                "current_resource_id": resource.id,
                "current_title": resource.title,
                "current_provider": resource.provider,
                "current_url": resource.url,
                "failure_type": failure_type,
                "verification_evidence": verification_evidence,
                "why_current_resource_failed": item.get("evidence", failure_type),
                "existing_estimated_minutes": resource.estimated_minutes or topic_est_min,
                "existing_boundary": existing_boundary,
                "difficulty": diff,
                "track": topic_track,
                "depth": topic_depth,
                "prerequisites": prereq_slugs,
                "downstream_dependents": dependents,
                "practice_contract": practice_contract,
                "project_links": proj_links,
                "replacement_priority": priority,
                "research_brief": research_brief,
            }
            queue.append(entry)

        print(f"\nResearch queue built: {len(queue)} items")

        # Sort by priority then domain
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        queue.sort(key=lambda x: (priority_order.get(x["replacement_priority"], 9), x["domain"], x["topic_slug"]))

        # ── Write JSON ──
        output_json = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_items": len(queue),
            "domain_counts": dict(sorted(domain_counts.items())),
            "priority_counts": {
                "P0": sum(1 for q in queue if q["replacement_priority"] == "P0"),
                "P1": sum(1 for q in queue if q["replacement_priority"] == "P1"),
                "P2": sum(1 for q in queue if q["replacement_priority"] == "P2"),
            },
            "queue": queue,
        }
        json_path = REPORT_DIR / "resource_replacement_research_queue.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=2, default=str)
        print(f"JSON written: {json_path}")

        # ── Write Markdown ──
        md_lines = [
            "# Resource Replacement Research Queue",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "",
            f"**Total items: {len(queue)}**",
            "",
            "## Priority Summary",
            "",
            f"- **P0** (learner reaches soon / important prerequisite): {output_json['priority_counts']['P0']}",
            f"- **P1** (core domain / downstream impact): {output_json['priority_counts']['P1']}",
            f"- **P2** (later specialist topic): {output_json['priority_counts']['P2']}",
            "",
            "## Domain Breakdown",
            "",
            "| Domain | Count |",
            "|--------|-------|",
        ]
        # Ensure all domains from spec are listed
        all_domains = [
            "Foundations", "Java", "DSA", "ML", "Deep Learning",
            "Computer Vision", "NLP", "GenAI", "AI Engineering",
            "Math", "MLOps", "Backend", "SE", "other",
        ]
        for d in all_domains:
            c = domain_counts.get(d, 0)
            if c > 0:
                md_lines.append(f"| {d} | {c} |")
        md_lines.append("")

        # Group by domain
        by_domain = defaultdict(list)
        for entry in queue:
            by_domain[entry["domain"]].append(entry)

        for domain in all_domains:
            items = by_domain.get(domain, [])
            if not items:
                continue
            md_lines.append(f"## {domain} ({len(items)})")
            md_lines.append("")
            for entry in items:
                md_lines.append(f"### [{entry['replacement_priority']}] `{entry['topic_slug']}`")
                md_lines.append("")
                md_lines.append(f"**Topic:** {entry['topic_title']}")
                md_lines.append("")
                md_lines.append(f"**Learning objective:** {entry['learning_objective']}")
                md_lines.append("")
                if entry["required_concepts"]:
                    md_lines.append(f"**Required concepts:** {', '.join(entry['required_concepts'])}")
                    md_lines.append("")
                md_lines.append(f"**Current resource:** {entry['current_title']}")
                md_lines.append(f"- Provider: {entry['current_provider']}")
                md_lines.append(f"- URL: {entry['current_url']}")
                md_lines.append(f"- Failure: {entry['failure_type']}")
                md_lines.append(f"- Evidence: {entry['why_current_resource_failed']}")
                md_lines.append("")
                md_lines.append(f"**Difficulty:** {entry['difficulty']} | **Track:** {entry['track']} | **Depth:** {entry['depth']}")
                if entry["existing_estimated_minutes"]:
                    md_lines.append(f"**Estimated minutes:** {entry['existing_estimated_minutes']}")
                md_lines.append("")
                if entry["prerequisites"]:
                    md_lines.append(f"**Prerequisites:** {', '.join(entry['prerequisites'][:10])}")
                if entry["downstream_dependents"]:
                    md_lines.append(f"**Downstream dependents:** {', '.join(entry['downstream_dependents'][:10])}")
                if entry["project_links"]:
                    md_lines.append(f"**Project links:** {', '.join(entry['project_links'])}")
                if entry["practice_contract"]:
                    pc = entry["practice_contract"]
                    md_lines.append(f"**Practice contract:** {pc['count']} exercises ({', '.join(pc['types'])})")
                md_lines.append("")
                md_lines.append("**Research brief:**")
                md_lines.append("```")
                md_lines.append(entry["research_brief"])
                md_lines.append("```")
                md_lines.append("")
                md_lines.append("---")
                md_lines.append("")

        md_path = REPORT_DIR / "resource_replacement_research_queue.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")
        print(f"Markdown written: {md_path}")

        # Print domain summary
        print("\n" + "=" * 70)
        print("DOMAIN SUMMARY")
        print("=" * 70)
        for d in all_domains:
            c = domain_counts.get(d, 0)
            if c > 0:
                slugs = [e["topic_slug"] for e in by_domain[d]]
                print(f"  {d}: {c}")
                for s in slugs:
                    print(f"    - {s}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
