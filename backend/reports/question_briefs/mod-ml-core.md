# Question brief: Supervised learning path (`mod-ml-core`)

Subject: Machine Learning Foundations
Topics: 35

For each topic below, write at least 4 self-check questions in
`content/questions/mod-ml-core.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `ml-what-is-ml` — What is machine learning

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Distinguish supervised/unsupervised learning and typical tasks.
- Resources:
  - **PRIMARY** Vizuara — ML Teach by Doing - Introduction (~26 min)
    https://www.youtube.com/watch?v=ngiICHD5dVc
  - **REFERENCE** scikit-learn — Getting Started — scikit-learn (~14 min)
    https://scikit-learn.org/stable/getting_started.html
    exact part: Getting Started
- Currently has 1 question(s), to be replaced:
  - What is the core idea of What is machine learning?  <- template filler

## `ml-features-labels` — Features & labels

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Frame tabular problems with features X and label y.
- Resources:
  - **PRIMARY** scikit-learn — scikit-learn: Features & labels (~14 min)
    https://scikit-learn.org/stable/getting_started.html
- Currently has 1 question(s), to be replaced:
  - What is the core idea of Features & labels?  <- template filler

## `ml-train-test` — Train/test split

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Split data to estimate generalization, avoid leakage.
- Resources:
  - **PRIMARY** scikit-learn — scikit-learn: Train/test split (~42 min)
    https://scikit-learn.org/stable/modules/cross_validation.html
    exact part: cross_validation.html
- Currently has 1 question(s), to be replaced:
  - What is the core idea of Train/test split?  <- template filler

## `ml-linear-regression` — Linear regression

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Fit and interpret a linear regressor.
- Resources:
  - **PRIMARY** scikit-learn — scikit-learn: Linear regression (~60 min)
    https://scikit-learn.org/stable/modules/linear_model.html
    exact part: linear_model.html
- Currently has 1 question(s), to be replaced:
  - What is the core idea of Linear regression?  <- template filler

## `ml-classification` — Classification basics

- Depth target: STRONG  ·  Track: CORE
- Objective: Train a classifier and read a confusion matrix.
- Resources:
  - **PRIMARY** StatQuest with Josh Starmer — Decision and Classification Trees, Clearly Explained!!! (~30 min)
    https://www.youtube.com/watch?v=_L39rN6gz7Y
    exact part: 00:18
  - **REFERENCE** scikit-learn — scikit-learn: Classification basics
    https://scikit-learn.org/stable/modules/tree.html
- Currently has 1 question(s), to be replaced:
  - What is the core idea of Classification basics?  <- template filler

## `ml-metrics` — ML metrics

- Depth target: STRONG  ·  Track: CORE
- Objective: Choose accuracy/precision/recall/F1 appropriately.
- Resources:
  - **PRIMARY** scikit-learn — scikit-learn: ML metrics (~75 min)
    https://scikit-learn.org/stable/modules/model_evaluation.html
    exact part: model_evaluation.html
- Currently has 1 question(s), to be replaced:
  - What is the core idea of ML metrics?  <- template filler

## `ml-overfitting` — Overfitting & regularization

- Depth target: STRONG  ·  Track: CORE
- Objective: Detect overfitting and apply simple regularization.
- Resources:
  - **PRIMARY** scikit-learn — scikit-learn: Overfitting & regularization (~60 min)
    https://scikit-learn.org/stable/modules/linear_model.html#ridge-regression
    exact part: ridge-regression
- Currently has 1 question(s), to be replaced:
  - What is the core idea of Overfitting & regularization?  <- template filler

## `ml-sklearn-pipeline` — sklearn Pipeline

- Depth target: STRONG  ·  Track: CORE
- Objective: Compose preprocessing + model in a Pipeline.
- Resources:
  - **PRIMARY** scikit-learn — scikit-learn: sklearn Pipeline (~24 min)
    https://scikit-learn.org/stable/modules/compose.html
    exact part: compose.html
- Currently has 1 question(s), to be replaced:
  - What is the core idea of sklearn Pipeline?  <- template filler

## `ml-types-of-ml` — Types of machine learning

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Distinguish supervised, unsupervised, and reinforcement settings with one example each
- Context: Distinguish supervised, unsupervised, and reinforcement settings with one example each.
- Resources:
  - **PRIMARY** D2L.ai — Supervised learning (ML Crash Course) (~75 min)
    https://d2l.ai/chapter_introduction/index.html
- Currently has **no questions at all**.

## `ml-validation-split` — Validation split

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Explain why train/test alone leaks decisions; carve out a validation set
- Context: Explain why train/test alone leaks decisions; carve out a validation set.
- Resources:
  - **PRIMARY** scikit-learn — Cross-validation: evaluating estimator performance (~42 min)
    https://scikit-learn.org/stable/modules/cross_validation.html
- Currently has **no questions at all**.

## `ml-loss-intuition` — Cost & loss intuition

- Depth target: INTUITION  ·  Track: CORE
- Objective: Interpret a loss surface; explain why squared error punishes large misses
- Context: Interpret a loss surface; explain why squared error punishes large misses.
- Resources:
  - **PRIMARY** scikit-learn — Linear model — OLS cost (~60 min)
    https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares
- Currently has **no questions at all**.

## `ml-gradient-descent-intuition` — Gradient descent intuition

- Depth target: INTUITION  ·  Track: CORE
- Objective: Descend a loss surface step by step; relate step size to learning rate
- Context: Descend a loss surface step by step; relate step size to learning rate.
- Resources:
  - **PRIMARY** Vizuara — ML Teach by Doing Day 6: Linear Classifiers Part 1 (~26 min)
    https://www.youtube.com/watch?v=rcXcGS1M77g
  - **REFERENCE** scikit-learn — Gradient descent (~60 min)
    https://scikit-learn.org/stable/modules/linear_model.html#gradient-descent
    exact part: end
- Currently has **no questions at all**.

## `ml-logistic-regression` — Logistic regression

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Map outputs through a sigmoid to probabilities; pick thresholds deliberately
- Context: Map outputs through a sigmoid to probabilities; pick thresholds deliberately.
- Resources:
  - **PRIMARY** scikit-learn — Logistic regression (~60 min)
    https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression
- Currently has **no questions at all**.

## `ml-decision-trees` — Decision trees

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Trace splits by information gain/Gini; state why trees overfit deeply grown leaves
- Context: Trace splits by information gain/Gini; state why trees overfit deeply grown leaves.
- Resources:
  - **PRIMARY** StatQuest with Josh Starmer — Decision and Classification Trees, Clearly Explained!!! (~30 min)
    https://www.youtube.com/watch?v=_L39rN6gz7Y
    exact part: 00:18
  - **REFERENCE** scikit-learn — Decision Trees user guide
    https://scikit-learn.org/stable/modules/tree.html
- Currently has **no questions at all**.

## `ml-random-forests` — Random forests

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Bootstrap + feature bagging → variance reduction; explain OOB estimates
- Context: Bootstrap + feature bagging → variance reduction; explain OOB estimates.
- Resources:
  - **PRIMARY** scikit-learn — Forests of randomized trees (~63 min)
    https://scikit-learn.org/stable/modules/ensemble.html#forests-of-randomized-trees
- Currently has **no questions at all**.

## `ml-knn` — K-nearest neighbors

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Classify by vote of neighbors; discuss k, distance choice, and scaling sensitivity
- Context: Classify by vote of neighbors; discuss k, distance choice, and scaling sensitivity.
- Resources:
  - **PRIMARY** scikit-learn — Nearest Neighbors user guide (~33 min)
    https://scikit-learn.org/stable/modules/neighbors.html
- Currently has **no questions at all**.

## `ml-naive-bayes` — Naive Bayes

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Apply Bayes' theorem with conditional independence; classic text baseline
- Context: Apply Bayes' theorem with conditional independence; classic text baseline.
- Resources:
  - **PRIMARY** scikit-learn — Naive Bayes user guide (~14 min)
    https://scikit-learn.org/stable/modules/naive_bayes.html
- Currently has **no questions at all**.

## `ml-svm` — Support vector machines

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Maximum-margin intuition; kernels lift features to separate non-linear data
- Context: Maximum-margin intuition; kernels lift features to separate non-linear data.
- Resources:
  - **PRIMARY** scikit-learn — Support Vector Machines user guide (~32 min)
    https://scikit-learn.org/stable/modules/svm.html
- Currently has **no questions at all**.

## `ml-confusion-matrix` — Confusion matrix deep dive

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Derive precision/recall/F1 from TP/FP/FN/TN; choose metrics for imbalanced data
- Context: Derive precision/recall/F1 from TP/FP/FN/TN; choose metrics for imbalanced data.
- Resources:
  - **PRIMARY** scikit-learn — Confusion matrix (~75 min)
    https://scikit-learn.org/stable/modules/model_evaluation.html#confusion-matrix
- Currently has **no questions at all**.

## `ml-bias-variance` — Bias–variance tradeoff

- Depth target: INTUITION  ·  Track: CORE
- Objective: Diagnose underfit vs overfit from train/val gaps; pick remedies accordingly
- Context: Diagnose underfit vs overfit from train/val gaps; pick remedies accordingly.
- Resources:
  - **PRIMARY** scikit-learn — Underfitting vs overfitting (~75 min)
    https://scikit-learn.org/stable/modules/model_evaluation.html#underfitting-vs-overfitting
- Currently has **no questions at all**.

## `ml-cross-validation` — Cross-validation

- Depth target: MECHANICS  ·  Track: CORE
- Objective: K-fold rotation gives robust estimates on small data; stratify classification folds
- Context: K-fold rotation gives robust estimates on small data; stratify classification folds.
- Resources:
  - **PRIMARY** scikit-learn — Cross-validation guide (~42 min)
    https://scikit-learn.org/stable/modules/cross_validation.html
- Currently has **no questions at all**.

## `ml-feature-scaling` — Feature scaling

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Standardize/normalize so distance-based methods and gradient descent behave
- Context: Standardize/normalize so distance-based methods and gradient descent behave.
- Resources:
  - **PRIMARY** scikit-learn — Standardization & scaling (~49 min)
    https://scikit-learn.org/stable/modules/preprocessing.html#standardization-or-mean-removal-and-variance-scaling
- Currently has **no questions at all**.

## `ml-encoding-categorical` — Encoding categorical data

- Depth target: MECHANICS  ·  Track: CORE
- Objective: One-hot vs ordinal vs target encoding; leakage dangers in target statistics
- Context: One-hot vs ordinal vs target encoding; leakage dangers in target statistics.
- Resources:
  - **PRIMARY** scikit-learn — Encoding categorical features (~49 min)
    https://scikit-learn.org/stable/modules/preprocessing.html#encoding-categorical-features
- Currently has **no questions at all**.

## `ml-ensemble-learning` — Ensemble learning

- Depth target: INTUITION  ·  Track: CORE
- Objective: Bagging cuts variance, boosting cuts bias, stacking blends strengths
- Context: Bagging cuts variance, boosting cuts bias, stacking blends strengths.
- Resources:
  - **PRIMARY** StatQuest with Josh Starmer — StatQuest: Random Forests Part 1 - Building, Using and Evaluating (~63 min)
    https://www.youtube.com/watch?v=J4Wdy0Wc_xQ
    exact part: 00:31
  - **REFERENCE** scikit-learn — Ensembles user guide overview
    https://scikit-learn.org/stable/modules/ensemble.html
- Currently has **no questions at all**.

## `ml-end-to-end-workflow` — End-to-end ML workflow

- Depth target: APPLICATION  ·  Track: CORE
- Objective: Frame problem → data → features → model → validate → iterate: the full loop once
- Context: Frame problem → data → features → model → validate → iterate: the full loop once.
- Resources:
  - **PRIMARY** Google Developers — ML workflow checklist (~10 min)
    https://developers.google.com/machine-learning/crash-course/production-ml-systems
- Currently has **no questions at all**.

## `ml-ridge-lasso` — Ridge & Lasso regularization

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Constrain linear weights with L2/L1 penalties; pick via validation
- Context: Constrain linear weights with L2/L1 penalties; pick via validation.
- Resources:
  - **PRIMARY** Vizuara — ML Teach by Doing Day 6: Linear Classifiers Part 1 (~10 min)
    https://www.youtube.com/watch?v=rcXcGS1M77g
  - **REFERENCE** scikit-learn — Linear Models — Ridge/Lasso (~60 min)
    https://scikit-learn.org/stable/modules/linear_model.html
    exact part: above; content inspection pending
  - **REFERENCE** Vizuara — Vizuara — Ridge Regression fundamentals and intuition (~10 min)
    https://www.youtube.com/watch?v=-2Dbj1IzZm4
- Currently has **no questions at all**.

## `ml-roc-auc` — ROC curves & AUC

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Read TPR/FPR across thresholds; compare models with AUC and PR curves
- Context: Read TPR/FPR across thresholds; compare models with AUC and PR curves.
- Resources:
  - **PRIMARY** StatQuest — What Are ROC Curves and AUC in Classification? (~75 min)
    https://www.youtube.com/watch?v=4jRBRDbJemM
    exact part: 00:00 through 
- Currently has **no questions at all**.

## `ml-regression-metrics` — Regression metrics

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Interpret MAE vs MSE vs RMSE vs R² and when each misleads
- Context: Interpret MAE vs MSE vs RMSE vs R² and when each misleads.
- Resources:
  - **PRIMARY** scikit-learn — scikit-learn — Regression metrics (~75 min)
    https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics
    exact part: Regression metrics
- Currently has **no questions at all**.

## `ml-grid-search` — Hyperparameter search

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Grid vs randomized search with cross-validation and validation curves
- Context: Grid vs randomized search with cross-validation and validation curves.
- Resources:
  - **PRIMARY** scikit-learn — Grid Search & Randomized Search (~31 min)
    https://scikit-learn.org/stable/modules/grid_search.html
- Currently has **no questions at all**.

## `ml-kmeans` — K-means clustering

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Iterative centroid assignment; elbow/silhouette choice of k
- Context: Iterative centroid assignment; elbow/silhouette choice of k.
- Resources:
  - **PRIMARY** StatQuest — StatQuest — K-means Clustering (~10 min)
    https://www.youtube.com/watch?v=4b5d3muPQmA
    exact part: K-means Clustering · Conceptual motivation; K-means algorithm; Choosing K
- Currently has **no questions at all**.

## `ml-hierarchical-dbscan` — Hierarchical clustering & DBSCAN

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Dendrograms vs density reachability; noise handling without fixed k
- Context: Dendrograms vs density reachability; noise handling without fixed k.
- Resources:
  - **PRIMARY** scikit-learn — scikit-learn — Clustering: Hierarchical and DBSCAN (~74 min)
    https://scikit-learn.org/stable/modules/clustering.html
    exact part: Hierarchical clustering; DBSCAN; Density-based clustering
- Currently has **no questions at all**.

## `ml-pca` — Principal component analysis

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Project onto top-variance directions; explained variance & whitening
- Context: Project onto top-variance directions; explained variance & whitening.
- Resources:
  - **PRIMARY** StatQuest — StatQuest — Principal Component Analysis (PCA), Step-by-Step (~10 min)
    https://www.youtube.com/watch?v=FgakZw6K1QQ
    exact part: Principal Component Analysis (PCA), Step-by-Step · Conceptual motivation; PCA worked out; Eigenvectors/values; Explained variation
- Currently has **no questions at all**.

## `ml-anomaly-awareness` — Anomaly detection awareness

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Novelty vs outlier detection settings; when unsupervised flags fail
- Context: Novelty vs outlier detection settings; when unsupervised flags fail.
- Resources:
  - **PRIMARY** scikit-learn — scikit-learn — Novelty and Outlier Detection (~20 min)
    https://scikit-learn.org/stable/modules/outlier_detection.html
    exact part: Overview; Novelty detection; Outlier detection
- Currently has **no questions at all**.

## `ml-gradient-boosting` — Gradient boosting

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Fit trees to residual gradients stage-wise; learning-rate/shallow-depth
- Context: Fit trees to residual gradients stage-wise; learning-rate/shallow-depth.
- Resources:
  - **PRIMARY** scikit-learn — Gradient-boosted trees (~63 min)
    https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting
    exact part: Gradient-boosted trees
- Currently has **no questions at all**.

## `ml-feature-importance` — Feature importance

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Impurity importances vs permutation importance; correlation pitfalls
- Context: Impurity importances vs permutation importance; correlation pitfalls.
- Resources:
  - **PRIMARY** scikit-learn — Permutation Importance (~14 min)
    https://scikit-learn.org/stable/modules/permutation_importance.html
- Currently has **no questions at all**.

