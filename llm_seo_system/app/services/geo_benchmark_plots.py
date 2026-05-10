"""Matplotlib figures for benchmark batches (headless-safe)."""

from __future__ import annotations

import os
from typing import Any, Dict, List


def save_benchmark_plots(
    results: List[Dict[str, Any]],
    out_dir: str,
    prefix: str = "benchmark",
) -> List[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)
    paths: List[str] = []

    coverages: List[float] = []
    deltas: List[float] = []
    finals_v2: List[float] = []

    for r in results:
        c = r.get("coverage")
        if c is None:
            mr = r.get("measurement_report") or {}
            c = (mr.get("serp") or {}).get("coverage")
        coverages.append(float(c) if c is not None else 0.0)
        d = r.get("delta")
        deltas.append(float(d) if d is not None else 0.0)
        finals_v2.append(float(r.get("final_score_v2") or 0))

    # Coverage × Δ (behavioral shift vs competition proxy)
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.scatter(coverages, deltas, alpha=0.75, c="#7c3aed", edgecolors="white", linewidths=0.5)
    ax.set_xlabel("SERP coverage (competition)")
    ax.set_ylabel("Δ mention rate (LLM)")
    ax.set_title("Opportunity map — coverage vs Δ")
    ax.grid(True, alpha=0.25)
    p1 = os.path.join(out_dir, f"{prefix}_coverage_vs_delta.png")
    fig.savefig(p1, dpi=130, bbox_inches="tight")
    plt.close(fig)
    paths.append(p1)

    # Coverage × final_score_v2
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.scatter(coverages, finals_v2, alpha=0.75, c="#059669", edgecolors="white", linewidths=0.5)
    ax.set_xlabel("Competition (SERP coverage)")
    ax.set_ylabel("Opportunity (final_score_v2)")
    ax.set_title("Opportunity map — coverage vs product score v2")
    ax.grid(True, alpha=0.25)
    p2 = os.path.join(out_dir, f"{prefix}_coverage_vs_score_v2.png")
    fig.savefig(p2, dpi=130, bbox_inches="tight")
    plt.close(fig)
    paths.append(p2)

    return paths
