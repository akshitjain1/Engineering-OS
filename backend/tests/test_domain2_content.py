from urllib.parse import urlparse

from app.content.import_curriculum import import_path, validate_manifest_group
from app.content.validate import validate_manifest
from app.db.models import CurriculumResource, CurriculumTopic, LessonExercise, LessonQuestion
from app.db.session import SessionLocal

from test_curriculum_v1 import ADVANCED_JAVA, D0, D1, D2, _load, _topic_slugs, _walk_topics


def test_domain2_validates_with_prior_domains():
    d0 = _load(D0)
    d1 = _load(D1)
    d2 = _load(D2)
    validate_manifest_group([d0, d1, d2])
    validate_manifest(d2, existing_topic_slugs=_topic_slugs(d0) | _topic_slugs(d1))


def test_domain2_every_topic_has_questions_and_exercises():
    for topic in _walk_topics(_load(D2)):
        lesson = topic["lessons"][0]
        assert 4 <= len(lesson["questions"]) <= 12, topic["slug"]
        assert lesson["exercises"], topic["slug"]
        assert 0.3 <= lesson["hours_estimated"] <= 2.5
        assert topic["mastery_criteria"]
        primaries = [r for r in lesson["resources"] if r.get("role") == "PRIMARY"]
        assert len(primaries) == 1, topic["slug"]
        assert primaries[0].get("url", "").startswith("https://")
        for question in lesson["questions"]:
            assert len(question["options"]) == 4
            assert question["answer"] in question["options"]
            assert question.get("explanation")
        for resource in lesson["resources"]:
            if resource.get("url"):
                parsed = urlparse(resource["url"])
                assert parsed.scheme == "https"
                assert parsed.netloc
                assert "leetcode.com/problems/" not in resource["url"]
        assert "video completion" not in " ".join(topic["mastery_criteria"]).lower()


def test_domain2_graph_and_java_gates():
    topics = list(_walk_topics(_load(D2)))
    assert topics[0]["slug"] == "dsa-algorithmic-thinking"
    assert topics[-1]["slug"] == "dsa-interview-hygiene"
    by_slug = {t["slug"]: t for t in topics}
    assert "java-arrays" in by_slug["dsa-array-traversal"]["prerequisites"]
    assert "java-map" in by_slug["dsa-hash-map"]["prerequisites"]
    assert "java-references" in by_slug["dsa-singly-linked-list"]["prerequisites"]
    assert "java-priority-queue" in by_slug["dsa-heap-structure"]["prerequisites"]
    for topic in topics:
        leak = set(topic.get("prerequisites") or []) & ADVANCED_JAVA
        assert not leak, f"{topic['slug']} {leak}"


def test_domain0_and_domain1_files_untouched_by_dsa_urls():
    d0 = D0.read_text(encoding="utf-8")
    d1 = D1.read_text(encoding="utf-8")
    assert "neetcode.io" not in d0 and "neetcode.io" not in d1
    assert "Abdul Bari Algorithms playlist" not in d0
    assert list(_walk_topics(_load(D0)))[0]["slug"] == "cf-bits-and-bytes"
    assert list(_walk_topics(_load(D1)))[0]["slug"] == "java-jdk-jre"


def test_v1_index_only_three_domains():
    index = _load(D0.parent.parent / "v1-index.yaml")
    # Original three spines remain first; later domains append additively.
    assert index["files"][:3] == [
        "foundation/00-computer-developer-foundations.yaml",
        "programming/01-java-programming.yaml",
        "dsa/02-data-structures-algorithms.yaml",
    ]
    assert len(index["files"]) >= 3


def test_domain2_import_after_prior_domains(client):
    import_path(D0)
    import_path(D1)
    stats = import_path(D2)
    assert stats["created"] >= 1
    db = SessionLocal()
    try:
        assert db.query(CurriculumTopic).filter_by(slug="dsa-algorithmic-thinking").one()
        hashing = db.query(CurriculumTopic).filter_by(slug="dsa-hash-map").one()
        assert "java-map" in hashing.prerequisites
        assert db.query(LessonQuestion).count() >= 800
        assert db.query(LessonExercise).count() >= 210
        assert db.query(CurriculumResource).count() >= 150
    finally:
        db.close()
