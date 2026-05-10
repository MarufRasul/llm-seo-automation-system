"""
Research-grade scoring: adaptive weights, evaluator agreement (confidence), final_score_v2.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence, Tuple

from app.services.topic_ranking import _delta_for_formula


def learn_weights(delta_01_values: Sequence[float]) -> Tuple[float, float, float]:
    """
    Adapt (w_serp, w_delta, w_impact) from batch mean Δ on [0,1].
    Intended use: rescale with ``combine_weights_with_confidence`` so total + conf = 1.0.
    """
    vals = [float(x) for x in delta_01_values if x is not None]
    if not vals:
        return (0.5, 0.3, 0.2)
    avg_delta = sum(vals) / len(vals)
    if avg_delta < 0.3:
        return (0.6, 0.2, 0.2)
    if avg_delta > 0.7:
        return (0.4, 0.4, 0.2)
    return (0.5, 0.3, 0.2)


def combine_weights_with_confidence(
    w_serp: float,
    w_delta: float,
    w_impact: float,
    conf_weight: float = 0.1,
) -> Tuple[float, float, float, float]:
    """Scale SERP/Δ/impact so they sum to (1 - conf_weight)."""
    s = max(w_serp + w_delta + w_impact, 1e-9)
    target = 1.0 - conf_weight
    scale = target / s
    return (
        w_serp * scale,
        w_delta * scale,
        w_impact * scale,
        conf_weight,
    )


def compute_confidence(measurement_report: Dict[str, Any] | None) -> float:
    """
    Share of evaluators that mention the brand (context channel preferred; else baseline).
    1.0 = all models agree (all mention); 0.0 = none or no evaluators.
    """
    mr = measurement_report or {}
    ctx = mr.get("llm_with_external_context") or {}
    base = mr.get("llm_baseline") or {}
    by = ctx.get("by_model") or base.get("by_model") or {}
    if not by:
        return 0.0
    vals = list(by.values())
    return sum(1.0 for v in vals if v) / len(vals)


def final_score_v2(
    serp_final: float,
    delta_01: float,
    impact: float,
    confidence: float,
    weights_serp_delta_impact: Tuple[float, float, float] | None = None,
    conf_weight: float = 0.1,
) -> float:
    """
    Default fixed blend (when weights_serp_delta_impact is None):
      0.4*serp + 0.3*delta + 0.2*impact + 0.1*conf

    When adaptive triple is passed, it is rescaled with ``combine_weights_with_confidence``.
    """
    serp_final = max(0.0, min(1.0, float(serp_final)))
    delta_01 = max(0.0, min(1.0, float(delta_01)))
    impact = max(0.0, min(1.0, float(impact)))
    confidence = max(0.0, min(1.0, float(confidence)))

    if weights_serp_delta_impact is None:
        w_s, w_d, w_i, w_c = 0.4, 0.3, 0.2, conf_weight
        if abs(w_s + w_d + w_i + w_c - 1.0) > 1e-6:
            w_s, w_d, w_i = 0.4, 0.3, 0.2
            w_c = 0.1
    else:
        ws, wd, wi = weights_serp_delta_impact
        w_s, w_d, w_i, w_c = combine_weights_with_confidence(ws, wd, wi, conf_weight)

    out = w_s * serp_final + w_d * delta_01 + w_i * impact + w_c * confidence
    return round(max(0.0, min(1.0, out)), 3)


def enrich_row_scores_v2(
    row: Dict[str, Any],
    measurement_report: Dict[str, Any],
    weights_serp_delta_impact: Tuple[float, float, float] | None,
) -> Dict[str, Any]:
    """Mutates copy: adds confidence, weight tuple used, final_score_v2."""
    serp_f = float(row.get("serp_final") or 0.0)
    delta_01 = _delta_for_formula(measurement_report or {})
    imp = float(row.get("impact") or 0.0)
    conf = compute_confidence(measurement_report)

    fs2 = final_score_v2(serp_f, delta_01, imp, conf, weights_serp_delta_impact)
    out = {**row}
    out["delta_01"] = round(delta_01, 4)
    out["confidence"] = round(conf, 4)
    out["final_score_v2"] = fs2
    out["weights_serp_delta_impact"] = (
        list(weights_serp_delta_impact) if weights_serp_delta_impact else None
    )
    return out
