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

df = load_csv("usability_testing_analysis_ready.csv")

st.title("Usability testing validation")
st.caption("Task success · errors · time · frustration · help requests")

with st.container(border=True):
    filter_bar()
    f1, f2 = st.columns(2)
    with f1:
        selected_tasks = multiselect_all(
            "Tasks to include",
            sorted(df["task_name"].dropna().unique().tolist()),
            key="usability_tasks",
        )
    with f2:
        selected_devices = multiselect_all(
            "Device type",
            sorted(df["device_type"].dropna().unique().tolist()),
            key="usability_devices",
        )

filtered = df[df["task_name"].isin(selected_tasks) & df["device_type"].isin(selected_devices)]
if filtered.empty:
    st.warning("No rows match the selected filters.")
    st.stop()

completion = filtered["task_success"].mean() * 100
mean_errors = filtered["error_count"].mean()
help_rate = filtered["help_requested"].mean() * 100
mean_sat = filtered["satisfaction_score"].mean()
mean_frustration = filtered["frustration_level"].mean()

decision_banner(
    "Validate the highest-error / highest-frustration tasks before expanding the study scope.",
    [
        "Use task-level success and error counts to rank redesign candidates.",
        "Help requests and frustration mark where the UI is not self-explanatory.",
        "Compare devices to see if friction is platform-specific.",
    ],
    severity="Medium",
)

st.markdown("### Snapshot (filtered sample)")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Sessions in view", f"{len(filtered):,}")
k2.metric("Task success", f"{completion:.1f}%", help="% of sessions that completed the task")
k3.metric("Avg errors / session", f"{mean_errors:.2f}", help="Average number of errors recorded per session")
k4.metric("Asked for help", f"{help_rate:.1f}%", help="% of sessions that requested help")
k5.metric("Avg satisfaction", f"{mean_sat:.2f} / 7", help="1 = low, 7 = high")
section_caption(
    f"Also tracking average frustration = **{mean_frustration:.2f}** (higher = more frustrated)."
)

st.markdown("### Task friction ranking")
section_caption("Sorted by most errors, then frustration. Top rows are redesign candidates.")
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
display = task_summary.copy()
display["success_rate"] = (display["success_rate"] * 100).round(1)
display["help_rate"] = (display["help_rate"] * 100).round(1)
display = display.round(
    {"avg_errors": 2, "avg_time_s": 1, "avg_frustration": 2, "avg_satisfaction": 2}
)
display = display.rename(
    columns={
        "task_name": "Task",
        "sessions": "Sessions",
        "success_rate": "Success %",
        "avg_errors": "Avg errors",
        "avg_time_s": "Avg time (sec)",
        "avg_frustration": "Avg frustration",
        "help_rate": "Help requested %",
        "avg_satisfaction": "Avg satisfaction (1–7)",
    }
)
st.dataframe(display, use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.markdown("#### Average errors by task")
    plot_df = display[["Task", "Avg errors"]].copy()
    fig = px.bar(
        plot_df,
        x="Task",
        y="Avg errors",
        text="Avg errors",
        labels={"Task": "Task name", "Avg errors": "Average errors per session"},
    )
    labeled_bar(fig, ".2f")
    style_fig(fig, "Average errors per session", "Task name", height=420)
    fig.update_layout(xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("#### Frustration when people completed vs failed")
    fig = px.box(
        filtered,
        x="task_success_label",
        y="frustration_level",
        color="task_success_label",
        labels={
            "task_success_label": "Did they finish the task?",
            "frustration_level": "Frustration level (higher = worse)",
        },
    )
    style_fig(fig, "Frustration level (higher = worse)", "Did they finish the task?", height=420)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    section_caption("If the Failed box sits higher, failure is emotionally costly — not just a binary miss.")

st.markdown("### Completed vs failed — mean differences")
rows = []
for metric, label, note in [
    ("error_count", "Errors per session", "lower better"),
    ("completion_time_s", "Time (seconds)", "lower usually better"),
    ("frustration_level", "Frustration", "lower better"),
    ("satisfaction_score", "Satisfaction (1–7)", "higher better"),
]:
    success = filtered.loc[filtered["task_success"] == 1, metric]
    failure = filtered.loc[filtered["task_success"] == 0, metric]
    _, p_value = stats.ttest_ind(success, failure, equal_var=False, nan_policy="omit")
    rows.append(
        {
            "What we measured": label,
            "Better direction": note,
            "Avg if completed": round(float(success.mean()), 2),
            "Avg if failed": round(float(failure.mean()), 2),
            "Statistically different?": "Yes (p < 0.05)" if p_value < 0.05 else "No",
        }
    )
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("### Method")
st.markdown(
    """
**Study type:** usability testing log (task, success, errors, time, frustration, help, satisfaction).  
**Pipeline:** `src/clean_usability_testing.py` → this page.  
**Honesty:** educational synthetic data (Rafiei / PUX).
"""
)
