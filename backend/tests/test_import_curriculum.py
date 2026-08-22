from copy import deepcopy

import pytest

from app.content.importer import import_manifest
from app.content.schema import ManifestError
from app.content.validate import validate_manifest
from app.db.models import CurriculumLesson, CurriculumTopic, UserProgress
from app.db.session import SessionLocal


def _manifest(**overrides):
    data = {
        "schema_version": 1,
        "kind": "curriculum_manifest",
        "origin": "demo",
        "track": {
            "slug": "se",
            "name": "Software Engineering",
            "order": 0,
            "levels": [
                {
                    "slug": "l1",
                    "name": "Level 1",
                    "order": 0,
                    "subjects": [
                        {
                            "slug": "backend",
                            "name": "Backend",
                            "order": 0,
                            "modules": [
                                {
                                    "slug": "rest",
                                    "name": "REST",
                                    "order": 0,
                                    "topics": [
                                        {
                                            "slug": "http",
                                            "name": "HTTP Fundamentals",
                                            "order": 0,
                                            "prerequisites": [],
                                            "lessons": [
                                                {
                                                    "slug": "methods",
                                                    "title": "HTTP Methods",
                                                    "description": "Verbs",
                                                    "order": 0,
                                                    "resources": [
                                                        {
                                                            "slug": "mdn",
                                                            "title": "MDN",
                                                            "type": "documentation",
                                                            "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP",
                                                            "provider": "MDN",
                                                            "order": 0,
                                                        }
                                                    ],
                                                    "questions": [
                                                        {
                                                            "slug": "q1",
                                                            "prompt": "Which method is safe?",
                                                            "options": ["GET", "POST"],
                                                            "answer": "GET",
                                                            "explanation": "GET does not modify state.",
                                                        }
                                                    ],
                                                    "exercises": [
                                                        {
                                                            "slug": "ex1",
                                                            "title": "List status codes",
                                                            "instructions": "Write 1xx-5xx examples.",
                                                            "difficulty": "beginner",
                                                        }
                                                    ],
                                                }
                                            ],
                                        },
                                        {
                                            "slug": "rest-principles",
                                            "name": "REST Principles",
                                            "order": 1,
                                            "prerequisites": ["http"],
                                            "lessons": [
                                                {
                                                    "slug": "constraints",
                                                    "title": "REST constraints",
                                                    "order": 0,
                                                }
                                            ],
                                        },
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        },
    }
    data.update(overrides)
    return data


def test_valid_manifest():
    manifest = validate_manifest(_manifest())
    assert manifest.track.slug == "se"
    assert manifest.origin == "demo"


def test_duplicate_ids():
    data = _manifest()
    data["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"][1]["slug"] = "http"
    with pytest.raises(ManifestError) as exc:
        validate_manifest(data)
    assert "duplicate ID" in str(exc.value)


def test_missing_prerequisite():
    data = _manifest()
    data["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"][1]["prerequisites"] = ["missing-topic"]
    with pytest.raises(ManifestError) as exc:
        validate_manifest(data)
    assert "missing prerequisite" in str(exc.value)


def test_circular_prerequisite():
    data = _manifest()
    topics = data["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"]
    topics[0]["prerequisites"] = ["rest-principles"]
    topics[1]["prerequisites"] = ["http"]
    with pytest.raises(ManifestError) as exc:
        validate_manifest(data)
    assert "circular prerequisites" in str(exc.value)


def test_invalid_parent():
    data = _manifest()
    data["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"][0]["lessons"][0]["topic"] = "other-topic"
    with pytest.raises(ManifestError) as exc:
        validate_manifest(data)
    assert "invalid lesson reference" in str(exc.value)


def test_invalid_url():
    data = _manifest()
    data["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"][0]["lessons"][0]["resources"][0]["url"] = "not-a-url"
    with pytest.raises(ManifestError) as exc:
        validate_manifest(data)
    assert "invalid resource URL" in str(exc.value)


def test_duplicate_lesson_order():
    data = _manifest()
    lessons = data["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"][0]["lessons"]
    extra = deepcopy(lessons[0])
    extra["slug"] = "methods-2"
    extra["title"] = "HTTP Methods 2"
    extra["resources"] = []
    extra["questions"] = []
    extra["exercises"] = []
    extra["order"] = 0
    lessons.append(extra)
    with pytest.raises(ManifestError) as exc:
        validate_manifest(data)
    assert "duplicate lesson order" in str(exc.value)


def test_idempotent_import_and_update(client):
    db = SessionLocal()
    try:
        first = import_manifest(db, _manifest())
        assert first["created"] >= 1
        second = import_manifest(db, _manifest())
        assert second["created"] == 0
        topics = db.query(CurriculumTopic).filter(CurriculumTopic.slug == "http").all()
        assert len(topics) == 1

        updated = _manifest()
        updated["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"][0]["description"] = "Updated HTTP"
        third = import_manifest(db, updated)
        assert third["updated"] >= 1
        db.refresh(topics[0])
        assert topics[0].description == "Updated HTTP"
    finally:
        db.close()


def test_progress_preserved_on_reimport(client):
    db = SessionLocal()
    try:
        import_manifest(db, _manifest())
        lesson = db.query(CurriculumLesson).filter(CurriculumLesson.slug == "methods").one()
        lesson.completion_status = "completed"
        db.add(UserProgress(user_id="akshit", lesson_id=lesson.id, progress_state="completed"))
        db.commit()
        lesson_id = lesson.id

        changed = _manifest()
        changed["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"][0]["lessons"][0]["description"] = "New copy"
        import_manifest(db, changed)

        lesson = db.query(CurriculumLesson).filter(CurriculumLesson.slug == "methods").one()
        assert lesson.id == lesson_id
        assert lesson.completion_status == "completed"
        assert lesson.description == "New copy"
        progress = db.query(UserProgress).filter(UserProgress.lesson_id == lesson_id).one()
        assert progress.progress_state == "completed"
    finally:
        db.close()


def test_invalid_next_topic():
    data = _manifest()
    data["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"][0]["next_topic"] = "does-not-exist"
    with pytest.raises(ManifestError) as exc:
        validate_manifest(data)
    assert "missing next_topic" in str(exc.value)


def test_valid_next_topic_within_file():
    data = _manifest()
    data["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"][0]["next_topic"] = "rest-principles"
    validate_manifest(data)


def test_failed_validation_does_not_insert(client):
    db = SessionLocal()
    try:
        bad = _manifest()
        bad["track"]["levels"][0]["subjects"][0]["modules"][0]["topics"][1]["prerequisites"] = ["nope"]
        with pytest.raises(ManifestError):
            import_manifest(db, bad)
        assert db.query(CurriculumTopic).count() == 0
    finally:
        db.close()
