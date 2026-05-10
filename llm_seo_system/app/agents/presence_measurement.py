"""
Independent measurement channels (no generated article in evaluator prompts):

  Query → SERP metrics (objective)
        → optional: Tavily / SERP excerpts as external retrieval
        → LLM evaluators (baseline: query-only; test: query + external context only)

Rules:
  - Different prompts for baseline vs with-context (no prompt reuse).
  - ArticleAgent / pipeline draft is NEVER passed to these evaluators.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple

import requests

# Deprecated IDs (e.g. claude-3-haiku-20240307) return 404 — use a current Haiku/Sonnet ID.
# Aligns with LLMPresenceChecker; override via GEO_EVAL_ANTHROPIC_MODEL.
_DEFAULT_ANTHROPIC_EVAL_MODEL = "claude-haiku-4-5-20251001"


def _anthropic_eval_model() -> str:
    return os.getenv("GEO_EVAL_ANTHROPIC_MODEL", _DEFAULT_ANTHROPIC_EVAL_MODEL)


# --- SERP ---------------------------------------------------------------------

def brand_mentioned_in_text(text: str, brand: str) -> bool:
    t = (text or "").lower()
    b = (brand or "").strip().lower()
    if not b:
        return False
    if b in t:
        return True
    for token in b.split():
        if len(token) >= 2 and token.lower() in t:
            return True
    return False


def compute_serp_metrics(serp: List[Dict[str, Any]], brand: str) -> Dict[str, Any]:
    """
    Objective SERP coverage:
      coverage = (# organic rows where brand appears) / N
      first_rank = 1-based index of first hit (999 if none)
    """
    mentions = 0
    first_rank = None
    for i, r in enumerate(serp):
        blob = (r.get("title") or "") + " " + (r.get("snippet") or "")
        if brand_mentioned_in_text(blob, brand):
            mentions += 1
            if first_rank is None:
                first_rank = i + 1
    n = len(serp)
    denom = max(n, 1)
    return {
        "coverage": mentions / denom,
        "first_rank": first_rank if first_rank is not None else 999,
        "mentions": mentions,
        "n": n,
    }


# --- Retrieval (NOT your article) ---------------------------------------------

def retrieve_external_context(query: str, organic: List[Dict[str, Any]]) -> str:
    """
    External index: Tavily when configured; otherwise top organic snippets from SERP.
    """
    key = os.getenv("TAVILY_API_KEY")
    if key:
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": key,
                    "query": query,
                    "max_results": 5,
                    "include_answer": False,
                },
                timeout=20,
            )
            if resp.status_code == 200:
                data = resp.json()
                parts = []
                for i, r in enumerate(data.get("results") or [], start=1):
                    parts.append(
                        f"[{i}] {r.get('title', '')}\n{r.get('content', '')[:600]}",
                    )
                if parts:
                    return "\n\n".join(parts)
        except Exception as exc:
            print(f"  ⚠️ Tavily retrieval failed: {exc}")

    lines = []
    for i, r in enumerate((organic or [])[:7]):
        lines.append(
            f"[SERP {i + 1}] {r.get('title', '')}\n{r.get('snippet', '')}\n{r.get('link', '')}",
        )
    return "\n\n".join(lines) if lines else "(no external context available)"


# --- LLM evaluators (query-only baseline) ------------------------------------

def _openai_client():
    from openai import OpenAI

    return OpenAI()


def _anthropic_client():
    import anthropic

    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


def ask_openai_baseline(query: str, model: str | None = None) -> str:
    """Evaluator A: short list from query only (no article, no extra retrieval)."""
    model = model or os.getenv("GEO_EVAL_OPENAI_MODEL", "gpt-4o-mini")
    client = _openai_client()
    resp = client.chat.completions.create(
        model=model,
        temperature=0.3,
        messages=[
            {
                "role": "user",
                "content": (
                    "Task: recommend purchase options only from general knowledge.\n"
                    "Do not claim you browsed the web.\n"
                    f"List best options for: {query}\n"
                    "Keep it short (one short paragraph or bullet list)."
                ),
            },
        ],
    )
    msg = resp.choices[0].message.content
    return (msg or "").lower()


def ask_anthropic_baseline(query: str, model: str | None = None) -> str:
    """Evaluator B: different provider, same task shape, different wording."""
    model = model or _anthropic_eval_model()
    client = _anthropic_client()
    msg = client.messages.create(
        model=model,
        max_tokens=400,
        messages=[
            {
                "role": "user",
                "content": (
                    "Give a concise recommendation of suitable products or choices "
                    "for the user's need. No browsing claims.\n\n"
                    f"Need: {query}\n"
                    "Answer in a few sentences or short bullets."
                ),
            },
        ],
    )
    block = msg.content[0]
    text = getattr(block, "text", str(block))
    return text.lower()


def check_mention(answer: str, brand: str) -> bool:
    return brand_mentioned_in_text(answer, brand)


def evaluate_llm_baseline(query: str, brand: str) -> Tuple[Dict[str, bool], float]:
    results: Dict[str, bool] = {}
    if os.getenv("OPENAI_API_KEY"):
        try:
            oa_model = os.getenv("GEO_EVAL_OPENAI_MODEL", "gpt-4o-mini")
            ans = ask_openai_baseline(query, oa_model)
            results[f"openai:{oa_model}"] = check_mention(ans, brand)
        except Exception as e:
            print(f"  ⚠️ OpenAI baseline eval failed: {e}")
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            cl_model = _anthropic_eval_model()
            ans = ask_anthropic_baseline(query, cl_model)
            results[f"anthropic:{cl_model}"] = check_mention(ans, brand)
        except Exception as e:
            print(f"  ⚠️ Anthropic baseline eval failed: {e}")

    if not results:
        return {}, 0.0
    score = sum(results.values()) / len(results)
    return results, score


# --- LLM evaluators (external context — different prompts) --------------------

def ask_openai_with_context(query: str, context: str, model: str | None = None) -> str:
    model = model or os.getenv("GEO_EVAL_OPENAI_MODEL", "gpt-4o-mini")
    client = _openai_client()
    resp = client.chat.completions.create(
        model=model,
        temperature=0.3,
        messages=[
            {
                "role": "user",
                "content": (
                    "You are given excerpts from third-party pages (may be incomplete).\n"
                    "Use them only as supporting background; synthesize recommendations.\n\n"
                    f"--- BEGIN EXCERPTS ---\n{context[:12000]}\n--- END EXCERPTS ---\n\n"
                    f"Based on the excerpts and general reasoning, list strong options for: {query}\n"
                    "Keep it short."
                ),
            },
        ],
    )
    msg = resp.choices[0].message.content
    return (msg or "").lower()


def ask_anthropic_with_context(query: str, context: str, model: str | None = None) -> str:
    model = model or _anthropic_eval_model()
    client = _anthropic_client()
    msg = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": (
                    "Below are snippets from external sources (not authored by you).\n"
                    "Use them as context only and suggest suitable choices.\n\n"
                    f"--- SOURCES ---\n{context[:12000]}\n---\n\n"
                    f"Question: what are good options for: {query}?\n"
                    "Brief answer."
                ),
            },
        ],
    )
    block = msg.content[0]
    text = getattr(block, "text", str(block))
    return text.lower()


def evaluate_llm_with_external_context(
    query: str,
    brand: str,
    context: str,
) -> Tuple[Dict[str, bool], float]:
    results: Dict[str, bool] = {}
    if os.getenv("OPENAI_API_KEY"):
        try:
            oa_model = os.getenv("GEO_EVAL_OPENAI_MODEL", "gpt-4o-mini")
            ans = ask_openai_with_context(query, context, oa_model)
            results[f"openai:{oa_model}"] = check_mention(ans, brand)
        except Exception as e:
            print(f"  ⚠️ OpenAI context eval failed: {e}")
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            cl_model = _anthropic_eval_model()
            ans = ask_anthropic_with_context(query, context, cl_model)
            results[f"anthropic:{cl_model}"] = check_mention(ans, brand)
        except Exception as e:
            print(f"  ⚠️ Anthropic context eval failed: {e}")

    if not results:
        return {}, 0.0
    score = sum(results.values()) / len(results)
    return results, score


def build_measurement_report(
    query: str,
    brand: str,
    organic: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Full report: SERP metrics + baseline LLM mention rate + context-conditioned rate + delta.
    Skips LLM calls if GEO_SKIP_LLM_EVAL=1.
    """
    serp = compute_serp_metrics(organic, brand)
    if os.getenv("GEO_SKIP_LLM_EVAL", "").lower() in ("1", "true", "yes"):
        return {
            "serp": serp,
            "llm_baseline": {"by_model": {}, "mention_rate": None, "skipped": True},
            "llm_with_external_context": {"by_model": {}, "mention_rate": None, "skipped": True},
            "delta_mention_rate": None,
            "external_context_preview": "",
            "note": "GEO_SKIP_LLM_EVAL set — LLM evaluators skipped",
        }

    base_models, base_score = evaluate_llm_baseline(query, brand)
    context = retrieve_external_context(query, organic)
    ctx_models, ctx_score = evaluate_llm_with_external_context(query, brand, context)

    return {
        "serp": serp,
        "llm_baseline": {
            "by_model": base_models,
            "mention_rate": round(base_score, 4),
            "n_models": len(base_models),
        },
        "llm_with_external_context": {
            "by_model": ctx_models,
            "mention_rate": round(ctx_score, 4),
            "n_models": len(ctx_models),
        },
        "delta_mention_rate": round(ctx_score - base_score, 4)
        if base_models and ctx_models
        else None,
        "external_context_chars": len(context),
        "external_context_preview": context[:600],
        "note": (
            "Baseline = query-only evaluators; "
            "with_context uses Tavily or SERP excerpts — never your generated article."
        ),
    }


# --- Product-level unified opportunity score ----------------------------------


def _interpret_opportunity(final_score: float) -> str:
    if final_score >= 0.8:
        return "strong opportunity"
    if final_score >= 0.6:
        return "worth doing"
    if final_score >= 0.4:
        return "mixed"
    return "low priority"


def _opportunity_decision(final_score: float) -> str:
    if final_score > 0.8:
        return "PRIORITY ARTICLE"
    if final_score > 0.6:
        return "GOOD TOPIC"
    return "SKIP"


def compute_geo_opportunity_score(
    measurement_report: Dict[str, Any],
    presence_check: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """
    Single product metric: SERP (reality) + Δ (independent LLM eval) + impact (article effect).

    final_score = 0.5 * serp_final + 0.3 * delta_01 + 0.2 * impact_score
    All sub-scores in [0, 1] where possible.
    """
    if measurement_report.get("error"):
        return {
            "final_score": None,
            "decision": "SKIP",
            "interpretation": "error",
            "error": measurement_report.get("error"),
            "components": {},
        }

    serp = measurement_report.get("serp") or {}
    coverage = float(serp.get("coverage", 0.0))
    first_rank = int(serp.get("first_rank", 999))

    serp_score = 1.0 - max(0.0, min(1.0, coverage))
    rank_score = (1.0 / first_rank) if first_rank < 999 else 0.0
    serp_final = 0.7 * serp_score + 0.3 * rank_score

    raw_delta = measurement_report.get("delta_mention_rate")
    if raw_delta is None:
        delta_01 = 0.0
    else:
        d = float(raw_delta)
        d = max(-1.0, min(1.0, d))
        # Map [-1, 1] → [0, 1] so negative lifts do not explode the sum
        delta_01 = (d + 1.0) / 2.0

    presence = presence_check or {}
    impact = float(presence.get("impact_score", 0.0))
    impact = max(0.0, min(1.0, impact))

    final_score = (
        0.5 * serp_final + 0.3 * delta_01 + 0.2 * impact
    )
    final_score = max(0.0, min(1.0, final_score))

    decision = _opportunity_decision(final_score)

    return {
        "final_score": round(final_score, 4),
        "decision": decision,
        "interpretation": _interpret_opportunity(final_score),
        "components": {
            "serp_score": round(serp_score, 4),
            "rank_score": round(rank_score, 4),
            "serp_final": round(serp_final, 4),
            "coverage": coverage,
            "first_rank": first_rank,
            "delta_mention_rate_raw": raw_delta,
            "delta_component_01": round(delta_01, 4),
            "impact_score": impact,
        },
        "weights": {"serp_final": 0.5, "delta_01": 0.3, "impact": 0.2},
        "formula": "0.5*serp_final + 0.3*delta_01 + 0.2*impact",
    }
