"""Merge decomposition_contracts.json into concept_contracts.json (idempotent)."""
import json
import pathlib

base = pathlib.Path(__file__).resolve().parent.parent / "app" / "content" / "data"
deco = json.loads((base / "decomposition_contracts.json").read_text(encoding="utf-8"))
cc_path = base / "concept_contracts.json"
if cc_path.exists():
    cc = json.loads(cc_path.read_text(encoding="utf-8"))
else:
    cc = {"contracts": {}, "topic_count": 0}
before = len(cc["contracts"])
for slug, c in deco["contracts"].items():
    cc["contracts"][slug] = c
cc["topic_count"] = len(cc["contracts"])
cc_path.write_text(json.dumps(cc, indent=2), encoding="utf-8")
print("merged", len(deco["contracts"]), "contracts; had", before, "; total", len(cc["contracts"]))
