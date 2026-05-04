#!/usr/bin/env python3
"""
Verify that the RAG and citation agents use real external data.

This script intentionally does not print API keys. It performs live calls to:
- example.com via WebBaseLoader
- OpenAI embeddings/LLM via RAGEvaluatorAgent
- Tavily Search via AICitationTrackerAgent
- Google results via SerpAPI
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "llm_seo_system"))
os.environ.setdefault("USER_AGENT", "llm-seo-automation-system/verification")

from app.agents.ai_citation_tracker_agent import AICitationTrackerAgent
from app.agents.rag_evaluator_agent import RAGEvaluatorAgent


def pass_fail(condition: bool) -> str:
    return "PASS" if condition else "FAIL"


def verify_rag() -> dict:
    query = "Is LG Gram good for students?"
    url = "https://marufrasul.github.io/llm-seo-automation-system/lg-gram-laptop-for-students.html"

    agent = RAGEvaluatorAgent()
    result = agent.evaluate(query=query, urls=[url], k=1)
    docs = result.get("retrieved_docs", [])
    first_doc = docs[0] if docs else {}

    checks = {
        "downloaded_live_document": len(docs) >= 1,
        "source_url_is_live_url": url in first_doc.get("url", ""),
        "llm_response_present": bool(result.get("response")),
        "no_hardcoded_simulation_docs": "LG Gram is a lightweight laptop" not in json.dumps(result),
    }

    return {
        "name": "RAGEvaluatorAgent",
        "query": query,
        "url": url,
        "document_count": len(docs),
        "source_url": first_doc.get("url"),
        "response_preview": result.get("response", "")[:180],
        "checks": checks,
        "passed": all(checks.values()),
    }


async def verify_citation_tracker() -> dict:
    article_url = "https://marufrasul.github.io/llm-seo-automation-system/lg-gram-laptop-for-students.html"
    article_title = "LG Gram Laptop for Students"
    topic = "LG Gram laptop for students"

    tracker = AICitationTrackerAgent()
    result = await tracker.track_article(
        article_title=article_title,
        topic=topic,
        article_url=article_url,
    )

    tavily = result.get("tavily", {})
    google = result.get("google", {})
    perplexity = result.get("perplexity", {})

    checks = {
        "tavily_key_loaded": bool(tracker.tavily_key),
        "serpapi_key_loaded": bool(tracker.serpapi_key),
        "tavily_returned_results": len(tavily.get("results", [])) > 0,
        "google_returned_results": google.get("total_results") is not None,
        "score_is_numeric": isinstance(result.get("citation_score"), int | float),
    }

    return {
        "name": "AICitationTrackerAgent",
        "article_url": article_url,
        "article_title": article_title,
        "topic": topic,
        "citation_score": result.get("citation_score"),
        "tavily_mentions": tavily.get("mentions"),
        "tavily_results": len(tavily.get("results", [])),
        "google_position": google.get("position"),
        "google_total_results": google.get("total_results"),
        "article_visible_in_tavily": tavily.get("mentions", 0) > 0,
        "article_visible_in_google_top_results": google.get("position") is not None,
        "perplexity_enabled": bool(tracker.perplexity_key),
        "perplexity_found": perplexity.get("found"),
        "checks": checks,
        "passed": all(checks.values()),
    }


async def main() -> int:
    print("Real agent verification")
    print("=======================")
    print("API key availability:")
    print(f"  OPENAI_API_KEY: {pass_fail(bool(os.getenv('OPENAI_API_KEY')))}")
    print(f"  TAVILY_API_KEY: {pass_fail(bool(os.getenv('TAVILY_API_KEY')))}")
    print(f"  SERPAPI_KEY: {pass_fail(bool(os.getenv('SERPAPI_KEY')))}")
    print(f"  PERPLEXITY_API_KEY: {'ON' if os.getenv('PERPLEXITY_API_KEY') else 'OFF (optional)'}")

    rag_report = verify_rag()
    citation_report = await verify_citation_tracker()
    reports = [rag_report, citation_report]

    for report in reports:
        print()
        print(report["name"])
        print("-" * len(report["name"]))
        for check, passed in report["checks"].items():
            print(f"  {pass_fail(passed)} {check}")

        printable = {k: v for k, v in report.items() if k not in {"checks"}}
        print(json.dumps(printable, indent=2, ensure_ascii=False))

    all_passed = all(report["passed"] for report in reports)
    print()
    print(f"FINAL RESULT: {pass_fail(all_passed)}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
