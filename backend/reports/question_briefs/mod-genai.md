# Question brief: Generative AI / LLM Engineering (`mod-genai`)

Subject: Deep Learning, GenAI, MLOps, System Design
Topics: 17

For each topic below, write at least 4 self-check questions in
`content/questions/mod-genai.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `genai-embeddings` — Embeddings & semantic search

- Depth target: DEEP  ·  Track: SPECIALIZATION
- Objective: Embed text and retrieve similar chunks.
- Resources:
  - **PRIMARY** OpenAI — Embeddings (~36 min)
    https://developers.openai.com/api/docs/guides/embeddings
    exact part: Embedding generation through semantic similarity
- Currently has 1 question(s), to be replaced:
  - Core idea of Embeddings & semantic search?  <- template filler

## `genai-rag` — RAG systems

- Depth target: DEEP  ·  Track: SPECIALIZATION
- Objective: Retrieve context and ground LLM answers.
- Resources:
  - **PRIMARY** Pinecone — Retrieval-Augmented Generation - the full pipeline (~14 min)
    https://www.pinecone.io/learn/retrieval-augmented-generation/
    exact part: Retrieval; Retrieval-augmented generation
- Currently has 1 question(s), to be replaced:
  - Core idea of RAG systems?  <- template filler

## `genai-agents` — Tool-using agents

- Depth target: DEEP  ·  Track: SPECIALIZATION
- Objective: Orchestrate tools with guarded agent loops.
- Resources:
  - **PRIMARY** OpenAI — OpenAI: Tool-using agents (~75 min)
    https://developers.openai.com/api/docs/guides/function-calling
    exact part: function-calling
- Currently has 1 question(s), to be replaced:
  - Core idea of Tool-using agents?  <- template filler

## `genai-eval` — LLM evaluation

- Depth target: DEEP  ·  Track: SPECIALIZATION
- Objective: Evaluate answer quality with explicit rubrics.
- Resources:
  - **PRIMARY** OpenAI — OpenAI Evals guide (~43 min)
    https://developers.openai.com/api/docs/guides/evals
    exact part: Evals
- Currently has 1 question(s), to be replaced:
  - Core idea of LLM evaluation?  <- template filler

## `genai-what-is-lm` — What is a language model?

- Depth target: INTUITION  ·  Track: CORE
- Objective: Probability distribution over next tokens; sampling makes it generative
- Context: Probability distribution over next tokens; sampling makes it generative.
- Resources:
  - **PRIMARY** Vizuara — Transformers Explained: Overview (~10 min)
    https://www.youtube.com/watch?v=FVcUKMu_M5Q
  - **PRIMARY** Hugging Face — Introduction to NLP and Language Models (~19 min)
    https://huggingface.co/learn/llm-course/chapter1/1
    exact part: Introduction through NLP/LLM basics
- Currently has **no questions at all**.

## `genai-next-token-prediction` — Next-token prediction

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Train loop of masking/predicting; emergent capability framing
- Context: Train loop of masking/predicting; emergent capability framing.
- Resources:
  - **PRIMARY** D2L.ai — Language Modeling (~19 min)
    https://d2l.ai/chapter_recurrent-neural-networks/language-model.html
    exact part: Pretraining objective through next-token prediction
- Currently has **no questions at all**.

## `genai-tokenization-llm` — LLM tokenization

- Depth target: MECHANICS  ·  Track: CORE
- Objective: BPE subwords in production LLMs; cost/context implications of token counts
- Context: BPE subwords in production LLMs; cost/context implications of token counts.
- Resources:
  - **PRIMARY** Hugging Face — Tokenization for LLMs (~14 min)
    https://huggingface.co/learn/llm-course/chapter2/2
  - **REFERENCE** Vizuara — Vizuara — Positional Encoding (~10 min)
    https://www.youtube.com/watch?v=7CNElr-TAQw
- Currently has **no questions at all**.

## `genai-pretraining-finetuning` — Pretraining → fine-tuning pipeline

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Stages from base model to usable assistant; data mixes at each stage
- Context: Stages from base model to usable assistant; data mixes at each stage.
- Resources:
  - **PRIMARY** Hugging Face LLM Course — Introduction to fine-tuning (~25 min)
    https://huggingface.co/learn/llm-course/chapter3/1
    exact part: Introduction through fine-tuning
- Currently has **no questions at all**.

## `genai-instruction-tuning-rlhf` — Instruction tuning & RLHF awareness

- Depth target: AWARENESS  ·  Track: CORE
- Objective: SFT then preference optimization; alignment vs capability distinction
- Context: SFT then preference optimization; alignment vs capability distinction.
- Resources:
  - **PRIMARY** Hugging Face LLM Course — Instruction tuning and alignment (~25 min)
    https://huggingface.co/learn/llm-course/chapter11/1
    exact part: Supervised Fine-Tuning through Evaluation
- Currently has **no questions at all**.

## `genai-inference-parameters` — Inference parameters

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Temperature/top-k/top-p steering; determinism vs creativity dial
- Context: Temperature/top-k/top-p steering; determinism vs creativity dial.
- Resources:
  - **PRIMARY** Prompt Engineering Guide — Chat completion parameters (~11 min)
    https://www.promptingguide.ai/introduction/settings
- Currently has **no questions at all**.

## `genai-context-windows` — Context windows

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Finite attention span economics; truncation strategies
- Context: Finite attention span economics; truncation strategies.
- Resources:
  - **PRIMARY** Anthropic — Context Windows (~18 min)
    https://platform.claude.com/docs/en/build-with-claude/context-windows
    exact part: context-window explanation
- Currently has **no questions at all**.

## `genai-prompt-engineering` — Prompt engineering

- Depth target: APPLICATION  ·  Track: CORE
- Objective: Role/format/examples patterns; iteration discipline and eval harnesses
- Context: Role/format/examples patterns; iteration discipline and eval harnesses.
- Resources:
  - **PRIMARY** Prompt Engineering Guide — Prompt engineering guide (~13 min)
    https://www.promptingguide.ai/introduction/tips
- Currently has **no questions at all**.

## `genai-vector-databases` — Vector databases

- Depth target: MECHANICS  ·  Track: CORE
- Objective: ANN indexes trade recall/latency; persistence and filtering basics
- Context: ANN indexes trade recall/latency; persistence and filtering basics.
- Resources:
  - **PRIMARY** Pinecone — What is a Vector Database? (~28 min)
    https://www.pinecone.io/learn/vector-database/
  - **REFERENCE** OpenAI — Embeddings & similarity storage
    https://developers.openai.com/api/docs/guides/embeddings
- Currently has **no questions at all**.

## `genai-chunking-retrieval` — Chunking & retrieval

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Split documents semantically; embed chunks; rank and rerank
- Context: Split documents semantically; embed chunks; rank and rerank.
- Resources:
  - **PRIMARY** LangChain — Retrieval-augmented generation (~41 min)
    https://docs.langchain.com/oss/python/deepagents/rag
- Currently has **no questions at all**.

## `genai-hallucinations-guardrails` — Hallucinations & guardrails

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Why fluent ≠ factual; grounding, validation, refusal patterns
- Context: Why fluent ≠ factual; grounding, validation, refusal patterns.
- Resources:
  - **PRIMARY** Prompt Engineering Guide — Production best practices (~10 min)
    https://www.promptingguide.ai/risks
- Currently has **no questions at all**.

## `genai-lora-peft` — LoRA & parameter-efficient fine-tuning

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Train low-rank adapters instead of full weights; memory tradeoffs
- Context: Train low-rank adapters instead of full weights; memory tradeoffs.
- Resources:
  - **PRIMARY** Hugging Face — PEFT and LoRA (~10 min)
    https://huggingface.co/docs/peft/en/index
    exact part: LoRA through parameter-efficient fine-tuning
- Currently has **no questions at all**.

## `genai-production-serving` — LLM serving economics

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Latency/throughput levers, KV-cache reuse, cost per token, autoscaling
- Context: Latency/throughput levers, KV-cache reuse, cost per token, autoscaling.
- Resources:
  - **PRIMARY** vLLM — vLLM (~10 min)
    https://docs.vllm.ai/en/latest/
    exact part: introduction through serving architecture
- Currently has **no questions at all**.

