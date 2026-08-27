"""Source-first delivery: resource metadata, topic grouping, plan payload."""
from urllib.parse import parse_qs, urlparse
from app.content.import_curriculum import expand_targets, import_path
from app.content.importer import import_manifest
from app.content.resources import UNRESOLVED, VERIFIED, serialize_resource, youtube_video_id
from app.content.source_delivery import CS50_L0, CS50_L1, SOURCE_PATCHES, apply_source_delivery
from app.db.models import (
    CurriculumResource,
    CurriculumTopic,
    TopicMastery,
    UserXP,
)
from app.db.session import SessionLocal
from app.learning.xp import get_or_create_xp
from test_curriculum_v1 import D0, D1, D2, V1_INDEX, _load, _walk_topics


YOUTUBE_WATCH = "https://www.youtube.com/watch?v=0IAPZzGSbME"
PLAYLIST = "https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O"
DOCS = "https://dev.java/learn/language-basics/arrays/"


def _source_manifest(include_primary=True, youtube=True):
    resources = []
    if include_primary:
        if youtube:
            resources.append(
                {
                    "slug": "primary-video",
                    "title": "Abdul Bari — Introduction to Algorithms",
                    "type": "youtube_video",
                    "url": YOUTUBE_WATCH,
                    "provider": "Abdul Bari",
                    "role": "PRIMARY",
                    "order": 0,
                }
            )
        else:
            resources.append(
                {
                    "slug": "primary-docs",
                    "title": "Arrays",
                    "type": "documentation",
                    "url": DOCS,
                    "provider": "Dev.java",
                    "role": "PRIMARY",
                    "order": 0,
                }
            )
        resources.append(
            {
                "slug": "playlist-ref",
                "title": "Abdul Bari Algorithms playlist",
                "type": "youtube_playlist",
                "url": PLAYLIST,
                "provider": "Abdul Bari",
                "role": "REFERENCE",
                "order": 1,
            }
        )
        resources.append(
            {
                "slug": "practice-collection",
                "title": "NeetCode 150",
                "type": "exercise",
                "url": "https://neetcode.io/practice/practice/neetcode150",
                "provider": "NeetCode",
                "role": "PRACTICE",
                "order": 2,
            }
        )
    return {
        "schema_version": 1,
        "kind": "curriculum_manifest",
        "origin": "demo",
        "track": {
            "slug": "source-track",
            "name": "Source Track",
            "order": 0,
            "levels": [
                {
                    "slug": "source-level",
                    "name": "Source Level",
                    "order": 0,
                    "subjects": [
                        {
                            "slug": "source-subject",
                            "name": "Source Subject",
                            "order": 0,
                            "modules": [
                                {
                                    "slug": "source-module",
                                    "name": "Source Module",
                                    "order": 0,
                                    "topics": [
                                        {
                                            "slug": "source-topic",
                                            "name": "Source Topic",
                                            "order": 0,
                                            "prerequisites": [],
                                            "learning_objective": "Use the official source.",
                                            "lessons": [
                                                {
                                                    "slug": "source-lesson",
                                                    "title": "Source Lesson",
                                                    "order": 0,
                                                    "hours_estimated": 0.5,
                                                    "resources": resources,
                                                    "questions": [
                                                        {
                                                            "slug": "source-q1",
                                                            "prompt": "Which is a source-first move?",
                                                            "options": ["Open the official page", "Invent a lecture"],
                                                            "answer": "Open the official page",
                                                            "explanation": "Use the mapped URL.",
                                                        },
                                                        {
                                                            "slug": "source-q2",
                                                            "prompt": "Resource complete means?",
                                                            "options": ["Mastery", "Source consumed"],
                                                            "answer": "Source consumed",
                                                            "explanation": "Evidence of consumption only.",
                                                        },
                                                    ],
                                                    "exercises": [
                                                        {
                                                            "slug": "source-ex",
                                                            "title": "Implement from the source",
                                                            "instructions": "Do the official exercise, then write your own trace.",
                                                            "difficulty": "beginner",
                                                        },
                                                        {
                                                            "slug": "source-transfer",
                                                            "title": "Transfer aliasing",
                                                            "instructions": "TRANSFER: solve an unseen reference/aliasing problem.",
                                                            "difficulty": "intermediate",
                                                        },
                                                    ],
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
    }


def test_youtube_video_id_extracted_not_invented():
    assert youtube_video_id(YOUTUBE_WATCH) == "0IAPZzGSbME"
    assert youtube_video_id(PLAYLIST) is None
    assert youtube_video_id(None) is None
    assert youtube_video_id("https://dev.java/learn/") is None


def test_resource_metadata_serialization(client):
    db = SessionLocal()
    try:
        import_manifest(db, _source_manifest())
        row = db.query(CurriculumResource).filter_by(slug="primary-video").one()
        payload = serialize_resource(row)
        assert payload["role"] == "PRIMARY"
        assert payload["provider"] == "Abdul Bari"
        assert payload["video_id"] == "0IAPZzGSbME"
        assert payload["resource_type"] == "youtube"
        assert payload["verification_status"] == VERIFIED
        assert payload["embeddable"] is True
        assert payload["exact"] is True
        assert payload["url"] == YOUTUBE_WATCH
    finally:
        db.close()


def test_verified_youtube_and_playlist_not_confused(client):
    db = SessionLocal()
    try:
        import_manifest(db, _source_manifest())
        playlist = db.query(CurriculumResource).filter_by(slug="playlist-ref").one()
        payload = serialize_resource(playlist)
        assert payload["is_playlist"] is True
        assert payload["video_id"] is None
        assert payload["embeddable"] is False
        assert payload["verification_status"] == VERIFIED
        assert payload["url"] == PLAYLIST
    finally:
        db.close()


def test_unresolved_when_no_primary_resource(client):
    db = SessionLocal()
    try:
        import_manifest(db, _source_manifest(include_primary=False))
        topic = db.query(CurriculumTopic).filter_by(slug="source-topic").one()
        body = client.get(f"/api/topic/{topic.id}").json()
        assert body["resources_by_role"]["PRIMARY"] == []
        plan = client.post("/api/daily-plan/generate", json={"minutes": 60}).json()["plan"]
        learn = next(item for item in plan["items"] if item["type"] == "LEARN")
        assert learn["topic_slug"] == "source-topic"
        assert learn["resource_status"] == UNRESOLVED
        assert learn["resource_url"] is None
        assert learn["video_id"] is None
    finally:
        db.close()


def test_topic_endpoint_groups_resources_by_role(client):
    db = SessionLocal()
    try:
        import_manifest(db, _source_manifest())
        topic = db.query(CurriculumTopic).filter_by(slug="source-topic").one()
        body = client.get(f"/api/topic/{topic.id}").json()
        assert [item["role"] for item in body["resources_by_role"]["PRIMARY"]] == ["PRIMARY"]
        assert body["resources_by_role"]["REFERENCE"][0]["is_playlist"] is True
        assert body["resources_by_role"]["PRACTICE"][0]["exact"] is False
        assert body["implement"]
        assert body["transfer"]
        assert body["mastery"]["pace_mode"] == "FOUNDATION"
        assert "learning_objective" in body
        assert body["hours_estimated"] == 0.5
    finally:
        db.close()


def test_daily_plan_contains_source_metadata(client):
    db = SessionLocal()
    try:
        import_manifest(db, _source_manifest())
        plan = client.post("/api/daily-plan/generate", json={"minutes": 90}).json()["plan"]
        learn = next(item for item in plan["items"] if item["type"] == "LEARN")
        assert learn["activity_type"] == "LEARN"
        assert learn["topic_title"] == "Source Topic"
        assert learn["provider"] == "Abdul Bari"
        assert learn["resource_title"] == "Abdul Bari — Introduction to Algorithms"
        assert learn["resource_type"] == "youtube"
        assert learn["resource_url"] == YOUTUBE_WATCH
        assert learn["video_id"] == "0IAPZzGSbME"
        assert learn["verification_status"] == VERIFIED
        assert learn["section"] is None
        assert learn["lecture"] is None
        practice = next(item for item in plan["items"] if item["type"] == "PRACTICE")
        assert practice["resource_url"] == "https://neetcode.io/practice/practice/neetcode150"
        assert practice["exact"] is False
    finally:
        db.close()


def test_no_fabricated_resource_urls(client):
    db = SessionLocal()
    try:
        import_manifest(db, _source_manifest())
        urls = {row.url for row in db.query(CurriculumResource).all()}
        assert urls == {YOUTUBE_WATCH, PLAYLIST, "https://neetcode.io/practice/practice/neetcode150"}
        for row in db.query(CurriculumResource).all():
            payload = serialize_resource(row)
            if payload["video_id"]:
                assert payload["video_id"] in (payload["url"] or "")
    finally:
        db.close()


def test_resource_completion_is_not_mastery(client):
    db = SessionLocal()
    try:
        import_manifest(db, _source_manifest())
        resource = db.query(CurriculumResource).filter_by(slug="primary-video").one()
        topic = db.query(CurriculumTopic).filter_by(slug="source-topic").one()
        xp_before = get_or_create_xp(db).total_xp
        db.commit()
        client.post(f"/api/progress/resource/{resource.id}", json={"completed": True})
        db.expire_all()
        assert db.get(CurriculumResource, resource.id).completion_status == "completed"
        mastery = db.query(TopicMastery).filter_by(topic_slug="source-topic").first()
        assert mastery is None
        assert get_or_create_xp(db).total_xp == xp_before
        detail = client.get(f"/api/topic/{topic.id}").json()
        assert detail["mastery"]["status"] == "UNKNOWN"
        assert detail["resources_by_role"]["PRIMARY"][0]["completed"] is True
    finally:
        db.close()


def test_xp_unchanged_on_get_topic_and_plan(client):
    db = SessionLocal()
    try:
        import_manifest(db, _source_manifest())
        topic = db.query(CurriculumTopic).filter_by(slug="source-topic").one()
        get_or_create_xp(db)
        db.commit()
        before = client.get("/api/xp").json()["total_xp"]
        client.get(f"/api/topic/{topic.id}")
        client.get("/api/daily-plan")
        client.post("/api/daily-plan/generate", json={"minutes": 30})
        client.get("/api/dashboard")
        after = client.get("/api/xp").json()["total_xp"]
        assert after == before
        events = db.query(UserXP).filter_by(user_id="akshit").one()
        assert events.total_xp == before
    finally:
        db.close()


def test_curriculum_graph_unchanged_after_v1_import(client):
    yaml_graph = {}
    for path in (D0, D1, D2):
        for topic in _walk_topics(_load(path)):
            yaml_graph[topic["slug"]] = {
                "name": topic["name"],
                "prerequisites": list(topic.get("prerequisites") or []),
                "next_topic": topic.get("next_topic"),
            }
    for target in expand_targets(V1_INDEX):
        import_path(target)
    db = SessionLocal()
    try:
        rows = db.query(CurriculumTopic).filter(CurriculumTopic.slug.in_(yaml_graph.keys())).all()
        assert len(rows) == 222
        for row in rows:
            expected = yaml_graph[row.slug]
            assert row.name == expected["name"]
            assert list(row.prerequisites or []) == expected["prerequisites"]
            blob = row.description or ""
            if expected["next_topic"]:
                assert expected["next_topic"] in blob
        dashboard = client.get("/api/dashboard").json()
        assert dashboard["focus"]["current"]["slug"] == "cf-bits-and-bytes"
        assert dashboard["focus"]["current"]["primary"]["url"]
    finally:
        db.close()


def test_existing_resource_records_remain_valid(client):
    db = SessionLocal()
    try:
        import_manifest(db, _source_manifest(youtube=False))
        row = db.query(CurriculumResource).filter_by(slug="primary-docs").one()
        assert row.url == DOCS
        assert row.provider == "Dev.java"
        assert row.role == "PRIMARY"
        payload = serialize_resource(row)
        assert payload["resource_type"] == "documentation"
        assert payload["embeddable"] is False
        assert payload["verification_status"] == VERIFIED
    finally:
        db.close()


def _import_official_v1():
    for target in expand_targets(V1_INDEX):
        import_path(target)


def test_bits_and_bytes_has_usable_primary_after_delivery(client):
    _import_official_v1()
    db = SessionLocal()
    try:
        apply_source_delivery(db)
        topic = db.query(CurriculumTopic).filter_by(slug="cf-bits-and-bytes").one()
        body = client.get(f"/api/topic/{topic.id}").json()
        primaries = body["resources_by_role"]["PRIMARY"]
        assert primaries
        youtube = next(item for item in primaries if item.get("video_id") == "UuIEbpQms8o")
        assert youtube["url"] == CS50_L0
        assert youtube["embeddable"] is True
        assert youtube["is_playlist"] is False
        assert youtube["exact"] is True
        assert youtube["lecture"] == "Lecture 0"
        assert youtube["section"] is None
        assert body["source_readiness"] == "READY_EXACT"
        week = next(item for item in primaries if item.get("url") and "/weeks/0" in item["url"])
        assert week["exact"] is False
        assert week["embeddable"] is False
        xp_before = client.get("/api/xp").json()["total_xp"]
        client.get(f"/api/topic/{topic.id}")
        client.get("/api/dashboard")
        assert client.get("/api/xp").json()["total_xp"] == xp_before
        plan = client.post("/api/daily-plan/generate", json={"minutes": 60}).json()["plan"]
        learn = next(item for item in plan["items"] if item["type"] == "LEARN")
        assert learn["topic_slug"] == "cf-bits-and-bytes"
        assert learn["resource_url"]
        assert learn["video_id"] == "UuIEbpQms8o"
    finally:
        db.close()


def test_playlists_are_not_treated_as_videos_after_v1(client):
    _import_official_v1()
    db = SessionLocal()
    try:
        apply_source_delivery(db)
        playlists = [
            serialize_resource(row)
            for row in db.query(CurriculumResource).all()
            if serialize_resource(row)["is_playlist"]
        ]
        assert playlists
        for payload in playlists:
            assert payload["embeddable"] is False
            assert payload["video_id"] is None
    finally:
        db.close()


def test_documentation_is_not_embeddable(client):
    _import_official_v1()
    db = SessionLocal()
    try:
        apply_source_delivery(db)
        cpu = db.query(CurriculumTopic).filter_by(slug="cf-cpu").one()
        body = client.get(f"/api/topic/{cpu.id}").json()
        primary = body["resources_by_role"]["PRIMARY"][0]
        assert "geeksforgeeks.org" in primary["url"]
        assert primary["embeddable"] is False
        assert primary["video_id"] is None
        assert primary["source_readiness"] == "READY_DOCUMENTATION"
    finally:
        db.close()


def test_source_delivery_does_not_change_curriculum_graph(client):
    yaml_graph = {}
    for path in (D0, D1, D2):
        for topic in _walk_topics(_load(path)):
            yaml_graph[topic["slug"]] = {
                "name": topic["name"],
                "prerequisites": list(topic.get("prerequisites") or []),
                "next_topic": topic.get("next_topic"),
            }
    _import_official_v1()
    db = SessionLocal()
    try:
        apply_source_delivery(db)
        rows = db.query(CurriculumTopic).filter(CurriculumTopic.slug.in_(yaml_graph.keys())).all()
        assert len(rows) == 222
        for row in rows:
            expected = yaml_graph[row.slug]
            assert row.name == expected["name"]
            assert list(row.prerequisites or []) == expected["prerequisites"]
        for spec in SOURCE_PATCHES:
            if spec["resource_type"] == "youtube_video":
                url = spec["url"]
                parsed = urlparse(url)
                query = parse_qs(parsed.query)

                video_id = query.get("v", [None])[0]

                assert video_id, f"YouTube PRIMARY missing video id in URL: {url}"

                row = db.query(CurriculumResource).filter(
                    CurriculumResource.slug == spec["slug"]
                ).first()

                assert row is not None, f"Missing resource row: {spec['slug']}"
                assert row.video_id == video_id, (
                    f"video_id mismatch for {spec['slug']}: "
                    f"DB={row.video_id}, URL={video_id}"
                )
                edge = db.query(CurriculumTopic).filter_by(slug="cf-edge-cases").one()
                body = client.get(f"/api/topic/{edge.id}").json()
                assert body["resources_by_role"]["PRIMARY"]
                assert body["source_readiness"] == "READY_DOCUMENTATION"
    finally:
        db.close()
