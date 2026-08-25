import json
import sys

sys.path.insert(0, r"D:\Akshit Personal OS\backend")
sys.path.insert(0, r"D:\Akshit Personal OS\backend\scripts")

from inspect_new_primaries import fetch, parse
from app.content.concept_contracts import load_contract_payload

C = load_contract_payload()["contracts"]
ev = {r["resource_slug"]: r for r in json.load(open(r"reports/resource_evidence_final.json", encoding="utf-8"))["resources"]}

STUBBORN = {
    "cv-evaluation-metrics-cv": ["map-construction"],
    "cv-image-tensors": ["batch-dim", "dtype-normalize"],
    "cv-what-is-an-image": ["image-as-grid", "resolution-effects"],
    "genai-context-windows": ["finite-span"],
    "genai-hallucinations-guardrails": ["fluent-unfactual", "grounding-techniques", "validation-refusal"],
    "math-covariance-correlation": ["covariance-joint", "correlation-normalized"],
    "ai-eng-observability-security": ["injection-threats"],
    "ai-eng-planning-memory": ["scratchpad-longterm"],
    "cv-sift-orb-awareness": ["orb-binary"],
    "dl-backprop-intuition": ["two-layer-handwork"],
    "nlp-tokenization-nlp": ["bpe-algorithm"],
}

for slug, concepts in STUBBORN.items():
    contract = C.get(slug) or {}
    rec = next((r for r in ev.values() if r["topic_slug"] == slug), None)
    url = rec["url"] if rec else "?"
    cls, code, payload = fetch(url)
    print("=" * 72)
    print(slug, "|", code, "|", url[:90])
    if cls != "OK":
        continue
    _h, v = parse(payload)
    low = v.lower()
    for cs in concepts:
        entry = next((x for x in contract.get("required", []) if x["slug"] == cs), None)
        terms = (entry or {}).get("evidence_terms") or []
        hits = [t for t in terms if t.lower() in low]
        print(f"   {cs}: terms={terms} -> hits={hits}")
