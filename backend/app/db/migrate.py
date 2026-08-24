"""Lightweight SQLite/Postgres column patches for additive fields."""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

QUESTION_COLUMNS = {
    "options": "JSON",
    "last_answer": "TEXT",
    "attempt_count": "INTEGER DEFAULT 0 NOT NULL",
    "last_correct": "BOOLEAN",
    "slug": "VARCHAR(160)",
    "last_attempt_at": "DATETIME",
}

EXERCISE_COLUMNS = {
    "exercise_type": "VARCHAR(20) DEFAULT 'SELF_REFLECTION' NOT NULL",
    "correct_answer": "TEXT",
    "user_answer": "TEXT",
    "user_code": "TEXT",
    "user_explanation": "TEXT",
    "user_complexity": "VARCHAR(20)",
    "evaluated": "BOOLEAN DEFAULT 0",
    "destination_type": "VARCHAR(40)",
    "destination_url": "VARCHAR(500)",
    "quantity": "INTEGER",
    "concepts_required": "JSON",
    "practice_instructions": "TEXT",
}

TOPIC_COLUMNS = {
    "learning_track": "VARCHAR(20) DEFAULT 'CORE' NOT NULL",
    "depth_target": "VARCHAR(30) DEFAULT 'WORKING_KNOWLEDGE' NOT NULL",
    "parallel_eligible": "BOOLEAN DEFAULT 0 NOT NULL",
    "estimated_minutes": "INTEGER",
    "domain_key": "VARCHAR(60)",
}

RESOURCE_EXTRA_COLUMNS = {
    "estimated_minutes": "INTEGER",
    "required_concepts_covered": "JSON",
    "exactness": "VARCHAR(20)",
    "notes": "TEXT",
    "estimate_confidence": "VARCHAR(10)",
    "estimate_method": "VARCHAR(40)",
    "verification_evidence": "TEXT",
    "last_verified_at": "VARCHAR(40)",
    "learner_visible": "BOOLEAN DEFAULT 1",
    "visibility_class": "VARCHAR(40)",
}

TABLE_SLUGS = [
    "curriculum_tracks",
    "curriculum_levels",
    "curriculum_subjects",
    "curriculum_modules",
    "curriculum_topics",
    "curriculum_lessons",
    "curriculum_resources",
    "lesson_questions",
    "lesson_exercises",
]


def _columns(conn, table: str) -> set[str]:
    dialect = conn.dialect.name
    if dialect == "sqlite":
        return {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()}
    rows = conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = :table AND table_schema = current_schema()"
        ),
        {"table": table},
    ).fetchall()
    return {row[0] for row in rows}


def ensure_optional_columns(engine: Engine) -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        if "lesson_questions" in tables:
            existing = _columns(conn, "lesson_questions")
            for name, ddl in QUESTION_COLUMNS.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE lesson_questions ADD COLUMN {name} {ddl}"))
                    existing.add(name)

        if "lesson_exercises" in tables:
            existing = _columns(conn, "lesson_exercises")
            for name, ddl in EXERCISE_COLUMNS.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE lesson_exercises ADD COLUMN {name} {ddl}"))
                    existing.add(name)

        if "assessment_sessions" not in tables:
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS assessment_sessions ("
                    "id INTEGER PRIMARY KEY, "
                    "user_id VARCHAR(50) NOT NULL DEFAULT 'akshit', "
                    "topic_id INTEGER NOT NULL REFERENCES curriculum_topics(id), "
                    "status VARCHAR(20) NOT NULL DEFAULT 'in_progress', "
                    "question_ids JSON, "
                    "current_index INTEGER NOT NULL DEFAULT 0, "
                    "answers JSON, "
                    "started_at DATETIME NOT NULL, "
                    "completed_at DATETIME, "
                    "summary JSON)"
                )
            )
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS ix_assessment_sessions_user_topic "
                     "ON assessment_sessions (user_id, topic_id, id)")
            )

        if "mastery_evidence" in tables:
            existing = _columns(conn, "mastery_evidence")
            if "created_at" not in existing:
                conn.execute(text("ALTER TABLE mastery_evidence ADD COLUMN created_at DATETIME"))
                existing.add("created_at")
            _dedupe_evidence_registers(conn)

        if "curriculum_resources" in tables:
            existing = _columns(conn, "curriculum_resources")
            if "provider" not in existing:
                conn.execute(text("ALTER TABLE curriculum_resources ADD COLUMN provider VARCHAR(100)"))
                existing.add("provider")
            resource_columns = {
                "role": "VARCHAR(20)",
                "section": "VARCHAR(200)",
                "lecture": "VARCHAR(200)",
                "video_id": "VARCHAR(40)",
                "verification_status": "VARCHAR(20) DEFAULT 'UNRESOLVED'",
            }
            for name, ddl in resource_columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE curriculum_resources ADD COLUMN {name} {ddl}"))
                    existing.add(name)
            for name, ddl in RESOURCE_EXTRA_COLUMNS.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE curriculum_resources ADD COLUMN {name} {ddl}"))
                    existing.add(name)

        if "curriculum_topics" in tables:
            existing = _columns(conn, "curriculum_topics")
            for name, ddl in TOPIC_COLUMNS.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE curriculum_topics ADD COLUMN {name} {ddl}"))
                    existing.add(name)

        if "user_study_settings" not in tables:
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS user_study_settings ("
                    "id INTEGER PRIMARY KEY, "
                    "user_id VARCHAR(50) NOT NULL DEFAULT 'akshit', "
                    "weekday_capacity_minutes INTEGER NOT NULL DEFAULT 90, "
                    "weekend_capacity_minutes INTEGER NOT NULL DEFAULT 180, "
                    "timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Kolkata', "
                    "CONSTRAINT uq_user_study_settings UNIQUE (user_id))"
                )
            )
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS ix_user_study_settings_user_id "
                     "ON user_study_settings (user_id)")
            )

        if "engineering_projects" not in tables:
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS engineering_projects ("
                    "id INTEGER PRIMARY KEY, "
                    "slug VARCHAR(160) NOT NULL, "
                    "title VARCHAR(200) NOT NULL, "
                    "goal TEXT, "
                    "level INTEGER NOT NULL DEFAULT 1, "
                    "difficulty VARCHAR(20) NOT NULL DEFAULT 'beginner', "
                    "estimated_hours FLOAT NOT NULL DEFAULT 2.0, "
                    "prerequisites JSON, "
                    "concepts_applied JSON, "
                    "milestones JSON, "
                    "deliverable TEXT, "
                    "order_index INTEGER NOT NULL DEFAULT 0)"
                )
            )
            conn.execute(
                text("CREATE UNIQUE INDEX IF NOT EXISTS ix_engineering_projects_slug "
                     "ON engineering_projects (slug)")
            )

        if "user_project_progress" not in tables:
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS user_project_progress ("
                    "id INTEGER PRIMARY KEY, "
                    "user_id VARCHAR(50) NOT NULL DEFAULT 'akshit', "
                    "project_id INTEGER NOT NULL REFERENCES engineering_projects(id), "
                    "state VARCHAR(20) NOT NULL DEFAULT 'locked', "
                    "started_at DATETIME, "
                    "completed_at DATETIME, "
                    "CONSTRAINT uq_user_project UNIQUE (user_id, project_id))"
                )
            )
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS ix_user_project_progress_user_id "
                     "ON user_project_progress (user_id)")
            )

        for table in TABLE_SLUGS:
            if table not in tables:
                continue
            existing = _columns(conn, table)
            if "slug" not in existing:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN slug VARCHAR(160)"))
                conn.execute(
                    text(f"CREATE UNIQUE INDEX IF NOT EXISTS ix_{table}_slug ON {table} (slug)")
                )

    _backfill_resource_metadata(engine)


def _dedupe_evidence_registers(conn) -> None:
    """Collapse mastery_evidence into one row per (user, topic, source, category).

    Keeps the latest row of each register so mastery reflects current evidence
    rather than cumulative history. Idempotent; safe to run repeatedly.
    """
    for table in ("mastery_evidence",):
        cols = _columns(conn, table)
        if "created_at" not in cols:
            continue
        conn.execute(
            text(
                "DELETE FROM mastery_evidence WHERE id NOT IN ("
                "SELECT MAX(m2.id) FROM mastery_evidence m2 "
                "GROUP BY m2.user_id, m2.topic_slug, m2.source, m2.category)"
            )
        )
    index_names = {
        row[1]
        for row in conn.execute(text("PRAGMA index_list(mastery_evidence)")).fetchall()
    }
    if "ix_mastery_evidence_register" not in index_names:
        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_mastery_evidence_register "
                "ON mastery_evidence (user_id, topic_slug, source, category)"
            )
        )


def _backfill_resource_metadata(engine: Engine) -> None:
    """Populate new resource columns from existing URLs and [ROLE] description tags.

    Does not invent URLs, video IDs, section names, or lecture titles.
    """
    from app.content.resources import (
        extract_role_from_description,
        is_youtube_playlist,
        metadata_from_spec,
        youtube_video_id,
    )
    from app.db.models import CurriculumResource
    from sqlalchemy.orm import Session

    inspector = inspect(engine)
    if "curriculum_resources" not in inspector.get_table_names():
        return
    with Session(engine) as session:
        rows = session.query(CurriculumResource).all()
        changed = False
        for row in rows:
            role_from_desc, cleaned = extract_role_from_description(row.description)
            if role_from_desc and not row.role:
                row.role = role_from_desc
                row.description = cleaned
                changed = True
            meta = metadata_from_spec(
                url=row.url,
                resource_type=row.resource_type,
                role=row.role,
                section=row.section,
                lecture=row.lecture,
                video_id=row.video_id,
                verification_status=row.verification_status,
            )
            if is_youtube_playlist(row.url, row.resource_type):
                meta["video_id"] = None
            elif not row.video_id:
                meta["video_id"] = youtube_video_id(row.url)
            if row.role != meta["role"] and meta["role"]:
                row.role = meta["role"]
                changed = True
            # Never clobber content-verification statuses with URL-only VERIFIED.
            content_statuses = {
                "VERIFIED_COVERAGE",
                "PARTIAL_COVERAGE",
                "COLLECTION_ONLY",
                "BROKEN",
                "NEEDS_REVIEW",
            }
            current_status = (row.verification_status or "").upper()
            if current_status not in content_statuses:
                if row.verification_status != meta["verification_status"]:
                    row.verification_status = meta["verification_status"]
                    changed = True
            if (row.video_id or None) != (meta["video_id"] or None):
                row.video_id = meta["video_id"]
                changed = True
            if getattr(row, "learner_visible", None) is None:
                row.learner_visible = True
                changed = True
            if not getattr(row, "visibility_class", None):
                row.visibility_class = "LEARNER"
                changed = True
        if changed:
            session.commit()
