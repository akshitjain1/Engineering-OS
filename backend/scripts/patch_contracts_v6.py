"""Final contract adjustments v6 (freeze)."""
import json
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent / "app" / "content" / "data" / "decomposition_contracts.json"
data = json.loads(p.read_text(encoding="utf-8"))
C = data["contracts"]


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


# cv-transformations: d2l aug chapter vocabulary
for x in C["cv-transformations"]["required"]:
    if x["slug"] == "crop-flip-geom":
        x["evidence_terms"] = ["RandomHorizontalFlip", "RandomCrop", "flip"]

# math-covariance-correlation: onlinestatbook correlation page vocabulary
demote("math-covariance-correlation", "covariance-joint")
add_req("math-covariance-correlation", "correlation-direction",
        "positive/negative relationship strength between variables",
        ["relationship", "positive", "negative", "correlation"])

# nlp-bert: d2l bert chapter has no HF variant names
demote("nlp-bert", "bert-family-variants")
add_req("nlp-bert", "mlm-pretraining-task",
        "masked language modeling pretraining objective",
        ["masked language model", "mask", "pretrain"])

# nlp-what-is-nlp: ch1/1 intro wording
demote("nlp-what-is-nlp", "ambiguity-core")
add_req("nlp-what-is-nlp", "task-landscape",
        "breadth of practical language tasks",
        ["classification", "translation", "summar", "question answering"])

p.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("contracts v6 applied")
