"""Regenerate the immutable prechange snapshot from REAL database state."""
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import (
    CurriculumTopic,
    CurriculumModule,
    CurriculumSubject,
    CurriculumTrack,
    CurriculumLesson,
    CurriculumResource,
    UserProgress,
    TopicMastery,
    RevisionSchedule,
    XpEvent,
)
from sqlalchemy import func


def main() -> None:
    db = SessionLocal()
    try:
        topics = db.query(CurriculumTopic).all()
        topic_slugs = sorted([t.slug for t in topics if t.slug])

        # Prerequisite edges (topic_slug -> list of prereq slugs/objects)
        prereq_edges = {}
        edge_count = 0
        for t in topics:
            if t.prerequisites:
                prereq_edges[t.slug] = t.prerequisites
                edge_count += len(t.prerequisites)

        resource_count = db.query(CurriculumResource).count()
        lesson_count = db.query(CurriculumLesson).count()

        progress_rows = db.query(UserProgress).all()
        completed_topics = 0
        in_progress_topics = 0
        not_started_topics = 0
        for row in progress_rows:
            state = (row.progress_state or "").lower()
            if state == "mastered":
                completed_topics += 1
            elif state in ("learning", "practicing"):
                in_progress_topics += 1
            else:
                not_started_topics += 1

        mastery_rows = db.query(TopicMastery).count()
        revision_rows = db.query(RevisionSchedule).count()
        overdue = (
            db.query(RevisionSchedule)
            .filter(RevisionSchedule.next_review <= func.now())
            .count()
        )
        xp_events = db.query(XpEvent).count()
        total_xp_row = db.query(func.sum(XpEvent.amount)).scalar()

        tracks = db.query(CurriculumTrack).order_by(CurriculumTrack.order_index).all()
        track_summary = []
        for tr in tracks:
            subjects = db.query(CurriculumSubject).filter(CurriculumSubject.track_id == tr.id).all()
            subject_ids = [s.id for s in subjects]
            modules = (
                db.query(CurriculumModule)
                .filter(CurriculumModule.subject_id.in_(subject_ids))
                .all()
                if subject_ids
                else []
            )
            module_ids = [m.id for m in modules]
            topic_count = (
                db.query(CurriculumTopic)
                .filter(CurriculumTopic.module_id.in_(module_ids))
                .count()
                if module_ids
                else 0
            )
            track_summary.append({"slug": tr.slug, "name": tr.name, "topics": topic_count})

        snapshot = {
            "snapshot_timestamp": datetime.now(timezone.utc).isoformat(),
            "snapshot_purpose": "Immutable pre-change baseline for curriculum intelligence work",
            "counts": {
                "tracks": len(tracks),
                "subjects": len(subject_ids) if tracks else 0,
                "modules": len(
                    set(m.id for m in db.query(CurriculumModule).all())
                ),
                "topics": len(topics),
                "lessons": lesson_count,
                "resources": resource_count,
            },
            "topic_slugs": topic_slugs,
            "prerequisite_edges": prereq_edges,
            "prerequisite_edge_count": edge_count,
            "learner_progress": {
                "progress_rows": len(progress_rows),
                "mastered": completed_topics,
                "learning_or_practicing": in_progress_topics,
                "other_states": not_started_topics,
                "topic_mastery_rows": mastery_rows,
            },
            "revision_state": {
                "revision_schedule_rows": revision_rows,
                "overdue_rows": overdue,
            },
            "xp_history": {
                "xp_event_count": xp_events,
                "total_xp": int(total_xp_row or 0),
            },
            "track_summary": track_summary,
        }

        out_path = r"D:\Akshit Personal OS\backend\reports\final_intelligence_prechange_snapshot.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)

        print("Snapshot written:", out_path)
        print(json.dumps({k: v for k, v in snapshot.items() if k != "topic_slugs" and k != "prerequisite_edges"}, indent=2))
        print("topic_slugs count:", len(topic_slugs))
    finally:
        db.close()


if __name__ == "__main__":
    main()
