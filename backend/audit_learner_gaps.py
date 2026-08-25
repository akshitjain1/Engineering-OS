"""Identify learner-visible resources missing exactness or estimated_minutes."""

import sys
sys.path.insert(0, 'D:/Akshit Personal OS/backend')

from app.db.session import SessionLocal
from app.db.models import CurriculumResource
from app.content.learner_visibility import is_learner_visible, VIS_LEARNER, VIS_VERIFICATION_ONLY, VIS_LEGACY_DUPLICATE, VIS_COVERAGE_SUPPLEMENT

db = SessionLocal()

# Get all resources with exactness=None
no_exact = db.query(CurriculumResource).filter(CurriculumResource.exactness == None).all()
print("Resources with exactness=None:", len(no_exact))

# Check which are learner-visible
learner_visible_no_exact = []
for r in no_exact:
    lv = is_learner_visible(r)
    if lv:
        learner_visible_no_exact.append(r)
        # Set visibility_class if not set
        if not r.visibility_class:
            r.visibility_class = VIS_LEARNER

print("Of those, learner-visible:", len(learner_visible_no_exact))

# Group learner-visible by role
by_role = {}
for r in learner_visible_no_exact:
    role = r.role or "None"
    by_role.setdefault(role, []).append({
        "slug": r.slug,
        "title": r.title,
        "url": r.url[:60] if r.url else "NO_URL",
        "resource_type": r.resource_type,
    })

for role, resources in by_role.items():
    print("  Role=" + role + ": " + str(len(resources)) + " resources")
    for res in resources[:3]:
        print("    - " + res["slug"] + " | " + res["resource_type"] + " | url=" + (res["url"][:50] if res["url"] and len(res["url"])>50 else (res["url"] if res["url"] else "-")))

# Now do the same for estimated_minutes=None
no_est = db.query(CurriculumResource).filter(CurriculumResource.estimated_minutes == None).all()
print("\nResources with estimated_minutes=None:", len(no_est))

learner_visible_no_est = []
for r in no_est:
    lv = is_learner_visible(r)
    if lv:
        learner_visible_no_est.append(r)

print("Of those, learner-visible:", len(learner_visible_no_est))

by_role2 = {}
for r in learner_visible_no_est:
    role = r.role or "None"
    by_role2.setdefault(role, []).append({
        "slug": r.slug,
        "title": r.title,
        "url": r.url[:60] if r.url else "NO_URL",
        "resource_type": r.resource_type,
    })

for role, resources in by_role2.items():
    print("  Role=" + role + ": " + str(len(resources)) + " resources")
    for res in resources[:3]:
        print("    - " + res["slug"] + " | " + res["resource_type"] + " | url=" + (res["url"][:50] if res["url"] and len(res["url"])>50 else (res["url"] if res["url"] else "-")))

db.close()