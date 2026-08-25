"""PRE-LOCK FIX BATCH: spine defect repair + audit corrections."""
import json
import pathlib
import sys

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

# ── 1. SPINE DEFECT REPAIR ──────────────────────────────────────────
# cf-problem-decomposition ← dependency-management is pedagogically wrong:
# decomposition is a Week-0 thinking skill (its own description cites CS50
# Week 0); dependency management is late-stage tooling. This single edge
# artificially delayed the entire DSA gate by ~30 unrelated foundations
# topics. Removing it per "repair clearly incorrect dependency" clause.
from app.db.session import SessionLocal
from app.db.models import CurriculumTopic

db = SessionLocal()
try:
    pd = db.query(CurriculumTopic).filter(
        CurriculumTopic.slug == "cf-problem-decomposition").first()
    old = list(pd.prerequisites or [])
    pd.prerequisites = [r for r in old
                        if (r if isinstance(r, str) else r.get("slug")) != "cf-dependency-management"]
    db.commit()
    print("spine defect repaired:", old, "->", pd.prerequisites)

    corr_path = pathlib.Path(r"D:\Akshit Personal OS\backend\reports\prerequisite_timing_corrections.json")
    corr = json.loads(corr_path.read_text(encoding="utf-8"))
    if not any(c["topic"] == "cf-problem-decomposition" for c in corr["changes"]):
        corr["changes"].append({
            "topic": "cf-problem-decomposition",
            "old": ["cf-dependency-management"],
            "new": [],
            "reason": "Week-0 thinking skill wrongly gated on late tooling; blocked DSA gate by ~30 unrelated topics",
        })
        corr_path.write_text(json.dumps(corr, indent=2), encoding="utf-8")
        print("whitelist updated")
finally:
    db.close()

# ── 2. Override fixes ────────────────────────────────────────────────
op = pathlib.Path(r"D:\Akshit Personal OS\backend\scripts\url_overrides.json")
ov = json.loads(op.read_text(encoding="utf-8"))
D2L_RAW = "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/"
MLF = "https://raw.githubusercontent.com/mlflow/mlflow/master/docs/docs/classic-ml/"
ov["cv-transformations"] = [D2L_RAW + "chapter_computer-vision/image-augmentation.md"]
ov["mlops-experiment-lifecycle"] = [MLF + "tracking/index.mdx", "https://mlflow.org/docs/latest/tracking/"]
ov["mlops-drift-quality"] = [MLF + "evaluation/index.mdx", "https://mlflow.org/docs/latest/model-evaluation/"]
op.write_text(json.dumps(ov, indent=2), encoding="utf-8")
print("overrides fixed:", 3)

# ── 3. Shell stub contracts removal ─────────────────────────────────
cp = pathlib.Path(r"D:\Akshit Personal OS\backend\app\content\data\decomposition_contracts.json")
data = json.loads(cp.read_text(encoding="utf-8"))
SHELLS = ["ai-eng-awareness", "ai-eng-path", "dl-awareness", "dl-path",
          "genai-awareness", "genai-path", "nlp-awareness", "nlp-path"]
removed = [s for s in SHELLS if data["contracts"].pop(s, None)]
data["topic_count"] = len(data["contracts"])
cp.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("shell stubs removed:", removed)

# regenerate merged contracts
mp = pathlib.Path(r"D:\Akshit Personal OS\backend\scripts\merge_decomposition_contracts.py")
base = pathlib.Path(r"D:\Akshit Personal OS\backend\app\content\data")
deco = json.loads((base / "decomposition_contracts.json").read_text(encoding="utf-8"))
ccp = base / "concept_contracts.json"
cc = json.loads(ccp.read_text(encoding="utf-8"))
cc["contracts"].update(deco["contracts"])
# remove shells from merged too
for s in removed:
    cc["contracts"].pop(s, None)
cc["topic_count"] = len(cc["contracts"])
ccp.write_text(json.dumps(cc, indent=2), encoding="utf-8")
print("merged contracts:", cc["topic_count"])

# ── 4. hallucinations grounding/validation → optional (taught later) ─
d2 = json.loads(cp.read_text(encoding="utf-8"))
c = d2["contracts"]["genai-hallucinations-guardrails"]
for concept in ("grounding-techniques", "validation-refusal"):
    kept = [x for x in c["required"] if x["slug"] != concept]
    moved = [x for x in c["required"] if x["slug"] == concept]
    if moved:
        c["required"] = kept
        c.setdefault("optional", []).extend(moved)
cp.write_text(json.dumps(d2, indent=2), encoding="utf-8")
cc2 = json.loads(ccp.read_text(encoding="utf-8"))
cc2["contracts"]["genai-hallucinations-guardrails"] = c
ccp.write_text(json.dumps(cc2, indent=2), encoding="utf-8")
print("hallucinations contract adjusted")
