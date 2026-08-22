from app.db.models import CurriculumTrack, DSATopic, UserXP
from app.db.session import Base, SessionLocal


def test_shared_base_registers_models():
    assert "curriculum_tracks" in Base.metadata.tables
    assert "dsa_topics" in Base.metadata.tables
    assert "user_xp" in Base.metadata.tables


def test_can_insert_track(client):
    db = SessionLocal()
    try:
        db.add(CurriculumTrack(name="Test Track", description="x", order_index=0))
        db.commit()
        assert db.query(CurriculumTrack).count() == 1
        assert db.query(DSATopic).count() == 0
        assert db.query(UserXP).count() == 0
    finally:
        db.close()
