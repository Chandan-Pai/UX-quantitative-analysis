"""Shared Streamlit UI helpers for the Quant UX Validation Suite."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

ATTRIBUTION_MD = """
**Data credit (required):** Educational synthetic datasets from **Mohsen Rafiei, Ph.D.**,
*UX Datasets Collection* (2025), **Perceptual User Experience Lab (PUX Lab)**.
Source: [github.com/mohsen-rafiei/UX_datasets](https://github.com/mohsen-rafiei/UX_datasets).
**Not real product users.** Methods practice and portfolio demonstration only.
"""


def page_setup(title: str) -> None:
    st.set_page_config(
        page_title=title,
        page_icon="📐",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_attribution() -> None:
    st.info(ATTRIBUTION_MD)


def render_sidebar_about() -> None:
    with st.sidebar:
        st.markdown("### Quant UX Validation Suite")
        st.caption("Survey · Usability · A/B experiment readouts")
        st.markdown(ATTRIBUTION_MD)
        st.markdown(
            "[GitHub repo](https://github.com/Chandan-Pai/UX-quantitative-analysis) · "
            "Analysis by **Chandan Umesh Pai**"
        )


def load_csv(name: str) -> pd.DataFrame:
    path = PROCESSED / name
    if not path.exists():
        st.error(f"Missing processed data: `{name}`. Run the matching clean script under `src/`.")
        st.stop()
    return pd.read_csv(path)


def decision_banner(headline: str, bullets: list[str], severity: str = "Medium") -> None:
    st.markdown(f"### Validation decision")
    st.markdown(f"**{headline}**")
    cols = st.columns([1, 3])
    cols[0].metric("Priority", severity)
    with cols[1]:
        for item in bullets:
            st.markdown(f"- {item}")


def section_caption(text: str) -> None:
    st.caption(text)
