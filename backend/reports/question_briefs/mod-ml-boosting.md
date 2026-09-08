# Question brief: Gradient Boosting in Practice (`mod-ml-boosting`)

Subject: Machine Learning Foundations
Topics: 5

For each topic below, write at least 4 self-check questions in
`content/questions/mod-ml-boosting.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `gbm-boosted-trees-theory` — Boosted trees theory

- Depth target: DEEP  ·  Track: CORE
- Objective: Derive the split-gain formula and explain what the regularisation terms control.
- Context: The regularised objective, the second-order (gradient plus Hessian) approximation and the split-gain formula - why XGBoost is not "just gradient boosting".
- Resources:
  - **PRIMARY** XGBoost — Introduction to Boosted Trees
    https://xgboost.readthedocs.io/en/stable/tutorials/model.html
  - **REFERENCE** StatQuest (YouTube) — Gradient Boost Part 1 (of 4): Regression Main Ideas
    https://www.youtube.com/watch?v=3CC4N4z3GJc
- Currently has **no questions at all**.

## `gbm-xgboost-tuning` — XGBoost tuning

- Depth target: STRONG  ·  Track: CORE
- Objective: Tune a boosted-tree model by choosing parameters that address a diagnosed problem.
- Context: The bias-variance dial for boosted trees stated as parameter groups - control overfitting, handle imbalance, speed up - so tuning stops being a random grid search.
- Resources:
  - **PRIMARY** XGBoost — Notes on Parameter Tuning
    https://xgboost.readthedocs.io/en/stable/tutorials/param_tuning.html
  - **REFERENCE** StatQuest (YouTube) — XGBoost Part 1 (of 4): Regression
    https://www.youtube.com/watch?v=OtD8wVaFm6E
- Currently has **no questions at all**.

## `gbm-lightgbm-mechanics` — LightGBM mechanics

- Depth target: STRONG  ·  Track: CORE
- Objective: Explain why LightGBM is fast and what its growth strategy costs you.
- Context: Histogram binning, leaf-wise growth and native categorical splits - the three ideas that make LightGBM the default on large tabular data - plus the overfitting warning that comes with leaf-wise growth.
- Resources:
  - **PRIMARY** LightGBM — Features
    https://lightgbm.readthedocs.io/en/stable/Features.html
    exact part: Sections "Optimization in Speed and Memory Usage", "Sparse Optimization", "Optimization in Accuracy", "Leaf-wise (Best-first) Tree Growth", "Optimal Split for Categorical Features" (headings verified; skip everything from "Optimization in Network Communication" onward)
  - **REFERENCE** LightGBM — Parameters Tuning
    https://lightgbm.readthedocs.io/en/stable/Parameters-Tuning.html
- Currently has **no questions at all**.

## `gbm-categorical-features` — Categorical features in tree models

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Encode a high-cardinality categorical column for a tree model without leaking the target.
- Context: Native categorical support and the partition-based split, plus ordered target statistics as the third approach - including exactly how target encoding leaks unless it is done ordered.
- Resources:
  - **PRIMARY** XGBoost — Categorical Data
    https://xgboost.readthedocs.io/en/stable/tutorials/categorical.html
  - **REFERENCE** CatBoost — Transforming categorical features to numerical features
    https://catboost.ai/docs/en/concepts/algorithm-main-stages_cat-to-numberic
- Currently has **no questions at all**.

## `gbm-tabular-vs-deep-learning` — Tabular data versus deep learning

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Argue from published evidence why to reach for boosted trees on tabular data.
- Context: The evidence-based answer to why boosted trees still win on typical tabular data: specific inductive biases, not a data-volume argument.
- Resources:
  - **PRIMARY** arXiv — Why do tree-based models still outperform deep learning on typical tabular data?
    https://arxiv.org/abs/2207.08815
    exact part: Abstract and Introduction first, then skim the empirical findings and figures — the three inductive-bias explanations are the payload. PDF at https://arxiv.org/pdf/2207.08815
- Currently has **no questions at all**.

