from app.db.session import SessionLocal
from app.db.models import (
    CurriculumLesson,
    CurriculumModule,
    CurriculumSubject,
    CurriculumTrack,
    CurriculumLevel,
    CurriculumTopic,
    DSATopic,
)


def _seed_lesson():
    db = SessionLocal()
    try:
        track = CurriculumTrack(name="Software Engineering", order_index=0)
        level = CurriculumLevel(name="Level 1: Fundamentals", order_index=0)
        db.add_all([track, level])
        db.flush()
        subject = CurriculumSubject(
            name="Backend Development",
            track_id=track.id,
            level_id=level.id,
            order_index=0,
        )
        db.add(subject)
        db.flush()
        module = CurriculumModule(name="REST APIs", subject_id=subject.id, order_index=0)
        db.add(module)
        db.flush()
        topic = CurriculumTopic(
            name="HTTP Fundamentals",
            module_id=module.id,
            order_index=0,
            prerequisites=[],
        )
        db.add(topic)
        db.flush()
        lesson = CurriculumLesson(title="HTTP Methods", topic_id=topic.id, order_index=0)
        db.add(lesson)
        db.add(DSATopic(name="Arrays", pattern="Arrays"))
        db.commit()
        return {
            "track_id": track.id,
            "subject_id": subject.id,
            "module_id": module.id,
            "topic_id": topic.id,
            "lesson_id": lesson.id,
        }
    finally:
        db.close()


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Akshit" in response.json()["message"]


def test_curriculum_hierarchy(client):
    ids = _seed_lesson()
    tracks = client.get("/api/tracks").json()
    assert tracks[0]["name"] == "Software Engineering"
    subjects = client.get("/api/subjects").json()
    assert subjects[0]["id"] == ids["subject_id"]
    modules = client.get(f"/api/modules/{ids['subject_id']}").json()
    assert modules[0]["name"] == "REST APIs"
    topics = client.get(f"/api/topics/{ids['module_id']}").json()
    assert topics[0]["prerequisites"] == []
    lessons = client.get(f"/api/lessons/{ids['topic_id']}").json()
    assert lessons[0]["title"] == "HTTP Methods"
    detail = client.get(f"/api/lesson/{ids['lesson_id']}").json()
    assert detail["id"] == ids["lesson_id"]
    assert detail["resources"] == []


def test_missing_track_404(client):
    response = client.get("/api/tracks/999")
    assert response.status_code == 404


def test_legacy_dsa_topic_routes_are_gone(client):
    """The dsa_topics CRUD surface was removed; /api/dsa/board replaced it.

    dsa_topics has been empty since the DSA curriculum moved into
    curriculum_topics (domain_key='dsa'). The table and the DSATopic model stay
    because user_progress.dsa_topic_id still references them, but nothing reads
    them over HTTP any more.
    """
    paths = set(client.app.openapi()["paths"])
    assert "/api/dsa/topics" not in paths
    assert "/api/dsa/topics/{topic_name}" not in paths
    assert "/api/progress/dsa/{topic_id}" not in paths
    assert "/api/dsa/board" in paths


def test_dsa_board_reads_the_curriculum(client):
    board = client.get("/api/dsa/board")
    assert board.status_code == 200
    body = board.json()
    assert set(body) == {"cursor", "totals", "modules"}
    assert set(body["totals"]) == {"topics", "completed", "questions", "exercises"}


def test_xp_award_and_get(client):
    first = client.post("/api/xp/award", params={"amount": 50, "activity": "lesson"})
    assert first.status_code == 200
    assert first.json()["total_xp"] == 50
    assert first.json()["level"] == 1
    assert first.json()["sessions_completed"] == 0
    second = client.post("/api/xp/award", params={"amount": 60, "activity": "session"})
    assert second.json()["total_xp"] == 110
    assert second.json()["level"] == 2
    assert second.json()["sessions_completed"] == 1
    fetched = client.get("/api/xp").json()
    assert fetched["total_xp"] == 110


def test_progress_summary_uses_xp_total(client):
    ids = _seed_lesson()
    client.post("/api/xp/award", params={"amount": 25, "activity": "lesson"})
    client.post(
        f"/api/progress/lesson/{ids['lesson_id']}",
        params={"state": "learning"},
    )
    progress = client.get("/api/progress").json()
    assert progress["xp_earned"] == 25
    assert progress["streak_days"] == 0
    assert any(item["lesson_id"] == ids["lesson_id"] for item in progress["items"])


def test_invalid_lesson_state(client):
    ids = _seed_lesson()
    response = client.post(
        f"/api/progress/lesson/{ids['lesson_id']}",
        params={"state": "finished"},
    )
    assert response.status_code == 400


def test_revision_schedule_and_pending(client):
    created = client.post(
        "/api/revision/schedule",
        params={"item_id": 1, "item_type": "lesson", "confidence": 10},
    )
    assert created.status_code == 200
    assert created.json()["review_interval"] == 1
    pending = client.get("/api/revision/pending").json()
    assert len(pending) == 1
    updated = client.post(
        "/api/revision/schedule",
        params={"item_id": 1, "item_type": "lesson", "confidence": 90},
    )
    assert updated.json()["review_interval"] == 30
    assert updated.json()["id"] == created.json()["id"]
