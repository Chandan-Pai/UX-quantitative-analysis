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
    filter_bar,
    labeled_bar,
    load_csv,
    multiselect_all,
    render_sidebar_about,
    section_caption,
    style_fig,
)

render_sidebar_about()

METRIC_LABELS = {
    "sus_score": "SUS usability score (higher = easier)",
    "trust_score": "Trust (1–7, higher = more trust)",
    "ease_of_use": "Ease of use (1–7, higher = easier)",
    "nasa_tlx_frustration": "Frustration (higher = worse)",
    "completion_time_s": "Completion time (seconds)",
}
METRIC_SHORT = {
    "sus_score": "SUS",
    "trust_score": "Trust",
    "ease_of_use": "Ease of use",
    "nasa_tlx_frustration": "Frustration",
    "completion_time_s": "Time (sec)",
}

df = load_csv("survey_questionnaire_analysis_ready.csv")
metrics_path = Path(__file__).resolve().parents[2] / "data" / "processed" / "survey_task_success_metrics.csv"
model_metrics = {}
if metrics_path.exists():
    raw_metrics = pd.read_csv(metrics_path)
    if "Unnamed: 0" in raw_metrics.columns:
        model_metrics = dict(zip(raw_metrics["Unnamed: 0"], raw_metrics["value"]))

st.title("Survey validation")
st.caption("Post-task questionnaire · task success · product-facing recommendations")

with st.container(border=True):
    filter_bar()
    f1, f2, f3 = st.columns([1.2, 1.2, 1])
    with f1:
        selected_devices = multiselect_all(
            "Device type",
            sorted(df["device_type"].dropna().unique().tolist()),
            key="survey_devices",
        )
    with f2:
        selected_experience = multiselect_all(
            "Experience level",
            sorted(df["experience_level"].dropna().unique().tolist()),
            key="survey_experience",
        )
    with f3:
        metric_choice = st.selectbox(
            "Metric shown in the comparison chart",
            list(METRIC_LABELS.keys()),
            format_func=lambda key: METRIC_SHORT[key],
            key="survey_metric",
        )
        st.caption(METRIC_LABELS[metric_choice])

filtered = df[df["device_type"].isin(selected_devices) & df["experience_level"].isin(selected_experience)]
if filtered.empty:
    st.warning("No rows match the selected filters. Add at least one device and experience level.")
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

st.markdown("### Snapshot (filtered sample)")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("People in view", f"{len(filtered):,}", help="Rows left after filters")
k2.metric("Finished the task", f"{completion:.1f}%", help="% who completed the task successfully")
k3.metric("Avg SUS", f"{mean_sus:.1f} / 100", help="System Usability Scale. Higher is better. ~68 is often a rough benchmark.")
k4.metric("Avg trust", f"{mean_trust:.2f} / 7", help="1 = low trust, 7 = high trust")
k5.metric("Avg frustration", f"{mean_frustration:.2f}", help="Workload frustration item. Higher means more frustration.")
section_caption(
    "Read as a set: high “Finished the task” with mid SUS means people got through, but the experience still felt mediocre."
)

st.markdown("### Where experience breaks (completed vs failed)")
compare_rows = []
for metric, label, unit_note in [
    ("sus_score", "SUS usability", "higher better"),
    ("trust_score", "Trust (1–7)", "higher better"),
    ("ease_of_use", "Ease of use (1–7)", "higher better"),
    ("nasa_tlx_frustration", "Frustration", "higher = worse"),
    ("completion_time_s", "Time to finish (sec)", "lower usually better"),
]:
    success = filtered.loc[filtered["task_success"] == 1, metric]
    failure = filtered.loc[filtered["task_success"] == 0, metric]
    _, p_value = stats.ttest_ind(success, failure, equal_var=False, nan_policy="omit")
    compare_rows.append(
        {
            "What we measured": label,
            "Scale note": unit_note,
            "Avg if completed": round(float(success.mean()), 2),
            "Avg if failed": round(float(failure.mean()), 2),
            "Difference (completed − failed)": round(float(success.mean() - failure.mean()), 2),
            "Statistically different?": "Yes (p < 0.05)" if p_value < 0.05 else "No",
        }
    )
st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)
section_caption(
    "Example: if Trust is higher for completers and Frustration is higher for failures, the product is usable enough to finish but emotionally costly when it breaks."
)

left, right = st.columns(2)
with left:
    st.markdown(f"#### {METRIC_SHORT[metric_choice]} for people who completed vs failed")
    fig = px.box(
        filtered,
        x="task_success_label",
        y=metric_choice,
        color="task_success_label",
        labels={
            "task_success_label": "Did they finish the task?",
            metric_choice: METRIC_LABELS[metric_choice],
        },
        points="outliers",
    )
    style_fig(fig, METRIC_LABELS[metric_choice], "Did they finish the task?")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    section_caption("Box = middle 50% of people. Line inside = median. Dots = unusual outliers.")
with right:
    st.markdown("#### How many people finished vs failed")
    outcome = filtered["task_success_label"].value_counts().rename_axis("Outcome").reset_index(name="People")
    fig2 = px.bar(
        outcome,
        x="Outcome",
        y="People",
        color="Outcome",
        text="People",
        labels={"Outcome": "Task result", "People": "Number of people"},
    )
    style_fig(fig2, "Number of people", "Task result")
    labeled_bar(fig2, "d")
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("### Segments — average scores by device and experience")
section_caption("Each bar is an average score for that group (after filters). Compare colors within a group, not across different scales blindly.")
s1, s2 = st.columns(2)
metric_cols = ["sus_score", "trust_score", "ease_of_use", "nasa_tlx_frustration"]
with s1:
    device = (
        filtered.groupby("device_type", as_index=False)[metric_cols]
        .mean()
        .melt(id_vars="device_type", var_name="Metric", value_name="Average score")
    )
    device["Metric"] = device["Metric"].map(METRIC_SHORT)
    device["Average score"] = device["Average score"].round(2)
    fig = px.bar(
        device,
        x="device_type",
        y="Average score",
        color="Metric",
        barmode="group",
        text="Average score",
        labels={"device_type": "Device", "Average score": "Average score", "Metric": "UX measure"},
    )
    style_fig(fig, "Average score", "Device", height=420)
    labeled_bar(fig, ".1f")
    st.plotly_chart(fig, use_container_width=True)
with s2:
    exp = (
        filtered.groupby("experience_level", as_index=False)[metric_cols]
        .mean()
        .melt(id_vars="experience_level", var_name="Metric", value_name="Average score")
    )
    exp["Metric"] = exp["Metric"].map(METRIC_SHORT)
    exp["Average score"] = exp["Average score"].round(2)
    fig = px.bar(
        exp,
        x="experience_level",
        y="Average score",
        color="Metric",
        barmode="group",
        text="Average score",
        labels={"experience_level": "Experience level", "Average score": "Average score", "Metric": "UX measure"},
    )
    style_fig(fig, "Average score", "Experience level", height=420)
    labeled_bar(fig, ".1f")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Method and model check")
m1, m2 = st.columns(2)
with m1:
    st.markdown(
        """
**Study type:** post-task survey with SUS, trust / ease ratings, NASA-TLX frustration.  
**Pipeline:** raw CSV → `src/clean_survey_questionnaire.py` → this page.  
**Honesty:** educational synthetic data (Rafiei / PUX). Not real product users.
"""
    )
with m2:
    if model_metrics:
        st.markdown("**Can UX scores predict task success?** (holdout logistic model)")
        c = st.columns(3)
        c[0].metric("Accuracy", f"{model_metrics.get('accuracy', 0)*100:.1f}%", help="Share of held-out people classified correctly")
        c[1].metric("ROC-AUC", f"{model_metrics.get('roc_auc', 0):.3f}", help="1.0 = perfect separation, 0.5 = chance")
        c[2].metric("F1", f"{model_metrics.get('f1', 0):.3f}", help="Balance of precision and recall")
        section_caption("This is a diagnostic check, not a production scoring model.")
    else:
        st.write("Model metrics file not found.")
