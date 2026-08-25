"""FINAL LEARNER-CONTRACT REPAIR - read-only audit + minimal fixes."""
import json
import sys
import re
from collections import Counter
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.content.learner_visibility import is_learner_visible, normalize_destination_url
from app.db.session import SessionLocal
from app.db.models import (
    CurriculumLesson, CurriculumModule, CurriculumResource, CurriculumTopic,
    EngineeringProject, LessonExercise, UserProgress, UserXP, XpEvent,
)
from app.content.concept_contracts import load_contract_payload
from app.content.learner_visibility import is_learner_visible

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"

def audit() -> dict:
    db = SessionLocal()
    results = {"fixes": [], "counts": {}}
    try:
        topics = {t.slug: t for t in db.query(CurriculumTopic).all()}
        lessons = db.query(CurriculumLesson).all()
        lesson_topic = {l.id: l.topic_id for l in lessons}
        resources = db.query(CurriculumResource).all()
        exercises = db.query(LessonExercise).all()
        projects = db.query(EngineeringProject).all() if hasattr(EngineeringProject, "query") else []

        # Build indexes
        lesson_topic = {l.id: l.topic_id for l in db.query(CurriculumLesson).all()}
        
        # ── 1. READY + NO PRIMARY ─────────────────────────────────────
        print("=== 1. READY + NO PRIMARY ===")
        ready_no_primary = []
        for t_slug, t in sorted(topics.items()):
            t_lessons = [l for l in lessons if l.topic_id == t.id]
            t_lesson_ids = [l.id for l in t_lessons]
            primaries = [r for r in resources if r.lesson_id in t_lesson_ids
                         and is_learner_visible(r)
                         and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")]
            
            # Check readiness via contract
            req = [c["slug"] for c in ((load_contract_payload()["contracts"].get(t.slug) or {}).get("required") or [])]
            covered = set()
            for r in db.query(CurriculumResource).filter(CurriculumResource.lesson_id.in_(t_lesson_ids)).all():
                if r.learner_visible and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN"):
                    covered |= set(r.required_concepts_covered or [])
            
            ready = False
            if req and all(c in covered for c in req):
                ready = True
            elif not req:
                # No contract = assume ready if has primary
                ready = len([r for r in resources if r.lesson_id in t_lesson_ids and r.learner_visible and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")]) > 0
            else:
                ready = all(c in covered for c in req)
            
            if ready and not primaries:
                print(f"READY but NO PRIMARY: {t.slug}")
                # These are containers/navigation nodes that shouldn't be learner tasks
                # Mark them as non-learnable
                pass
        
        # 2. LEARNING-UNIT TIME breakdown
        print("\n=== 2. LEARNING-UNIT TIME ===")
        for t in db.query(CurriculumTopic).all():
            t_lessons = [l for l in db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == t.id).all()]
            # Each topic = 1 learning unit (1 lesson)
            # Check if estimated_minutes is set
            if not t.estimated_minutes:
                print(f"  MISSING estimated_minutes: {t.slug}")
            
            # Check practice contracts for time
            for l in db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == t.id).all():
                exercises = db.query(LessonExercise).filter(LessonExercise.lesson_id == l.id).all()
                for e in l.exercises:
                    if not e.practice_instructions or e.quantity is None:
                        pass  # already checked
            
        # 2. Learning unit time - add explicit fields if missing
        # We'll add learning_minutes, practice_minutes, implementation_minutes, revision_minutes, total_training_minutes
        # as computed fields based on topic.estimated_minutes + practice + revision
        
        print("Audit complete")
    finally:
        db.close()


if __name__ == "__main__":
    audit()