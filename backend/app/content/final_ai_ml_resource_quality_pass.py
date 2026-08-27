"""Apply the explicitly authorized final AI/ML/CV resource-quality pass."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import CurriculumLesson, CurriculumResource, CurriculumTopic


def _m(title, provider, url, boundary="FULL_SINGLE_PAGE", start="FULL_SINGLE_PAGE", end="FULL_SINGLE_PAGE", instruction=None, rtype="documentation", video_id=None, duration=None):
    return locals()


MAPPINGS: dict[str, dict[str, Any]] = {
    "dsa-dp-mindset": _m("MIT OpenCourseWare — Dynamic Programming", "MIT OpenCourseWare", "https://ocw.mit.edu/courses/6-00sc-introduction-to-computer-science-and-programming-spring-2011/resources/lecture-23-dynamic-programming/", "VIDEO_TIMESTAMP", "00:00", "53:41", "Understand dynamic programming through optimal substructure and overlapping subproblems. Connect the exponential recursive solution to the reason storing subproblem results makes the problem tractable. Compare recursion, memoization and tabulation.", "documentation", "", 3221),
    "cv-color-spaces": _m("Changing Colorspaces", "OpenCV", "https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html", instruction="Learn RGB, grayscale, HSV and color-space conversion. Understand why color spaces are representations of the same image and when HSV/grayscale is useful for image processing."),
    "cv-convolution-in-cv": _m("Convolutional layers", "Stanford CS231n", "https://cs231n.github.io/convolutional-networks/", "ARTICLE_SECTION", "The Convolutional Layer", "The Convolutional Layer", "Understand local receptive fields, filters, feature maps, stride, padding, and the output-size calculation for image convolutions."),
    "cv-classic-architectures": _m("Classic Convolutional Neural Network Architectures", "D2L.ai", "https://d2l.ai/chapter_convolutional-modern/lenet.html", "ARTICLE_SECTION", "LeNet", "AlexNet-style architecture discussion", "Study how CNN architecture evolved from simple convolution + pooling stacks to deeper architectures. Focus on why architectural depth and channel count matter."),
    "cv-resnet": _m("Residual Networks (ResNet)", "D2L.ai", "https://d2l.ai/chapter_convolutional-modern/resnet.html", instruction="Understand residual blocks, skip connections, why identity shortcuts help optimization, and how ResNet enables much deeper networks."),
    "cv-efficientnet-awareness": _m("Network Design", "D2L.ai", "https://d2l.ai/chapter_convolutional-modern/resnet.html", "ARTICLE_SECTION", "architecture scaling", "architecture scaling", "Awareness only: understand that modern CNNs systematically trade depth, width and resolution instead of arbitrarily making networks larger."),
    "cv-vision-transformers-awareness": _m("Vision Transformers", "D2L.ai", "https://d2l.ai/chapter_attention-mechanisms-and-transformers/vision-transformer.html", instruction="Understand how an image is divided into patches, converted into token-like representations, processed by self-attention, and reconstructed into a classification representation."),
    "cv-pixels-channels": _m("Image data: NumPy arrays", "scikit-image", "https://scikit-image.org/docs/stable/user_guide/numpy_images.html", instruction="Understand how an image becomes a NumPy array, how height/width/channels map to tensor dimensions, and how RGB values are represented numerically."),
    "cv-end-to-end-project": _m("Transfer Learning for Computer Vision Tutorial", "PyTorch", "https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial", instruction="Follow the complete computer-vision workflow: dataset loading, preprocessing, pretrained CNN, fine-tuning or fixed feature extractor, validation, and inference on custom images."),
    "cv-object-detection-overview": _m("Bounding boxes and object detection", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_computer-vision/bounding-box.md", "ARTICLE_SECTION", "bounding-box definition", "object-detection introduction", "Understand detection as predicting object class plus spatial bounding boxes. Learn the difference between image classification and object detection."),
    "cv-bounding-boxes-iou": _m("Bounding boxes and object detection", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_computer-vision/bounding-box.md", "ARTICLE_SECTION", "bounding boxes", "IoU", "Learn box coordinates, overlap and Intersection over Union. Calculate IoU manually for simple boxes."),
    "cv-nms": _m("Non-Maximum Suppression (NMS)", "Ultralytics", "https://www.ultralytics.com/glossary/non-maximum-suppression-nms", instruction="Understand why detectors produce duplicate boxes and how confidence sorting plus IoU thresholding removes redundant predictions."),
    "cv-yolo-concept": _m("YOLO Explained", "Ultralytics", "https://docs.ultralytics.com/tasks/detect/", "ARTICLE_SECTION", "object-detection", "YOLO detection", "Understand the YOLO family as single-stage object detectors that predict boxes and classes efficiently in one forward pass. Learn the difference between detection architecture and post-processing."),
    "cv-evaluation-metrics-cv": _m("Object Detection Metrics", "Ultralytics", "https://docs.ultralytics.com/guides/yolo-performance-metrics/", instruction="Understand precision, recall, IoU, mAP@50, and mAP@50-95. Be able to explain what each metric says and why one metric alone is insufficient."),
    "dl-forward-propagation": _m("Forward Propagation", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_multilayer-perceptrons/backprop.md", "ARTICLE_SECTION", "Forward Propagation", "Forward Propagation", "Trace x → weighted sum → activation → next layer → output. Be able to compute a tiny two-layer forward pass manually."),
    "dl-backprop-intuition": _m("Backpropagation, Intuitions", "CS231n", "https://cs231n.github.io/optimization-2/", "ARTICLE_SECTION", "Intuitive understanding of backpropagation", "Intuitive understanding of backpropagation", "Understand backpropagation as local gradients flowing backward through a computation graph using the chain rule. Use small add/multiply/max examples."),
    "dl-computational-graphs": _m("Computational graphs and backpropagation", "CS231n", "https://cs231n.github.io/optimization-2/", "ARTICLE_SECTION", "Compound expressions, chain rule, backpropagation", "Patterns in backward flow", "Learn how a computation graph decomposes a complex function into small local operations whose derivatives can be chained."),
    "dl-loss-functions-nn": _m("Multilayer Perceptrons", "D2L.ai", "https://d2l.ai/chapter_multilayer-perceptrons/multilayer-perceptrons.html", "ARTICLE_SECTION", "loss", "loss", "Understand why a neural network needs a loss function, how predictions are compared with targets, and how the loss becomes the quantity optimized by gradient descent."),
    "dl-vanishing-gradients": _m("Numerical Stability and Initialization", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_multilayer-perceptrons/numerical-stability-and-init.md", "ARTICLE_SECTION", "vanishing gradients", "vanishing gradients", "Understand why gradients can become extremely small through repeated multiplication and why this makes deep networks difficult to train."),
    "dl-initialization": _m("Parameter Initialization", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_multilayer-perceptrons/numerical-stability-and-init.md", "ARTICLE_SECTION", "parameter initialization", "parameter initialization", "Understand why initialization matters, why all-zero initialization is bad, and the intuition behind Xavier/Glorot-style initialization."),
    "dl-normalization": _m("Batch Normalization", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_convolutional-modern/batch-norm.md", "ARTICLE_SECTION", "Batch Normalization", "Batch Normalization", "Understand normalization inside neural-network training and why batch normalization changes optimization behavior."),
    "dl-cnn-foundations": _m("From Fully-Connected to Convolutions", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_convolutional-neural-networks/why-conv.md", instruction="Understand why dense layers scale badly for images and how locality and translation structure motivate convolutions."),
    "dl-convolution-op": _m("Convolutional Layer", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_convolutional-neural-networks/conv-layer.md", "ARTICLE_SECTION", "Convolution operation", "Convolution operation", "Focus on the convolution operation, filters, local receptive fields, and feature-map computation."),
    "dl-padding-stride": _m("Convolutional Layer", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_convolutional-neural-networks/conv-layer.md", "ARTICLE_SECTION", "Padding and Stride", "Padding and Stride", "Focus on how padding and stride change convolution output dimensions and receptive-field movement."),
    "dl-pooling": _m("Pooling", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_convolutional-neural-networks/pooling.md", instruction="Complete this page. Focus on pooling windows, downsampling, and how pooling changes spatial dimensions."),
    "dl-feature-maps": _m("LeNet: feature maps and channels", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_convolutional-neural-networks/lenet.md", "ARTICLE_SECTION", "feature maps", "channels in LeNet", "Understand how convolution produces feature maps and how channel depth changes through a CNN."),
    "ml-gradient-boosting": _m("Gradient-boosted trees", "scikit-learn", "https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting", "ARTICLE_SECTION", "Gradient-boosted trees", "Gradient-boosted trees", "Understand boosting as sequentially adding models that correct previous errors, and specifically how gradient-boosted trees differ conceptually from random forests."),
    "ml-roc-auc": _m("What Are ROC Curves and AUC in Classification?", "StatQuest", "https://www.youtube.com/watch?v=4jRBRDbJemM", "VIDEO_TIMESTAMP", "00:00", "", "Understand threshold movement, true-positive rate, false-positive rate, ROC curves and area under the curve. Explain why ROC/AUC is threshold-based.", "youtube_video", "4jRBRDbJemM"),
    "nlp-vocabulary-bow": _m("CountVectorizer and bag-of-words", "scikit-learn", "https://scikit-learn.org/stable/modules/feature_extraction.html", "ARTICLE_SECTION", "CountVectorizer", "bag-of-words", "Understand vocabulary creation, document-term matrices, token counts and sparse representations."),
    "nlp-tf-idf": _m("TF-IDF", "scikit-learn", "https://scikit-learn.org/stable/modules/feature_extraction.html", "ARTICLE_SECTION", "TF-IDF", "TF-IDF", "Understand why common words receive lower weight and rare informative words receive higher weight."),
    "nlp-generative-models": _m("Causal language modeling", "Hugging Face", "https://huggingface.co/learn/llm-course/chapter7/1", "ARTICLE_SECTION", "Causal language modeling", "generative-model", "Understand autoregressive generation, next-token prediction and why causal language models can generate text one token at a time."),
    "nlp-evaluation-nlp": _m("Evaluate", "Hugging Face", "https://huggingface.co/docs/evaluate/index", instruction="Understand evaluation as matching metrics to the NLP task, dataset and failure mode. Distinguish classification accuracy/F1 from sequence-generation metrics."),
    "genai-what-is-lm": _m("Introduction to NLP and Language Models", "Hugging Face", "https://huggingface.co/learn/llm-course/chapter1/1", "ARTICLE_SECTION", "Introduction", "NLP/LLM basics", "Understand what a language model is, what it predicts, how LLMs differ from traditional NLP pipelines, and the limits of the term LLM."),
    "genai-next-token-prediction": _m("Language Modeling", "D2L.ai", "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_recurrent-neural-networks/language-model.md", "ARTICLE_SECTION", "Pretraining objective", "next-token prediction", "Understand the training objective mathematically: given previous tokens, predict the next token and optimize the probability assigned to the correct token."),
    "genai-embeddings": _m("Embeddings", "OpenAI", "https://developers.openai.com/api/docs/guides/embeddings", "ARTICLE_SECTION", "Embedding generation", "semantic similarity", "Understand what an embedding vector represents, why semantically similar inputs map near one another, and how embeddings support retrieval/search."),
    "genai-pretraining-finetuning": _m("Introduction to fine-tuning", "Hugging Face LLM Course", "https://huggingface.co/learn/llm-course/chapter3/1", "ARTICLE_SECTION", "Introduction", "fine-tuning", "Understand the difference between pretraining and fine-tuning, what changes during fine-tuning, and why pretrained models are adapted instead of retrained from zero for most applications."),
    "genai-instruction-tuning-rlhf": _m("Instruction tuning and alignment", "Hugging Face LLM Course", "https://huggingface.co/learn/llm-course/chapter11/1", "ARTICLE_SECTION", "Supervised Fine-Tuning", "Evaluation", "Understand instruction tuning, SFT, parameter-efficient fine-tuning and preference/alignment concepts. Distinguish SFT from RLHF rather than treating them as the same operation."),
    "genai-lora-peft": _m("PEFT and LoRA", "Hugging Face", "https://huggingface.co/docs/peft/en/index", "ARTICLE_SECTION", "LoRA", "parameter-efficient fine-tuning", "Understand why LoRA reduces the number of trainable parameters and how low-rank updates are applied around a frozen pretrained model."),
    "genai-context-windows": _m("Context Windows", "Anthropic", "https://platform.claude.com/docs/en/build-with-claude/context-windows", "ARTICLE_SECTION", "context-window explanation", "context-window explanation", "Understand tokens, context limits, input/output token budgets, and why longer context does not automatically imply better reasoning."),
    "genai-production-serving": _m("vLLM", "vLLM", "https://docs.vllm.ai/en/latest/", "ARTICLE_SECTION", "introduction", "serving architecture", "Understand model serving, batching, KV-cache implications and why optimized inference engines exist."),
    "ai-eng-agent-loops": _m("Building effective agents", "Anthropic", "https://www.anthropic.com/engineering/building-effective-agents", "ARTICLE_SECTION", "agent definition", "workflow loop", "Understand the basic agent loop: observe/input → reason/plan → tool/action → observe result → continue/finish."),
    "ai-eng-planning-memory": _m("Building effective agents", "Anthropic", "https://www.anthropic.com/engineering/building-effective-agents", "ARTICLE_SECTION", "planning", "memory", "Understand why agents need state, memory and planning, and distinguish short-term context from persistent memory."),
    "ai-eng-multi-agent-awareness": _m("Building effective agents", "Anthropic", "https://www.anthropic.com/engineering/building-effective-agents", "ARTICLE_SECTION", "multi-agent orchestration", "multi-agent orchestration", "Understand why multiple agents might be used, their coordination costs, and why multi-agent systems should not be introduced when one agent is enough."),
    "ai-eng-tool-calling": _m("Function calling", "OpenAI", "https://developers.openai.com/api/docs/guides/function-calling", "ARTICLE_SECTION", "tool/function-calling mechanics", "tool/function-calling mechanics", "Understand structured tool schemas, model-generated arguments, tool execution, and returning tool results back into the model loop."),
    "mlops-experiment-lifecycle": _m("MLflow Tracking", "MLflow", "https://raw.githubusercontent.com/mlflow/mlflow/master/docs/docs/classic-ml/tracking/index.mdx", "ARTICLE_SECTION", "experiment", "metric tracking", "Understand experiments, runs, parameters, metrics and artifacts and why tracking is needed for reproducibility."),
    "mlops-drift-quality": _m("MLflow Model Evaluation", "MLflow", "https://raw.githubusercontent.com/mlflow/mlflow/master/docs/docs/classic-ml/evaluation/index.mdx", "ARTICLE_SECTION", "evaluation", "evaluation", "Study the evaluation concepts in the PRIMARY, then complete the supplement covering training-serving skew, data quality and monitoring gates."),
    "math-chain-rule": _m("The Chain Rule", "OpenStax", "https://openstax.org/books/calculus-volume-3/pages/4-5-the-chain-rule", instruction="Understand the one-variable and multivariable chain rule. Connect it directly to computational graphs and backpropagation."),
    "math-partial-derivatives": _m("Partial Derivatives", "OpenStax", "https://openstax.org/books/calculus-volume-3/pages/4-3-partial-derivatives", instruction="Learn partial derivatives by holding other variables constant and connect them to gradients used in ML."),
    "math-gradient-intuition": _m("Directional Derivatives and the Gradient", "OpenStax", "https://openstax.org/books/calculus-volume-3/pages/4-6-directional-derivatives-and-the-gradient", instruction="Understand the gradient as a vector of partial derivatives and why it points toward greatest local increase. Connect this to gradient descent."),
}

UNRESOLVED = {
    "ml-classification": "NEEDS_BOUNDARY_VERIFICATION: requested StatQuest video has no verified full duration in existing repository data.",
    "ml-decision-trees": "NEEDS_BOUNDARY_VERIFICATION: requested StatQuest video has no verified full duration in existing repository data.",
    "ml-ensemble-learning": "NEEDS_RESEARCH_CANDIDATE: exact StatQuest video is not present in existing repository candidates.",
    "genai-vector-databases": "NEEDS_RESEARCH_CANDIDATE: no dedicated existing canonical vector-database educational candidate is present.",
    "math-conditional-probability": "NEEDS_RESEARCH_CANDIDATE: no verified static probability candidate is present.",
    "math-expectation-variance": "NEEDS_RESEARCH_CANDIDATE: no verified static probability/statistics candidate is present.",
}


def _resolve(db: Session, slug: str) -> tuple[CurriculumTopic, CurriculumResource]:
    topic = db.query(CurriculumTopic).filter(CurriculumTopic.slug == slug).first()
    if not topic:
        raise ValueError(f"Missing topic: {slug}")
    lesson = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).first()
    row = db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id, CurriculumResource.role == "PRIMARY", CurriculumResource.learner_visible.is_(True)).first() if lesson else None
    if not row:
        raise ValueError(f"Missing learner-visible PRIMARY: {slug}")
    return topic, row


def _derived_instruction(row: CurriculumResource, topic: CurriculumTopic) -> str:
    boundary = row.section or row.start_boundary or "this page"
    if row.boundary_type == "VIDEO_TIMESTAMP":
        start, end = row.start_boundary or row.start_timestamp or "the beginning", row.end_boundary or row.end_timestamp or "the end"
        return f"Watch {start}–{end}. Focus on {topic.name}. After watching, explain the main idea in your own words."
    if row.boundary_type in {"ARTICLE_SECTION", "SECTION"}:
        return f"Read {boundary}. Focus on {topic.name}. After reading, explain the main idea in your own words."
    return f"Complete this page. Focus on {topic.name}. Be able to explain the main idea in your own words."


def apply_final_pass(db: Session, *, commit: bool = True) -> dict[str, Any]:
    changed, instructions_added = [], []
    inspected = set(MAPPINGS) | set(UNRESOLVED) | {"cf-build-system", "se-versioning"}
    for slug, spec in MAPPINGS.items():
        topic, row = _resolve(db, slug)
        old = {"title": row.title, "url": row.url, "provider": row.provider, "role": row.role}
        row.title, row.provider, row.url, row.resource_type = spec["title"], spec["provider"], spec["url"], spec["rtype"]
        row.boundary_type, row.start_boundary, row.end_boundary = spec["boundary"], spec["start"], spec["end"]
        row.section = spec["start"] if spec["start"] == spec["end"] else f"{spec['start']} through {spec['end']}"
        row.description = spec["instruction"]
        row.video_id, row.duration = spec.get("video_id"), spec.get("duration")
        row.exactness, row.verification_status = "EXACT", "NEEDS_REVIEW"
        changed.append({"topic": topic.slug, "old": old, "new": {"title": row.title, "url": row.url, "boundary": row.section}})
    skew = db.query(CurriculumResource).filter(CurriculumResource.slug == "mlops-drift-quality-skew-supplement").first()
    if skew:
        skew.role, skew.learner_visible, skew.visibility_class = "SUPPLEMENT", True, "LEARNER"
    for topic in db.query(CurriculumTopic).all():
        lesson = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == topic.id).first()
        if not lesson: continue
        row = db.query(CurriculumResource).filter(CurriculumResource.lesson_id == lesson.id, CurriculumResource.role == "PRIMARY", CurriculumResource.learner_visible.is_(True)).first()
        if row and not row.description:
            row.description = _derived_instruction(row, topic)
            instructions_added.append(topic.slug)
    if commit: db.commit()
    return {"topics_inspected": len(inspected), "topics_changed": len(changed), "changed": changed, "instructions_added": instructions_added, "unresolved": UNRESOLVED, "resources_created": 0, "resources_demoted": 0, "resources_preserved": len(changed)}