from pathlib import Path

import pytest
import yaml

from app.content.import_curriculum import expand_targets, import_path
from app.content.importer import import_manifest
from app.content.schema import ManifestError
from app.content.validate import validate_manifest
from app.db.models import CurriculumResource, CurriculumTopic
from app.db.session import SessionLocal

CURRICULUM = Path(__file__).resolve().parents[1] / "content" / "curriculum"
V1_INDEX = CURRICULUM / "v1-index.yaml"
D0 = CURRICULUM / "foundation" / "00-computer-developer-foundations.yaml"
D1 = CURRICULUM / "programming" / "01-java-programming.yaml"
D2 = CURRICULUM / "dsa" / "02-data-structures-algorithms.yaml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _topic_slugs(data: dict) -> set[str]:
    slugs = set()
    for level in data["track"]["levels"]:
        for subject in level["subjects"]:
            for module in subject["modules"]:
                for topic in module["topics"]:
                    slugs.add(topic["slug"])
    return slugs


def _counts(data: dict) -> tuple[int, int]:
    modules = topics = 0
    for level in data["track"]["levels"]:
        for subject in level["subjects"]:
            modules += len(subject["modules"])
            for module in subject["modules"]:
                topics += len(module["topics"])
    return modules, topics


def test_v1_files_exist():
    assert V1_INDEX.is_file()
    assert D0.is_file() and D1.is_file() and D2.is_file()


def test_v1_index_order():
    index = _load(V1_INDEX)
    assert index["kind"] == "curriculum_index"
    assert index["origin"] == "official"
    # Original three spines stay first; later domains append additively.
    assert index["files"][:3] == [
        "foundation/00-computer-developer-foundations.yaml",
        "programming/01-java-programming.yaml",
        "dsa/02-data-structures-algorithms.yaml",
    ]
    expanded = expand_targets(V1_INDEX)
    assert expanded[:3] == [D0.resolve(), D1.resolve(), D2.resolve()]
    assert len(index["files"]) >= 3


def test_official_manifests_validate_in_order():
    d0 = _load(D0)
    d1 = _load(D1)
    d2 = _load(D2)
    assert d0["origin"] == d1["origin"] == d2["origin"] == "official"

    validate_manifest(d0)
    validate_manifest(d1, existing_topic_slugs=_topic_slugs(d0))
    validate_manifest(d2, existing_topic_slugs=_topic_slugs(d0) | _topic_slugs(d1))

    assert _counts(d0) == (6, 64)
    assert _counts(d1) == (21, 52)
    assert _counts(d2) == (25, 106)


def test_no_invented_resource_urls():
    # Official manifests must not use http://. Domain 2 now has verified https resources.
    for path in (D0, D1, D2):
        text = path.read_text(encoding="utf-8")
        assert "http://" not in text
        data = _load(path)
        for topic in _walk_topics(data):
            assert topic["prerequisites"] is not None
            assert topic["learning_objective"]
            assert topic["mastery_criteria"]
            assert "video completion" not in " ".join(topic["mastery_criteria"]).lower()


def test_java_requires_foundations(client):
    d1 = _load(D1)
    with pytest.raises(ManifestError) as exc:
        validate_manifest(d1)
    assert "missing prerequisite" in str(exc.value)


def test_optional_url_is_skipped_on_import(client):
    db = SessionLocal()
    try:
        stats = import_manifest(
            db,
            {
                "schema_version": 1,
                "kind": "curriculum_manifest",
                "origin": "official",
                "track": {
                    "slug": "slot-track",
                    "name": "Slot Track",
                    "order": 9,
                    "levels": [
                        {
                            "slug": "slot-level",
                            "name": "Slot Level",
                            "order": 0,
                            "subjects": [
                                {
                                    "slug": "slot-subject",
                                    "name": "Slot Subject",
                                    "order": 0,
                                    "modules": [
                                        {
                                            "slug": "slot-module",
                                            "name": "Slot Module",
                                            "order": 0,
                                            "topics": [
                                                {
                                                    "slug": "slot-topic",
                                                    "name": "Slot Topic",
                                                    "order": 0,
                                                    "prerequisites": [],
                                                    "lessons": [
                                                        {
                                                            "slug": "slot-lesson",
                                                            "title": "Slot Lesson",
                                                            "order": 0,
                                                            "resources": [
                                                                {
                                                                    "slug": "slot-primary",
                                                                    "title": "Pending",
                                                                    "type": "other",
                                                                    "role": "PRIMARY",
                                                                    "order": 0,
                                                                }
                                                            ],
                                                            "questions": [],
                                                            "exercises": [],
                                                        }
                                                    ],
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                },
            },
        )
        assert stats["skipped_resources"] >= 1
        assert db.query(CurriculumResource).count() == 0
        assert db.query(CurriculumTopic).filter(CurriculumTopic.slug == "slot-topic").count() == 1
    finally:
        db.close()


def test_import_v1_index(client):
    totals = {"created": 0, "skipped_resources": 0}
    for path in expand_targets(V1_INDEX):
        stats = import_path(path)
        totals["created"] += stats["created"]
        totals["skipped_resources"] += stats["skipped_resources"]
    db = SessionLocal()
    try:
        assert db.query(CurriculumTopic).filter(CurriculumTopic.slug == "cf-bits-and-bytes").count() == 1
        assert db.query(CurriculumTopic).filter(CurriculumTopic.slug == "java-jdk-jre").count() == 1
        assert db.query(CurriculumTopic).filter(CurriculumTopic.slug == "dsa-algorithmic-thinking").count() == 1
        java = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "java-jdk-jre").one()
        assert "cf-space-complexity-intro" in java.prerequisites
        hashing = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "dsa-hash-map").one()
        assert "java-map" in hashing.prerequisites
        assert "java-streams" not in (hashing.prerequisites or [])
        linked = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "dsa-singly-linked-list").one()
        assert "java-classes-objects" in linked.prerequisites
        assert "java-references" in linked.prerequisites
        assert totals["created"] >= 1
        assert db.query(CurriculumResource).count() >= 1
    finally:
        db.close()


DEMO = CURRICULUM / "demo" / "rest-apis.yaml"
ADVANCED_JAVA = {
    "java-stream-pipeline",
    "java-stream-operations",
    "java-lambdas",
    "java-functional-interfaces",
    "java-threads",
    "java-synchronization-basics",
    "java-bytecode",
    "java-memory-model-basics",
    "java-gc-intro",
    "java-packages",
    "java-api-hygiene",
}


def _walk_topics(data: dict):
    for level in data["track"]["levels"]:
        for subject in level["subjects"]:
            for module in subject["modules"]:
                for topic in module["topics"]:
                    yield topic


def test_demo_curriculum_validates():
    validate_manifest(_load(DEMO))


def test_next_topic_targets_exist_in_same_file_or_are_null():
    for path in (D0, D1, D2):
        data = _load(path)
        slugs = _topic_slugs(data)
        for topic in _walk_topics(data):
            nxt = topic.get("next_topic")
            if nxt:
                assert nxt in slugs, f"{topic['slug']} next_topic {nxt} missing in {path.name}"


def test_dsa_not_gated_on_advanced_java():
    d2 = _load(D2)
    for topic in _walk_topics(d2):
        prereqs = set(topic.get("prerequisites") or [])
        leak = prereqs & ADVANCED_JAVA
        assert not leak, f"{topic['slug']} requires advanced Java {leak}"


def test_dsa_practice_layers_present():
    topic = next(t for t in _walk_topics(_load(D2)) if t["slug"] == "dsa-array-traversal")
    roles = [r["role"] for r in topic["lessons"][0]["resources"]]
    titles = " ".join(r["title"] for r in topic["lessons"][0]["resources"])
    blob = topic["lessons"][0]["description"] + " " + topic["description"]
    assert roles.count("PRIMARY") == 1
    assert "Abdul Bari" in titles
    assert "NeetCode" in titles
    assert "ArrayList" in blob or "vector" in blob or "C++" in blob
    assert "Java" in blob


def test_java_last_topic_does_not_force_dsa():
    d1 = _load(D1)
    last = list(_walk_topics(d1))[-1]
    assert last["slug"] == "java-api-hygiene"
    assert last.get("next_topic") is None


def test_index_group_validation():
    from app.content.import_curriculum import validate_manifest_group

    validate_manifest_group([_load(D0), _load(D1), _load(D2)])

