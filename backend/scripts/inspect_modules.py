"""Inspect module structure for AI/ML subjects."""
import sys
sys.path.insert(0, r"D:\Akshit Personal OS\backend")
from app.db.session import SessionLocal
from app.db.models import CurriculumModule, CurriculumSubject, CurriculumTopic

db = SessionLocal()
try:
    subjects = db.query(CurriculumSubject).order_by(CurriculumSubject.order_index).all()
    print("=== Subjects ===")
    for s in subjects:
        print(f"  id={s.id} slug={s.slug} name={s.name}")
    print()
    print("=== Modules per subject ===")
    mods = db.query(CurriculumModule).order_by(CurriculumModule.subject_id, CurriculumModule.order_index).all()
    for m in mods:
        cnt = db.query(CurriculumTopic).filter(CurriculumTopic.module_id == m.id).count()
        print(f"  id={m.id} subject={m.subject_id} slug={m.slug} name={m.name} [{cnt} topics]")
finally:
    db.close()
