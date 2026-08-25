"""Backfill prerequisite types into the topics table."""

import sys
sys.path.insert(0, 'D:/Akshit Personal OS/backend')

from app.db.session import SessionLocal
from app.db.models import CurriculumTopic

db = SessionLocal()
Changed = 0
for t in db.query(CurriculumTopic).all():
    if t.prerequisites and isinstance(t.prerequisites, list) and len(t.prerequisites) > 0:
        # Check if already in new format (dict with slug)
        if isinstance(t.prerequisites[0], dict):
            continue  # already enhanced
        # Convert from ['slug1', 'slug2'] to [{'slug': 'slug1', 'type': 'REQUIRED'}, ...]
        new_prereqs = [{'slug': s, 'type': 'REQUIRED'} for s in t.prerequisites]
        t.prerequisites = new_prereqs
        Changed += 1

db.commit()
print('Backfilled ' + str(Changed) + ' topics with enhanced prerequisite format')
db.close()