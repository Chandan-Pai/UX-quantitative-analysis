from __future__ import annotations

import streamlit as st

from ui import page_setup, render_attribution, render_sidebar_about

page_setup("Quant UX Validation Suite")
render_sidebar_about()

st.title("Quant UX Validation Suite")
st.caption(
    "A portfolio hub for quantitative UX validation: clean educational datasets, "
    "compare outcomes, and turn metrics into product decisions."
)
render_attribution()

st.success(
    "**Open a study from the left sidebar:** "
    "Survey Validation · Usability Testing · A/B Experiment"
)

st.markdown("### What this suite is for")
st.markdown(
    """
Hiring managers and research partners often ask: *can you run quant validation end to end?*
This app shows that motion across study types:

1. **Survey validation** — SUS / trust / workload vs task success, with a predictive check
2. **Usability testing** — errors, time, frustration, help requests by task and device
3. **A/B experiment** — conversion and engagement by variant (decision-oriented readout)

Each page follows the same story: **decision → KPIs → where it breaks → segments → method**.
"""
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("#### Survey")
    st.write("Post-task questionnaire + task success modeling.")
    st.caption("Sidebar → Survey Validation")
with c2:
    st.markdown("#### Usability")
    st.write("Moderated-style task metrics and friction signals.")
    st.caption("Sidebar → Usability Testing")
with c3:
    st.markdown("#### A/B test")
    st.write("Variant comparison for conversion and session quality.")
    st.caption("Sidebar → A/B Experiment")

st.markdown("### Pipeline (what runs behind the scenes)")
st.markdown(
    """
```
raw educational CSV  →  clean script (src/)  →  analysis-ready CSV  →  Streamlit readout
```
Re-run cleaners after adding a new dataset from the same Rafiei / PUX collection, then add a page.
Recommender / ML systems work stays in a **separate** repo so this suite stays research-decision focused.
"""
)

st.markdown("### How to read any page")
st.markdown(
    """
- **Decision banner** = what to do next (not just charts)
- **KPIs** = health of the experience
- **Breaks / segments** = who struggles and on which surface
- **Method** = sample, instruments, honesty limits (synthetic educational data)
"""
)
