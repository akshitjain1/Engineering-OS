from urllib.parse import urlparse

from app.content.import_curriculum import import_path
from app.content.validate import validate_manifest
from app.db.models import CurriculumResource, CurriculumTopic, LessonExercise, LessonQuestion
from app.db.session import SessionLocal

from test_curriculum_v1 import D0, D1, D2, _load, _topic_slugs, _walk_topics


def test_domain1_validates_with_domain0_slugs():
    validate_manifest(_load(D1), existing_topic_slugs=_topic_slugs(_load(D0)))


def test_domain1_every_topic_has_questions_and_exercises():
    for topic in _walk_topics(_load(D1)):
        lesson = topic["lessons"][0]
        assert 3 <= len(lesson["questions"]) <= 10, topic["slug"]
        assert lesson["exercises"], topic["slug"]
        assert 0.3 <= lesson["hours_estimated"] <= 2.5
        assert topic["mastery_criteria"]
        for question in lesson["questions"]:
            assert len(question["options"]) == 4
            assert question["answer"] in question["options"]
            assert question.get("explanation")
        for resource in lesson["resources"]:
            if resource.get("url"):
                parsed = urlparse(resource["url"])
                assert parsed.scheme == "https"
                assert parsed.netloc
        assert "video completion" not in " ".join(topic["mastery_criteria"]).lower()


def test_domain1_graph_unchanged():
    topics = list(_walk_topics(_load(D1)))
    assert topics[0]["slug"] == "java-jdk-jre"
    assert topics[0]["prerequisites"] == ["cf-space-complexity-intro", "cf-dependency-management"]
    assert topics[-1]["slug"] == "java-api-hygiene"
    assert topics[-1].get("next_topic") is None
    by_slug = {t["slug"]: t for t in topics}
    assert by_slug["java-method-basics"]["next_topic"] == "java-overloading"
    assert by_slug["java-arrays"]["prerequisites"] == ["java-scope"]
    assert "java-streams" not in (by_slug["java-arrays"].get("prerequisites") or [])
    assert by_slug["java-priority-queue"]["next_topic"] == "java-generic-types"


def test_domain0_still_has_authored_content():
    d0 = _load(D0)
    topics = list(_walk_topics(d0))
    assert len(topics) == 64
    lesson = topics[0]["lessons"][0]
    assert lesson["questions"]
    assert any(
        (r.get("url") or "").startswith("https://cs50.harvard.edu/")
        for r in lesson["resources"]
    )


def test_domain0_and_domain1_remain_authored():
    d0 = list(_walk_topics(_load(D0)))
    d1 = list(_walk_topics(_load(D1)))
    assert len(d0) == 64
    assert len(d1) == 52
    assert d0[0]["lessons"][0]["questions"]
    assert d1[0]["lessons"][0]["questions"]
    assert any(
        (r.get("url") or "").startswith("https://dev.java/")
        for r in d1[0]["lessons"][0]["resources"]
    )
    assert "https://cs50.harvard.edu/" in D0.read_text(encoding="utf-8")


def test_domain1_import_after_domain0(client):
    import_path(D0)
    stats = import_path(D1)
    assert stats["created"] >= 1
    db = SessionLocal()
    try:
        assert db.query(CurriculumTopic).filter_by(slug="java-jdk-jre").one()
        java = db.query(CurriculumTopic).filter_by(slug="java-method-basics").one()
        assert java.prerequisites == ["java-break-continue"]
        assert db.query(LessonQuestion).count() >= 400
        assert db.query(LessonExercise).count() >= 110
        assert db.query(CurriculumResource).count() >= 80
    finally:
        db.close()
