from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats


st.set_page_config(
    page_title="UX Quant Dashboard",
    page_icon="📊",
    layout="wide",
)

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "survey_questionnaire_analysis_ready.csv"

METRIC_LABELS = {
    "sus_score": "SUS",
    "trust_score": "Trust",
    "ease_of_use": "Ease of Use",
    "nasa_tlx_frustration": "Frustration",
    "nasa_tlx_mental": "Mental Demand",
    "nasa_tlx_temporal": "Time Pressure",
    "completion_time_s": "Completion Time (s)",
}

RECOMMENDATIONS = [
    "Improve clarity and guidance in the interface so users need less effort to complete the task.",
    "Focus on trust and ease-of-use issues, because successful users still rate the experience only moderately.",
    "Reduce frustration and cognitive load in the task flow before adding new features.",
    "Keep monitoring task success together with UX scores, because completion alone hides friction.",
]


@st.cache_data

def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["task_success_label"] = df["task_success"].map({0: "Failed", 1: "Completed"})
    return df


@st.cache_data

def group_ttest(df: pd.DataFrame, metric: str) -> dict[str, float]:
    success = df[df["task_success"] == 1][metric]
    failure = df[df["task_success"] == 0][metric]
    t_stat, p_value = stats.ttest_ind(success, failure, equal_var=False, nan_policy="omit")
    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "success_mean": float(success.mean()),
        "failure_mean": float(failure.mean()),
    }


@st.cache_data

def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "task_success",
        "sus_score",
        "trust_score",
        "ease_of_use",
        "nasa_tlx_frustration",
        "nasa_tlx_mental",
        "nasa_tlx_temporal",
        "completion_time_s",
    ]
    return df[cols].corr(numeric_only=True)


@st.cache_data

def summary_metrics(df: pd.DataFrame) -> dict[str, float]:
    total = len(df)
    completed = int(df["task_success"].sum())
    failed = total - completed
    return {
        "rows": total,
        "completion_rate": completed / total * 100,
        "failure_rate": failed / total * 100,
        "mean_sus": df["sus_score"].mean(),
        "mean_trust": df["trust_score"].mean(),
        "mean_ease": df["ease_of_use"].mean(),
        "mean_frustration": df["nasa_tlx_frustration"].mean(),
    }


if not DATA_PATH.exists():
    st.error(f"Data file not found: {DATA_PATH}")
    st.stop()


df = load_data()
summary = summary_metrics(df)

st.title("UX Quant Dashboard")
st.caption("Interactive report for survey usability, task success, and UX bottlenecks.")

with st.sidebar:
    st.header("Filters")
    device_options = sorted(df["device_type"].dropna().unique().tolist())
    experience_options = sorted(df["experience_level"].dropna().unique().tolist())
    selected_devices = st.multiselect("Device type", device_options, default=device_options)
    selected_experience = st.multiselect("Experience level", experience_options, default=experience_options)
    metric_choice = st.selectbox(
        "Metric to compare",
        ["sus_score", "trust_score", "ease_of_use", "nasa_tlx_frustration", "completion_time_s"],
        format_func=lambda value: METRIC_LABELS[value],
    )

filtered = df[df["device_type"].isin(selected_devices) & df["experience_level"].isin(selected_experience)]

if filtered.empty:
    st.warning("No rows match the selected filters.")
    st.stop()

summary = summary_metrics(filtered)

kpi_cols = st.columns(6)
kpi_cols[0].metric("Rows", f"{summary['rows']}")
kpi_cols[1].metric("Task completion", f"{summary['completion_rate']:.1f}%")
kpi_cols[2].metric("Failure rate", f"{summary['failure_rate']:.1f}%")
kpi_cols[3].metric("Mean SUS", f"{summary['mean_sus']:.1f}")
kpi_cols[4].metric("Mean trust", f"{summary['mean_trust']:.2f}")
kpi_cols[5].metric("Mean frustration", f"{summary['mean_frustration']:.2f}")

left_col, right_col = st.columns([1.1, 1])

with left_col:
    st.subheader("Outcome and UX summary")
    outcome_df = filtered["task_success_label"].value_counts().rename_axis("Outcome").reset_index(name="Count")
    fig = px.bar(outcome_df, x="Outcome", y="Count", color="Outcome", text="Count", title="Task outcomes")
    fig.update_layout(showlegend=False, height=360)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"{METRIC_LABELS[metric_choice]} by task outcome")
    metric_fig = px.box(
        filtered,
        x="task_success_label",
        y=metric_choice,
        color="task_success_label",
        points="all",
        title=f"{METRIC_LABELS[metric_choice]} by success or failure",
    )
    metric_fig.update_layout(showlegend=False, height=420)
    st.plotly_chart(metric_fig, use_container_width=True)

with right_col:
    st.subheader("Bottleneck checks")
    ttest_results = pd.DataFrame(
        {
            "Metric": ["SUS", "Completion Time", "Trust", "Ease of Use", "Frustration"],
            **{
                key: [
                    group_ttest(filtered, metric)[key]
                    for metric in ["sus_score", "completion_time_s", "trust_score", "ease_of_use", "nasa_tlx_frustration"]
                ]
                for key in ["success_mean", "failure_mean", "t_stat", "p_value"]
            },
        }
    )
    ttest_results["p_value"] = ttest_results["p_value"].map(lambda value: f"{value:.4g}")
    ttest_results["success_mean"] = ttest_results["success_mean"].round(2)
    ttest_results["failure_mean"] = ttest_results["failure_mean"].round(2)
    ttest_results["t_stat"] = ttest_results["t_stat"].round(3)
    st.dataframe(ttest_results, use_container_width=True, hide_index=True)

    st.subheader("Completion time distribution")
    time_fig = px.histogram(filtered, x="completion_time_s", nbins=30, color="task_success_label", barmode="overlay")
    time_fig.update_layout(height=360)
    st.plotly_chart(time_fig, use_container_width=True)

st.subheader("Device and experience breakdown")
bar_left, bar_right = st.columns(2)
with bar_left:
    device_fig = px.bar(
        filtered.groupby("device_type", as_index=False)[["sus_score", "trust_score", "ease_of_use", "nasa_tlx_frustration"]].mean().melt(
            id_vars="device_type", var_name="Metric", value_name="Value"
        ),
        x="device_type",
        y="Value",
        color="Metric",
        barmode="group",
        title="Average UX metrics by device",
    )
    st.plotly_chart(device_fig, use_container_width=True)
with bar_right:
    experience_fig = px.bar(
        filtered.groupby("experience_level", as_index=False)[["sus_score", "trust_score", "ease_of_use", "nasa_tlx_frustration"]].mean().melt(
            id_vars="experience_level", var_name="Metric", value_name="Value"
        ),
        x="experience_level",
        y="Value",
        color="Metric",
        barmode="group",
        title="Average UX metrics by experience",
    )
    st.plotly_chart(experience_fig, use_container_width=True)

st.subheader("Relationship view")
heatmap = correlation_matrix(filtered)
heatmap_fig = go.Figure(
    data=go.Heatmap(
        z=heatmap.values,
        x=heatmap.columns,
        y=heatmap.index,
        colorscale="RdBu",
        zmin=-1,
        zmax=1,
        colorbar=dict(title="Correlation"),
    )
)
heatmap_fig.update_layout(height=520)
st.plotly_chart(heatmap_fig, use_container_width=True)

st.subheader("Key insight")
st.markdown(
    """
- Users are completing the task often enough, but the experience scores show that success does not equal a good UX.
- Trust, ease of use, and frustration are the strongest signals separating successful and failed users.
- That means the product likely needs clarity and friction reduction, not just better completion mechanics.
"""
)

st.subheader("Recommendations")
for item in RECOMMENDATIONS:
    st.write(f"- {item}")

st.subheader("Data source")
st.write(f"Dashboard is driven by: {DATA_PATH}")
