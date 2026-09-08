"""Restore the prerequisite edges the manifests cannot express.

## Why this file has to exist

The curriculum's source of truth is split, and this is where the seam shows.

316 of 449 topics are defined in reviewable YAML under
``content/curriculum/``. The other 133 — the whole of Deep Learning Core,
Computer Vision, NLP Core, GenAI, MLOps and the just-in-time maths — exist only
because ``content/d2_populate.py`` inserted them. They are in ``dev.db`` and in
the committed snapshot, but in no manifest.

Ten new manifests (Python tooling, reinforcement learning, cloud, AI security,
inference performance, retrieval quality, data quality, gradient boosting, time
series, CI/CD for ML) add 57 topics, and 49 of their prerequisite edges point
into that script-created set. Those edges are correct: reinforcement learning
really does depend on ``math-expectation-variance``, and gradient boosting
really does depend on ``ml-decision-trees``.

But ``tests/test_curriculum_v1.py`` and ``tests/test_anti_false_ready.py``
rebuild the curriculum from ``v1-index.yaml`` into an empty database, and an
edge pointing at a topic no manifest defines can never resolve there. Leaving
the edges in the manifests broke 13 tests. Deleting them outright would have
let the planner offer data leakage before cross-validation.

So the manifests keep only edges that resolve inside the manifest set, and the
49 that cross into script-created territory live here and are applied to the
database after import. Idempotent, and it never removes an edge it did not add.

**This is a workaround for the split, not a fix for it.** The real fix is to
express those 133 topics as manifests so the index is self-sufficient; then
this file can be deleted and its edges folded back in.

Run (after `python -m app.content.import_curriculum content/curriculum/v1-index.yaml`):
    python -m app.content.apply_gap_prerequisites --dry-run
    python -m app.content.apply_gap_prerequisites
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND / "dev.db"
REPORTS = BACKEND / "reports"

#: topic slug -> prerequisite slugs that live outside the manifest set.
#: Taken verbatim from the ten gap manifests before they were stripped.
GAP_PREREQUISITES: dict[str, tuple[str, ...]] = {
    # Reinforcement learning rests on probability, the ML taxonomy, gradient
    # descent in networks, and the existing awareness-level RLHF topic.
    "rl-mdp-fundamentals": ("math-expectation-variance", "ml-types-of-ml"),
    "rl-policy-gradients": ("dl-gradient-descent-nn", "math-partial-derivatives"),
    "rl-rlhf-mechanics": ("genai-instruction-tuning-rlhf", "genai-pretraining-finetuning"),
    # Security topics presuppose that you have already built the thing being
    # attacked: prompts, tool calls, agent loops, structured output.
    "aisec-owasp-llm-top-10": (
        "genai-prompt-engineering",
        "ai-eng-tool-calling",
        "ai-eng-observability-security",
    ),
    "aisec-prompt-injection": ("genai-prompt-engineering", "ai-eng-function-calling"),
    "aisec-data-exfiltration-tools": ("ai-eng-tool-calling", "ai-eng-agent-loops"),
    "aisec-improper-output-handling": ("ai-eng-structured-output",),
    "aisec-model-supply-chain": ("dl-pytorch-save-load",),
    # Inference performance needs tensors, attention and the context window.
    "infra-quantization-concepts": ("dl-pytorch-tensors",),
    "infra-kv-cache": (
        "dl-transformers-foundations",
        "dl-attention-intuition",
        "genai-context-windows",
    ),
    "infra-continuous-batching": ("genai-production-serving",),
    # Retrieval quality builds on the baseline retrieval and NLP topics.
    "rag-reranking-cross-encoders": ("nlp-bert",),
    "rag-hybrid-search": ("nlp-tf-idf",),
    "rag-chunking-evaluation": ("genai-chunking-retrieval",),
    "rag-ann-index-choice": ("genai-vector-databases",),
    # Renting a GPU only makes sense once you know what fills its memory.
    "cloud-gpu-instances": ("dl-pytorch-tensors",),
    "cloud-gpu-memory-sizing": ("dl-pytorch-tensors", "dl-batch-epoch-lr"),
    "cloud-managed-inference": ("genai-production-serving",),
    # Delivery topics presuppose the lifecycle they automate.
    "mlcicd-cd4ml": ("mlops-experiment-lifecycle",),
    "mlcicd-testing-ml-systems": ("ml-end-to-end-workflow",),
    "mlcicd-production-readiness": ("mlops-drift-quality",),
    # Data quality: leakage is only meaningful once you know what a fold is.
    "dq-data-leakage": ("ml-cross-validation", "ml-feature-scaling"),
    "dq-outliers": ("ml-anomaly-awareness",),
    "dq-class-imbalance": ("ml-confusion-matrix", "ml-roc-auc"),
    # Boosting needs trees, gradients and a tuning loop.
    "gbm-boosted-trees-theory": (
        "ml-gradient-boosting",
        "ml-decision-trees",
        "math-derivatives",
        "math-partial-derivatives",
    ),
    "gbm-xgboost-tuning": ("ml-grid-search", "ml-bias-variance"),
    "gbm-categorical-features": ("ml-encoding-categorical",),
    "gbm-tabular-vs-deep-learning": ("dl-why-deep-learning", "ml-bias-variance"),
    # Time series: the whole point is that the usual validation is wrong.
    "ts-why-random-splits-fail": ("ml-cross-validation", "ml-validation-split"),
    "ts-forecasting-baselines": ("ml-regression-metrics",),
    "ts-forecast-accuracy-metrics": ("ml-regression-metrics",),
}


def _slug_of(ref) -> str:
    return ref if isinstance(ref, str) else (ref or {}).get("slug", "")


def collect(conn: sqlite3.Connection) -> tuple[list[dict], list[str]]:
    conn.row_factory = sqlite3.Row
    known = {row["slug"] for row in conn.execute("SELECT slug FROM curriculum_topics WHERE slug IS NOT NULL")}

    planned: list[dict] = []
    problems: list[str] = []

    for topic_slug, extra in GAP_PREREQUISITES.items():
        row = conn.execute(
            "SELECT id, slug, prerequisites FROM curriculum_topics WHERE slug = ?", (topic_slug,)
        ).fetchone()
        if row is None:
            problems.append(f"topic {topic_slug!r} not in the database — import the manifests first")
            continue

        try:
            current = json.loads(row["prerequisites"] or "[]")
        except (TypeError, ValueError):
            current = []
        if not isinstance(current, list):
            current = []

        have = {_slug_of(ref) for ref in current}
        missing_targets = [slug for slug in extra if slug not in known]
        if missing_targets:
            problems.append(
                f"{topic_slug}: prerequisite target(s) {missing_targets} do not exist; skipping those"
            )

        to_add = [slug for slug in extra if slug not in have and slug in known]
        if not to_add:
            continue

        planned.append(
            {
                "id": row["id"],
                "topic_slug": topic_slug,
                "added": to_add,
                # Match the typed form the rest of the graph already uses.
                "prerequisites": current + [{"slug": slug, "type": "REQUIRED"} for slug in to_add],
            }
        )

    return planned, problems


def apply(conn: sqlite3.Connection, planned: list[dict]) -> int:
    for entry in planned:
        conn.execute(
            "UPDATE curriculum_topics SET prerequisites = ? WHERE id = ?",
            (json.dumps(entry["prerequisites"]), entry["id"]),
        )
    conn.commit()
    return len(planned)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    planned, problems = collect(conn)

    for problem in problems:
        print(f"  ! {problem}")
    print(f"{len(planned)} topic(s) need prerequisite edges restored, "
          f"{sum(len(p['added']) for p in planned)} edge(s) total")
    for entry in planned:
        print(f"  {entry['topic_slug']:32} += {', '.join(entry['added'])}")

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "gap_prerequisites.json").write_text(
        json.dumps({"planned": planned, "problems": problems, "dry_run": args.dry_run}, indent=2),
        encoding="utf-8",
    )

    if args.dry_run:
        print("\ndry run — nothing written")
        return
    print(f"\nrestored edges on {apply(conn, planned)} topic(s)")


if __name__ == "__main__":
    main()
