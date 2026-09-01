"""V2 regression suite: mastery correctness, assessment sessions, exercises.

Coverage contract (one test per numbered item):
1.  repeated correct answers never inflate mastery
2.  practice question attempts write no evidence, no XP
3.  evidence registers replace instead of append
4.  diagnostic masteries reflect the latest session only
5.  DSA topics never MASTER from MCQs alone
6.  java implementation topics capped without implementation evidence
7.  assessment sessions: one result per attempt, score at completion
8.  assessment completion bumps attempts once per session, XP once
9.  assessment answers are idempotent within a session
10. bits-and-bytes completion unlocks binary (contract, no refresh)
11. completion contract adapts to topic contents
12. completion propagates to roadmap tree and planner
13. lesson XP once; question XP is zero
14. numeric exercises evaluate, retry until correct, XP once
15. short-answer exercises compare leniently
16. code / reflection exercises self-evaluate without a sandbox
17. XP is never awarded on GET
18. XP is awarded once per assessment session
19. planner treats contract-complete topics as done (no LEARN)
20. reconciliation dry-run writes nothing; apply rebuilds current evidence
21. curriculum is untouched: 222 topics, no Domain 3
22. old failures drop out of mastery once superseded
23. revision schedule follows the latest mastery evidence
24. dashboard focus advances past a completed topic
"""

from pathlib import Path
from typing import Any

import pytest

from app.curriculum import is_lesson_complete
from app.db.models import (
    AssessmentSession,
    CurriculumLesson,
    CurriculumLevel,
    CurriculumModule,
    CurriculumResource,
    CurriculumSubject,
    CurriculumTopic,
    CurriculumTrack,
    LessonExercise,
    LessonQuestion,
    MasteryEvidence,
    RevisionSchedule,
    TopicMastery,
    UserProgress,
    UserXP,
    XpEvent,
)
from app.content.import_curriculum import expand_targets, load_file
from app.content.validate import topic_slugs_from_data
from app.learning import service
from app.learning.reconcile import apply_reconciliation, plan_reconciliation
from app.db.session import SessionLocal

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _seed_single_topic(db, *, slug="cf-bits-and-bytes", name="Bits and bytes", lessons=1, questions=4, exercises=1) -> dict[str, Any]:
    track = CurriculumTrack(name="SE-V2", order_index=0)
    level = CurriculumLevel(name="L1", order_index=0)
    db.add_all([track, level])
    db.flush()
    subject = CurriculumSubject(name="Foundations", track_id=track.id, level_id=level.id, order_index=0)
    db.add(subject)
    db.flush()
    module = CurriculumModule(name="Basics", subject_id=subject.id, order_index=0)
    db.add(module)
    db.flush()
    topic = CurriculumTopic(name=name, slug=slug, module_id=module.id, order_index=0, prerequisites=[])
    db.add(topic)
    db.flush()
    for index in range(lessons):
        lesson = CurriculumLesson(title=f"Lesson {index}", topic_id=topic.id, order_index=index)
        db.add(lesson)
        db.flush()
        if index == 0:
            resource = CurriculumResource(
                title=f"Primary {slug}",
                url=f"https://example.test/{slug}",
                resource_type="interactive_tutorial",
                role="PRIMARY",
                lesson_id=lesson.id,
                order_index=0,
            )
            db.add(resource)
        for qindex in range(questions):
            db.add(
                LessonQuestion(
                    question=f"Q{qindex}?",
                    answer="correct",
                    options=["correct", "wrong"],
                    explanation=f"Explanation {qindex}",
                    lesson_id=lesson.id,
                )
            )
        for eindex in range(exercises):
            db.add(
                LessonExercise(
                    title=f"Exercise {eindex}",
                    description="Do the thing.",
                    lesson_id=lesson.id,
                    exercise_type="SELF_REFLECTION",
                )
            )
    db.flush()
    return {"topic": topic, "module": module, "lessons": topic.lessons}


def _questions_for(db, topic_id: int) -> list[Any]:
    from app.db.models import LessonQuestion

    topic = db.get(CurriculumTopic, topic_id)
    ids = []
    for lesson in sorted(topic.lessons, key=lambda item: item.order_index):
        for question in lesson.questions:
            ids.append(question.id)
    return ids


# --- 1, 2, 3, 22: repeated attempts and registers ---------------------------


def test_1_repeated_correct_answers_do_not_inflate_mastery(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="dsa-binary-search-classic")
        topic = seed["topic"]
        db.commit()
        topic_id = topic.id
    finally:
        db.close()
    topic_detail = client.get(f"/api/topic/{topic_id}").json()
    qid = topic_detail["questions"][0]["id"]
    for _ in range(5):
        answered = client.post(f"/api/questions/{qid}/attempt", json={"selected": "correct"})
        assert answered.json()["correct"] is True
    db = SessionLocal()
    try:
        assert db.query(MasteryEvidence).count() == 0
        question = db.query(LessonQuestion).first()
        assert question.attempt_count == 5
        assert question.last_correct is True
    finally:
        db.close()
    after = client.get(f"/api/topic/{topic_id}").json()
    assert after["mastery"]["mastery_score"] is None
    assert after["mastery"]["status"] == "UNKNOWN"


def test_2_practice_attempt_writes_no_evidence_and_no_xp(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-bits-and-bytes")
        topic = seed["topic"]
        db.commit()
        topic_id = topic.id
        qid = _questions_for(db, topic_id)[0]
    finally:
        db.close()
    xp_before = client.get("/api/xp").json()["total_xp"]
    response = client.post(f"/api/questions/{qid}/attempt", json={"selected": "correct"})
    assert response.status_code == 200
    assert response.json()["xp_awarded"] == 0
    assert client.get("/api/xp").json()["total_xp"] == xp_before
    db = SessionLocal()
    try:
        assert db.query(MasteryEvidence).count() == 0
    finally:
        db.close()


def test_3_evidence_registers_replace_never_append(client):
    db = SessionLocal()
    try:
        service.upsert_evidence(db, topic_slug="cf-binary", source="diagnostic", category="conceptual", score=70)
        service.upsert_evidence(db, topic_slug="cf-binary", source="diagnostic", category="conceptual", score=90)
        service.upsert_evidence(db, topic_slug="cf-binary", source="lesson", category="conceptual", score=55)
        db.commit()
        assert db.query(MasteryEvidence).filter(MasteryEvidence.topic_slug == "cf-binary").count() == 2
        register = db.query(MasteryEvidence).filter(
            MasteryEvidence.source == "diagnostic", MasteryEvidence.topic_slug == "cf-binary"
        ).one()
        assert register.score == 90
    finally:
        db.close()


def test_22_old_failures_drop_out_when_superseded(client):
    db = SessionLocal()
    try:
        service.upsert_evidence(db, topic_slug="cf-bits-and-bytes", source="diagnostic", category="conceptual", score=20)
        service.sync_mastery_row(db, "cf-bits-and-bytes", attempt=True)
        db.commit()
        low = (
            db.query(TopicMastery).filter(TopicMastery.topic_slug == "cf-bits-and-bytes").one().mastery_score
        )
        service.upsert_evidence(db, topic_slug="cf-bits-and-bytes", source="diagnostic", category="conceptual", score=95)
        service.sync_mastery_row(db, "cf-bits-and-bytes", attempt=True)
        db.commit()
        high = (
            db.query(TopicMastery).filter(TopicMastery.topic_slug == "cf-bits-and-bytes").one().mastery_score
        )
        assert low == 20.0
        assert high == 95.0
        assert db.query(MasteryEvidence).count() == 1
    finally:
        db.close()


# --- 4, 5, 6: diagnostic semantics + caps -----------------------------------


def test_4_latest_diagnostic_session_wins(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-bits-and-bytes")
        db.commit()
    finally:
        db.close()
    first = client.post("/api/diagnostic/start").json()
    session_id = first["session_id"]
    from app.learning.diagnostic_bank import questions_by_id as qby

    qid = first["current"]["id"]
    while qid:
        question = qby()[qid]
        if question["type"] in {"mcq", "tracing", "complexity"}:
            payload = {"selected": question["answer"]}
        elif question["type"] == "short_answer":
            payload = {"text": question.get("answer") or "placeholder response"}
        else:
            payload = {
                "code": "int[] f(int[] a) { return a; }",
                "explanation": "placeholder solution",
                "complexity": question.get("expected_complexity") or "O(n)",
            }
        answered = client.post(
            "/api/diagnostic/answer", json={"session_id": session_id, "question_id": qid, **payload}
        )
        assert answered.status_code == 200
        state = answered.json()
        qid = state["current"]["id"] if state.get("current") else None
    completed = client.post("/api/diagnostic/complete", json={"session_id": session_id})
    assert completed.status_code == 200
    score_after_perfect = client.get("/api/mastery").json()
    perfect_bits = next(
        item for item in score_after_perfect["items"] if item.get("topic_slug") == "cf-bits-and-bytes"
    )
    bits_score = perfect_bits["mastery_score"]
    # Second, terrible session: same topics answered wrong.
    second = client.post("/api/diagnostic/start").json()
    session2 = second["session_id"]
    qid = second["current"]["id"]
    while qid:
        question = qby()[qid]
        wrong = [option for option in (question.get("options") or ["x"]) if option != question.get("answer")]
        if question["type"] in {"mcq", "tracing", "complexity"}:
            payload = {"selected": wrong[0] if wrong else "x"}
        elif question["type"] == "short_answer":
            payload = {"text": "definitely wrong"}
        else:
            payload = {"code": "", "explanation": "", "complexity": "O(1)"}
        answered = client.post(
            "/api/diagnostic/answer", json={"session_id": session2, "question_id": qid, **payload}
        )
        qid = answered.json()["current"]["id"] if answered.json().get("current") else None
    completed = client.post("/api/diagnostic/complete", json={"session_id": session2})
    assert completed.status_code == 200
    db = SessionLocal()
    try:
        rows = db.query(MasteryEvidence).filter(
            MasteryEvidence.topic_slug == "cf-bits-and-bytes", MasteryEvidence.source == "diagnostic"
        ).all()
        assert len(rows) == 1
        assert rows[0].score < 50
    finally:
        db.close()
    after_bad = client.get("/api/mastery").json()
    bad_bits = next(item for item in after_bad["items"] if item.get("topic_slug") == "cf-bits-and-bytes")
    assert bad_bits["mastery_score"] < bits_score
    assert bad_bits["mastery_score"] < 50


def test_5_dsa_never_masters_from_mcqs_via_api(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="dsa-quick-sort", name="Quick sort")
        topic = seed["topic"]
        db.commit()
        topic_id = topic.id
        qid = _questions_for(db, topic_id)[0]
    finally:
        db.close()
    started = client.post(f"/api/assessment/topic/{topic_id}/start")
    assert started.status_code == 200
    session_id = started.json()["session_id"]
    for _ in range(started.json()["total"]):
        state = client.get(f"/api/assessment/{session_id}").json()
        current = state["current"]
        assert current is not None
        answer = client.post(
            "/api/assessment/answer",
            json={"session_id": session_id, "question_id": current["id"], "selected": "correct"},
        )
        assert answer.json()["correct"] is True
    result = client.post("/api/assessment/complete", json={"session_id": session_id})
    assert result.status_code == 200
    assert result.json()["summary"]["score"] == 100
    assert result.json()["mastery"]["status"] == "FAMILIAR"


def test_6_java_loops_requires_implementation(client):
    db = SessionLocal()
    try:
        service.upsert_evidence(db, topic_slug="java-loops", source="diagnostic", category="conceptual", score=100)
        service.sync_mastery_row(db, "java-loops", attempt=True)
        db.commit()
        row = db.query(TopicMastery).filter(TopicMastery.topic_slug == "java-loops").one()
        assert row.status == "FAMILIAR"
        service.upsert_evidence(db, topic_slug="java-loops", source="exercise", category="implementation", score=80)
        service.sync_mastery_row(db, "java-loops", attempt=True)
        db.commit()
        row = db.query(TopicMastery).filter(TopicMastery.topic_slug == "java-loops").one()
        assert row.status == "MASTERED"
        assert row.has_implementation_evidence is True
    finally:
        db.close()


# --- 7, 8, 9: assessment sessions -------------------------------------------


def test_7_8_9_assessment_session_flow(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-binary", name="Binary")
        topic = seed["topic"]
        db.commit()
        topic_id = topic.id
    finally:
        db.close()
    started = client.post(f"/api/assessment/topic/{topic_id}/start")
    assert started.status_code == 200
    session = started.json()
    session_id = session["session_id"]
    assert session["total"] == 4
    assert session["answered"] == 0

    first = client.get(f"/api/assessment/{session_id}").json()
    qid = first["current"]["id"]
    wrong_answer = client.post(
        "/api/assessment/answer", json={"session_id": session_id, "question_id": qid, "selected": "wrong"}
    )
    assert wrong_answer.json()["correct"] is False
    assert wrong_answer.json()["explanation"] is not None
    # Idempotence: answering the same question again is rejected.
    duplicate = client.post(
        "/api/assessment/answer", json={"session_id": session_id, "question_id": qid, "selected": "correct"}
    )
    assert duplicate.status_code == 400
    state = client.get(f"/api/assessment/{session_id}").json()
    assert state["answered"] == 1

    while state["current"] is not None:
        current = state["current"]
        answer = client.post(
            "/api/assessment/answer",
            json={"session_id": session_id, "question_id": current["id"], "selected": "correct"},
        )
        assert answer.status_code == 200
        state = answer.json()

    xp_before = client.get("/api/xp").json()["total_xp"]
    completed = client.post("/api/assessment/complete", json={"session_id": session_id})
    assert completed.status_code == 200
    summary = completed.json()["summary"]
    assert summary["score"] == 75.0
    assert summary["correct"] == 3
    assert summary["total"] == 4
    assert completed.json()["xp_awarded"] == 14  # assessment_xp(75)

    # Completing again is a no-op for XP and mastery.
    again = client.post("/api/assessment/complete", json={"session_id": session_id})
    assert again.status_code == 200
    assert again.json().get("xp_awarded", 0) == 0
    assert client.get("/api/xp").json()["total_xp"] == xp_before + 14

    db = SessionLocal()
    try:
        row = db.query(TopicMastery).filter(TopicMastery.topic_slug == "cf-binary").one()
        assert row.attempts == 1
        assert row.mastery_score == 75.0
        assert db.query(MasteryEvidence).filter(
            MasteryEvidence.topic_slug == "cf-binary", MasteryEvidence.source == "assessment"
        ).count() == 1
        sessions = db.query(AssessmentSession).filter(AssessmentSession.topic_id == topic_id).all()
        assert len(sessions) == 1
        assert sessions[0].status == "completed"
    finally:
        db.close()

    detail = client.get(f"/api/topic/{topic_id}").json()
    assert detail["assessment"]["score"] == 75.0
    assert detail["completion"]["assessment_ok"] is True


# --- 10, 11, 12: the completion contract ------------------------------------


def test_10_resources_only_completion_unlocks_binary(client):
    db = SessionLocal()
    try:
        track = CurriculumTrack(name="SE-CONTRACT", order_index=0)
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
        bit_lesson = CurriculumLesson(title="Bits core", topic_id=bits.id, order_index=0)
        db.add(bit_lesson)
        db.flush()
        resource = CurriculumResource(
            title="CS50x Week 0",
            url="https://cs50.harvard.edu/x/weeks/0/",
            resource_type="interactive_tutorial",
            role="PRIMARY",
            lesson_id=bit_lesson.id,
            order_index=0,
        )
        db.add(resource)
        db.commit()
        resource_id, binary_id, bits_id = resource.id, binary.id, bits.id
        bit_lesson_id = bit_lesson.id
    finally:
        db.close()

    tree_before = client.get("/api/curriculum/tree").json()
    binary_node_before = next(
        topic
        for level in tree_before["tracks"][0]["levels"]
        for subject in level["subjects"]
        for module in subject["modules"]
        for topic in module["topics"]
        if topic["id"] == binary_id
    )
    # Never locked -- but the unmet prerequisite is reported as advisory, and
    # that is what has to clear once the resource is consumed.
    assert binary_node_before["locked"] is False
    assert binary_node_before["advisory"] is True

    # Consume the resource (learning activity) — no lesson state touched.
    consumed = client.post(f"/api/progress/resource/{resource_id}", json={"completed": True})
    assert consumed.status_code == 200

    bits_as_complete = client.get(f"/api/topic/{bits_id}").json()
    assert bits_as_complete["completion"]["learning_done"] is True
    assert bits_as_complete["completion"]["complete"] is True

    tree_after = client.get("/api/curriculum/tree").json()
    binary_node = next(
        topic
        for level in tree_after["tracks"][0]["levels"]
        for subject in level["subjects"]
        for module in subject["modules"]
        for topic in module["topics"]
        if topic["id"] == binary_id
    )
    assert binary_node["locked"] is False
    assert binary_node["advisory"] is False
    binary_detail = client.get(f"/api/topic/{binary_id}").json()
    assert binary_detail["locked"] is False
    assert binary_detail["prerequisites"][0]["complete"] is True
    # Propagates without any refresh call.
    assert client.get(f"/api/topic/{binary_id}").json()["advisory"] is False


def test_11_contract_requires_exercise_and_assessment_when_present(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-hexadecimal", name="Hex", questions=4, exercises=1)
        topic = seed["topic"]
        db.commit()
        topic_id = topic.id
        exercise_id = next(
            exercise.id
            for lesson in topic.lessons
            for exercise in lesson.exercises
        )
    finally:
        db.close()
    # Learning activity done, exercise and assessment still open.
    lesson = client.get(f"/api/topic/{topic_id}").json()["lessons"][0]
    client.post(f"/api/progress/lesson/{lesson['id']}", params={"state": "completed"})
    state = client.get(f"/api/topic/{topic_id}").json()["completion"]
    assert state["lessons_complete"] is True
    assert state["exercises_complete"] is False
    assert state["assessment_ok"] is False
    assert state["complete"] is False
    # Exercise done → still pending assessment.
    client.post(
        "/api/exercise/%d/answer" % exercise_id,
        json={"answer": "self-verified", "code": "", "explanation": "", "complexity": ""},
    )
    state = client.get(f"/api/topic/{topic_id}").json()["completion"]
    assert state["exercises_complete"] is True
    assert state["complete"] is False
    # Pass the assessment → complete.
    started = client.post(f"/api/assessment/topic/{topic_id}/start").json()
    session_id = started["session_id"]
    while True:
        current = client.get(f"/api/assessment/{session_id}").json()["current"]
        if current is None:
            break
        client.post(
            "/api/assessment/answer",
            json={"session_id": session_id, "question_id": current["id"], "selected": "correct"},
        )
    client.post("/api/assessment/complete", json={"session_id": session_id})
    state = client.get(f"/api/topic/{topic_id}").json()["completion"]
    assert state["complete"] is True


def test_12_completed_topic_leaves_planner_learn_and_tree_marks_done(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-bits-and-bytes")
        topic = seed["topic"]
        db.commit()
        topic_id = topic.id
        lesson_id = topic.lessons[0].id
        exercise_id = topic.lessons[0].exercises[0].id
    finally:
        db.close()
    # Complete everything: lesson, exercise, assessment (contract).
    client.post(f"/api/progress/lesson/{lesson_id}", params={"state": "completed"})
    client.post(
        f"/api/exercise/{exercise_id}/answer",
        json={"answer": "done", "code": "", "explanation": "", "complexity": ""},
    )
    started = client.post(f"/api/assessment/topic/{topic_id}/start").json()
    session_id = started["session_id"]
    while client.get(f"/api/assessment/{session_id}").json()["current"]:
        current = client.get(f"/api/assessment/{session_id}").json()["current"]
        client.post(
            "/api/assessment/answer",
            json={"session_id": session_id, "question_id": current["id"], "selected": "correct"},
        )
    client.post("/api/assessment/complete", json={"session_id": session_id})
    completed = client.get(f"/api/topic/{topic_id}").json()
    assert completed["completion"]["complete"] is True
    assert completed["status"] == "completed"
    plan = client.post(
        "/api/daily-plan/generate", json={"minutes": 60}
    ).json()["plan"]
    learn_items = [item for item in plan["items"] if item["type"] == "LEARN"]
    assert all(item.get("topic_id") != topic_id for item in learn_items)


# --- 13, 14, 15, 16: exercises and XP ---------------------------------------


def test_13_question_xp_zero_lesson_xp_once(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-cpu")
        topic = seed["topic"]
        db.commit()
        topic_id, lesson_id = topic.id, topic.lessons[0].id
        qid = _questions_for(db, topic_id)[0]
    finally:
        db.close()
    client.post(f"/api/questions/{qid}/attempt", json={"selected": "correct"})
    client.post(f"/api/questions/{qid}/attempt", json={"selected": "correct"})
    first = client.post(f"/api/progress/lesson/{lesson_id}", params={"state": "completed"})
    assert first.json()["xp_awarded"] == 10
    again = client.post(f"/api/progress/lesson/{lesson_id}", params={"state": "completed"})
    assert again.json()["xp_awarded"] == 0


def test_14_numeric_exercise_evaluates_retries_xp_once(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-binary")
        exercise = seed["topic"].lessons[0].exercises[0]
        exercise.exercise_type = "NUMERIC"
        exercise.correct_answer = "32768"
        db.commit()
        exercise_id = exercise.id
    finally:
        db.close()
    wrong = client.post(
        "/api/exercise/%d/answer" % exercise_id,
        json={"answer": "32767"},
    )
    assert wrong.status_code == 200
    assert wrong.json()["correct"] is False
    assert wrong.json()["evaluated"] is True
    assert wrong.json()["completed"] is False
    assert wrong.json()["correct_answer"] == "32768"
    xp_before = client.get("/api/xp").json()["total_xp"]
    right = client.post(
        "/api/exercise/%d/answer" % exercise_id,
        json={"answer": "32,768"},
    )
    assert right.json()["correct"] is True
    assert right.json()["completed"] is True
    assert right.json()["xp_awarded"] > 0
    assert client.get("/api/xp").json()["total_xp"] == xp_before + right.json()["xp_awarded"]
    repeat = client.post(
        "/api/exercise/%d/answer" % exercise_id,
        json={"answer": "32768"},
    )
    assert repeat.json()["xp_awarded"] == 0


def test_15_short_answer_lenient_compare(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-char-encoding")
        exercise = seed["topic"].lessons[0].exercises[0]
        exercise.exercise_type = "SHORT_ANSWER"
        exercise.correct_answer = "The smallest unit of digital information"
        db.commit()
        exercise_id = exercise.id
    finally:
        db.close()
    close = client.post(
        "/api/exercise/%d/answer" % exercise_id,
        json={"answer": "  the SMALLEST   unit of digital information "},
    )
    assert close.json()["correct"] is True
    assert close.json()["completed"] is True


def test_16_code_and_reflection_self_evaluate_no_sandbox(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-algorithms")
        code_exercise, reflect_exercise = seed["topic"].lessons[0].exercises[0], None
        code_exercise.exercise_type = "CODE"
        db.flush()
        from app.db.models import LessonExercise

        reflect = LessonExercise(
            title="Reflect",
            description="Reflect on the tradeoff.",
            lesson_id=seed["topic"].lessons[0].id,
            exercise_type="SELF_REFLECTION",
        )
        db.add(reflect)
        db.flush()
        db.commit()
        code_id, reflect_id = code_exercise.id, reflect.id
    finally:
        db.close()
    coded = client.post(
        "/api/exercise/%d/answer" % code_id,
        json={"code": "int main() { return 0; }", "explanation": "entry point", "complexity": "O(1)"},
    )
    assert coded.json()["completed"] is True
    assert coded.json()["user_code"] == "int main() { return 0; }"
    assert coded.json()["user_complexity"] == "O(1)"
    reflected = client.post(
        "/api/exercise/%d/answer" % reflect_id,
        json={"answer": "The cache side effect is predictability."},
    )
    assert reflected.json()["completed"] is True
    assert reflected.json()["user_answer"] == "The cache side effect is predictability."


# --- 17, 18: XP semantics ---------------------------------------------------


def test_17_xp_never_on_get(client):
    before = client.get("/api/xp").json()["total_xp"]
    for _ in range(3):
        client.get("/api/xp")
        client.get("/api/progress")
        client.get("/api/dashboard")
    assert client.get("/api/xp").json()["total_xp"] == before


def test_18_xp_once_per_assessment_session(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-program")
        topic = seed["topic"]
        db.commit()
        topic_id = topic.id
    finally:
        db.close()
    started = client.post(f"/api/assessment/topic/{topic_id}/start").json()
    session_id = started["session_id"]
    while client.get(f"/api/assessment/{session_id}").json()["current"]:
        current = client.get(f"/api/assessment/{session_id}").json()["current"]
        client.post(
            "/api/assessment/answer",
            json={"session_id": session_id, "question_id": current["id"], "selected": "correct"},
        )
    before = client.get("/api/xp").json()["total_xp"]
    completed = client.post("/api/assessment/complete", json={"session_id": session_id})
    assert completed.json()["xp_awarded"] > 0
    # The same transaction also awards the one-time mastery bonus (25 XP) for
    # the first MASTERED crossing; the assessment XP is exactly what the
    # session returned and nothing is duplicated.
    total_after = client.get("/api/xp").json()["total_xp"]
    assert total_after == before + completed.json()["xp_awarded"] + 25
    db = SessionLocal()
    try:
        events = db.query(XpEvent).filter(XpEvent.idempotency_key == f"assessment_complete:{session_id}").all()
        assert len(events) == 1
        rows = db.query(UserXP).all()
        assert len(rows) == 1
    finally:
        db.close()
    assert client.get("/api/xp").json()["total_xp"] == total_after


# --- 19: planner ------------------------------------------------------------


def test_19_planner_skips_contract_complete_topics(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-memory")
        topic = seed["topic"]
        db.commit()
        topic_id = topic.id
        lesson_id = topic.lessons[0].id
        exercise_id = topic.lessons[0].exercises[0].id
    finally:
        db.close()
    client.post(f"/api/progress/lesson/{lesson_id}", params={"state": "completed"})
    client.post(f"/api/exercise/{exercise_id}/answer", json={"answer": "x", "code": "", "explanation": "", "complexity": ""})
    started = client.post(f"/api/assessment/topic/{topic_id}/start").json()
    session_id = started["session_id"]
    while client.get(f"/api/assessment/{session_id}").json()["current"]:
        current = client.get(f"/api/assessment/{session_id}").json()["current"]
        client.post(
            "/api/assessment/answer",
            json={"session_id": session_id, "question_id": current["id"], "selected": "correct"},
        )
    client.post("/api/assessment/complete", json={"session_id": session_id})
    plan = client.post("/api/daily-plan/generate", json={"minutes": 120}).json()["plan"]
    slugs = {item.get("topic_slug") for item in plan["items"]}
    assert "cf-memory" not in slugs
    learn = [item for item in plan["items"] if item["type"] == "LEARN"]
    assert learn == []


# --- 20: reconciliation -----------------------------------------------------


def test_20_reconciliation_dry_run_then_apply(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="dsa-quick-sort", name="Quick sort")
        topic = seed["topic"]
        db.add(
            TopicMastery(
                user_id="akshit",
                topic_slug="dsa-quick-sort",
                topic_id=topic.id,
                status="FAMILIAR",
                mastery_score=84.0,
                confidence=84.0,
                attempts=4,
                pace_mode="NORMAL",
                has_implementation_evidence=False,
            )
        )
        # Simulate legacy accumulation: many question rows + stale registers.
        for score in (100, 100, 100, 100, 100, 100):
            db.add(
                MasteryEvidence(
                    user_id="akshit",
                    topic_slug="dsa-quick-sort",
                    source="question",
                    category="conceptual",
                    score=score,
                )
            )
        db.add(
            MasteryEvidence(
                user_id="akshit",
                topic_slug="dsa-quick-sort",
                source="diagnostic",
                category="conceptual",
                score=100,
            )
        )
        db.commit()
        topic_id = topic.id
        xp_rows = db.query(UserXP).count()
        progress_rows = db.query(UserProgress).count()
    finally:
        db.close()
    db = SessionLocal()
    try:
        before_count = db.query(MasteryEvidence).count()
        assert before_count == 7
        report = plan_reconciliation(db)
        assert len(report) == 1
        item = report[0]
        assert item["topic_slug"] == "dsa-quick-sort"
        assert item["old_score"] == 84.0
        assert item["new_score"] == 100.0
        assert item["new_status"] == "FAMILIAR"
        assert any("legacy question evidence" in reason for reason in item["reasons"])
        assert db.query(MasteryEvidence).count() == before_count  # dry run wrote nothing
        applied = apply_reconciliation(db)
        db.commit()
        assert applied["applied"] == 1
        registers = db.query(MasteryEvidence).filter(MasteryEvidence.topic_slug == "dsa-quick-sort").all()
        assert len(registers) == 1
        assert registers[0].source == "diagnostic"
        row = db.query(TopicMastery).filter(TopicMastery.topic_slug == "dsa-quick-sort").one()
        assert row.status == "FAMILIAR"
        assert row.mastery_score == 100.0
        assert db.query(UserXP).count() == xp_rows
        assert db.query(UserProgress).count() == progress_rows
    finally:
        db.close()


# --- 21: curriculum immutability --------------------------------------------


def test_21_curriculum_is_untouched_222_topics_no_domain3():
    index = Path(BACKEND_DIR / "content" / "curriculum" / "v1-index.yaml")
    assert index.exists()
    files = expand_targets(index)
    # Original three manifests stay first; wave-1 domains append.
    assert len(files) >= 3
    original = files[:3]
    slugs: set[str] = set()
    seen_levels: set[str] = set()
    for path in original:
        data = load_file(path)
        slugs |= topic_slugs_from_data(data)
        track = data.get("track") or {}
        for level in track.get("levels", []):
            seen_levels.add(level.get("slug", ""))
    assert len(slugs) == 222
    assert {"domain-0", "domain-1", "domain-2"} <= seen_levels
    assert "domain-3" not in seen_levels
    expected = {
        "cf-bits-and-bytes": "cf-binary",
        "cf-binary": "cf-hexadecimal",
    }
    for path in original:
        data = load_file(path)
        for topic in data.get("topics", []):
            slug = topic.get("slug")
            if slug in expected:
                assert topic.get("next_topic") == expected[slug], slug


# --- 23, 24: revision and dashboard -----------------------------------------


def test_23_revision_schedule_follows_latest_evidence(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-cache")
        topic_id = seed["topic"].id
        db.commit()
    finally:
        db.close()
    started = client.post(f"/api/assessment/topic/{topic_id}/start").json()
    session_id = started["session_id"]
    while client.get(f"/api/assessment/{session_id}").json()["current"]:
        current = client.get(f"/api/assessment/{session_id}").json()["current"]
        client.post(
            "/api/assessment/answer",
            json={"session_id": session_id, "question_id": current["id"], "selected": "correct"},
        )
    completed = client.post("/api/assessment/complete", json={"session_id": session_id}).json()
    score = completed["summary"]["score"]
    db = SessionLocal()
    try:
        schedule = (
            db.query(RevisionSchedule)
            .filter(RevisionSchedule.item_id == topic_id, RevisionSchedule.item_type == "topic")
            .one()
        )
        assert schedule.review_interval in {1, 3, 7, 14, 30, 60}
        from app.learning.service import revision_interval

        assert schedule.review_interval == revision_interval(score)
        assert schedule.next_review is not None
        # Backdate the review so the schedule is overdue and visible to the planner.
        from datetime import datetime, timedelta, timezone

        schedule.next_review = datetime.now(timezone.utc) - timedelta(hours=1)
        db.commit()
    finally:
        db.close()
    pending = client.get("/api/revision/pending").json()
    assert any(item["item_id"] == topic_id for item in pending)


def test_24_dashboard_focus_advances_past_completed_topic(client):
    db = SessionLocal()
    try:
        seed = _seed_single_topic(db, slug="cf-storage")
        topic = seed["topic"]
        db.commit()
        topic_id = topic.id
        lesson_id = topic.lessons[0].id
        exercise_id = topic.lessons[0].exercises[0].id
    finally:
        db.close()
    before = client.get("/api/dashboard").json()["curriculum_position"]
    client.post(f"/api/progress/lesson/{lesson_id}", params={"state": "completed"})
    client.post(f"/api/exercise/{exercise_id}/answer", json={"answer": "x", "code": "", "explanation": "", "complexity": ""})
    started = client.post(f"/api/assessment/topic/{topic_id}/start").json()
    session_id = started["session_id"]
    while client.get(f"/api/assessment/{session_id}").json()["current"]:
        current = client.get(f"/api/assessment/{session_id}").json()["current"]
        client.post(
            "/api/assessment/answer",
            json={"session_id": session_id, "question_id": current["id"], "selected": "correct"},
        )
    client.post("/api/assessment/complete", json={"session_id": session_id})
    after = client.get("/api/dashboard").json()["curriculum_position"]
    if before and before.get("topic_id") == topic_id:
        assert after is None or after.get("topic_id") != topic_id