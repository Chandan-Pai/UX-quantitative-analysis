from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ui import decision_banner, load_csv, page_setup, render_sidebar_about, section_caption  # noqa: E402

page_setup("A/B Experiment Validation")
render_sidebar_about()

df = load_csv("ab_testing_analysis_ready.csv")

st.title("A/B experiment validation")
st.caption("Variant comparison · conversion · engagement · experience quality proxies")

with st.sidebar:
    st.header("Filters")
    devices = sorted(df["device_type"].dropna().unique().tolist())
    countries = sorted(df["country"].dropna().unique().tolist())
    selected_devices = st.multiselect("Device", devices, default=devices)
    selected_countries = st.multiselect("Country", countries, default=countries)

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

# pairwise A vs B if present
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
    # proportions z-test style via ttest on binary as quick educational check
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

k1, k2, k3, k4 = st.columns(4)
overall_conv = filtered["conversion"].mean() * 100
k1.metric("Users (filtered)", f"{len(filtered):,}")
k2.metric("Overall conversion", f"{overall_conv:.1f}%")
k3.metric("Variants", ", ".join(variants))
k4.metric("Avg bounce %", f"{filtered['bounce_rate_pct'].mean():.1f}")

st.markdown("### Variant scorecard")
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
st.dataframe(show, use_container_width=True, hide_index=True)
section_caption("Conversion is primary. Bounce and load time are experience / quality guards.")

left, right = st.columns(2)
with left:
    st.markdown("#### Conversion by variant")
    fig = px.bar(
        show,
        x="variant",
        y="conversion_rate",
        text="conversion_rate",
        labels={"variant": "Variant", "conversion_rate": "Conversion %"},
    )
    fig.update_layout(height=380, margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("#### Bounce rate by variant")
    fig = px.box(
        filtered,
        x="variant",
        y="bounce_rate_pct",
        color="variant",
        labels={"variant": "Variant", "bounce_rate_pct": "Bounce rate %"},
    )
    fig.update_layout(showlegend=False, height=380, margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Device segments (conversion)")
seg = (
    filtered.groupby(["variant", "device_type"], as_index=False)["conversion"]
    .mean()
    .assign(conversion_pct=lambda d: d["conversion"] * 100)
)
fig = px.bar(
    seg,
    x="device_type",
    y="conversion_pct",
    color="variant",
    barmode="group",
    labels={"device_type": "Device", "conversion_pct": "Conversion %"},
)
fig.update_layout(height=380, margin=dict(t=30))
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Method")
st.markdown(
    """
**Study type:** A/B experiment log (variant, conversion, clicks, load time, session, revenue, bounce).  
**Pipeline:** `src/clean_ab_testing.py` → `data/processed/ab_testing_analysis_ready.csv`.  
**Stats note:** significance here is an educational check on conversion rates, not a full sequential experiment design.  
**Honesty:** synthetic educational traffic (Rafiei / PUX).
"""
)
