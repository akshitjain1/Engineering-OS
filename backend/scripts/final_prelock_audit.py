"""FINAL PRE-LOCK AUDIT — read-only verification + minimal fixes."""
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
        projects = list(db.query(EngineeringProject).all()) if hasattr(EngineeringProject, "query") else []

        # indexes
        lesson_topic = {l.id: l.topic_id for l in lessons}
        res_by_topic = {}
        for r in db.query(CurriculumResource).all():
            tid = lesson_topic.get(r.lesson_id)
            if tid is not None:
                r.learner_visible = (r.learner_visible is not False)
        for r in db.query(CurriculumResource).all():
            tid = lesson_topic.get(r.lesson_id)
            if tid is not None:
                pass  # we'll use in-memory

        # 1. READY + NO PRIMARY
        ready_no_primary = []
        for t in db.query(CurriculumTopic).all():
            slug = t.slug
            primaries = [r for r in db.query(CurriculumResource).filter(CurriculumResource.lesson_id.in_(
                [l.id for l in db.query(CurriculumLesson).filter(CurriculumLesson.topic_id==t.id).all()])
            ) if is_learner_visible(r) and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN")]
            # simple readiness heuristic
            from app.content.learner_visibility import is_learner_visible
            # simplified readiness: if it has learner-visible PRIMARY → READY candidate
            pass

    finally:
        db.close()
    return results

if __name__ == "__main__":
    print("audit scaffold ready")