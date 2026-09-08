# Question brief: Data Quality for ML (`mod-ml-data-quality`)

Subject: Machine Learning Foundations
Topics: 5

For each topic below, write at least 4 self-check questions in
`content/questions/mod-ml-data-quality.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `dq-data-leakage` — Data leakage

- Depth target: DEEP  ·  Track: CORE
- Objective: Detect leakage in a training script and fix it by moving preprocessing inside the pipeline.
- Context: The most common cause of a model that scores well offline and fails in production, taught with wrong-code and right-code pairs, and the fix: fit transformers inside the cross-validation loop.
- Resources:
  - **PRIMARY** scikit-learn — Common pitfalls and recommended practices
    https://scikit-learn.org/stable/common_pitfalls.html
    exact part: §12.2 "Data leakage", including §12.2.1 "How to avoid data leakage" and §12.2.2 "Data leakage during pre-processing" (headings verified)
- Currently has **no questions at all**.

## `dq-inconsistent-preprocessing` — Inconsistent preprocessing

- Depth target: STRONG  ·  Track: CORE
- Objective: Guarantee that inference applies exactly the transforms training applied.
- Context: Train/serve skew: transforms applied at training and forgotten at inference, and the packaging discipline that removes the whole class of bug.
- Resources:
  - **PRIMARY** scikit-learn — Common pitfalls and recommended practices
    https://scikit-learn.org/stable/common_pitfalls.html
    exact part: §12.1 "Inconsistent preprocessing" (heading verified)
- Currently has **no questions at all**.

## `dq-missing-values` — Missing values and imputation

- Depth target: STRONG  ·  Track: CORE
- Objective: Choose an imputation strategy and apply it without leaking.
- Context: Univariate, multivariate and nearest-neighbour imputation, the missing-indicator column, and imputation inside a Pipeline so it does not leak.
- Resources:
  - **PRIMARY** scikit-learn — Imputation of missing values
    https://scikit-learn.org/stable/modules/impute.html
- Currently has **no questions at all**.

## `dq-outliers` — Outliers and novelty

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Decide which of the two problems you actually have before choosing a detection method.
- Context: The distinction that matters operationally: outlier detection on contaminated training data versus novelty detection with clean training data and dirty inference input.
- Resources:
  - **PRIMARY** scikit-learn — Novelty and Outlier Detection
    https://scikit-learn.org/stable/modules/outlier_detection.html
    exact part: The section intro plus "Overview of outlier detection methods" — the comparison figure is the payload; skip the per-estimator maths on a first pass
- Currently has **no questions at all**.

## `dq-class-imbalance` — Class imbalance

- Depth target: STRONG  ·  Track: CORE
- Objective: Handle an imbalanced dataset without destroying calibration or leaking through resampling.
- Context: Why accuracy is meaningless at 1:1000, downsampling with upweighting to keep calibration intact, and SMOTE's variants with the warning that resampling belongs inside the cross-validation fold.
- Resources:
  - **PRIMARY** Google for Developers — Datasets: Class-imbalanced datasets
    https://developers.google.com/machine-learning/crash-course/overfitting/imbalanced-datasets
  - **REFERENCE** imbalanced-learn — Over-sampling
    https://imbalanced-learn.org/stable/over_sampling.html
- Currently has **no questions at all**.

