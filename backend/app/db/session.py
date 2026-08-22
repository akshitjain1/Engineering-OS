import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional in a bare venv
    load_dotenv = None

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

if load_dotenv:
    load_dotenv(BACKEND_DIR / ".env")


def resolve_database_url(url: str | None = None) -> str:
    """Resolve DATABASE_URL, anchoring relative SQLite paths to the backend directory."""
    raw = url if url is not None else os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    if not raw.startswith("sqlite:///"):
        return raw
    if raw.startswith("sqlite:///:memory:"):
        return raw
    path_part = raw[len("sqlite:///"):]
    path = Path(path_part)
    if not path.is_absolute():
        path = (BACKEND_DIR / path_part).resolve()
    return "sqlite:///" + path.as_posix()


DB_URL = resolve_database_url()

_engine_kwargs: dict = {"echo": False}
if DB_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    if ":memory:" in DB_URL:
        _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(DB_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Single metadata registry for all ORM models."""

    pass
