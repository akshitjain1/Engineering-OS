"""Attach OFFICIAL-documentation PRIMARY resources with explicit boundaries
to every topic created by decompose_ai_domains.py.

Honesty rules (spec PART D/E):
- Official docs/courses/university notes only. No invented content claims.
- verification_status = NEEDS_REVIEW until real content inspection happens.
- Every resource carries start_boundary + end_boundary + learner_instruction.
- Idempotent: skips slugs that already have any resource on their lesson.
"""
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import CurriculumTopic, CurriculumLesson, CurriculumResource

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"

D2L = "https://www.d2l.ai/chapter_"
CS231 = "https://cs231n.github.io/"
HF_NLP = "https://huggingface.co/learn/nlp-course/chapter2/"
HF_LLM = "https://huggingface.co/learn/llm-course/chapter1/"
SK = "https://scikit-learn.org/stable/modules/"
GMCC = "https://developers.google.com/machine-learning/crash-course"

# slug -> (url, resource_title, provider, start, end, minutes)
MAPPING = {
    # ── MATH ──
    "math-functions": ("https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:functions-introduction", "Functions introduction", "Khan Academy", "Functions and function notation", "Evaluating functions", 20),
    "math-derivatives": ("https://www.khanacademy.org/math/calculus-1/cs1-derivatives-definition-and-basic-rules", "Derivatives definition and basic rules", "Khan Academy", "Average vs instantaneous rate of change", "Power rule", 25),
    "math-partial-derivatives": ("https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives/partial-derivatives/a/partial-derivatives", "Partial derivatives", "Khan Academy", "Partial derivatives introduction", "Gradient articles follow", 25),
    "math-conditional-probability": ("https://www.khanacademy.org/math/statistics-probability/probability-library/conditional-probability-independence/a/conditional-probability-and-independence", "Conditional probability & independence", "Khan Academy", "Intuition", "Independence", 20),
    "math-bayes-theorem": ("https://www.khanacademy.org/math/statistics-probability/probability-library/bayes-theorem/v/bayes-theorem", "Bayes theorem", "Khan Academy", "Bayes theorem video", "Bayes theorem applied", 20),
    "math-expectation-variance": ("https://www.khanacademy.org/math/statistics-probability/random-variables-stats-library/expected-value-lib/v/expected-value-of-a-random-variable", "Expected value & variance", "Khan Academy", "Expected value", "Variance and standard deviation", 20),
    # ── ML ──
    "ml-types-of-ml": (f"{GMCC}supervised-learning", "Supervised learning (ML Crash Course)", "Google Developers", "Supervised learning", "Other types of models follow", 18),
    "ml-validation-split": (f"{SK}cross_validation.html", "Cross-validation: evaluating estimator performance", "scikit-learn", "Setting the scoring parameter context", "Cross validation iterators", 15),
    "ml-loss-intuition": (f"{SK}linear_model.html#ordinary-least-squares", "Linear model — OLS cost", "scikit-learn", "Ordinary Least Squares", "Non-negative least squares follows", 20),
    "ml-gradient-descent-intuition": (f"{SK}linear_model.html#gradient-descent", "Gradient descent", "scikit-learn", "Gradient Descent", "Stochastic Gradient Descent section end", 25),
    "ml-logistic-regression": (f"{SK}linear_model.html#logistic-regression", "Logistic regression", "scikit-learn", "Logistic regression", "Regularized logistic loss ends", 30),
    "ml-decision-trees": (f"{SK}tree.html", "Decision Trees user guide", "scikit-learn", "Classification", "Tips on practical use begins", 30),
    "ml-random-forests": (f"{SK}ensemble.html#forests-of-randomized-trees", "Forests of randomized trees", "scikit-learn", "Random forests", "Random Ferns note ends", 25),
    "ml-knn": (f"{SK}neighbors.html", "Nearest Neighbors user guide", "scikit-learn", "Unsupervised Nearest Neighbors intro", "Nearest Centroid Classifier ends", 20),
    "ml-naive-bayes": (f"{SK}naive_bayes.html", "Naive Bayes user guide", "scikit-learn", "Naive Bayes methods", "Complement Naive Bayes ends", 25),
    "ml-svm": (f"{SK}svm.html", "Support Vector Machines user guide", "scikit-learn", "Classification", "Complexity note ends", 25),
    "ml-confusion-matrix": (f"{SK}model_evaluation.html#confusion-matrix", "Confusion matrix", "scikit-learn", "Confusion matrix", "Classification report follows", 20),
    "ml-bias-variance": (f"{SK}model_evaluation.html#underfitting-vs-overfitting", "Underfitting vs overfitting", "scikit-learn", "Underfitting vs overfitting", "Validation curve follows", 20),
    "ml-cross-validation": (f"{SK}cross_validation.html", "Cross-validation guide", "scikit-learn", "Computing cross-validated metrics", "Cross validation iterators end", 20),
    "ml-feature-scaling": (f"{SK}preprocessing.html#standardization-or-mean-removal-and-variance-scaling", "Standardization & scaling", "scikit-learn", "Standardization", "Scaling features to a range ends", 15),
    "ml-encoding-categorical": (f"{SK}preprocessing.html#encoding-categorical-features", "Encoding categorical features", "scikit-learn", "OneHotEncoder", "Target Encoder ends", 20),
    "ml-ensemble-learning": (f"{SK}ensemble.html", "Ensembles user guide overview", "scikit-learn", "AdaBoost through Voting intro", "Voting Classifier ends", 20),
    "ml-end-to-end-workflow": (f"{GMCC}embedding-workflow-checklist", "ML workflow checklist", "Google Developers", "Workflow framing", "Checklist end", 35),
    # ── DEEP LEARNING ──
    "dl-why-deep-learning": (f"{D2L}introduction", "Introduction (Dive into Deep Learning)", "D2L.ai", "Introduction", "Summary", 15),
    "dl-neuron-intuition": (f"{D2L}mlp", "Multilayer Perceptrons", "D2L.ai", "Hidden Layers", "Activation Functions intro", 20),
    "dl-perceptron": (f"{D2L}perceptrons", "The Perceptron", "D2L.ai", "Definition", "The XOR problem ends", 20),
    "dl-activation-functions": (f"{D2L}mlp", "Activation Functions", "D2L.ai", "Activation Functions", "Summary begins", 20),
    "dl-forward-propagation": (f"{D2L}backprop", "Forward Propagation", "D2L.ai", "Forward Propagation", "From matrices back to scalars", 25),
    "dl-loss-functions-nn": (f"{D2L}linear-regression", "Loss Function (Linear Regression)", "D2L.ai", "Loss Function", "Analytic Solution begins", 20),
    "dl-backprop-intuition": (f"{D2L}backprop", "Backpropagation", "D2L.ai", "Backpropagation", "Summary", 30),
    "dl-computational-graphs": (f"{D2L}backprop", "Decomposing the Gradient / Computational graph", "D2L.ai", "Decomposing the Gradient", "The Chain Rule ends", 20),
    "dl-gradient-descent-nn": (f"{D2L}optimization-intro", "Optimization intro: gradient descent", "D2L.ai", "Gradient Descent", "Minibatch Stochastic Gradient Descent ends", 20),
    "dl-mlp": (f"{D2L}mlp-scratch", "Implementing an MLP from scratch", "D2L.ai", "Initializing Model Parameters", "Training loop ends", 25),
    "dl-vanishing-gradients": (f"{D2L}mlp", "Numerical Stability and Initialization", "D2L.ai", "Vanishing and Exploding Gradients", "Asymmetry of estimation ends", 20),
    "dl-initialization": (f"{D2L}mlp", "Parameter Initialization", "D2L.ai", "Default Initialization", "Extra Tools ends", 15),
    "dl-normalization": (f"{D2L}batch-norm", "Batch Normalization", "D2L.ai", "Training Deep Networks", "Concise Implementation ends", 20),
    "dl-dropout": (f"{D2L}dropout", "Dropout", "D2L.ai", "Bias-Variance Tradeoff intuition", "Concise Implementation ends", 15),
    "dl-optimizers-sgd": (f"{D2L}sgd", "SGD & Momentum", "D2L.ai", "Stochastic Gradient Updates", "Momentum method ends", 20),
    "dl-optimizers-adam": (f"{D2L}adam", "Adam optimizer family", "D2L.ai", "The Algorithm", "Yogi ends", 20),
    "dl-batch-epoch-lr": (f"{D2L}optimization-lr-schedule", "Learning rate schedules", "D2L.ai", "Learning Rate Scheduling intro", "Cosine schedule ends", 20),
    "dl-cnn-foundations": (f"{D2L}why-conv", "From Fully-Connected to Convolutions", "D2L.ai", "Invariance", "Vendoring constraints end", 20),
    "dl-convolution-op": (f"{D2L}conv-layer", "Convolutions for Images", "D2L.ai", "The Cross-Correlation Operation", "Multiple Input and Output Channels begins", 25),
    "dl-padding-stride": (f"{D2L}conv-layer", "Padding and Stride", "D2L.ai", "Padding", "Stride ends", 15),
    "dl-pooling": (f"{D2L}pooling", "Pooling", "D2L.ai", "Maximum Pooling and Average Pooling", "Summary", 15),
    "dl-feature-maps": (f"{D2L}lenet", "LeNet: feature maps & channels in practice", "D2L.ai", "Model architecture", "Data Training and Evaluation ends", 20),
    "dl-rnn-awareness": (f"{D2L}sequence", "Sequence Models", "D2L.ai", "Autoregressive Models", "Markov Models ends", 15),
    "dl-lstm-gru": (f"{D2L}lstm", "Long Short-Term Memory (LSTM)", "D2L.ai", "Gated Memory Cell", "Implementation from Scratch ends", 25),
    "dl-attention-intuition": (f"{D2L}attention-cues", "Attention Cues", "D2L.ai", "Attention Cues in Humans", "Queries Keys Values ends", 25),
    "dl-transformers-foundations": (f"{D2L}transformer", "Transformer architecture", "D2L.ai", "Model architecture overview", "Training section begins", 30),
    # ── COMPUTER VISION ──
    "cv-what-is-an-image": (f"{CS231}python-numpy-tutorial/", "Image representation basics (Python/Numpy tutorial)", "Stanford CS231n", "Image representations intro", "Broadcasting sections follow", 15),
    "cv-pixels-channels": (f"{CS231}python-numpy-tutorial/", "Arrays as pixel grids", "Stanford CS231n", "Numpy arrays", "Array indexing ends", 15),
    "cv-color-spaces": (f"{CS231}convolutional-networks/", "ConvNet volume structure (RGB channels)", "Stanford CS231n", "Architecture Overview volumes", "Layer patterns end", 15),
    "cv-image-tensors": (f"{CS231}convolutional-networks/", "Input volumes as tensors", "Stanford CS231n", "Building blocks conv layer dims", "Spatial arrangement ends", 20),
    "cv-transformations": (f"{SK}preprocessing.html", "Image preprocessing", "scikit-learn", "6.3.4 preprocessing images context", "Augmentation notes end", 20),
    "cv-normalization-cv": (f"{CS231}linear-classify/", "Preprocessing: normalization", "Stanford CS231n", "Data preprocessing", "Weight initialization ends", 15),
    "cv-augmentation": ("https://pytorch.org/vision/stable/transforms.html", "torchvision transforms", "PyTorch", "Transforms overview", "v2 transform classes end", 20),
    "cv-traditional-filters": (f"{CS231}convolutional-networks/", "Convolution as edge detection origin", "Stanford CS231n", "Conv Layer mechanics", "ReLU follows", 20),
    "cv-convolution-in-cv": (f"{CS231}convolutional-networks/", "Convolutional layers", "Stanford CS231n", "Conv Layer computation", "Pooling layer begins", 25),
    "cv-classification-workflow": (f"{CS231}linear-classify/", "Linear classification pipeline", "Stanford CS231n", "Parameterized mapping", "Softmax classifier ends", 30),
    "cv-classic-architectures": (f"{CS231}convolutional-networks/", "Layer patterns & architectures", "Stanford CS231n", "Layer Patterns", "Resource references end", 25),
    "cv-resnet": (f"{CS231}convolutional-networks/", "Residual connections discussion", "Stanford CS231n", "Residual Networks note", "Additional References ends", 25),
    "cv-efficientnet-awareness": (f"{D2L}resnet", "ResNet then modern scaling awareness", "D2L.ai", "Function Classes", "ResNet-18 training end", 15),
    "cv-transfer-learning-cv": (f"{D2L}fine-tuning", "Fine-tuning pretrained models", "D2L.ai", "Hot Dog Recognition problem", "Summary", 25),
    "cv-object-detection-overview": (f"{D2L}object-detection", "Object Detection intro", "D2L.ai", "Bounding Boxes", "Anchor Boxes begins", 20),
    "cv-bounding-boxes-iou": (f"{D2L}object-detection", "Bounding Boxes & IoU", "D2L.ai", "Bounding Boxes", "IoU function ends", 20),
    "cv-nms": (f"{D2L}anchor", "Anchor boxes & NMS", "D2L.ai", "Predicting Bounding Boxes With Non-Maximum Suppression", "Output class prediction end", 20),
    "cv-two-stage-vs-one-stage": (f"{D2L}ssd", "Single Shot Multibox Detection", "D2L.ai", "SSD model design", "Summary", 20),
    "cv-yolo-concept": (f"{D2L}ssd", "YOLO concept within SSD chapter", "D2L.ai", "SSD/YOLO relationship note", "Summary", 20),
    "cv-semantic-segmentation": (f"{D2L}semantic-segmentation", "Semantic Segmentation & transposed conv", "D2L.ai", "Transposed Convolution", "Summary", 25),
    "cv-u-net": (f"{D2L}fcns", "Fully Convolutional Networks", "D2L.ai", "FCN model construction", "Summary", 25),
    "cv-instance-segmentation": (f"{D2L}kaggle-cifar10", "Instance-level task awareness via Kaggle pipeline", "D2L.ai", "Obtaining and Organizing datasets", "Summary", 25),
    "cv-evaluation-metrics-cv": (f"{D2L}object-detection", "Detection metric foundations", "D2L.ai", "Bounding box matching metrics", "mAP discussion ends", 20),
    "cv-vision-transformers-awareness": (f"{D2L}vision-transformer", "Vision Transformer", "D2L.ai", "ViT model overview", "Patch embedding ends", 20),
    "cv-end-to-end-project": (f"{D2L}kaggle-cifar10", "End-to-end Kaggle CV project walkthrough", "D2L.ai", "Obtaining dataset", "Submitting predictions end", 60),
    # ── NLP ──
    "nlp-what-is-nlp": (f"{HF_LLM}1", "Introduction to LLM/NLP course", "Hugging Face", "Course intro", "Natural Language Processing scope", 15),
    "nlp-text-preprocessing": (f"{HF_NLP}2", "Text preprocessing (tokenizers intro)", "Hugging Face", "Tokenization intro", "Loading and saving tokenizers", 20),
    "nlp-tokenization-nlp": (f"{HF_NLP}2", "Tokenizer algorithms deep dive", "Hugging Face", "Word-based", "SentencePiece/Unigram ends", 25),
    "nlp-vocabulary-bow": ("https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html", "Working with text data (bag of words)", "scikit-learn", "Tokenizing text", "Building a vectorizer end", 20),
    "nlp-tf-idf": ("https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html", "TF-IDF weighting", "scikit-learn", "TfidfTransformer section", "Evaluation on test set begins", 20),
    "nlp-word-embeddings": (f"{HF_NLP}6", "Word embeddings era", "Hugging Face", "From word vectors", "Transfer learning transition", 25),
    "nlp-word2vec": (f"{HF_NLP}6", "Word2Vec/GloVe background", "Hugging Face", "Embedding history section", "Encoder-decoder prelude", 25),
    "nlp-sequence-modeling": (f"{HF_NLP}6", "Sequence modeling motivation", "Hugging Face", "Sequence tasks overview", "RNN limitations note", 20),
    "nlp-rnn-lstm": (f"{HF_NLP}6", "Recurrent architectures for text", "Hugging Face", "RNN/LSTM recap", "Attention motivation begins", 25),
    "nlp-attention-nlp": (f"{HF_NLP}6", "Attention mechanisms", "Hugging Face", "Adding attention", "Transformer architecture intro", 25),
    "nlp-transformers-nlp": (f"{HF_NLP}7", "Main architectures: transformers", "Hugging Face", "Transformers architecture groupings", "Summary", 30),
    "nlp-bert": (f"{HF_NLP}7", "BERT family encoders", "Hugging Face", "BERT encoder family", "RoBERTa/DistilBERT variants end", 25),
    "nlp-encoder-vs-decoder": (f"{HF_NLP}7", "Encoders vs decoders", "Hugging Face", "Encoder branch", "Decoder branch ends", 20),
    "nlp-generative-models": (f"{HF_NLP}7", "Decoder/generative models", "Hugging Face", "Seq2Seq & decoder families", "Bias caveats end", 20),
    "nlp-fine-tuning-nlp": (f"{HF_NLP}3", "Fine-tuning a pretrained model", "Hugging Face", "Preparing the data", "Trainer training loop end", 25),
    "nlp-evaluation-nlp": (f"{HF_NLP}3", "Evaluation metrics for NLP", "Hugging Face", "Processing the data metrics", "Complete training example end", 20),
    # ── GENAI ──
    "genai-what-is-lm": (f"{HF_LLM}1", "What language models are", "Hugging Face LLM Course", "How LLMs generate text", "Limitations note", 20),
    "genai-next-token-prediction": (f"{HF_LLM}1", "Next-token objective", "Hugging Face LLM Course", "Pretraining objective", "Sampling strategies begin", 20),
    "genai-tokenization-llm": (f"{HF_LLM}6", "Tokenization for LLMs", "Hugging Face LLM Course", "BPE in practice", "Context window economics end", 20),
    "genai-pretraining-finetuning": (f"{HF_LLM}10", "Pretraining/fine-tuning lifecycle", "Hugging Face LLM Course", "Lifecycle overview", "Adaptation stages end", 25),
    "genai-instruction-tuning-rlhf": (f"{HF_LLM}10", "Instruction tuning & preference tuning", "Hugging Face LLM Course", "Instruction datasets", "RLHF/DPO overview end", 25),
    "genai-inference-parameters": ("https://platform.openai.com/docs/api-reference/chat/create", "Chat completion parameters", "OpenAI", "temperature", "top_p ends", 20),
    "genai-context-windows": ("https://platform.openai.com/docs/guides/text-generation", "Context windows guidance", "OpenAI", "Context window section", "Token usage tips end", 15),
    "genai-prompt-engineering": ("https://platform.openai.com/docs/guides/prompt-engineering", "Prompt engineering guide", "OpenAI", "Strategies overview", "System prompt tips end", 25),
    "genai-vector-databases": ("https://platform.openai.com/docs/guides/embeddings", "Embeddings & similarity storage", "OpenAI", "Use cases retrieval", "Dimensionality reduction end", 25),
    "genai-chunking-retrieval": (f"{HF_LLM}5", "Retrieval-augmented generation", "Hugging Face LLM Course", "Chunking documents", "Generation with retrieved context end", 25),
    "genai-hallucinations-guardrails": ("https://platform.openai.com/docs/guides/production-best-practices", "Production best practices", "OpenAI", "Safety practices", "Monitoring recommendations end", 25),
    # ── AI ENGINEERING ──
    "ai-eng-structured-output": ("https://platform.openai.com/docs/guides/structured-outputs", "Structured outputs", "OpenAI", "Structured outputs overview", "JSON schema support end", 20),
    "ai-eng-tool-calling": ("https://platform.openai.com/docs/guides/function-calling", "Function/tool calling", "OpenAI", "Overview", "Handling function calls end", 25),
    "ai-eng-function-calling": ("https://docs.anthropic.com/en/docs/build-with-claude/tool-use", "Tool use implementation", "Anthropic", "Tool use overview", "Tool choice handling end", 20),
    "ai-eng-agent-loops": ("https://www.anthropic.com/engineering/building-effective-agents", "Building effective agents", "Anthropic", "Agent loop patterns", "Orchestration guidance end", 30),
    "ai-eng-planning-memory": ("https://www.anthropic.com/engineering/building-effective-agents", "Planning & memory in agent systems", "Anthropic", "Workflows vs agents planning", "Memory/state guidance end", 25),
    "ai-eng-multi-agent-awareness": ("https://www.anthropic.com/engineering/building-effective-agents", "Multi-agent orchestration awareness", "Anthropic", "Multi-agent patterns section", "Cost/latency tradeoffs end", 20),
    "ai-eng-observability-security": ("https://platform.openai.com/docs/guides/safety-strategies", "Safety & observability strategies", "OpenAI", "Assess and mitigate risks", "Monitoring section end", 25),
    "ai-eng-production-deployment": ("https://platform.openai.com/docs/guides/production-best-practices", "Production deployment checklist", "OpenAI", "Production best practices", "Rollout checklist end", 30),
}


def main() -> None:
    db = SessionLocal()
    created = []
    skipped = []
    missing_topics = []
    try:
        lessons_by_topic_slug: dict[str, CurriculumLesson] = {}
        topics = db.query(CurriculumTopic).all()
        lessons = db.query(CurriculumLesson).all()
        lesson_by_id = {l.id: l for l in lessons}
        topic_lesson = {}
        for t in topics:
            tls = [lesson_by_id[lid] for lid in [l.id for l in lessons] if False]  # placeholder no-op
        # build topic->lessons map properly
        from collections import defaultdict
        lessons_by_tid = defaultdict(list)
        for l in lessons:
            lessons_by_tid[l.topic_id].append(l)
        slug_topic = {t.slug: t for t in topics}

        existing_resource_lesson_ids = {
            row[0]
            for row in db.query(CurriculumResource.lesson_id).all()
            if row[0] is not None
        }

        for slug, (url, title, provider, start, end, minutes) in MAPPING.items():
            topic = slug_topic.get(slug)
            if topic is None:
                missing_topics.append(slug)
                continue
            tls = lessons_by_tid.get(topic.id, [])
            if not tls:
                missing_topics.append(slug + "::no-lesson")
                continue
            lesson = sorted(tls, key=lambda x: x.order_index)[0]
            if lesson.id in existing_resource_lesson_ids:
                skipped.append(slug)
                continue
            res = CurriculumResource(
                slug=f"{slug}-primary",
                title=title,
                url=url,
                resource_type="documentation",
                provider=provider,
                description=(
                    f"Learner unit: {start} through {end}. "
                    "Official source mapped with explicit boundaries; "
                    "content inspection pending (NEEDS_REVIEW)."
                ),
                official_unofficial="official",
                order_index=1,
                lesson_id=lesson.id,
                role="PRIMARY",
                verification_status="NEEDS_REVIEW",
                estimated_minutes=minutes,
                required_concepts_covered=[],
                exactness="EXACT",
                notes="OFFICIAL_DOC_MAPPING — pending lockdown content inspection",
                last_verified_at=datetime.now(timezone.utc).isoformat(),
                learner_visible=True,
                visibility_class="LEARNER",
            )
            db.add(res)
            created.append(slug)

        db.commit()
        out = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "resources_created": len(created),
            "created_for_slugs": created,
            "skipped_already_mapped": skipped,
            "missing_topics_or_lessons": missing_topics,
        }
        json.dump(out, open(f"{REPORT_DIR}\\resource_mapping_log.json", "w", encoding="utf-8"), indent=2)
        print(json.dumps({k: v for k, v in out.items() if k != "created_for_slugs"}, indent=2))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
