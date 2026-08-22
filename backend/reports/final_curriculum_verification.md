# Final Curriculum Verification

Generated: 2026-08-22T10:13:34.887430+00:00

## Scorecard

- TOTAL TOPICS: 316
- PARTIAL_COVERAGE: 6
- READY: 294
- RESOURCE_GAP: 16

## By domain

### foundations: 64/64 READY

### java: 49/52 READY
- PARTIAL_COVERAGE: 2
- RESOURCE_GAP: 1

### dsa: 102/106 READY
- PARTIAL_COVERAGE: 4

### software-engineering: 8/10 READY
- RESOURCE_GAP: 2

### backend: 11/12 READY
- RESOURCE_GAP: 1

### mathematics: 1/6 READY
- RESOURCE_GAP: 5

### python: 5/5 READY

### ml: 8/8 READY

### data-science: 4/5 READY
- RESOURCE_GAP: 1

### deep-learning: 3/6 READY
- RESOURCE_GAP: 3

### nlp: 2/2 READY

### genai: 6/6 READY

### ai-engineering: 2/2 READY

### mlops: 2/4 READY
- RESOURCE_GAP: 2

### web: 8/8 READY

### networking: 6/6 READY

### devops: 7/8 READY
- RESOURCE_GAP: 1

### system-design: 6/6 READY

## Topic detail (failures first)

### be-json — RESOURCE_GAP
- Topic: JSON APIs
- Reason: Missing required concepts: ['be-json-json-apis-in-your-own-words', 'be-json-serialize-request-response-bodies-and-validate-s']
- Resource: be-json-primary | https://www.json.org/json-en.html
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['be-json-json-apis-in-your-own-words', 'be-json-serialize-request-response-bodies-and-validate-s']
- Covered: []
- Practice status: PRACTICE_VERIFIED

### ds-sql-analytics — RESOURCE_GAP
- Topic: SQL for analytics
- Reason: Missing required concepts: ['ds-sql-analytics-answer-analytical-questions-with-sql-aggregation', 'ds-sql-analytics-sql-for-analytics']
- Resource: ds-sql-analytics-primary | https://www.postgresql.org/docs/current/tutorial-agg.html
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['ds-sql-analytics-answer-analytical-questions-with-sql-aggregation', 'ds-sql-analytics-sql-for-analytics']
- Covered: []
- Practice status: PRACTICE_VERIFIED

### dl-backprop — RESOURCE_GAP
- Topic: Backpropagation intuition
- Reason: Missing required concepts: ['dl-backprop-backpropagation-intuition', 'dl-backprop-relate-loss-gradients-to-parameter-updates']
- Resource: dl-backprop-primary | https://pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['dl-backprop-backpropagation-intuition', 'dl-backprop-relate-loss-gradients-to-parameter-updates']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### dl-cnn — RESOURCE_GAP
- Topic: CNN basics
- Reason: Missing required concepts: ['dl-cnn-cnn-basics', 'dl-cnn-use-convolutions-for-spatial-data']
- Resource: dl-cnn-primary | https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['dl-cnn-cnn-basics', 'dl-cnn-use-convolutions-for-spatial-data']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### dl-nn-basics — RESOURCE_GAP
- Topic: Neural network basics
- Reason: Missing required concepts: ['dl-nn-basics-explain-layers-activations-and-forward-pass', 'dl-nn-basics-neural-network-basics']
- Resource: dl-nn-basics-primary | https://pytorch.org/tutorials/beginner/basics/intro.html
- Resource status: NEEDS_REVIEW exactness=MULTI_TOPIC
- Missing concepts: ['dl-nn-basics-explain-layers-activations-and-forward-pass', 'dl-nn-basics-neural-network-basics']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### devops-path — RESOURCE_GAP
- Topic: DevOps learning path
- Reason: Missing required concepts: ['devops-path-devops-learning-path-in-your-own-words', 'devops-path-sketch-a-personal-learning-path-into-devops-afte']
- Resource: devops-path-primary | https://12factor.net/
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['devops-path-devops-learning-path-in-your-own-words', 'devops-path-sketch-a-personal-learning-path-into-devops-afte']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### dsa-call-stack — PARTIAL_COVERAGE
- Topic: Call stack
- Reason: Missing required concepts: ['dsa-call-stack-the-idea-without-notes-language-independent', 'dsa-call-stack-trace-frames-on-the-call-stack']
- Resource: dsa-call-stack-learn-exact | https://www.geeksforgeeks.org/stack-data-structure/
- Resource status: VERIFIED_COVERAGE exactness=EXACT
- Missing concepts: ['dsa-call-stack-the-idea-without-notes-language-independent', 'dsa-call-stack-trace-frames-on-the-call-stack']
- Covered: ['dsa-call-stack-in-java-without-copying', 'dsa-call-stack-recursion-on-paper-for-a-small-input']
- Practice status: PRACTICE_VERIFIED

### dsa-dp-state — PARTIAL_COVERAGE
- Topic: State definition
- Reason: Missing required concepts: ['dsa-dp-state-choose-a-dp-state-that-uniquely-describes-a-subp', 'dsa-dp-state-name-indices-parameters-for-a-novel-prompt']
- Resource: dsa-dp-state-learn-exact | https://www.geeksforgeeks.org/dynamic-programming/
- Resource status: VERIFIED_COVERAGE exactness=EXACT
- Missing concepts: ['dsa-dp-state-choose-a-dp-state-that-uniquely-describes-a-subp', 'dsa-dp-state-name-indices-parameters-for-a-novel-prompt']
- Covered: ['dsa-dp-state-document-state-transition-base-order-complexity', 'dsa-dp-state-in-java-without-copying']
- Practice status: PRACTICE_VERIFIED

### dsa-hash-map — PARTIAL_COVERAGE
- Topic: Hash map
- Reason: Missing required concepts: ['dsa-hash-map-the-core-idea-without-notes-language-independent', 'dsa-hash-map-the-pattern-in-java-without-copying-a-solution', 'dsa-hash-map-use-hashmap-for-expected-o-1-keyed-lookup-and-co']
- Resource: dsa-hash-map-learn-exact | https://www.geeksforgeeks.org/hashing-data-structure/
- Resource status: VERIFIED_COVERAGE exactness=EXACT
- Missing concepts: ['dsa-hash-map-the-core-idea-without-notes-language-independent', 'dsa-hash-map-the-pattern-in-java-without-copying-a-solution', 'dsa-hash-map-use-hashmap-for-expected-o-1-keyed-lookup-and-co']
- Covered: ['dsa-hash-map-the-c-equivalent-structure-at-a-high-level-where']
- Practice status: PRACTICE_VERIFIED

### dsa-monotonic-stack — PARTIAL_COVERAGE
- Topic: Monotonic stack
- Reason: Missing required concepts: ['dsa-monotonic-stack-maintain-an-increasing-or-decreasing-stack', 'dsa-monotonic-stack-the-idea-without-notes-language-independent']
- Resource: dsa-monotonic-stack-learn-exact | https://www.geeksforgeeks.org/stack-data-structure/
- Resource status: VERIFIED_COVERAGE exactness=EXACT
- Missing concepts: ['dsa-monotonic-stack-maintain-an-increasing-or-decreasing-stack', 'dsa-monotonic-stack-the-idea-without-notes-language-independent']
- Covered: ['dsa-monotonic-stack-dry-run-next-greater-element-with-a-monotonic-st', 'dsa-monotonic-stack-in-java-without-copying']
- Practice status: PRACTICE_VERIFIED

### java-api-hygiene — RESOURCE_GAP
- Topic: API hygiene
- Reason: Missing required concepts: ['java-api-hygiene-put-a-tiny-library-tests-in-a-maven-or-gradle-la', 'java-api-hygiene-refactor-one-bloated-method-name-things-clearly', 'java-api-hygiene-ship-a-small-tidy-java-project-packages-build-to']
- Resource: java-api-hygiene-reference | https://dev.java/learn/classes-objects/design-best-practices/
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['java-api-hygiene-put-a-tiny-library-tests-in-a-maven-or-gradle-la', 'java-api-hygiene-refactor-one-bloated-method-name-things-clearly', 'java-api-hygiene-ship-a-small-tidy-java-project-packages-build-to']
- Covered: []
- Practice status: PRACTICE_VERIFIED

### java-assertions — PARTIAL_COVERAGE
- Topic: Assertions
- Reason: Missing required concepts: ['java-assertions-assert-a-return-value-and-an-exception', 'java-assertions-use-junit-assertions-for-return-values-and-throw']
- Resource: java-assertions-primary | https://junit.org/junit5/docs/current/user-guide/
- Resource status: VERIFIED_COVERAGE exactness=EXACT
- Missing concepts: ['java-assertions-assert-a-return-value-and-an-exception', 'java-assertions-use-junit-assertions-for-return-values-and-throw']
- Covered: ['java-assertions-add-at-least-one-boundary-case']
- Practice status: PRACTICE_VERIFIED

### java-composition — PARTIAL_COVERAGE
- Topic: Composition
- Reason: Missing required concepts: ['java-composition-build-a-small-object-that-contains-another-objec', 'java-composition-model-has-a-relationships-with-composition-and-k']
- Resource: java-composition-reference | https://dev.java/learn/classes-objects/design-best-practices/
- Resource status: VERIFIED_COVERAGE exactness=EXACT
- Missing concepts: ['java-composition-build-a-small-object-that-contains-another-objec', 'java-composition-model-has-a-relationships-with-composition-and-k']
- Covered: ['java-composition-one-case-where-composition-beats-inheritance']
- Practice status: PRACTICE_VERIFIED

### math-gradient-intuition — RESOURCE_GAP
- Topic: Gradient intuition
- Reason: Missing required concepts: ['math-gradient-intuition-explain-gradient-as-direction-of-steepest-ascent', 'math-gradient-intuition-gradient-intuition-in-your-own-words']
- Resource: math-gradient-intuition-primary | https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['math-gradient-intuition-explain-gradient-as-direction-of-steepest-ascent', 'math-gradient-intuition-gradient-intuition-in-your-own-words']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### math-matrices — RESOURCE_GAP
- Topic: Matrices intuition
- Reason: Missing required concepts: ['math-matrices-matrices-intuition-in-your-own-words', 'math-matrices-multiply-small-matrices-and-interpret-as-linear']
- Resource: math-matrices-primary | https://www.khanacademy.org/math/linear-algebra/matrix-transformations
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['math-matrices-matrices-intuition-in-your-own-words', 'math-matrices-multiply-small-matrices-and-interpret-as-linear']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### math-probability — RESOURCE_GAP
- Topic: Probability basics
- Reason: Missing required concepts: ['math-probability-probability-basics-in-your-own-words', 'math-probability-use-probability-rules-for-independent-events-and']
- Resource: math-probability-primary | https://www.khanacademy.org/math/statistics-probability/probability-library
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['math-probability-probability-basics-in-your-own-words', 'math-probability-use-probability-rules-for-independent-events-and']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### math-stats-summary — RESOURCE_GAP
- Topic: Summary statistics
- Reason: Missing required concepts: ['math-stats-summary-compute-mean-variance-and-interpret-them', 'math-stats-summary-summary-statistics-in-your-own-words']
- Resource: math-stats-summary-primary | https://www.khanacademy.org/math/statistics-probability
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['math-stats-summary-compute-mean-variance-and-interpret-them', 'math-stats-summary-summary-statistics-in-your-own-words']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### math-vectors — RESOURCE_GAP
- Topic: Vectors intuition
- Reason: Missing required concepts: ['math-vectors-reason-about-vectors-as-lists-of-numbers-with-di', 'math-vectors-vectors-intuition-in-your-own-words']
- Resource: math-vectors-primary | https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['math-vectors-reason-about-vectors-as-lists-of-numbers-with-di', 'math-vectors-vectors-intuition-in-your-own-words']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### mlops-model-packaging — RESOURCE_GAP
- Topic: Model packaging
- Reason: Missing required concepts: ['mlops-model-packaging-model-packaging', 'mlops-model-packaging-package-models-for-reproducible-serving']
- Resource: mlops-model-packaging-primary | https://mlflow.org/docs/latest/model.html
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['mlops-model-packaging-model-packaging', 'mlops-model-packaging-package-models-for-reproducible-serving']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### mlops-tracking — RESOURCE_GAP
- Topic: Experiment tracking
- Reason: Missing required concepts: ['mlops-tracking-experiment-tracking', 'mlops-tracking-track-params-metrics-artifacts-for-experiments']
- Resource: mlops-tracking-primary | https://mlflow.org/docs/latest/tracking.html
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['mlops-tracking-experiment-tracking', 'mlops-tracking-track-params-metrics-artifacts-for-experiments']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### se-requirements — RESOURCE_GAP
- Topic: Requirements & scope
- Reason: Missing required concepts: ['se-requirements-requirements-scope-in-your-own-words', 'se-requirements-turn-a-vague-ask-into-testable-requirements-and']
- Resource: se-requirements-primary | https://www.ibm.com/think/topics/software-development-life-cycle
- Resource status: NEEDS_REVIEW exactness=EXACT
- Missing concepts: ['se-requirements-requirements-scope-in-your-own-words', 'se-requirements-turn-a-vague-ask-into-testable-requirements-and']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED

### se-solid-ocp — RESOURCE_GAP
- Topic: SOLID — Open/Closed
- Reason: Missing required concepts: ['se-solid-ocp-extend-behavior-without-rewriting-stable-cores', 'se-solid-ocp-solid-open-closed-in-your-own-words']
- Resource: se-solid-ocp-primary | https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design
- Resource status: NEEDS_REVIEW exactness=MULTI_TOPIC
- Missing concepts: ['se-solid-ocp-extend-behavior-without-rewriting-stable-cores', 'se-solid-ocp-solid-open-closed-in-your-own-words']
- Covered: []
- Practice status: NO_PRACTICE_REQUIRED
