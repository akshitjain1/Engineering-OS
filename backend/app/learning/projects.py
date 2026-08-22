"""Engineering project unlock system.

Projects unlock when all prerequisite topic slugs have lessons_complete
(same completion index as the planner — not mastery bypass).
Project-slug prerequisites unlock after those projects are completed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.db.models import EngineeringProject, UserProjectProgress

DEFAULT_USER = "akshit"

PROJECT_SEEDS: list[dict[str, Any]] = [
    {
        "slug": "cli-calculator",
        "title": "CLI Calculator",
        "goal": "Build a command-line calculator that parses simple expressions.",
        "level": 1,
        "difficulty": "beginner",
        "estimated_hours": 2.0,
        "prerequisites": ["cf-shell", "cf-command-line"],
        "concepts_applied": ["CLI", "parsing", "error handling"],
        "milestones": ["Parse + - * /", "Handle errors", "README"],
        "deliverable": "Runnable CLI tool with tests for basic ops",
        "order_index": 10,
    },
    {
        "slug": "file-organizer",
        "title": "File Organizer",
        "goal": "Script that sorts files in a folder by extension or date.",
        "level": 1,
        "difficulty": "beginner",
        "estimated_hours": 3.0,
        "prerequisites": ["cf-filesystem-navigation", "cf-shell"],
        "concepts_applied": ["filesystem", "paths", "automation"],
        "milestones": ["List files", "Move by rule", "Dry-run mode"],
        "deliverable": "Python/Java script with dry-run flag",
        "order_index": 20,
    },
    {
        "slug": "java-dsa-lib",
        "title": "DSA Implementation Library",
        "goal": "Implement core structures/algorithms in Java with tests.",
        "level": 2,
        "difficulty": "intermediate",
        "estimated_hours": 12.0,
        "prerequisites": ["java-methods", "dsa-arrays"],
        "concepts_applied": ["Java", "DSA", "testing"],
        "milestones": ["Arrays/lists", "Trees/graphs subset", "README + tests"],
        "deliverable": "GitHub repo of implementations",
        "order_index": 35,
    },
    {
        "slug": "simple-rest-api",
        "title": "Simple REST API",
        "goal": "Expose CRUD endpoints for a single resource over HTTP.",
        "level": 1,
        "difficulty": "beginner",
        "estimated_hours": 4.0,
        "prerequisites": ["java-methods", "cf-command-line"],
        "concepts_applied": ["HTTP", "REST", "JSON"],
        "milestones": ["GET list", "POST create", "OpenAPI notes"],
        "deliverable": "FastAPI or Spring Boot hello CRUD service",
        "order_index": 40,
    },
    {
        "slug": "sql-crud-app",
        "title": "SQL CRUD App",
        "goal": "Persist a resource in SQLite/Postgres with create/read/update/delete.",
        "level": 1,
        "difficulty": "beginner",
        "estimated_hours": 4.0,
        "prerequisites": ["db-sql-select"],
        "concepts_applied": ["SQL", "transactions", "schema"],
        "milestones": ["Schema", "CRUD queries", "CLI or API front"],
        "deliverable": "App with SQL migrations and CRUD",
        "order_index": 45,
    },
    {
        "slug": "auth-service",
        "title": "Auth Service",
        "goal": "Register/login with hashed passwords and session or JWT tokens.",
        "level": 2,
        "difficulty": "intermediate",
        "estimated_hours": 8.0,
        "prerequisites": ["simple-rest-api", "sql-crud-app"],
        "concepts_applied": ["auth", "hashing", "sessions"],
        "milestones": ["Register", "Login", "Protected route"],
        "deliverable": "Auth microservice with tests",
        "order_index": 50,
    },
    {
        "slug": "fullstack-todo",
        "title": "Fullstack Todo",
        "goal": "End-to-end todo app with API + simple UI.",
        "level": 2,
        "difficulty": "intermediate",
        "estimated_hours": 10.0,
        "prerequisites": ["simple-rest-api", "web-react-intro"],
        "concepts_applied": ["fullstack", "CRUD", "UI"],
        "milestones": ["API", "UI list/add", "Persist"],
        "deliverable": "Deployable todo app",
        "order_index": 60,
    },
    {
        "slug": "dockerized-service",
        "title": "Dockerized Service",
        "goal": "Containerize an API with Compose for app + DB.",
        "level": 2,
        "difficulty": "intermediate",
        "estimated_hours": 6.0,
        "prerequisites": ["ops-docker-intro", "simple-rest-api"],
        "concepts_applied": ["Docker", "Compose", "ports"],
        "milestones": ["Dockerfile", "Compose", "README runbook"],
        "deliverable": "docker compose up demo",
        "order_index": 65,
    },
    {
        "slug": "data-analysis-project",
        "title": "Data Analysis Project",
        "goal": "Clean a dataset, EDA, and written findings.",
        "level": 2,
        "difficulty": "intermediate",
        "estimated_hours": 8.0,
        "prerequisites": ["ds-eda"],
        "concepts_applied": ["Pandas", "EDA", "communication"],
        "milestones": ["Clean", "EDA notebook", "1-page findings"],
        "deliverable": "Notebook + findings markdown",
        "order_index": 70,
    },
    {
        "slug": "ml-prediction-stub",
        "title": "Classical ML Project",
        "goal": "Train a sklearn model and serve a predict endpoint.",
        "level": 3,
        "difficulty": "intermediate",
        "estimated_hours": 10.0,
        "prerequisites": ["ml-sklearn-pipeline", "be-fastapi-intro"],
        "concepts_applied": ["sklearn", "train/serve", "metrics"],
        "milestones": ["Train", "Evaluate", "Predict API"],
        "deliverable": "Notebook + FastAPI predict service",
        "order_index": 80,
    },
    {
        "slug": "ml-deploy-project",
        "title": "ML Deployment Project",
        "goal": "Package, serve, and document a model service.",
        "level": 3,
        "difficulty": "advanced",
        "estimated_hours": 12.0,
        "prerequisites": ["mlops-serving", "ops-docker-intro"],
        "concepts_applied": ["MLOps", "Docker", "APIs"],
        "milestones": ["Package", "Serve", "Runbook"],
        "deliverable": "Deployable model API",
        "order_index": 85,
    },
    {
        "slug": "dl-vision-or-text",
        "title": "Deep Learning Mini-Project",
        "goal": "Train a small PyTorch model on a toy vision or text task.",
        "level": 3,
        "difficulty": "advanced",
        "estimated_hours": 14.0,
        "prerequisites": ["dl-nn-basics"],
        "concepts_applied": ["PyTorch", "training loop", "eval"],
        "milestones": ["Dataset", "Train", "Report metrics"],
        "deliverable": "Training notebook + metrics",
        "order_index": 90,
    },
    {
        "slug": "rag-mini-app",
        "title": "RAG Application",
        "goal": "Retrieve chunks and ground answers with an LLM stub/API.",
        "level": 4,
        "difficulty": "advanced",
        "estimated_hours": 16.0,
        "prerequisites": ["genai-rag", "fullstack-todo"],
        "concepts_applied": ["embeddings", "retrieval", "RAG"],
        "milestones": ["Index", "Retrieve", "Answer + eval"],
        "deliverable": "RAG demo with README",
        "order_index": 100,
    },
    {
        "slug": "ai-agent-system",
        "title": "AI Agent System",
        "goal": "Tool-using agent with guardrails and basic eval.",
        "level": 4,
        "difficulty": "advanced",
        "estimated_hours": 18.0,
        "prerequisites": ["genai-agents", "genai-eval"],
        "concepts_applied": ["agents", "tools", "evals"],
        "milestones": ["Tools", "Loop", "Eval harness"],
        "deliverable": "Agent repo with eval notes",
        "order_index": 110,
    },
    {
        "slug": "ai-backend-portfolio",
        "title": "AI Engineering Capstone",
        "goal": "Ship a polished AI/backend portfolio system with deploy notes.",
        "level": 4,
        "difficulty": "advanced",
        "estimated_hours": 24.0,
        "prerequisites": ["rag-mini-app", "ml-deploy-project", "auth-service"],
        "concepts_applied": ["deploy", "portfolio", "system design"],
        "milestones": ["Architecture", "Deploy", "Case study"],
        "deliverable": "Public portfolio project + deploy guide",
        "order_index": 120,
    },
]

PROJECT_SLUGS = {spec["slug"] for spec in PROJECT_SEEDS}


def seed_projects(db: Session) -> dict[str, int]:
    created = 0
    updated = 0
    for spec in PROJECT_SEEDS:
        row = db.query(EngineeringProject).filter(EngineeringProject.slug == spec["slug"]).first()
        fields = {k: v for k, v in spec.items() if k != "slug"}
        if row:
            for key, value in fields.items():
                setattr(row, key, value)
            updated += 1
        else:
            db.add(EngineeringProject(slug=spec["slug"], **fields))
            created += 1
    db.flush()
    return {"created": created, "updated": updated}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _prereqs_satisfied(
    prereqs: list[str],
    completion: dict[str, bool],
    project_done: set[str],
) -> bool:
    for ref in prereqs or []:
        if ref in PROJECT_SLUGS or ref in project_done:
            if ref not in project_done:
                return False
        elif not completion.get(ref):
            return False
    return True


def _compute_state(
    project: EngineeringProject,
    progress: Optional[UserProjectProgress],
    completion: dict[str, bool],
    project_done: set[str],
) -> str:
    if progress and progress.state == "completed":
        return "completed"
    if progress and progress.state == "in_progress":
        return "in_progress"
    if not _prereqs_satisfied(list(project.prerequisites or []), completion, project_done):
        return "locked"
    return "available"


def sync_project_unlocks(db: Session, user_id: str = DEFAULT_USER) -> None:
    from app.learning.service import topic_completion_index

    seed_projects(db)
    completion = topic_completion_index(db, user_id)
    projects = db.query(EngineeringProject).order_by(EngineeringProject.order_index).all()
    progress_rows = {
        row.project_id: row
        for row in db.query(UserProjectProgress)
        .filter(UserProjectProgress.user_id == user_id)
        .all()
    }
    # Multi-pass so project→project unlocks resolve in order
    for _ in range(len(projects) + 1):
        project_done = {
            p.slug
            for p in projects
            if progress_rows.get(p.id) and progress_rows[p.id].state == "completed"
        }
        changed = False
        for project in projects:
            progress = progress_rows.get(project.id)
            state = _compute_state(project, progress, completion, project_done)
            if progress is None:
                progress = UserProjectProgress(
                    user_id=user_id, project_id=project.id, state=state
                )
                db.add(progress)
                progress_rows[project.id] = progress
                changed = True
            elif progress.state == "completed":
                continue
            elif progress.state == "in_progress" and state != "locked":
                continue
            elif progress.state != state:
                progress.state = state
                changed = True
        if not changed:
            break
    db.flush()


def serialize_project(project: EngineeringProject, state: str) -> dict[str, Any]:
    return {
        "id": project.id,
        "slug": project.slug,
        "title": project.title,
        "goal": project.goal,
        "level": project.level,
        "difficulty": project.difficulty,
        "estimated_hours": project.estimated_hours,
        "prerequisites": list(project.prerequisites or []),
        "concepts_applied": list(project.concepts_applied or []),
        "milestones": list(project.milestones or []),
        "deliverable": project.deliverable,
        "order_index": project.order_index,
        "state": state,
    }


def list_projects(db: Session, user_id: str = DEFAULT_USER) -> dict[str, list[dict[str, Any]]]:
    sync_project_unlocks(db, user_id)
    projects = db.query(EngineeringProject).order_by(EngineeringProject.order_index).all()
    progress = {
        row.project_id: row
        for row in db.query(UserProjectProgress)
        .filter(UserProjectProgress.user_id == user_id)
        .all()
    }
    buckets: dict[str, list[dict[str, Any]]] = {
        "available": [],
        "locked": [],
        "in_progress": [],
        "completed": [],
    }
    for project in projects:
        row = progress.get(project.id)
        state = row.state if row else "locked"
        buckets.setdefault(state, []).append(serialize_project(project, state))
    return buckets


def start_project(db: Session, project_id: int, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    sync_project_unlocks(db, user_id)
    project = db.get(EngineeringProject, project_id)
    if not project:
        raise ValueError("project not found")
    progress = (
        db.query(UserProjectProgress)
        .filter(
            UserProjectProgress.user_id == user_id,
            UserProjectProgress.project_id == project_id,
        )
        .first()
    )
    if not progress or progress.state == "locked":
        raise PermissionError("project is locked")
    if progress.state == "completed":
        return serialize_project(project, "completed")
    progress.state = "in_progress"
    progress.started_at = progress.started_at or _now()
    db.flush()
    return serialize_project(project, progress.state)


def complete_project(db: Session, project_id: int, user_id: str = DEFAULT_USER) -> dict[str, Any]:
    sync_project_unlocks(db, user_id)
    project = db.get(EngineeringProject, project_id)
    if not project:
        raise ValueError("project not found")
    progress = (
        db.query(UserProjectProgress)
        .filter(
            UserProjectProgress.user_id == user_id,
            UserProjectProgress.project_id == project_id,
        )
        .first()
    )
    if not progress or progress.state == "locked":
        raise PermissionError("project is locked")
    progress.state = "completed"
    progress.started_at = progress.started_at or _now()
    progress.completed_at = _now()
    db.flush()
    sync_project_unlocks(db, user_id)
    return serialize_project(project, "completed")
