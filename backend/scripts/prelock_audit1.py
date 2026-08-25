"""PRE-LOCK AUDIT part 1: exact PARTIAL list + DSA timing root cause."""
import json
import sys
from datetime import date, timedelta

sys.path.insert(0, r"D:\Akshit Personal OS\backend")
sys.path.insert(0, r"D:\Akshit Personal OS\backend\scripts")

from app.content.concept_contracts import load_contract_payload
from app.content.learner_visibility import is_learner_visible
from app.db.session import SessionLocal
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic
import scripts.run_simulations as rs

# ── 1. Exact PARTIAL topics ─────────────────────────────────────────
db = SessionLocal()
contracts = load_contract_payload()["contracts"]
lessons = db.query(CurriculumLesson).all()
lesson_topic = {l.id: l.topic_id for l in lessons}
topics = {t.slug: t for t in db.query(CurriculumTopic).all()}
prim_by_topic = {}
for r in db.query(CurriculumResource).all():
    tid = lesson_topic.get(r.lesson_id)
    if tid is None or not is_learner_visible(r):
        continue
    if (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN"):
        prim_by_topic.setdefault(tid, []).append(r)

partials = []
for slug, t in sorted(topics.items()):
    req = [c["slug"] for c in ((contracts.get(slug) or {}).get("required") or [])]
    prim = prim_by_topic.get(t.id, [])
    covered = set()
    for r in prim:
        covered |= set(r.required_concepts_covered or [])
    if req and not all(c in covered for c in req):
        missing = [c for c in req if c not in covered]
        url = prim[0].url if prim else None
        partials.append((slug, missing, url))
print("=== PARTIAL TOPICS ===")
for s, m, u in partials:
    print(f"  {s} | missing={m} | {str(u)[:80]}")

# p-d prereq check
pd = topics.get("cf-problem-decomposition")
print("\ncf-problem-decomposition prereqs:", pd.prerequisites if pd else None)
db.close()

# ── 2. DSA cause instrumentation ────────────────────────────────────
print("\n=== DSA CAUSE INSTRUMENTATION (weekday=220/weekend=300) ===")
dbs = SessionLocal()
try:
    views = rs.load_views(dbs)
finally:
    dbs.close()
completed = set()
by_slug = {v.slug: v for v in views}
for off in range(0, 110):
    rs.refresh_locks(views, completed)
    d = date(2026, 8, 24) + timedelta(days=off)
    wk = d.weekday() >= 5
    budget = 300 if wk else 220
    # eligible runway heads BEFORE plan
    elig = [v.slug for v in views
            if v.track == "S" and (v.slug or "").startswith(("java-", "dsa-", "cf-"))
            and not v.lessons_complete and rs.unlock_status(v, views)]
    plan = rs.build_daily_plan(budget_minutes=budget, topics=views,
                               overdue_revisions=[], mode="weekend" if wk else "weekday")
    picked = [i["topic_slug"] for i in plan["items"]
              if i["type"] == "LEARN" and i.get("group") == "parallel"
              and (i.get("topic_slug") or "").startswith(("java-", "dsa-", "cf-"))]
    if off in (10, 20, 30, 40, 50, 60, 70, 80):
        print(f"d{off:>3} elig_heads={len(elig):>2} picked={len(picked)} "
              f"remaining_unpicked={len([e for e in elig if e not in picked])}")
    for i in plan["items"]:
        if i["type"] == "LEARN" and i.get("topic_slug"):
            completed.add(i["topic_slug"])

rs.refresh_locks(views, completed)
dsa_day = None
# find actual first scheduled day for dsa in a fresh pass marker
print("dsa unlocked by end:", rs.unlock_status(by_slug["dsa-algorithmic-thinking"], views))
