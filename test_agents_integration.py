#!/usr/bin/env python
"""
🧪 Демонстрация работы RAGEvaluatorAgent и AICitationTrackerAgent
Запустить: python test_agents_integration.py
"""

import sys
import os
import asyncio
from pathlib import Path

# Добавляем путь
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, os.path.join(str(Path(__file__).parent), "llm_seo_system"))

from app.agents.rag_evaluator_agent import RAGEvaluatorAgent
from app.agents.ai_citation_tracker_agent import AICitationTrackerAgent


def test_rag_evaluator():
    """Тест 1: RAGEvaluatorAgent - работает с документами и LLM"""
    print("\n" + "="*70)
    print("🔍 ТЕСТ 1: RAGEvaluatorAgent")
    print("="*70)
    print("\n📝 Что делает RAGEvaluatorAgent:")
    print("  1. Создает базу данных документов (FAISS)")
    print("  2. Конвертирует запрос в вектора (embeddings)")
    print("  3. Ищет похожие документы в базе")
    print("  4. LLM генерирует ответ на основе найденных документов (RAG)")
    
    try:
        print("\n▶️  Запуск агента...")
        agent = RAGEvaluatorAgent()
        
        # Тестовый запрос
        query = "best lightweight laptop for students"
        print(f"\n📌 Запрос: '{query}'")
        
        result = agent.evaluate(query)
        
        print("\n✅ Результат:")
        print(f"\n  Найденные документы:")
        for i, doc in enumerate(result["retrieved_docs"], 1):
            print(f"    {i}. {doc}")
        
        print(f"\n  LLM ответ:")
        print(f"    {result['response']}")
        
        print("\n✅ RAGEvaluatorAgent работает!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False


async def test_ai_citation_tracker():
    """Тест 2: AICitationTrackerAgent - отслеживает цитирование в AI"""
    print("\n" + "="*70)
    print("📊 ТЕСТ 2: AICitationTrackerAgent")
    print("="*70)
    print("\n📝 Что делает AICitationTrackerAgent:")
    print("  1. Проверяет Perplexity API, если ключ есть")
    print("  2. Проверяет AI-oriented web visibility через Tavily")
    print("  3. Проверяет позицию в Google через SerpAPI")
    print("  4. Считает citation_score на основе реальных внешних ответов")
    print("  6. Сохраняет результаты в JSON")
    
    try:
        print("\n▶️  Инициализация агента...")
        tracker = AICitationTrackerAgent()
        
        print(f"  Perplexity: {'on' if tracker.perplexity_key else 'off'}")
        print(f"  Tavily: {'on' if tracker.tavily_key else 'off'}")
        print(f"  SerpAPI: {'on' if tracker.serpapi_key else 'off'}")
        
        # Тестовое отслеживание
        title = "LG Gram Laptop for Students 2026"
        topic = "lightweight laptop"
        url = "https://example.com/lg-gram"
        
        print(f"\n📌 Отслеживаем:")
        print(f"  Title: {title}")
        print(f"  Topic: {topic}")
        print(f"  URL: {url}")
        
        print("\n▶️  Запуск отслеживания (это может занять ~30 сек)...")
        result = await tracker.track_article(title, topic, url)
        
        print("\n✅ Результат отслеживания:")
        print(f"\n  Citation Score: {result['citation_score']}/100")
        print(f"  Timestamp: {result['timestamp']}")
        print(f"  Tavily matches: {result['tavily']['mentions']}")
        print(f"  Google position: {result['google'].get('position')}")
        print(f"  Perplexity found: {result['perplexity'].get('found')}")
        
        print("\n✅ AICitationTrackerAgent работает!")
        print(f"\n📁 Результаты сохранены в: memory/ai_citations_real.json")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_integration():
    """Тест 3: Интеграция агентов в Workflow"""
    print("\n" + "="*70)
    print("⚙️  ТЕСТ 3: Интеграция в ArticleWorkflow")
    print("="*70)
    
    try:
        print("\n▶️  Импортируем workflow...")
        # Добавляем llm_seo_system в path для правильного импорта
        sys.path.insert(0, os.path.join(Path(__file__).parent, "llm_seo_system"))
        from app.workflows.article_workflow import ArticleWorkflow
        
        print("  ✅ Инициализируем workflow...")
        workflow = ArticleWorkflow()
        
        print("\n  Агенты в workflow:")
        print(f"    ✓ rag_evaluator: {type(workflow.rag_evaluator).__name__}")
        print(f"    ✓ citation_agent: {type(workflow.citation_agent).__name__}")
        print(f"    ✓ site_brain: {type(workflow.site_brain).__name__}")
        print(f"    ✓ research_agent: {type(workflow.research_agent).__name__}")
        print(f"    ✓ и еще {len([a for a in dir(workflow) if 'agent' in a.lower()]) - 5} агентов...")
        
        print("\n✅ Все агенты успешно инициализированы!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Главная функция с всеми тестами"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  🚀 Тестирование RAGEvaluatorAgent & AICitationTrackerAgent    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    results = {}
    
    # Тест 1: RAG Evaluator
    results["RAG Evaluator"] = test_rag_evaluator()
    
    # Тест 2: AI Citation Tracker (асинхронный)
    results["AI Citation Tracker"] = await test_ai_citation_tracker()
    
    # Тест 3: Workflow Integration
    results["Workflow Integration"] = test_workflow_integration()
    
    # Итоги
    print("\n" + "="*70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n  Всего: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    else:
        print(f"\n⚠️  {total - passed} тестов не прошли")
    
    print("\n" + "="*70)
    print("\n💡 Как использовать в коде:")
    print("""
# Для RAG:
from app.agents.rag_evaluator_agent import RAGEvaluatorAgent
agent = RAGEvaluatorAgent()
result = agent.evaluate("your query")
print(result["response"])

# Для Citation Tracker (асинхронный):
from app.agents.ai_citation_tracker_agent import AICitationTrackerAgent
tracker = AICitationTrackerAgent()
result = await tracker.track_article("Article Title", "topic", "url")
print(f"Citation Score: {result['citation_score']}/100")

# В workflow:
from app.workflows.article_workflow import ArticleWorkflow
workflow = ArticleWorkflow()
rag_result = workflow.rag_evaluator.evaluate("query")
    """)


if __name__ == "__main__":
    asyncio.run(main())
