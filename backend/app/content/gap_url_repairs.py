"""Repair broken/weak PRIMARY URLs for remaining unresolved topics."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.content.verification import VERIFICATION_NEEDS_REVIEW
from app.db.models import CurriculumResource

REPLACEMENTS: dict[str, dict] = {
    # Broken GFG
    "dsa-big-o-learn-exact": {
        "url": "https://www.geeksforgeeks.org/analysis-algorithms-big-o-analysis/",
        "section": "Big-O analysis",
    },
    "dsa-array-insert-delete-learn-exact": {
        "url": "https://www.geeksforgeeks.org/array-data-structure-guide/",
        "section": "Array insert and delete operations",
    },
    "dsa-singly-linked-list-learn-exact": {
        "url": "https://www.geeksforgeeks.org/linked-list-set-1-introduction/",
        "section": "Singly linked list introduction",
    },
    "dsa-binary-search-boundaries-learn-exact": {
        "url": "https://www.geeksforgeeks.org/binary-search/",
        "section": "Binary search bounds / low-high updates",
    },
    "genai-eval-primary": {
        "url": "https://platform.openai.com/docs/guides/evals",
        "section": "Evals",
    },
    # Better exact pages for weak hubs
    "dsa-bubble-sort-learn-exact": {"url": "https://www.geeksforgeeks.org/bubble-sort/", "section": "Bubble sort"},
    "dsa-selection-sort-learn-exact": {"url": "https://www.geeksforgeeks.org/selection-sort/", "section": "Selection sort"},
    "dsa-insertion-sort-learn-exact": {"url": "https://www.geeksforgeeks.org/insertion-sort/", "section": "Insertion sort"},
    "dsa-merge-sort-learn-exact": {"url": "https://www.geeksforgeeks.org/merge-sort/", "section": "Merge sort"},
    "dsa-quick-sort-learn-exact": {"url": "https://www.geeksforgeeks.org/quick-sort/", "section": "Quick sort"},
    "dsa-heap-sort-learn-exact": {"url": "https://www.geeksforgeeks.org/heap-sort/", "section": "Heap sort"},
    "dsa-knapsack-learn-exact": {"url": "https://www.geeksforgeeks.org/0-1-knapsack-problem-dp-10/", "section": "0/1 Knapsack"},
    "dsa-bst-search-learn-exact": {"url": "https://www.geeksforgeeks.org/binary-search-tree-set-1-search-and-insertion/", "section": "BST search"},
    "dsa-bst-insert-learn-exact": {"url": "https://www.geeksforgeeks.org/binary-search-tree-set-1-search-and-insertion/", "section": "BST insert"},
    "dsa-bst-delete-learn-exact": {"url": "https://www.geeksforgeeks.org/binary-search-tree-set-2-delete/", "section": "BST delete"},
    "dsa-bst-validate-learn-exact": {"url": "https://www.geeksforgeeks.org/a-program-to-check-if-a-binary-tree-is-bst-or-not/", "section": "Validate BST"},
    "dsa-union-find-learn-exact": {"url": "https://www.geeksforgeeks.org/introduction-to-disjoint-set-data-structure-or-union-find-algorithm/", "section": "Union-Find"},
    "dsa-memoization-learn-exact": {"url": "https://www.geeksforgeeks.org/memoization-1d-2d-and-3d/", "section": "Memoization"},
    "dsa-top-k-learn-exact": {"url": "https://www.geeksforgeeks.org/k-largestor-smallest-elements-in-an-array/", "section": "Top-K / heap selection"},
    "dsa-dp-1d-learn-exact": {"url": "https://www.geeksforgeeks.org/introduction-to-dynamic-programming-data-structures-and-algorithm-tutorials/", "section": "1D DP"},
    "dsa-dp-2d-learn-exact": {"url": "https://www.geeksforgeeks.org/dynamic-programming/", "section": "2D DP overview"},
    "dsa-grid-dp-learn-exact": {"url": "https://www.geeksforgeeks.org/unique-paths-in-a-grid-with-obstacles/", "section": "Grid DP paths"},
    "be-json-primary": {"url": "https://www.json.org/json-en.html", "section": "JSON grammar and values"},
    "math-vectors-primary": {"url": "https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces/vectors/a/vectors-intro-linear-algebra", "section": "Vectors intro"},
    "math-matrices-primary": {"url": "https://www.khanacademy.org/math/precalculus/x9e81a4f98389efdf:matrices/x9e81a4f98389efdf:mat-intro-to-matrices/a/intro-to-matrices", "section": "Intro to matrices"},
    "math-probability-primary": {"url": "https://www.khanacademy.org/math/statistics-probability/probability-library/basic-theoretical-probability/a/basic-probability", "section": "Basic probability"},
    "math-stats-summary-primary": {"url": "https://www.khanacademy.org/math/statistics-probability/summarizing-quantitative-data/mean-median-basics/a/mean-median-and-mode-review", "section": "Mean median mode"},
    "math-gradient-intuition-primary": {"url": "https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives/gradient-and-directional-derivatives/a/the-gradient", "section": "The gradient"},
    "dl-nn-basics-primary": {"url": "https://pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html", "section": "Build the neural network"},
    "dl-backprop-primary": {"url": "https://pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html", "section": "Autograd"},
    "dl-cnn-primary": {"url": "https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html", "section": "Training a classifier"},
    "mlops-tracking-primary": {"url": "https://mlflow.org/docs/latest/ml/tracking/", "section": "MLflow Tracking"},
    "mlops-model-packaging-primary": {"url": "https://mlflow.org/docs/latest/ml/model/", "section": "MLflow Models"},
    "ds-pandas-primary": {"url": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/01_table_oriented.html", "section": "What kind of data does pandas handle"},
    "ds-eda-primary": {"url": "https://pandas.pydata.org/docs/user_guide/10min.html", "section": "10 minutes to pandas"},
    "ds-sql-analytics-primary": {"url": "https://www.postgresql.org/docs/current/tutorial-agg.html", "section": "Aggregate functions"},
    "net-dns-primary": {"url": "https://developer.mozilla.org/en-US/docs/Glossary/DNS", "section": "DNS glossary"},
    "net-tcp-udp-primary": {"url": "https://developer.mozilla.org/en-US/docs/Glossary/TCP", "section": "TCP glossary"},
    "java-encapsulation-primary": {"url": "https://dev.java/learn/classes-objects/more-on-classes/", "section": "More on classes / encapsulation"},
    "java-set-primary": {"url": "https://dev.java/learn/api/collections-framework/sets/", "section": "Sets"},
    "java-map-primary": {"url": "https://dev.java/learn/api/collections-framework/maps/", "section": "Maps"},
    "se-solid-srp-primary": {
        "url": "https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design",
        "section": "Single Responsibility Principle",
    },
    "se-solid-ocp-primary": {
        "url": "https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design",
        "section": "Open-Closed Principle",
    },
}


def apply_gap_url_repairs(db: Session) -> dict[str, int]:
    fixed = 0
    missing = 0
    now = datetime.now(timezone.utc).isoformat()
    for slug, spec in REPLACEMENTS.items():
        row = db.query(CurriculumResource).filter(CurriculumResource.slug == slug).first()
        if not row:
            # try without -learn-exact / -primary variants already exact
            missing += 1
            continue
        row.url = spec["url"]
        if spec.get("section"):
            row.section = spec["section"][:200]
        row.verification_status = VERIFICATION_NEEDS_REVIEW
        row.required_concepts_covered = []
        row.last_verified_at = now
        fixed += 1
    db.flush()
    return {"fixed": fixed, "missing_slug": missing}
