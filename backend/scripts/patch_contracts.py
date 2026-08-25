"""Patch decomposition_contracts.json: demote over-specified concepts."""
import json
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent / "app" / "content" / "data" / "decomposition_contracts.json"
data = json.loads(p.read_text(encoding="utf-8"))

moves = [
    ("genai-what-is-lm", "emergent-capability"),
    ("genai-next-token-prediction", "emergent-capability"),
    ("genai-tokenization-llm", "token-economics"),
    ("nlp-what-is-nlp", "pretraining-objective"),
]
for slug, concept in moves:
    c = data["contracts"].get(slug)
    if not c:
        continue
    kept = [x for x in c["required"] if x["slug"] != concept]
    moved = [x for x in c["required"] if x["slug"] == concept]
    if moved:
        c["required"] = kept
        c.setdefault("optional", []).extend(moved)

p.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("contracts patched")
