"""Shared Streamlit UI helpers for the Quant UX Validation Suite."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

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


def render_attribution() -> None:
    st.info(ATTRIBUTION_MD)


def render_sidebar_about() -> None:
    with st.sidebar:
        st.markdown("### Quant UX Validation Suite")
        st.caption("Use the links above to switch studies.")
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
    st.markdown("### Validation decision")
    st.markdown(f"**{headline}**")
    cols = st.columns([1, 3])
    cols[0].metric("Priority", severity)
    with cols[1]:
        for item in bullets:
            st.markdown(f"- {item}")


def section_caption(text: str) -> None:
    st.caption(text)


def filter_bar(title: str = "Filters (applies to every chart below)") -> None:
    st.markdown(f"#### {title}")
    st.caption("Add or remove values to update KPIs and graphs. Leave all selected to see the full sample.")


def style_fig(fig, y_title: str, x_title: str, height: int = 400):
    fig.update_layout(
        height=height,
        margin=dict(t=40, b=60, l=60, r=20),
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend_title_text="",
        font=dict(size=13),
    )
    fig.update_xaxes(title_font=dict(size=13), tickfont=dict(size=12))
    fig.update_yaxes(title_font=dict(size=13), tickfont=dict(size=12))
    return fig


def labeled_bar(fig, fmt: str = ".1f"):
    fig.update_traces(texttemplate="%{text:" + fmt + "}", textposition="outside", cliponaxis=False)
    return fig


def multiselect_all(label: str, options: Iterable, key: str) -> list:
    options = list(options)
    return st.multiselect(label, options, default=options, key=key)
