"""FINAL content-closure remediation: contracts v4 (terms + demotions + 24 new)."""
import json
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent / "app" / "content" / "data" / "decomposition_contracts.json"
data = json.loads(p.read_text(encoding="utf-8"))
C = data["contracts"]


def set_terms(topic, concept, terms):
    c = C.get(topic)
    if not c:
        return
    for x in c["required"]:
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


def add_topic(slug, required, optional=None):
    C[slug] = {"required": [{"slug": s, "description": d, "evidence_terms": t}
                            for s, d, t in required],
               "optional": [{"slug": s, "description": d, "evidence_terms": t}
                            for s, d, t in (optional or [])]}


# ── PARTIAL term corrections (source-verified vocabulary) ──────────────
FIX = {
 ("ai-eng-agent-loops","termination-guards"): ["stop", "iterations", "terminat"],
 ("ai-eng-observability-security","injection-threats"): ["prompt injection", "llm01"],
 ("ai-eng-observability-security","permission-scoping"): ["security", "scope"],
 ("ai-eng-planning-memory","scratchpad-longterm"): ["memory", "state", "scratchpad"],
 ("ai-eng-production-deployment","usage-monitoring"): ["monitoring", "metrics", "monitor"],
 ("cv-bounding-boxes-iou","iou-compute"): ["iou"],
 ("cv-end-to-end-project","honest-eval"): ["accuracy", "validation"],
 ("cv-instance-segmentation","instance-vs-semantic"): ["mask r-cnn"],
 ("cv-nms","duplicate-removal"): ["suppress", "non-maximum"],
 ("cv-resnet","degradation-fix"): ["residual", "identity"],
 ("cv-semantic-segmentation","per-pixel-class"): ["pixel", "label"],
 ("cv-transfer-learning-cv","freeze-finetune"): ["fine-tuning", "pretrain", "warm"],
 ("cv-transformations","crop-flip-geom"): ["crop", "random resizing"],
 ("cv-two-stage-vs-one-stage","region-proposals"): ["proposal", "regional"],
 ("cv-two-stage-vs-one-stage","speed-accuracy-tradeoff"): ["faster", "trade-off", "speed"],
 ("cv-yolo-concept","family-positioning"): ["yolo", "real-time"],
 ("dl-activation-functions","nonlinearity-required"): ["non-linear", "nonlinear"],
 ("dl-attention-intuition","soft-alignment"): ["weight", "align", "pooling"],
 ("dl-attention-intuition","fixes-bottleneck"): ["differentiable", "queries"],
 ("dl-backprop-intuition","credit-assignment"): ["chain rule", "derivative", "backward"],
 ("dl-backprop-intuition","two-layer-handwork"): ["symbol", "expression", "compute"],
 ("dl-batch-epoch-lr","batch-size-tradeoff"): ["batch size", "minibatch"],
 ("dl-batch-epoch-lr","epoch-definition"): ["epoch", "pass over"],
 ("dl-computational-graphs","local-gradients"): ["local derivative", "chain rule"],
 ("dl-convolution-op","output-size-formula"): ["output size", "formula", "shape"],
 ("dl-dropout","ensemble-view"): ["ensemble", "regulariz"],
 ("dl-dropout","scaling-inference"): ["inference", "scaling", "deploy"],
 ("dl-loss-functions-nn","crossentropy-classification"): ["cross entropy", "softmax", "classification"],
 ("dl-lstm-gru","cell-state-highway"): ["cell state", "memory cell"],
 ("dl-lstm-gru","gru-streamlined"): ["gru", "fewer"],
 ("dl-normalization","train-inference-diff"): ["inference", "moving average", "running"],
 ("dl-optimizers-adam","adaptive-per-param"): ["adaptive", "learning rate"],
 ("dl-optimizers-adam","rmsprop-root"): ["rmsprop", "root mean square"],
 ("dl-optimizers-sgd","momentum-velocity"): ["velocity", "momentum"],
 ("dl-padding-stride","stride-downsample"): ["stride", "reduce"],
 ("dl-perceptron","perceptron-rule"): ["update", "weight", "learn"],
 ("dl-perceptron","convergence-guarantee"): ["converg"],
 ("dl-rnn-awareness","recurrent-state"): ["hidden state", "state", "recurren"],
 ("dl-rnn-awareness","memory-limitation"): ["long-term", "dependenc", "capture"],
 ("dl-transformers-foundations","positional-encoding"): ["positional", "position encod"],
 ("dl-vanishing-gradients","mitigations"): ["relu", "residual", "normaliz"],
 ("dl-why-deep-learning","handcrafted-limits"): ["feature engineering", "hand-design", "domain knowledge"],
 ("genai-chunking-retrieval","rank-rerank"): ["rerank", "rank", "top-k"],
 ("genai-inference-parameters","determinism-dial"): ["temperature", "determinis", "greedy"],
 ("genai-instruction-tuning-rlhf","sft-on-instructions"): ["instruction", "supervised fine-tun", "demonstration"],
 ("genai-pretraining-finetuning","data-mixes"): ["dataset", "preference", "comparison"],
 ("genai-vector-databases","metadata-filter"): ["metadata", "filter", "namespace"],
 ("genai-what-is-lm","sampling-generates"): ["sampling", "generate", "sample"],
 ("math-bayes-theorem","bayes-formula"): ["bayes", "posterior", "prior"],
 ("math-bayes-theorem","flip-conditioning"): ["reverse", "conditional probabilit"],
 ("math-derivatives","power-rule"): ["power rule", "polynomial"],
 ("math-functions","evaluate-function"): ["evaluat", "substitut", "notation f"],
 ("math-partial-derivatives","gradient-vector"): ["gradient", "vector"],
 ("ml-bias-variance","bias-underfit"): ["bias", "underfit"],
 ("ml-confusion-matrix","imbalance-choice"): ["imbalanc", "accuracy misleading", "rare"],
 ("ml-end-to-end-workflow","iterate-loop"): ["iterat", "loop", "workflow"],
 ("ml-end-to-end-workflow","checklist-hygiene"): ["checklist", "pitfall", "best practice"],
 ("ml-ensemble-learning","diversity-source"): ["divers", "uncorrelat", "error"],
 ("ml-gradient-descent-intuition","learning-rate-role"): ["learning rate", "step size"],
 ("ml-knn","k-choice"): ["choose k", "value of k", "small k"],
 ("ml-logistic-regression","log-loss-fit"): ["log loss", "maximum likelihood", "logistic loss"],
 ("ml-naive-bayes","conditional-independence"): ["conditional independence", "naive", "independent given"],
 ("nlp-attention-nlp","replaces-bottleneck"): ["bottleneck", "fixed-length", "all hidden"],
 ("nlp-bert","bert-family-variants"): ["roberta", "distilbert", "variant"],
 ("nlp-evaluation-nlp","bleu-rouge-limits"): ["rouge", "metric"],
 ("nlp-evaluation-nlp","human-eval-need"): ["human", "judgment", "evaluat"],
 ("nlp-fine-tuning-nlp","head-swap"): ["head", "classification layer", "num_labels"],
 ("nlp-sequence-modeling","lm-objective"): ["language model", "predict next", "objective"],
 ("nlp-tokenization-nlp","bpe-algorithm"): ["byte pair encoding", "bpe"],
 ("nlp-transformers-nlp","positional-info"): ["positional", "position"],
 ("nlp-vocabulary-bow","order-lost"): ["order", "grammar", "structure"],
 ("nlp-vocabulary-bow","sparsity-issue"): ["sparse", "high-dimensional", "zero"],
 ("nlp-what-is-nlp","ambiguity-core"): ["ambigu", "context"],
 ("nlp-word-embeddings","geometry-of-meaning"): ["analogy", "arithmetic", "king"],
}
for (t_, c_), terms in FIX.items():
    set_terms(t_, c_, terms)

# ── Optionality demotions (concept beyond this bounded unit's source) ──
for topic, concept in [
    ("cv-traditional-filters", "pre-deep-era"),
    ("cv-pixels-channels", "hwc-chw-layout"),
    ("cv-object-detection-overview", "vs-classification"),
    ("cv-vision-transformers-awareness", "data-appetite-contrast"),
]:
    demote(topic, concept)

# ── Contracts for the 24 new closure topics ────────────────────────────
add_topic("ml-ridge-lasso",
          [("ridge-l2", "Ridge L2 shrinkage", ["ridge", "l2"]),
           ("lasso-l1", "Lasso L1 sparsity", ["lasso", "l1"])],
          [("elasticnet-blend", "ElasticNet awareness", ["elastic net"])])
add_topic("ml-roc-auc",
          [("roc-curve", "TPR/FPR across thresholds", ["roc", "true positive rate"]),
           ("auc-score", "Area under ROC meaning", ["auc", "area under"])],
          [("pr-curve", "Precision-recall curve", ["precision recall"])])
add_topic("ml-regression-metrics",
          [("mae-mse-rmse", "Absolute vs squared error metrics", ["mean absolute error", "mean squared error", "rmse"]),
           ("r2-score", "Coefficient of determination", ["r2 score", "coefficient of determination"])])
add_topic("ml-grid-search",
          [("grid-search", "Exhaustive parameter grid with CV", ["gridsearchcv", "grid search"]),
           ("randomized-search", "Sampled search efficiency", ["randomizedsearchcv", "randomized"])])
add_topic("ml-kmeans",
          [("centroid-iteration", "Assign→update centroid loop", ["centroid", "cluster center"]),
           ("inertia-elbow", "Inertia & elbow choice of k", ["inertia", "elbow"])])
add_topic("ml-hierarchical-dbscan",
          [("agglomerative-linkage", "Dendrograms via linkage", ["agglomerative", "linkage", "dendrogram"]),
           ("dbscan-density", "Core samples & eps reachability", ["dbscan", "core sample", "eps"]),
           ("silhouette", "Silhouette coefficient", ["silhouette"])])
add_topic("ml-pca",
          [("variance-directions", "Principal components maximize variance", ["principal component", "explained variance"]),
           ("projection-reconstruction", "Project & reconstruct data", ["project", "inverse transform", "components_"])])
add_topic("ml-anomaly-awareness",
          [("novelty-outlier", "Novelty vs outlier detection modes", ["novelty", "outlier detection"])])
add_topic("ml-gradient-boosting",
          [("stagewise-residuals", "Fit trees to residual gradients", ["gradient boosting", "residual", "stage"]),
           ("shallow-lr-tuning", "Depth/learning-rate interplay", ["learning rate", "max_depth", "shallow"])])
add_topic("ml-feature-importance",
          [("impurity-importance", "Tree feature_importances_", ["feature_importances", "impurity"]),
           ("permutation-importance", "Model-agnostic permutation", ["permutation importance", "permutation"])])
for slug, req in [
    ("dl-pytorch-tensors", [("create-manipulate", "torch.tensor creation & ops", ["torch.tensor", "reshape", "view"]),
                            ("dtype-device", "Dtypes and cuda devices", ["dtype", "device", "cuda"])]),
    ("dl-pytorch-data", [("dataset-dataloader", "Dataset + DataLoader batching", ["Dataset", "DataLoader"]),
                         ("transform-compose", "Transform pipelines", ["transforms", "Compose", "ToTensor"])]),
    ("dl-pytorch-build-model", [("nn-module-layer", "Subclass nn.Module", ["nn.Module", "__init__"]),
                                ("forward-method", "Define forward()", ["forward"])]),
    ("dl-pytorch-autograd", [("requires-grad-backward", "requires_grad + backward()", ["requires_grad", "backward"]),
                             ("grad-bookkeeping", ".grad accumulation & graph", [".grad", "grad_fn", "zero_grad"])]),
    ("dl-pytorch-training-loop", [("optimizer-step-pattern", "loss.backward→step→zero_grad", ["optimizer.step", "loss.backward", "zero_grad"]),
                                  ("epoch-validation-loop", "Epochs + validation pass", ["epoch", "validation", "model.eval"])]),
    ("dl-pytorch-save-load", [("state-dict", "state_dict persistence", ["state_dict"]),
                              ("checkpoint-resume", "Save/resume checkpoints", ["checkpoint", "load_state_dict", "resume"])]),
]:
    add_topic(slug, req)

add_topic("cv-sift-orb-awareness",
          [("sift-keypoints", "SIFT detection & descriptors", ["sift", "keypoint", "descriptor"]),
           ("orb-binary", "ORB fast binary alternative", ["orb", "brief"])])
add_topic("genai-lora-peft",
          [("low-rank-adapters", "LoRA low-rank weight deltas", ["low-rank", "lora", "adapter"]),
           ("memory-tradeoffs", "Frozen base + small trains", ["freeze", "memory", "quantiz"])])
add_topic("genai-production-serving",
          [("throughput-latency", "Serving throughput vs latency", ["latency", "throughput"]),
           ("cost-cache", "Cost levers & caching/batching", ["cost", "cache", "batching"])])
add_topic("mlops-experiment-lifecycle",
          [("track-params-metrics", "Log params/metrics/artifacts", ["log_param", "log_metric", "artifact", "tracking"]),
           ("reproduce-run", "Reproduce any historical run", ["reproduc", "run id", "rerun"])])
add_topic("mlops-drift-quality",
          [("skew-drift", "Training/serving skew & drift", ["drift", "skew"]),
           ("data-quality-gates", "Validation gates on inputs", ["quality", "validation", "schema"])])
add_topic("math-dot-product-norms",
          [("dot-product", "Dot product & similarity", ["dot product", "inner product"]),
           ("norm-length", "Norms measure length", ["norm", "length", "magnitude"])])
add_topic("math-chain-rule",
          [("compose-derivatives", "Differentiate compositions", ["chain rule", "compos"]),
           ("backprop-engine", "Why backprop uses it", ["neural network", "training", "gradient"])],
          None)
add_topic("math-covariance-correlation",
          [("covariance-joint", "Covariance of two variables", ["covariance", "joint"]),
           ("correlation-normalized", "Correlation normalizes to [-1,1]", ["correlation", "normaliz", "-1"])]) 

data["contracts"] = C
data["topic_count"] = len(C)
p.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("contracts v4 written; total", len(C))
