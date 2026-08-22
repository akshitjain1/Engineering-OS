"""Polish pass: sections for MULTI_TOPIC, practice contracts for expansion tracks, broken URL fixes."""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

from sqlalchemy.orm import Session, selectinload

from app.content.verification import EXACTNESS_EXACT, EXACTNESS_MULTI_TOPIC, VERIFICATION_NEEDS_REVIEW
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic, LessonExercise

BROKEN_FIXES = {
    "cf-space-complexity-primary": "https://www.geeksforgeeks.org/space-complexity-in-data-structure/",
    "dsa-big-o-learn-exact": "https://www.geeksforgeeks.org/analysis-algorithms-big-o-analysis/",
    "dsa-array-insert-delete-learn-exact": "https://www.geeksforgeeks.org/insertion-deletion-array/",
    "dsa-singly-linked-list-learn-exact": "https://www.geeksforgeeks.org/linked-list-set-1-introduction/",
    "dsa-binary-search-boundaries-learn-exact": "https://www.geeksforgeeks.org/upper-bound-and-lower-bound/",
    "genai-eval-primary": "https://platform.openai.com/docs/guides/evals",
}

PRACTICE_DOMAINS = {
    "web": ("OFFICIAL_EXERCISE", "https://developer.mozilla.org/", 2),
    "python": ("LOCAL_IDE", "local", 2),
    "backend": ("LOCAL_IDE", "local", 2),
    "ml": ("LOCAL_IDE", "local", 2),
    "data-science": ("LOCAL_IDE", "local", 2),
    "mathematics": ("OFFICIAL_EXERCISE", "https://www.khanacademy.org/", 2),
}


def ensure_sections(db: Session) -> int:
    n = 0
    rows = db.query(CurriculumResource).filter(
        CurriculumResource.role.in_(["PRIMARY", "PRIMARY_LEARN"])
    ).all()
    for r in rows:
        if r.section:
            continue
        url = r.url or ""
        parsed = urlparse(url)
        frag = (parsed.fragment or "").strip()
        path = (parsed.path or "").rstrip("/").split("/")[-1]
        section = frag or path or (r.title or "")[:80]
        if section:
            r.section = section[:200]
            if (r.exactness or "") in ("", None, "COLLECTION") and "playlist" not in url:
                # documentation hubs with section become MULTI_TOPIC navigable
                if any(h in url for h in ("github.com", "khanacademy", "tutorial/index", "docs.python.org/3/tutorial/index")):
                    r.exactness = EXACTNESS_MULTI_TOPIC
                elif (r.exactness or "") == EXACTNESS_MULTI_TOPIC or "primer" in url or "modules/" in url:
                    r.exactness = EXACTNESS_MULTI_TOPIC
            n += 1
    db.flush()
    return n


def fix_broken(db: Session) -> int:
    n = 0
    for slug, url in BROKEN_FIXES.items():
        row = db.query(CurriculumResource).filter(CurriculumResource.slug == slug).first()
        if not row:
            continue
        row.url = url
        row.verification_status = VERIFICATION_NEEDS_REVIEW
        row.required_concepts_covered = []
        row.last_verified_at = datetime.now(timezone.utc).isoformat()
        n += 1
    db.flush()
    return n


def enrich_expansion_practice(db: Session) -> dict[str, int]:
    updated = 0
    created = 0
    topics = (
        db.query(CurriculumTopic)
        .options(selectinload(CurriculumTopic.lessons).selectinload(CurriculumLesson.exercises))
        .filter(CurriculumTopic.domain_key.in_(list(PRACTICE_DOMAINS.keys())))
        .all()
    )
    for topic in topics:
        dest_type, dest_url, qty = PRACTICE_DOMAINS[topic.domain_key]
        instructions = (
            f"Complete {qty} concrete exercises for: {topic.name}. "
            f"DESTINATION: {dest_type}. EXPECTED: demonstrable outputs matching the topic objective."
        )
        for les in topic.lessons or []:
            if les.exercises:
                ex = les.exercises[0]
                if ex.destination_type and ex.quantity:
                    continue
                ex.destination_type = dest_type
                ex.destination_url = dest_url
                ex.quantity = qty
                ex.practice_instructions = instructions
                ex.concepts_required = []
                updated += 1
            else:
                db.add(
                    LessonExercise(
                        slug=f"{topic.slug}-practice",
                        title=f"Practice: {topic.name}",
                        description=instructions,
                        lesson_id=les.id,
                        exercise_type="CODING",
                        destination_type=dest_type,
                        destination_url=dest_url,
                        quantity=qty,
                        practice_instructions=instructions,
                        concepts_required=[],
                    )
                )
                created += 1
    db.flush()
    return {"updated": updated, "created": created}


def demote_collection_primaries_with_section(db: Session) -> int:
    """If primary was COLLECTION_ONLY but now has section, allow MULTI_TOPIC navigation."""
    n = 0
    rows = db.query(CurriculumResource).filter(
        CurriculumResource.role.in_(["PRIMARY", "PRIMARY_LEARN"]),
        CurriculumResource.verification_status == "COLLECTION_ONLY",
    ).all()
    for r in rows:
        if r.section and not any(x in (r.url or "") for x in ("playlist", "/tag/")):
            r.exactness = EXACTNESS_MULTI_TOPIC
            r.verification_status = VERIFICATION_NEEDS_REVIEW
            n += 1
    db.flush()
    return n
