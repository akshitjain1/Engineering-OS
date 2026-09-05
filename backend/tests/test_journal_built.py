"""The day should ask what you built, and the study log should carry it.

study-activity renders three sections: DSA, Projects and Learning. Projects was
fed only by BUILD blocks, which appear on weekends and only when a project hint
exists -- so on a normal working day the section was empty while the actual
building happened at a job this app never sees.

The close-of-day form now asks, and the answer goes to that section.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.db import models
from app.db.session import Base, SessionLocal, engine
from app.learning import day_engine
from app.learning.day_models import DayJournal
from scripts.publish_study_activity import SEPARATOR, summarise_day

DAY = "2026-09-05"


@pytest.fixture
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _save(db, **fields):
    day_engine.local_today = lambda *a, **k: DAY
    result = day_engine.save_journal(db, **fields)
    db.commit()
    return result


def test_the_answer_is_stored_and_returned(db):
    result = _save(db, built="Shipped the retry queue at work")

    assert result["built"] == "Shipped the retry queue at work"
    row = db.query(DayJournal).filter(DayJournal.entry_date == DAY).one()
    assert row.built == "Shipped the retry queue at work"


def test_saving_one_field_does_not_wipe_the_others(db):
    """The form saves on blur, one field at a time."""
    _save(db, learned="Prefix sums")
    _save(db, built="Fixed a flaky test at work")

    row = db.query(DayJournal).filter(DayJournal.entry_date == DAY).one()
    assert row.learned == "Prefix sums"
    assert row.built == "Fixed a flaky test at work"


def test_it_reaches_the_projects_section(db):
    db.add(DayJournal(user_id="akshit", entry_date=DAY, built="Shipped the retry queue",
                      updated_at=datetime(2026, 9, 5, 20, 0)))
    db.commit()

    assert summarise_day(db, DAY)["projects"] == [f"Worked on{SEPARATOR}Shipped the retry queue"]


def test_a_blank_answer_publishes_nothing(db):
    """Most days there is nothing, and an empty bullet is worse than no bullet."""
    db.add(DayJournal(user_id="akshit", entry_date=DAY, built="   ",
                      updated_at=datetime(2026, 9, 5, 20, 0)))
    db.commit()

    assert summarise_day(db, DAY)["projects"] == []


def test_it_sits_alongside_a_build_block_rather_than_replacing_it(db):
    """A weekend BUILD block and job work are both project work."""
    from app.learning.day_models import DailyPlanItem

    db.add(DailyPlanItem(
        user_id="akshit", plan_date=DAY, position=0, activity_type="BUILD",
        title="Ship the parser", planned_minutes=45, actual_minutes=45, status="done",
    ))
    db.add(DayJournal(user_id="akshit", entry_date=DAY, built="Fixed a flaky test at work",
                      updated_at=datetime(2026, 9, 5, 20, 0)))
    db.commit()

    projects = summarise_day(db, DAY)["projects"]
    assert f"Ship the parser{SEPARATOR}45 min" in projects
    assert f"Worked on{SEPARATOR}Fixed a flaky test at work" in projects


def test_the_day_payload_exposes_it(db):
    """So the form can show what was written earlier in the day."""
    _save(db, built="Reviewed two PRs")
    payload = day_engine.get_day(db)

    assert payload["journal"]["built"] == "Reviewed two PRs"
