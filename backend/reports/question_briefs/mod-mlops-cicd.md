# Question brief: CI/CD for ML (`mod-mlops-cicd`)

Subject: DevOps and Platform Engineering
Topics: 5

For each topic below, write at least 4 self-check questions in
`content/questions/mod-mlops-cicd.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `mlcicd-cd4ml` — Continuous delivery for ML

- Depth target: STRONG  ·  Track: CORE
- Objective: Describe an end-to-end CD4ML pipeline and place a team on the MLOps maturity ladder.
- Context: Why CI/CD for ML is not CI with a training step bolted on: an ML system has three versioned artifacts - code, data and model - plus the MLOps maturity ladder for placing any team you join.
- Resources:
  - **PRIMARY** martinfowler.com — Continuous Delivery for Machine Learning
    https://martinfowler.com/articles/cd4ml.html
    exact part: FULL_SINGLE_PAGE (long; the "Technical Components of CD4ML" walkthrough is the core)
  - **REFERENCE** Google Cloud — MLOps: Continuous delivery and automation pipelines in machine learning
    https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
    exact part: The "MLOps level 0 / level 1 / level 2" ladder
- Currently has **no questions at all**.

## `mlcicd-testing-ml-systems` — Testing ML systems

- Depth target: DEEP  ·  Track: CORE
- Objective: Write ML tests that run in CI and say what each one would catch.
- Context: The distinction that makes ML testable at all: pre-train tests (shape, leakage, label distribution - runnable in CI without a GPU) versus post-train behavioural tests (invariance, directional expectation, minimum functionality).
- Resources:
  - **PRIMARY** jeremyjordan.me — Effective testing for machine learning systems
    https://www.jeremyjordan.me/testing-ml/
  - **REFERENCE** Made With ML — Testing Machine Learning Systems: Code, Data and Models
    https://madewithml.com/courses/mlops/testing/
- Currently has **no questions at all**.

## `mlcicd-production-readiness` — Production readiness scoring

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Score an ML system against the ML Test Score rubric and name its lowest-scoring section.
- Context: A 28-item rubric across features/data, model development, infrastructure and monitoring, used as a literal pre-launch checklist.
- Resources:
  - **PRIMARY** Google Research (served from storage.googleapis.com) — The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction
    https://storage.googleapis.com/gweb-research2023-media/pubtools/4156.pdf
    exact part: FULL_SINGLE_PAGE (PDF, 8 pp.) — the 28 tests are the payload, the scoring rubric at the end is what you actually use
  - **REFERENCE** Google Research — The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction
    https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/
- Currently has **no questions at all**.

## `mlcicd-training-in-ci` — Training in CI

- Depth target: STRONG  ·  Track: CORE
- Objective: Add a CI job that trains on a branch and reports metrics back into the pull request.
- Context: Turning CI from "run the tests" into "train the model on this branch and post the metrics and plots as a PR comment", so model changes get reviewed like code changes - plus self-hosted GPU runners for when the job outgrows a hosted runner.
- Resources:
  - **PRIMARY** CML (Iterative) — Get Started with CML on GitHub
    https://cml.dev/doc/start/github
  - **REFERENCE** GitHub (iterative/cml) — CML - Continuous Machine Learning | CI/CD for ML
    https://github.com/iterative/cml
    exact part: Rendered README
- Currently has **no questions at all**.

## `mlcicd-model-registry` — Model registry and versioning

- Depth target: STRONG  ·  Track: CORE
- Objective: Promote a model to production as a recorded, reversible decision rather than a file copy.
- Context: Registered models, versions, aliases and tags as the deployment gate, plus the git-native alternative of versioning datasets and model files alongside code.
- Resources:
  - **PRIMARY** MLflow — ML Model Registry
    https://mlflow.org/docs/latest/ml/model-registry/
  - **REFERENCE** DVC — Versioning Data and Models
    https://doc.dvc.org/example-scenarios/versioning-data-and-models
- Currently has **no questions at all**.

