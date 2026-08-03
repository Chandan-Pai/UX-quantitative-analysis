# UX Quant Analysis — Validation Suite

Interactive **Quant UX Validation Suite** (Streamlit): survey, usability testing, and A/B experiment readouts.

**Live app:** https://ux-quantitative-analysis-f7wxsl89jopdxvcaycsukx.streamlit.app/

> **Data credit (required):** Survey / usability / A/B data from **Mohsen Rafiei, Ph.D.**, *UX Datasets Collection* (2025), **Perceptual User Experience Lab (PUX Lab)**.  
> Source: https://github.com/mohsen-rafiei/UX_datasets  
> License: Educational Dataset License (see [`DATA_LICENSE.md`](DATA_LICENSE.md)).  
> **These are synthetically generated educational datasets**, not real product telemetry. Results are for methods practice and portfolio demonstration only. Do **not** treat findings as claims about real products or systems.

**Citation (APA):**  
Rafiei, M. (2025). UX Datasets Collection: Multi-method UX research datasets for teaching HCI and cognitive psychology [Dataset]. GitHub. https://github.com/mohsen-rafiei/UX_datasets

---

## What this repo shows

| Piece | Purpose |
|-------|---------|
| `dashboard/app.py` | Suite home (decision-oriented hub) |
| `dashboard/pages/` | Survey · Usability · A/B validation pages |
| `src/clean_*.py` | Reproducible cleaning → analysis-ready CSVs |
| `notebooks/` | Survey clean + logistic model notebook |
| `data/raw/` | Educational CSVs (attributed) |
| `data/processed/` | Cleaned outputs + model metrics |

Each Streamlit page follows: **decision → KPIs → where it breaks → segments → method**.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Refresh processed data

```bash
python src/clean_survey_questionnaire.py
python src/clean_usability_testing.py
python src/clean_ab_testing.py
```

## Run locally

```bash
streamlit run dashboard/app.py
```

Open **http://localhost:8501**

## Streamlit Community Cloud

- Repo: `Chandan-Pai/UX-quantitative-analysis`
- Main file: `dashboard/app.py`
- Pushes to `main` redeploy the live app

## Roadmap

See [`STUDY_ROADMAP.md`](STUDY_ROADMAP.md). Next datasets (same attribution rules): feature adoption, funnel/retention, system UX metrics. Recommender / ML pipelines stay in a **separate** repo.

## Attribution and honesty

- **Dataset owner:** **Mohsen Rafiei, Ph.D.** (PUX Lab)
- Analysis, cleaning, dashboard: **Chandan Umesh Pai**
- Not for commercial product claims without permission from the dataset creator
