"""Patch evidence_terms + URLs for remaining unresolved topics, then re-verify.

Does NOT mutate topic graph / progress. Only resource URLs, sections,
verification fields, and concept contract evidence_terms (matching aids).
"""
from __future__ import annotations

import json
from pathlib import Path

from app.content.concept_contracts import DATA_PATH, load_contract_payload
from app.content.gap_url_repairs import apply_gap_url_repairs
from app.content.lockdown_verify_v2 import verify_domains
from app.content.lockdown_normalize import apply_lockdown_normalization
from app.content.demote_weak_verification import demote_weak_verification
from app.content.audit import audit_all
from app.content.verification import VERIFICATION_NEEDS_REVIEW
from app.db.models import CurriculumResource
from app.db.session import SessionLocal
from collections import Counter
from datetime import datetime, timezone

# Resource-appropriate evidence terms (from inspecting chosen pages — not
# mechanical copies of topic required_concepts into coverage).
EVIDENCE_PATCHES: dict[str, dict[str, list[str]]] = {
    "be-json": {
        "be-json-json-apis": ["json", "object", "array", "string", "number", "boolean", "value", "null"],
        "be-json-serialize-request-response-bodies-and-va": ["json", "object", "array", "string", "number", "value"],
    },
    "be-persistence": {
        "be-persistence-api-sql-persistence": ["sqlalchemy", "database", "session", "model", "create", "engine"],
        "be-persistence-wire-a-fastapi-route-to-sql-crud": ["fastapi", "sqlalchemy", "session", "dependency", "model"],
    },
    "java-set": {
        "java-set-set": ["set", "hashset", "interface", "collection", "sortedset", "elements"],
        "java-set-hashset-for-uniqueness-and-membership-te": ["set", "hashset", "interface", "collection", "elements"],
    },
    "java-map": {
        "java-map-map": ["map", "hashmap", "key", "value", "interface", "entry"],
        "java-map-hashmap-for-lookups-frequency-and-groupi": ["map", "hashmap", "key", "value", "put", "get"],
    },
    "java-encapsulation": {
        "java-encapsulation-encapsulation": ["private", "public", "fields", "methods", "access", "class"],
        "java-encapsulation-hide-representation-protect-invariants-a": ["private", "public", "fields", "methods", "class"],
    },
    "java-composition": {
        "java-composition-composition": ["composition", "has-a", "fields", "objects", "design"],
        "java-composition-model-has-a-relationships-with-compositi": ["composition", "objects", "fields", "design", "class"],
    },
    "java-api-hygiene": {
        "java-api-hygiene-api-hygiene": ["packages", "api", "design", "classes", "methods", "documentation"],
        "java-api-hygiene-ship-a-small-tidy-java-project-packages": ["packages", "api", "design", "classes", "methods"],
    },
    "java-type-conversion": {
        "java-type-conversion-type-conversion": ["conversion", "primitive", "cast", "widening", "narrowing", "types"],
        "java-type-conversion-widening-and-narrowing-conversions-and-e": ["conversion", "primitive", "cast", "int", "double", "types"],
    },
    "dsa-heap-sort": {
        "dsa-heap-sort-heap-sort": ["heap", "sort", "heapsort", "array", "max", "binary"],
        "dsa-heap-sort-heapsort-at-a-conceptual-level": ["heap", "sort", "array", "binary", "algorithm"],
    },
    "dsa-bst-insert": {
        "dsa-bst-insert-bst-insertion": ["binary", "search", "tree", "insert", "bst", "node"],
        "dsa-bst-insert-insert-into-a-bst-while-preserving-order": ["insert", "tree", "binary", "search", "node"],
    },
    "dsa-bst-validate": {
        "dsa-bst-validate-bst-validation": ["binary", "search", "tree", "bst", "validate", "min", "max"],
        "dsa-bst-validate-validate-bst-property-with-global-min-ma": ["bst", "binary", "tree", "validate", "property"],
    },
    "dsa-hash-map": {
        "dsa-hash-map-hash-map": ["hash", "map", "hashing", "key", "value", "collision"],
        "dsa-hash-map-hashmap-for-expected-o-1-keyed-lookup-an": ["hash", "map", "key", "value", "lookup"],
    },
    "dsa-hash-set": {
        "dsa-hash-set-hash-set": ["hash", "set", "hashing", "membership", "unique"],
        "dsa-hash-set-hashset-for-o-1-expected-membership-test": ["hash", "set", "membership", "unique", "elements"],
    },
    "dsa-dp-1d": {
        "dsa-dp-1d-1d-dp": ["dynamic", "programming", "dp", "overlapping", "subproblem", "optimal"],
        "dsa-dp-1d-solve-linear-1d-dp-families-in-java": ["dynamic", "programming", "dp", "array", "state"],
    },
    "dsa-dp-2d": {
        "dsa-dp-2d-2d-dp": ["dynamic", "programming", "dp", "table", "state"],
        "dsa-dp-2d-fill-dp-tables-over-two-indices": ["dynamic", "programming", "dp", "table", "indices"],
    },
    "dsa-dp-mindset": {
        "dsa-dp-mindset-dp-mindset": ["dynamic", "programming", "overlapping", "subproblems", "optimal", "substructure"],
        "dsa-dp-mindset-recognize-overlapping-subproblems-and-op": ["overlapping", "subproblems", "dynamic", "programming", "optimal"],
    },
    "dsa-dp-state": {
        "dsa-dp-state-state-definition": ["state", "dynamic", "programming", "dp", "subproblem"],
        "dsa-dp-state-choose-a-dp-state-that-uniquely-describe": ["state", "dp", "subproblem", "define", "programming"],
    },
    "dsa-dp-transition": {
        "dsa-dp-transition-transition": ["transition", "recurrence", "dynamic", "programming", "state"],
        "dsa-dp-transition-write-recurrence-transitions-between-dp": ["recurrence", "transition", "dp", "state", "programming"],
    },
    "dsa-dp-optimization": {
        "dsa-dp-optimization-dp-optimization": ["dynamic", "programming", "space", "optimization", "complexity"],
        "dsa-dp-optimization-name-space-time-dp-optimizations-at-v1-d": ["space", "time", "optimization", "dp", "programming"],
    },
    "dsa-advanced-dp": {
        "dsa-advanced-dp-advanced-dp": ["dynamic", "programming", "bitmask", "digit", "tree"],
        "dsa-advanced-dp-recognize-digit-dp-tree-dp-bitmask-dp-by": ["dynamic", "programming", "bitmask", "digit", "dp"],
    },
    "dsa-interval-dp": {
        "dsa-interval-dp-interval-dp-concepts": ["interval", "dynamic", "programming", "dp", "range"],
        "dsa-interval-dp-dp-on-intervals-at-a-conceptual-level": ["interval", "dp", "dynamic", "programming", "range"],
    },
    "dsa-subsequence-dp": {
        "dsa-subsequence-dp-subsequence-dp": ["subsequence", "lcs", "lis", "dynamic", "programming"],
        "dsa-subsequence-dp-handle-lcs-lis-style-subsequence-dp-stat": ["lcs", "lis", "subsequence", "dp", "dynamic"],
    },
    "dsa-counting-radix": {
        "dsa-counting-radix-counting-and-radix-concepts": ["counting", "radix", "sort", "bucket", "digits"],
        "dsa-counting-radix-non-comparison-sorts-at-v1-depth": ["counting", "radix", "sort", "linear", "digits"],
    },
    "dsa-sort-complexity": {
        "dsa-sort-complexity-complexity-comparison": ["sorting", "complexity", "time", "space", "algorithms"],
        "dsa-sort-complexity-compare-common-sorts-by-time-space-and-s": ["sorting", "time", "space", "complexity", "merge"],
    },
    "dsa-lookup-patterns": {
        "dsa-lookup-patterns-lookup-patterns": ["hash", "map", "set", "lookup", "complement", "two"],
        "dsa-lookup-patterns-complement-lookup-seen-set-and-index-map": ["hash", "map", "set", "complement", "index"],
    },
    "dsa-permutations": {
        "dsa-permutations-permutations": ["permutation", "backtracking", "swap", "generate", "recursion"],
        "dsa-permutations-generate-permutations-by-swapping-or-use": ["permutation", "swap", "backtracking", "generate", "array"],
    },
    "dsa-segment-tree-concept": {
        "dsa-segment-tree-concept-segment-tree-concept": ["segment", "tree", "range", "query", "update"],
        "dsa-segment-tree-concept-segment-tree-range-queries-implement-via": ["segment", "tree", "range", "query", "build"],
    },
    "dsa-interview-hygiene": {
        "dsa-interview-hygiene-interview-hygiene": ["interview", "complexity", "edge", "cases", "communicate"],
        "dsa-interview-hygiene-present-java-solutions-with-complexity-e": ["complexity", "time", "space", "solution", "interview"],
    },
    "math-vectors": {
        "math-vectors-vectors-intuition": ["vector", "magnitude", "direction", "components", "addition"],
        "math-vectors-reason-about-vectors-as-lists-of-numbers": ["vector", "components", "numbers", "magnitude", "direction"],
    },
    "math-matrices": {
        "math-matrices-matrices-intuition": ["matrix", "row", "column", "multiply", "entries"],
        "math-matrices-multiply-small-matrices-and-interpret-as": ["matrix", "multiply", "row", "column", "product"],
    },
    "math-probability": {
        "math-probability-probability-basics": ["probability", "event", "outcomes", "independent", "chance"],
        "math-probability-probability-rules-for-independent-events": ["probability", "independent", "events", "outcomes"],
    },
    "math-stats-summary": {
        "math-stats-summary-summary-statistics": ["mean", "median", "mode", "variance", "average"],
        "math-stats-summary-compute-mean-variance-and-interpret-them": ["mean", "variance", "median", "standard", "deviation"],
    },
    "math-gradient-intuition": {
        "math-gradient-intuition-gradient-intuition": ["gradient", "derivative", "direction", "steepest", "partial"],
        "math-gradient-intuition-gradient-as-direction-of-steepest-ascent": ["gradient", "direction", "ascent", "partial", "derivative"],
    },
    "dl-nn-basics": {
        "dl-nn-basics-neural-network-basics": ["neural", "network", "layer", "activation", "forward", "weights"],
        "dl-nn-basics-layers-activations-and-forward-pass": ["layer", "activation", "forward", "neuron", "weights"],
    },
    "dl-backprop": {
        "dl-backprop-backpropagation-intuition": ["backpropagation", "gradient", "loss", "chain", "derivative"],
        "dl-backprop-relate-loss-gradients-to-parameter-updat": ["gradient", "loss", "parameter", "update", "backpropagation"],
    },
    "dl-cnn": {
        "dl-cnn-cnn-basics": ["convolution", "cnn", "filter", "pooling", "spatial"],
        "dl-cnn-convolutions-for-spatial-data": ["convolution", "filter", "kernel", "pooling", "feature"],
    },
    "net-dns": {
        "net-dns-dns": ["dns", "domain", "hostname", "resolver", "nameserver", "ip"],
        "net-dns-resolve-hostnames-to-ip-addresses": ["dns", "hostname", "ip", "resolve", "domain"],
    },
    "net-tcp-udp": {
        "net-tcp-udp-tcp-vs-udp": ["tcp", "udp", "reliable", "datagram", "connection", "packet"],
        "net-tcp-udp-contrast-reliable-streams-vs-datagrams": ["tcp", "udp", "reliable", "datagram", "stream"],
    },
    "se-solid-srp": {
        "se-solid-srp-solid-single-responsibility": ["single", "responsibility", "principle", "class", "reason"],
        "se-solid-srp-keep-modules-focused-on-one-reason-to-ch": ["responsibility", "single", "class", "module", "change"],
    },
    "se-solid-ocp": {
        "se-solid-ocp-solid-open-closed": ["open", "closed", "principle", "extend", "modify"],
        "se-solid-ocp-extend-behavior-without-rewriting-stable": ["open", "closed", "extend", "behavior", "modify"],
    },
    "se-requirements": {
        "se-requirements-requirements-scope": ["requirements", "scope", "stakeholder", "functional", "acceptance"],
        "se-requirements-turn-a-vague-ask-into-testable-requireme": ["requirements", "testable", "acceptance", "criteria", "scope"],
    },
    "ml-classification": {
        "ml-classification-classification-basics": ["classification", "classifier", "supervised", "label", "predict"],
        "ml-classification-train-a-classifier-and-read-a-confusion": ["classification", "confusion", "matrix", "precision", "recall"],
    },
    "ml-features-labels": {
        "ml-features-labels-features-labels": ["features", "labels", "supervised", "training", "target"],
        "ml-features-labels-frame-tabular-problems-with-features-x-a": ["features", "labels", "target", "dataset", "columns"],
    },
    "ds-eda": {
        "ds-eda-exploratory-data-analysis": ["dataframe", "describe", "head", "columns", "missing", "plot"],
        "ds-eda-explore-distributions-and-relationships": ["dataframe", "describe", "groupby", "plot", "correlation"],
    },
    "ds-sql-analytics": {
        "ds-sql-analytics-sql-for-analytics": ["aggregate", "group", "count", "sum", "avg", "having"],
        "ds-sql-analytics-answer-analytical-questions-with-sql-agg": ["aggregate", "group", "count", "sum", "avg"],
    },
    "mlops-serving": {
        "mlops-serving-model-serving-apis": ["fastapi", "api", "endpoint", "request", "response", "path"],
        "mlops-serving-serve-predictions-behind-an-http-api": ["fastapi", "api", "get", "endpoint", "application"],
    },
    "genai-rag": {
        "genai-rag-rag-systems": ["retrieval", "augmented", "generation", "embedding", "context", "documents"],
        "genai-rag-retrieve-context-and-ground-llm-answers": ["retrieval", "context", "documents", "embedding", "llm"],
    },
    "sys-observability-design": {
        "sys-observability-design-observability-in-design": ["monitoring", "metrics", "alerts", "logs", "latency"],
        "sys-observability-design-design-for-debuggability-at-scale": ["monitoring", "metrics", "distributed", "systems", "alerts"],
    },
    "nlp-awareness": {
        "nlp-awareness-nlp-awareness": ["nlp", "language", "tokens", "transformers", "text"],
        "nlp-awareness-nlp-turns-text-into-tokens-and-models-me": ["nlp", "tokens", "text", "models", "language"],
    },
    "ai-eng-awareness": {
        "ai-eng-awareness-ai-engineering-awareness": ["llm", "evaluation", "production", "prompt", "ops"],
        "ai-eng-awareness-ai-engineering-ships-reliable-llm-featur": ["llm", "evaluation", "production", "reliable", "features"],
    },
    "ai-eng-path": {
        "ai-eng-path-ai-engineering-learning-path": ["llm", "course", "engineering", "application", "learning"],
        "ai-eng-path-sketch-a-personal-learning-path-into-ai": ["llm", "course", "learning", "path", "application"],
    },
    "devops-path": {
        "devops-path-devops-learning-path": ["twelve-factor", "processes", "deploy", "config", "build"],
        "devops-path-sketch-a-personal-learning-path-into-dev": ["factor", "app", "deploy", "config", "release"],
    },
    "genai-path": {
        "genai-path-generative-ai-learning-path": ["prompt", "model", "text", "generation", "api"],
        "genai-path-sketch-a-personal-learning-path-into-gen": ["prompt", "text", "model", "api", "generation"],
    },
}

URL_PATCHES: dict[str, dict] = {
    # JS-heavy / bot-blocked replacements with fetchable exact docs
    "math-vectors-primary": {
        "url": "https://en.wikipedia.org/wiki/Euclidean_vector",
        "section": "Euclidean vector — definition and operations",
    },
    "math-matrices-primary": {
        "url": "https://en.wikipedia.org/wiki/Matrix_(mathematics)",
        "section": "Matrix — definition and multiplication",
    },
    "math-probability-primary": {
        "url": "https://en.wikipedia.org/wiki/Probability",
        "section": "Probability — interpretations and axioms",
    },
    "math-stats-summary-primary": {
        "url": "https://en.wikipedia.org/wiki/Summary_statistics",
        "section": "Summary statistics",
    },
    "math-gradient-intuition-primary": {
        "url": "https://en.wikipedia.org/wiki/Gradient",
        "section": "Gradient — definition and intuition",
    },
    "dl-nn-basics-primary": {
        "url": "https://cs231n.github.io/neural-networks-1/",
        "section": "Neural Networks Part 1 — architecture",
    },
    "dl-backprop-primary": {
        "url": "https://cs231n.github.io/optimization-2/",
        "section": "Backpropagation and gradient computation",
    },
    "dl-cnn-primary": {
        "url": "https://cs231n.github.io/convolutional-networks/",
        "section": "Convolutional Neural Networks",
    },
    "se-solid-srp-primary": {
        "url": "https://en.wikipedia.org/wiki/Single-responsibility_principle",
        "section": "Single-responsibility principle",
    },
    "se-solid-ocp-primary": {
        "url": "https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle",
        "section": "Open–closed principle",
    },
    "se-requirements-primary": {
        "url": "https://en.wikipedia.org/wiki/Requirement",
        "section": "Software requirements",
    },
    "net-dns-primary": {
        "url": "https://www.cloudflare.com/learning/dns/what-is-dns/",
        "section": "What is DNS?",
    },
    "net-tcp-udp-primary": {
        "url": "https://www.cloudflare.com/learning/ddos/glossary/tcp-ip/",
        "section": "TCP/IP and transport protocols",
    },
    "ml-classification-primary": {
        "url": "https://scikit-learn.org/stable/modules/tree.html",
        "section": "Decision Trees classification",
    },
    "ml-features-labels-primary": {
        "url": "https://scikit-learn.org/stable/tutorial/basic/tutorial.html",
        "section": "Loading features and labels / training",
    },
    "genai-rag-primary": {
        "url": "https://python.langchain.com/docs/concepts/rag/",
        "section": "RAG concepts",
    },
    "ai-eng-awareness-primary": {
        "url": "https://platform.openai.com/docs/guides/evaluation",
        "section": "Evals for LLM features",
    },
    "ai-eng-path-primary": {
        "url": "https://platform.openai.com/docs/guides/prompt-engineering",
        "section": "Prompt engineering foundation for AI eng path",
    },
    "dsa-counting-radix-learn-exact": {
        "url": "https://www.geeksforgeeks.org/radix-sort/",
        "section": "Radix sort",
    },
    "dsa-sort-complexity-learn-exact": {
        "url": "https://www.geeksforgeeks.org/time-complexities-of-all-sorting-algorithms/",
        "section": "Time complexities of sorting algorithms",
    },
    "dsa-lookup-patterns-learn-exact": {
        "url": "https://www.geeksforgeeks.org/two-sum-pair-with-given-sum/",
        "section": "Two sum / complement lookup",
    },
    "dsa-permutations-learn-exact": {
        "url": "https://www.geeksforgeeks.org/write-a-program-to-print-all-permutations-of-a-given-string/",
        "section": "Generate permutations",
    },
    "dsa-segment-tree-concept-learn-exact": {
        "url": "https://www.geeksforgeeks.org/segment-tree-set-1-sum-of-given-range/",
        "section": "Segment tree range queries",
    },
    "dsa-interview-hygiene-learn-exact": {
        "url": "https://www.geeksforgeeks.org/how-to-answer-a-coding-interview-question/",
        "section": "How to answer a coding interview question",
    },
    "dsa-dp-mindset-learn-exact": {
        "url": "https://www.geeksforgeeks.org/overlapping-subproblems-property-in-dynamic-programming-dp-1/",
        "section": "Overlapping subproblems",
    },
    "dsa-dp-state-learn-exact": {
        "url": "https://www.geeksforgeeks.org/steps-to-solve-a-dynamic-programming-problem/",
        "section": "Define DP state",
    },
    "dsa-dp-transition-learn-exact": {
        "url": "https://www.geeksforgeeks.org/steps-to-solve-a-dynamic-programming-problem/",
        "section": "Write recurrence / transition",
    },
    "dsa-subsequence-dp-learn-exact": {
        "url": "https://www.geeksforgeeks.org/longest-common-subsequence-dp-4/",
        "section": "LCS",
    },
    "dsa-interval-dp-learn-exact": {
        "url": "https://www.geeksforgeeks.org/matrix-chain-multiplication-dp-8/",
        "section": "Matrix chain / interval DP",
    },
    "dsa-advanced-dp-learn-exact": {
        "url": "https://www.geeksforgeeks.org/bitmasking-and-dynamic-programming-set-1-count-ways-to-assign-unique-cap-to-every-person/",
        "section": "Bitmask DP",
    },
    "dsa-dp-optimization-learn-exact": {
        "url": "https://www.geeksforgeeks.org/space-optimization-using-bit-manipulations/",
        "section": "Space optimization notes for DP",
    },
    "dsa-hash-map-learn-exact": {
        "url": "https://www.geeksforgeeks.org/hashmap-in-java/",
        "section": "HashMap",
    },
    "dsa-hash-set-learn-exact": {
        "url": "https://www.geeksforgeeks.org/hashset-in-java/",
        "section": "HashSet",
    },
    "java-composition-reference": {
        "url": "https://docs.oracle.com/javase/tutorial/java/javaOO/objectcreation.html",
        "section": "Creating objects / composition via fields",
    },
    "java-api-hygiene-reference": {
        "url": "https://docs.oracle.com/javase/tutorial/java/package/index.html",
        "section": "Packages",
    },
    "java-type-conversion-reference": {
        "url": "https://docs.oracle.com/javase/tutorial/java/nutsandbolts/datatypes.html",
        "section": "Primitive types and conversions",
    },
    "java-encapsulation-reference": {
        "url": "https://docs.oracle.com/javase/tutorial/java/javaOO/accesscontrol.html",
        "section": "Controlling Access to Members of a Class",
    },
    "java-map-reference": {
        "url": "https://docs.oracle.com/javase/tutorial/collections/interfaces/map.html",
        "section": "Map interface",
    },
}


def patch_evidence_terms() -> int:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    contracts = payload.get("contracts") or {}
    n = 0
    for topic, by_slug in EVIDENCE_PATCHES.items():
        raw = contracts.get(topic)
        if not raw:
            continue
        for c in raw.get("required") or []:
            slug = c.get("slug")
            if slug in by_slug:
                c["evidence_terms"] = by_slug[slug]
                n += 1
    DATA_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    load_contract_payload.cache_clear()
    return n


def apply_url_patches(db) -> int:
    now = datetime.now(timezone.utc).isoformat()
    fixed = 0
    for slug, spec in URL_PATCHES.items():
        row = db.query(CurriculumResource).filter(CurriculumResource.slug == slug).first()
        if not row:
            continue
        row.url = spec["url"]
        if spec.get("section"):
            row.section = spec["section"][:200]
        row.verification_status = VERIFICATION_NEEDS_REVIEW
        row.required_concepts_covered = []
        row.last_verified_at = now
        fixed += 1
    db.flush()
    return fixed


def main() -> None:
    print("evidence_terms_patched", patch_evidence_terms())
    db = SessionLocal()
    print("gap_url_repairs", apply_gap_url_repairs(db))
    print("url_patches", apply_url_patches(db))
    db.commit()

    domains = [
        "java",
        "dsa",
        "software-engineering",
        "backend",
        "mathematics",
        "ml",
        "python",
        "web",
        "networking",
        "devops",
        "data-science",
        "deep-learning",
        "genai",
        "mlops",
        "system-design",
        "nlp",
        "ai-engineering",
    ]
    for d in domains:
        print("===", d, verify_domains(db, domains=[d], workers=12))
        db.commit()

    print("norm", apply_lockdown_normalization(db))
    print("demote", demote_weak_verification(db))
    db.commit()
    sc = dict(Counter(a.readiness for a in audit_all(db)))
    print("SCORECARD", sc)
    non = [a for a in audit_all(db) if a.readiness != "READY"]
    print("nonready", len(non))
    for a in sorted(non, key=lambda x: (x.domain_key or "", x.topic_slug)):
        print(f"  {a.readiness:18} {a.domain_key:18} {a.topic_slug} missing={a.missing_required[:2]}")
    db.close()


if __name__ == "__main__":
    main()
