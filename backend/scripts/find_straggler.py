import sys

sys.path.insert(0, r"D:\Akshit Personal OS\backend")
sys.path.insert(0, r"D:\Akshit Personal OS\backend\scripts")

import scripts.run_simulations as rs
from datetime import date, timedelta

db = rs.SessionLocal()
try:
    views = rs.load_views(db)
finally:
    db.close()
by_slug = {v.slug: v for v in views}
completed = set()
for off in range(365):
    rs.refresh_locks(views, completed)
    d = date(2026, 8, 24) + timedelta(days=off)
    wk = d.weekday() >= 5
    plan = rs.build_daily_plan(budget_minutes=(300 if wk else 200), topics=views,
                               overdue_revisions=[], mode="weekend" if wk else "weekday")
    for i in plan["items"]:
        if i["type"] == "LEARN" and i.get("topic_slug"):
            completed.add(i["topic_slug"])
rs.refresh_locks(views, completed)
for v in views:
    if v.slug not in completed and rs.unlock_status(v, views):
        print("straggler:", v.slug, "| track:", v.learning_track,
              "| prereqs:", by_slug[v.slug].prerequisite_slugs[:6])
