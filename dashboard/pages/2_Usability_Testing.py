from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ui import decision_banner, load_csv, page_setup, render_sidebar_about, section_caption  # noqa: E402

page_setup("Usability Validation")
render_sidebar_about()

df = load_csv("usability_testing_analysis_ready.csv")

st.title("Usability testing validation")
st.caption("Task success · errors · time · frustration · help requests")

with st.sidebar:
    st.header("Filters")
    tasks = sorted(df["task_name"].dropna().unique().tolist())
    devices = sorted(df["device_type"].dropna().unique().tolist())
    selected_tasks = st.multiselect("Tasks", tasks, default=tasks)
    selected_devices = st.multiselect("Device", devices, default=devices)

filtered = df[df["task_name"].isin(selected_tasks) & df["device_type"].isin(selected_devices)]
if filtered.empty:
    st.warning("No rows match the selected filters.")
    st.stop()

completion = filtered["task_success"].mean() * 100
mean_errors = filtered["error_count"].mean()
mean_frustration = filtered["frustration_level"].mean()
help_rate = filtered["help_requested"].mean() * 100
mean_sat = filtered["satisfaction_score"].mean()

decision_banner(
    "Validate the highest-error / highest-frustration tasks before expanding the study scope.",
    [
        "Use task-level success and error counts to rank redesign candidates.",
        "Help requests and frustration mark where the UI is not self-explanatory.",
        "Compare devices to see if friction is platform-specific.",
    ],
    severity="Medium",
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Sessions", f"{len(filtered):,}")
k2.metric("Task success", f"{completion:.1f}%")
k3.metric("Avg errors", f"{mean_errors:.2f}")
k4.metric("Help requested", f"{help_rate:.1f}%")
k5.metric("Satisfaction", f"{mean_sat:.2f}")
section_caption("How to read: success without low errors/frustration still means a painful path.")

st.markdown("### Task friction ranking")
task_summary = (
    filtered.groupby("task_name", as_index=False)
    .agg(
        sessions=("participant_id", "count"),
        success_rate=("task_success", "mean"),
        avg_errors=("error_count", "mean"),
        avg_time_s=("completion_time_s", "mean"),
        avg_frustration=("frustration_level", "mean"),
        help_rate=("help_requested", "mean"),
        avg_satisfaction=("satisfaction_score", "mean"),
    )
    .sort_values(["avg_errors", "avg_frustration"], ascending=False)
)
task_summary["success_rate"] = (task_summary["success_rate"] * 100).round(1)
task_summary["help_rate"] = (task_summary["help_rate"] * 100).round(1)
task_summary = task_summary.round({"avg_errors": 2, "avg_time_s": 1, "avg_frustration": 2, "avg_satisfaction": 2})
st.dataframe(task_summary, use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.markdown("#### Errors by task")
    fig = px.bar(task_summary, x="task_name", y="avg_errors", labels={"task_name": "Task", "avg_errors": "Avg errors"})
    fig.update_layout(height=380, margin=dict(t=30), xaxis_tickangle=-25)
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("#### Frustration by outcome")
    fig = px.box(
        filtered,
        x="task_success_label",
        y="frustration_level",
        color="task_success_label",
        labels={"task_success_label": "Outcome", "frustration_level": "Frustration"},
    )
    fig.update_layout(showlegend=False, height=380, margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Success vs failure (key metrics)")
rows = []
for metric, label in [
    ("error_count", "Errors"),
    ("completion_time_s", "Completion time (s)"),
    ("frustration_level", "Frustration"),
    ("satisfaction_score", "Satisfaction"),
]:
    success = filtered.loc[filtered["task_success"] == 1, metric]
    failure = filtered.loc[filtered["task_success"] == 0, metric]
    _, p_value = stats.ttest_ind(success, failure, equal_var=False, nan_policy="omit")
    rows.append(
        {
            "Metric": label,
            "Completed (mean)": round(float(success.mean()), 2),
            "Failed (mean)": round(float(failure.mean()), 2),
            "Significant?": "Yes" if p_value < 0.05 else "No",
            "p-value": f"{p_value:.3g}",
        }
    )
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("### Method")
st.markdown(
    """
**Study type:** usability testing log (task, success, errors, time, frustration, help, satisfaction).  
**Pipeline:** `src/clean_usability_testing.py` → `data/processed/usability_testing_analysis_ready.csv`.  
**Honesty:** educational synthetic data (Rafiei / PUX), not a live product study.
"""
)
