# Question brief: Retrieval Quality (`mod-retrieval-quality`)

Subject: Deep Learning, GenAI, MLOps, System Design
Topics: 6

For each topic below, write at least 4 self-check questions in
`content/questions/mod-retrieval-quality.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `rag-reranking-cross-encoders` — Reranking with cross-encoders

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Add a reranking stage to a retrieval pipeline and explain the recall/precision division of labour.
- Context: The two-stage retrieve-and-rerank architecture - cheap bi-encoder recall, then expensive cross-encoder precision - and why a cross-encoder cannot be pre-indexed.
- Resources:
  - **PRIMARY** Sentence Transformers — Retrieve & Re-Rank
    https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html
  - **REFERENCE** Sentence Transformers — Cross-Encoders
    https://sbert.net/examples/cross_encoder/applications/README.html
- Currently has **no questions at all**.

## `rag-hybrid-search` — Hybrid search

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Fuse keyword and vector retrieval, and treat the fusion step as a formula rather than a magic dial.
- Context: Combining BM25 keyword scores with dense vector scores, including the fusion algorithms and the alpha weighting, plus reciprocal rank fusion stated as a formula.
- Resources:
  - **PRIMARY** Weaviate — Hybrid search
    https://docs.weaviate.io/weaviate/search/hybrid
  - **REFERENCE** Elastic — Reciprocal rank fusion
    https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion
- Currently has **no questions at all**.

## `rag-chunking-evaluation` — Evaluating chunking strategies

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Measure a chunking strategy instead of choosing one by convention.
- Context: A controlled experiment across chunking strategies with token-level recall and precision - a measurement method that replaces chunk sizes copied from tutorials.
- Resources:
  - **PRIMARY** Chroma — Evaluating Chunking Strategies for Retrieval
    https://www.trychroma.com/research/evaluating-chunking
- Currently has **no questions at all**.

## `rag-retrieval-metrics` — Ranked retrieval metrics

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Choose and compute the right ranked-retrieval metric for a RAG system.
- Context: Precision@k, recall@k, MAP and NDCG from the standard information-retrieval textbook - the metrics RAG evaluation keeps reinventing badly.
- Resources:
  - **PRIMARY** Stanford NLP (Introduction to Information Retrieval) — Evaluation of ranked retrieval results
    https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html
- Currently has **no questions at all**.

## `rag-ann-index-choice` — Choosing an ANN index

- Depth target: WORKING_KNOWLEDGE  ·  Track: SPECIALIZATION
- Objective: Pick an ANN index from dataset size, memory budget and recall target, and read a recall/QPS curve.
- Context: A decision tree over dataset size, memory budget and recall target - flat versus IVF versus HNSW versus product quantization - checked against objective measured recall/QPS data. Honest gap from the research: there is no vendor-neutral authoritative page comparing FAISS, Chroma, pgvector and managed services, so this topic teaches the index trade-off rather than a product comparison.
- Resources:
  - **PRIMARY** GitHub (facebookresearch/faiss wiki) — Guidelines to choose an index
    https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index
  - **REFERENCE** ann-benchmarks.com — ANN-Benchmarks
    https://ann-benchmarks.com/index.html
    exact part: FULL_SINGLE_PAGE — read the recall/QPS Pareto plots
- Currently has **no questions at all**.

## `rag-when-postgres-is-enough` — When Postgres is enough

- Depth target: WORKING_KNOWLEDGE  ·  Track: SPECIALIZATION
- Objective: Justify using, or not using, Postgres as the vector store for a given project.
- Context: pgvector as the honest default: if the data already lives in Postgres, a vector column plus an HNSW index removes a whole service from the architecture. Read it to be able to justify not adopting a vector database.
- Resources:
  - **PRIMARY** GitHub (pgvector/pgvector) — pgvector
    https://github.com/pgvector/pgvector
    exact part: README sections "Getting Started", "Storing", "Querying", "Indexing", "Filtering", "Hybrid Search", "Performance" (headings verified; skip the language bindings and installation notes)
- Currently has **no questions at all**.

