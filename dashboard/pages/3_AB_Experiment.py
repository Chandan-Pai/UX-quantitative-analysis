from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
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

df = load_csv("ab_testing_analysis_ready.csv")

st.title("A/B experiment validation")
st.caption("Variant comparison · conversion · engagement · experience quality proxies")

with st.container(border=True):
    filter_bar()
    f1, f2 = st.columns(2)
    with f1:
        selected_devices = multiselect_all(
            "Device type",
            sorted(df["device_type"].dropna().unique().tolist()),
            key="ab_devices",
        )
    with f2:
        selected_countries = multiselect_all(
            "Country",
            sorted(df["country"].dropna().unique().tolist()),
            key="ab_countries",
        )

filtered = df[df["device_type"].isin(selected_devices) & df["country"].isin(selected_countries)]
if filtered.empty:
    st.warning("No rows match the selected filters.")
    st.stop()

summary = (
    filtered.groupby("variant", as_index=False)
    .agg(
        users=("user_id", "count"),
        conversion_rate=("conversion", "mean"),
        avg_clicks=("click_count", "mean"),
        avg_load_ms=("page_load_time_ms", "mean"),
        avg_session_s=("session_length_s", "mean"),
        avg_revenue=("revenue_usd", "mean"),
        avg_bounce=("bounce_rate_pct", "mean"),
    )
    .sort_values("variant")
)

variants = summary["variant"].tolist()
headline = "Compare conversion and experience proxies before declaring a winner."
bullets = [
    "Lead with conversion rate, then check bounce / load time so a 'win' is not a worse experience.",
    "Segment by device if one variant only helps a subset of users.",
    "Treat revenue as supporting evidence when conversion is close.",
]
severity = "Medium"

if set(["A", "B"]).issubset(set(filtered["variant"].unique())):
    a = filtered.loc[filtered["variant"] == "A", "conversion"]
    b = filtered.loc[filtered["variant"] == "B", "conversion"]
    _, p_value = stats.ttest_ind(a, b, equal_var=False, nan_policy="omit")
    rate_a = float(a.mean())
    rate_b = float(b.mean())
    lift = (rate_b - rate_a) / rate_a * 100 if rate_a else np.nan
    winner = "B" if rate_b > rate_a else "A"
    if p_value < 0.05:
        headline = (
            f"Variant **{winner}** leads on conversion "
            f"(A {rate_a:.1%} vs B {rate_b:.1%}, lift {lift:+.1f}% toward B). Difference looks significant."
        )
        severity = "High"
        bullets = [
            f"Ship-oriented read: prefer {winner} on conversion, then confirm bounce and load time are not worse.",
            "Check device segments so the win is not driven by one platform only.",
            "Document sample size and that this is educational synthetic traffic, not a live experiment.",
        ]
    else:
        headline = (
            f"Conversion is close (A {rate_a:.1%} vs B {rate_b:.1%}). "
            "Do not call a product winner on conversion alone yet."
        )
        severity = "Low"
        bullets = [
            "Look at bounce, session length, and load time for directional UX risk.",
            "Consider longer runtime / larger sample before a ship decision (in a real experiment).",
            "Use segments to see if either variant helps a critical audience.",
        ]

decision_banner(headline, bullets, severity=severity)

st.markdown("### Snapshot (filtered sample)")
k1, k2, k3, k4 = st.columns(4)
overall_conv = filtered["conversion"].mean() * 100
k1.metric("Users in view", f"{len(filtered):,}")
k2.metric("Overall conversion", f"{overall_conv:.1f}%", help="% of users who converted")
k3.metric("Variants in data", ", ".join(str(v) for v in variants))
k4.metric("Avg bounce rate", f"{filtered['bounce_rate_pct'].mean():.1f}%", help="Higher bounce usually means weaker engagement")

st.markdown("### Variant scorecard")
section_caption(
    "Conversion % = share who converted. Bounce % = experience/quality guard. Load time = performance proxy."
)
show = summary.copy()
show["conversion_rate"] = (show["conversion_rate"] * 100).round(2)
show = show.round(
    {
        "avg_clicks": 2,
        "avg_load_ms": 1,
        "avg_session_s": 1,
        "avg_revenue": 2,
        "avg_bounce": 1,
    }
)
show = show.rename(
    columns={
        "variant": "Variant",
        "users": "Users",
        "conversion_rate": "Conversion %",
        "avg_clicks": "Avg clicks",
        "avg_load_ms": "Avg page load (ms)",
        "avg_session_s": "Avg session (sec)",
        "avg_revenue": "Avg revenue (USD)",
        "avg_bounce": "Avg bounce %",
    }
)
st.dataframe(show, use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.markdown("#### Conversion rate by variant")
    fig = px.bar(
        show,
        x="Variant",
        y="Conversion %",
        text="Conversion %",
        labels={"Variant": "Experiment variant", "Conversion %": "Conversion rate (%)"},
    )
    style_fig(fig, "Conversion rate (%)", "Experiment variant", height=400)
    labeled_bar(fig, ".2f")
    st.plotly_chart(fig, use_container_width=True)
    section_caption("Higher bar = more users completed the conversion goal.")
with right:
    st.markdown("#### Bounce rate distribution by variant")
    fig = px.box(
        filtered,
        x="variant",
        y="bounce_rate_pct",
        color="variant",
        labels={"variant": "Experiment variant", "bounce_rate_pct": "Bounce rate (%)"},
    )
    style_fig(fig, "Bounce rate (%)", "Experiment variant", height=400)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    section_caption("If the “winning” variant also bounces more, dig before shipping.")

st.markdown("### Device segments — conversion %")
seg = (
    filtered.groupby(["variant", "device_type"], as_index=False)["conversion"]
    .mean()
    .assign(**{"Conversion %": lambda d: (d["conversion"] * 100).round(2)})
)
fig = px.bar(
    seg,
    x="device_type",
    y="Conversion %",
    color="variant",
    barmode="group",
    text="Conversion %",
    labels={"device_type": "Device", "Conversion %": "Conversion rate (%)", "variant": "Variant"},
)
style_fig(fig, "Conversion rate (%)", "Device", height=420)
labeled_bar(fig, ".2f")
st.plotly_chart(fig, use_container_width=True)
section_caption("Grouped bars: compare Variant A vs B inside each device.")

st.markdown("### Method")
st.markdown(
    """
**Study type:** A/B experiment log (variant, conversion, clicks, load time, session, revenue, bounce).  
**Pipeline:** `src/clean_ab_testing.py` → this page.  
**Stats note:** significance check is educational, not a full sequential experiment design.  
**Honesty:** synthetic educational traffic (Rafiei / PUX).
"""
)
