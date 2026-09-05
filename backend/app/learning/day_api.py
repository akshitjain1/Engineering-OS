"""HTTP surface for the guided day session.

Every mutating endpoint returns the *next* thing to do. That is what lets the
frontend chain blocks without ever sending you back to a dashboard to re-orient.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.learning import day_engine

router = APIRouter()
DEFAULT_USER = "akshit"


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class GenerateBody(BaseModel):
    minutes: Optional[int] = Field(default=None, ge=20, le=600)
    force: bool = False


class ExtendBody(BaseModel):
    minutes: int = Field(default=60, ge=20, le=240)


class CompleteBody(BaseModel):
    minutes: Optional[int] = Field(default=None, ge=0, le=600)
    note: Optional[str] = None
    complete_topic: bool = False


class SkipBody(BaseModel):
    reason: Optional[str] = None


class JournalBody(BaseModel):
    learned: Optional[str] = None
    struggled: Optional[str] = None
    tomorrow: Optional[str] = None
    built: Optional[str] = None


@router.get("/api/day", tags=["Day"])
def read_day(db: Session = Depends(get_db)):
    """Today's session, read-only.

    This used to generate the day when none existed, which meant any page that
    read it wrote rows -- including /learn, which only wants the current topic
    for a banner. Callers that should build a day (only /today) act on
    needs_generation and POST /api/day/generate.
    """
    return day_engine.get_day(db, user_id=DEFAULT_USER)


@router.post("/api/day/generate", tags=["Day"])
def generate(body: GenerateBody | None = None, db: Session = Depends(get_db)):
    body = body or GenerateBody()
    return day_engine.generate_day(
        db, budget_minutes=body.minutes, force=body.force, user_id=DEFAULT_USER
    )


@router.post("/api/day/extend", tags=["Day"])
def extend(body: ExtendBody | None = None, db: Session = Depends(get_db)):
    """Append one more teaching cycle to today.

    Distinct from /generate, which rebuilds. This never touches an existing
    block and always advances to topics today has not covered yet.
    """
    body = body or ExtendBody()
    return day_engine.extend_day(db, minutes=body.minutes, user_id=DEFAULT_USER)


@router.post("/api/day/item/{item_id}/start", tags=["Day"])
def start(item_id: int, db: Session = Depends(get_db)):
    try:
        return day_engine.start_item(db, item_id, user_id=DEFAULT_USER)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/day/item/{item_id}/complete", tags=["Day"])
def complete(item_id: int, body: CompleteBody | None = None, db: Session = Depends(get_db)):
    body = body or CompleteBody()
    try:
        return day_engine.complete_item(
            db,
            item_id,
            minutes=body.minutes,
            note=body.note,
            complete_topic=body.complete_topic,
            user_id=DEFAULT_USER,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/day/item/{item_id}/skip", tags=["Day"])
def skip(item_id: int, body: SkipBody | None = None, db: Session = Depends(get_db)):
    body = body or SkipBody()
    try:
        return day_engine.skip_item(db, item_id, reason=body.reason, user_id=DEFAULT_USER)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/api/day/journal", tags=["Day"])
def journal(body: JournalBody, db: Session = Depends(get_db)):
    return day_engine.save_journal(
        db,
        learned=body.learned,
        struggled=body.struggled,
        tomorrow=body.tomorrow,
        built=body.built,
        user_id=DEFAULT_USER,
    )
