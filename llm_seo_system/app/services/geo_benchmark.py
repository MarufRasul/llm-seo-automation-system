"""
Batch GEO benchmark: 20–50 fixed queries → SERP + measurement + scores + plots metadata.

Does not run full article generation per query (use ``rank_topics_for_niche`` / GEO pipeline for that).
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.agents.presence_measurement import build_measurement_report
from app.services.scoring_v2 import enrich_row_scores_v2, learn_weights
from app.services.topic_ranking import (
    _delta_for_formula,
    build_rank_row,
    ranked_to_csv_string,
)


DEFAULT_BENCHMARK_QUERIES: List[str] = [
    "best laptop for students",
    "best lightweight laptop",
    "best laptop for college",
    "best laptop under $1000",
    "best ultrabook 2026",
    "best laptop for programming",
    "best laptop for video editing",
    "best business laptop 2026",
    "best 2-in-1 laptop",
    "best laptop battery life",
    "best laptop for travel",
    "best gaming laptop under 1500",
    "best macbook alternative",
    "best chromebook for students",
    "best laptop for writers",
    "best laptop with OLED display",
    "best laptop for photo editing",
    "best budget ultrabook",
    "best laptop for streaming",
    "best laptop for architects",
]


def run_benchmark(
    queries: List[str],
    brand: str,
    gap_finder: Any,
    *,
    include_measurement: bool = True,
    use_gap_as_impact: bool = True,
    use_adaptive_weights: bool = True,
) -> Dict[str, Any]:
    """
    For each query: SerpAPI/SERP → gap heuristics → optional LLM measurement → rank row.

    Passes #2: compute ``learn_weights`` from batch Δ₀₁, then ``final_score_v2`` per row.
    """
    brand = (brand or "").strip()
    if not brand:
        raise ValueError("brand is required")

    cleaned = [q.strip() for q in queries if (q or "").strip()]
    if not cleaned:
        raise ValueError("queries must be a non-empty list")

    gap_results = gap_finder.analyze(cleaned, target_brand=brand, max_queries=len(cleaned))
    max_gs = max((float(g.get("score") or 0) for g in gap_results), default=0.0)

    rows_intermediate: List[Dict[str, Any]] = []
    measurements: List[Dict[str, Any]] = []

    for item in gap_results:
        q = item.get("query") or ""
        organic = item.get("organic_results") or []
        serp_m = dict(item.get("serp_metrics") or {})
        gap_sc = float(item.get("score") or 0.0)

        measurement_report: Dict[str, Any] = {}
        if include_measurement:
            try:
                measurement_report = build_measurement_report(q, brand, organic)
                serp_from_mr = measurement_report.get("serp") or {}
                if serp_from_mr:
                    serp_m = serp_from_mr
            except Exception as exc:
                measurement_report = {"error": str(exc), "delta_mention_rate": None}

        impact = 0.0
        if use_gap_as_impact and max_gs > 0:
            impact = min(1.0, gap_sc / max_gs)

        row = build_rank_row(q, gap_sc, serp_m, measurement_report, impact)
        rows_intermediate.append(row)
        measurements.append(measurement_report)

    delta_01_list = [_delta_for_formula(m) for m in measurements]
    triple = learn_weights(delta_01_list) if use_adaptive_weights else None

    enriched: List[Dict[str, Any]] = []
    for row, mr in zip(rows_intermediate, measurements):
        er = enrich_row_scores_v2(row, mr, triple)
        er["measurement_report"] = mr
        er["gap_analysis_score"] = row.get("gap_score")
        enriched.append(er)

    ranked = sorted(enriched, key=lambda x: x.get("final_score_v2", 0), reverse=True)

    slim_for_csv = [{k: v for k, v in r.items() if k != "measurement_report"} for r in ranked]

    summary = {
        "n_queries": len(cleaned),
        "avg_delta_01": round(sum(delta_01_list) / len(delta_01_list), 4)
        if delta_01_list
        else 0.0,
        "avg_confidence": round(
            sum(r.get("confidence") or 0 for r in enriched) / max(len(enriched), 1),
            4,
        ),
        "weights_learned": list(triple) if triple else None,
        "use_adaptive_weights": use_adaptive_weights,
    }

    return {
        "brand": brand,
        "benchmark_queries": cleaned,
        "gap_queries_analyzed": len(gap_results),
        "results": enriched,
        "ranked_by_v2": ranked,
        "summary": summary,
        "csv": ranked_to_csv_string(slim_for_csv),
    }


def save_benchmark_json(payload: Dict[str, Any], directory: str) -> str:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "benchmark_results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def benchmark_output_dir(repo_root: Optional[str] = None) -> str:
    """``llm_seo_system/outputs/benchmarks/<utc_timestamp>``."""
    here = os.path.dirname(os.path.abspath(__file__))
    llm_root = repo_root or os.path.dirname(
        os.path.dirname(os.path.dirname(here)),
    )
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return os.path.join(llm_root, "outputs", "benchmarks", stamp)
