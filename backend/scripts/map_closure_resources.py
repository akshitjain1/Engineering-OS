"""Create learner-visible PRIMARY resources for the 24 closure topics."""
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"

TITLES = {
    "ml-ridge-lasso": ("Linear Models — Ridge/Lasso", "scikit-learn"),
    "ml-roc-auc": ("Model Evaluation — ROC/AUC", "scikit-learn"),
    "ml-regression-metrics": ("Model Evaluation — Regression metrics", "scikit-learn"),
    "ml-grid-search": ("Grid Search & Randomized Search", "scikit-learn"),
    "ml-kmeans": ("Clustering — K-means", "scikit-learn"),
    "ml-hierarchical-dbscan": ("Clustering — Hierarchical & DBSCAN", "scikit-learn"),
    "ml-pca": ("Decompositions — PCA", "scikit-learn"),
    "ml-anomaly-awareness": ("Novelty & Outlier Detection", "scikit-learn"),
    "ml-gradient-boosting": ("Ensembles — Gradient Boosting", "scikit-learn"),
    "ml-feature-importance": ("Permutation Importance", "scikit-learn"),
    "dl-pytorch-tensors": ("Tensors", "PyTorch"),
    "dl-pytorch-data": ("Datasets & DataLoaders", "PyTorch"),
    "dl-pytorch-build-model": ("Build the Model", "PyTorch"),
    "dl-pytorch-autograd": ("Automatic Differentiation", "PyTorch"),
    "dl-pytorch-training-loop": ("Optimize the Model", "PyTorch"),
    "dl-pytorch-save-load": ("Save & Load the Model", "PyTorch"),
    "cv-sift-orb-awareness": ("Introduction to SIFT", "OpenCV"),
    "genai-lora-peft": ("PEFT / LoRA documentation", "Hugging Face"),
    "genai-production-serving": ("vLLM serving engine docs", "vLLM"),
    "mlops-experiment-lifecycle": ("MLflow Tracking", "MLflow"),
    "mlops-drift-quality": ("MLflow Model Evaluation", "MLflow"),
    "math-dot-product-norms": ("Linear algebra", "D2L.ai"),
    "math-chain-rule": ("Multivariable calculus", "D2L.ai"),
    "math-covariance-correlation": ("Probability & statistics", "D2L.ai"),
}


def main() -> None:
    overrides = json.load(open(r"D:\Akshit Personal OS\backend\scripts\url_overrides.json",
                               encoding="utf-8"))
    v2 = json.load(open(f"{REPORT_DIR}\\decomposition_v2_log.json", encoding="utf-8"))["created_topics"]

    db = SessionLocal()
    created = []
    try:
        topics = {t.slug: t for t in db.query(CurriculumTopic).all()}
        lessons_by_tid = {}
        for l in db.query(CurriculumLesson).all():
            lessons_by_tid.setdefault(l.topic_id, []).append(l)
        has_resource = {row[0] for row in db.query(CurriculumResource.lesson_id).all()}

        for slug in sorted(v2):
            t = topics.get(slug)
            if not t or not lessons_by_tid.get(t.id):
                continue
            lesson = sorted(lessons_by_tid[t.id], key=lambda x: x.order_index)[0]
            if lesson.id in has_resource:
                continue
            url = (overrides.get(slug) or [None])[0]
            title, provider = TITLES.get(slug, (slug, None))
            res = CurriculumResource(
                slug=f"{slug}-primary",
                title=title,
                url=url,
                resource_type="documentation",
                provider=provider,
                description=(f"Learner unit bounded to the official section above; "
                             "content inspection pending."),
                official_unofficial="official",
                order_index=1,
                lesson_id=lesson.id,
                role="PRIMARY",
                verification_status="NEEDS_REVIEW",
                estimated_minutes=t.estimated_minutes or 25,
                required_concepts_covered=[],
                exactness="EXACT",
                notes="OFFICIAL_DOC_MAPPING — pending lockdown content inspection",
                last_verified_at=datetime.now(timezone.utc).isoformat(),
                learner_visible=True,
                visibility_class="LEARNER",
            )
            db.add(res)
            has_resource.add(lesson.id)
            created.append(slug)
        db.commit()
        print("resources created:", len(created))
        missing_url = [s for s in created if not (overrides.get(s) or [None])[0]]
        if missing_url:
            print("NO-URL slugs:", missing_url)
    finally:
        db.close()


if __name__ == "__main__":
    main()
