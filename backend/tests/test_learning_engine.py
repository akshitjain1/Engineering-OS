from app.db.session import SessionLocal
from app.db.models import (
    CurriculumLesson,
    CurriculumLevel,
    CurriculumModule,
    CurriculumSubject,
    CurriculumTopic,
    CurriculumTrack,
    RevisionSchedule,
    UserProgress,
    UserXP,
    TopicMastery,
)
from app.learning.diagnostic import score_implementation, score_mcq, score_response
from app.learning.diagnostic_bank import domain_counts, questions_by_id
from app.learning.mastery import mastery_score, pace_from_score, status_from_score, summarize_mastery
from app.learning.planner import RevisionView, TopicView, build_daily_plan
from app.learning.streak import day_is_meaningful, record_activity, refresh_streak_for_date
from app.learning.xp import award_xp


def test_mastery_score_redistributes_missing_category():
    evidence = [
        {"category": "conceptual", "score": 100},
        {"category": "problem_solving", "score": 80},
        {"category": "explanation", "score": 50},
    ]
    score = mastery_score(evidence)
    assert score is not None
    assert 75 <= score <= 90


def test_score_status_threshold_mapping():
    cases = [
        (100, "MASTERED", "FAST"),
        (90, "MASTERED", "FAST"),
        (89, "FAMILIAR", "NORMAL"),
        (75, "FAMILIAR", "NORMAL"),
        (74, "LEARNING", "DEEP"),
        (50, "LEARNING", "DEEP"),
        (49, "NEEDS_REVIEW", "REMEDIAL"),
        (0, "NEEDS_REVIEW", "REMEDIAL"),
        (None, "UNKNOWN", "FOUNDATION"),
    ]
    for score, status, pace in cases:
        assert status_from_score(score) == status
        assert pace_from_score(score) == pace


def test_score_100_is_capped_for_dsa_mcq_only():
    evidence = [{"category": "conceptual", "score": 100, "source": "diagnostic"}]
    summary = summarize_mastery("dsa-quick-sort", evidence)
    assert summary["mastery_score"] == 100
    assert summary["status"] == "FAMILIAR"
    assert summary["pace_mode"] == "FAST"
    assert summary["implementation_required"] is True
    assert summary["has_implementation_evidence"] is False


def test_java_loops_100_is_capped_without_implementation():
    summary = summarize_mastery("java-loops", [{"category": "conceptual", "score": 100, "source": "diagnostic"}])
    assert summary["status"] == "FAMILIAR"
    assert summary["pace_mode"] == "FAST"


def test_dsa_with_implementation_still_mastered():
    evidence = [
        {"category": "conceptual", "score": 95, "source": "diagnostic"},
        {"category": "implementation", "score": 90, "source": "exercise"},
        {"category": "problem_solving", "score": 92, "source": "diagnostic"},
        {"category": "explanation", "score": 90, "source": "diagnostic"},
    ]
    summary = summarize_mastery("dsa-graph-bfs", evidence)
    assert summary["status"] == "MASTERED"
    assert summary["has_implementation_evidence"] is True


def test_diagnostic_does_not_drop_implementation_evidence():
    evidence = [
        {"category": "implementation", "score": 90, "source": "exercise"},
        {"category": "conceptual", "score": 40, "source": "diagnostic"},
    ]
    summary = summarize_mastery("dsa-hash-set", evidence)
    assert summary["has_implementation_evidence"] is True
    assert summary["mastery_score"] is not None
    # Both categories remain; diagnostic conceptual does not erase implementation.
    from app.learning.mastery import average_category_scores

    cats = average_category_scores(evidence)
    assert cats["implementation"] == 90
    assert cats["conceptual"] == 40


def test_one_question_maps_to_primary_and_secondary_deterministically():
    item = questions_by_id()["dsa-27"]
    slugs = list(item["topics"]) + list(item.get("secondary") or [])
    assert slugs == ["dsa-hash-map", "dsa-big-o"]
    score = score_response(item, {"selected": item["answer"]})
    for slug in slugs:
        summary = summarize_mastery(slug, [{"category": item["category"], "score": score, "source": "diagnostic"}])
        assert summary["mastery_score"] == 100
        if slug == "dsa-big-o":
            assert summary["status"] == "MASTERED"
        else:
            # implementation topics cannot MASTER on MCQ evidence alone
            assert summary["status"] == "FAMILIAR"


def test_thresholds_and_pace():
    assert status_from_score(40) == "NEEDS_REVIEW"
    assert status_from_score(60) == "LEARNING"
    assert status_from_score(80) == "FAMILIAR"
    assert status_from_score(95) == "MASTERED"
    assert pace_from_score(None) == "FOUNDATION"
    assert pace_from_score(40) == "REMEDIAL"
    assert pace_from_score(60) == "DEEP"
    assert pace_from_score(80) == "NORMAL"
    assert pace_from_score(95) == "FAST"


def test_diagnostic_bank_size_and_mapping():
    counts = domain_counts()
    assert 15 <= counts["foundations"] <= 20
    assert 20 <= counts["java"] <= 25
    assert 30 <= counts["dsa"] <= 40
    item = questions_by_id()["dsa-27"]
    assert "dsa-hash-map" in item["topics"]
    assert "dsa-big-o" in item["secondary"]


def test_diagnostic_scoring_types():
    assert score_mcq("O(1)", "O(1)") == 100
    assert score_mcq("O(n)", "O(1)") == 0
    impl = score_implementation(
        {
            "code": "for (int i=0,j=n-1;i<j;i++,j--) swap(a,i,j);",
            "explanation": "Two pointers swap from both ends until they meet.",
            "complexity": "O(n)",
        },
        "O(n)",
    )
    assert impl == 100
    assert score_implementation({"code": "", "explanation": "x", "complexity": "O(n)"}) == 0
    q = questions_by_id()["java-01"]
    assert score_response(q, {"selected": q["answer"]}) == 100


def _views():
    arrays = TopicView(
        id=1,
        slug="java-arrays",
        name="Java arrays",
        locked=False,
        lessons_complete=False,
        domain="java",
        unfinished_exercises=2,
        practice_pending=1,
    )
    refs = TopicView(
        id=2,
        slug="java-references",
        name="Java references",
        locked=False,
        lessons_complete=True,
        domain="java",
        unfinished_exercises=0,
        practice_pending=0,
    )
    window = TopicView(
        id=3,
        slug="dsa-window-variable",
        name="Sliding Window",
        locked=True,
        lessons_complete=False,
        domain="dsa",
        prerequisite_slugs=["java-arrays"],
    )
    search = TopicView(
        id=4,
        slug="dsa-binary-search-classic",
        name="Binary search",
        locked=False,
        lessons_complete=False,
        domain="dsa",
        prerequisite_slugs=["java-arrays"],
    )
    return [arrays, refs, window, search]


def test_daily_plan_respects_time_budget():
    plan = build_daily_plan(budget_minutes=60, topics=_views(), overdue_revisions=[])
    assert plan["total_minutes"] <= 60
    assert plan["budget_minutes"] == 60
    assert all(item["minutes"] > 0 for item in plan["items"])


def test_cursor_topic_is_planned_first_and_stays_in_sequence():
    plan = build_daily_plan(budget_minutes=60, topics=_views(), overdue_revisions=[])
    assert plan["items"][0]["type"] == "LEARN"
    assert plan["items"][0]["topic_slug"] == "java-arrays"
    assert "sequence" in plan["items"][0]["why"].lower()
    assert "mastery" not in plan["items"][0]["why"].lower()
    assert "diagnostic" not in plan["items"][0]["why"].lower()


def test_cursor_gets_practice_and_build_when_activities_exist():
    plan = build_daily_plan(budget_minutes=120, topics=_views(), overdue_revisions=[])
    types = [item["type"] for item in plan["items"] if item.get("topic_slug") == "java-arrays"]
    assert "PRACTICE" in types
    assert "BUILD" in types
    practice = next(item for item in plan["items"] if item["type"] == "PRACTICE")
    assert "practice" in practice["why"].lower()
    build = next(item for item in plan["items"] if item["type"] == "BUILD")
    assert "implementation" in build["why"].lower()


def test_completed_topics_never_get_learn_items():
    plan = build_daily_plan(budget_minutes=180, topics=_views(), overdue_revisions=[])
    learn_slugs = [item["topic_slug"] for item in plan["items"] if item["type"] == "LEARN"]
    assert "java-references" not in learn_slugs


def test_locked_topic_never_in_plan():
    plan = build_daily_plan(budget_minutes=180, topics=_views(), overdue_revisions=[])
    assert all(item.get("topic_slug") != "dsa-window-variable" for item in plan["items"])


def test_review_comes_first():
    plan = build_daily_plan(
        budget_minutes=90,
        topics=_views(),
        overdue_revisions=[RevisionView(id=1, item_id=1, item_type="topic", title="Java arrays", topic_slug="java-arrays")],
    )
    assert plan["items"][0]["type"] == "REVIEW"
    assert "review" in plan["items"][0]["why"].lower()


def test_curriculum_sequence_intact_with_follow_on_learn():
    plan = build_daily_plan(budget_minutes=180, topics=_views(), overdue_revisions=[])
    learn = [item for item in plan["items"] if item["type"] == "LEARN"]
    slugs = [item["topic_slug"] for item in learn]
    assert slugs == ["java-arrays", "dsa-binary-search-classic"]


def test_follow_on_learn_only_when_budget_allows():
    plan = build_daily_plan(budget_minutes=40, topics=_views(), overdue_revisions=[])
    learn = [item for item in plan["items"] if item["type"] == "LEARN"]
    assert [item["topic_slug"] for item in learn] == ["java-arrays"]


def test_streak_requires_meaningful_activity(client):
    db = SessionLocal()
    try:
        record_activity(db, activity_type="open_dashboard", minutes=1, local_date="2026-08-18")
        db.commit()
        assert day_is_meaningful(db, "2026-08-18") is False
        record_activity(db, activity_type="exercise", minutes=5, local_date="2026-08-18")
        db.commit()
        streak = refresh_streak_for_date(db, "2026-08-18")
        db.commit()
        assert day_is_meaningful(db, "2026-08-18") is True
        assert streak.current_streak == 1
        record_activity(db, activity_type="exercise", minutes=5, local_date="2026-08-19")
        db.commit()
        streak = refresh_streak_for_date(db, "2026-08-19")
        db.commit()
        assert streak.current_streak == 2
        assert streak.longest_streak == 2
        record_activity(db, activity_type="assessment", minutes=5, local_date="2026-08-21")
        db.commit()
        streak = refresh_streak_for_date(db, "2026-08-21")
        db.commit()
        assert streak.current_streak == 1
        assert streak.longest_streak == 2
    finally:
        db.close()


def test_xp_idempotent_and_not_on_get(client):
    first = client.post("/api/xp/award", params={"amount": 10, "activity": "lesson", "idempotency_key": "k1"})
    assert first.json()["total_xp"] == 10
    second = client.post("/api/xp/award", params={"amount": 10, "activity": "lesson", "idempotency_key": "k1"})
    assert second.json()["xp_awarded"] == 0
    assert second.json()["total_xp"] == 10
    before = client.get("/api/xp").json()["total_xp"]
    again = client.get("/api/xp").json()["total_xp"]
    assert before == again == 10
    progress = client.get("/api/progress").json()
    assert progress["xp_earned"] == 10
    client.get("/api/progress")
    assert client.get("/api/xp").json()["total_xp"] == 10


def test_lesson_complete_not_mastered_and_duplicate_xp(client):
    db = SessionLocal()
    try:
        track = CurriculumTrack(name="SE", order_index=0)
        level = CurriculumLevel(name="L1", order_index=0)
        db.add_all([track, level])
        db.flush()
        subject = CurriculumSubject(name="Java", track_id=track.id, level_id=level.id, order_index=0)
        db.add(subject)
        db.flush()
        module = CurriculumModule(name="Arrays", subject_id=subject.id, order_index=0)
        db.add(module)
        db.flush()
        topic = CurriculumTopic(name="Java arrays", slug="java-arrays", module_id=module.id, order_index=0, prerequisites=[])
        db.add(topic)
        db.flush()
        lesson = CurriculumLesson(title="Arrays core", topic_id=topic.id, order_index=0)
        db.add(lesson)
        db.commit()
        lesson_id = lesson.id
        topic_id = topic.id
    finally:
        db.close()

    done = client.post(f"/api/progress/lesson/{lesson_id}", params={"state": "completed"})
    assert done.json()["xp_awarded"] == 10
    again = client.post(f"/api/progress/lesson/{lesson_id}", params={"state": "completed"})
    assert again.json()["xp_awarded"] == 0
    mastery = client.get("/api/mastery").json()
    arrays = next(item for item in mastery["items"] if item["topic_slug"] == "java-arrays")
    assert arrays["status"] != "MASTERED"
    assert arrays["status"] in {"LEARNING", "FAMILIAR", "NEEDS_REVIEW", "UNKNOWN"}
    detail = client.get(f"/api/mastery/{topic_id}").json()
    assert detail["topic_slug"] == "java-arrays"


def test_diagnostic_and_planner_endpoints(client):
    started = client.post("/api/diagnostic/start").json()
    assert started["started"] is True
    qid = started["current"]["id"]
    session_id = started["session_id"]
    question = questions_by_id()[qid]
    payload = {"session_id": session_id, "question_id": qid}
    if question["type"] in {"mcq", "tracing", "complexity"}:
        payload["selected"] = question["answer"]
    elif question["type"] == "short_answer":
        payload["text"] = question.get("answer") or "empty boundary overflow"
    else:
        payload.update(
            {
                "code": "int[] reverse(int[] a){return a;}",
                "explanation": "Placeholder reverse using two pointers in a real solution.",
                "complexity": question.get("expected_complexity") or "O(n)",
            }
        )
    answered = client.post("/api/diagnostic/answer", json=payload)
    assert answered.status_code == 200
    assert answered.json()["score"] >= 0
    completed = client.post("/api/diagnostic/complete", json={"session_id": session_id})
    assert completed.status_code == 200
    status = client.get("/api/diagnostic/status").json()
    assert status["completed"] is True
    xp_after = client.get("/api/xp").json()["total_xp"]
    client.get("/api/diagnostic/status")
    assert client.get("/api/xp").json()["total_xp"] == xp_after

    plan = client.post("/api/daily-plan/generate", json={"minutes": 60}).json()["plan"]
    assert plan["total_minutes"] <= 60
    assert client.post("/api/daily-plan/generate", json={"minutes": 45}).status_code == 400
    fetched = client.get("/api/daily-plan").json()["plan"]
    assert fetched["budget_minutes"] == 60
    streak = client.get("/api/streak").json()
    assert "current_streak" in streak
    assert client.get("/api/revision/pending").status_code == 200


def test_planner_does_not_reset_progress(client):
    db = SessionLocal()
    try:
        track = CurriculumTrack(name="SE2", order_index=0)
        level = CurriculumLevel(name="L1b", order_index=0)
        db.add_all([track, level])
        db.flush()
        subject = CurriculumSubject(name="DSA", track_id=track.id, level_id=level.id, order_index=0)
        db.add(subject)
        db.flush()
        module = CurriculumModule(name="Search", subject_id=subject.id, order_index=0)
        db.add(module)
        db.flush()
        topic = CurriculumTopic(name="Binary search", slug="dsa-binary-search-classic", module_id=module.id, order_index=0)
        db.add(topic)
        db.flush()
        lesson = CurriculumLesson(title="BS core", topic_id=topic.id, order_index=0, completion_status="completed")
        db.add(lesson)
        progress = UserProgress(user_id="akshit", lesson_id=lesson.id, progress_state="completed")
        db.add(progress)
        db.commit()
        before = db.query(UserProgress).count()
        state = progress.progress_state
    finally:
        db.close()
    client.post("/api/daily-plan/generate", json={"minutes": 30})
    db = SessionLocal()
    try:
        assert db.query(UserProgress).count() == before
        row = db.query(UserProgress).filter(UserProgress.progress_state == state).first()
        assert row is not None
    finally:
        db.close()


def test_revision_interval_ladder_from_mastery(client):
    db = SessionLocal()
    try:
        track = CurriculumTrack(name="SE3", order_index=0)
        level = CurriculumLevel(name="L1c", order_index=0)
        db.add_all([track, level])
        db.flush()
        subject = CurriculumSubject(name="Foundations", track_id=track.id, level_id=level.id, order_index=0)
        db.add(subject)
        db.flush()
        module = CurriculumModule(name="Bits", subject_id=subject.id, order_index=0)
        db.add(module)
        db.flush()
        topic = CurriculumTopic(name="Bits", slug="cf-bits-and-bytes", module_id=module.id, order_index=0)
        db.add(topic)
        db.commit()
        topic_id = topic.id
    finally:
        db.close()
    from app.learning.service import sync_mastery_row, upsert_evidence

    db = SessionLocal()
    try:
        upsert_evidence(db, topic_slug="cf-bits-and-bytes", source="diagnostic", category="conceptual", score=90)
        sync_mastery_row(db, "cf-bits-and-bytes", topic_id=topic_id)
        db.commit()
        row = db.query(RevisionSchedule).filter(RevisionSchedule.item_id == topic_id).first()
        assert row is not None
        assert row.review_interval in {1, 3, 7, 14, 30, 60}
        first_next = row.next_review
        upsert_evidence(db, topic_slug="cf-bits-and-bytes", source="diagnostic", category="conceptual", score=95)
        sync_mastery_row(db, "cf-bits-and-bytes", topic_id=topic_id)
        db.commit()
        assert db.query(UserProgress).count() == 0
        row = db.query(RevisionSchedule).filter(RevisionSchedule.item_id == topic_id).first()
        assert row.next_review is not None
        assert first_next is not None
    finally:
        db.close()


def test_award_xp_unit_idempotent(client):
    from app.db.session import SessionLocal as SL

    db = SL()
    try:
        a, rec = award_xp(db, idempotency_key="u1", amount=12, activity="exercise")
        b, rec2 = award_xp(db, idempotency_key="u1", amount=12, activity="exercise")
        db.commit()
        assert a == 12
        assert b == 0
        assert rec2.total_xp == 12
        assert db.query(UserXP).count() == 1
    finally:
        db.close()


def test_cursor_topic_still_in_plan_without_mastery_input():
    topics = [
        TopicView(
            id=1,
            slug="dsa-quick-sort",
            name="Quick sort",
            locked=False,
            lessons_complete=False,
            domain="dsa",
            unfinished_exercises=1,
            practice_pending=1,
        )
    ]
    plan = build_daily_plan(budget_minutes=60, topics=topics, overdue_revisions=[])
    learn = [item for item in plan["items"] if item["type"] == "LEARN"]
    assert learn
    assert learn[0]["topic_slug"] == "dsa-quick-sort"
    assert "skipped" not in learn[0]["why"].lower()


def test_stale_familiar_100_without_impl_reads_capped_and_no_xp_on_get(client):
    """A stale high score without implementation evidence reads capped, never MASTERED."""
    db = SessionLocal()
    try:
        db.add(
            TopicMastery(
                user_id="akshit",
                topic_slug="dsa-fast-slow",
                status="FAMILIAR",
                mastery_score=100,
                pace_mode="FAST",
                attempts=3,
                has_implementation_evidence=False,
            )
        )
        db.commit()
    finally:
        db.close()

    xp_before = client.get("/api/xp").json()["total_xp"]
    listed = client.get("/api/mastery").json()
    item = next(row for row in listed["items"] if row["topic_slug"] == "dsa-fast-slow")
    assert item["status"] == "FAMILIAR"
    assert item["mastery_score"] == 100
    assert item["pace_mode"] == "FAST"
    assert item["attempts"] == 3
    assert listed["counts"]["MASTERED"] == 0
    assert client.get("/api/xp").json()["total_xp"] == xp_before
    db = SessionLocal()
    try:
        stored = db.query(TopicMastery).filter(TopicMastery.topic_slug == "dsa-fast-slow").one()
        assert stored.status == "FAMILIAR"
        assert stored.attempts == 3
        assert db.query(TopicMastery).filter(TopicMastery.topic_slug == "dsa-fast-slow").count() == 1
        assert db.query(UserProgress).count() == 0
    finally:
        db.close()


def test_sync_does_not_duplicate_mastery_or_award_xp_for_already_high_score(client):
    from app.learning.service import sync_mastery_row, upsert_evidence

    db = SessionLocal()
    try:
        upsert_evidence(
            db,
            topic_slug="dsa-dijkstra",
            source="diagnostic",
            category="conceptual",
            score=100,
        )
        first = sync_mastery_row(db, "dsa-dijkstra", attempt=True)
        db.commit()
        first_id = first.id
        attempts = first.attempts
        xp_after_first = db.query(UserXP).first()
        xp_total = xp_after_first.total_xp if xp_after_first else 0

        second = sync_mastery_row(db, "dsa-dijkstra", attempt=True)
        db.commit()
        assert second.id == first_id
        assert db.query(TopicMastery).filter(TopicMastery.topic_slug == "dsa-dijkstra").count() == 1
        assert second.attempts == attempts + 1
        xp_row = db.query(UserXP).first()
        assert (xp_row.total_xp if xp_row else 0) == xp_total
        assert db.query(UserProgress).count() == 0
    finally:
        db.close()

