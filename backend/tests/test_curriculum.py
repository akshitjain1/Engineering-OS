from app.db.session import SessionLocal
from app.db.models import (
    CurriculumLesson,
    CurriculumLevel,
    CurriculumModule,
    CurriculumSubject,
    CurriculumTopic,
    CurriculumTrack,
    LessonQuestion,
)
from app.curriculum import evaluate_prerequisites, is_topic_complete, topic_lesson_progress


def _seed_chain():
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
        http_topic = CurriculumTopic(
            name="HTTP Fundamentals",
            module_id=module.id,
            order_index=0,
            prerequisites=[],
        )
        rest_topic = CurriculumTopic(
            name="REST Principles",
            module_id=module.id,
            order_index=1,
            prerequisites=["HTTP Fundamentals"],
        )
        db.add_all([http_topic, rest_topic])
        db.flush()
        http_lesson = CurriculumLesson(title="HTTP Methods", topic_id=http_topic.id, order_index=0)
        rest_lesson = CurriculumLesson(title="REST constraints", topic_id=rest_topic.id, order_index=0)
        db.add_all([http_lesson, rest_lesson])
        db.flush()
        db.add(
            LessonQuestion(
                question="Which HTTP method is idempotent and safe?",
                answer="GET",
                options=["GET", "POST", "PATCH", "CONNECT"],
                explanation="GET does not modify state.",
                lesson_id=http_lesson.id,
            )
        )
        db.commit()
        return {
            "track_id": track.id,
            "module_id": module.id,
            "http_topic_id": http_topic.id,
            "rest_topic_id": rest_topic.id,
            "http_lesson_id": http_lesson.id,
            "rest_lesson_id": rest_lesson.id,
        }
    finally:
        db.close()


def test_tree_empty(client):
    response = client.get("/api/curriculum/tree")
    assert response.status_code == 200
    body = response.json()
    assert body["tracks"] == []
    assert body["next"] is None


def test_tree_and_prerequisites(client):
    ids = _seed_chain()
    tree = client.get("/api/curriculum/tree").json()
    topics = tree["tracks"][0]["levels"][0]["subjects"][0]["modules"][0]["topics"]
    http = next(topic for topic in topics if topic["id"] == ids["http_topic_id"])
    rest = next(topic for topic in topics if topic["id"] == ids["rest_topic_id"])
    assert http["locked"] is False
    assert http["status"] == "not_started"
    # Prerequisites are advisory now: REST still reports HTTP as unmet, but it
    # is not locked and the learner may open it whenever they like.
    assert rest["locked"] is False
    assert rest["status"] == "not_started"
    assert rest["advisory"] is True
    assert "HTTP Fundamentals" in rest["lock_message"]
    assert rest["prerequisites"][0]["complete"] is False
    # A topic with nothing unmet carries no advisory at all.
    assert http["advisory"] is False
    assert http["lock_message"] is None
    assert tree["next"]["topic_id"] == ids["http_topic_id"]


def test_topic_404(client):
    assert client.get("/api/topic/999").status_code == 404
    assert client.get("/api/lessons/999").status_code == 404
    assert client.get("/api/lesson/999").status_code == 404


def test_topic_detail_and_progress_open(client):
    """A topic with unmet prerequisites is fully usable, advisory only."""
    ids = _seed_chain()
    response = client.get(f"/api/topic/{ids['rest_topic_id']}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["locked"] is False
    assert detail["advisory"] is True
    assert "HTTP Fundamentals" in detail["lock_message"]
    accepted = client.post(
        f"/api/progress/lesson/{ids['rest_lesson_id']}",
        params={"state": "completed"},
    )
    assert accepted.status_code == 200


def test_completing_prereq_unlocks_next_topic(client):
    ids = _seed_chain()
    started = client.post(
        f"/api/progress/lesson/{ids['http_lesson_id']}",
        params={"state": "in_progress"},
    )
    assert started.status_code == 200
    assert started.json()["completion_status"] == "in_progress"
    assert started.json()["xp_awarded"] == 0

    done = client.post(
        f"/api/progress/lesson/{ids['http_lesson_id']}",
        params={"state": "completed"},
    )
    assert done.status_code == 200
    assert done.json()["xp_awarded"] == 10
    again = client.post(
        f"/api/progress/lesson/{ids['http_lesson_id']}",
        params={"state": "completed"},
    )
    assert again.json()["xp_awarded"] == 0

    # The completion contract requires a passed assessment when the topic
    # contains questions (learning activity alone is not enough to unlock).
    state = client.get(f"/api/topic/{ids['http_topic_id']}").json()
    assert state["completion"]["lessons_complete"] is True
    assert state["completion"]["assessment_ok"] is False
    started = client.post(f"/api/assessment/topic/{ids['http_topic_id']}/start")
    assert started.status_code == 200
    session_id = started.json()["session_id"]
    current = client.get(f"/api/assessment/{session_id}").json()["current"]
    assert current is not None
    answered = client.post(
        "/api/assessment/answer",
        json={"session_id": session_id, "question_id": current["id"], "selected": "GET"},
    )
    assert answered.json()["correct"] is True
    completed = client.post("/api/assessment/complete", json={"session_id": session_id})
    assert completed.status_code == 200
    assert completed.json()["summary"]["score"] == 100.0

    rest = client.get(f"/api/topic/{ids['rest_topic_id']}").json()
    assert rest["locked"] is False
    assert rest["status"] == "not_started"
    allowed = client.post(
        f"/api/progress/lesson/{ids['rest_lesson_id']}",
        params={"state": "completed"},
    )
    assert allowed.status_code == 200
    rest = client.get(f"/api/topic/{ids['rest_topic_id']}").json()
    assert rest["status"] == "completed"
    assert rest["progress"]["completed"] == 1
    assert rest["progress"]["total"] == 1


def test_lesson_omits_answer_until_attempt(client):
    ids = _seed_chain()
    lesson = client.get(f"/api/lesson/{ids['http_lesson_id']}").json()
    question = lesson["questions"][0]
    assert "answer" not in question
    assert question["options"] == ["GET", "POST", "PATCH", "CONNECT"]
    wrong = client.post(
        f"/api/questions/{question['id']}/attempt",
        json={"selected": "POST"},
    )
    assert wrong.status_code == 200
    assert wrong.json()["correct"] is False
    assert wrong.json()["attempt_count"] == 1
    right = client.post(
        f"/api/questions/{question['id']}/attempt",
        json={"selected": "GET"},
    )
    assert right.json()["correct"] is True
    assert right.json()["explanation"]


def test_evaluate_prerequisites_unit():
    class FakeTopic:
        def __init__(self, lessons):
            self.lessons = lessons

    class FakeLesson:
        def __init__(self, status):
            self.completion_status = status

    by_name = {
        "HTTP Fundamentals": FakeTopic([FakeLesson("completed")]),
        "REST Principles": FakeTopic([FakeLesson("not_started")]),
    }
    unlocked = evaluate_prerequisites(["HTTP Fundamentals"], by_name)
    assert unlocked["locked"] is False
    assert unlocked["missing"] == []
    assert unlocked["advisory"] is False
    # Unmet prerequisites are still reported -- they just do not lock.
    unmet = evaluate_prerequisites(["REST Principles"], by_name)
    assert unmet["locked"] is False
    assert unmet["missing"] == ["REST Principles"]
    assert unmet["advisory"] is True
    assert unmet["message"] is not None
    assert unmet["items"][0]["complete"] is False
    assert is_topic_complete(by_name["HTTP Fundamentals"].lessons) is True
    progress = topic_lesson_progress(by_name["REST Principles"].lessons)
    assert progress["status"] == "not_started"
    empty = evaluate_prerequisites([], by_name)
    assert empty["locked"] is False
    assert empty["advisory"] is False
