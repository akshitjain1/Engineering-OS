# Question brief: AI/ML Security (`mod-ai-security`)

Subject: Deep Learning, GenAI, MLOps, System Design
Topics: 6

For each topic below, write at least 4 self-check questions in
`content/questions/mod-ai-security.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `aisec-owasp-llm-top-10` — OWASP Top 10 for LLM applications

- Depth target: AWARENESS  ·  Track: SPECIALIZATION
- Objective: Recognise and name the ten OWASP LLM risks in a design review.
- Context: The industry's shared vocabulary for LLM risk, read once as a map before going deep on the individual risks.
- Resources:
  - **PRIMARY** OWASP Gen AI Security Project — OWASP Top 10 for LLM Applications 2025
    https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
    exact part: FULL_SINGLE_PAGE (the ten risk summaries; the linked PDF is optional)
- Currently has **no questions at all**.

## `aisec-prompt-injection` — Prompt injection

- Depth target: DEEP  ·  Track: SPECIALIZATION
- Objective: Explain indirect prompt injection and state honestly what the available mitigations do and do not achieve.
- Context: Direct and indirect prompt injection, the mitigations that only partly work, and the published attacks against real LLM-integrated applications.
- Resources:
  - **PRIMARY** OWASP Gen AI Security Project — LLM01:2025 Prompt Injection
    https://genai.owasp.org/llmrisk/llm01-prompt-injection/
  - **REFERENCE** arXiv — Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection
    https://arxiv.org/abs/2302.12173
    exact part: Abstract, §1 Introduction, then the threat model and attack sections
- Currently has **no questions at all**.

## `aisec-data-exfiltration-tools` — Data exfiltration through tools

- Depth target: DEEP  ·  Track: SPECIALIZATION
- Objective: Audit a tool-using agent for the three legs of the exfiltration trifecta and remove one of them.
- Context: The lethal trifecta - private data, untrusted content and external communication - and the permission-minimisation controls that break it.
- Resources:
  - **PRIMARY** simonwillison.net — The lethal trifecta for AI agents: private data, untrusted content, and external communication
    https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
  - **REFERENCE** OWASP Gen AI Security Project — LLM06:2025 Excessive Agency
    https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- Currently has **no questions at all**.

## `aisec-improper-output-handling` — Improper output handling

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Treat model output as untrusted and place the right validation at each downstream consumer.
- Context: Model output as untrusted input to whatever consumes it - the path from "the LLM wrote some SQL" to XSS, SSRF and remote code execution.
- Resources:
  - **PRIMARY** OWASP Gen AI Security Project — LLM05:2025 Improper Output Handling
    https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/
- Currently has **no questions at all**.

## `aisec-model-supply-chain` — Model supply chain

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Load third-party model weights safely and explain the risk you are avoiding.
- Context: Why loading an untrusted pickle checkpoint is arbitrary code execution, how the Hub scans for it, and the format that is safe by construction.
- Resources:
  - **PRIMARY** Hugging Face — Pickle Scanning
    https://huggingface.co/docs/hub/security-pickle
  - **REFERENCE** Hugging Face — Safetensors
    https://huggingface.co/docs/safetensors/index
- Currently has **no questions at all**.

## `aisec-pii-and-disclosure` — PII and sensitive information disclosure

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Find the paths PII takes out of an LLM system and choose a de-identification technique per path.
- Context: How PII leaves an LLM system - through prompts, logs, embeddings, fine-tuning data and RAG corpora - and the de-identification techniques for each. Honest gap from the research: the obvious tool anchor (Microsoft Presidio) is orphaned and is deliberately not linked, so the reference is a vendor-hosted technique taxonomy; read it for the taxonomy, not the API. This is the weakest resource pairing in an otherwise strong module.
- Resources:
  - **PRIMARY** OWASP Gen AI Security Project — LLM02:2025 Sensitive Information Disclosure
    https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/
  - **REFERENCE** Google Cloud — De-identification | Sensitive Data Protection
    https://docs.cloud.google.com/sensitive-data-protection/docs/concepts-de-identification
- Currently has **no questions at all**.

