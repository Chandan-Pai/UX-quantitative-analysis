# UX Quant Analysis

Quantitative UX research portfolio: survey cleaning, descriptive analysis, task-success modeling, and a Streamlit dashboard.

> **Data credit (required):** Survey data from **Mohsen Rafiei, Ph.D.**, *UX Datasets Collection* (2025), **Perceptual User Experience Lab (PUX Lab)**.  
> Source: https://github.com/mohsen-rafiei/UX_datasets  
> License: Educational Dataset License (see [`DATA_LICENSE.md`](DATA_LICENSE.md)).  
> **These are synthetically generated educational datasets**, not real product telemetry. Results are for methods practice and portfolio demonstration only. Do **not** treat findings as claims about real products or systems.

**Citation (APA):**  
Rafiei, M. (2025). UX Datasets Collection: Multi-method UX research datasets for teaching HCI and cognitive psychology [Dataset]. GitHub. https://github.com/mohsen-rafiei/UX_datasets

---

## What this repo shows

| Piece | Purpose |
|-------|---------|
| `src/clean_survey_questionnaire.py` | Reproducible cleaning → analysis-ready CSV |
| `notebooks/01_survey_questionnaire_clean_and_model.ipynb` | Clean → preprocess → logistic model → evaluation |
| `dashboard/app.py` | Streamlit readout for product partners |
| `data/raw/` | Educational survey CSV (attributed) |
| `data/processed/` | Cleaned outputs + model metrics |

## Key results (survey / task success model)

On the educational analysis-ready sample (attention-check passed):

- Logistic regression holdout metrics (see `data/processed/survey_task_success_metrics.csv`): accuracy ≈ **0.93**, ROC-AUC ≈ **0.96**
- Product-facing takeaway: pair task success with SUS / trust / frustration; completion alone hides friction

Full write-up: [`reports/survey_exec_summary.md`](reports/survey_exec_summary.md)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run cleaning

```bash
python src/clean_survey_questionnaire.py
```

## Run notebook

```bash
jupyter notebook notebooks/01_survey_questionnaire_clean_and_model.ipynb
```

## Run dashboard

```bash
streamlit run dashboard/app.py
```

## Project layout

```
data/raw/          # attributed educational CSV
data/processed/    # cleaned CSVs, metrics, model artifact
notebooks/         # analysis notebooks
src/               # reusable cleaning script
dashboard/         # Streamlit app
reports/           # short exec summaries
```

## Attribution and honesty

- **Dataset owner:** **Mohsen Rafiei, Ph.D.** (PUX Lab) — attribution required for any use/redistribution of the educational data.
- Analysis, cleaning code, modeling, and dashboard in this repo: **Chandan Umesh Pai**.
- Not for commercial product claims without permission from the dataset creator (`Admin@puxlab.com` per their license).

## Roadmap

See [`STUDY_ROADMAP.md`](STUDY_ROADMAP.md) for usability, A/B, and feature-adoption follow-ons (same educational collection, same attribution rules).
