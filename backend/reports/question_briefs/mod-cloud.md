# Question brief: Cloud for AI workloads (`mod-cloud`)

Subject: DevOps and Platform Engineering
Topics: 6

For each topic below, write at least 4 self-check questions in
`content/questions/mod-cloud.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `cloud-service-models` — Cloud service models

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Classify any cloud offering as IaaS, PaaS or SaaS and name what the provider takes responsibility for.
- Context: The vendor-neutral definitions of IaaS, PaaS and SaaS and the five essential characteristics of cloud computing.
- Resources:
  - **PRIMARY** NIST — The NIST Definition of Cloud Computing (SP 800-145)
    https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-145.pdf
    exact part: FULL_SINGLE_PAGE (7 pp., ~2 pp. of substance)
  - **REFERENCE** NIST — SP 800-145, The NIST Definition of Cloud Computing | CSRC
    https://csrc.nist.gov/pubs/sp/800/145/final
- Currently has **no questions at all**.

## `cloud-object-storage` — Object storage

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Explain how object storage differs from a filesystem and decide where ML artifacts belong.
- Context: Buckets, keys, regions, durability and storage classes - the mental model for where datasets, checkpoints and model artifacts live.
- Resources:
  - **PRIMARY** Amazon Web Services — What is Amazon S3?
    https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html
- Currently has **no questions at all**.

## `cloud-gpu-instances` — GPU instance types

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Turn a requirement like "one GPU with 24 GB" into a specific instance type.
- Context: Reading an accelerated-computing instance table on two clouds: family letters, GPU model, GPU count and GPU memory per row.
- Resources:
  - **PRIMARY** Amazon Web Services — Specifications for Amazon EC2 accelerated computing instances
    https://docs.aws.amazon.com/ec2/latest/instancetypes/ac.html
    exact part: FULL_SINGLE_PAGE — reference tables; skim, do not memorise. Goal: learn the family letters (P = training, G = inference/graphics) and read GPU count + GPU memory off a row
  - **REFERENCE** Google Cloud — GPU machine types
    https://docs.cloud.google.com/compute/docs/gpus
    exact part: FULL_SINGLE_PAGE (skim)
- Currently has **no questions at all**.

## `cloud-gpu-memory-sizing` — GPU memory sizing

- Depth target: STRONG  ·  Track: CORE
- Objective: Estimate the GPU memory a training or inference run needs and compare it to an instance's capacity.
- Context: Breaking GPU memory into weights, optimiser state, gradients and activations, with real measurements, so you can answer "will this fit?" before paying for the instance.
- Resources:
  - **PRIMARY** Hugging Face — GPU memory usage
    https://huggingface.co/docs/transformers/en/model_memory_anatomy
  - **REFERENCE** Hugging Face — Model memory estimator
    https://huggingface.co/docs/accelerate/en/usage_guides/model_size_estimator
- Currently has **no questions at all**.

## `cloud-managed-inference` — Managed inference endpoints

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Decide between a managed endpoint and self-hosted serving for a given workload.
- Context: What a managed real-time endpoint gives you (an endpoint, autoscaling, traffic variants for A/B) and what it costs you (always-on instances), at two very different ceremony levels.
- Resources:
  - **PRIMARY** Amazon SageMaker AI — Real-time inference
    https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html
  - **REFERENCE** Hugging Face — Inference Endpoints
    https://huggingface.co/docs/inference-endpoints/index
- Currently has **no questions at all**.

## `cloud-cost-control` — Cost control for GPU workloads

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Choose a purchasing and right-sizing strategy for a GPU workload from mechanisms rather than price lists.
- Context: Spot instances and interruption handling as the biggest lever on GPU cost, plus the vocabulary of cost discipline. Honest gap from the research: GPU prices move monthly and no authoritative vendor-neutral page states what an AI workload costs, so this topic teaches mechanisms rather than numbers.
- Resources:
  - **PRIMARY** Amazon Web Services — Spot Instances
    https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html
  - **REFERENCE** Amazon Web Services — Cost Optimization Pillar - AWS Well-Architected Framework
    https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html
    exact part: "Abstract" and "Introduction" only (headings verified) — the five-goals list is the whole takeaway
- Currently has **no questions at all**.

