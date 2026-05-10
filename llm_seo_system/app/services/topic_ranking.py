"""
Topic ranking: combine SERP + Δ + impact into one score (Ahrefs/Surfer-style prioritization).
"""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List, Optional


def _serp_final(serp_metrics: Dict[str, Any]) -> float:
    coverage = float(serp_metrics.get("coverage", 0.0))
    first_rank = int(serp_metrics.get("first_rank", 999))
    serp_score = 1.0 - max(0.0, min(1.0, coverage))
    rank_score = (1.0 / first_rank) if first_rank < 999 else 0.0
    return 0.7 * serp_score + 0.3 * rank_score


def _delta_for_formula(measurement_report: Dict[str, Any]) -> float:
    """Map delta_mention_rate (≈ [-1, 1]) to [0, 1] for weighted sum."""
    raw = measurement_report.get("delta_mention_rate")
    if raw is None:
        return 0.0
    d = float(raw)
    d = max(-1.0, min(1.0, d))
    return (d + 1.0) / 2.0


def compute_rank_score(
    serp_metrics: Dict[str, Any],
    measurement_report: Dict[str, Any],
    impact_score: float,
) -> float:
    """
    Same structure as product opportunity score (ranking batch uses impact=0 unless provided).

    final = 0.5 * serp_final + 0.3 * delta_01 + 0.2 * impact
    """
    serp_final = _serp_final(serp_metrics or {})
    delta_01 = _delta_for_formula(measurement_report or {})
    imp = max(0.0, min(1.0, float(impact_score)))

    final = 0.5 * serp_final + 0.3 * delta_01 + 0.2 * imp
    return round(max(0.0, min(1.0, final)), 3)


def decision_label(final_score: float) -> str:
    if final_score > 0.8:
        return "PRIORITY"
    if final_score > 0.6:
        return "GOOD"
    return "LOW"


def build_rank_row(
    query: str,
    gap_score: float,
    serp_metrics: Dict[str, Any],
    measurement_report: Dict[str, Any],
    impact_score: float,
) -> Dict[str, Any]:
    fs = compute_rank_score(serp_metrics, measurement_report, impact_score)
    lb = (measurement_report or {}).get("llm_baseline") or {}
    lc = (measurement_report or {}).get("llm_with_external_context") or {}
    return {
        "query": query,
        "final_score": fs,
        "gap_score": round(float(gap_score), 3),
        "coverage": serp_metrics.get("coverage"),
        "first_rank": serp_metrics.get("first_rank"),
        "delta": (measurement_report or {}).get("delta_mention_rate"),
        "baseline_mr": lb.get("mention_rate"),
        "context_mr": lc.get("mention_rate"),
        "impact": impact_score,
        "decision": decision_label(fs),
        "serp_final": round(_serp_final(serp_metrics or {}), 4),
    }


def rank_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(rows, key=lambda x: x.get("final_score", 0), reverse=True)


def ranked_to_csv_string(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return ""
    fieldnames = list(rows[0].keys())
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def print_opportunities_table(ranked: List[Dict[str, Any]], limit: int = 20) -> None:
    print("\n=== TOP OPPORTUNITIES ===\n")
    for r in ranked[:limit]:
        fs = r.get("final_score", 0)
        sym = "🔥 PRIORITY" if fs > 0.8 else "✅ GOOD" if fs > 0.6 else "⚠️ LOW"
        print(f"{r.get('query')}")
        print(
            f"  score: {fs} | Δ: {r.get('delta')} | coverage: {r.get('coverage')} | → {sym}\n",
        )
