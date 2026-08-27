"""Apply the authoritative Batch 3 MIT Missing Semester mappings only."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic


TARGETS: dict[str, dict[str, str]] = {
    "cf-shell": {"title": "MIT Missing Semester 2026 — Course Overview + Introduction to the Shell", "url": "https://missing.csail.mit.edu/2026/", "section": "Course Overview + Introduction to the Shell"},
    "cf-command-line": {"title": "MIT Missing Semester 2026 — Introduction to the Shell", "url": "https://missing.csail.mit.edu/2026/01-shell/", "section": "Introduction to the Shell"},
    "cf-filesystem-navigation": {"title": "MIT Missing Semester 2026 — Introduction to the Shell", "url": "https://missing.csail.mit.edu/2026/01-shell/", "section": "Introduction to the Shell"},
    "cf-linux-files": {"title": "MIT Missing Semester 2026 — Introduction to the Shell", "url": "https://missing.csail.mit.edu/2026/01-shell/", "section": "Introduction to the Shell"},
    "cf-pipes": {"title": "MIT Missing Semester 2026 — Introduction to the Shell", "url": "https://missing.csail.mit.edu/2026/01-shell/", "section": "Introduction to the Shell"},
    "cf-redirection": {"title": "MIT Missing Semester 2026 — Introduction to the Shell", "url": "https://missing.csail.mit.edu/2026/01-shell/", "section": "Introduction to the Shell"},
    "cf-grep": {"title": "MIT Missing Semester 2026 — Introduction to the Shell", "url": "https://missing.csail.mit.edu/2026/01-shell/", "section": "Introduction to the Shell"},
    "cf-find": {"title": "MIT Missing Semester 2026 — Introduction to the Shell", "url": "https://missing.csail.mit.edu/2026/01-shell/", "section": "Introduction to the Shell"},
    "cf-linux-permissions": {"title": "MIT Missing Semester 2026 — Command-line Environment", "url": "https://missing.csail.mit.edu/2026/02-environment/", "section": "Files and Permissions"},
    "cf-linux-processes": {"title": "MIT Missing Semester 2026 — Command-line Environment", "url": "https://missing.csail.mit.edu/2026/02-environment/", "section": "Processes / Signals / Job Control"},
}


def _resolve(db: Session, slug: str) -> tuple[CurriculumTopic, CurriculumLesson, list[CurriculumResource]]:
    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
    if not topic:
        raise ValueError(f"Missing topic: {slug}")
    lesson = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).first()
    if not lesson:
        raise ValueError(f"Missing lesson for topic: {slug}")
    rows = db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id).all()
    return topic, lesson, rows


def apply_batch3_mit_shell_mapping(db: Session, *, commit: bool = True) -> dict[str, Any]:
    repaired_at = datetime.now(timezone.utc).isoformat()
    changed = []
    for slug, spec in TARGETS.items():
        topic, lesson, rows = _resolve(db, slug)
        primaries = [row for row in rows if row.role == "PRIMARY" and row.learner_visible]
        target = next((row for row in rows if row.slug == f"{slug}-primary"), None)
        if not target or not primaries:
            raise ValueError(f"Missing target/current PRIMARY for {slug}")
        old = {"slug": primaries[0].slug, "title": primaries[0].title, "url": primaries[0].url, "boundary": primaries[0].section}
        for row in primaries:
            if row is not target:
                row.role = "REFERENCE"
                row.learner_visible = False
                row.visibility_class = "INTERNAL"
        target.title = spec["title"]
        target.url = spec["url"]
        target.provider = "MIT Missing Semester 2026"
        target.resource_type = "documentation"
        target.role = "PRIMARY"
        target.learner_visible = True
        target.visibility_class = "LEARNER"
        target.section = spec["section"]
        target.boundary_type = "ARTICLE_SECTION"
        target.start_boundary = spec["section"]
        target.end_boundary = spec["section"]
        target.exactness = "EXACT"
        target.verification_status = "NEEDS_REVIEW"
        target.notes = "Authoritative Batch 3 mapping supplied by user."
        target.verification_evidence = json.dumps({"repair": "batch3_mit_shell_mapping", "repaired_at": repaired_at})
        changed.append({"topic": topic.slug, "lesson_id": lesson.id, "old_primary": old, "new_primary": {"slug": target.slug, "title": target.title, "url": target.url, "boundary": target.section}})
    if commit:
        db.commit()
    return {"processed": len(changed), "changed": changed}