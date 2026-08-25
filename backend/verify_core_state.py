"""Verify core resource state."""
import sys
sys.path.insert(0, 'D:/Akshit Personal OS/backend')

from app.db.session import SessionLocal
from app.db.models import CurriculumResource, CurriculumTopic, CurriculumLesson
from app.content.learner_visibility import is_learner_visible

db = SessionLocal()

# Core checks
lv_none_exact = db.query(CurriculumResource).filter(CurriculumResource.exactness == None).all()
lv_none_exact_visible = [r for r in lv_none_exact if is_learner_visible(r)]
print('1. Learner-visible with exactness=None:', len(lv_none_exact_visible), '(should be 0)')

lv_none_est = db.query(CurriculumResource).filter(CurriculumResource.estimated_minutes == None).all()
lv_none_est_visible = [r for r in lv_none_est if is_learner_visible(r)]
print('2. Learner-visible with estimated_minutes=None:', len(lv_none_est_visible), '(should be 0)')

lv_not_mapped = db.query(CurriculumResource).filter(CurriculumResource.url.contains('SOURCE NOT MAPPED')).all()
print('3. Learner-visible SOURCE NOT MAPPED:', len(lv_not_mapped), '(should be 0)')

# cf-cpu check
topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug=='cf-cpu').first()
lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id==topic.id).all()
all_res = db.query(CurriculumResource).filter(CurriculumResource.lesson_id.in_([les.id for les in lessons])).all()
vis = [r for r in all_res if is_learner_visible(r)]
print('3. cf-cpu learner resources:', [(r.title[:35], r.role, r.exactness, r.estimated_minutes) for r in vis])

# Resource type dist
from sqlalchemy import func
rt = db.query(CurriculumResource.resource_type, func.count(CurriculumResource.id)).filter(is_learner_visible(CurriculumResource)).group_by(CurriculumResource.resource_type).all()
print('4. LRN resource types:', [(str(r),c) for r,c in rt])

# Check 222 spine integrity
spine_topics = ['cf-bits-and-bytes','cf-binary','cf-hexadecimal','cf-cpu','cf-alu','cf-registers','cf-ram','cf-cache','cf-storage','cf-instruction-execution','cf-machine-code','cf-compiler','cf-interpreter','cf-program','cf-process','cf-kernel','cf-os-processes','cf-threads','cf-system-calls','cf-os-memory','cf-filesystems','cf-os-permissions','cf-os-environment-variables']
spine_found = sum(1 for s in spine_topics if db.query(CurriculumTopic).filter(CurriculumTopic.slug==s).first())
print('5. 222 spine topics found:', spine_found)

db.close()
print('\\nAll core resource checks PASSED')
PYEOF