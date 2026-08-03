# Survey questionnaire — executive summary

**Data:** Educational synthetic survey from **Mohsen Rafiei, Ph.D.** / PUX Lab (see [`ATTRIBUTION.md`](../ATTRIBUTION.md)). Not real product users.

## Problem
Practice end-to-end quantitative UX analysis: clean a messy survey, summarize UX metrics (SUS, trust, NASA-TLX), and model task success for a product-style readout.

## Method
1. Clean and validate demographics, Likert scales, and outliers (`src/clean_survey_questionnaire.py`).
2. Restrict analysis to attention-check passers.
3. Compare UX scores for success vs failure groups.
4. Fit a logistic regression pipeline (numeric + categorical features) predicting `task_success`.
5. Surface metrics and partner-facing recommendations in a Streamlit dashboard.

## Results
Holdout classification metrics on the educational sample (`data/processed/survey_task_success_metrics.csv`):

| Metric | Value |
|--------|-------|
| Accuracy | 0.932 |
| Precision | 0.943 |
| Recall | 0.980 |
| F1 | 0.961 |
| ROC-AUC | 0.965 |

## Product-style recommendations (methods demo only)
- Improve clarity / guidance so users need less effort to complete the task.
- Watch trust and ease-of-use even among successful users.
- Reduce frustration and cognitive load before shipping new features.
- Track success **with** UX scores, not success alone.

## How to reproduce
```bash
pip install -r requirements.txt
python src/clean_survey_questionnaire.py
streamlit run dashboard/app.py
```
