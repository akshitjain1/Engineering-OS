"""Contract refinements v2: term corrections + optionality demotions."""
import json
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent / "app" / "content" / "data" / "decomposition_contracts.json"
data = json.loads(p.read_text(encoding="utf-8"))
C = data["contracts"]


def set_terms(slug, concept_slug, terms):
    for c in C[slug]["required"]:
        if c["slug"] == concept_slug:
            c["evidence_terms"] = terms
            return True
    return False


def demote_to_optional(slug, concept_slug):
    c = C[slug]
    kept = [x for x in c["required"] if x["slug"] != concept_slug]
    moved = [x for x in c["required"] if x["slug"] == concept_slug]
    if moved:
        c["required"] = kept
        c.setdefault("optional", []).extend(moved)


# Term corrections to match actual source vocabulary:
set_terms("cv-normalization-cv", "per-channel-stats", ["mean subtraction", "mean", "subtract"])
set_terms("cv-normalization-cv", "pretrained-match", ["data preprocessing", "preprocessing", "scale inputs"])
set_terms("cv-augmentation", "label-preserving", ["flip", "crop", "augmentation"])
set_terms("cv-nms", "greedy-suppression", ["non-maximum suppression", "nms", "suppression"])
set_terms("cv-nms", "duplicate-removal", ["duplicate", "overlap", "suppress"])
set_terms("cv-evaluation-metrics-cv", "map-construction", ["map", "average precision", "precision"])
set_terms("cv-instance-segmentation", "mask-rcnn-branch", ["mask r-cnn", "mask", "roipooling", "instance"])
set_terms("cv-instance-segmentation", "instance-vs-semantic", ["instance", "semantic segmentation"])
set_terms("ai-eng-function-calling", "typed-signatures", ["schema", "input_schema", "parameter"])
set_terms("ai-eng-function-calling", "error-idempotency", ["is_error", "error", "tool_result"])
set_terms("nlp-tokenization-nlp", "oov-vocab-tradeoff", ["[UNK]", "unknown", "vocabulary size", "vocab"])
set_terms("nlp-text-preprocessing", "cleaning-steps", ["lowercase", "lower case", "normalizer", "strip accents", "punctuation"])
set_terms("genai-hallucinations-guardrails", "fluent-unfactual", ["hallucinat", "fabricat", "made up", "false"])
set_terms("genai-hallucinations-guardrails", "grounding-techniques", ["grounding", "cite", "source", "reference"])
set_terms("genai-hallucinations-guardrails", "validation-refusal", ["verify", "validate", "refus"])
set_terms("genai-inference-parameters", "temperature-steering", ["temperature", "randomness"])
set_terms("genai-inference-parameters", "top-k-top-p", ["top-k", "top-p", "top_k", "top_p"])
set_terms("genai-context-windows", "finite-span", ["context window", "maximum", "token limit"])
set_terms("genai-context-windows", "truncation-strategies", ["truncat", "summariz", "exceed"])
set_terms("nlp-generative-models", "autoregressive-decode", ["causal", "autoregressive", "next token"])
set_terms("nlp-generative-models", "gpt-lineage", ["gpt", "decoder-only", "from scratch"])

# Optionality demotions (concepts genuinely beyond the mapped single unit):
demote_to_optional("cv-augmentation", "over-augment-risk")
demote_to_optional("cv-efficientnet-awareness", "compound-scaling")
demote_to_optional("cv-evaluation-metrics-cv", "seg-iou-dice")
demote_to_optional("nlp-text-preprocessing", "over-cleaning-risk")
demote_to_optional("genai-next-token-prediction", "pretraining-objective")

p.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("contracts v2 patched")
