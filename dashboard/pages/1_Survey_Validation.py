from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats

_DASHBOARD_DIR = Path(__file__).resolve().parents[1]
if str(_DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD_DIR))
from ui import (  # noqa: E402
    decision_banner,
    load_csv,
    page_setup,
    render_sidebar_about,
    section_caption,
)

page_setup("Survey Validation")
render_sidebar_about()

METRIC_LABELS = {
    "sus_score": "SUS",
    "trust_score": "Trust",
    "ease_of_use": "Ease of use",
    "nasa_tlx_frustration": "Frustration",
    "completion_time_s": "Completion time (s)",
}

df = load_csv("survey_questionnaire_analysis_ready.csv")
metrics_path = Path(__file__).resolve().parents[2] / "data" / "processed" / "survey_task_success_metrics.csv"
model_metrics = {}
if metrics_path.exists():
    raw_metrics = pd.read_csv(metrics_path)
    if "Unnamed: 0" in raw_metrics.columns:
        model_metrics = dict(zip(raw_metrics["Unnamed: 0"], raw_metrics["value"]))
    elif {"metric", "value"} <= set(raw_metrics.columns):
        model_metrics = dict(zip(raw_metrics["metric"], raw_metrics["value"]))

st.title("Survey validation")
st.caption("Post-task UX questionnaire · task success · product-facing recommendations")

with st.sidebar:
    st.header("Filters")
    devices = sorted(df["device_type"].dropna().unique().tolist())
    experiences = sorted(df["experience_level"].dropna().unique().tolist())
    selected_devices = st.multiselect("Device", devices, default=devices)
    selected_experience = st.multiselect("Experience", experiences, default=experiences)
    metric_choice = st.selectbox(
        "Compare metric",
        list(METRIC_LABELS.keys()),
        format_func=lambda key: METRIC_LABELS[key],
    )

filtered = df[df["device_type"].isin(selected_devices) & df["experience_level"].isin(selected_experience)]
if filtered.empty:
    st.warning("No rows match the selected filters.")
    st.stop()

if "task_success_label" not in filtered.columns:
    filtered = filtered.copy()
    filtered["task_success_label"] = filtered["task_success"].map({0: "Failed", 1: "Completed"})

completion = filtered["task_success"].mean() * 100
mean_sus = filtered["sus_score"].mean()
mean_trust = filtered["trust_score"].mean()
mean_frustration = filtered["nasa_tlx_frustration"].mean()

decision_banner(
    "Completion is healthy, but UX quality is only moderate — fix clarity and trust friction before shipping more features.",
    [
        "Treat success rate as necessary but not sufficient (pair with SUS / trust / frustration).",
        "Failed users show higher frustration and lower trust — prioritize guidance and feedback in the critical path.",
        "Use segment views (device / experience) to target the worst friction first.",
    ],
    severity="High",
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Sample (filtered)", f"{len(filtered):,}")
k2.metric("Task completion", f"{completion:.1f}%")
k3.metric("Mean SUS", f"{mean_sus:.1f}", help="System Usability Scale (0–100 style score in this dataset)")
k4.metric("Mean trust", f"{mean_trust:.2f}")
k5.metric("Mean frustration", f"{mean_frustration:.2f}")
section_caption("How to read: high completion with mid SUS usually means people finish, but the experience still hurts.")

st.markdown("### Where experience breaks")
compare_rows = []
for metric, label in [
    ("sus_score", "SUS"),
    ("trust_score", "Trust"),
    ("ease_of_use", "Ease of use"),
    ("nasa_tlx_frustration", "Frustration"),
    ("completion_time_s", "Completion time (s)"),
]:
    success = filtered.loc[filtered["task_success"] == 1, metric]
    failure = filtered.loc[filtered["task_success"] == 0, metric]
    t_stat, p_value = stats.ttest_ind(success, failure, equal_var=False, nan_policy="omit")
    compare_rows.append(
        {
            "Metric": label,
            "Completed (mean)": round(float(success.mean()), 2),
            "Failed (mean)": round(float(failure.mean()), 2),
            "Gap": round(float(success.mean() - failure.mean()), 2),
            "Significant?": "Yes" if p_value < 0.05 else "No",
            "p-value": f"{p_value:.3g}",
        }
    )
st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)
section_caption("Gap = completed minus failed. Frustration often flips sign (failed users more frustrated).")

left, right = st.columns(2)
with left:
    st.markdown(f"#### {METRIC_LABELS[metric_choice]} by outcome")
    fig = px.box(
        filtered,
        x="task_success_label",
        y=metric_choice,
        color="task_success_label",
        labels={"task_success_label": "Outcome", metric_choice: METRIC_LABELS[metric_choice]},
        points="outliers",
    )
    fig.update_layout(showlegend=False, height=400, margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("#### Task outcomes")
    outcome = filtered["task_success_label"].value_counts().rename_axis("Outcome").reset_index(name="Count")
    fig2 = px.bar(outcome, x="Outcome", y="Count", color="Outcome", text="Count")
    fig2.update_layout(showlegend=False, height=400, margin=dict(t=30))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("### Segments")
s1, s2 = st.columns(2)
metric_cols = ["sus_score", "trust_score", "ease_of_use", "nasa_tlx_frustration"]
with s1:
    device = (
        filtered.groupby("device_type", as_index=False)[metric_cols]
        .mean()
        .melt(id_vars="device_type", var_name="Metric", value_name="Value")
    )
    device["Metric"] = device["Metric"].map(METRIC_LABELS)
    fig = px.bar(device, x="device_type", y="Value", color="Metric", barmode="group", labels={"device_type": "Device"})
    fig.update_layout(height=380, margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)
with s2:
    exp = (
        filtered.groupby("experience_level", as_index=False)[metric_cols]
        .mean()
        .melt(id_vars="experience_level", var_name="Metric", value_name="Value")
    )
    exp["Metric"] = exp["Metric"].map(METRIC_LABELS)
    fig = px.bar(
        exp, x="experience_level", y="Value", color="Metric", barmode="group", labels={"experience_level": "Experience"}
    )
    fig.update_layout(height=380, margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Method and model check")
m1, m2 = st.columns(2)
with m1:
    st.markdown(
        """
**Study type:** post-task survey with SUS, UEQ-style ratings, NASA-TLX items, trust / ease.  
**Pipeline:** raw CSV → cleaning (`src/clean_survey_questionnaire.py`) → analysis-ready → this readout.  
**Honesty:** educational synthetic data (Rafiei / PUX). Do not claim real product users.
"""
    )
with m2:
    if model_metrics:
        st.markdown("**Task-success model (holdout logistic regression)**")
        c = st.columns(3)
        c[0].metric("Accuracy", f"{model_metrics.get('accuracy', 0):.3f}")
        c[1].metric("ROC-AUC", f"{model_metrics.get('roc_auc', 0):.3f}")
        c[2].metric("F1", f"{model_metrics.get('f1', 0):.3f}")
        section_caption("Model is a diagnostic check that UX features separate success vs failure — not a production scorer.")
    else:
        st.write("Model metrics file not found.")
