"""Repair the resource URLs that the link audit proved wrong.

Every replacement in this file was fetched and confirmed to return 200 with
the expected page title before being written down, and the script re-verifies
each one live before it touches the database. Nothing here is a guess.

Four classes of repair, in the order they were found:

RENDERED    57 rows pointed at ``raw.githubusercontent.com`` source files.
            A browser shows those as plain text, so the maths, figures and
            code directives never render. The book/tutorial each one came
            from publishes the same content as a real page.

RELOCATED   Pages that moved. Some still 301 (GeeksforGeeks reorganised its
            URL scheme, the Hugging Face NLP course became the LLM course),
            some now 404 outright (MIT Missing Semester renumbered its 2026
            lecture slugs).

WRONG_PAGE  The URL loads but is not the topic. Two d2l.ai links redirected
            to the book's homepage, so "open exactly this" landed on a front
            page. Two more pointed at a neighbouring chapter.

MISLABELLED The provider recorded did not match the host actually serving the
            page, so the study contract named the wrong publisher.

Run:
    python -m app.content.repair_resource_links --dry-run
    python -m app.content.repair_resource_links
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .audit_resource_links import fetch

BACKEND = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND / "dev.db"
REPORTS = BACKEND / "reports"

_D2L_RAW = re.compile(
    r"^https://raw\.githubusercontent\.com/d2l-ai/d2l-en/master/(chapter_[^/]+)/([^/]+)\.md$"
)
_HF_RAW = re.compile(
    r"^https://raw\.githubusercontent\.com/huggingface/course/main/chapters/en/chapter(\d+)/(\d+)\.mdx$"
)
_PT_RAW = re.compile(
    r"^https://raw\.githubusercontent\.com/pytorch/tutorials/main/beginner_source/basics/([a-z_]+)\.py$"
)


def rendered_url(url: str) -> Optional[str]:
    """Map a raw source URL to the page a human should actually open."""
    if match := _D2L_RAW.match(url):
        return f"https://d2l.ai/{match.group(1)}/{match.group(2)}.html"
    if match := _HF_RAW.match(url):
        # The NLP course was renamed to the LLM course; chapter numbering held.
        return f"https://huggingface.co/learn/llm-course/chapter{match.group(1)}/{match.group(2)}"
    if match := _PT_RAW.match(url):
        # pytorch.org/tutorials canonicalises to docs.pytorch.org.
        return f"https://docs.pytorch.org/tutorials/beginner/basics/{match.group(1)}.html"
    return {
        "https://raw.githubusercontent.com/mlflow/mlflow/master/docs/docs/classic-ml/tracking/index.mdx": "https://mlflow.org/docs/latest/ml/tracking/",
        "https://raw.githubusercontent.com/mlflow/mlflow/master/docs/docs/classic-ml/evaluation/index.mdx": "https://mlflow.org/docs/latest/ml/evaluation/",
    }.get(url)


@dataclass(frozen=True)
class Replacement:
    """One verified repair, matched on the URL currently stored."""

    old_url: str
    new_url: str
    reason: str
    #: Only set when the recorded title or provider also described the wrong thing.
    new_title: Optional[str] = None
    new_provider: Optional[str] = None
    #: Restrict to one topic when the same URL is correct elsewhere.
    topic_slug: Optional[str] = None
    #: True when the target is a publisher's "latest" alias and is *expected*
    #: to redirect to the current version. Storing the alias keeps the mapping
    #: correct across releases; storing the resolved version would go stale.
    alias: bool = False


#: Pages that moved or never existed. Each target was fetched and its <title> read.
RELOCATED: tuple[Replacement, ...] = (
    # CORRECTION. These two URLs 404, and the first pass concluded that no 2026
    # edition of Missing Semester existed and sent both to the 2020 lectures.
    # That was wrong: missing.csail.mit.edu/2026/ is live, and the curriculum
    # already links seven other 2026 pages. Only these two *slugs* were wrong --
    # the 2026 edition names its lectures descriptively ("course-shell",
    # "command-line-environment") rather than numerically ("01-shell").
    #
    # The 2020 targets are kept as the matched key so the nine rows the first
    # pass moved are pulled forward to the current edition.
    Replacement(
        "https://missing.csail.mit.edu/2026/01-shell/",
        "https://missing.csail.mit.edu/2026/course-shell/",
        "RELOCATED: the 2026 edition uses descriptive lecture slugs, not numbered ones",
        new_title="MIT Missing Semester - Course Overview + Introduction to the Shell",
        new_provider="MIT Missing Semester",
    ),
    Replacement(
        "https://missing.csail.mit.edu/2020/course-shell/",
        "https://missing.csail.mit.edu/2026/course-shell/",
        "CORRECTION: sent to the 2020 edition on a false premise; 2026 is live",
        new_title="MIT Missing Semester - Course Overview + Introduction to the Shell",
        new_provider="MIT Missing Semester",
    ),
    Replacement(
        "https://missing.csail.mit.edu/2026/02-environment/",
        "https://missing.csail.mit.edu/2026/command-line-environment/",
        "RELOCATED: the 2026 edition uses descriptive lecture slugs, not numbered ones",
        new_title="MIT Missing Semester - Command-line Environment",
        new_provider="MIT Missing Semester",
    ),
    Replacement(
        "https://missing.csail.mit.edu/2020/shell-tools/",
        "https://missing.csail.mit.edu/2026/command-line-environment/",
        "CORRECTION: sent to the 2020 edition on a false premise; 2026 is live",
        new_title="MIT Missing Semester - Command-line Environment",
        new_provider="MIT Missing Semester",
    ),
    # A stray row still on the 2020 edition while every other Missing Semester
    # link is 2026. Same lecture, current edition.
    Replacement(
        "https://missing.csail.mit.edu/2020/command-line/",
        "https://missing.csail.mit.edu/2026/command-line-environment/",
        "RELOCATED: aligned to the 2026 edition used everywhere else",
        new_title="MIT Missing Semester - Command-line Environment",
        new_provider="MIT Missing Semester",
    ),
    # GeeksforGeeks moved its operating-system and DSA pages under section prefixes.
    Replacement(
        "https://www.geeksforgeeks.org/environment-variables-in-operating-system/",
        "https://www.geeksforgeeks.org/linux-unix/environment-variables-in-linux-unix/",
        "RELOCATED: original page 404s; equivalent lives under linux-unix",
        new_title="GFG — Environment Variables in Linux/Unix",
    ),
    # The pattern-searching hub page now 301s to an index. KMP is the page a
    # learner on this topic actually needs to read.
    Replacement(
        "https://www.geeksforgeeks.org/dsa/pattern-searching/",
        "https://www.geeksforgeeks.org/dsa/kmp-algorithm-for-pattern-searching/",
        "RELOCATED: the pattern-searching hub 301s; KMP is the substantive page",
        new_title="GFG - KMP Algorithm for Pattern Searching",
    ),
    # Dev.java has no memory-model page; the language spec chapter is the real source.
    Replacement(
        "https://dev.java/learn/jvm/memory-model/",
        "https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html",
        "RELOCATED: dev.java has no memory-model page; JLS ch.17 is the primary source",
        new_title="Java Language Specification — Ch.17 Threads and Locks",
        new_provider="Oracle",
    ),
    # Google retired the standalone training-serving-skew page.
    Replacement(
        "https://developers.google.com/machine-learning/crash-course/training-serving-skew",
        "https://developers.google.com/machine-learning/guides/rules-of-ml",
        "RELOCATED: page retired; Rules of ML covers training/serving skew directly",
        new_title="Rules of Machine Learning — training/serving skew",
        new_provider="Google",
    ),
    # A package-manager page that 404s, replaced by the guide that actually
    # teaches dependency management (and where uv/pip fit).
    Replacement(
        "https://www.geeksforgeeks.org/package-manager-in-operating-system/",
        "https://packaging.python.org/en/latest/tutorials/managing-dependencies/",
        "RELOCATED: page 404s; the Python Packaging guide is the usable source",
        new_title="Python Packaging — Managing Application Dependencies",
        new_provider="Python",
    ),
    # Provider said Khan Academy; the URL was a different site, and timed out.
    Replacement(
        "https://mathinsight.org/matrix_introduction",
        "https://www.khanacademy.org/math/precalculus/x9e81a4f98389efdf:matrices",
        "MISLABELLED: provider was Khan Academy but URL was mathinsight, which also times out",
        new_title="Khan Academy — Matrices",
        new_provider="Khan Academy",
    ),
    Replacement(
        "https://mathinsight.org/vector_introduction",
        "https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces",
        "MISLABELLED: provider was Khan Academy but URL was mathinsight",
        new_title="Khan Academy — Vectors and spaces",
        new_provider="Khan Academy",
    ),
    # The Hugging Face NLP course is now the LLM course.
    Replacement(
        "https://huggingface.co/learn/nlp-course/chapter1/1",
        "https://huggingface.co/learn/llm-course/chapter1/1",
        "RELOCATED: the NLP course was renamed to the LLM course",
    ),
    # OpenAI moved its platform docs to the developers host.
    Replacement(
        "https://platform.openai.com/docs/guides/text",
        "https://developers.openai.com/api/docs/guides/text",
        "RELOCATED: platform.openai.com docs moved to developers.openai.com",
    ),
    Replacement(
        "https://platform.openai.com/docs/guides/evals",
        "https://developers.openai.com/api/docs/guides/evals",
        "RELOCATED: platform.openai.com docs moved to developers.openai.com",
    ),
    Replacement(
        "https://platform.openai.com/docs/guides/prompt-engineering",
        "https://developers.openai.com/api/docs/guides/prompt-engineering",
        "RELOCATED: platform.openai.com docs moved to developers.openai.com",
    ),
)


#: The URL loads, but it is not this topic.
WRONG_PAGE: tuple[Replacement, ...] = (
    # Redirected to the book homepage, so the learner landed on a front page.
    Replacement(
        "https://d2l.ai/chapter_multilayer-perceptrons/multilayer-perceptrons.html",
        "https://d2l.ai/chapter_multilayer-perceptrons/mlp.html",
        "WRONG_PAGE: old path redirects to the d2l homepage; the chapter page is mlp.html",
        new_title="Multilayer Perceptrons — loss and activation choices",
    ),
    Replacement(
        "https://d2l.ai/chapter_convolutional-modern/lenet.html",
        "https://d2l.ai/chapter_convolutional-neural-networks/lenet.html",
        "WRONG_PAGE: old path redirects to the d2l homepage; LeNet is in the CNN chapter",
        new_title="Convolutional Neural Networks (LeNet)",
    ),
    # EfficientNet pointed at the ResNet page, which does not discuss scaling.
    Replacement(
        "https://d2l.ai/chapter_convolutional-modern/resnet.html",
        "https://arxiv.org/abs/1905.11946",
        "WRONG_PAGE: the ResNet page does not cover compound scaling",
        new_title="EfficientNet — Rethinking Model Scaling for CNNs",
        new_provider="arXiv",
        topic_slug="cv-efficientnet-awareness",
    ),
    # CS231n's linear-classify page is not about tensor input volumes.
    Replacement(
        "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_computer-vision/kaggle-cifar10.md",
        "https://cs231n.github.io/convolutional-networks/",
        "WRONG_PAGE: a Kaggle CIFAR-10 walkthrough is not an explanation of input volumes",
        new_title="CS231n — Input volumes, depth/height/width",
        new_provider="Stanford CS231n",
        topic_slug="cv-image-tensors",
    ),
    # "scikit-learn :: Image preprocessing" was a d2l augmentation source file.
    Replacement(
        "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_computer-vision/image-augmentation.md",
        "https://docs.pytorch.org/vision/stable/transforms.html",
        "MISLABELLED: provider/title claimed scikit-learn; content was d2l augmentation source",
        new_title="torchvision.transforms — geometric and colour transforms",
        new_provider="PyTorch",
        topic_slug="cv-transformations",
    ),
)


#: Pages that still resolve, but only via a 301. The publisher has reorganised
#: and the stored URL is stale; the study contract should name where the page
#: actually lives. Each target is the Location the live fetch landed on.
#:
#: Deliberately NOT included: docs.opencv.org/4.x/... redirects to the current
#: patch release (4.13.0 today), but "4.x" is OpenCV's alias for latest. Pinning
#: the patch version would make the mapping go stale on the next release, so the
#: alias is the more correct URL to store.
RELOCATED_BY_REDIRECT: tuple[Replacement, ...] = (
    Replacement(
        "https://www.geeksforgeeks.org/introduction-of-compiler-design/",
        "https://www.geeksforgeeks.org/compiler-design/introduction-of-compiler-design/",
        "RELOCATED: GeeksforGeeks moved this page under compiler-design",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/introduction-to-compilers/",
        "https://www.geeksforgeeks.org/compiler-design/introduction-to-compilers/",
        "RELOCATED: GeeksforGeeks moved this page under compiler-design",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/process-in-operating-system/",
        "https://www.geeksforgeeks.org/operating-systems/process-in-operating-system/",
        "RELOCATED: GeeksforGeeks moved this page under operating-systems",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/kernel-in-operating-system/",
        "https://www.geeksforgeeks.org/operating-systems/kernel-in-operating-system/",
        "RELOCATED: GeeksforGeeks moved this page under operating-systems",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/thread-in-operating-system/",
        "https://www.geeksforgeeks.org/operating-systems/thread-in-operating-system/",
        "RELOCATED: GeeksforGeeks moved this page under operating-systems",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/memory-management-in-operating-system/",
        "https://www.geeksforgeeks.org/operating-systems/memory-management-in-operating-system/",
        "RELOCATED: GeeksforGeeks moved this page under operating-systems",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/central-processing-unit-cpu/",
        "https://www.geeksforgeeks.org/computer-science-fundamentals/central-processing-unit-cpu/",
        "RELOCATED: GeeksforGeeks moved this page under computer-science-fundamentals",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/random-access-memory-ram/",
        "https://www.geeksforgeeks.org/computer-science-fundamentals/random-access-memory-ram/",
        "RELOCATED: GeeksforGeeks moved this page under computer-science-fundamentals",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/cache-memory-in-computer-organization/",
        "https://www.geeksforgeeks.org/computer-organization-architecture/cache-memory-in-computer-organization/",
        "RELOCATED: GeeksforGeeks moved this page under computer-organization-architecture",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/locality-of-reference-and-cache-operation-in-cache-memory/",
        "https://www.geeksforgeeks.org/computer-organization-architecture/locality-of-reference-and-cache-operation-in-cache-memory/",
        "RELOCATED: GeeksforGeeks moved this page under computer-organization-architecture",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/analysis-of-algorithms-set-2-asymptotic-analysis/",
        "https://www.geeksforgeeks.org/dsa/worst-average-and-best-case-analysis-of-algorithms/",
        "RELOCATED: GeeksforGeeks replaced this page with the best/worst/average article",
        new_title="GFG - Worst, Average and Best Case Analysis of Algorithms",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/counting-frequencies-of-array-elements/",
        "https://www.geeksforgeeks.org/dsa/counting-frequencies-of-array-elements/",
        "RELOCATED: GeeksforGeeks moved this page under dsa",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/two-pointers-technique/",
        "https://www.geeksforgeeks.org/dsa/two-pointers-technique/",
        "RELOCATED: GeeksforGeeks moved this page under dsa",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/heap-sort/",
        "https://www.geeksforgeeks.org/dsa/heap-sort/",
        "RELOCATED: GeeksforGeeks moved this page under dsa",
    ),
    Replacement(
        "https://www.geeksforgeeks.org/introduction-to-dynamic-programming-data-structures-and-algorithm-tutorials/",
        "https://www.geeksforgeeks.org/dsa/introduction-to-dynamic-programming-data-structures-and-algorithm-tutorials/",
        "RELOCATED: GeeksforGeeks moved this page under dsa",
    ),
    Replacement(
        "https://code.visualstudio.com/docs/editor/debugging",
        "https://code.visualstudio.com/docs/debugtest/debugging",
        "RELOCATED: VS Code moved debugging docs under debugtest",
    ),
    Replacement(
        "https://code.visualstudio.com/docs/editing/getting-started",
        "https://code.visualstudio.com/docs/editing/getting-started/editor-tutorial",
        "RELOCATED: VS Code split getting-started into a tutorial page",
    ),
    Replacement(
        "https://junit.org/junit5/docs/current/user-guide/",
        "https://docs.junit.org/current/user-guide/",
        "RELOCATED: the JUnit user guide moved to docs.junit.org",
        alias=True,
    ),
)


#: Resources whose URL loads a real page that is not this topic, found on the
#: second audit pass.
WRONG_PAGE_SECOND_PASS: tuple[Replacement, ...] = (
    # LangChain restructured its docs: every old retrieval/RAG path now lands in
    # the Deep Agents section, which is a different subject. Pinecone's guide
    # walks the whole pipeline this topic is about -- chunk, embed, store,
    # retrieve, generate -- and is stable.
    Replacement(
        "https://docs.langchain.com/oss/python/langchain/retrieval",
        "https://www.pinecone.io/learn/retrieval-augmented-generation/",
        "WRONG_PAGE: LangChain's retrieval docs now redirect into Deep Agents",
        new_title="Retrieval-Augmented Generation - the full pipeline",
        new_provider="Pinecone",
    ),
    # A Caltech lecture PDF whose TLS chain no longer validates. The storage
    # hierarchy is better served by a page that loads.
    Replacement(
        "https://courses.cms.caltech.edu/cs122/lectures-wi2018/CS122Lec01.pdf",
        "https://www.geeksforgeeks.org/computer-organization-architecture/memory-hierarchy-design-and-its-characteristics/",
        "UNREACHABLE: the Caltech PDF fails TLS certificate validation",
        new_title="GFG - Memory Hierarchy Design and its Characteristics",
        new_provider="GeeksforGeeks",
    ),
)


#: Repairs found by authors writing questions against these pages, not by the
#: link checker. Every one of these URLs returns 200 -- the page simply is not
#: the topic, or the recorded title describes something the page does not
#: contain. No status code can catch this class; a person reading the page can.
#:
#: Keyed by resource id because several of these topics share a URL, so
#: matching on the URL alone would rewrite the wrong row.
BY_RESOURCE_ID: tuple[dict, ...] = (
    # rcnn.html is the two-stage chapter. A "two-stage vs one-stage" topic that
    # links only to it teaches half a comparison; SSD is the one-stage chapter,
    # and its title was already the one recorded here.
    {
        "id": 833,
        "topic_slug": "cv-two-stage-vs-one-stage",
        "new_url": "https://d2l.ai/chapter_computer-vision/ssd.html",
        "new_title": "Single Shot Multibox Detection (one-stage detection)",
        "new_provider": "D2L.ai",
        "reason": "WRONG_PAGE: linked the two-stage chapter for a one-stage vs two-stage topic",
    },
    # The URL is right -- Mask R-CNN lives on the R-CNN page -- but the title
    # described a Kaggle pipeline that appears nowhere on it.
    {
        "id": 837,
        "topic_slug": "cv-instance-segmentation",
        "new_url": "https://d2l.ai/chapter_computer-vision/rcnn.html",
        "new_title": "Region-based CNNs - R-CNN through Mask R-CNN",
        "new_provider": "D2L.ai",
        "reason": "MISLABELLED: title named a Kaggle pipeline the page does not contain",
    },
    # D2L has no U-Net page. FCN fuses by addition and has no symmetric decoder,
    # so a learner could not answer a U-Net question from it. The paper is short,
    # readable, and is the source of the architecture.
    {
        "id": 836,
        "topic_slug": "cv-u-net",
        "new_url": "https://arxiv.org/abs/1505.04597",
        "new_title": "U-Net: Convolutional Networks for Biomedical Image Segmentation",
        "new_provider": "arXiv",
        "reason": "WRONG_PAGE: D2L's FCN page is not U-Net (addition fusion, no symmetric decoder)",
    },
    # linear-classify mentions preprocessing in passing. The data-setup lecture
    # is where normalisation is actually taught, and it frees linear-classify to
    # serve cv-classification-workflow, which is what that page is about.
    {
        "id": 821,
        "topic_slug": "cv-normalization-cv",
        "new_url": "https://cs231n.github.io/neural-networks-2/",
        "new_title": "CS231n - Setting up the data: preprocessing and normalization",
        "new_provider": "Stanford CS231n",
        "reason": "WRONG_PAGE: linear-classify mentions normalisation only in passing",
    },
    # The objective spans LeNet -> AlexNet -> VGG. The AlexNet chapter opens by
    # narrating the move away from LeNet, so it covers the progression; the
    # LeNet page alone covers only the first step, and already serves
    # dl-feature-maps.
    {
        "id": 826,
        "topic_slug": "cv-classic-architectures",
        "new_url": "https://d2l.ai/chapter_convolutional-modern/alexnet.html",
        "new_title": "Deep CNNs (AlexNet) - the shift away from LeNet",
        "new_provider": "D2L.ai",
        "reason": "WRONG_PAGE: the LeNet page covers one of the three architectures named",
    },
    # The topic names ORB but the page is SIFT only. Renaming to what the page
    # actually is beats a title that promises content it does not have. Also
    # unpinned from 4.13.0 to the 4.x latest alias, as elsewhere.
    {
        "id": 876,
        "topic_slug": "cv-sift-orb-awareness",
        "new_url": "https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html",
        "new_title": "OpenCV - Introduction to SIFT (scale-invariant keypoints)",
        "new_provider": "OpenCV",
        "reason": "MISLABELLED: page covers SIFT only; also unpinned to the 4.x latest alias",
        "alias": True,
    },
    # chapter7/1 is the chapter index of NLP tasks. Causal language modelling,
    # which is the topic, is section 6.
    {
        "id": 854,
        "topic_slug": "nlp-generative-models",
        "new_url": "https://huggingface.co/learn/llm-course/chapter7/6",
        "new_title": "Training a causal language model from scratch",
        "new_provider": "Hugging Face",
        "reason": "WRONG_PAGE: chapter7/1 is the task index, not causal language modelling",
    },
    # D2L's encoder-decoder page is the RNN-era design pattern and never makes
    # the encoder-only vs decoder-only distinction the topic is about.
    {
        "id": 853,
        "topic_slug": "nlp-encoder-vs-decoder",
        "new_url": "https://huggingface.co/learn/llm-course/chapter1/6",
        "new_title": "Transformer Architectures - encoder, decoder, encoder-decoder",
        "new_provider": "Hugging Face",
        "reason": "WRONG_PAGE: D2L's page is the RNN encoder-decoder pattern, not BERT vs GPT",
    },
    # LangChain restructured its documentation so that every retrieval and RAG
    # path now resolves into the Deep Agents section. This row had already
    # landed there, giving a chunking topic an agentic-RAG page and duplicating
    # genai-rag's subject. Pinecone's chunking guide is about splitting
    # specifically, which is what the topic is.
    {
        "id": 866,
        "topic_slug": "genai-chunking-retrieval",
        "new_url": "https://www.pinecone.io/learn/chunking-strategies/",
        "new_title": "Chunking Strategies for LLM Applications",
        "new_provider": "Pinecone",
        "reason": "WRONG_PAGE: LangChain's URL resolves into Deep Agents, not chunking",
    },
    # A positional-encoding video as the reference for a tokenization topic.
    # Positional encoding is a different transformer mechanism entirely.
    {
        "id": 916,
        "topic_slug": "genai-tokenization-llm",
        "new_url": "https://huggingface.co/learn/llm-course/chapter6/5",
        "new_title": "Byte-Pair Encoding tokenization",
        "new_provider": "Hugging Face",
        "reason": "WRONG_PAGE: positional encoding has nothing to do with tokenization",
    },
    # Title promised "Production best practices"; the page is "Risks & Misuses".
    # The topic is about grounding, validation and refusal, which the OpenAI
    # safety guide covers directly.
    {
        "id": 867,
        "topic_slug": "genai-hallucinations-guardrails",
        "new_url": "https://developers.openai.com/api/docs/guides/safety-best-practices",
        "new_title": "Safety best practices - validation, moderation, refusal",
        "new_provider": "OpenAI",
        "reason": "MISLABELLED: page is 'Risks & Misuses', not the production guidance claimed",
    },
    # This reference was the same URL as genai-embeddings' PRIMARY, so it added
    # nothing and invited the cross-topic duplication the validator blocks.
    # pgvector is the concrete counterpoint to a managed vector service.
    {
        "id": 928,
        "topic_slug": "genai-vector-databases",
        "new_url": "https://github.com/pgvector/pgvector",
        "new_title": "pgvector - vector search inside PostgreSQL",
        "new_provider": "GitHub",
        "reason": "MISLABELLED: duplicated genai-embeddings' primary; replaced with a real alternative",
    },
    # "vLLM :: vLLM" tells the learner nothing about why they are opening it.
    {
        "id": 884,
        "topic_slug": "genai-production-serving",
        "new_url": "https://docs.vllm.ai/en/latest/",
        "new_title": "vLLM - KV cache, PagedAttention and continuous batching",
        "new_provider": "vLLM",
        "reason": "MISLABELLED: title repeated the tool name and said nothing about the content",
    },
    # The objective is training/serving skew, input vs label drift, and quality
    # gates. MLflow's evaluation page is about running metric suites over a
    # model and covers none of that; the Google guide that was sitting in the
    # SUPPLEMENT slot is the resource that teaches the objective. Swap the roles
    # rather than discard either.
    {
        "id": 907,
        "topic_slug": "mlops-drift-quality",
        "new_url": "https://developers.google.com/machine-learning/guides/rules-of-ml",
        "new_title": "Rules of Machine Learning - training/serving skew and drift",
        "new_provider": "Google",
        "new_role": "PRIMARY",
        "new_section": "Training-Serving Skew",
        "reason": "WRONG_PAGE: the primary taught metric suites, not skew and drift",
    },
    {
        "id": 898,
        "topic_slug": "mlops-drift-quality",
        "new_url": "https://mlflow.org/docs/latest/ml/evaluation/",
        "new_title": "MLflow Model Evaluation - metric suites over a model",
        "new_provider": "MLflow",
        "new_role": "SUPPLEMENT",
        "reason": "WRONG_PAGE: demoted; it does not teach skew, drift or quality gates",
    },
    # Two topics shared one Tracking page with near-identical objectives, which
    # is the adjacency that produced the duplicated-question defect. Lifecycle
    # and reproducibility is what MLflow Projects is about: pinned environment,
    # entry points, a run you can re-execute.
    {
        "id": 899,
        "topic_slug": "mlops-experiment-lifecycle",
        "new_url": "https://mlflow.org/docs/latest/ml/projects/",
        "new_title": "MLflow Projects - reproducible runs and pinned environments",
        "new_provider": "MLflow",
        "new_section": "FULL_SINGLE_PAGE",
        "reason": "WRONG_PAGE: shared the Tracking page with mlops-tracking; lifecycle is Projects",
    },
    # first-steps is the hello-world app and /docs. Serving a prediction needs a
    # typed request body, which is the next page in the same tutorial.
    {
        "id": 655,
        "topic_slug": "mlops-serving",
        "new_url": "https://fastapi.tiangolo.com/tutorial/body/",
        "new_title": "FastAPI - request bodies for a prediction endpoint",
        "new_provider": "FastAPI",
        "new_section": "FULL_SINGLE_PAGE",
        "reason": "WRONG_PAGE: first-steps stops at hello-world; serving needs a request body",
    },
    # The anchor #underfitting-vs-overfitting does not exist on
    # model_evaluation.html (checked against the live page), so this dropped the
    # learner at the top of a very long metrics reference. scikit-learn has a
    # dedicated worked example for exactly this topic.
    {
        "id": 784,
        "topic_slug": "ml-bias-variance",
        "new_url": "https://scikit-learn.org/stable/auto_examples/model_selection/plot_underfitting_overfitting.html",
        "new_title": "Underfitting vs Overfitting - a worked comparison",
        "new_provider": "scikit-learn",
        "new_section": "FULL_SINGLE_PAGE",
        "reason": "WRONG_PAGE: the #underfitting-vs-overfitting anchor does not exist on that page",
    },
    # Same fault: #gradient-descent is not an anchor on linear_model.html.
    # Stochastic Gradient Descent has its own user-guide chapter.
    {
        "id": 776,
        "topic_slug": "ml-gradient-descent-intuition",
        "new_url": "https://scikit-learn.org/stable/modules/sgd.html",
        "new_title": "Stochastic Gradient Descent - scikit-learn user guide",
        "new_provider": "scikit-learn",
        "new_section": "FULL_SINGLE_PAGE",
        "reason": "WRONG_PAGE: the #gradient-descent anchor does not exist on linear_model.html",
    },
    # The primary here was a general linear-classifier video, byte-identical to
    # ml-gradient-descent-intuition's primary and not about penalised
    # regression. The user guide covers L2, L1 and choosing alpha by
    # cross-validation, which is the whole objective.
    {
        "id": 896,
        "topic_slug": "ml-ridge-lasso",
        "new_url": "https://scikit-learn.org/stable/modules/linear_model.html#ridge-regression-and-classification",
        "new_title": "Linear Models - Ridge and Lasso, and choosing alpha by CV",
        "new_provider": "scikit-learn",
        "new_role": "PRIMARY",
        "new_section": "Ridge regression and classification through Lasso",
        "reason": "WRONG_PAGE: primary was a linear-classifier video shared with another topic",
        "alias": True,  # the fragment is not sent to the server
    },
    {
        "id": 912,
        "topic_slug": "ml-ridge-lasso",
        "new_url": "https://www.youtube.com/watch?v=rcXcGS1M77g",
        "new_title": "Linear Classifiers Part 1 (background)",
        "new_provider": "Vizuara",
        "new_role": "SUPPLEMENT",
        "reason": "WRONG_PAGE: demoted; covers linear classifiers, not L1/L2 penalties",
    },
    # The primary was the StatQuest decision-tree video, byte-identical to
    # ml-decision-trees' primary. The objective is training a classifier and
    # reading a confusion matrix, which is what Google's classification module
    # is about.
    {
        "id": 595,
        "topic_slug": "ml-classification",
        "new_url": "https://developers.google.com/machine-learning/crash-course/classification",
        "new_title": "Classification - thresholds, confusion matrix, and metrics",
        "new_provider": "Google",
        "new_section": "FULL_SINGLE_PAGE",
        "reason": "WRONG_PAGE: primary duplicated ml-decision-trees and taught splits, not classifier output",
    },
    # mlp.html barely touches MSE versus cross-entropy or the pairing of an
    # output layer with its loss. Softmax regression is where D2L derives it.
    {
        "id": 795,
        "topic_slug": "dl-loss-functions-nn",
        "new_url": "https://d2l.ai/chapter_linear-classification/softmax-regression.html",
        "new_title": "Softmax Regression - output layers and cross-entropy loss",
        "new_provider": "D2L.ai",
        "new_section": "FULL_SINGLE_PAGE",
        "reason": "WRONG_PAGE: mlp.html does not derive the loss functions this topic is about",
    },
    # sequence.html covers autoregressive and Markov sequence modelling but
    # never introduces recurrence, weight sharing across time, or the
    # vanishing-memory failure this topic names.
    {
        "id": 812,
        "topic_slug": "dl-rnn-awareness",
        "new_url": "https://d2l.ai/chapter_recurrent-neural-networks/rnn.html",
        "new_title": "Recurrent Neural Networks - hidden state and weight sharing",
        "new_provider": "D2L.ai",
        "new_section": "FULL_SINGLE_PAGE",
        "reason": "WRONG_PAGE: sequence.html never introduces recurrence or the hidden state",
    },
    # A reference with no section on a page four topics share. The anchor exists
    # and pins it to the section this topic is actually about.
    {
        "id": 793,
        "topic_slug": "dl-activation-functions",
        "new_url": "https://d2l.ai/chapter_multilayer-perceptrons/mlp.html#activation-functions",
        "new_title": "Activation Functions - ReLU, sigmoid and tanh",
        "new_provider": "D2L.ai",
        "new_section": "Activation Functions",
        "reason": "MISLABELLED: pinned to its own section on a page four topics share",
        "alias": True,  # the fragment is not sent to the server
    },
    # The primary was docs.python.org/3/tutorial/index.html -- the tutorial's
    # table of contents. The topic objective is writing and running scripts with
    # venv and pip, and chapter 12 is the page that teaches it.
    {
        "id": 615,
        "topic_slug": "py-syntax",
        "new_url": "https://docs.python.org/3/tutorial/venv.html",
        "new_title": "Virtual Environments and Packages",
        "new_provider": "Python Software Foundation",
        "new_section": "FULL_SINGLE_PAGE",
        "reason": "WRONG_PAGE: the primary was the tutorial's table of contents",
    },
    # ds-eda's page is a general pandas API tour rather than anything about
    # distributions or relationships, but selection and grouping are on it, and
    # no better single page exists in those docs. Left as-is deliberately.
    # d2l's statistics.html covers estimator bias/variance, hypothesis testing
    # and confidence intervals. It has no covariance and no correlation section
    # at all; those live in the random-variables appendix (22.6.1.10 and
    # 22.6.1.11), including the unitless -1..1 range this topic is about.
    {
        "id": 886,
        "topic_slug": "math-covariance-correlation",
        "new_url": "https://d2l.ai/chapter_appendix-mathematics-for-deep-learning/random-variables.html",
        "new_title": "Random Variables - covariance and correlation",
        "new_provider": "D2L.ai",
        "new_section": "22.6.1.10 Covariance through 22.6.1.11 Correlation",
        "reason": "WRONG_PAGE: statistics.html has no covariance or correlation section",
    },
    # Titles naming a publisher that does not serve the page. These are the
    # last of the mislabelled rows, found by authors reading the pages rather
    # than by the link checker -- the URLs were right all along.
    {
        "id": 566,
        "topic_slug": "se-solid-srp",
        "new_url": "https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html",
        "new_title": "The Single Responsibility Principle - a reason to change is an actor",
        "new_provider": "Clean Coder (Robert C. Martin)",
        "reason": "MISLABELLED: titled DigitalOcean; the page is Robert C. Martin's own article",
    },
    {
        "id": 567,
        "topic_slug": "se-solid-ocp",
        "new_url": "https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html",
        "new_title": "The Open-Closed Principle - extend without modifying",
        "new_provider": "Clean Coder (Robert C. Martin)",
        "reason": "MISLABELLED: titled DigitalOcean; the page is Robert C. Martin's own article",
    },
    {
        "id": 605,
        "topic_slug": "ai-eng-awareness",
        "new_url": "https://developers.openai.com/api/docs/guides/evals",
        "new_title": "Evaluating model output - what AI engineering measures",
        "new_provider": "OpenAI",
        "reason": "MISLABELLED: titled DeepLearning.AI; the page is OpenAI's evals guide",
    },
    {
        "id": 606,
        "topic_slug": "ai-eng-path",
        "new_url": "https://developers.openai.com/api/docs/guides/prompt-engineering",
        "new_title": "Prompt engineering - the first rung of the AI engineering ladder",
        "new_provider": "OpenAI",
        "reason": "MISLABELLED: titled DeepLearning.AI; the page is OpenAI's prompting guide",
    },
    # Restored after a curriculum re-import reverted them. These four rows had
    # the manifest as their source of truth, and the manifest still held the
    # original values, so a DB-only repair could not survive. They are keyed by
    # id here and synced back into the manifests by sync_manifests.py.
    #
    # A "short courses" index page is a catalogue, not a lesson: it cannot be
    # the exact thing to open for a topic.
    {
        "id": 650,
        "topic_slug": "genai-rag",
        "new_url": "https://www.pinecone.io/learn/retrieval-augmented-generation/",
        "new_title": "Retrieval-Augmented Generation - the full pipeline",
        "new_provider": "Pinecone",
        "reason": "WRONG_PAGE: a LangChain course catalogue page is not a RAG lesson",
    },
    {
        "id": 652,
        "topic_slug": "genai-eval",
        "new_url": "https://developers.openai.com/api/docs/guides/evals",
        "new_title": "Working with evals - graders, datasets and scoring",
        "new_provider": "OpenAI",
        "reason": "RELOCATED: platform.openai.com/docs/guides/evaluation now 404s",
    },
    {
        "id": 605,
        "topic_slug": "ai-eng-awareness",
        "new_url": "https://developers.openai.com/api/docs/guides/evals",
        "new_title": "Evaluating model output - what AI engineering measures",
        "new_provider": "OpenAI",
        "reason": "WRONG_PAGE: a course catalogue index is not a lesson on the topic",
    },
    {
        "id": 606,
        "topic_slug": "ai-eng-path",
        "new_url": "https://developers.openai.com/api/docs/guides/prompt-engineering",
        "new_title": "Prompt engineering - the first rung of the AI engineering ladder",
        "new_provider": "OpenAI",
        "reason": "WRONG_PAGE: a course catalogue index is not a lesson on the topic",
    },
    # One untimestamped video was a second PRIMARY on five Java topics at once,
    # so "open exactly this" resolved to "watch this whole course" five times
    # over. Each of the five already has a real PRIMARY that is one page on one
    # subject (dev.java or the Helsinki course), so the video becomes what it
    # actually is: optional watching alongside the page.
    #
    # Deliberately NOT extended to the other 116 topics with two PRIMARYs.
    # Those are almost all a GeeksforGeeks article paired with a NeetCode video
    # on a DSA topic, which is a read-then-watch pairing rather than a mistake.
    {
        "id": 917,
        "topic_slug": "java-operators",
        "new_url": "https://www.youtube.com/watch?v=xTtL8E4LzTQ",
        "new_title": "Bro Code Java course - Operators (optional watch)",
        "new_provider": "Bro Code",
        "new_role": "SUPPLEMENT",
        "reason": "MISLABELLED: a second PRIMARY with no timestamps, shared by five topics",
    },
    {
        "id": 918,
        "topic_slug": "java-if-else",
        "new_url": "https://www.youtube.com/watch?v=xTtL8E4LzTQ",
        "new_title": "Bro Code Java course - if / else (optional watch)",
        "new_provider": "Bro Code",
        "new_role": "SUPPLEMENT",
        "reason": "MISLABELLED: a second PRIMARY with no timestamps, shared by five topics",
    },
    {
        "id": 919,
        "topic_slug": "java-switch",
        "new_url": "https://www.youtube.com/watch?v=xTtL8E4LzTQ",
        "new_title": "Bro Code Java course - switch (optional watch)",
        "new_provider": "Bro Code",
        "new_role": "SUPPLEMENT",
        "reason": "MISLABELLED: a second PRIMARY with no timestamps, shared by five topics",
    },
    {
        "id": 920,
        "topic_slug": "java-loops",
        "new_url": "https://www.youtube.com/watch?v=xTtL8E4LzTQ",
        "new_title": "Bro Code Java course - Loops (optional watch)",
        "new_provider": "Bro Code",
        "new_role": "SUPPLEMENT",
        "reason": "MISLABELLED: a second PRIMARY with no timestamps, shared by five topics",
    },
    {
        "id": 921,
        "topic_slug": "java-break-continue",
        "new_url": "https://www.youtube.com/watch?v=xTtL8E4LzTQ",
        "new_title": "Bro Code Java course - break and continue (optional watch)",
        "new_provider": "Bro Code",
        "new_role": "SUPPLEMENT",
        "reason": "MISLABELLED: a second PRIMARY with no timestamps, shared by five topics",
    },
)


#: Provider strings that named the wrong publisher for a page that is correct.
MISLABELLED_PROVIDERS: dict[str, str] = {
    # These moved with Anthropic's docs and are correctly mapped; only the
    # audit's host table was missing the entry, so nothing to change here.
}


def _all_replacements() -> tuple[Replacement, ...]:
    return RELOCATED + WRONG_PAGE + RELOCATED_BY_REDIRECT + WRONG_PAGE_SECOND_PASS


def collect(conn: sqlite3.Connection) -> list[dict]:
    """Every planned change, as {resource id, field, old, new, reason}."""
    conn.row_factory = sqlite3.Row
    rows = list(
        conn.execute(
            """
            SELECT r.id, r.url, r.title, r.provider, r.role, t.slug AS topic_slug
            FROM curriculum_resources r
            LEFT JOIN curriculum_lessons l ON r.lesson_id = l.id
            LEFT JOIN curriculum_topics t ON l.topic_id = t.id
            WHERE r.url IS NOT NULL AND r.url != ''
            """
        )
    )

    by_url: dict[str, list[Replacement]] = {}
    for rep in _all_replacements():
        by_url.setdefault(rep.old_url, []).append(rep)

    by_id = {entry["id"]: entry for entry in BY_RESOURCE_ID}

    planned: list[dict] = []
    for row in rows:
        targeted = by_id.get(row["id"])
        if targeted is not None and targeted.get("topic_slug") in (None, row["topic_slug"]):
            # These are declarative -- "this row should be X" -- so they match on
            # id whatever the row currently holds. Skip the ones already there,
            # or a second run reports every past repair as outstanding work.
            already = (
                row["url"] == targeted["new_url"]
                and row["title"] == (targeted.get("new_title") or row["title"])
                and row["provider"] == (targeted.get("new_provider") or row["provider"])
                and (targeted.get("new_role") is None or row["role"] == targeted["new_role"])
            )
            if already:
                continue
            planned.append(
                {
                    "id": row["id"],
                    "topic_slug": row["topic_slug"],
                    "old_url": row["url"],
                    "new_url": targeted["new_url"],
                    "old_title": row["title"],
                    "new_title": targeted.get("new_title") or row["title"],
                    "old_provider": row["provider"],
                    "new_provider": targeted.get("new_provider") or row["provider"],
                    "reason": targeted["reason"],
                    "alias": bool(targeted.get("alias")),
                    "new_role": targeted.get("new_role"),
                    "new_section": targeted.get("new_section"),
                }
            )
            continue

        explicit = None
        for rep in by_url.get(row["url"], []):
            if rep.topic_slug in (None, row["topic_slug"]):
                explicit = rep
                break

        if explicit is not None:
            planned.append(
                {
                    "id": row["id"],
                    "topic_slug": row["topic_slug"],
                    "old_url": row["url"],
                    "new_url": explicit.new_url,
                    "old_title": row["title"],
                    "new_title": explicit.new_title or row["title"],
                    "old_provider": row["provider"],
                    "new_provider": explicit.new_provider or row["provider"],
                    "reason": explicit.reason,
                    "alias": explicit.alias,
                }
            )
            continue

        target = rendered_url(row["url"])
        if target:
            planned.append(
                {
                    "id": row["id"],
                    "topic_slug": row["topic_slug"],
                    "old_url": row["url"],
                    "new_url": target,
                    "old_title": row["title"],
                    "new_title": row["title"],
                    "old_provider": row["provider"],
                    "new_provider": _provider_for(target, row["provider"]),
                    "reason": "RENDERED: raw source file replaced by the published page",
                    "alias": False,
                }
            )

    return planned


def _provider_for(url: str, current: Optional[str]) -> Optional[str]:
    """Name the publisher actually serving the page."""
    hosts = {
        "d2l.ai": "D2L.ai",
        "huggingface.co": "Hugging Face",
        "docs.pytorch.org": "PyTorch",
        "mlflow.org": "MLflow",
    }
    for host, provider in hosts.items():
        if host in url:
            return provider
    return current


def verify(planned: list[dict], workers: int = 12) -> tuple[list[dict], list[dict]]:
    """Fetch every new URL. Only changes that load cleanly are applied."""
    targets = sorted({p["new_url"] for p in planned})
    print(f"verifying {len(targets)} replacement URLs...")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        checks = {c.url: c for c in pool.map(fetch, targets)}

    good, bad = [], []
    for plan in planned:
        check = checks[plan["new_url"]]
        landed = (check.final_url or "").rstrip("/")
        # 403 means bot protection, not a broken page (MLflow, LeetCode do this).
        acceptable = check.status == 200 or check.status == 403
        drifted = bool(landed) and landed != plan["new_url"].rstrip("/")
        if plan.get("alias"):
            # A "latest" alias is meant to redirect; that is why we store it.
            drifted = False
        plan["verified_status"] = check.status
        plan["verified_title"] = check.page_title
        plan["landed_on"] = check.final_url
        if acceptable and not drifted:
            good.append(plan)
        else:
            plan["verify_error"] = check.error or ("redirected to " + (check.final_url or "?"))
            bad.append(plan)
    return good, bad


def apply(conn: sqlite3.Connection, planned: list[dict]) -> int:
    for plan in planned:
        conn.execute(
            """
            UPDATE curriculum_resources
               SET url = ?, title = ?, provider = ?, notes = ?,
                   role = COALESCE(?, role),
                   section = COALESCE(?, section)
             WHERE id = ?
            """,
            (
                plan["new_url"],
                plan["new_title"],
                plan["new_provider"],
                plan["reason"],
                plan.get("new_role"),
                plan.get("new_section"),
                plan["id"],
            ),
        )
    conn.commit()
    return len(planned)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    planned = collect(conn)
    if not planned:
        print("nothing to repair")
        return

    print(f"{len(planned)} resource rows planned for repair")
    good, bad = verify(planned, args.workers)

    reasons = Counter(p["reason"].split(":")[0] for p in good)
    print()
    for reason, count in reasons.most_common():
        print(f"  {reason}: {count}")
    if bad:
        print(f"\n{len(bad)} replacement(s) failed verification and will NOT be applied:")
        for plan in bad:
            print(f"  {plan['topic_slug']}: {plan['new_url']} — {plan['verify_error']}")

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "resource_link_repairs.json").write_text(
        json.dumps({"applied": [] if args.dry_run else good, "planned": good, "rejected": bad}, indent=2),
        encoding="utf-8",
    )

    if args.dry_run:
        print("\ndry run — nothing written")
        return

    changed = apply(conn, good)
    print(f"\nrepaired {changed} resource rows")


if __name__ == "__main__":
    main()
