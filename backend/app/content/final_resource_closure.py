"""Apply the six final resource decisions and fill empty learner instructions."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic


MAPPINGS: dict[str, dict[str, Any]] = {
    "ml-classification": {"title": "Decision and Classification Trees, Clearly Explained!!!", "provider": "StatQuest with Josh Starmer", "url": "https://www.youtube.com/watch?v=_L39rN6gz7Y", "resource_type": "youtube_video", "boundary_type": "VIDEO_TIMESTAMP", "start": "00:18", "end": "15:38", "video_id": "_L39rN6gz7Y", "instruction": "Watch 00:18–15:38. Focus on how a classification tree turns feature-based questions into class predictions, how Gini impurity guides splitting, and why trees can overfit. After watching, explain the difference between an internal node and a leaf and why the split quality matters."},
    "ml-decision-trees": {"title": "Decision and Classification Trees, Clearly Explained!!!", "provider": "StatQuest with Josh Starmer", "url": "https://www.youtube.com/watch?v=_L39rN6gz7Y", "resource_type": "youtube_video", "boundary_type": "VIDEO_TIMESTAMP", "start": "00:18", "end": "15:38", "video_id": "_L39rN6gz7Y", "instruction": "Watch 00:18–15:38. Learn how a decision tree is built from the root, how candidate splits are evaluated using impurity, how branches and leaves are created, how predictions are made, and why unrestricted trees overfit."},
    "ml-ensemble-learning": {"title": "StatQuest: Random Forests Part 1 - Building, Using and Evaluating", "provider": "StatQuest with Josh Starmer", "url": "https://www.youtube.com/watch?v=J4Wdy0Wc_xQ", "resource_type": "youtube_video", "boundary_type": "VIDEO_TIMESTAMP", "start": "00:31", "end": "08:34", "video_id": "J4Wdy0Wc_xQ", "instruction": "Watch 00:31–08:34. Focus on bootstrap samples, random feature selection, building many trees, voting/averaging, bagging, and evaluating a random forest. Be able to explain why combining many varied trees reduces the weaknesses of an individual tree."},
    "genai-vector-databases": {"title": "What is a Vector Database?", "provider": "Pinecone", "url": "https://www.pinecone.io/learn/vector-database/", "resource_type": "article", "boundary_type": "FULL_SINGLE_PAGE", "start": "FULL_SINGLE_PAGE", "end": "FULL_SINGLE_PAGE", "estimated_minutes": 28, "instruction": "Read the complete article. Focus on why embeddings need specialized storage, vector databases versus vector indexes, similarity search, metadata filtering, indexing, ANN, HNSW intuition, and operational capabilities. After reading, explain why an embedding model and a vector database are different components of a RAG system."},
    "math-conditional-probability": {"title": "3.1 Terminology — Introductory Statistics 2e", "provider": "OpenStax", "url": "https://openstax.org/books/introductory-statistics-2e/pages/3-1-terminology", "resource_type": "documentation", "boundary_type": "ARTICLE_SECTION", "start": "Conditional Probability of A GIVEN B", "end": "Conditional Probability of A GIVEN B", "instruction": "Read the conditional-probability section and worked example. Focus on the idea that conditioning reduces the sample space. Be able to compute P(A|B) = P(A AND B) / P(B) and explain what the condition B changes."},
    "math-expectation-variance": {"title": "4.2 Mean or Expected Value and Standard Deviation — Introductory Statistics 2e", "provider": "OpenStax", "url": "https://openstax.org/books/introductory-statistics-2e/pages/4-2-mean-or-expected-value-and-standard-deviation", "resource_type": "documentation", "boundary_type": "FULL_SINGLE_PAGE", "start": "FULL_SINGLE_PAGE", "end": "FULL_SINGLE_PAGE", "instruction": "Read the page. Focus on expected value or mean of a discrete random variable, variance, standard deviation, and interpreting expected value as a long-run average. Be able to calculate E(X), variance, and standard deviation for a small discrete probability distribution."},
}


def _primary(db: Session, slug: str) -> tuple[CurriculumTopic, CurriculumResource]:
    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
    if not topic:
        raise ValueError(f"Missing topic: {slug}")
    lesson = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).first()
    row = db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id, CurriculumResource.role == "PRIMARY", CurriculumResource.learner_visible.is_(True)).first() if lesson else None
    if not row:
        raise ValueError(f"Missing learner-visible PRIMARY: {slug}")
    return topic, row


def _instruction(row: CurriculumResource, topic: CurriculumTopic) -> str | None:
    concept = topic.name or row.title or row.provider or "the declared topic"
    boundary = row.section or row.start_boundary or row.title or "the declared section"
    if row.boundary_type == "VIDEO_TIMESTAMP":
        start = row.start_boundary or row.start_timestamp or "the start"
        end = row.end_boundary or row.end_timestamp or "the end"
        return f"Watch {start}–{end}. Focus on {concept}. After watching, explain the main idea and one concrete retrieval target."
    if row.boundary_type in {"ARTICLE_SECTION", "SECTION"}:
        return f"Read {boundary}. Focus on {concept}. After reading, explain the main idea and one concrete retrieval target."
    if row.boundary_type == "FULL_SINGLE_PAGE":
        return f"Complete this page. Focus on {concept}. Be able to explain the main idea and one concrete retrieval target."
    return None


def apply_closure(db: Session, *, commit: bool = True) -> dict[str, Any]:
    changed, already_correct, created, instructions_added, review = [], [], [], [], []
    for slug, spec in MAPPINGS.items():
        topic, row = _primary(db, slug)
        before = {"slug": row.slug, "title": row.title, "provider": row.provider, "url": row.url, "role": row.role}
        if before["url"] == spec["url"] and before["title"] == spec["title"]:
            already_correct.append(slug)
        elif not db.query(CurriculumResource).filter(CurriculumResource.slug == f"{row.slug}-legacy-reference").first():
            db.add(CurriculumResource(slug=f"{row.slug}-legacy-reference", title=row.title, url=row.url, resource_type=row.resource_type, provider=row.provider, lesson_id=row.lesson_id, role="REFERENCE", learner_visible=False, visibility_class="INTERNAL", section=row.section, start_boundary=row.start_boundary, end_boundary=row.end_boundary, boundary_type=row.boundary_type, description=row.description))
            created.append(f"{row.slug}-legacy-reference")
        row.title, row.provider, row.url, row.resource_type = spec["title"], spec["provider"], spec["url"], spec["resource_type"]
        row.role, row.learner_visible, row.visibility_class = "PRIMARY", True, "LEARNER"
        row.boundary_type, row.start_boundary, row.end_boundary = spec["boundary_type"], spec["start"], spec["end"]
        row.section, row.video_id = spec["start"], spec.get("video_id")
        row.end_timestamp, row.start_timestamp = spec["end"], spec["start"]
        row.estimated_minutes = spec.get("estimated_minutes", row.estimated_minutes)
        row.description, row.exactness = spec["instruction"], "EXACT"
        changed.append({"topic": topic.slug, "old": before, "new": {"title": row.title, "provider": row.provider, "url": row.url, "boundary": row.section}})
    for row in db.query(CurriculumResource).filter(CurriculumResource.role == "PRIMARY", CurriculumResource.learner_visible.is_(True)).all():
        if not row.description:
            topic = row.lesson.topic if row.lesson else None
            instruction = _instruction(row, topic) if topic else None
            if instruction:
                row.description = instruction
                instructions_added.append(row.slug)
            else:
                review.append(row.lesson.topic.slug if row.lesson and row.lesson.topic else row.slug)
    if commit:
        db.commit()
    return {"changed": changed, "already_correct": already_correct, "resources_created": created, "learner_instructions_added": instructions_added, "needs_instruction_review": review}