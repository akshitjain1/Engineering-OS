"""Resource granularity audit — identify resources missing exactness or estimated_minutes."""

import sys
sys.path.insert(0, 'D:/Akshit Personal OS/backend')

from app.db.session import SessionLocal
from app.db.models import CurriculumTopic, CurriculumLesson, CurriculumResource
from sqlalchemy import func

db = SessionLocal()

no_exact = db.query(CurriculumResource).filter(CurriculumResource.exactness == None).all()
print("=== Resources with exactness=None ===")
print("Count:", len(no_exact))
print()

by_role = {}
for r in no_exact:
    role = r.role or "None"
    by_role.setdefault(role, []).append(
        {
            "slug": r.slug,
            "title": r.title,
            "url": r.url[:60] if r.url else "NO_URL",
            "resource_type": r.resource_type,
            "topic": r.lesson.topic.slug if r.lesson else "NO_LESSON",
        }
    )

for role, resources in by_role.items():
    print("Role=" + role + ": " + str(len(resources)) + " resources")
    for res in resources[:5]:
        u = res["url"]
        url_display = u[:50] if u and len(u) > 50 else (u if u else "-")
        print(
            "  - "
            + res["slug"]
            + " | "
            + res["resource_type"]
            + " | "
            + res["topic"]
            + " | url="
            + url_display
        )
    if len(resources) > 5:
        print("  ... and " + str(len(resources) - 5) + " more")
    print()

no_est = db.query(CurriculumResource).filter(CurriculumResource.estimated_minutes == None).all()
print("=== Resources with estimated_minutes=None: " + str(len(no_est)) + " ===")
print()

by_role2 = {}
for r in no_est:
    role = r.role or "None"
    by_role2.setdefault(role, []).append(
        {
            "slug": r.slug,
            "title": r.title,
            "url": r.url[:60] if r.url else "NO_URL",
            "resource_type": r.resource_type,
        }
    )

for role, resources in by_role2.items():
    print("Role=" + role + ": " + str(len(resources)) + " resources")
    for res in resources[:5]:
        u = res["url"]
        url_display = u[:50] if u and len(u) > 50 else (u if u else "-")
        print(
            "  - " + res["slug"] + " | " + res["resource_type"] + " | url=" + url_display
        )
    if len(resources) > 5:
        print("  ... and " + str(len(resources) - 5) + " more")
    print()

# Resource type distribution
rt = db.query(CurriculumResource.resource_type, func.count(CurriculumResource.id)).group_by(CurriculumResource.resource_type).all()
print("Resource type distribution (ALL):")
for rt_val, c in rt:
    print("  " + str(rt_val) + ": " + str(c))

rt_no_exact = (
    db.query(CurriculumResource.resource_type, func.count(CurriculumResource.id))
    .filter(CurriculumResource.exactness == None)
    .group_by(CurriculumResource.resource_type)
    .all()
)
print("Resource type distribution (exactness=None):")
for rt_val, c in rt_no_exact:
    print("  " + str(rt_val) + ": " + str(c))

rt_no_est = (
    db.query(CurriculumResource.resource_type, func.count(CurriculumResource.id))
    .filter(CurriculumResource.estimated_minutes == None)
    .group_by(CurriculumResource.resource_type)
    .all()
)
print("Resource type distribution (estimated_minutes=None):")
for rt_val, c in rt_no_est:
    print("  " + str(rt_val) + ": " + str(c))

db.close()