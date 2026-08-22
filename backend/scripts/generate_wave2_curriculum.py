"""Generate wave-2+ curriculum expansions: Web, Networking, DevOps, Data Science, DL, GenAI, MLOps, SysDesign."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1] / "content" / "curriculum"


def topic(
    slug,
    name,
    order,
    prereqs,
    objective,
    url,
    provider,
    practice,
    *,
    track="CORE",
    depth="WORKING_KNOWLEDGE",
    domain="web",
    minutes=45,
    practice_dest="OFFICIAL_EXERCISE",
    practice_qty=3,
    practice_url=None,
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
            "description": f"TRUSTED primary docs for {name}. Content inspection pending upgrade to VERIFIED_COVERAGE.",
        }
    ]
    exercises = [
        {
            "slug": f"{slug}-practice",
            "title": f"Practice: {name}",
            "type": "ACTION_CHECKLIST",
            "instructions": practice,
            "difficulty": "beginner",
            "order": 0,
        }
    ]
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
    answer = (objective[:80] + "...") if len(objective) > 80 else objective
    return {
        "slug": slug,
        "name": name,
        "description": objective,
        "order": order,
        "prerequisites": prereqs,
        "learning_objective": objective,
        "mastery_criteria": [f"Explain {name}.", "Complete mapped practice with stated quantity."],
        "fast_trackable": True,
        "learning_track": track,
        "depth_target": depth,
        "parallel_eligible": track in {"ALWAYS_ON", "OPTIONAL"},
        "estimated_minutes": minutes,
        "domain_key": domain,
        "lessons": [
            {
                "slug": f"{slug}-core",
                "title": name,
                "description": (
                    f"WHY NOW: {objective}\n\n"
                    f"LEARN: {provider} — {url}\n"
                    f"TIME: ~{minutes} minutes (MEDIUM confidence until measured).\n"
                    f"PRACTICE: {practice}\n"
                    f"DESTINATION: {practice_dest}"
                    + (f" ({practice_url})" if practice_url else "")
                    + f"\nQUANTITY: {practice_qty}\n"
                    + (f"BUILD: {build}\n" if build else "")
                    + "DONE WHEN: You can explain the focus concepts without notes and finish the practice quantity."
                ),
                "order": 0,
                "hours_estimated": round(minutes / 60, 2),
                "resources": resources,
                "questions": [
                    {
                        "slug": f"{slug}-q1",
                        "prompt": f"Core idea of {name}?",
                        "options": [
                            "A vague buzzword",
                            answer,
                            "Irrelevant outside interviews",
                            "Replaces prerequisites",
                        ],
                        "answer": answer,
                        "explanation": "Match the learning objective.",
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
            "description": "Complete engineering learning map.",
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
                            "order": 0,
                            "modules": modules,
                        }
                    ],
                }
            ],
        },
    }


def build_web():
    specs = [
        ("web-html-basics", "HTML basics", [], "Structure documents with semantic HTML elements.", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content", "MDN", "WHAT: Build a 1-page semantic HTML outline (header/nav/main/footer). HOW MANY: 1 page. WHERE: local IDE.", "web", "WORKING_KNOWLEDGE"),
        ("web-css-basics", "CSS basics", ["web-html-basics"], "Style layouts with CSS selectors, box model, and flexbox.", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics", "MDN", "WHAT: Style the HTML page with flexbox layout. HOW MANY: 1 stylesheet. WHERE: local IDE.", "web", "WORKING_KNOWLEDGE"),
        ("web-responsive", "Responsive design", ["web-css-basics"], "Make layouts adapt across viewports with media queries.", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design", "MDN", "WHAT: Add 2 breakpoints to your page. HOW MANY: 2. WHERE: local IDE.", "web", "WORKING_KNOWLEDGE"),
        ("web-js-basics", "JavaScript basics", ["web-html-basics"], "Use JS variables, functions, DOM events for interactive pages.", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting", "MDN", "WHAT: Add 3 DOM event handlers. HOW MANY: 3. WHERE: local IDE.", "web", "WORKING_KNOWLEDGE"),
        ("web-ts-intro", "TypeScript intro", ["web-js-basics"], "Add static types to JavaScript modules.", "https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html", "TypeScript", "WHAT: Convert 1 JS module to TS with types. HOW MANY: 1. WHERE: local IDE.", "web", "WORKING_KNOWLEDGE"),
        ("web-react-intro", "React intro", ["web-js-basics"], "Build UI with components, props, and state.", "https://react.dev/learn", "React", "WHAT: Build a counter + list component. HOW MANY: 2 components. WHERE: local IDE.", "web", "WORKING_KNOWLEDGE"),
        ("web-nextjs-intro", "Next.js intro", ["web-react-intro"], "Create a Next.js app with routing and data fetching.", "https://nextjs.org/docs/app/getting-started", "Next.js", "WHAT: Create app router page + fetch. HOW MANY: 1 app. WHERE: local IDE.", "web", "WORKING_KNOWLEDGE"),
        ("web-forms-a11y", "Forms & accessibility", ["web-html-basics", "web-css-basics"], "Build accessible forms with labels and keyboard support.", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms", "MDN", "WHAT: Build a form with 4 labeled fields + validation. HOW MANY: 1. WHERE: local IDE.", "web", "WORKING_KNOWLEDGE"),
    ]
    topics = []
    for i, (slug, name, prereqs, obj, url, provider, practice, domain, depth) in enumerate(specs):
        topics.append(
            topic(
                slug,
                name,
                i,
                prereqs,
                obj,
                url,
                provider,
                practice,
                domain=domain,
                depth=depth,
                track="SPECIALIZATION",
                build=f"IMPLEMENT: small demo for {name}." if i % 2 == 1 else None,
                practice_dest="LOCAL_IDE",
                practice_qty=1,
            )
        )
    return manifest("domain-web", "Web Development", 8, "web-development", "Web Development", [
        module("mod-web-core", "Full-stack web foundations", 0, topics)
    ])


def build_networking():
    specs = [
        ("net-internet-basics", "Internet basics", [], "Explain how clients reach servers over the internet.", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/How_does_the_Internet_work", "MDN", "WHAT: Diagram client→DNS→server path. HOW MANY: 1 diagram. WHERE: notes."),
        ("net-dns", "DNS", ["net-internet-basics"], "Resolve hostnames to IP addresses.", "https://developer.mozilla.org/en-US/docs/Glossary/DNS", "MDN", "WHAT: Run dig/nslookup for 3 hosts. HOW MANY: 3. WHERE: terminal."),
        ("net-tcp-udp", "TCP vs UDP", ["net-internet-basics"], "Contrast reliable streams vs datagrams.", "https://developer.mozilla.org/en-US/docs/Glossary/TCP", "MDN", "WHAT: List 4 use-cases for TCP vs UDP. HOW MANY: 4. WHERE: notes."),
        ("net-http", "HTTP deep dive", ["net-internet-basics", "be-http"], "Use methods, headers, status codes, and caching headers correctly.", "https://developer.mozilla.org/en-US/docs/Web/HTTP", "MDN", "WHAT: Capture 5 requests in DevTools and label method/status. HOW MANY: 5. WHERE: browser."),
        ("net-https-tls", "HTTPS & TLS", ["net-http"], "Explain certificates and encrypted transport.", "https://developer.mozilla.org/en-US/docs/Glossary/TLS", "MDN", "WHAT: Inspect cert chain for 2 sites. HOW MANY: 2. WHERE: browser."),
        ("net-websockets", "WebSockets", ["net-http"], "Use persistent bidirectional channels when needed.", "https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API", "MDN", "WHAT: Sketch WS handshake vs HTTP polling. HOW MANY: 1. WHERE: notes."),
    ]
    topics = [
        topic(slug, name, i, prereqs, obj, url, provider, practice, domain="networking", depth="WORKING_KNOWLEDGE", track="SPECIALIZATION", practice_dest="LOCAL_IDE")
        for i, (slug, name, prereqs, obj, url, provider, practice) in enumerate(specs)
    ]
    return manifest("domain-networking", "Networking", 9, "networking", "Networking Foundations", [
        module("mod-net-core", "Network fundamentals", 0, topics)
    ])


def build_devops():
    specs = [
        ("ops-docker-intro", "Docker intro", ["cf-shell"], "Build and run containers from Dockerfiles.", "https://docs.docker.com/get-started/", "Docker", "WHAT: Build and run 1 image from a Dockerfile. HOW MANY: 1. WHERE: local Docker."),
        ("ops-compose", "Docker Compose", ["ops-docker-intro"], "Orchestrate multi-service local stacks.", "https://docs.docker.com/compose/", "Docker", "WHAT: Compose app + DB services. HOW MANY: 1 compose file. WHERE: local Docker."),
        ("ops-ci-github-actions", "GitHub Actions CI", ["se-ci-basics"], "Automate test/build on push.", "https://docs.github.com/en/actions", "GitHub", "WHAT: Write a workflow that runs tests. HOW MANY: 1 workflow. WHERE: GitHub."),
        ("ops-linux-services", "Linux services basics", ["cf-linux-processes"], "Manage long-running services and logs.", "https://man7.org/linux/man-pages/man1/systemctl.1.html", "man7", "WHAT: Inspect status/logs for 2 services. HOW MANY: 2. WHERE: Linux/WSL."),
        ("ops-k8s-awareness", "Kubernetes awareness", ["ops-docker-intro", "ops-compose"], "Explain pods, services, and deployments at awareness level.", "https://kubernetes.io/docs/concepts/overview/", "Kubernetes", "WHAT: Define pod vs deployment in 5 bullets. HOW MANY: 1. WHERE: notes.", "OPTIONAL", "AWARENESS"),
        ("ops-observability", "Observability basics", ["ops-docker-intro"], "Use logs, metrics, and traces for runtime insight.", "https://opentelemetry.io/docs/concepts/observability-primer/", "OpenTelemetry", "WHAT: Map logs/metrics/traces to a sample API. HOW MANY: 1. WHERE: notes."),
    ]
    topics = []
    for i, spec in enumerate(specs):
        slug, name, prereqs, obj, url, provider, practice, *rest = spec
        track = rest[0] if rest else "SPECIALIZATION"
        depth = rest[1] if len(rest) > 1 else "WORKING_KNOWLEDGE"
        topics.append(topic(slug, name, i, prereqs, obj, url, provider, practice, domain="devops", depth=depth, track=track, practice_dest="LOCAL_IDE", build=f"IMPLEMENT: {name} demo." if "docker" in slug else None))
    return manifest("domain-devops", "DevOps & Platform", 10, "devops-platform", "DevOps and Platform Engineering", [
        module("mod-ops-core", "Containers and delivery", 0, topics)
    ])


def build_datascience():
    specs = [
        ("ds-numpy", "NumPy foundations", ["math-vectors", "python-ready"], "Manipulate arrays with NumPy.", "https://numpy.org/doc/stable/user/absolute_beginners.html", "NumPy", "WHAT: Create arrays and compute mean/std for 2 datasets. HOW MANY: 2. WHERE: notebook."),
        ("ds-pandas", "Pandas foundations", ["ds-numpy"], "Load and transform tabular data with Pandas.", "https://pandas.pydata.org/docs/getting_started/intro_tutorials/", "Pandas", "WHAT: Load CSV, filter, groupby. HOW MANY: 3 ops. WHERE: notebook."),
        ("ds-eda", "Exploratory data analysis", ["ds-pandas", "math-stats-summary"], "Explore distributions and relationships before modeling.", "https://pandas.pydata.org/docs/user_guide/visualization.html", "Pandas", "WHAT: Produce 3 EDA plots + written findings. HOW MANY: 3. WHERE: notebook."),
        ("ds-feature-eng", "Feature engineering", ["ds-eda"], "Create usable features without leakage.", "https://scikit-learn.org/stable/modules/preprocessing.html", "scikit-learn", "WHAT: Build 3 feature transforms in a Pipeline. HOW MANY: 3. WHERE: notebook."),
        ("ds-sql-analytics", "SQL for analytics", ["db-sql-select", "ds-pandas"], "Answer analytical questions with SQL aggregations.", "https://www.postgresql.org/docs/current/tutorial-agg.html", "PostgreSQL", "WHAT: Write 5 aggregate queries. HOW MANY: 5. WHERE: SQL."),
    ]
    # python-ready is a soft prereq alias — use math-vectors only if python track not present
    fixed = []
    for i, (slug, name, prereqs, obj, url, provider, practice) in enumerate(specs):
        prereqs = [p for p in prereqs if p != "python-ready"]
        fixed.append(topic(slug, name, i, prereqs, obj, url, provider, practice, domain="data-science", depth="WORKING_KNOWLEDGE", track="SPECIALIZATION", practice_dest="LOCAL_IDE", build="IMPLEMENT: notebook section." if i > 0 else None))
    return manifest("domain-datascience", "Data Science", 11, "data-science", "Data Science Path", [
        module("mod-ds-core", "Scientific Python path", 0, fixed)
    ])


def build_dl_genai_mlops_sys():
    dl = [
        ("dl-nn-basics", "Neural network basics", ["ml-sklearn-pipeline", "math-gradient-intuition"], "Explain layers, activations, and forward pass.", "https://pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html", "PyTorch", "WHAT: Build a tiny MLP in PyTorch. HOW MANY: 1 model. WHERE: notebook."),
        ("dl-backprop", "Backpropagation intuition", ["dl-nn-basics"], "Relate loss gradients to parameter updates.", "https://pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html", "PyTorch", "WHAT: Print grads for 3 parameters. HOW MANY: 3. WHERE: notebook."),
        ("dl-cnn", "CNN basics", ["dl-nn-basics"], "Use convolutions for spatial data.", "https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html", "PyTorch", "WHAT: Train CNN for 1 epoch on toy images. HOW MANY: 1. WHERE: notebook."),
        ("dl-transformers-intro", "Transformers intro", ["dl-nn-basics"], "Explain attention and transformer blocks at working level.", "https://huggingface.co/learn/nlp-course/chapter1/4", "Hugging Face", "WHAT: Summarize attention in 8 bullets. HOW MANY: 1. WHERE: notes."),
    ]
    gen = [
        ("genai-embeddings", "Embeddings & semantic search", ["dl-transformers-intro"], "Embed text and retrieve similar chunks.", "https://platform.openai.com/docs/guides/embeddings", "OpenAI", "WHAT: Embed 10 docs and retrieve top-3 for a query. HOW MANY: 1 demo. WHERE: notebook."),
        ("genai-rag", "RAG systems", ["genai-embeddings", "be-fastapi-intro"], "Retrieve context and ground LLM answers.", "https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/", "DeepLearning.AI", "WHAT: Build a mini RAG over 5 documents. HOW MANY: 1. WHERE: local repo."),
        ("genai-agents", "Tool-using agents", ["genai-rag"], "Orchestrate tools with guarded agent loops.", "https://platform.openai.com/docs/guides/function-calling", "OpenAI", "WHAT: Implement 2 tools + agent loop. HOW MANY: 1. WHERE: local repo."),
        ("genai-eval", "LLM evaluation", ["genai-rag"], "Evaluate answer quality with explicit rubrics.", "https://platform.openai.com/docs/guides/evaluation", "OpenAI", "WHAT: Score 10 answers with a rubric. HOW MANY: 10. WHERE: notebook."),
    ]
    mlops = [
        ("mlops-tracking", "Experiment tracking", ["ml-sklearn-pipeline"], "Track params/metrics/artifacts for experiments.", "https://mlflow.org/docs/latest/tracking.html", "MLflow", "WHAT: Log 3 runs with params+metrics. HOW MANY: 3. WHERE: local MLflow."),
        ("mlops-model-packaging", "Model packaging", ["mlops-tracking"], "Package models for reproducible serving.", "https://mlflow.org/docs/latest/model.html", "MLflow", "WHAT: Save/load one model flavor. HOW MANY: 1. WHERE: local."),
        ("mlops-serving", "Model serving APIs", ["mlops-model-packaging", "be-fastapi-intro"], "Serve predictions behind an HTTP API.", "https://fastapi.tiangolo.com/tutorial/first-steps/", "FastAPI", "WHAT: Serve /predict for a saved model. HOW MANY: 1 API. WHERE: local repo."),
        ("mlops-monitoring", "Model monitoring basics", ["mlops-serving"], "Watch for drift and quality regressions.", "https://www.evidentlyai.com/blog/ml-monitoring", "Evidently", "WHAT: List 5 monitoring signals for a model. HOW MANY: 1 checklist. WHERE: notes."),
    ]
    sysd = [
        ("sys-scalability", "Scalability basics", ["be-persistence", "db-indexes"], "Scale reads/writes with caching and partitioning ideas.", "https://github.com/donnemartin/system-design-primer#performance-vs-scalability", "System Design Primer", "WHAT: Design scale plan for a read-heavy API. HOW MANY: 1. WHERE: notes."),
        ("sys-caching", "Caching strategies", ["sys-scalability"], "Choose cache placement and invalidation.", "https://github.com/donnemartin/system-design-primer#cache", "System Design Primer", "WHAT: Compare CDN vs app cache vs DB cache. HOW MANY: 1 write-up. WHERE: notes."),
        ("sys-queues", "Message queues", ["sys-scalability"], "Decouple producers/consumers with queues.", "https://github.com/donnemartin/system-design-primer#asynchronous-processing-with-message-queues", "System Design Primer", "WHAT: Sketch queue for email jobs. HOW MANY: 1. WHERE: notes."),
        ("sys-observability-design", "Observability in design", ["ops-observability", "sys-scalability"], "Design for debuggability at scale.", "https://sre.google/sre-book/monitoring-distributed-systems/", "Google SRE", "WHAT: Define SLIs/SLOs for an API. HOW MANY: 3 SLIs. WHERE: notes."),
    ]

    def pack(specs, domain, depth="STRONG", track="SPECIALIZATION"):
        return [
            topic(slug, name, i, prereqs, obj, url, provider, practice, domain=domain, depth=depth, track=track, practice_dest="LOCAL_IDE", build="IMPLEMENT: runnable demo." if i % 2 == 0 else None)
            for i, (slug, name, prereqs, obj, url, provider, practice) in enumerate(specs)
        ]

    return manifest(
        "domain-ai-systems",
        "AI Systems & Design",
        12,
        "ai-systems-design",
        "Deep Learning, GenAI, MLOps, System Design",
        [
            module("mod-dl", "Deep Learning", 0, pack(dl, "deep-learning", "DEEP", "SPECIALIZATION")),
            module("mod-genai", "Generative AI / LLM Engineering", 1, pack(gen, "genai", "DEEP", "SPECIALIZATION")),
            module("mod-mlops", "MLOps / AI Engineering", 2, pack(mlops, "mlops", "STRONG", "SPECIALIZATION")),
            module("mod-sysdesign", "System Design", 3, pack(sysd, "system-design", "STRONG", "SPECIALIZATION")),
        ],
    )


def build_python_track():
    specs = [
        ("py-syntax", "Python syntax & tooling", ["cf-command-line"], "Write and run Python scripts with venv and pip.", "https://docs.python.org/3/tutorial/index.html", "Python Docs", "WHAT: Create venv, install one package, run a script. HOW MANY: 1. WHERE: local IDE."),
        ("py-data-structures", "Python data structures", ["py-syntax"], "Use lists, dicts, sets, and comprehensions fluently.", "https://docs.python.org/3/tutorial/datastructures.html", "Python Docs", "WHAT: Solve 5 small structure drills. HOW MANY: 5. WHERE: local IDE."),
        ("py-functions-modules", "Functions & modules", ["py-data-structures"], "Organize code into functions and importable modules.", "https://docs.python.org/3/tutorial/modules.html", "Python Docs", "WHAT: Split a script into 2 modules. HOW MANY: 1. WHERE: local IDE."),
        ("py-oop", "Python OOP", ["py-functions-modules"], "Model problems with classes and composition.", "https://docs.python.org/3/tutorial/classes.html", "Python Docs", "WHAT: Implement 2 classes with composition. HOW MANY: 1 mini design. WHERE: local IDE."),
        ("py-testing", "pytest for Python", ["py-functions-modules", "se-unit-tests"], "Write and run pytest unit tests.", "https://docs.pytest.org/en/stable/", "pytest", "WHAT: Write 5 pytest tests. HOW MANY: 5. WHERE: local IDE."),
    ]
    topics = [
        topic(slug, name, i, prereqs, obj, url, provider, practice, domain="python", depth="STRONG", track="CORE", practice_dest="LOCAL_IDE", build="IMPLEMENT: small Python utility." if i == 4 else None)
        for i, (slug, name, prereqs, obj, url, provider, practice) in enumerate(specs)
    ]
    return manifest("domain-python", "Python", 2, "python-programming", "Python for AI/ML", [
        module("mod-py-core", "Python core", 0, topics)
    ])


def main():
    files = {
        "python/08-python-core.yaml": build_python_track(),
        "web/09-web-development.yaml": build_web(),
        "networking/10-networking.yaml": build_networking(),
        "devops/11-devops-platform.yaml": build_devops(),
        "data-science/12-data-science.yaml": build_datascience(),
        "ai-systems/13-ai-systems-design.yaml": build_dl_genai_mlops_sys(),
    }
    for rel, data in files.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
        n = sum(len(m["topics"]) for lvl in data["track"]["levels"] for s in lvl["subjects"] for m in s["modules"])
        print(rel, n)

    idx_path = ROOT / "v1-index.yaml"
    index = yaml.safe_load(idx_path.read_text(encoding="utf-8"))
    for rel in files:
        if rel not in index["files"]:
            index["files"].append(rel)
    idx_path.write_text(yaml.safe_dump(index, sort_keys=False), encoding="utf-8")
    print("index", len(index["files"]), "files")


if __name__ == "__main__":
    main()
