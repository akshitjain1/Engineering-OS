"""V3 simplification tests: source-first completion, no gamification.

Coverage contract:
1.  POST /api/topic/{id}/complete marks a topic complete, idempotentially
2.  completing a topic writes no XP, no mastery row, no revision schedule
3.  completing a topic unlocks the next topic in sequence
4.  locked topics reject the complete action with 403
5.  POST /api/exercise/{id}/complete marks a build task done, no XP
6.  GET /api/roadmap is available and mirrors the curriculum tree
7.  the daily planner emits only LEARN / PRACTICE / BUILD / REVIEW
8.  a completed topic leaves the daily plan
"""

from app.db.models import (
    CurriculumLesson,
    CurriculumLevel,
    CurriculumModule,
    CurriculumResource,
    CurriculumSubject,
    CurriculumTopic,
    CurriculumTrack,
    LessonExercise,
    MasteryEvidence,
    RevisionSchedule,
    TopicMastery,
    UserProgress,
)
from app.db.session import SessionLocal
from app.learning import service


def _generate_plan(minutes):
    """Legacy planner output, straight from the service.

    GET /api/daily-plan and POST /api/daily-plan/generate were removed -- two
    endpoints both claiming to own "today" (the other being /api/day) is how you
    end up trusting neither. The planner itself is still live behind
    /api/dashboard, so these tests exercise it directly.
    """
    db = SessionLocal()
    try:
        plan = service.generate_daily_plan(db, budget_minutes=minutes)
        db.commit()
        return plan
    finally:
        db.close()


def _seed_pair() -> dict:
    """Bits and bytes -> Binary, with lessons, one implementation exercise."""
    db = SessionLocal()
    try:
        track = CurriculumTrack(name="SE-V3", order_index=0)
        level = CurriculumLevel(name="L1", order_index=0)
        db.add_all([track, level])
        db.flush()
        subject = CurriculumSubject(name="Foundations", track_id=track.id, level_id=level.id, order_index=0)
        db.add(subject)
        db.flush()
        module = CurriculumModule(name="Bits", subject_id=subject.id, order_index=0)
        db.add(module)
        db.flush()
        bits = CurriculumTopic(name="Bits and bytes", slug="cf-bits-and-bytes", module_id=module.id, order_index=0, prerequisites=[])
        binary = CurriculumTopic(
            name="Binary",
            slug="cf-binary",
            module_id=module.id,
            order_index=1,
            prerequisites=["cf-bits-and-bytes"],
        )
        db.add_all([bits, binary])
        db.flush()
        lesson = CurriculumLesson(title="Bits core", topic_id=bits.id, order_index=0)
        db.add(lesson)
        db.flush()
        db.add(
            CurriculumResource(
                title="CS50x Week 0",
                url="https://cs50.harvard.edu/x/weeks/0/",
                resource_type="interactive_tutorial",
                role="PRIMARY",
                lesson_id=lesson.id,
                order_index=0,
            )
        )
        exercise = LessonExercise(
            title="Count bits",
            description="Implement a function that counts set bits.",
            lesson_id=lesson.id,
            exercise_type="SELF_REFLECTION",
        )
        db.add(exercise)
        db.commit()
        return {
            "bits_id": bits.id,
            "binary_id": binary.id,
            "lesson_id": lesson.id,
            "exercise_id": exercise.id,
        }
    finally:
        db.close()


def _node_payload(tree, topic_id: int) -> dict:
    for track in tree["tracks"]:
        for level in track["levels"]:
            for subject in level["subjects"]:
                for module in subject["modules"]:
                    for topic in module["topics"]:
                        if topic["id"] == topic_id:
                            return topic
    raise AssertionError(f"topic {topic_id} not found in tree")


def test_1_2_complete_topic_idempotent_no_gamification(client):
    seed = _seed_pair()
    bits_id = seed["bits_id"]

    first = client.post(f"/api/topic/{bits_id}/complete")
    assert first.status_code == 200
    body = first.json()
    assert body["complete"] is True
    assert body["status"] == "completed"

    second = client.post(f"/api/topic/{bits_id}/complete")
    assert second.status_code == 200
    assert second.json()["complete"] is True

    db = SessionLocal()
    try:
        assert db.query(MasteryEvidence).count() == 0
        assert db.query(TopicMastery).count() == 0
        assert db.query(RevisionSchedule).count() == 0
        rows = db.query(UserProgress).filter(UserProgress.topic_id == bits_id).all()
        assert len(rows) == 1
        assert rows[0].progress_state == "completed"
        lesson = db.get(CurriculumLesson, seed["lesson_id"])
        assert lesson.completion_status == "completed"
        exercise = db.get(LessonExercise, seed["exercise_id"])
        assert exercise.completion_status == "completed"
    finally:
        db.close()

    assert client.get("/api/xp").json()["total_xp"] == 0


def test_3_complete_topic_advances_cursor(client):
    """Completing a prerequisite still clears the advisory and moves the cursor."""
    seed = _seed_pair()
    binary_before = client.get("/api/roadmap").json()
    node = _node_payload(binary_before, seed["binary_id"])
    assert node["locked"] is False
    assert node["advisory"] is True
    assert binary_before["next"]["topic_id"] == seed["bits_id"]

    client.post(f"/api/topic/{seed['bits_id']}/complete")

    tree_after = client.get("/api/roadmap").json()
    node = _node_payload(tree_after, seed["binary_id"])
    assert node["locked"] is False
    assert node["advisory"] is False
    detail = client.get(f"/api/topic/{seed['binary_id']}").json()
    assert detail["locked"] is False
    assert detail["prerequisites"][0]["complete"] is True
    # Cursor has moved off the completed topic and onto the next one.
    assert tree_after["next"]["topic_id"] == seed["binary_id"]


def test_4_any_topic_accepts_complete(client):
    """Completing out of order is allowed: prerequisites never block."""
    seed = _seed_pair()
    response = client.post(f"/api/topic/{seed['binary_id']}/complete")
    assert response.status_code == 200
    detail = client.get(f"/api/topic/{seed['binary_id']}").json()
    assert detail["locked"] is False


def test_5_exercise_complete_no_xp(client):
    seed = _seed_pair()
    response = client.post(f"/api/exercise/{seed['exercise_id']}/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert client.get("/api/xp").json()["total_xp"] == 0
    db = SessionLocal()
    try:
        exercise = db.get(LessonExercise, seed["exercise_id"])
        assert exercise.completion_status == "completed"
        assert db.query(MasteryEvidence).count() == 0
        assert db.query(UserProgress).count() == 0
    finally:
        db.close()


def test_6_roadmap_mirrors_tree(client):
    _seed_pair()
    tree = client.get("/api/curriculum/tree").json()
    roadmap = client.get("/api/roadmap").json()
    assert roadmap["next"] == tree["next"]
    assert _node_payload(roadmap, tree["next"]["topic_id"]) is not None


def test_7_8_planner_emits_only_learn_practice_build_review(client):
    seed = _seed_pair()
    plan = _generate_plan(120)
    allowed = {"LEARN", "PRACTICE", "BUILD", "REVIEW"}
    assert plan["total_minutes"] <= 120
    for item in plan["items"]:
        assert item["type"] in allowed
    # Bits is the cursor -> a LEARN item exists for it.
    assert any(item["type"] == "LEARN" and item.get("topic_id") == seed["bits_id"] for item in plan["items"])

    client.post(f"/api/topic/{seed['bits_id']}/complete")

    plan2 = _generate_plan(120)
    learn = [item for item in plan2["items"] if item["type"] == "LEARN"]
    assert all(item.get("topic_id") != seed["bits_id"] for item in learn)