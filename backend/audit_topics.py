import sys
sys.path.insert(0, r'D:\Akshit Personal OS\backend')
from app.db.session import SessionLocal
from app.db.models import CurriculumTopic, CurriculumResource, CurriculumLesson
from sqlalchemy import func

db = SessionLocal()

# Check topic names and descriptions for potential splitting
print("=== Topics with long descriptions (potential splitting candidates) ===")
long_desc = db.query(CurriculumTopic).filter(
    CurriculumTopic.description != None, 
    func.length(CurriculumTopic.description) > 200
).all()
for t in long_desc:
    safe_desc = t.description.replace('\u2192', '->') if t.description else ''
    print(f"  slug={t.slug}, name={t.name}, desc_len={len(t.description)}")
    print(f"    description: {safe_desc[:200]}...")

print("\n\n=== Topic with shortest descriptions (might need merging?) ===")
short_desc = db.query(CurriculumTopic).filter(
    CurriculumTopic.description != None
).order_by(func.length(CurriculumTopic.description).asc()).limit(10).all()
for t in short_desc:
    print(f"  slug={t.slug}, name={t.name}, desc_len={len(t.description)}")
    print(f"    description: {t.description[:100]}...")

db.close()