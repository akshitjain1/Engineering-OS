"""Personal learning engine HTTP API (diagnostic, mastery, planner, streak)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.models import TopicMastery
from app.db.session import SessionLocal
from app.learning import service
from app.learning.diagnostic_bank import domain_counts
from app.learning.streak import get_or_create_streak, serialize_streak

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DiagnosticAnswerBody(BaseModel):
    session_id: int
    question_id: str
    selected: Optional[str] = None
    answer: Optional[str] = None
    text: Optional[str] = None
    code: Optional[str] = None
    explanation: Optional[str] = None
    complexity: Optional[str] = None
    timezone: Optional[str] = None

    def payload(self) -> dict[str, Any]:
        return {
            "selected": self.selected,
            "answer": self.answer,
            "text": self.text,
            "code": self.code,
            "explanation": self.explanation,
            "complexity": self.complexity,
        }


class DiagnosticCompleteBody(BaseModel):
    session_id: int
    timezone: Optional[str] = None


class DailyPlanBody(BaseModel):
    minutes: Optional[int] = Field(None, ge=1, le=360)
    goal: str = service.DEFAULT_GOAL
    timezone: Optional[str] = None


class StudySettingsBody(BaseModel):
    weekday_capacity_minutes: Optional[int] = Field(None, ge=15, le=360)
    weekend_capacity_minutes: Optional[int] = Field(None, ge=15, le=480)
    timezone: Optional[str] = None
    revision_weighted: Optional[bool] = None


@router.get("/api/diagnostic/status", tags=["Diagnostic"])
def diagnostic_status(db: Session = Depends(get_db)):
    return {**service.diagnostic_status(db), "bank": domain_counts()}


@router.post("/api/diagnostic/start", tags=["Diagnostic"])
def diagnostic_start(db: Session = Depends(get_db)):
    result = service.diagnostic_start(db)
    db.commit()
    return {**result, "bank": domain_counts()}


@router.post("/api/diagnostic/answer", tags=["Diagnostic"])
def diagnostic_answer(body: DiagnosticAnswerBody, db: Session = Depends(get_db)):
    try:
        result = service.diagnostic_answer(
            db,
            session_id=body.session_id,
            question_id=body.question_id,
            payload=body.payload(),
            timezone_name=body.timezone,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return result


@router.post("/api/diagnostic/complete", tags=["Diagnostic"])
def diagnostic_complete(body: DiagnosticCompleteBody, db: Session = Depends(get_db)):
    try:
        result = service.diagnostic_complete(db, body.session_id, timezone_name=body.timezone)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return result


@router.get("/api/mastery", tags=["Mastery"])
def list_mastery(db: Session = Depends(get_db)):
    rows = (
        db.query(TopicMastery)
        .filter(TopicMastery.user_id == service.DEFAULT_USER)
        .order_by(TopicMastery.id)
        .all()
    )
    return {
        "counts": service.mastery_counts(db),
        "items": [service.serialize_mastery(row) for row in rows],
    }


@router.get("/api/mastery/{topic_id}", tags=["Mastery"])
def get_mastery(topic_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(TopicMastery)
        .filter(TopicMastery.user_id == service.DEFAULT_USER, TopicMastery.topic_id == topic_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="No mastery record for this topic yet")
    return service.serialize_mastery(row)


@router.get("/api/daily-plan", tags=["Planner"])
def get_daily_plan(timezone: Optional[str] = Query(None), db: Session = Depends(get_db)):
    plan = service.get_daily_plan(db, timezone_name=timezone)
    if not plan:
        return {"plan": None}
    return {"plan": plan}


@router.post("/api/daily-plan/generate", tags=["Planner"])
def generate_daily_plan(body: DailyPlanBody, db: Session = Depends(get_db)):
    minutes = body.minutes
    allowed = {30, 60, 90, 120, 180}
    if minutes is not None and minutes not in allowed:
        raise HTTPException(status_code=400, detail="minutes must be one of 30, 60, 90, 120, 180")
    plan = service.generate_daily_plan(
        db,
        budget_minutes=minutes,
        goal=body.goal,
        timezone_name=body.timezone,
    )
    db.commit()
    return {"plan": plan}


@router.get("/api/streak", tags=["Streak"])
def get_streak(db: Session = Depends(get_db)):
    return serialize_streak(get_or_create_streak(db))


@router.get("/api/dashboard", tags=["Dashboard"])
def dashboard(timezone: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return service.dashboard_snapshot(db, timezone_name=timezone)


@router.get("/api/study-tracks", tags=["Tracks"])
def study_tracks(db: Session = Depends(get_db)):
    return {"tracks": service.tracks_snapshot(db)}


@router.get("/api/study-settings", tags=["Settings"])
def get_study_settings(db: Session = Depends(get_db)):
    return service.serialize_study_settings(service.get_or_create_study_settings(db))


@router.put("/api/study-settings", tags=["Settings"])
def put_study_settings(body: StudySettingsBody, db: Session = Depends(get_db)):
    result = service.update_study_settings(
        db,
        weekday_capacity_minutes=body.weekday_capacity_minutes,
        weekend_capacity_minutes=body.weekend_capacity_minutes,
        timezone_name=body.timezone,
        revision_weighted=body.revision_weighted,
    )
    db.commit()
    return result


@router.get("/api/projects", tags=["Projects"])
def get_projects(db: Session = Depends(get_db)):
    from app.learning import projects as projects_svc

    result = projects_svc.list_projects(db)
    db.commit()
    return result


@router.post("/api/projects/{project_id}/start", tags=["Projects"])
def start_project(project_id: int, db: Session = Depends(get_db)):
    from app.learning import projects as projects_svc

    try:
        result = projects_svc.start_project(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    db.commit()
    return result


@router.post("/api/projects/{project_id}/complete", tags=["Projects"])
def complete_project(project_id: int, db: Session = Depends(get_db)):
    from app.learning import projects as projects_svc

    try:
        result = projects_svc.complete_project(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    db.commit()
    return result
