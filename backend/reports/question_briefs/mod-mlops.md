# Question brief: MLOps / AI Engineering (`mod-mlops`)

Subject: Deep Learning, GenAI, MLOps, System Design
Topics: 14

For each topic below, write at least 4 self-check questions in
`content/questions/mod-mlops.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `mlops-tracking` — Experiment tracking

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Track params/metrics/artifacts for experiments.
- Resources:
  - **PRIMARY** MLflow — MLflow: Experiment tracking (~22 min)
    https://mlflow.org/docs/latest/ml/tracking/
    exact part: MLflow Tracking
- Currently has 1 question(s), to be replaced:
  - Core idea of Experiment tracking?  <- template filler

## `mlops-model-packaging` — Model packaging

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Package models for reproducible serving.
- Resources:
  - **PRIMARY** MLflow — MLflow: Model packaging (~68 min)
    https://mlflow.org/docs/latest/ml/model/
    exact part: MLflow Models
- Currently has 1 question(s), to be replaced:
  - Core idea of Model packaging?  <- template filler

## `mlops-serving` — Model serving APIs

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Serve predictions behind an HTTP API.
- Resources:
  - **PRIMARY** FastAPI — FastAPI: Model serving APIs (~18 min)
    https://fastapi.tiangolo.com/tutorial/first-steps/
    exact part: first-steps
- Currently has 1 question(s), to be replaced:
  - Core idea of Model serving APIs?  <- template filler

## `mlops-monitoring` — Model monitoring basics

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Watch for drift and quality regressions.
- Resources:
  - **PRIMARY** Evidently — Model monitoring overview (~40 min)
    https://www.evidentlyai.com/ml-in-production/model-monitoring
    exact part: Model monitoring
- Currently has 1 question(s), to be replaced:
  - Core idea of Model monitoring basics?  <- template filler

## `ai-eng-structured-output` — Structured output

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Schema-constrained generation; JSON modes and validation loops
- Context: Schema-constrained generation; JSON modes and validation loops.
- Resources:
  - **PRIMARY** OpenAI — Structured outputs (~20 min)
    https://developers.openai.com/api/docs/guides/structured-outputs
- Currently has **no questions at all**.

## `ai-eng-tool-calling` — Tool calling

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Model decides to invoke tools; request/response contract design
- Context: Model decides to invoke tools; request/response contract design.
- Resources:
  - **PRIMARY** OpenAI — Function calling (~25 min)
    https://developers.openai.com/api/docs/guides/function-calling
    exact part: tool/function-calling mechanics
- Currently has **no questions at all**.

## `ai-eng-function-calling` — Function calling patterns

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Typed signatures, error surfacing, idempotency for model-invoked functions
- Context: Typed signatures, error surfacing, idempotency for model-invoked functions.
- Resources:
  - **PRIMARY** Anthropic — Tool use implementation (~20 min)
    https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- Currently has **no questions at all**.

## `ai-eng-agent-loops` — Agent loops

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Observe→think→act cycles with termination conditions; runaway-cost guards
- Context: Observe→think→act cycles with termination conditions; runaway-cost guards.
- Resources:
  - **PRIMARY** Anthropic — Building effective agents (~30 min)
    https://www.anthropic.com/engineering/building-effective-agents
    exact part: agent definition through workflow loop
- Currently has **no questions at all**.

## `ai-eng-planning-memory` — Planning & memory

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Task decomposition strategies; short-term scratchpad vs long-term stores
- Context: Task decomposition strategies; short-term scratchpad vs long-term stores.
- Resources:
  - **PRIMARY** Anthropic — Building effective agents (~25 min)
    https://www.anthropic.com/engineering/building-effective-agents
    exact part: planning through memory
- Currently has **no questions at all**.

## `ai-eng-multi-agent-awareness` — Multi-agent awareness

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Role-specialized agents hand off work; coordination overhead honesty
- Context: Role-specialized agents hand off work; coordination overhead honesty.
- Resources:
  - **PRIMARY** Anthropic — Building effective agents (~20 min)
    https://www.anthropic.com/engineering/building-effective-agents
    exact part: multi-agent orchestration
- Currently has **no questions at all**.

## `ai-eng-observability-security` — Observability & security

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Tracing prompts/costs/latency; injection threats and permission scopes
- Context: Tracing prompts/costs/latency; injection threats and permission scopes.
- Resources:
  - **PRIMARY** Microsoft Learn — Microsoft Learn — Observability for Generative AI and agentic AI systems (~20 min)
    https://learn.microsoft.com/en-us/security/zero-trust/sfi/observability-ai-systems
  - **REFERENCE** OWASP — OWASP Top 10 for LLM Applications (~20 min)
    https://owasp.org/www-project-top-10-for-large-language-model-applications/
- Currently has **no questions at all**.

## `ai-eng-production-deployment` — Production deployment

- Depth target: APPLICATION  ·  Track: CORE
- Objective: Versioned prompts, eval gates in CI, rollback strategy, usage monitoring
- Context: Versioned prompts, eval gates in CI, rollback strategy, usage monitoring.
- Resources:
  - **PRIMARY** OpenAI — Production deployment checklist (~30 min)
    https://developers.openai.com/api/docs/guides/production-best-practices
- Currently has **no questions at all**.

## `mlops-experiment-lifecycle` — ML lifecycle & reproducibility

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Track params/metrics/artifacts so any run can be reproduced
- Context: Track params/metrics/artifacts so any run can be reproduced.
- Resources:
  - **PRIMARY** MLflow — MLflow Tracking (~20 min)
    https://mlflow.org/docs/latest/ml/tracking/
    exact part: experiment through metric tracking
- Currently has **no questions at all**.

## `mlops-drift-quality` — Drift & data quality

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Training/serving skew, input vs label drift, quality gates
- Context: Training/serving skew, input vs label drift, quality gates.
- Resources:
  - **PRIMARY** MLflow — MLflow Model Evaluation (~14 min)
    https://mlflow.org/docs/latest/ml/evaluation/
    exact part: evaluation
  - **SUPPLEMENT** Google — Rules of Machine Learning — training/serving skew
    https://developers.google.com/machine-learning/guides/rules-of-ml
    exact part: Training-Serving Skew
- Currently has **no questions at all**.

