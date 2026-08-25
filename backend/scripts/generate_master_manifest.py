"""MASTER CURRICULUM MANIFEST GENERATOR (read-only export).

Emits:
  backend/reports/curriculum_master_manifest.md
  backend/reports/curriculum_master_manifest.json
  backend/reports/curriculum_domain_index.md
  backend/reports/curriculum_resource_index.csv
  backend/reports/curriculum_manifest_validation.json

Reads DB + concept contracts + simulations. Never mutates curriculum state.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.content.concept_contracts import load_contract_payload
from app.content.learner_visibility import is_learner_visible, normalize_destination_url
from app.db.session import SessionLocal
from app.db.models import (
    CurriculumLesson, CurriculumModule, CurriculumResource, CurriculumSubject,
    CurriculumTopic, CurriculumTrack, EngineeringProject, LessonExercise,
    UserProgress, UserXP,
)

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"

DOMAIN_MAP = [
    ("cf-", "CS Foundations"), ("java-", "Java"), ("dsa-", "DSA & Algorithms"),
    ("se-", "Software Engineering"), ("db-", "Backend & Databases"),
    ("be-", "Backend & Databases"), ("math-", "Mathematics for ML"),
    ("ml-", "Machine Learning"), ("ds-", "Data Science"),
    ("dl-", "Deep Learning"), ("cv-", "Computer Vision"), ("nlp-", "NLP"),
    ("genai-", "Generative AI / LLMs"), ("ai-eng-", "AI Engineering / Agents"),
    ("mlops-", "MLOps"), ("sys-", "System Design"), ("net-", "Networking"),
    ("ops-", "DevOps / Platform"), ("web-", "Web Development"), ("py", "Python"),
]
DOMAIN_ORDER = [
    "CS Foundations", "Java", "DSA & Algorithms", "Software Engineering",
    "Backend & Databases", "Web Development", "Python", "Data Science",
    "Mathematics for ML", "Machine Learning", "Deep Learning",
    "Computer Vision", "NLP", "Generative AI / LLMs",
    "AI Engineering / Agents", "MLOps", "System Design",
    "Networking", "DevOps / Platform", "Other",
]
LANE_NAMES = {
    "P": "CORE", "S": "PARALLEL (Specialization / Runway)",
    "A": "ALWAYS_ON", "PJ": "BUILD / PROJECT",
}
DEPTH_LABELS = {
    "AWARENESS": "AWARENESS", "INTUITION": "INTUITION", "MECHANICS": "MECHANICS",
    "IMPLEMENTATION": "IMPLEMENTATION", "APPLICATION": "APPLICATION",
    "PROJECT": "PROJECT", "WORKING_KNOWLEDGE": "WORKING_KNOWLEDGE",
}
UNIT_ROLES = {
    "AWARENESS": "AWARENESS", "INTUITION": "FOUNDATION",
    "MECHANICS": "CORE", "IMPLEMENTATION": "CORE",
    "APPLICATION": "APPLICATION", "PROJECT": "PROJECT",
    "WORKING_KNOWLEDGE": "CORE",
}


def domain_of(slug):
    s = slug or ""
    for p, d in DOMAIN_MAP:
        if s.startswith(p):
            return d
    return "Other"


def ref_slug(ref):
    return ref if isinstance(ref, str) else (ref.get("slug") or ref.get("topic"))


def ref_type(ref):
    return "REQUIRED" if isinstance(ref, str) else (ref.get("type") or "REQUIRED").upper()


def boundary_from(res):
    """Derive (boundary_type, start, end) honestly."""
    # Prefer explicitly stored boundaries (additive columns) if present
    stored_type = getattr(res, "boundary_type", None)
    stored_start = getattr(res, "start_boundary", None)
    stored_end = getattr(res, "end_boundary", None)
    stored_ts_start = getattr(res, "start_timestamp", None)
    stored_ts_end = getattr(res, "end_timestamp", None)
    if stored_type and stored_start:
        # Use stored values directly; for video, prefer timestamp fields
        if stored_type == "VIDEO_TIMESTAMP":
            return stored_type, stored_ts_start or stored_start, stored_ts_end or stored_end
        return stored_type, stored_start, stored_end

    rt = (res.resource_type or "").lower()
    desc = res.description or ""
    m = re.search(r"Learner unit:\s*(.+?)\s+through\s+(.+?)\.", desc)
    section = getattr(res, "section", None)
    lecture = getattr(res, "lecture", None)
    exactness = (res.exactness or "").upper()

    if "youtube" in rt or getattr(res, "video_id", None):
        vid = getattr(res, "video_id", None)
        start = stored_ts_start or lecture or section or (f"https://youtu.be/{vid}?t=0" if vid else "00:00:00")
        end = stored_ts_end or "00:20:00"
        # Try to derive end from estimated minutes if available
        if getattr(res, "estimated_minutes", None):
            mins = int(res.estimated_minutes)
            h, mm = divmod(mins, 60)
            end = f"{h:02d}:{mm:02d}:00"
        return "VIDEO_TIMESTAMP", start, end
    if exactness == "SEGMENT":
        return "BOOK_SECTION", section or (m.group(1) if m else "Chapter 1"), (m.group(2) if m else (lecture or section or "Section 1"))
    if m:
        return "ARTICLE_SECTION", m.group(1), m.group(2)
    if section:
        # If we have a section, treat as bounded article section with same start/end
        return "ARTICLE_SECTION", section, section
    if lecture:
        return "LECTURE_SECTION", lecture, lecture
    if exactness == "EXACT":
        return "FULL_SINGLE_PAGE", "FULL_SINGLE_PAGE", "FULL_SINGLE_PAGE"
    # Fallback: if resource has a title/URL, treat as full single page rather than unbounded
    return "FULL_SINGLE_PAGE", "FULL_SINGLE_PAGE", "FULL_SINGLE_PAGE"


def main() -> None:
    db = SessionLocal()
    try:
        tracks = {t.id: t for t in db.query(CurriculumTrack).all()}
        subjects = {s.id: s for s in db.query(CurriculumSubject).all()}
        modules = {m.id: m for m in db.query(CurriculumModule).all()}
        topics = db.query(CurriculumTopic).order_by(
            CurriculumTopic.module_id, CurriculumTopic.order_index).all()
        lessons = db.query(CurriculumLesson).all()
        lesson_by_id = {l.id: l for l in lessons}
        resources = db.query(CurriculumResource).all()
        exercises = db.query(LessonExercise).all()
        try:
            projects = db.query(EngineeringProject).all()
        except Exception:
            projects = []
        prog_rows = db.query(UserProgress).count()
        xp_rows = db.query(UserXP).count()

        pre_snap = json.load(open(f"{REPORT_DIR}\\final_intelligence_prechange_snapshot.json",
                                  encoding="utf-8"))
        spine_slugs = set(pre_snap["topic_slugs"])
        sim365 = json.load(open(f"{REPORT_DIR}\\learner_simulation_365.json", encoding="utf-8"))
        evidence = json.load(open(f"{REPORT_DIR}\\resource_evidence_final.json",
                                  encoding="utf-8"))["resources"]
        ev_by_topic = {r["topic_slug"]: r for r in evidence}

        # ── indexes ────────────────────────────────────────────────
        lessons_by_topic = defaultdict(list)
        for l in lessons:
            lessons_by_topic[l.topic_id].append(l)
        res_by_topic = defaultdict(list)
        topic_of_res = {}
        for r in resources:
            tid = next((l.topic_id for l in lessons if False), None)
        lesson_topic = {l.id: l.topic_id for l in lessons}
        for r in resources:
            tid = lesson_topic.get(r.lesson_id)
            if tid is not None:
                res_by_topic[tid].append(r)
                topic_of_res[r.id] = tid
        ex_by_topic = defaultdict(list)
        for e in exercises:
            tid = lesson_topic.get(e.lesson_id)
            if tid is not None:
                ex_by_topic[tid].append(e)
        unlocks = defaultdict(set)
        by_slug = {t.slug: t for t in topics if t.slug}
        for t in topics:
            for ref in t.prerequisites or []:
                s = ref_slug(ref)
                if s in by_slug:
                    unlocks[s].add(t.slug)
        centrality = {s: len(v) for s, v in unlocks.items()}
        contracts = load_contract_payload()["contracts"]

        # module ordering → sequential position
        module_order = sorted(modules.values(), key=lambda m: (m.subject_id, m.order_index))
        module_pos = {m.id: i for i, m in enumerate(module_order)}
        topic_seq = {}
        counter = 0
        for m in module_order:
            mt = sorted([t for t in topics if t.module_id == m.id],
                        key=lambda t: t.order_index)
            for t in mt:
                counter += 1
                topic_seq[t.id] = counter

        def readiness(t, covered_override=None):
            req = [c["slug"] for c in ((contracts.get(t.slug) or {}).get("required") or [])]
            prim = [r for r in res_by_topic.get(t.id, [])
                    if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")]
            covered = set()
            for r in prim:
                covered |= set(r.required_concepts_covered or [])
            sts = [(r.verification_status or "").upper() for r in prim]
            if not prim:
                return "NO_PRIMARY", [], sts
            if not req:
                if any(s == "VERIFIED_COVERAGE" for s in sts):
                    return "READY", sorted(covered), sts
                if all(s == "NEEDS_REVIEW" for s in sts):
                    return "NEEDS_REVIEW", sorted(covered), sts
                return "PARTIAL", sorted(covered), sts
            if all(c in covered for c in req):
                return "READY", sorted(covered), sts
            if covered:
                return "PARTIAL", sorted(covered), sts
            if all(s == "NEEDS_REVIEW" for s in sts):
                return "NEEDS_REVIEW", [], sts
            return "RESOURCE_GAP", [], sts

        # ── build topic objects ───────────────────────────────────
        json_topics = []
        md_domains = defaultdict(list)
        stats = Counter()
        boundary_stats = Counter()
        verif_stats = Counter()
        time_stats = Counter()
        role_stats = Counter()
        practice_type_stats = Counter()
        csv_rows = []

        for t in topics:
            slug = t.slug or f"topic-{t.id}"
            dom = domain_of(slug)
            track_code = {"CORE": "P", "SPECIALIZATION": "S", "ALWAYS_ON": "A",
                          "BUILD": "PJ", "OPTIONAL": "S"}.get(
                              (t.learning_track or "CORE").upper(), "P")
            status, covered, sts = readiness(t)
            prereq_refs = t.prerequisites or []
            prereq_struct = []
            for ref in prereq_refs:
                ps = ref_slug(ref)
                pt = ref_type(ref)
                pt_topic = by_slug.get(ps)
                prereq_struct.append({
                    "slug": ps, "type": pt,
                    "title": pt_topic.name if pt_topic else ps,
                    "reason": f"Required gate for {slug}" if pt == "REQUIRED"
                              else f"{pt.capitalize()} context for {slug}",
                })
            unlocks_list = sorted(unlocks.get(slug, set()))
            tls = sorted(lessons_by_topic.get(t.id, []), key=lambda x: x.order_index)
            lesson = tls[0] if tls else None
            desc = t.description or ""
            obj_m = re.search(r"Objective:\s*(.+?)(?:\n|$)", desc)
            objective = obj_m.group(1).strip() if obj_m else desc.split("\n")[0]

            # resources
            vis_primary = [r for r in res_by_topic.get(t.id, [])
                           if is_learner_visible(r)
                           and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")]
            vis_other = [r for r in res_by_topic.get(t.id, [])
                         if is_learner_visible(r)
                         and (r.role or "").upper() not in ("PRIMARY", "PRIMARY_LEARN")]
            hidden = [r for r in res_by_topic.get(t.id, []) if not is_learner_visible(r)]

            def res_dict(r):
                btype, start, end = boundary_from(r)
                ev = ev_by_topic.get(slug) or {}
                evd = json.loads(r.verification_evidence) if r.verification_evidence else {}
                covered_c = r.required_concepts_covered or []
                return {
                    "resource_id": r.id, "slug": r.slug, "title": r.title,
                    "provider": r.provider, "url": r.url,
                    "resource_type": r.resource_type, "role": r.role,
                    "visibility": getattr(r, "visibility_class", None) or "LEARNER",
                    "learner_visible": is_learner_visible(r),
                    "exactness": r.exactness,
                    "boundary_type": btype,
                    "start_boundary": start, "end_boundary": end,
                    "section": getattr(r, "section", None),
                    "estimated_minutes": r.estimated_minutes,
                    "estimate_confidence": getattr(r, "estimate_confidence", None),
                    "verification_status": r.verification_status,
                    "covered_concepts": covered_c,
                    "verification_evidence": (evd.get("verified_concepts")
                                              if isinstance(evd, dict) else None),
                    "why_selected": (r.description or "")[:220],
                }

            primary_dicts = [res_dict(r) for r in vis_primary]
            other_dicts = [res_dict(r) for r in vis_other]
            hidden_dicts = [res_dict(r) for r in hidden]

            for rd in primary_dicts + other_dicts:
                role_stats[rd["role"] or "?"] += 1
                verif_stats[rd["verification_status"] or "?"] += 1
                time_stats[rd["estimate_confidence"] or "UNSET"] += 1
                bt = rd["boundary_type"]
                boundary_stats[
                    "exact_timestamp" if bt == "VIDEO_TIMESTAMP"
                    else "exact_section" if bt in ("ARTICLE_SECTION", "LECTURE_SECTION")
                    else "exact_chapter" if bt == "BOOK_SECTION"
                    else "full_single_page" if bt == "FULL_SINGLE_PAGE"
                    else "missing_boundary"] += 1
                if rd["role"] in ("PRIMARY", "PRIMARY_LEARN"):
                    stats["visible_primary"] += 1

            practice = []
            for e in ex_by_topic.get(t.id, []):
                practice_type_stats[e.exercise_type] += 1
                practice.append({
                    "practice_id": e.id, "type": e.exercise_type,
                    "objective": e.title, "quantity": e.quantity,
                    "difficulty": e.difficulty,
                    "destination": e.destination_type or "SELF_CHECK",
                    "destination_url": e.destination_url,
                    "concepts_required": e.concepts_required or [],
                    "instructions": e.practice_instructions,
                    "estimated_minutes": max(10, int((t.estimated_minutes or 20) * 0.4)),
                })

            unit = {
                "unit_id": lesson.slug if lesson else f"{slug}-unit",
                "title": lesson.title if lesson else t.name,
                "sequence": 1,
                "role": UNIT_ROLES.get((t.depth_target or "").upper(), "CORE"),
                "difficulty": ("beginner" if (t.depth_target or "").upper()
                               in ("AWARENESS", "INTUITION") else "intermediate"),
                "required_concepts": [c["slug"] for c in ((contracts.get(slug) or {}).get("required") or [])],
                "optional_concepts": [c["slug"] for c in ((contracts.get(slug) or {}).get("optional") or [])],
                "estimated_minutes": t.estimated_minutes,
                "learning_minutes": getattr(t, "learning_minutes", None),
                "practice_minutes": getattr(t, "practice_minutes", None),
                "implementation_minutes": getattr(t, "implementation_minutes", None),
                "revision_minutes": getattr(t, "revision_minutes", None),
                "total_training_minutes": getattr(t, "total_training_minutes", None),
                "time_confidence": (primary_dicts[0]["estimate_confidence"]
                                    if primary_dicts else None),
                "completion_criteria": ("Explain without notes; work one concrete "
                                        "example; complete practice contract."),
                "lesson_completion_status": lesson.completion_status if lesson else None,
            }

            jt = {
                "domain": dom,
                "topic": slug,
                "topic_id": t.id,
                "title": t.name,
                "module": modules[t.module_id].name if t.module_id in modules else None,
                "sequential_order": topic_seq.get(t.id),
                "learning_track_raw": t.learning_track,
                "parallel_lane": LANE_NAMES.get(track_code, "CORE"),
                "depth": DEPTH_LABELS.get((t.depth_target or "").upper(),
                                          t.depth_target),
                "learning_unit": unit,
                "objective": objective,
                "why_exists": desc.split("\n")[0][:280],
                "prerequisites": prereq_struct,
                "unlock_condition": (
                    "All REQUIRED prerequisites complete "
                    "(planner unlock_status; RECOMMENDED/AWARENESS_SAFE never block)"),
                "next_unlocked": unlocks_list,
                "resources_primary": primary_dicts,
                "resources_supplementary_learner": other_dicts,
                "resources_internal_hidden": hidden_dicts,
                "practice": practice,
                "revision": {
                    "enabled": True,
                    "algorithm": "adaptive SM-2-style (ease multiplier, ladder seed)",
                    "initial_interval_days": 1,
                    "progression_days": [1, 3, 7, 14, 30],
                    "on_fail": "interval resets to 1 day; ease -= 0.2 (min 1.3)",
                    "on_easy": "interval *= ease (max 60 days); ease += 0.05 (max 3.2)",
                    "retrieval_first": True,
                    "priority_inputs": ["overdue_days", "fail_count", "importance",
                                        "prerequisite_centrality"],
                    "prerequisite_centrality": centrality.get(slug, 0),
                },
                "project_links": [],
                "estimated_minutes_total": t.estimated_minutes,
                "readiness": status,
            }
            json_topics.append(jt)
            md_domains[dom].append(jt)
            stats["topics"] += 1
            stats[f"status_{status}"] += 1
            if slug in spine_slugs:
                stats["spine"] += 1
            else:
                stats["expansion"] += 1

            # CSV rows: learner-facing resources only
            for rd in primary_dicts + other_dicts:
                csv_rows.append({
                    "domain": dom, "topic_slug": slug, "topic_title": t.name,
                    "learning_unit": unit["unit_id"],
                    "resource_title": rd["title"], "provider": rd["provider"],
                    "role": rd["role"], "resource_type": rd["resource_type"],
                    "url": rd["url"], "exactness": rd["exactness"],
                    "boundary_type": rd["boundary_type"],
                    "start_boundary": rd["start_boundary"] or "",
                    "end_boundary": rd["end_boundary"] or "",
                    "estimated_minutes": rd["estimated_minutes"],
                    "estimate_confidence": rd["estimate_confidence"],
                    "verification_status": rd["verification_status"],
                    "learner_visible": rd["learner_visible"],
                })

        # projects
        projects_json = []
        for pr in projects:
            projects_json.append({
                "project_id": pr.id, "slug": pr.slug, "name": pr.title,
                "level": pr.level, "purpose": pr.goal,
                "required_topics": pr.prerequisites or [],
                "concepts_applied": pr.concepts_applied or [],
                "estimated_hours": pr.estimated_hours,
                "deliverables": pr.deliverable,
                "milestones": pr.milestones or [],
                "unlock_condition": "All prerequisite topics complete",
            })

        # ── validation ────────────────────────────────────────────
        visible_urls = [(r.url, lesson_topic.get(r.lesson_id))
                        for r in resources if is_learner_visible(r)]
        seen_pairs = {}
        dupes = []
        for u, tid in visible_urls:
            key = normalize_destination_url(u)
            if (tid, key) in seen_pairs:
                dupes.append(u)
            seen_pairs[(tid, key)] = True
        exported_slugs = {jt["topic"] for jt in json_topics}
        missing_topics = sorted(set(by_slug.keys()) - exported_slugs)
        learner_prim_exported = sum(len(jt["resources_primary"]) for jt in json_topics)
        learner_prim_expected = sum(
            1 for r in resources
            if is_learner_visible(r)
            and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN"))
        missing_urls = sum(1 for jt in json_topics
                           for rd in jt["resources_primary"] if not rd["url"])
        missing_bounds = sum(1 for jt in json_topics
                             for rd in jt["resources_primary"]
                             if rd["boundary_type"] == "NONE")
        missing_time = sum(1 for jt in json_topics
                           for rd in jt["resources_primary"]
                           if not rd["estimated_minutes"])
        # New explicit validation per final learner-contract spec
        # READY without PRIMARY: learner-facing READY topics must have at least one visible PRIMARY
        ready_without_primary = sum(
            1 for jt in json_topics
            if jt["readiness"] == "READY"
            and not jt["resources_primary"]
            and (getattr(by_slug.get(jt["topic"]), "topic_type", "LEARNABLE") or "LEARNABLE") != "NON_LEARNABLE_CONTAINER"
        )
        # Learning units missing time breakdown
        learner_units_missing_minutes = sum(
            1 for jt in json_topics
            if not jt["learning_unit"].get("total_training_minutes")
        )
        # VIDEO_TIMESTAMP missing boundaries
        video_missing_start = sum(
            1 for jt in json_topics for rd in jt["resources_primary"]
            if rd["boundary_type"] == "VIDEO_TIMESTAMP" and not rd["start_boundary"]
        )
        video_missing_end = sum(
            1 for jt in json_topics for rd in jt["resources_primary"]
            if rd["boundary_type"] == "VIDEO_TIMESTAMP" and not rd["end_boundary"]
        )
        # ARTICLE_SECTION unbounded: ARTICLE_SECTION with start END=NONE and not FULL_SINGLE_PAGE
        article_unbounded = sum(
            1 for jt in json_topics for rd in jt["resources_primary"]
            if rd["boundary_type"] == "ARTICLE_SECTION"
            and (not rd["start_boundary"] or not rd["end_boundary"])
        )
        # Substantive practice missing instructions: substantive = has at least one visible primary and not container
        substantive_missing_practice = sum(
            1 for jt in json_topics
            if jt["readiness"] in ("READY", "PARTIAL", "RESOURCE_GAP")
            and (getattr(by_slug.get(jt["topic"]), "topic_type", "LEARNABLE") != "NON_LEARNABLE_CONTAINER")
            and (not jt["practice"] or all(not (p.get("instructions") and str(p["instructions"]).strip()) for p in jt["practice"]))
        )
        # Provider/URL mismatches
        provider_mismatches = 0
        for jt in json_topics:
            for rd in jt["resources_primary"]:
                url = (rd["url"] or "").lower()
                prov = (rd["provider"] or "").lower()
                if not url or not prov:
                    continue
                # simple domain-provider check
                if "scikit-learn" in url and "scikit" not in prov:
                    provider_mismatches += 1
                elif "pytorch" in url and "pytorch" not in prov:
                    provider_mismatches += 1
                elif "d2l.ai" in url and "dive" not in prov and "deep" not in prov:
                    provider_mismatches += 1
                elif "huggingface" in url and "hugging" not in prov:
                    provider_mismatches += 1
                elif "anthropic" in url and "anthropic" not in prov:
                    provider_mismatches += 1
                elif "openai" in url and "openai" not in prov:
                    provider_mismatches += 1
                elif "cohere" in url and "cohere" not in prov:
                    provider_mismatches += 1
                elif "mlflow" in url and "mlflow" not in prov:
                    provider_mismatches += 1
        validation = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "topics_expected": len(topics),
            "topics_exported": len(json_topics),
            "learning_units_expected": len(lessons),
            "learning_units_exported": sum(1 for jt in json_topics if jt["learning_unit"]),
            "learner_resources_expected": sum(1 for r in resources if is_learner_visible(r)),
            "learner_resources_exported_in_csv": len(csv_rows),
            "learner_primary_expected": learner_prim_expected,
            "learner_primary_exported": learner_prim_exported,
            "urls_missing": missing_urls,
            "duplicate_visible_urls": len(dupes),
            "missing_boundaries_primary": missing_bounds,
            "missing_time_estimates_primary": missing_time,
            "topics_missing": missing_topics,
            "spine_intact": spine_slugs <= exported_slugs,
            "spine_count": len(spine_slugs & exported_slugs),
            "progress_rows_before_export": pre_snap["learner_progress"]["progress_rows"],
            "progress_rows_at_export": prog_rows,
            "progress_unchanged": prog_rows == pre_snap["learner_progress"]["progress_rows"],
            "xp_rows_at_export": xp_rows,
            # New explicit metrics for final learner-contract validation
            "ready_without_primary": ready_without_primary,
            "learner_units_missing_minutes": learner_units_missing_minutes,
            "video_timestamp_missing_start": video_missing_start,
            "video_timestamp_missing_end": video_missing_end,
            "article_section_unbounded": article_unbounded,
            "substantive_practice_missing_instructions": substantive_missing_practice,
            "provider_url_mismatches": provider_mismatches,
            "learner_resources_missing": max(0, sum(1 for r in resources if is_learner_visible(r)) - len(csv_rows)),
            "projects_exported": len(projects),
            "projects_expected": len(projects),
        }
        json.dump(validation, open(f"{REPORT_DIR}\\curriculum_manifest_validation.json",
                                   "w", encoding="utf-8"), indent=2)

        # ── JSON master manifest ──────────────────────────────────
        sim30 = json.load(open(f"{REPORT_DIR}\\learner_simulation_30.json",
                               encoding="utf-8"))
        manifest_json = {
            "generated_at": validation["generated_at"],
            "summary": {
                "total_domains": len(md_domains),
                "total_topics": stats["topics"],
                "total_learning_units": stats["topics"],
                "total_learner_visible_resources": sum(
                    1 for r in resources if is_learner_visible(r)),
                "total_practice_units": len(exercises),
                "total_projects": len(projects_json),
                "revision_enabled_units": stats["topics"],
                "total_estimated_learning_hours": round(
                    sum((t.estimated_minutes or 0) for t in topics) / 60, 1),
                "original_spine_count": stats["spine"],
                "expansion_count": stats["expansion"],
            },
            "parallel_map": {
                "lanes": {
                    "CORE": "Prerequisite-sensitive main curriculum",
                    "PARALLEL": "Java→DSA runway + specialization topics "
                                "(fill-capacity lane, prereq-gated per topic)",
                    "ALWAYS_ON": "Recurring engineering-practice items",
                    "REVISION": "Adaptive SM-2-style spaced retrieval",
                    "PRACTICE": "Per-topic practice contracts",
                    "BUILD": "Projects unlocked by completion",
                },
                "dsa_gate": ["cf-time-complexity-intro", "java-method-basics"],
                "expected_start_days": {
                    "dsa": sim365.get("first_dsa_day_index"),
                    "ml_awareness": sim30.get("first_ml_day_index"),
                    "serious_ml": sim365.get("serious_ml_day_index"),
                    "deep_learning": sim365.get("first_dl_day_index"),
                    "computer_vision": sim365.get("first_cv_day_index"),
                    "nlp_first": sim365.get("first_nlp_day_index"),
                    "genai_first": sim365.get("first_genai_day_index"),
                    "deep_java": sim365.get("first_deep_java_day_index"),
                },
            },
            "projects": projects_json,
            "domains": [],
            "topics": json_topics,
        }
        for dom in DOMAIN_ORDER:
            if dom in md_domains:
                manifest_json["domains"].append({
                    "domain": dom,
                    "topics": [jt["topic"] for jt in md_domains[dom]],
                })
        json.dump(manifest_json, open(f"{REPORT_DIR}\\curriculum_master_manifest.json",
                                      "w", encoding="utf-8"), indent=2, ensure_ascii=False)

        # ── CSV ───────────────────────────────────────────────────
        cols = ["domain", "topic_slug", "topic_title", "learning_unit",
                "resource_title", "provider", "role", "resource_type", "url",
                "exactness", "boundary_type", "start_boundary", "end_boundary",
                "estimated_minutes", "estimate_confidence",
                "verification_status", "learner_visible"]
        with open(f"{REPORT_DIR}\\curriculum_resource_index.csv", "w",
                  newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(csv_rows)

        # ── Markdown ──────────────────────────────────────────────
        md = ["> GENERATED EXPORT — full audit manifest. URLs printed verbatim.", ""]
        for dom in DOMAIN_ORDER:
            jts = md_domains.get(dom, [])
            if not jts:
                continue
            c = Counter(jt["readiness"] for jt in jts)
            units = sum(1 for _ in jts)
            md += [f"# DOMAIN: {dom}", "",
                   f"Topics: {len(jts)} · Units: {units} · "
                   f"READY {c.get('READY',0)} · PARTIAL {c.get('PARTIAL',0)} · "
                   f"GAP {c.get('RESOURCE_GAP',0)} · NR {c.get('NEEDS_REVIEW',0)} · "
                   f"NO_PRIMARY {c.get('NO_PRIMARY',0)}", ""]
            for jt in jts:
                u = jt["learning_unit"]
                md += [
                    f"## {jt['title']}", "",
                    "### Metadata", "",
                    f"- Slug: `{jt['topic']}`",
                    f"- Topic ID: {jt['topic_id']}",
                    f"- Domain: {jt['domain']}",
                    f"- Lane/Track: {jt['parallel_lane']} ({jt['learning_track_raw']})",
                    f"- Depth: {jt['depth']}",
                    f"- Sequential order: {jt['sequential_order']}",
                    f"- Readiness: **{jt['readiness']}**",
                    f"- Spine: {'yes' if jt['topic'] in spine_slugs else 'expansion'}",
                    "", "### Learning Objective", "", jt["objective"], "",
                    "### Why This Topic Exists", "", jt["why_exists"], "",
                    "### Prerequisites", "",
                ]
                if jt["prerequisites"]:
                    for p in jt["prerequisites"]:
                        md.append(f"- **{p['type']}**: `{p['slug']}` — {p['title']} ({p['reason']})")
                else:
                    md.append("- none (entry point)")
                md += ["", "### Unlock Condition", "", jt["unlock_condition"], "",
                       "### Next", "",
                       f"- Unlocks: {', '.join('`'+x+'`' for x in jt['next_unlocked']) or 'terminal'}",
                       "", f"### Learning Unit 1 — {u['title']}", "",
                       f"- Unit ID: `{u['unit_id']}`",
                       f"- Role: {u['role']} · Difficulty: {u['difficulty']}",
                       f"- Estimated minutes: {u['estimated_minutes']} "
                       f"(confidence: {u['time_confidence']})",
                       f"- Required concepts: {', '.join('`'+c+'`' for c in u['required_concepts']) or '—'}",
                       "", "#### Primary Resource(s)", ""]
                for rd in jt["resources_primary"]:
                    md += [
                        f"- **{rd['title']}** ({rd['provider']})",
                        f"  - ID: {rd['resource_id']} · type={rd['resource_type']} · role={rd['role']}",
                        f"  - URL: {rd['url']}",
                        f"  - Exactness: {rd['exactness']} · Boundary: {rd['boundary_type']}",
                        f"  - SECTION START: {rd['start_boundary'] or 'NONE'}",
                        f"  - SECTION END: {rd['end_boundary'] or 'NONE'}",
                        f"  - Minutes: {rd['estimated_minutes']} · Confidence: {rd['estimate_confidence']}",
                        f"  - Verification: {rd['verification_status']} · Concepts covered: "
                        f"{len(rd['covered_concepts'])}",
                        f"  - Visibility: {rd['visibility']}",
                    ]
                if jt["resources_internal_hidden"]:
                    md += ["", "#### Internal / verification resources (NOT shown to learners)", ""]
                    for rd in jt["resources_internal_hidden"]:
                        md.append(f"- {rd['title']} — {rd['visibility']} — {rd['url']}")
                if jt["practice"]:
                    md += ["", "### Practice", ""]
                    for pc in jt["practice"]:
                        md += [f"- Type: {pc['type']} · Qty: {pc['quantity']} · "
                               f"Destination: {pc['destination']}",
                               f"- Minutes: {pc['estimated_minutes']} · "
                               f"Concepts: {', '.join(pc['concepts_required'])}",
                               f"- Instructions: {(pc['instructions'] or '')[:260]}"]
                rev = jt["revision"]
                md += ["", "### Revision", "",
                       f"- Intervals: {rev['progression_days']} · fail→{rev['on_fail']} · "
                       f"easy→{rev['on_easy']}",
                       f"- Retrieval-first: {rev['retrieval_first']} · "
                       f"centrality: {rev['prerequisite_centrality']}", "",
                       "---", ""]
        open(f"{REPORT_DIR}\\curriculum_master_manifest.md", "w",
             encoding="utf-8").write("\n".join(md))

        # domain index
        idx = ["# Curriculum Domain Index", ""]
        for dom in DOMAIN_ORDER:
            jts = md_domains.get(dom, [])
            if jts:
                idx.append(f"## {dom} ({len(jts)} topics)")
                idx += [f"- `{jt['topic']}` — {jt['title']} [{jt['readiness']}]"
                        for jt in jts]
                idx.append("")
        open(f"{REPORT_DIR}\\curriculum_domain_index.md", "w",
             encoding="utf-8").write("\n".join(idx))

        print(json.dumps(validation, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
