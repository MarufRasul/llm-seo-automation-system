"""
Streamlit: visualize ``benchmark_results.json`` from ``outputs/benchmarks/*/``.

Run from repo / llm_seo_system with PYTHONPATH set:

  cd llm_seo_system && streamlit run geo_dashboard.py
"""

from __future__ import annotations

import json
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _ROOT)

import streamlit as st

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def main() -> None:
    st.set_page_config(page_title="GEO Opportunity Dashboard", layout="wide")
    st.title("GEO Opportunity Dashboard")
    st.caption("Research-grade batch view: SERP + Δ + confidence + final_score_v2")

    uploaded = st.file_uploader("Load benchmark_results.json", type=["json"])
    path = st.text_input(
        "Or path to benchmark_results.json",
        value="",
        placeholder=os.path.join(_ROOT, "outputs", "benchmarks", "…", "benchmark_results.json"),
    )

    raw = None
    if uploaded is not None:
        raw = json.loads(uploaded.read().decode("utf-8"))
    elif path.strip() and os.path.isfile(path.strip()):
        with open(path.strip(), encoding="utf-8") as f:
            raw = json.load(f)

    if not raw:
        st.info("Upload a JSON file or paste a valid path from a benchmark run.")
        return

    summary = raw.get("summary") or {}
    st.subheader("Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Queries", summary.get("n_queries", "—"))
    c2.metric("Avg Δ (0–1)", summary.get("avg_delta_01", "—"))
    c3.metric("Avg confidence", summary.get("avg_confidence", "—"))
    wl = summary.get("weights_learned")
    c4.metric("Adaptive weights", str(wl) if wl else "fixed v2")

    ranked = raw.get("ranked_by_v2") or raw.get("results") or []
    st.subheader("Ranked topics")
    for r in ranked[:30]:
        fs = float(r.get("final_score_v2") or r.get("final_score") or 0)
        with st.container():
            st.metric(label=r.get("query", ""), value=f"{fs:.3f}")
            st.progress(min(max(fs, 0.0), 1.0))

    cov = []
    delt = []
    fv2 = []
    for r in ranked:
        cov.append(float(r.get("coverage") or 0))
        d = r.get("delta")
        delt.append(float(d) if d is not None else 0.0)
        fv2.append(float(r.get("final_score_v2") or r.get("final_score") or 0))

    if plt and cov:
        st.subheader("Opportunity maps")
        fig1, ax1 = plt.subplots(figsize=(7, 5))
        ax1.scatter(cov, delt, alpha=0.7, c="#7c3aed")
        ax1.set_xlabel("SERP coverage")
        ax1.set_ylabel("Δ")
        ax1.set_title("Coverage vs Δ")
        ax1.grid(True, alpha=0.3)
        st.pyplot(fig1)
        plt.close(fig1)

        fig2, ax2 = plt.subplots(figsize=(7, 5))
        ax2.scatter(cov, fv2, alpha=0.7, c="#059669")
        ax2.set_xlabel("SERP coverage")
        ax2.set_ylabel("final_score_v2")
        ax2.set_title("Coverage vs opportunity score")
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)
        plt.close(fig2)

    out_dir = raw.get("output_dir")
    if out_dir:
        st.subheader("Artifacts")
        st.code(out_dir, language="text")


if __name__ == "__main__":
    main()
