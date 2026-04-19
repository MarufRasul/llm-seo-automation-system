#!/usr/bin/env python3
"""Automated batch runner for LLM SEO content generation."""

import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from app.batch.batch_generator import BatchContentGenerator
from app.workflows.article_workflow import ArticleWorkflow

# Ensure logs are flushed immediately in terminal and when piped.
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


def _env_list(key: str, default: str = ""):
    raw_value = os.getenv(key, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def run_brand_batch():
    brands = _env_list("AUTO_RUN_BRANDS", "lg_notebook,dongwon_salmon,doshinji_ceramics")
    topics_per_brand = int(os.getenv("AUTO_RUN_TOPICS_PER_BRAND", "2"))

    generator = BatchContentGenerator()
    return generator.generate_batch(brands=brands, topics_per_brand=topics_per_brand)


def run_niche_batch():
    niches = _env_list("AUTO_RUN_NICHES", "LG전자 노트북,동원 연어,도슨티 도자기")
    workflow = ArticleWorkflow()
    results = []

    for niche in niches:
        try:
            print(f"\n=== Автоматический запуск для ниши: {niche} ===")
            result = workflow.run(topic=None, niche=niche)
            results.append({
                "niche": niche,
                "topic": result.get("topic"),
                "published_url": result.get("published_url"),
                **result,
            })
            print(f"✅ Успешно сгенерировано для ниши: {niche}")
        except Exception as exc:
            print(f"❌ Ошибка при генерации для ниши '{niche}': {exc}")

    return results


def run_daily_lg_laptop():
    workflow = ArticleWorkflow()
    niche = "LG전자 노트북"
    print(f"\n=== Ежедневная генерация LG 노트북 для ниши: {niche} ===")
    result = workflow.run(topic=None, niche=niche)
    return [result]


def main():
    load_dotenv()
    mode = os.getenv("AUTO_RUN_MODE", "brand_batch").strip().lower()
    started = datetime.now().isoformat(timespec="seconds")

    print("\nLLM SEO Automation Runner")
    print("Запуск: ", started)
    print(f"AUTO_RUN_MODE={mode}")

    if mode == "niche_batch":
        results = run_niche_batch()
    elif mode == "lg_daily":
        results = run_daily_lg_laptop()
    else:
        results = run_brand_batch()

    report_dir = "batch_reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"auto_run_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    with open(report_path, "w", encoding="utf-8") as f:
        import json
        json.dump({"mode": mode, "results": results}, f, ensure_ascii=False, indent=2)

    print(f"\n📦 Автоматический запуск завершен. Отчет: {report_path}")


if __name__ == "__main__":
    main()
