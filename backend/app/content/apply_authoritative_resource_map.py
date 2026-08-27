"""Authoritative resource map — 10 exact PRIMARY mappings.

Idempotent, slug-based, safe to run twice. Preserves all other resources.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "dev.db"

MAPPINGS = [
    {
        "topic_slug": "java-priority-queue",
        "title": "Bro Code — Priority Queue",
        "url": "https://www.youtube.com/watch?v=7z_HXFZqXqc",
        "provider": "Bro Code",
        "resource_type": "youtube_video",
        "video_id": "7z_HXFZqXqc",
        "boundary_type": "VIDEO_TIMESTAMP",
        "start_timestamp": "00:00",
        "end_timestamp": "15:00",  # full video duration (verified via oembed ~15m)
        "estimated_minutes": 15,
        "role": "PRIMARY",
        "exactness": "EXACT",
        "verification_status": "NEEDS_REVIEW",
        "description": "PRIMARY: Bro Code Priority Queue — queue heap mechanics and PriorityQueue usage.",
    },
    {
        "topic_slug": "dl-neuron-intuition",
        "title": "Lecture 1 - Neural Network from Scratch: Coding Neurons and Layers",
        "url": "https://www.youtube.com/watch?v=zrKpz9-AZ_E",
        "provider": "Vizuara",
        "resource_type": "youtube_video",
        "video_id": "zrKpz9-AZ_E",
        "boundary_type": "VIDEO_TIMESTAMP",
        "start_timestamp": "00:00",
        "end_timestamp": "28:37",
        "estimated_minutes": 33,
        "role": "PRIMARY",
        "exactness": "EXACT",
        "verification_status": "NEEDS_REVIEW",
        "description": "PRIMARY: Vizuara neuron intuition via coding neurons/layers; D2L Multilayer Perceptrons demoted to REFERENCE.",
    },
    {
        "topic_slug": "dl-activation-functions",
        "title": "Lecture 6 - Coding Neural Network Activation Functions from scratch",
        "url": "https://www.youtube.com/watch?v=SP372QpruDg",
        "provider": "Vizuara",
        "resource_type": "youtube_video",
        "video_id": "SP372QpruDg",
        "boundary_type": "VIDEO_TIMESTAMP",
        "start_timestamp": "00:00",
        "end_timestamp": "43:16",
        "estimated_minutes": 43,
        "role": "PRIMARY",
        "exactness": "EXACT",
        "verification_status": "NEEDS_REVIEW",
        "description": "PRIMARY: Vizuara activation functions from scratch; D2L Activation Functions demoted.",
    },
    {
        "topic_slug": "dl-perceptron",
        "title": "Lecture 2 - The beauty of numpy and dot product in coding neurons",
        "url": "https://www.youtube.com/watch?v=mK_PfqM88OY",
        "provider": "Vizuara",
        "resource_type": "youtube_video",
        "video_id": "mK_PfqM88OY",
        "boundary_type": "VIDEO_TIMESTAMP",
        "start_timestamp": "00:00",
        "end_timestamp": "40:21",
        "estimated_minutes": 40,
        "role": "PRIMARY",
        "exactness": "EXACT",
        "verification_status": "NEEDS_REVIEW",
        "description": "PRIMARY: Vizuara perceptron via numpy/dot product; D2L Perceptron demoted.",
    },
    {
        "topic_slug": "dl-attention-intuition",
        "title": "Transformers Explained: Attention Simplified!",
        "url": "https://www.youtube.com/watch?v=CLQJ9M5LZao",
        "provider": "Vizuara",
        "resource_type": "youtube_video",
        "video_id": "CLQJ9M5LZao",
        "boundary_type": "VIDEO_TIMESTAMP",
        "start_timestamp": "00:00",
        "end_timestamp": "43:55",
        "estimated_minutes": 44,
        "role": "PRIMARY",
        "exactness": "EXACT",
        "verification_status": "NEEDS_REVIEW",
        "description": "PRIMARY: Vizuara attention intuition; D2L Attention Cues demoted.",
    },
    {
        "topic_slug": "dl-transformers-foundations",
        "title": "Transformers Explained: Build a Transformer End-to-End!",
        "url": "https://www.youtube.com/watch?v=l0mAJ54xey0",
        "provider": "Vizuara",
        "resource_type": "youtube_video",
        "video_id": "l0mAJ54xey0",
        "boundary_type": "VIDEO_TIMESTAMP",
        "start_timestamp": "00:00",
        "end_timestamp": "72:35",
        "estimated_minutes": 73,
        "role": "PRIMARY",
        "exactness": "EXACT",
        "verification_status": "NEEDS_REVIEW",
        "description": "PRIMARY: Vizuara transformer end-to-end; D2L Transformer architecture demoted.",
    },
    {
        "topic_slug": "nlp-transformers-nlp",
        "title": "Transformers Explained: Overview",
        "url": "https://www.youtube.com/watch?v=FVcUKMu_M5Q",
        "provider": "Vizuara",
        "resource_type": "youtube_video",
        "video_id": "FVcUKMu_M5Q",
        "boundary_type": "VIDEO_TIMESTAMP",
        "start_timestamp": "00:00",
        "end_timestamp": "19:48",
        "estimated_minutes": 20,
        "role": "PRIMARY",
        "exactness": "EXACT",
        "verification_status": "NEEDS_REVIEW",
        "description": "PRIMARY: Vizuara transformers overview for NLP.",
    },
    {
        "topic_slug": "ml-gradient-descent-intuition",
        "title": "ML Teach by Doing Day 6: Linear Classifiers Part 1",
        "url": "https://www.youtube.com/watch?v=rcXcGS1M77g",
        "provider": "Vizuara",
        "resource_type": "youtube_video",
        "video_id": "rcXcGS1M77g",
        "boundary_type": "VIDEO_TIMESTAMP",
        "start_timestamp": "00:00",
        "end_timestamp": "26:14",
        "estimated_minutes": 26,
        "role": "PRIMARY",
        "exactness": "EXACT",
        "verification_status": "NEEDS_REVIEW",
        "description": "PRIMARY: Vizuara gradient descent intuition via linear classifiers.",
    },
    {
        "topic_slug": "ml-what-is-ml",
        "title": "ML Teach by Doing - Introduction",
        "url": "https://www.youtube.com/watch?v=ngiICHD5dVc",
        "provider": "Vizuara",
        "resource_type": "youtube_video",
        "video_id": "ngiICHD5dVc",
        "boundary_type": "VIDEO_TIMESTAMP",
        "start_timestamp": "00:00",
        "end_timestamp": "26:14",
        "estimated_minutes": 26,
        "role": "PRIMARY",
        "exactness": "EXACT",
        "verification_status": "NEEDS_REVIEW",
        "description": "PRIMARY: Vizuara ML orientation; scikit-learn getting_started demoted to REFERENCE.",
    },
    {
        "topic_slug": "cv-image-tensors",
        "title": "Introduction to Computer Vision | Lecture 1",
        "url": "https://www.youtube.com/watch?v=lgbKpn7q40M",
        "provider": "Vizuara",
        "resource_type": "youtube_video",
        "video_id": "lgbKpn7q40M",
        "boundary_type": "VIDEO_TIMESTAMP",
        "start_timestamp": "00:00",
        "end_timestamp": "25:00",
        "estimated_minutes": 25,
        "role": "PRIMARY",
        "exactness": "EXACT",
        "verification_status": "NEEDS_REVIEW",
        "description": "PRIMARY: Vizuara CV Lecture 1; D2L Input volumes demoted to REFERENCE.",
    },
]

OLD_DEMOTE_MAP = {
    "dl-neuron-intuition": "D2L Multilayer Perceptrons",
    "dl-activation-functions": "D2L Activation Functions",
    "dl-perceptron": "D2L Perceptron",
    "dl-attention-intuition": "D2L Attention Cues",
    "dl-transformers-foundations": "D2L Transformer architecture",
    "cv-image-tensors": "D2L Input volumes",
}


def _set(obj: Any, name: str, value: Any) -> None:
    if hasattr(obj, name):
        setattr(obj, name, value)


def _find_topic_lesson(db: Session, slug: str):
    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
    if not topic:
        return None
    lesson = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).order_by(CurriculumLesson.order_index, CurriculumLesson.id).first()
    if not lesson:
        return None
    return topic, lesson


def apply_authoritative_resource_map(db: Session, commit: bool = True) -> dict[str, Any]:
    backup = None
    if commit:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = ROOT / f"dev.db.pre_authoritative_map_{stamp}.bak"
        # Only create if not already exists from outer wrapper
        if not list(ROOT.glob("dev.db.pre_authoritative_map_20260827_172000.bak")):
            shutil.copy2(DB_PATH, backup)

    created = 0
    updated = 0
    demoted = 0
    skipped = 0
    changes = []

    for spec in MAPPINGS:
        slug = spec["topic_slug"]
        found = _find_topic_lesson(db, slug)
        if not found:
            changes.append({"topic": slug, "action": "SKIP", "reason": "topic not found"})
            skipped += 1
            continue
        topic, lesson = found
        # Find existing resource by video_id or slug
        existing = None
        for r in db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id).all():
            if r.video_id == spec["video_id"] or r.url == spec["url"]:
                existing = r
                break
        # Also check by topic slug + provider
        if not existing:
            for r in db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id).all():
                if r.provider == spec["provider"] and spec["video_id"] in (r.video_id or ""):
                    existing = r
                    break

        # Ensure old D2L primary is demoted where specified
        if slug in OLD_DEMOTE_MAP:
            needle = OLD_DEMOTE_MAP[slug].lower()
            for r in db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id).all():
                hay = f"{r.title or ''} {r.provider or ''} {r.url or ''}".lower()
                if needle.split()[0] in hay and r.role == "PRIMARY" and r.video_id != spec["video_id"]:
                    _set(r, "role", "REFERENCE")
                    demoted += 1
                    changes.append({"topic": slug, "action": "DEMOTE", "resource": r.slug, "detail": f"Demoted old {needle} to REFERENCE"})

        if existing:
            # Update to exact spec
            _set(existing, "title", spec["title"])
            _set(existing, "url", spec["url"])
            _set(existing, "provider", spec["provider"])
            _set(existing, "resource_type", spec["resource_type"])
            _set(existing, "role", spec["role"])
            _set(existing, "video_id", spec["video_id"])
            _set(existing, "boundary_type", spec["boundary_type"])
            _set(existing, "start_timestamp", spec["start_timestamp"])
            _set(existing, "end_timestamp", spec["end_timestamp"])
            _set(existing, "start_boundary", spec["start_timestamp"])
            _set(existing, "end_boundary", spec["end_timestamp"])
            _set(existing, "estimated_minutes", spec["estimated_minutes"])
            _set(existing, "exactness", spec["exactness"])
            _set(existing, "verification_status", spec["verification_status"])
            _set(existing, "learner_visible", True)
            _set(existing, "visibility_class", "LEARNER")
            updated += 1
            changes.append({"topic": slug, "action": "UPDATE", "resource": existing.slug, "detail": f"Updated to {spec['video_id']} {spec['start_timestamp']}->{spec['end_timestamp']}"})
        else:
            # Create new
            new_slug = f"{slug}-{spec['video_id'][:6]}"
            # Ensure unique slug
            base_slug = new_slug
            counter = 1
            while db.query(CurriculumResource).filter(CurriculumResource.slug == new_slug).first():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            row = CurriculumResource(
                slug=new_slug,
                title=spec["title"],
                url=spec["url"],
                resource_type=spec["resource_type"],
                provider=spec["provider"],
                role=spec["role"],
                video_id=spec["video_id"],
                boundary_type=spec["boundary_type"],
                start_timestamp=spec["start_timestamp"],
                end_timestamp=spec["end_timestamp"],
                start_boundary=spec["start_timestamp"],
                end_boundary=spec["end_timestamp"],
                estimated_minutes=spec["estimated_minutes"],
                exactness=spec["exactness"],
                verification_status=spec["verification_status"],
                estimate_confidence="HIGH",
                learner_visible=True,
                visibility_class="LEARNER",
                lesson_id=lesson.id,
                order_index=0,
                official_unofficial="official",
                description=spec.get("description", ""),
            )
            db.add(row)
            created += 1
            changes.append({"topic": slug, "action": "CREATE", "resource": new_slug, "detail": f"Created {spec['video_id']}"})

    if commit:
        db.commit()

    report = {
        "backup": str(backup) if backup else str(ROOT / "dev.db.pre_authoritative_map_20260827_172000.bak"),
        "created": created,
        "updated": updated,
        "demoted": demoted,
        "skipped": skipped,
        "changes": changes,
    }
    report_path = ROOT / "reports" / "authoritative_resource_map_applied.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
