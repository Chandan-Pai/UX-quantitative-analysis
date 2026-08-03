# UX Quant Dashboard

Interactive dashboard for the survey questionnaire analysis.

> **Data credit:** Educational synthetic survey from **Mohsen Rafiei, Ph.D.** (PUX Lab). See repo [`ATTRIBUTION.md`](../ATTRIBUTION.md) and [`DATA_LICENSE.md`](../DATA_LICENSE.md).

## What it shows
- Completion and failure rates
- SUS, trust, ease of use, and frustration summaries
- Success vs failure comparisons
- Device and experience breakdowns
- Correlation heatmap for key UX measures
- Recommendations based on the cleaned educational data

## Data source
- `../data/processed/survey_questionnaire_analysis_ready.csv`

## Run

```bash
# from repo root, with venv active
streamlit run dashboard/app.py
```
