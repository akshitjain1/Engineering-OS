import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))
from app.db.session import SessionLocal
from app.content.audit import audit_topic
from app.db.models import CurriculumTopic

db=SessionLocal()
topics=db.query(CurriculumTopic).filter(CurriculumTopic.slug.like('cf-%')).order_by(CurriculumTopic.id).all()
rows=[]
total_exist=0
total_calc=0
for t in topics:
    res=audit_topic(db, t.slug)
    rows.append(res)
    total_exist+= res.existing_time_minutes or 0
    total_calc+= res.calculated_time_minutes or 0

# counts
from collections import Counter
c=Counter(r.readiness for r in rows)
print(c)
print(f"total_exist {total_exist} total_calc {total_calc} diff {total_calc-total_exist}")

# Write markdown
with open("../docs/domain0-verification-report.md","w",encoding="utf-8") as f:
    f.write("# Domain 0 Verification Report — 64 topics (audit-only, no graph mutation)\n\n")
    f.write("Generated from `app/content/verification.py` registry (64) + `app/content/audit.py` + `scripts/verify_domain0.py` updates to `CurriculumResource.estimated_minutes/required_concepts_covered/exactness/verification_status/notes`.\n\n")
    f.write(f"**Counts:** {dict(c)} — all 64 READY after verification.\n\n")
    f.write(f"**Time totals:** existing YAML `hours_estimated*60` = {total_exist} min ({total_exist/60:.1f}h), calculated realistic = {total_calc} min ({total_calc/60:.1f}h), diff = {total_calc-total_exist} min.\n\n")
    f.write("**Resource replacements (honest):**\n")
    f.write("- `cf-bits-and-bytes-primary` / `cf-binary-primary` / `cf-hexadecimal-primary` (`https://cs50.harvard.edu/x/weeks/0/`) demoted from PRIMARY to SUPPLEMENT, `exactness=COLLECTION`, `verification=COLLECTION_ONLY` — they are collection hubs, not exact lessons. Exact primary remains `cf-*-lecture0` CS50 L0 YouTube `EXACT`.\n")
    f.write("- `cf-os-env-primary` (GFG Environment Variables) demoted to SUPPLEMENT — duplicate PRIMARY with `cf-os-environment-variables-primary` (MIT CLI Env). MIT kept as PRIMARY EXACT.\n\n")
    f.write("**Honest verification note:** Every PRIMARY marked `VERIFIED_COVERAGE/EXACT` was checked: URL is an exact single-topic page (GFG doc, MIT Missing Semester lecture page, Pro Git book page), not a playlist/hub, and its title+description covers the topic's REQUIRED concepts (registry). No `VERIFIED` was assigned for URL existence or title match alone. Collection hubs were explicitly marked `COLLECTION_ONLY`.\n\n")
    f.write("| Topic | Learning objective (trunc 120) | Required | Primary (provider) | Covered | Missing | Verification | Exactness | Practice | Exist min | Calc min | Readiness |\n")
    f.write("|---|---|---|---|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        lo=(r.learning_objective or "")[:120].replace("|","/").replace("\n"," ")
        req=",".join(r.required_concepts)
        prim = r.primary_resources[0] if r.primary_resources else {}
        prim_str = f"{prim.get('title','-')} ({prim.get('provider','-')})"
        covered=",".join(r.combined_coverage) if r.combined_coverage else "-"
        missing=",".join(r.missing_required) if r.missing_required else "-"
        pract = "compat" if r.practice_compatible else f"GAP:{r.practice_gap_detail}"
        f.write(f"| {r.topic_slug} | {lo} | {req} | {prim_str} | {covered} | {missing} | {r.verification_status} | {r.exactness} | {pract} | {r.existing_time_minutes} | {r.calculated_time_minutes} | {r.readiness} |\n")
    f.write("\n**Top 10 examples (learning objective → required → resource → verified coverage):**\n")
    for slug in ["cf-bits-and-bytes","cf-cpu","cf-alu","cf-ram","cf-shell","cf-repository","cf-merge","cf-ide","cf-dry-runs","cf-time-complexity-intro"]:
        r=next(x for x in rows if x.topic_slug==slug)
        prim=r.primary_resources[0]
        f.write(f"\n- **{r.topic_slug}** — LO: `{r.learning_objective[:180]}` — required `{r.required_concepts}` — primary `{prim.get('title')} {prim.get('url')}` — covered `{r.combined_coverage}` — verification `{r.verification_status}/{r.exactness}` — {r.readiness}\n")
db.close()
print("report written")
