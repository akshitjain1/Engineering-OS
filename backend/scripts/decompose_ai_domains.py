"""Decompose thin AI/ML domains into full spec progressions.

ADDITIVE ONLY (RULE 1):
- Never touches existing topic rows' IDs/slugs/descriptions.
- Existing prerequisite edges are preserved; only NEW edges are added,
  including enforcement edges onto placeholder/substantive AI topics.
- Creates new topics + one lesson each (matches 316:316 pattern).
- Idempotent: re-running adds nothing.

Domains expanded per spec Phases 5-10:
  Math-for-ML, Machine Learning, Deep Learning, Computer Vision (NEW),
  NLP, Generative AI, AI Engineering.
"""
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import (
    CurriculumTopic,
    CurriculumModule,
    CurriculumSubject,
    CurriculumLesson,
)

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"


# ── Topic definitions ────────────────────────────────────────────────
# (slug, name, objective, prereqs[list of str OR dict], minutes, depth, track)

MATH_TOPICS = [
    ("math-functions", "Functions intuition",
     "Understand functions as input-output mappings — the foundation for derivatives and gradients.",
     ["math-stats-summary"], 20, "INTUITION"),
    ("math-derivatives", "Derivatives intuition",
     "Read a derivative as instantaneous rate of change; compute simple power/rule derivatives.",
     ["math-functions"], 25, "MECHANICS"),
    ("math-partial-derivatives", "Partial derivatives",
     "Differentiate multi-variable functions one variable at a time — the seed of gradients.",
     ["math-derivatives", {"slug": "math-vectors", "type": "RECOMMENDED"}], 25, "MECHANICS"),
    ("math-conditional-probability", "Conditional probability",
     "Compute P(A|B) and reason about updated beliefs given evidence.",
     ["math-probability"], 20, "MECHANICS"),
    ("math-bayes-theorem", "Bayes theorem",
     "Apply Bayes' rule to flip conditioning; connect to Naive Bayes classifiers.",
     ["math-conditional-probability"], 20, "MECHANICS"),
    ("math-expectation-variance", "Expectation & variance",
     "Compute expected value and spread; interpret them in loss and evaluation contexts.",
     ["math-probability"], 20, "MECHANICS"),
]

ML_TOPICS = [
    ("ml-types-of-ml", "Types of machine learning",
     "Distinguish supervised, unsupervised, and reinforcement settings with one example each.",
     ["ml-what-is-ml"], 18, "AWARENESS"),
    ("ml-validation-split", "Validation split",
     "Explain why train/test alone leaks decisions; carve out a validation set.",
     ["ml-train-test"], 15, "MECHANICS"),
    ("ml-loss-intuition", "Cost & loss intuition",
     "Interpret a loss surface; explain why squared error punishes large misses.",
     ["ml-linear-regression"], 20, "INTUITION"),
    ("ml-gradient-descent-intuition", "Gradient descent intuition",
     "Descend a loss surface step by step; relate step size to learning rate.",
     ["ml-loss-intuition", "math-gradient-intuition", "math-derivatives"], 25, "INTUITION"),
    ("ml-logistic-regression", "Logistic regression",
     "Map outputs through a sigmoid to probabilities; pick thresholds deliberately.",
     ["ml-classification"], 30, "MECHANICS"),
    ("ml-decision-trees", "Decision trees",
     "Trace splits by information gain/Gini; state why trees overfit deeply grown leaves.",
     ["ml-classification"], 30, "MECHANICS"),
    ("ml-random-forests", "Random forests",
     "Bootstrap + feature bagging → variance reduction; explain OOB estimates.",
     ["ml-decision-trees"], 25, "MECHANICS"),
    ("ml-knn", "K-nearest neighbors",
     "Classify by vote of neighbors; discuss k, distance choice, and scaling sensitivity.",
     ["ml-classification"], 20, "MECHANICS"),
    ("ml-naive-bayes", "Naive Bayes",
     "Apply Bayes' theorem with conditional independence; classic text baseline.",
     ["ml-classification", "math-bayes-theorem"], 25, "MECHANICS"),
    ("ml-svm", "Support vector machines",
     "Maximum-margin intuition; kernels lift features to separate non-linear data.",
     ["ml-classification"], 25, "MECHANICS"),
    ("ml-confusion-matrix", "Confusion matrix deep dive",
     "Derive precision/recall/F1 from TP/FP/FN/TN; choose metrics for imbalanced data.",
     ["ml-metrics"], 20, "MECHANICS"),
    ("ml-bias-variance", "Bias–variance tradeoff",
     "Diagnose underfit vs overfit from train/val gaps; pick remedies accordingly.",
     ["ml-overfitting"], 20, "INTUITION"),
    ("ml-cross-validation", "Cross-validation",
     "K-fold rotation gives robust estimates on small data; stratify classification folds.",
     ["ml-validation-split"], 20, "MECHANICS"),
    ("ml-feature-scaling", "Feature scaling",
     "Standardize/normalize so distance-based methods and gradient descent behave.",
     ["ds-feature-eng"], 15, "MECHANICS"),
    ("ml-encoding-categorical", "Encoding categorical data",
     "One-hot vs ordinal vs target encoding; leakage dangers in target statistics.",
     ["ds-feature-eng"], 20, "MECHANICS"),
    ("ml-ensemble-learning", "Ensemble learning",
     "Bagging cuts variance, boosting cuts bias, stacking blends strengths.",
     ["ml-random-forests"], 20, "INTUITION"),
    ("ml-end-to-end-workflow", "End-to-end ML workflow",
     "Frame problem → data → features → model → validate → iterate: the full loop once.",
     ["ml-sklearn-pipeline", "ml-cross-validation"], 35, "APPLICATION"),
]

DL_TOPICS = [
    ("dl-why-deep-learning", "Why deep learning?",
     "State the problem handcrafted features could not solve; name what representation learning buys.",
     ["ml-end-to-end-workflow"], 15, "AWARENESS"),
    ("dl-neuron-intuition", "Neuron intuition",
     "Weighted sum + nonlinearity as a tiny decision unit; connect back to linear models.",
     ["dl-why-deep-learning", "ml-logistic-regression"], 20, "INTUITION"),
    ("dl-perceptron", "Perceptron",
     "Trace the perceptron learning rule on toy data; state its linear-limitation result.",
     ["dl-neuron-intuition"], 20, "MECHANICS"),
    ("dl-activation-functions", "Activation functions",
     "Compare sigmoid/tanh/ReLU families; explain why nonlinearity is non-negotiable.",
     ["dl-neuron-intuition"], 20, "MECHANICS"),
    ("dl-forward-propagation", "Forward propagation",
     "Push shapes and numbers through layer-by-layer; verify output dimension reasoning.",
     ["dl-activation-functions"], 25, "MECHANICS"),
    ("dl-loss-functions-nn", "Loss functions for networks",
     "Choose MSE vs cross-entropy deliberately; tie output activation to loss pairing.",
     ["dl-forward-propagation", "ml-loss-intuition"], 20, "MECHANICS"),
    ("dl-backprop-intuition", "Backpropagation intuition",
     "Chain rule backwards through a computational graph on paper for a 2-layer net.",
     ["dl-loss-functions-nn", "math-partial-derivatives"], 30, "INTUITION"),
    ("dl-computational-graphs", "Computational graphs",
     "Represent expressions as graphs; see how autodiff generalizes backprop.",
     ["dl-backprop-intuition"], 20, "MECHANICS"),
    ("dl-gradient-descent-nn", "Gradient descent in networks",
     "Update weights end-to-end once by hand-scale; connect LR to stability.",
     ["dl-computational-graphs"], 20, "MECHANICS"),
    ("dl-mlp", "Multi-layer perceptrons",
     "Build/train an MLP mentally: hidden widths, depth, parameter counting.",
     ["dl-gradient-descent-nn"], 25, "IMPLEMENTATION"),
    ("dl-vanishing-gradients", "Vanishing & exploding gradients",
     "Explain saturation and depth amplification; name ReLU/residuals as mitigations.",
     ["dl-mlp"], 20, "INTUITION"),
    ("dl-initialization", "Initialization",
     "Xavier/He scaling keeps signal variance stable at depth-one pass.",
     ["dl-vanishing-gradients"], 15, "MECHANICS"),
    ("dl-normalization", "Normalization layers",
     "BatchNorm steadies internal distributions; LayerNorm powers transformers.",
     ["dl-initialization"], 20, "MECHANICS"),
    ("dl-dropout", "Dropout",
     "Random deactivation as cheap ensembling; train vs inference mode distinction.",
     ["dl-mlp"], 15, "MECHANICS"),
    ("dl-optimizers-sgd", "SGD & momentum",
     "Noisy but honest steps; momentum accumulates velocity across flat regions.",
     ["dl-gradient-descent-nn"], 20, "MECHANICS"),
    ("dl-optimizers-adam", "RMSProp & Adam",
     "Per-parameter adaptive rates; when Adam's defaults win and when SGD generalizes better.",
     ["dl-optimizers-sgd"], 20, "MECHANICS"),
    ("dl-batch-epoch-lr", "Batch size, epochs, learning rate",
     "Trade noise/stability/throughput; schedule LR decay deliberately.",
     ["dl-optimizers-adam"], 20, "MECHANICS"),
    ("dl-cnn-foundations", "CNN foundations",
     "Why shared weights beat dense nets on images: locality + translation structure.",
     ["dl-batch-epoch-lr"], 20, "INTUITION"),
    ("dl-convolution-op", "Convolution operation",
     "Slide kernels over inputs; compute output sizes by hand for small cases.",
     ["dl-cnn-foundations"], 25, "MECHANICS"),
    ("dl-padding-stride", "Padding & stride",
     "Control spatial shrinkage; SAME vs VALID reasoning.",
     ["dl-convolution-op"], 15, "MECHANICS"),
    ("dl-pooling", "Pooling",
     "Downsample with max/avg; state what invariance it buys and costs.",
     ["dl-padding-stride"], 15, "MECHANICS"),
    ("dl-feature-maps", "Feature maps & channels",
     "Stack conv layers into channel volumes; trace tensor shape end to end.",
     ["dl-pooling"], 20, "MECHANICS"),
    ("dl-rnn-awareness", "RNN awareness",
     "Recurrence shares weights across time; name vanishing-memory failure mode.",
     ["dl-mlp"], 15, "AWARENESS"),
    ("dl-lstm-gru", "LSTM & GRU",
     "Gates as learned memory controllers; GRU as streamlined LSTM.",
     ["dl-rnn-awareness"], 25, "MECHANICS"),
    ("dl-attention-intuition", "Attention intuition",
     "Query-key-value lookup replaces fixed-size bottlenecks; alignment becomes dynamic.",
     ["dl-lstm-gru"], 25, "INTUITION"),
    ("dl-transformers-foundations", "Transformer foundations",
     "Self-attention blocks + residuals + norms stack into modern architectures.",
     ["dl-attention-intuition"], 30, "MECHANICS"),
]

CV_TOPICS = [
    ("cv-what-is-an-image", "What is an image?",
     "Grids of intensity values; resolution and aspect ratio consequences.",
     [], 15, "AWARENESS"),
    ("cv-pixels-channels", "Pixels & channels",
     "Index pixels; separate H×W×C tensor layout conventions (HWC vs CHW).",
     ["cv-what-is-an-image"], 15, "MECHANICS"),
    ("cv-color-spaces", "RGB & grayscale",
     "Channel mixing to gray; when color carries signal vs noise.",
     ["cv-pixels-channels"], 15, "MECHANICS"),
    ("cv-image-tensors", "Image tensors",
     "Batch tensors for networks; normalize ranges and dtype traps.",
     ["cv-color-spaces"], 20, "MECHANICS"),
    ("cv-transformations", "Image transformations",
     "Resize/crop/flip geometrically; interpolation artifacts awareness.",
     ["cv-image-tensors"], 20, "MECHANICS"),
    ("cv-normalization-cv", "Normalization for vision",
     "Match pretrained stats (mean/std per channel); avoid silent distribution drift.",
     ["cv-transformations"], 15, "MECHANICS"),
    ("cv-augmentation", "Data augmentation",
     "Label-preserving transforms expand data; over-augmentation destroys signal.",
     ["cv-normalization-cv"], 20, "MECHANICS"),
    ("cv-traditional-filters", "Traditional CV filters",
     "Edge/blur detectors before deep learning; convolution lineage starts here.",
     ["cv-what-is-an-image"], 20, "AWARENESS"),
    ("cv-convolution-in-cv", "Convolution for images",
     "Reuse DL conv mechanics on real image grids; stride/padding effects visually.",
     ["cv-traditional-filters", "dl-feature-maps"], 25, "MECHANICS"),
    ("cv-classification-workflow", "Image classification workflow",
     "Data → augment → CNN → softmax → metrics; assemble the standard loop.",
     ["cv-convolution-in-cv", "dl-cnn"], 30, "APPLICATION"),
    ("cv-classic-architectures", "LeNet → AlexNet → VGG",
     "Depth/history arc: what each added and why it mattered.",
     ["cv-classification-workflow"], 25, "AWARENESS"),
    ("cv-resnet", "ResNet & residual learning",
     "Identity shortcuts defeat degradation; skip connections as gradient highways.",
     ["cv-classic-architectures", "dl-vanishing-gradients"], 25, "MECHANICS"),
    ("cv-efficientnet-awareness", "EfficientNet awareness",
     "Compound scaling of depth/width/resolution; know when to reach for it.",
     ["cv-resnet"], 15, "AWARENESS"),
    ("cv-transfer-learning-cv", "Transfer learning for vision",
     "Freeze/fine-tune pretrained backbones; small-data wins explained.",
     ["cv-resnet"], 25, "APPLICATION"),
    ("cv-object-detection-overview", "Object detection overview",
     "Classification + localization jointly; output space of boxes+classes.",
     ["cv-classification-workflow"], 20, "AWARENESS"),
    ("cv-bounding-boxes-iou", "Bounding boxes & IoU",
     "Box formats; IoU computation by hand; matching threshold meaning.",
     ["cv-object-detection-overview"], 20, "MECHANICS"),
    ("cv-nms", "Non-maximum suppression",
     "Suppress duplicate detections; score-order greedy algorithm trace.",
     ["cv-bounding-boxes-iou"], 20, "MECHANICS"),
    ("cv-two-stage-vs-one-stage", "Two-stage vs one-stage detection",
     "Region proposals (R-CNN family) vs direct prediction (YOLO/SSD) tradeoffs.",
     ["cv-nms"], 20, "AWARENESS"),
    ("cv-yolo-concept", "YOLO family concept",
     "Single-shot grid predictions; speed/accuracy positioning across versions.",
     ["cv-two-stage-vs-one-stage"], 20, "AWARENESS"),
    ("cv-semantic-segmentation", "Semantic segmentation",
     "Per-pixel classes; encoder–decoder shape recovery idea.",
     ["cv-classification-workflow"], 25, "MECHANICS"),
    ("cv-u-net", "U-Net",
     "Skip connections fuse coarse and fine features; biomedical origin story.",
     ["cv-semantic-segmentation"], 25, "MECHANICS"),
    ("cv-instance-segmentation", "Instance segmentation & Mask R-CNN",
     "Separate overlapping instances; mask branch atop detection pipeline.",
     ["cv-u-net", "cv-two-stage-vs-one-stage"], 25, "AWARENESS"),
    ("cv-evaluation-metrics-cv", "CV evaluation metrics",
     "mAP construction; per-class recall pitfalls; segmentation IoU/Dice.",
     ["cv-bounding-boxes-iou"], 20, "MECHANICS"),
    ("cv-vision-transformers-awareness", "Vision Transformers awareness",
     "Patch embeddings route images through transformer stacks; data appetite contrast.",
     ["dl-transformers-foundations"], 20, "AWARENESS"),
    ("cv-end-to-end-project", "End-to-end CV project",
     "Ship one classifier or detector: data prep → train → evaluate → reflect.",
     ["cv-transfer-learning-cv", "cv-evaluation-metrics-cv"], 60, "PROJECT"),
]

NLP_TOPICS = [
    ("nlp-what-is-nlp", "What is NLP?",
     "Language tasks landscape; ambiguity as core difficulty.",
     [], 15, "AWARENESS"),
    ("nlp-text-preprocessing", "Text preprocessing",
     "Clean/case/normalize pipelines; why aggressive cleaning can hurt deep models.",
     ["nlp-what-is-nlp"], 20, "MECHANICS"),
    ("nlp-tokenization-nlp", "Tokenization",
     "Words vs subwords vs characters; vocabulary size/out-of-vocab tradeoffs.",
     ["nlp-text-preprocessing"], 25, "MECHANICS"),
    ("nlp-vocabulary-bow", "Vocabulary & bag of words",
     "Count vectors lose order but baseline hard; sparsity implications.",
     ["nlp-tokenization-nlp"], 20, "MECHANICS"),
    ("nlp-tf-idf", "TF-IDF",
     "Weight rarity; build a search-style similarity baseline.",
     ["nlp-vocabulary-bow"], 20, "MECHANICS"),
    ("nlp-word-embeddings", "Word embeddings",
     "Dense vectors encode similarity; geometry of meaning introduction.",
     ["nlp-tf-idf", "math-vectors"], 25, "INTUITION"),
    ("nlp-word2vec", "Word2Vec",
     "Skip-gram/CBOW training intuition; analogies from vector arithmetic.",
     ["nlp-word-embeddings"], 25, "MECHANICS"),
    ("nlp-sequence-modeling", "Sequence modeling",
     "Order matters: language modeling objective framing.",
     ["nlp-word-embeddings"], 20, "INTUITION"),
    ("nlp-rnn-lstm", "RNN/LSTM for text",
     "Recurrence over tokens; LSTM gating counters vanishing memory.",
     ["nlp-sequence-modeling", "dl-lstm-gru"], 25, "MECHANICS"),
    ("nlp-attention-nlp", "Attention for sequences",
     "Soft alignment fixes fixed-vector bottleneck; attention weights readable.",
     ["nlp-rnn-lstm", "dl-attention-intuition"], 25, "MECHANICS"),
    ("nlp-transformers-nlp", "Transformers in NLP",
     "Stacked self-attention processes tokens in parallel; positional encodings restore order.",
     ["nlp-attention-nlp", "dl-transformers-foundations"], 30, "MECHANICS"),
    ("nlp-bert", "BERT & encoders",
     "Masked LM pretraining; bidirectional context for understanding tasks.",
     ["nlp-transformers-nlp"], 25, "MECHANICS"),
    ("nlp-encoder-vs-decoder", "Encoder vs decoder",
     "Understanding vs generation architectures; when each fits.",
     ["nlp-bert"], 20, "MECHANICS"),
    ("nlp-generative-models", "Generative NLP models",
     "Autoregressive decoding; GPT-family lineage overview.",
     ["nlp-encoder-vs-decoder"], 20, "AWARENESS"),
    ("nlp-fine-tuning-nlp", "Fine-tuning for NLP",
     "Adapt pretrained checkpoints to tasks; head swap + light tuning recipe.",
     ["nlp-generative-models"], 25, "APPLICATION"),
    ("nlp-evaluation-nlp", "NLP evaluation",
     "Perplexity, BLEU/ROUGE limits, human eval necessity.",
     ["nlp-fine-tuning-nlp"], 20, "MECHANICS"),
]

GENAI_TOPICS = [
    ("genai-what-is-lm", "What is a language model?",
     "Probability distribution over next tokens; sampling makes it generative.",
     ["nlp-sequence-modeling"], 20, "INTUITION"),
    ("genai-next-token-prediction", "Next-token prediction",
     "Train loop of masking/predicting; emergent capability framing.",
     ["genai-what-is-lm"], 20, "MECHANICS"),
    ("genai-tokenization-llm", "LLM tokenization",
     "BPE subwords in production LLMs; cost/context implications of token counts.",
     ["genai-next-token-prediction", "nlp-tokenization-nlp"], 20, "MECHANICS"),
    ("genai-pretraining-finetuning", "Pretraining → fine-tuning pipeline",
     "Stages from base model to usable assistant; data mixes at each stage.",
     ["genai-next-token-prediction"], 25, "MECHANICS"),
    ("genai-instruction-tuning-rlhf", "Instruction tuning & RLHF awareness",
     "SFT then preference optimization; alignment vs capability distinction.",
     ["genai-pretraining-finetuning"], 25, "AWARENESS"),
    ("genai-inference-parameters", "Inference parameters",
     "Temperature/top-k/top-p steering; determinism vs creativity dial.",
     ["genai-what-is-lm"], 20, "MECHANICS"),
    ("genai-context-windows", "Context windows",
     "Finite attention span economics; truncation strategies.",
     ["genai-tokenization-llm"], 15, "MECHANICS"),
    ("genai-prompt-engineering", "Prompt engineering",
     "Role/format/examples patterns; iteration discipline and eval harnesses.",
     ["genai-context-windows"], 25, "APPLICATION"),
    ("genai-vector-databases", "Vector databases",
     "ANN indexes trade recall/latency; persistence and filtering basics.",
     ["genai-embeddings"], 25, "MECHANICS"),
    ("genai-chunking-retrieval", "Chunking & retrieval",
     "Split documents semantically; embed chunks; rank and rerank.",
     ["genai-vector-databases"], 25, "MECHANICS"),
    ("genai-hallucinations-guardrails", "Hallucinations & guardrails",
     "Why fluent ≠ factual; grounding, validation, refusal patterns.",
     ["genai-rag", "genai-eval"], 25, "MECHANICS"),
]

AIENG_TOPICS = [
    ("ai-eng-structured-output", "Structured output",
     "Schema-constrained generation; JSON modes and validation loops.",
     ["genai-prompt-engineering"], 20, "MECHANICS"),
    ("ai-eng-tool-calling", "Tool calling",
     "Model decides to invoke tools; request/response contract design.",
     ["ai-eng-structured-output"], 25, "MECHANICS"),
    ("ai-eng-function-calling", "Function calling patterns",
     "Typed signatures, error surfacing, idempotency for model-invoked functions.",
     ["ai-eng-tool-calling"], 20, "MECHANICS"),
    ("ai-eng-agent-loops", "Agent loops",
     "Observe→think→act cycles with termination conditions; runaway-cost guards.",
     ["ai-eng-tool-calling"], 30, "MECHANICS"),
    ("ai-eng-planning-memory", "Planning & memory",
     "Task decomposition strategies; short-term scratchpad vs long-term stores.",
     ["ai-eng-agent-loops"], 25, "MECHANICS"),
    ("ai-eng-multi-agent-awareness", "Multi-agent awareness",
     "Role-specialized agents hand off work; coordination overhead honesty.",
     ["ai-eng-planning-memory"], 20, "AWARENESS"),
    ("ai-eng-observability-security", "Observability & security",
     "Tracing prompts/costs/latency; injection threats and permission scopes.",
     ["genai-agents"], 25, "MECHANICS"),
    ("ai-eng-production-deployment", "Production deployment",
     "Versioned prompts, eval gates in CI, rollback strategy, usage monitoring.",
     ["ai-eng-observability-security", "ops-ci-github-actions"], 30, "APPLICATION"),
]


def get_or_create_module(db, subject_id: int, slug: str, name: str) -> CurriculumModule:
    mod = db.query(CurriculumModule).filter(CurriculumModule.slug == slug).first()
    if mod:
        return mod
    mod = CurriculumModule(
        slug=slug,
        name=name,
        description=f"Auto-created during AI domain decomposition (additive).",
        subject_id=subject_id,
        order_index=90 + subject_id,
    )
    db.add(mod)
    db.flush()
    return mod


def main() -> None:
    db = SessionLocal()
    created_topics = []
    skipped_existing = []
    added_edges = []
    try:
        subjects = {s.slug: s.id for s in db.query(CurriculumSubject).all()}
        subj_ml = subjects["ml-foundations"]
        subj_math = subjects["math-for-ml"]
        subj_ai = subjects["ai-systems-design"]

        mod_math = get_or_create_module(db, subj_math, "mod-math-jit", "Just-in-time calculus & probability")
        mod_ml = db.query(CurriculumModule).filter(CurriculumModule.slug == "mod-ml-core").first()
        mod_dl_core = get_or_create_module(db, subj_ai, "mod-dl-core", "Deep Learning Core")
        mod_cv = get_or_create_module(db, subj_ai, "mod-cv", "Computer Vision")
        mod_nlp_core = get_or_create_module(db, subj_ai, "mod-nlp-core", "NLP Core")
        mod_genai = db.query(CurriculumModule).filter(CurriculumModule.slug == "mod-genai").first()
        mod_aieng = db.query(CurriculumModule).filter(CurriculumModule.slug == "mod-mlops").first()

        groups = [
            (mod_math, MATH_TOPICS),
            (mod_ml, ML_TOPICS),
            (mod_dl_core, DL_TOPICS),
            (mod_cv, CV_TOPICS),
            (mod_nlp_core, NLP_TOPICS),
            (mod_genai, GENAI_TOPICS),
            (mod_aieng, AIENG_TOPICS),
        ]

        all_slugs_existing = {t.slug for t in db.query(CurriculumTopic).all()}

        def next_order(module_id: int) -> int:
            top_orders = [
                t.order_index
                for t in db.query(CurriculumTopic).filter(CurriculumTopic.module_id == module_id).all()
            ]
            return (max(top_orders) + 1) if top_orders else 1

        for mod, defs in groups:
            for idx, (slug, name, objective, prereqs, minutes, depth) in enumerate(defs):
                if slug in all_slugs_existing:
                    skipped_existing.append(slug)
                    continue
                topic = CurriculumTopic(
                    slug=slug,
                    name=name,
                    description=(
                        f"{objective}\n\n"
                        f"Objective: {objective.rstrip('.')}\n\n"
                        f"Mastery:\n"
                        f"- Explain {name.lower()} without notes.\n"
                        f"- Work one concrete micro-example.\n"
                        f"- State one common misconception."
                    ),
                    module_id=mod.id,
                    order_index=next_order(mod.id),
                    prerequisites=list(prereqs),
                    fast_trackable=True,
                    learning_track="CORE",
                    depth_target=depth,
                    parallel_eligible=False,
                    estimated_minutes=minutes,
                    domain_key=slug.split("-")[0],
                )
                db.add(topic)
                db.flush()
                lesson = CurriculumLesson(
                    slug=f"{slug}-lesson",
                    title=name,
                    description=f"Learning unit for {name}.",
                    topic_id=topic.id,
                    order_index=1,
                    hours_estimated=max(0.25, round(minutes / 60, 2)),
                )
                db.add(lesson)
                created_topics.append(slug)
                all_slugs_existing.add(slug)

        # Enforcement edges onto EXISTING topics (additive only — never removed).
        enforcement = {
            "dl-nn-basics": [{"slug": "dl-perceptron", "type": "REQUIRED"}],
            "dl-backprop": [{"slug": "dl-computational-graphs", "type": "REQUIRED"}],
            "dl-cnn": [{"slug": "dl-cnn-foundations", "type": "REQUIRED"}],
            "dl-transformers-intro": [{"slug": "dl-transformers-foundations", "type": "REQUIRED"}],
            "genai-rag": [{"slug": "genai-chunking-retrieval", "type": "REQUIRED"}],
            "genai-agents": [{"slug": "ai-eng-agent-loops", "type": "REQUIRED"}],
            "nlp-path": [{"slug": "nlp-what-is-nlp", "type": "REQUIRED"}],
            "cv-placeholder-guard": [],
        }
        for slug, extras in enforcement.items():
            if not extras:
                continue
            t = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
            if not t:
                continue
            existing_slugs = {
                p if isinstance(p, str) else (p.get("slug") or p.get("topic"))
                for p in (t.prerequisites or [])
            }
            changed = False
            for ref in extras:
                if ref["slug"] not in existing_slugs:
                    t.prerequisites = list(t.prerequisites or []) + [ref]
                    added_edges.append((slug, ref["slug"]))
                    changed = True

        db.commit()

        summary = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "created_topics": created_topics,
            "created_count": len(created_topics),
            "skipped_existing": skipped_existing,
            "added_enforcement_edges": [list(e) for e in added_edges],
        }
        with open(f"{REPORT_DIR}\\decomposition_log.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(json.dumps({k: v for k, v in summary.items() if k != "created_topics"}, indent=2))
        print("Created:", len(created_topics))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
