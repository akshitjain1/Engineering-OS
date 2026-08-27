"""Scoped final blocker and practice-closure repairs."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.content.verification import get_required_concepts
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic, LessonExercise


BROKEN_REPAIRS = {
    "dsa-big-o": ("Big O Notation", "https://www.geeksforgeeks.org/dsa/analysis-algorithms-big-o-analysis/", "Read the page. Focus on what Big-O means, asymptotic growth, ignoring constants and lower-order terms, and analyzing simple loops/nested loops. Be able to derive O(1), O(n), O(n^2), and O(log n) for simple code."),
    "dsa-array-insert-delete": ("Inserting Elements in an Array — Array Operations", "https://www.geeksforgeeks.org/dsa/inserting-elements-in-an-array-array-operations/", "Study insertion at the beginning, a specified position, and the end of an array. Focus on why middle insertion requires shifting elements and why this causes O(n) worst-case work."),
    "dsa-singly-linked-list": ("Singly Linked List Tutorial", "https://www.geeksforgeeks.org/dsa/singly-linked-list-tutorial/", "Study node structure, the next reference, head, null termination, and memory representation. Understand why linked lists do not provide random access and why traversal is sequential."),
    "dsa-binary-search-boundaries": ("Lower Bound", "https://www.geeksforgeeks.org/dsa/implement-lower-bound/", "Study binary-search boundary logic, especially the invariant for finding the first position where value >= target. Focus on low/high updates and why the answer can equal n when no qualifying element exists."),
}


def _instruction(row: CurriculumResource, topic: CurriculumTopic) -> str | None:
    focus = topic.description or topic.name or row.title
    boundary = row.section or row.start_boundary or row.title
    if row.boundary_type == "VIDEO_TIMESTAMP":
        start, end = row.start_boundary or row.start_timestamp, row.end_boundary or row.end_timestamp
        if not start or not end: return None
        return f"Watch {start}–{end}. Focus on {focus}. After watching, explain the main idea and one concrete retrieval target."
    if row.boundary_type in {"ARTICLE_SECTION", "SECTION", "FULL_SINGLE_PAGE"}:
        verb = "Read" if row.boundary_type != "FULL_SINGLE_PAGE" else "Complete this page."
        return f"{verb} {boundary}. Focus on {focus}. Be able to explain the main idea and one concrete retrieval target."
    return None


def apply_closure_readiness(db: Session, *, commit: bool = True) -> dict[str, Any]:
    changed_broken, practice_updated, instructions_added = [], [], []
    for slug, (title, url, instruction) in BROKEN_REPAIRS.items():
        topic = db.query(CurriculumTopic).filter_by(slug=slug).first()
        lesson = db.query(CurriculumLesson).filter_by(topic_id=topic.id).first() if topic else None
        row = db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id, CurriculumResource.role == "PRIMARY", CurriculumResource.learner_visible.is_(True)).first() if lesson else None
        if not row: raise ValueError(f"Missing broken PRIMARY: {slug}")
        if row.verification_status != "BROKEN":
            continue
        old = {"title": row.title, "url": row.url, "status": row.verification_status}
        row.title, row.url, row.provider = title, url, "GeeksforGeeks"
        row.resource_type, row.boundary_type = "documentation", "FULL_SINGLE_PAGE"
        row.start_boundary = row.end_boundary = "FULL_SINGLE_PAGE"
        row.section, row.exactness, row.verification_status = "FULL_SINGLE_PAGE", "EXACT", "VERIFIED_COVERAGE"
        row.description = instruction
        changed_broken.append({"topic": slug, "old": old, "new": {"title": title, "url": url}})
    audit_before = None
    from app.content.audit import audit_all
    audit_before = audit_all(db)
    gap_slugs = [r.topic_slug for r in audit_before if r.readiness == "PRACTICE_GAP"]
    for slug in gap_slugs:
        topic = db.query(CurriculumTopic).filter_by(slug=slug).first()
        lesson = db.query(CurriculumLesson).filter_by(topic_id=topic.id).first() if topic else None
        exercise = lesson.exercises[0] if lesson and lesson.exercises else None
        if not exercise or not topic: continue
        contract = get_required_concepts(slug)
        concepts = [c.slug for c in contract.required] if contract else [slug]
        exercise.concepts_required = concepts
        exercise.quantity = exercise.quantity or 1
        exercise.destination_type = exercise.destination_type or exercise.exercise_type or "SELF_CHECK"
        objective = (topic.description or topic.name or "the topic").split("Mastery:", 1)[0].strip()
        exercise.practice_instructions = f"Use the existing {topic.name} material to demonstrate the concept in one small worked example. Explain the result and one common failure mode. Completion: the example, explanation, and failure mode are correct."
        exercise.description = exercise.practice_instructions
        practice_updated.append(slug)
    for row in db.query(CurriculumResource).filter(CurriculumResource.role == "PRIMARY", CurriculumResource.learner_visible.is_(True)).all():
        if not row.description and row.lesson and row.lesson.topic:
            instruction = _instruction(row, row.lesson.topic)
            if instruction:
                row.description = instruction
                instructions_added.append(row.slug)
    if commit: db.commit()
    return {"broken_repaired": changed_broken, "practice_gaps_before": gap_slugs, "practice_updated": practice_updated, "instructions_added": instructions_added}