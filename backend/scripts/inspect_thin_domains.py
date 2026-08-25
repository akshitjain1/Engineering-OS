"""Inspect thin AI/ML domains + find 'Other' topics."""
import sys
sys.path.insert(0, r"D:\Akshit Personal OS\backend")
from app.db.session import SessionLocal
from app.db.models import CurriculumTopic

db = SessionLocal()
try:
    topics = db.query(CurriculumTopic).order_by(CurriculumTopic.module_id, CurriculumTopic.order_index).all()
    print("=== ML / DL / CV / MATH / NLP / GENAI / AI / PY slugs ===")
    prefixes = ("ml-", "dl-", "cv-", "math-", "nlp-", "genai-", "ai-", "py", "ds-")
    for t in topics:
        s = t.slug or ""
        if s.startswith(prefixes):
            print(f"  {s} :: {t.name}")
    print()
    print("=== 'Other' topics (unmatched prefixes) ===")
    known = ("cf-","java-","dsa-","se-","db-","be-","math-","ml-","ds-","dl-","cv-","nlp-","genai-","ai-","mlops-","sd-","sysdesign-","net-","devops-","py","python-")
    for t in topics:
        s = t.slug or ""
        if not s.startswith(known):
            print(f"  {s} :: {t.name}")
finally:
    db.close()
