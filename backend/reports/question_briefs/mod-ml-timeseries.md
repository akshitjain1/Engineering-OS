# Question brief: Time Series (`mod-ml-timeseries`)

Subject: Machine Learning Foundations
Topics: 6

For each topic below, write at least 4 self-check questions in
`content/questions/mod-ml-timeseries.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `ts-why-random-splits-fail` — Why random splits fail on time series

- Depth target: DEEP  ·  Track: CORE
- Objective: Replace random splitting with a temporal split and explain what the random split was actually measuring.
- Context: Autocorrelation breaks the i.i.d. assumption, so a random K-fold split leaks the future into the past and yields an optimistic error estimate - plus the drop-in fix and its gap and max-train-size knobs.
- Resources:
  - **PRIMARY** scikit-learn — Cross-validation: evaluating estimator performance
    https://scikit-learn.org/stable/modules/cross_validation.html
    exact part: §3.1.2.6 "Cross validation of time series data" and §3.1.2.6.1 "Time Series Split" (headings verified)
  - **REFERENCE** scikit-learn — TimeSeriesSplit
    https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
- Currently has **no questions at all**.

## `ts-rolling-origin-validation` — Rolling-origin validation

- Depth target: STRONG  ·  Track: CORE
- Objective: Design a rolling-origin evaluation for a stated forecast horizon.
- Context: Evaluation on a rolling forecasting origin, with the diagram that makes the scheme obvious, plus the multi-step-ahead variants.
- Resources:
  - **PRIMARY** OTexts (Forecasting: Principles and Practice, 3rd ed.) — 5.10 Time series cross-validation
    https://otexts.com/fpp3/tscv.html
- Currently has **no questions at all**.

## `ts-forecasting-baselines` — Forecasting baselines

- Depth target: STRONG  ·  Track: CORE
- Objective: Produce the four simple baselines and use them as the bar any model has to beat.
- Context: Naive, seasonal-naive, mean and drift forecasts - the baselines that beat most first attempts at a neural forecaster, and the bar any model must clear.
- Resources:
  - **PRIMARY** OTexts (Forecasting: Principles and Practice, 3rd ed.) — 5.2 Some simple forecasting methods
    https://otexts.com/fpp3/simple-methods.html
- Currently has **no questions at all**.

## `ts-forecast-accuracy-metrics` — Forecast accuracy metrics

- Depth target: STRONG  ·  Track: CORE
- Objective: Choose a forecast error metric that survives comparison across series.
- Context: Training versus test sets on time series, then scale-dependent (MAE, RMSE) versus percentage (MAPE) versus scale-free (MASE) errors - including why MAPE breaks near zero.
- Resources:
  - **PRIMARY** OTexts (Forecasting: Principles and Practice, 3rd ed.) — 5.8 Evaluating point forecast accuracy
    https://otexts.com/fpp3/accuracy.html
- Currently has **no questions at all**.

## `ts-stationarity-differencing` — Stationarity and differencing

- Depth target: WORKING_KNOWLEDGE  ·  Track: CORE
- Objective: Diagnose non-stationarity and apply the right differencing.
- Context: What stationarity means, how differencing and seasonal differencing achieve it, and the autocorrelation function as a diagnostic.
- Resources:
  - **PRIMARY** OTexts (Forecasting: Principles and Practice, 3rd ed.) — 9.1 Stationarity and differencing
    https://otexts.com/fpp3/stationarity.html
- Currently has **no questions at all**.

## `ts-lag-and-calendar-features` — Lag and calendar features

- Depth target: STRONG  ·  Track: CORE
- Objective: Build a correctly-validated ML forecasting pipeline out of timestamp features.
- Context: Turning timestamps into lag, calendar, spline and cyclical (sine/cosine) features, evaluated with a time-series split, comparing a gradient-boosted model against a linear one.
- Resources:
  - **PRIMARY** scikit-learn — Time-related feature engineering
    https://scikit-learn.org/stable/auto_examples/applications/plot_cyclical_feature_engineering.html
    exact part: FULL_SINGLE_PAGE — work through it as a notebook
- Currently has **no questions at all**.

