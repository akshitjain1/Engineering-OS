"""Contract refinements v3 (final freeze prep)."""
import json
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent / "app" / "content" / "data" / "decomposition_contracts.json"
data = json.loads(p.read_text(encoding="utf-8"))
C = data["contracts"]


def demote(slug, concept):
    c = C[slug]
    kept = [x for x in c["required"] if x["slug"] != concept]
    moved = [x for x in c["required"] if x["slug"] == concept]
    if moved:
        c["required"] = kept
        c.setdefault("optional", []).extend(moved)


def add_required(slug, concept_slug, description, terms):
    C[slug]["required"].append({"slug": concept_slug, "description": description,
                                "evidence_terms": terms})


demote("cv-u-net", "skip-fusion")
demote("cv-u-net", "biomedical-origin")
add_required("cv-u-net", "fcn-dense-prediction",
             "fully convolutional pixel-wise prediction",
             ["pixel", "prediction", "convolutional", "dense"])
demote("genai-context-windows", "truncation-strategies")

p.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("contracts v3 patched")
