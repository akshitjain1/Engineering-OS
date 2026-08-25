"""Write url_overrides v6: new-topic mappings + final GAP remaps."""
import json
import pathlib

SK = "https://scikit-learn.org/stable/"
PYT = "https://docs.pytorch.org/tutorials/beginner/basics/"
D2L_RAW = "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/"

overrides = {
    # ── 24 new topics ──
    "ml-ridge-lasso": [SK + "modules/linear_model.html"],
    "ml-roc-auc": [SK + "modules/model_evaluation.html"],
    "ml-regression-metrics": [SK + "modules/model_evaluation.html"],
    "ml-grid-search": [SK + "modules/grid_search.html", SK + "modules/model_selection.html"],
    "ml-kmeans": [SK + "modules/clustering.html"],
    "ml-hierarchical-dbscan": [SK + "modules/clustering.html"],
    "ml-pca": [SK + "modules/decomposition.html"],
    "ml-anomaly-awareness": [SK + "modules/neighbors.html", SK + "modules/ensemble.html"],
    "ml-gradient-boosting": [SK + "modules/ensemble.html"],
    "ml-feature-importance": [SK + "modules/inspection.html", SK + "modules/permutation_importance.html"],
    "dl-pytorch-tensors": [PYT + "tensors.html"],
    "dl-pytorch-data": [PYT + "data.html", PYT + "transforms.html"],
    "dl-pytorch-build-model": [PYT + "buildmodel.html"],
    "dl-pytorch-autograd": [PYT + "autograd.html", PYT + "autogradqs.html"],
    "dl-pytorch-training-loop": [PYT + "optimization.html"],
    "dl-pytorch-save-load": [PYT + "saveloadrun.html"],
    "cv-sift-orb-awareness": ["https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html",
                              "https://docs.opencv.org/3.4/da/df5/tutorial_py_sift_intro.html"],
    "genai-lora-peft": ["https://huggingface.co/docs/peft/index",
                        "https://raw.githubusercontent.com/huggingface/peft/main/README.md"],
    "genai-production-serving": ["https://docs.vllm.ai/en/latest/", "https://docs.vllm.ai/en/v0.4.2/"],
    "mlops-experiment-lifecycle": ["https://mlflow.org/docs/latest/tracking/",
                                   "https://raw.githubusercontent.com/mlflow/mlflow/master/docs/source/tracking.rst",
                                   "https://docs.mlflow.org/en/latest/tracking.html"],
    "mlops-drift-quality": ["https://mlflow.org/docs/latest/model-evaluation/",
                            "https://raw.githubusercontent.com/mlflow/mlflow/master/docs/source/model-evaluation.rst"],
    "math-dot-product-norms": [D2L_RAW + "chapter_appendix-mathematics-for-deep-learning/linear-algebra.md"],
    "math-chain-rule": [D2L_RAW + "chapter_appendix-mathematics-for-deep-learning/multivariable-calculus.md",
                        "https://tutorial.math.lamar.edu/Classes/CalcI/ChainRule.aspx"],
    "math-covariance-correlation": [D2L_RAW + "chapter_appendix-mathematics-for-deep-learning/probability-and-stats.md",
                                    D2L_RAW + "chapter_appendix-mathematics-for-deep-learning/probability.md",
                                    "https://onlinestatbook.com/2/summary_stats/correlation.html"],

    # ── Final GAP remaps ──
    "cv-evaluation-metrics-cv": [D2L_RAW + "chapter_computer-vision/ssd.md",
                                 D2L_RAW + "chapter_computer-vision/bounding-box.md"],
    "nlp-encoder-vs-decoder": [D2L_RAW + "chapter_recurrent-modern/encoder-decoder.md",
                               "https://huggingface.co/course/chapter3/1"],
    "genai-hallucinations-guardrails": ["https://www.promptingguide.ai/risks/hallucinations",
                                        "https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails",
                                        "https://www.promptingguide.ai/risks"],
}

p = pathlib.Path(__file__).resolve().parent / "url_overrides.json"
current = json.loads(p.read_text(encoding="utf-8"))
current.update(overrides)
p.write_text(json.dumps(current, indent=2), encoding="utf-8")
print("overrides v6 written; entries:", len(current))
