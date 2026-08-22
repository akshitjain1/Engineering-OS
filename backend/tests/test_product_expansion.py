"""Product expansion: tracks, capacity planner, projects, resources."""

from __future__ import annotations

from app.content.backfill_tracks import backfill_topic_tracks
from app.content.resources import BROKEN, TRUSTED, VERIFIED, select_resource_for_activity
from app.db.models import (
    CurriculumLesson,
    CurriculumLevel,
    CurriculumModule,
    CurriculumResource,
    CurriculumSubject,
    CurriculumTopic,
    CurriculumTrack,
)
from app.db.session import SessionLocal
from app.learning import projects as projects_svc
from app.learning.planner import (
    TRACK_ALWAYS_ON,
    TRACK_PRIMARY,
    TopicView,
    build_daily_plan,
    track_code_from_learning_track,
)


def _seed_track_topics(db):
    track = CurriculumTrack(slug="eos-test", name="EOS Test", order_index=0)
    level = CurriculumLevel(slug="l0", name="L0", order_index=0)
    db.add_all([track, level])
    db.flush()
    subject = CurriculumSubject(
        slug="foundations",
        name="Foundations",
        track_id=track.id,
        level_id=level.id,
        order_index=0,
    )
    db.add(subject)
    db.flush()
    module = CurriculumModule(slug="mod", name="Mod", subject_id=subject.id, order_index=0)
    db.add(module)
    db.flush()
    bits = CurriculumTopic(
        slug="cf-bits-and-bytes",
        name="Bits and bytes",
        module_id=module.id,
        order_index=0,
        prerequisites=[],
        learning_track="CORE",
        depth_target="WORKING_KNOWLEDGE",
    )
    shell = CurriculumTopic(
        slug="cf-shell",
        name="Shell",
        module_id=module.id,
        order_index=1,
        prerequisites=["cf-bits-and-bytes"],
        learning_track="ALWAYS_ON",
        parallel_eligible=True,
        depth_target="WORKING_KNOWLEDGE",
    )
    cmdline = CurriculumTopic(
        slug="cf-command-line",
        name="Command line",
        module_id=module.id,
        order_index=2,
        prerequisites=["cf-shell"],
        learning_track="ALWAYS_ON",
        parallel_eligible=True,
    )
    db.add_all([bits, shell, cmdline])
    db.flush()
    for topic in (bits, shell, cmdline):
        lesson = CurriculumLesson(title=f"{topic.name} core", topic_id=topic.id, order_index=0)
        db.add(lesson)
        db.flush()
        db.add(
            CurriculumResource(
                title="Doc",
                url="https://example.com/doc",
                resource_type="documentation",
                role="PRIMARY",
                verification_status=TRUSTED,
                lesson_id=lesson.id,
                order_index=0,
            )
        )
    db.flush()
    return bits, shell, cmdline


def test_track_codes_and_backfill(client):
    assert track_code_from_learning_track("CORE") == TRACK_PRIMARY
    assert track_code_from_learning_track("ALWAYS_ON") == TRACK_ALWAYS_ON
    db = SessionLocal()
    try:
        bits, shell, cmdline = _seed_track_topics(db)
        # Reset tracks then backfill
        shell.learning_track = "CORE"
        shell.parallel_eligible = False
        cmdline.learning_track = "CORE"
        db.flush()
        stats = backfill_topic_tracks(db)
        db.commit()
        db.refresh(shell)
        db.refresh(bits)
        assert shell.learning_track == "ALWAYS_ON"
        assert shell.parallel_eligible is True
        assert bits.learning_track == "CORE"
        assert bits.name == "Bits and bytes"
        assert stats["always_on"] >= 1
    finally:
        db.close()


def test_planner_weekday_vs_weekend_capacity():
    topics = [
        TopicView(
            id=1,
            slug="cf-bits-and-bytes",
            name="Bits",
            locked=False,
            lessons_complete=False,
            domain="foundations",
            track=TRACK_PRIMARY,
            learning_track="CORE",
            unfinished_exercises=1,
            practice_pending=1,
        ),
        TopicView(
            id=2,
            slug="cf-shell",
            name="Shell",
            locked=False,
            lessons_complete=False,
            domain="foundations",
            track=TRACK_ALWAYS_ON,
            learning_track="ALWAYS_ON",
            parallel_eligible=True,
        ),
    ]
    weekday = build_daily_plan(
        budget_minutes=90, topics=topics, overdue_revisions=[], mode="weekday"
    )
    weekend = build_daily_plan(
        budget_minutes=180, topics=topics, overdue_revisions=[], mode="weekend"
    )
    assert weekday["total_minutes"] <= 90
    assert weekend["total_minutes"] <= 180
    assert any(i["type"] == "LEARN" for i in weekday["items"])
    assert any(i["type"] == "ALWAYS_ON" for i in weekday["items"])
    assert all(
        not next(t for t in topics if t.slug == i["topic_slug"]).locked
        for i in weekday["items"]
        if i.get("topic_slug")
    )
    assert weekday["groups"]["core"]


def test_projects_locked_until_prereqs(client):
    db = SessionLocal()
    try:
        bits, shell, cmdline = _seed_track_topics(db)
        projects_svc.seed_projects(db)
        db.commit()
        buckets = projects_svc.list_projects(db)
        calc = next(p for p in buckets["locked"] if p["slug"] == "cli-calculator")
        assert calc["state"] == "locked"

        from app.learning.service import complete_topic

        complete_topic(db, bits.id)
        complete_topic(db, shell.id)
        complete_topic(db, cmdline.id)
        buckets = projects_svc.list_projects(db)
        calc = next(p for p in buckets["available"] if p["slug"] == "cli-calculator")
        started = projects_svc.start_project(db, calc["id"])
        assert started["state"] == "in_progress"
        done = projects_svc.complete_project(db, calc["id"])
        assert done["state"] == "completed"
        db.commit()
    finally:
        db.close()


def test_broken_never_primary_trusted_allowed():
    class R:
        def __init__(self, role, status, order_index=0, id=1):
            self.role = role
            self.verification_status = status
            self.order_index = order_index
            self.id = id
            self.url = "https://example.com/doc"
            self.resource_type = "documentation"
            self.title = "t"
            self.provider = "x"
            self.section = None
            self.lecture = None
            self.video_id = None
            self.duration = None
            self.difficulty = None
            self.description = None
            self.official_unofficial = "official"
            self.completion_status = "not_started"

    broken = R("PRIMARY", BROKEN, 0, 1)
    trusted = R("PRIMARY", TRUSTED, 1, 2)
    verified = R("PRIMARY", VERIFIED, 2, 3)
    assert select_resource_for_activity([broken, trusted], "LEARN") is trusted
    assert select_resource_for_activity([broken, trusted, verified], "LEARN") is verified
    assert select_resource_for_activity([broken], "LEARN") is None


def test_dashboard_includes_tracks_and_week(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    body = res.json()
    assert "tracks" in body
    assert "this_week" in body
    assert "study_settings" in body


def test_wave1_yaml_files_exist():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / "content" / "curriculum"
    for rel in (
        "software-engineering/03-software-engineering-core.yaml",
        "backend/04-databases-and-backend.yaml",
        "mathematics/05-math-for-ml.yaml",
        "ml/06-machine-learning-foundations.yaml",
        "shells/07-career-path-shells.yaml",
    ):
        assert (root / rel).is_file()
