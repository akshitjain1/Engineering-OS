"""Seed demo curriculum, DSA patterns, and the single-user XP row."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path

from app.content.import_curriculum import import_path
from app.db.migrate import ensure_optional_columns
from app.db.session import SessionLocal, Base, engine
from app.db.models import DSATopic, UserProgress, UserXP

DSA_PATTERNS = [
    ("Arrays", "Arrays"),
    ("Strings", "Strings"),
    ("Hashing", "Hashing"),
    ("Two Pointers", "Two Pointers"),
    ("Sliding Window", "Sliding Window"),
    ("Stack", "Stack"),
    ("Queue", "Queue"),
    ("Linked List", "Linked List"),
    ("Binary Search", "Binary Search"),
    ("Recursion", "Recursion"),
    ("Trees", "Trees"),
    ("BST", "BST"),
    ("Heap", "Heap"),
    ("Graphs", "Graphs"),
    ("Greedy", "Greedy"),
    ("Backtracking", "Backtracking"),
    ("Dynamic Programming", "Dynamic Programming"),
    ("Bit Manipulation", "Bit Manipulation"),
    ("Intervals", "Intervals"),
]

DEMO_MANIFEST = Path(__file__).resolve().parent / "content" / "curriculum" / "demo" / "rest-apis.yaml"


def _ensure_user(db):
    xp_rows = db.query(UserXP).filter(UserXP.user_id == "akshit").order_by(UserXP.id).all()
    if not xp_rows:
        db.add(UserXP(user_id="akshit", total_xp=0, level=1, xp_this_session=0, sessions_completed=0))
    else:
        primary = xp_rows[0]
        for duplicate in xp_rows[1:]:
            primary.total_xp = (primary.total_xp or 0) + (duplicate.total_xp or 0)
            db.delete(duplicate)
        primary.level = max(1, (primary.total_xp // 100) + 1)

    overview = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == "akshit",
            UserProgress.lesson_id.is_(None),
            UserProgress.topic_id.is_(None),
            UserProgress.dsa_topic_id.is_(None),
        )
        .first()
    )
    if not overview:
        db.add(UserProgress(user_id="akshit"))


def _ensure_dsa(db):
    existing = {row.name for row in db.query(DSATopic).all()}
    for name, pattern in DSA_PATTERNS:
        if name not in existing:
            db.add(DSATopic(name=name, pattern=pattern))


def seed():
    Base.metadata.create_all(bind=engine)
    ensure_optional_columns(engine)
    stats = import_path(DEMO_MANIFEST)
    print(
        f"Demo curriculum imported: created={stats['created']} "
        f"updated={stats['updated']} unchanged={stats['unchanged']}"
    )
    db = SessionLocal()
    try:
        _ensure_user(db)
        _ensure_dsa(db)
        db.commit()
        print("Seed complete (DEMO curriculum + DSA patterns + user row).")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
