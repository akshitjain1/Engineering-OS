"""Content-closure decomposition v2: fill genuine curriculum holes.

ADDITIVE ONLY. Adds 24 bounded units explicitly required by the closure spec:
  ML: ridge/lasso, ROC-AUC, regression metrics, grid/randomized search,
      k-means, hierarchical+DBSCAN(+silhouette), PCA, anomaly awareness,
      gradient boosting, permutation importance
  DL: official PyTorch beginner implementation spine (6 units -> exact
      tutorial pages)
  CV: traditional features (SIFT/ORB) awareness
  GenAI: LoRA/PEFT, production serving economics
  MLOps: lifecycle/reproducibility, drift & data quality
  Math: dot product/norms, chain rule, covariance/correlation
"""
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import CurriculumLesson, CurriculumModule, CurriculumTopic

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"

D2L_MATH = "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_appendix-mathematics-for-deep-learning/"
PYT = "https://docs.pytorch.org/tutorials/beginner/basics/"

NEW_TOPICS = {
    "mod-ml-core": [
        ("ml-ridge-lasso", "Ridge & Lasso regularization",
         "Constrain linear weights with L2/L1 penalties; pick via validation.",
         ["ml-linear-regression"], 30),
        ("ml-roc-auc", "ROC curves & AUC",
         "Read TPR/FPR across thresholds; compare models with AUC and PR curves.",
         ["ml-confusion-matrix"], 25),
        ("ml-regression-metrics", "Regression metrics",
         "Interpret MAE vs MSE vs RMSE vs R² and when each misleads.",
         ["ml-loss-intuition"], 20),
        ("ml-grid-search", "Hyperparameter search",
         "Grid vs randomized search with cross-validation and validation curves.",
         ["ml-cross-validation"], 25),
        ("ml-kmeans", "K-means clustering",
         "Iterative centroid assignment; elbow/silhouette choice of k.",
         ["ml-feature-scaling"], 25),
        ("ml-hierarchical-dbscan", "Hierarchical clustering & DBSCAN",
         "Dendrograms vs density reachability; noise handling without fixed k.",
         ["ml-kmeans"], 25),
        ("ml-pca", "Principal component analysis",
         "Project onto top-variance directions; explained variance & whitening.",
         ["ml-feature-scaling", "math-matrices"], 30),
        ("ml-anomaly-awareness", "Anomaly detection awareness",
         "Novelty vs outlier detection settings; when unsupervised flags fail.",
         ["ml-kmeans"], 20),
        ("ml-gradient-boosting", "Gradient boosting",
         "Fit trees to residual gradients stage-wise; learning-rate/shallow-depth.",
         ["ml-random-forests"], 30),
        ("ml-feature-importance", "Feature importance",
         "Impurity importances vs permutation importance; correlation pitfalls.",
         ["ml-random-forests"], 20),
    ],
    "mod-dl-core": [
        ("dl-pytorch-tensors", "PyTorch tensors",
         "Create/reshape/index tensors; dtypes and GPU devices.",
         [], 30),
        ("dl-pytorch-data", "Datasets, DataLoader & transforms",
         "Package samples; batch/shuffle loaders; compose transforms.",
         ["dl-pytorch-tensors"], 30),
        ("dl-pytorch-build-model", "Building models with nn.Module",
         "Layers + forward(); inspect parameters by shape.",
         ["dl-pytorch-data"], 30),
        ("dl-pytorch-autograd", "Autograd mechanics",
         "requires_grad, backward(), .grad bookkeeping; graph freeing.",
         ["dl-pytorch-build-model"], 30),
        ("dl-pytorch-training-loop", "Full optimization loop",
         "loss.backward + optimizer.step pattern; train/validate split loop.",
         ["dl-pytorch-autograd", "dl-batch-epoch-lr"], 35),
        ("dl-pytorch-save-load", "Save & load runs",
         "state_dict persistence; resume checkpoints reliably.",
         ["dl-pytorch-training-loop"], 20),
    ],
    "mod-cv": [
        ("cv-sift-orb-awareness", "SIFT & ORB awareness",
         "Keypoint descriptors before deep features; where they still win.",
         ["cv-traditional-filters"], 20),
    ],
    "mod-genai": [
        ("genai-lora-peft", "LoRA & parameter-efficient fine-tuning",
         "Train low-rank adapters instead of full weights; memory tradeoffs.",
         ["genai-pretraining-finetuning"], 25),
        ("genai-production-serving", "LLM serving economics",
         "Latency/throughput levers, KV-cache reuse, cost per token, autoscaling.",
         ["genai-inference-parameters"], 25),
    ],
    "mod-mlops": [
        ("mlops-experiment-lifecycle", "ML lifecycle & reproducibility",
         "Track params/metrics/artifacts so any run can be reproduced.",
         ["ml-end-to-end-workflow"], 25),
        ("mlops-drift-quality", "Drift & data quality",
         "Training/serving skew, input vs label drift, quality gates.",
         ["mlops-monitoring" if False else "mlops-serving"], 25),
    ],
}

MATH_APPENDIX = {
    "mod-math-jit": [
        ("math-dot-product-norms", "Dot products & norms",
         "Similarity via dot product; lengths via L2 norm; cosine intuition.",
         ["math-vectors"], D2L_MATH + "linear-algebra.md"),
        ("math-chain-rule", "Chain rule",
         "Compose derivatives through nested functions — backprop's engine.",
         ["math-derivatives"], D2L_MATH + "multivariable-calculus.md"),
        ("math-covariance-correlation", "Covariance & correlation",
         "Joint spread and normalized dependence between two variables.",
         ["math-expectation-variance"], D2L_MATH + "probability-and-stats.md"),
    ],
}


def get_module(db, slug):
    return db.query(CurriculumModule).filter(CurriculumModule.slug == slug).first()


def main() -> None:
    db = SessionLocal()
    created = []
    try:
        existing = {t.slug for t in db.query(CurriculumTopic).all()}

        def next_order(module_id):
            rows = [t.order_index for t in db.query(CurriculumTopic).filter(
                CurriculumTopic.module_id == module_id).all()]
            return max(rows) + 1 if rows else 1

        plan = {}
        for mod_slug, defs in NEW_TOPICS.items():
            mod = get_module(db, mod_slug)
            assert mod, mod_slug
            plan[mod.id] = [(s, n, o, p, m) for s, n, o, p, m in defs]
        for mod_slug, defs in MATH_APPENDIX.items():
            mod = get_module(db, mod_slug)
            assert mod, mod_slug
            plan[mod.id] = [(s, n, o, p, 20) for s, n, o, p, _src in defs]

        for module_id, defs in plan.items():
            for slug, name, objective, prereqs, minutes in defs:
                if slug in existing:
                    continue
                t = CurriculumTopic(
                    slug=slug,
                    name=name,
                    description=(f"{objective}\n\nObjective: {objective.rstrip('.')}\n\n"
                                 "Mastery:\n"
                                 f"- Explain {name.lower()} without notes.\n"
                                 "- Work one concrete micro-example.\n"
                                 "- State one common misconception."),
                    module_id=module_id,
                    order_index=next_order(module_id),
                    prerequisites=list(prereqs),
                    fast_trackable=True,
                    learning_track="CORE",
                    depth_target="MECHANICS",
                    parallel_eligible=False,
                    estimated_minutes=minutes,
                    domain_key=slug.split("-")[0],
                )
                db.add(t)
                db.flush()
                db.add(CurriculumLesson(slug=f"{slug}-lesson", title=name,
                                        description=f"Learning unit for {name}.",
                                        topic_id=t.id, order_index=1,
                                        hours_estimated=max(0.25, round(minutes / 60, 2))))
                created.append(slug)
                existing.add(slug)

        # Enforcement: CNN training requires the PyTorch loop unit (additive edge).
        cnnf = db.query(CurriculumTopic).filter(
            CurriculumTopic.slug == "dl-cnn-foundations").first()
        if cnnf is not None:
            have = {(p.get("slug") if isinstance(p, dict) else p)
                    for p in (cnnf.prerequisites or [])}
            if "dl-pytorch-training-loop" not in have:
                cnnf.prerequisites = list(cnnf.prerequisites or []) + [
                    {"slug": "dl-pytorch-training-loop", "type": "REQUIRED"}]

        db.commit()
        out = {"generated_at": datetime.now(timezone.utc).isoformat(),
               "created_count": len(created), "created_topics": sorted(created)}
        json.dump(out, open(f"{REPORT_DIR}\\decomposition_v2_log.json", "w",
                            encoding="utf-8"), indent=2)
        print(json.dumps({k: v for k, v in out.items() if k != "created_topics"}, indent=2))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
