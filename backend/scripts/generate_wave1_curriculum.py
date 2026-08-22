"""One-shot generator for wave-1 curriculum YAML (run from backend/)."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path("content/curriculum")


def topic(
    slug,
    name,
    order,
    prereqs,
    objective,
    url,
    provider,
    practice_what,
    *,
    track="CORE",
    depth="WORKING_KNOWLEDGE",
    domain="software-engineering",
    minutes=45,
    build=None,
):
    resources = [
        {
            "slug": f"{slug}-primary",
            "title": f"{provider}: {name}",
            "type": "documentation",
            "url": url,
            "provider": provider,
            "role": "PRIMARY",
            "verification_status": "TRUSTED",
            "official": True,
            "order": 0,
            "description": f"TRUSTED official/docs source for {name}.",
        }
    ]
    exercises = []
    if practice_what:
        exercises.append(
            {
                "slug": f"{slug}-practice",
                "title": f"Practice: {name}",
                "type": "ACTION_CHECKLIST",
                "instructions": practice_what,
                "difficulty": "beginner",
                "order": 0,
            }
        )
    if build:
        exercises.append(
            {
                "slug": f"{slug}-build",
                "title": f"Build: {name}",
                "type": "SELF_REFLECTION",
                "instructions": build,
                "difficulty": "intermediate",
                "order": 1,
            }
        )
    answer = objective[:80] + ("..." if len(objective) > 80 else "")
    return {
        "slug": slug,
        "name": name,
        "description": objective,
        "order": order,
        "prerequisites": prereqs,
        "learning_objective": objective,
        "mastery_criteria": [
            f"Explain {name} in your own words.",
            "Complete the mapped practice checklist.",
        ],
        "fast_trackable": True,
        "learning_track": track,
        "depth_target": depth,
        "parallel_eligible": track == "ALWAYS_ON",
        "estimated_minutes": minutes,
        "domain_key": domain,
        "lessons": [
            {
                "slug": f"{slug}-core",
                "title": name,
                "description": objective,
                "order": 0,
                "hours_estimated": round(minutes / 60, 2),
                "resources": resources,
                "questions": [
                    {
                        "slug": f"{slug}-q1",
                        "prompt": f"What is the core idea of {name}?",
                        "options": [
                            "A vague buzzword with no engineering meaning",
                            answer,
                            "Only relevant for interviews, not real systems",
                            "Replaces the need for prerequisites",
                        ],
                        "answer": answer,
                        "explanation": "Focus on the stated learning objective.",
                        "difficulty": "easy",
                        "mastery_requirement": True,
                    }
                ],
                "exercises": exercises,
            }
        ],
    }


def module(slug, name, order, topics):
    return {"slug": slug, "name": name, "order": order, "topics": topics}


def manifest(level_slug, level_name, level_order, subject_slug, subject_name, modules):
    return {
        "schema_version": 1,
        "kind": "curriculum_manifest",
        "origin": "official",
        "track": {
            "slug": "engineering-os-v1",
            "name": "Engineering OS",
            "description": "Curriculum V1 expanded with SE, backend, math, and ML foundations.",
            "order": 0,
            "levels": [
                {
                    "slug": level_slug,
                    "name": level_name,
                    "description": level_name,
                    "order": level_order,
                    "subjects": [
                        {
                            "slug": subject_slug,
                            "name": subject_name,
                            "description": subject_name,
                            "order": 0,
                            "modules": modules,
                        }
                    ],
                }
            ],
        },
    }


def main() -> None:
    se_specs = [
        (
            "se-sdlc",
            "SDLC overview",
            [],
            "Describe the software development lifecycle phases and why they exist.",
            "https://en.wikipedia.org/wiki/Software_development_process",
            "Wikipedia",
            "WHAT: List phases of a simple SDLC for a CLI tool. HOW MANY: 1 write-up. WHERE: notes.",
        ),
        (
            "se-requirements",
            "Requirements & scope",
            ["se-sdlc"],
            "Turn a vague ask into testable requirements and out-of-scope notes.",
            "https://www.ibm.com/think/topics/software-development-life-cycle",
            "IBM",
            "WHAT: Write 5 acceptance criteria for a todo API. HOW MANY: 5. WHERE: notes.",
        ),
        (
            "se-versioning",
            "Semantic versioning",
            ["se-sdlc"],
            "Apply SemVer to library changes without breaking consumers accidentally.",
            "https://semver.org/",
            "SemVer",
            "WHAT: Label 5 change scenarios as major/minor/patch. HOW MANY: 5. WHERE: notes.",
        ),
        (
            "se-solid-srp",
            "SOLID — Single Responsibility",
            ["se-sdlc"],
            "Keep modules focused on one reason to change.",
            "https://en.wikipedia.org/wiki/SOLID",
            "Wikipedia",
            "WHAT: Refactor a god-class sketch into SRP modules on paper. HOW MANY: 1. WHERE: notes.",
        ),
        (
            "se-solid-ocp",
            "SOLID — Open/Closed",
            ["se-solid-srp"],
            "Extend behavior without rewriting stable cores.",
            "https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle",
            "Wikipedia",
            "WHAT: Design a plugin hook instead of an if-ladder. HOW MANY: 1 sketch. WHERE: notes.",
        ),
        (
            "se-testing-pyramid",
            "Testing pyramid",
            ["se-sdlc"],
            "Choose unit vs integration vs E2E tests with cost/confidence tradeoffs.",
            "https://martinfowler.com/articles/practical-test-pyramid.html",
            "Martin Fowler",
            "WHAT: Map 6 checks onto pyramid layers. HOW MANY: 6. WHERE: notes.",
        ),
        (
            "se-unit-tests",
            "Unit testing basics",
            ["se-testing-pyramid"],
            "Write focused unit tests for pure functions and edge cases.",
            "https://docs.pytest.org/en/stable/",
            "pytest",
            "WHAT: Write 3 unit tests for a pure function. HOW MANY: 3. WHERE: local repo.",
        ),
        (
            "se-api-design",
            "API design basics",
            ["se-requirements"],
            "Design resource-oriented HTTP APIs with clear errors.",
            "https://restfulapi.net/",
            "restfulapi.net",
            "WHAT: Sketch endpoints for a notes service. HOW MANY: 1 sketch. WHERE: notes.",
        ),
        (
            "se-code-review",
            "Code review habits",
            ["se-unit-tests"],
            "Review diffs for correctness, clarity, and risk — not style nitpicks only.",
            "https://google.github.io/eng-practices/review/",
            "Google",
            "WHAT: Review a sample PR checklist. HOW MANY: 1. WHERE: notes.",
            "ALWAYS_ON",
        ),
        (
            "se-ci-basics",
            "CI basics",
            ["se-unit-tests"],
            "Run tests automatically on every push.",
            "https://docs.github.com/en/actions/get-started/understand-github-actions",
            "GitHub Docs",
            "WHAT: Describe a minimal CI workflow. HOW MANY: 1. WHERE: notes.",
        ),
    ]
    se_topics = []
    for i, spec in enumerate(se_specs):
        slug, name, prereqs, obj, url, provider, practice, *rest = spec
        track = rest[0] if rest else "CORE"
        se_topics.append(
            topic(
                slug,
                name,
                i,
                prereqs,
                obj,
                url,
                provider,
                practice,
                track=track,
                domain="software-engineering",
                build=f"IMPLEMENT: tiny demo related to {name}." if i % 3 == 2 else None,
            )
        )
    se = manifest(
        "domain-se",
        "Software Engineering",
        3,
        "software-engineering",
        "Software Engineering Core",
        [module("mod-se-core", "Engineering practice", 0, se_topics)],
    )

    be_specs = [
        (
            "db-sql-select",
            "SQL SELECT",
            [],
            "Query rows with SELECT, WHERE, ORDER BY.",
            "https://www.sqlite.org/lang_select.html",
            "SQLite",
            "WHAT: Write 5 SELECT queries on a sample table. HOW MANY: 5. WHERE: SQLite.",
        ),
        (
            "db-sql-joins",
            "SQL JOINs",
            ["db-sql-select"],
            "Combine tables with INNER/LEFT joins correctly.",
            "https://www.sqlite.org/lang_select.html",
            "SQLite",
            "WHAT: Write 3 JOIN queries. HOW MANY: 3. WHERE: SQLite.",
        ),
        (
            "db-indexes",
            "Indexes & query plans",
            ["db-sql-select"],
            "Explain when an index helps and when it hurts.",
            "https://www.sqlite.org/queryplanner.html",
            "SQLite",
            "WHAT: Compare EXPLAIN QUERY PLAN with/without index. HOW MANY: 2. WHERE: SQLite.",
        ),
        (
            "db-transactions",
            "Transactions",
            ["db-sql-select"],
            "Use BEGIN/COMMIT/ROLLBACK for atomic updates.",
            "https://www.sqlite.org/lang_transaction.html",
            "SQLite",
            "WHAT: Script a transfer with rollback on failure. HOW MANY: 1. WHERE: SQLite.",
        ),
        (
            "db-schema-design",
            "Schema design basics",
            ["db-sql-joins"],
            "Model entities, keys, and relationships without premature complexity.",
            "https://www.postgresql.org/docs/current/ddl.html",
            "PostgreSQL",
            "WHAT: Design schema for a notes app. HOW MANY: 1 ER sketch. WHERE: notes.",
        ),
        (
            "be-http",
            "HTTP fundamentals",
            [],
            "Explain methods, status codes, headers, and idempotency.",
            "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview",
            "MDN",
            "WHAT: Map 8 status codes to scenarios. HOW MANY: 8. WHERE: notes.",
        ),
        (
            "be-rest",
            "REST resources",
            ["be-http"],
            "Model collections/items with consistent URLs and verbs.",
            "https://restfulapi.net/rest-architectural-constraints/",
            "restfulapi.net",
            "WHAT: Design REST resources for bookstore. HOW MANY: 1. WHERE: notes.",
        ),
        (
            "be-json",
            "JSON APIs",
            ["be-http"],
            "Serialize request/response bodies and validate shapes.",
            "https://www.json.org/json-en.html",
            "json.org",
            "WHAT: Design 3 request/response JSON samples. HOW MANY: 3. WHERE: notes.",
        ),
        (
            "be-fastapi-intro",
            "FastAPI intro",
            ["be-rest", "be-json"],
            "Build a tiny FastAPI app with typed routes.",
            "https://fastapi.tiangolo.com/tutorial/first-steps/",
            "FastAPI",
            "WHAT: Create GET/POST hello endpoints. HOW MANY: 2 routes. WHERE: local repo.",
        ),
        (
            "be-auth-basics",
            "Auth basics",
            ["be-fastapi-intro"],
            "Distinguish authentication vs authorization; hash passwords.",
            "https://fastapi.tiangolo.com/tutorial/security/",
            "FastAPI",
            "WHAT: Outline register/login flow. HOW MANY: 1. WHERE: notes.",
        ),
        (
            "be-errors",
            "API error handling",
            ["be-fastapi-intro"],
            "Return structured errors without leaking internals.",
            "https://fastapi.tiangolo.com/tutorial/handling-errors/",
            "FastAPI",
            "WHAT: Define error envelope for 4 failure modes. HOW MANY: 4. WHERE: notes.",
        ),
        (
            "be-persistence",
            "API + SQL persistence",
            ["be-fastapi-intro", "db-sql-select"],
            "Wire a FastAPI route to SQL CRUD.",
            "https://fastapi.tiangolo.com/tutorial/sql-databases/",
            "FastAPI",
            "WHAT: Persist one resource with SQLAlchemy/SQLite. HOW MANY: 1 resource. WHERE: local repo.",
        ),
    ]
    be_topics = []
    for i, (slug, name, prereqs, obj, url, provider, practice) in enumerate(be_specs):
        be_topics.append(
            topic(
                slug,
                name,
                i,
                prereqs,
                obj,
                url,
                provider,
                practice,
                domain="backend",
                build=(
                    f"IMPLEMENT: small demo for {name}."
                    if "fastapi" in slug or slug.endswith("persistence")
                    else None
                ),
            )
        )
    be = manifest(
        "domain-backend",
        "Databases & Backend",
        4,
        "databases-backend",
        "Databases and Backend Foundations",
        [
            module("mod-db-sql", "SQL & data", 0, be_topics[:5]),
            module("mod-be-http", "HTTP & APIs", 1, be_topics[5:]),
        ],
    )

    math_specs = [
        (
            "math-vectors",
            "Vectors intuition",
            [],
            "Reason about vectors as lists of numbers with direction/magnitude.",
            "https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces",
            "Khan Academy",
            "WHAT: Compute 3 dot products by hand. HOW MANY: 3. WHERE: notes.",
        ),
        (
            "math-matrices",
            "Matrices intuition",
            ["math-vectors"],
            "Multiply small matrices and interpret as linear maps.",
            "https://www.khanacademy.org/math/linear-algebra/matrix-transformations",
            "Khan Academy",
            "WHAT: Multiply two 2x2 matrices. HOW MANY: 2. WHERE: notes.",
        ),
        (
            "math-probability",
            "Probability basics",
            [],
            "Use probability rules for independent events and simple conditionals.",
            "https://www.khanacademy.org/math/statistics-probability/probability-library",
            "Khan Academy",
            "WHAT: Solve 5 probability drills. HOW MANY: 5. WHERE: notes.",
        ),
        (
            "math-distributions",
            "Distributions intuition",
            ["math-probability"],
            "Describe Bernoulli/Normal distributions qualitatively.",
            "https://seeing-theory.brown.edu/probability-distributions/index.html",
            "Seeing Theory",
            "WHAT: Sketch PDF/PMF for 2 distributions. HOW MANY: 2. WHERE: notes.",
        ),
        (
            "math-stats-summary",
            "Summary statistics",
            ["math-probability"],
            "Compute mean/variance and interpret them.",
            "https://www.khanacademy.org/math/statistics-probability",
            "Khan Academy",
            "WHAT: Compute mean/variance for a tiny dataset. HOW MANY: 1. WHERE: notes.",
        ),
        (
            "math-gradient-intuition",
            "Gradient intuition",
            ["math-vectors"],
            "Explain gradient as direction of steepest ascent for loss surfaces.",
            "https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives",
            "Khan Academy",
            "WHAT: Sketch gradient arrows on a contour. HOW MANY: 1. WHERE: notes.",
        ),
    ]
    math_topics = [
        topic(slug, name, i, prereqs, obj, url, provider, practice, domain="mathematics")
        for i, (slug, name, prereqs, obj, url, provider, practice) in enumerate(math_specs)
    ]
    math = manifest(
        "domain-math",
        "Math for ML",
        5,
        "math-for-ml",
        "Mathematics for Machine Learning",
        [module("mod-math-ml", "Math foundations", 0, math_topics)],
    )

    ml_specs = [
        (
            "ml-what-is-ml",
            "What is machine learning",
            ["math-probability"],
            "Distinguish supervised/unsupervised learning and typical tasks.",
            "https://scikit-learn.org/stable/tutorial/basic/tutorial.html",
            "scikit-learn",
            "WHAT: Label 6 problems as supervised/unsupervised. HOW MANY: 6. WHERE: notes.",
        ),
        (
            "ml-features-labels",
            "Features & labels",
            ["ml-what-is-ml"],
            "Frame tabular problems with features X and label y.",
            "https://scikit-learn.org/stable/getting_started.html",
            "scikit-learn",
            "WHAT: Define features/labels for 2 datasets. HOW MANY: 2. WHERE: notes.",
        ),
        (
            "ml-train-test",
            "Train/test split",
            ["ml-features-labels"],
            "Split data to estimate generalization, avoid leakage.",
            "https://scikit-learn.org/stable/modules/cross_validation.html",
            "scikit-learn",
            "WHAT: Split a toy dataset 80/20. HOW MANY: 1. WHERE: notebook.",
        ),
        (
            "ml-linear-regression",
            "Linear regression",
            ["ml-train-test", "math-vectors"],
            "Fit and interpret a linear regressor.",
            "https://scikit-learn.org/stable/modules/linear_model.html",
            "scikit-learn",
            "WHAT: Fit LinearRegression on a toy set. HOW MANY: 1. WHERE: notebook.",
        ),
        (
            "ml-classification",
            "Classification basics",
            ["ml-train-test"],
            "Train a classifier and read a confusion matrix.",
            "https://scikit-learn.org/stable/supervised_learning.html",
            "scikit-learn",
            "WHAT: Train LogisticRegression; print confusion matrix. HOW MANY: 1. WHERE: notebook.",
        ),
        (
            "ml-metrics",
            "ML metrics",
            ["ml-classification"],
            "Choose accuracy/precision/recall/F1 appropriately.",
            "https://scikit-learn.org/stable/modules/model_evaluation.html",
            "scikit-learn",
            "WHAT: Compute precision/recall on a toy prediction set. HOW MANY: 1. WHERE: notebook.",
        ),
        (
            "ml-overfitting",
            "Overfitting & regularization",
            ["ml-metrics"],
            "Detect overfitting and apply simple regularization.",
            "https://scikit-learn.org/stable/modules/linear_model.html#ridge-regression",
            "scikit-learn",
            "WHAT: Compare train vs test error under complexity. HOW MANY: 1 experiment. WHERE: notebook.",
        ),
        (
            "ml-sklearn-pipeline",
            "sklearn Pipeline",
            ["ml-overfitting"],
            "Compose preprocessing + model in a Pipeline.",
            "https://scikit-learn.org/stable/modules/compose.html",
            "scikit-learn",
            "WHAT: Build Pipeline with scaler + model. HOW MANY: 1. WHERE: notebook.",
        ),
    ]
    ml_topics = []
    for i, (slug, name, prereqs, obj, url, provider, practice) in enumerate(ml_specs):
        ml_topics.append(
            topic(
                slug,
                name,
                i,
                prereqs,
                obj,
                url,
                provider,
                practice,
                domain="ml",
                depth="WORKING_KNOWLEDGE" if i < 4 else "STRONG",
                build=f"IMPLEMENT: notebook cell for {name}." if i >= 3 else None,
            )
        )
    ml = manifest(
        "domain-ml",
        "Machine Learning Foundations",
        6,
        "ml-foundations",
        "Machine Learning Foundations",
        [module("mod-ml-core", "Supervised learning path", 0, ml_topics)],
    )

    shell_domains = [
        (
            "dl",
            "Deep Learning",
            "deep-learning",
            "https://www.deeplearningbook.org/",
            "Deep Learning Book",
            "Neural nets stack differentiable layers to learn representations.",
        ),
        (
            "nlp",
            "NLP",
            "nlp",
            "https://huggingface.co/learn/nlp-course/chapter1/1",
            "Hugging Face",
            "NLP turns text into tokens and models meaning.",
        ),
        (
            "genai",
            "Generative AI",
            "genai",
            "https://platform.openai.com/docs/guides/text",
            "OpenAI Docs",
            "Generative models produce text/images from prompts and training data.",
        ),
        (
            "ai-eng",
            "AI Engineering",
            "ai-engineering",
            "https://www.deeplearning.ai/short-courses/",
            "DeepLearning.AI",
            "AI engineering ships reliable LLM features with evals and ops.",
        ),
        (
            "devops",
            "DevOps",
            "devops",
            "https://12factor.net/",
            "12-Factor",
            "DevOps connects build, release, run with automation and observability.",
        ),
        (
            "sysdesign",
            "System Design",
            "system-design",
            "https://github.com/donnemartin/system-design-primer",
            "System Design Primer",
            "System design trades latency, consistency, and cost at scale.",
        ),
    ]
    shell_modules = []
    for di, (key, title, domain, url, provider, idea) in enumerate(shell_domains):
        t1 = topic(
            f"{key}-awareness",
            f"{title} awareness",
            0,
            [],
            idea,
            url,
            provider,
            f"WHAT: Write a 5-bullet overview of {title}. HOW MANY: 1. WHERE: notes.",
            track="OPTIONAL",
            depth="AWARENESS",
            domain=domain,
            minutes=20,
        )
        t2 = topic(
            f"{key}-path",
            f"{title} learning path",
            1,
            [f"{key}-awareness"],
            f"Sketch a personal learning path into {title} after core ML/backend.",
            url,
            provider,
            f"WHAT: List 5 next resources for {title}. HOW MANY: 5. WHERE: notes.",
            track="OPTIONAL",
            depth="AWARENESS",
            domain=domain,
            minutes=20,
        )
        shell_modules.append(module(f"mod-{key}-shell", title, di, [t1, t2]))
    shells = manifest(
        "domain-shells",
        "Career Path Shells",
        7,
        "career-path-shells",
        "Later domains (awareness shells)",
        shell_modules,
    )

    files = {
        "software-engineering/03-software-engineering-core.yaml": se,
        "backend/04-databases-and-backend.yaml": be,
        "mathematics/05-math-for-ml.yaml": math,
        "ml/06-machine-learning-foundations.yaml": ml,
        "shells/07-career-path-shells.yaml": shells,
    }
    for rel, data in files.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
        n = sum(
            len(m["topics"])
            for lvl in data["track"]["levels"]
            for s in lvl["subjects"]
            for m in s["modules"]
        )
        print(rel, "topics", n)

    idx = ROOT / "v1-index.yaml"
    index = yaml.safe_load(idx.read_text(encoding="utf-8"))
    for rel in files:
        if rel not in index["files"]:
            index["files"].append(rel)
    idx.write_text(yaml.safe_dump(index, sort_keys=False), encoding="utf-8")
    print("index", index["files"])


if __name__ == "__main__":
    main()
