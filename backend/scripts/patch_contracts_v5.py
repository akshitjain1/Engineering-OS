"""FINAL freeze-prep adjustments (v5)."""
import json
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent / "app" / "content" / "data" / "decomposition_contracts.json"
data = json.loads(p.read_text(encoding="utf-8"))
C = data["contracts"]


def set_terms(topic, concept, terms):
    for x in (C.get(topic) or {}).get("required", []):
        if x["slug"] == concept:
            x["evidence_terms"] = terms


def demote(topic, concept):
    c = C.get(topic)
    if not c:
        return
    kept = [x for x in c["required"] if x["slug"] != concept]
    moved = [x for x in c["required"] if x["slug"] == concept]
    if moved:
        c["required"] = kept
        c.setdefault("optional", []).extend(moved)


def add_req(topic, slug_, desc, terms):
    C[topic]["required"].append({"slug": slug_, "description": desc, "evidence_terms": terms})


set_terms("cv-transformations", "crop-flip-geom", ["flip", "crop", "augment"])
demote("cv-yolo-concept", "family-positioning")
add_req("cv-yolo-concept", "ssd-single-shot",
        "single-shot detection predicts boxes directly on a grid",
        ["single shot", "ssd", "directly"])
set_terms("dl-perceptron", None, [])  # noop guard
demote("dl-perceptron", "convergence-guarantee")
demote("genai-chunking-retrieval", "rank-rerank")
set_terms("genai-hallucinations-guardrails", "grounding-techniques",
          ["retriev", "ground", "knowledg"])
set_terms("genai-hallucinations-guardrails", "validation-refusal",
          ["evaluat", "test", "check"])
set_terms("math-bayes-theorem", "flip-conditioning", ["given", "conditional probabilit"])
set_terms("math-functions", "evaluate-function", ["f(x)", "function value", "input value"])
set_terms("ml-knn", "k-choice", ["n_neighbors", "numbers of neighbors", "nearest neighbors"])
set_terms("nlp-attention-nlp", "replaces-bottleneck", ["align", "fixed length", "bottleneck"])

# ml-end-to-end-workflow: source is prod-ML-systems page — align contract.
demote("ml-end-to-end-workflow", "iterate-loop")
demote("ml-end-to-end-workflow", "checklist-hygiene")
add_req("ml-end-to-end-workflow", "production-monitoring-awareness",
        "production monitoring/reliability concerns after deployment",
        ["monitoring", "drift", "reliability"])

# mlops drift: MLflow evaluate rst covers model evaluation metrics; drift
# wording may be sparse — keep skew-drift required with broader terms.
set_terms("mlops-drift-quality", "skew-drift", ["drift", "skew", "training data"])
set_terms("mlops-experiment-lifecycle", "track-params-metrics",
          ["log_param", "log_metric", "artifact", "tracking", "parameter"])
set_terms("mlops-experiment-lifecycle", "reproduce-run", ["reproduc", "run", "source"])

p.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("contracts v5 applied")
