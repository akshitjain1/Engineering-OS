# Question brief: Inference Performance (`mod-inference-perf`)

Subject: Deep Learning, GenAI, MLOps, System Design
Topics: 6

For each topic below, write at least 4 self-check questions in
`content/questions/mod-inference-perf.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `infra-quantization-concepts` — Quantization concepts

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Explain what a quantized weight stores and evaluate a new quantization method on its own terms.
- Context: What int8 and int4 actually store - scale, zero-point, per-channel versus per-tensor - where the accuracy goes, and the 4-bit path most people actually run.
- Resources:
  - **PRIMARY** Hugging Face — Quantization concepts
    https://huggingface.co/docs/transformers/en/quantization/concept_guide
  - **REFERENCE** Hugging Face — Bitsandbytes
    https://huggingface.co/docs/transformers/en/quantization/bitsandbytes
- Currently has **no questions at all**.

## `infra-ptq-gptq-awq` — Post-training quantization: GPTQ and AWQ

- Depth target: WORKING_KNOWLEDGE  ·  Track: SPECIALIZATION
- Objective: Choose between a GPTQ and an AWQ checkpoint and say what the calibration knobs mean.
- Context: Calibration-based post-training quantization and the salient-weight alternative - enough to pick the right pre-quantized checkpoint off the Hub, which is the realistic job.
- Resources:
  - **PRIMARY** Hugging Face — GPTQ
    https://huggingface.co/docs/transformers/en/quantization/gptq
  - **REFERENCE** Hugging Face — AWQ
    https://huggingface.co/docs/transformers/en/quantization/awq
- Currently has **no questions at all**.

## `infra-kv-cache` — The KV cache

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Explain what the KV cache stores, estimate its size, and name a strategy for when it exceeds memory.
- Context: Why generation is linear rather than quadratic per token, what the cache costs in memory, the strategies for when it does not fit, and the fragmentation problem that leads to paged attention.
- Resources:
  - **PRIMARY** Hugging Face — Cache strategies
    https://huggingface.co/docs/transformers/en/kv_cache
  - **REFERENCE** Hugging Face (Text Generation Inference) — PagedAttention
    https://huggingface.co/docs/text-generation-inference/en/conceptual/paged_attention
- Currently has **no questions at all**.

## `infra-continuous-batching` — Continuous batching

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Explain iteration-level batching and why it beats request-level batching for generation.
- Context: Static versus dynamic versus continuous (iteration-level) batching, with measured throughput, and the paged memory manager that makes it practical.
- Resources:
  - **PRIMARY** Anyscale — Achieve 23x LLM Inference Throughput & Reduce p50 Latency
    https://www.anyscale.com/blog/continuous-batching-llm-inference
  - **REFERENCE** vLLM — vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention
    https://vllm.ai/blog/2023-06-20-vllm
- Currently has **no questions at all**.

## `infra-latency-vs-throughput` — Latency versus throughput

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: State an inference SLO in the right metrics instead of saying "make it faster".
- Context: Time to first token, inter-token latency, tokens per second and requests per second defined precisely, and the trade-off batch size forces between latency and throughput.
- Resources:
  - **PRIMARY** NVIDIA — LLM Inference Benchmarking: Fundamental Concepts
    https://developer.nvidia.com/blog/llm-benchmarking-fundamental-concepts/
    exact part: FULL_SINGLE_PAGE — headings verified: "How LLM inference works" → "LLM inference metrics" → time to first token / end-to-end request latency / intertoken latency / tokens per second / requests per second → "Benchmarking parameters and best practices"
- Currently has **no questions at all**.

## `infra-memory-bound-decoding` — Memory-bound decoding

- Depth target: DEEP  ·  Track: SPECIALIZATION
- Objective: Argue from arithmetic why decoding is memory-bandwidth bound, and what that predicts about batching, quantization and CPU inference.
- Context: The arithmetic showing that decoding is memory-bandwidth bound rather than compute bound - the honest answer to "CPU versus GPU inference" - plus the concrete CPU-side quantization story. Honest gap from the research: the best treatment of this mechanism is a personal blog, because no vendor page does the arithmetic.
- Resources:
  - **PRIMARY** kipp.ly — Transformer Inference Arithmetic
    https://kipp.ly/p/transformer-inference-arithmetic
    exact part: FULL_SINGLE_PAGE — the "kv cache" and "capacity" sections carry the argument
  - **REFERENCE** ONNX Runtime — Quantize ONNX models
    https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html
    exact part: Sections "Quantization Overview", "Dynamic Quantization", "Data type selection", "Quantization on GPU" (headings verified)
- Currently has **no questions at all**.

