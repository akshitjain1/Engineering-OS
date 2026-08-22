from urllib.parse import urlparse

from app.content.import_curriculum import import_path
from app.content.validate import validate_manifest
from app.db.models import CurriculumResource, CurriculumTopic, LessonExercise, LessonQuestion
from app.db.session import SessionLocal

from test_curriculum_v1 import D0, D1, D2, _load, _walk_topics


def test_domain0_validates():
    validate_manifest(_load(D0))


def test_domain0_every_topic_has_questions_and_exercises():
    for topic in _walk_topics(_load(D0)):
        lesson = topic["lessons"][0]
        assert 3 <= len(lesson["questions"]) <= 8, topic["slug"]
        assert lesson["exercises"], topic["slug"]
        assert 0.3 <= lesson["hours_estimated"] <= 2.5
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


def test_domain0_graph_unchanged_from_structure():
    # Frozen after authoring: first topic empty prereqs, last next_topic None, sequential chain.
    topics = list(_walk_topics(_load(D0)))
    assert topics[0]["slug"] == "cf-bits-and-bytes"
    assert topics[0]["prerequisites"] == []
    assert topics[-1]["slug"] == "cf-space-complexity-intro"
    assert topics[-1].get("next_topic") is None
    by_slug = {t["slug"]: t for t in topics}
    assert by_slug["cf-binary"]["prerequisites"] == ["cf-bits-and-bytes"]
    assert by_slug["cf-shell"]["prerequisites"] == ["cf-os-environment-variables"]
    assert by_slug["cf-repository"]["prerequisites"] == ["cf-linux-environment-variables"]
    assert by_slug["cf-ide"]["prerequisites"] == ["cf-github-workflow", "cf-compiler"]
    assert by_slug["cf-problem-decomposition"]["prerequisites"] == ["cf-dependency-management"]
    assert by_slug["cf-github-workflow"]["next_topic"] == "cf-ide"
    assert by_slug["cf-dependency-management"]["next_topic"] == "cf-problem-decomposition"


def test_domain2_file_is_present():
    assert D2.is_file()


def test_domain0_import_creates_questions(client):
    stats = import_path(D0)
    assert stats["created"] >= 1
    db = SessionLocal()
    try:
        assert db.query(LessonQuestion).count() >= 200
        assert db.query(LessonExercise).count() >= 64
        assert db.query(CurriculumResource).count() >= 40
        topic = db.query(CurriculumTopic).filter_by(slug="cf-bits-and-bytes").one()
        assert topic.prerequisites == []
    finally:
        db.close()
