# Question brief: NLP Core (`mod-nlp-core`)

Subject: Deep Learning, GenAI, MLOps, System Design
Topics: 16

For each topic below, write at least 4 self-check questions in
`content/questions/mod-nlp-core.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `nlp-what-is-nlp` — What is NLP?

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Language tasks landscape; ambiguity as core difficulty
- Context: Language tasks landscape; ambiguity as core difficulty.
- Resources:
  - **PRIMARY** Hugging Face — Introduction to LLM/NLP course (~15 min)
    https://huggingface.co/learn/llm-course/chapter1/1
- Currently has **no questions at all**.

## `nlp-text-preprocessing` — Text preprocessing

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Clean/case/normalize pipelines; why aggressive cleaning can hurt deep models
- Context: Clean/case/normalize pipelines; why aggressive cleaning can hurt deep models.
- Resources:
  - **PRIMARY** NLTK — Text preprocessing (tokenizers intro) (~75 min)
    https://www.nltk.org/book/ch03.html
- Currently has **no questions at all**.

## `nlp-tokenization-nlp` — Tokenization

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Words vs subwords vs characters; vocabulary size/out-of-vocab tradeoffs
- Context: Words vs subwords vs characters; vocabulary size/out-of-vocab tradeoffs.
- Resources:
  - **PRIMARY** Hugging Face — Tokenizer algorithms deep dive (~15 min)
    https://huggingface.co/learn/llm-course/chapter2/4
- Currently has **no questions at all**.

## `nlp-vocabulary-bow` — Vocabulary & bag of words

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Count vectors lose order but baseline hard; sparsity implications
- Context: Count vectors lose order but baseline hard; sparsity implications.
- Resources:
  - **PRIMARY** scikit-learn — CountVectorizer and bag-of-words (~42 min)
    https://scikit-learn.org/stable/modules/feature_extraction.html
    exact part: CountVectorizer through bag-of-words
- Currently has **no questions at all**.

## `nlp-tf-idf` — TF-IDF

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Weight rarity; build a search-style similarity baseline
- Context: Weight rarity; build a search-style similarity baseline.
- Resources:
  - **PRIMARY** scikit-learn — TF-IDF (~42 min)
    https://scikit-learn.org/stable/modules/feature_extraction.html
    exact part: TF-IDF
- Currently has **no questions at all**.

## `nlp-word-embeddings` — Word embeddings

- Depth target: INTUITION  ·  Track: CORE
- Objective: Dense vectors encode similarity; geometry of meaning introduction
- Context: Dense vectors encode similarity; geometry of meaning introduction.
- Resources:
  - **PRIMARY** D2L.ai — Word embeddings era (~15 min)
    https://d2l.ai/chapter_natural-language-processing-pretraining/word2vec.html
- Currently has **no questions at all**.

## `nlp-word2vec` — Word2Vec

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Skip-gram/CBOW training intuition; analogies from vector arithmetic
- Context: Skip-gram/CBOW training intuition; analogies from vector arithmetic.
- Resources:
  - **PRIMARY** D2L.ai — Word2Vec/GloVe background (~13 min)
    https://d2l.ai/chapter_natural-language-processing-pretraining/word2vec-pretraining.html
    exact part: through Encoder-decoder prelude
- Currently has **no questions at all**.

## `nlp-sequence-modeling` — Sequence modeling

- Depth target: INTUITION  ·  Track: CORE
- Objective: Order matters: language modeling objective framing
- Context: Order matters: language modeling objective framing.
- Resources:
  - **PRIMARY** D2L.ai — Sequence modeling motivation (~25 min)
    https://d2l.ai/chapter_recurrent-neural-networks/sequence.html
- Currently has **no questions at all**.

## `nlp-rnn-lstm` — RNN/LSTM for text

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Recurrence over tokens; LSTM gating counters vanishing memory
- Context: Recurrence over tokens; LSTM gating counters vanishing memory.
- Resources:
  - **PRIMARY** D2L.ai — Recurrent architectures for text (~16 min)
    https://d2l.ai/chapter_recurrent-neural-networks/rnn.html
- Currently has **no questions at all**.

## `nlp-attention-nlp` — Attention for sequences

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Soft alignment fixes fixed-vector bottleneck; attention weights readable
- Context: Soft alignment fixes fixed-vector bottleneck; attention weights readable.
- Resources:
  - **PRIMARY** D2L.ai — Attention mechanisms (~19 min)
    https://d2l.ai/chapter_attention-mechanisms-and-transformers/bahdanau-attention.html
- Currently has **no questions at all**.

## `nlp-transformers-nlp` — Transformers in NLP

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Stacked self-attention processes tokens in parallel; positional encodings restore order
- Context: Stacked self-attention processes tokens in parallel; positional encodings restore order.
- Resources:
  - **PRIMARY** Vizuara — Transformers Explained: Overview (~20 min)
    https://www.youtube.com/watch?v=FVcUKMu_M5Q
  - **REFERENCE** D2L.ai — Main architectures: transformers (~34 min)
    https://d2l.ai/chapter_attention-mechanisms-and-transformers/transformer.html
- Currently has **no questions at all**.

## `nlp-bert` — BERT & encoders

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Masked LM pretraining; bidirectional context for understanding tasks
- Context: Masked LM pretraining; bidirectional context for understanding tasks.
- Resources:
  - **PRIMARY** D2L.ai — BERT family encoders (~24 min)
    https://d2l.ai/chapter_natural-language-processing-pretraining/bert.html
- Currently has **no questions at all**.

## `nlp-encoder-vs-decoder` — Encoder vs decoder

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Understanding vs generation architectures; when each fits
- Context: Understanding vs generation architectures; when each fits.
- Resources:
  - **PRIMARY** D2L.ai — Encoders vs decoders (~11 min)
    https://d2l.ai/chapter_recurrent-modern/encoder-decoder.html
- Currently has **no questions at all**.

## `nlp-generative-models` — Generative NLP models

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Autoregressive decoding; GPT-family lineage overview
- Context: Autoregressive decoding; GPT-family lineage overview.
- Resources:
  - **PRIMARY** Hugging Face — Causal language modeling (~31 min)
    https://huggingface.co/learn/llm-course/chapter7/1
    exact part: Causal language modeling through generative-model
- Currently has **no questions at all**.

## `nlp-fine-tuning-nlp` — Fine-tuning for NLP

- Depth target: APPLICATION  ·  Track: CORE
- Objective: Adapt pretrained checkpoints to tasks; head swap + light tuning recipe
- Context: Adapt pretrained checkpoints to tasks; head swap + light tuning recipe.
- Resources:
  - **PRIMARY** Hugging Face — Fine-tuning a pretrained model (~15 min)
    https://huggingface.co/learn/llm-course/chapter3/3
- Currently has **no questions at all**.

## `nlp-evaluation-nlp` — NLP evaluation

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Perplexity, BLEU/ROUGE limits, human eval necessity
- Context: Perplexity, BLEU/ROUGE limits, human eval necessity.
- Resources:
  - **PRIMARY** Hugging Face — Evaluate (~31 min)
    https://huggingface.co/docs/evaluate/index
- Currently has **no questions at all**.

