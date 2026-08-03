"""Entrypoint for Streamlit Cloud / local: explicit multipage navigation."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Quant UX Validation Suite",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

home = st.Page("home.py", title="Home", icon="🏠", default=True)
survey = st.Page("pages/1_Survey_Validation.py", title="Survey Validation", icon="📋")
usability = st.Page("pages/2_Usability_Testing.py", title="Usability Testing", icon="🧪")
ab = st.Page("pages/3_AB_Experiment.py", title="A/B Experiment", icon="⚖️")

pg = st.navigation([home, survey, usability, ab])
pg.run()
