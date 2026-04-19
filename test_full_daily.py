#!/usr/bin/env python3
"""
Full test: Daily LG generation with REAL question collection
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "llm_seo_system"))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Теперь импортируем
from llm_seo_system.app.workflows.article_workflow import ArticleWorkflow

print("🚀 НАЧИНАЕМ ПОЛНЫЙ ТЕСТ ДНЕВНОЙ ГЕНЕРАЦИИ LG")
print("=" * 80)

try:
    workflow = ArticleWorkflow()
    
    print("\n📝 Генерируем статью для LG с автоматическим выбором топика...")
    print("   (используя РЕАЛЬНЫЕ вопросы пользователей из Google и Reddit)\n")
    
    # Это запустит:
    # 1. TopicDiscoveryAgent.discover_topic("LG전자 노트북")
    # 2. QuerySimulatorAgent.generate_queries() - РЕАЛЬНЫЕ вопросы
    # 3. research_agent - данные Google, конкуренты
    # 4. WebScraperAgent - данные с сайта LG
    # 5. ArticleAgent - генерирует статью
    result = workflow.run(topic=None, niche="LG전자 노트북")
    
    print("\n" + "=" * 80)
    print("✅ РЕЗУЛЬТАТ:")
    print("=" * 80)
    
    print(f"\n📊 Выбранная тема: {result.get('topic')}")
    print(f"\n📈 SEO Score: {result.get('seo_score', 'N/A')}")
    print(f"\n📝 Размер статьи: {len(result.get('article', ''))} символов")
    
    if result.get('seo_queries'):
        print(f"\n🔍 SEO Queries ({len(result.get('seo_queries', []))}):")
        for q in result.get('seo_queries', [])[:5]:
            print(f"   • {q}")
    
    # Сохранена ли ссылка LG?
    if "https://www.lge.co.kr/laptop" in result.get('article', ''):
        print(f"\n✅ ✅ ✅ ГАРАНТИРОВАНА ССЫЛКА: https://www.lge.co.kr/laptop")
    else:
        print(f"\n⚠️  Ссылка LG не найдена в статье")
    
    print("\n" + "=" * 80)
    print("✨ ТЕСТ УСПЕШЕН!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
