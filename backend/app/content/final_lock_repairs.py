"""Final lockdown repairs: broken URL replacements, demotions, accessibility honesty.

Does not change topic slugs, names, prerequisites, or next_topic.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.content.verification import (
    EXACTNESS_EXACT,
    VERIFICATION_BROKEN,
    VERIFICATION_NEEDS_REVIEW,
    VERIFICATION_VERIFIED_COVERAGE,
)
from app.db.models import CurriculumResource

# Known-good replacements after accessibility failures (404) or bot 403 on otherwise stable docs.
URL_REPLACEMENTS: dict[str, dict[str, Any]] = {
    "cf-dependency-primary": {
        "url": "https://pip.pypa.io/en/stable/topics/dependency-resolution/",
        "title": "Dependency resolution (pip)",
        "provider": "PyPA",
        "section": "Dependency resolution",
        "exactness": EXACTNESS_EXACT,
    },
    "cf-os-env-primary": {
        "url": "https://www.geeksforgeeks.org/environment-variables-in-linux-unix/",
        "title": "Environment Variables in Linux/Unix",
        "provider": "GeeksforGeeks",
        "section": "Environment variables",
        "exactness": EXACTNESS_EXACT,
    },
    "cf-os-environment-variables-primary": {
        "url": "https://missing.csail.mit.edu/2020/command-line/",
        "title": "The Shell — MIT Missing Semester",
        "provider": "MIT",
        "section": "Shell / environment variables",
        "exactness": EXACTNESS_EXACT,
    },
    "cf-shell-primary": {
        "url": "https://missing.csail.mit.edu/2020/shell-tools/",
        "section": "Shell tools and scripting",
    },
    "java-memory-model-basics-primary": {
        "url": "https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html",
        "title": "JLS Chapter 17 — Threads and Locks (memory model)",
        "provider": "Oracle",
        "section": "Chapter 17",
        "exactness": "MULTI_TOPIC",
    },
    "se-sdlc-primary": {
        "url": "https://www.ibm.com/topics/software-development-lifecycle",
        "title": "Software Development Lifecycle (IBM)",
        "provider": "IBM",
        "section": "SDLC overview",
        "exactness": EXACTNESS_EXACT,
    },
    "se-solid-srp-primary": {
        "url": "https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design",
        "title": "SOLID principles (DigitalOcean)",
        "provider": "DigitalOcean",
        "section": "Single Responsibility Principle",
        "exactness": "MULTI_TOPIC",
    },
    "se-solid-ocp-primary": {
        "url": "https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design",
        "title": "SOLID principles (DigitalOcean)",
        "provider": "DigitalOcean",
        "section": "Open-Closed Principle",
        "exactness": "MULTI_TOPIC",
    },
    "ml-what-is-ml-primary": {
        "url": "https://scikit-learn.org/stable/getting_started.html",
        "title": "Getting Started — scikit-learn",
        "provider": "scikit-learn",
        "section": "Getting Started",
        "exactness": EXACTNESS_EXACT,
    },
    "dl-nn-basics-primary": {
        "url": "https://pytorch.org/tutorials/beginner/basics/intro.html",
        "title": "PyTorch Basics Intro",
        "provider": "PyTorch",
        "section": "Learn the Basics",
        "exactness": "MULTI_TOPIC",
    },
    "dl-backprop-primary": {
        "url": "https://pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html",
        "title": "Automatic Differentiation with torch.autograd",
        "provider": "PyTorch",
        "section": "Autograd",
        "exactness": EXACTNESS_EXACT,
        # May 403 to bots — keep URL for learners; status set NEEDS_REVIEW if fetch fails
    },
    "dl-cnn-primary": {
        "url": "https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html",
        "title": "Training a Classifier (CIFAR10)",
        "provider": "PyTorch",
        "section": "CNN classifier",
        "exactness": EXACTNESS_EXACT,
    },
    "genai-eval-primary": {
        "url": "https://platform.openai.com/docs/guides/evaluation",
        "title": "OpenAI Evals guide",
        "provider": "OpenAI",
        "section": "Evaluation",
        "exactness": EXACTNESS_EXACT,
    },
    "mlops-monitoring-primary": {
        "url": "https://www.evidentlyai.com/ml-in-production/model-monitoring",
        "title": "Model monitoring overview",
        "provider": "Evidently",
        "section": "Model monitoring",
        "exactness": EXACTNESS_EXACT,
    },
    "cf-space-complexity-primary": {
        "url": "https://www.geeksforgeeks.org/gfact-51-space-complexity/",
        "title": "Space Complexity",
        "provider": "GeeksforGeeks",
        "section": "Space complexity",
        "exactness": EXACTNESS_EXACT,
    },
    "java-memory-model-primary": {
        "url": "https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html",
        "title": "JLS Chapter 17 — Threads and Locks",
        "provider": "Oracle",
        "section": "Chapter 17",
        "exactness": "MULTI_TOPIC",
    },
}


def apply_url_repairs(db: Session) -> dict[str, int]:
    fixed = 0
    missing = 0
    for slug, spec in URL_REPLACEMENTS.items():
        row = db.query(CurriculumResource).filter(CurriculumResource.slug == slug).first()
        if not row:
            missing += 1
            continue
        row.url = spec["url"]
        if spec.get("title"):
            row.title = spec["title"][:200]
        if spec.get("provider"):
            row.provider = spec["provider"]
        if spec.get("section"):
            row.section = spec["section"][:200]
        if spec.get("exactness"):
            row.exactness = spec["exactness"]
        # Clear broken flag so re-inspect can run; do not invent coverage here
        if (row.verification_status or "") in (VERIFICATION_BROKEN, "BROKEN"):
            row.verification_status = VERIFICATION_NEEDS_REVIEW
            row.required_concepts_covered = []
        row.notes = ((row.notes or "") + " | URL repaired at final lockdown").strip(" |")[:500]
        row.last_verified_at = datetime.now(timezone.utc).isoformat()
        fixed += 1

    # Demote duplicate secondary primary that shadows MIT env primary
    demoted = 0
    row = db.query(CurriculumResource).filter(CurriculumResource.slug == "cf-os-env-primary").first()
    if row and (row.role or "").upper() == "PRIMARY":
        row.role = "REFERENCE"
        demoted += 1

    db.flush()
    return {"url_fixed": fixed, "slug_missing": missing, "demoted": demoted}
