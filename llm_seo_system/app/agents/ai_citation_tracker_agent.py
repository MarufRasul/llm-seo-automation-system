"""
AI Citation Tracker Agent - РЕАЛЬНАЯ версия
Реально отслеживает цитирование через API
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import aiohttp
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")
load_dotenv(PACKAGE_ROOT / ".env")


class AICitationTrackerAgent:
    """
    Реальный трекер цитирования через API:
    1. Perplexity API - AI поиск с цитированием
    2. Tavily Search - AI-oriented web/source visibility
    3. Семантический поиск в Интернете
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # API ключи
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        
        self.db_path = "memory/ai_citations_real.json"
        self.load_db()
    
    def load_db(self):
        """Загружает или создает базу цитирований"""
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        else:
            self.db = {"citations": [], "summary": {}}
        
        # Убеждаемся в структуре
        if "citations" not in self.db:
            self.db["citations"] = []
        if "summary" not in self.db:
            self.db["summary"] = {}
        self.save_db()
    
    def save_db(self):
        """Сохраняет базу цитирований"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.db, f, indent=2, ensure_ascii=False)
    
    async def track_with_perplexity(
        self,
        article_url: str,
        article_title: str,
        topic: str
    ) -> Dict[str, Any]:
        """
        РЕАЛЬНЫЙ способ: Спрашиваем Perplexity API
        "Какие источники вы используете для ответа на [query]?"
        И проверяем, есть ли наш URL в ответе
        """
        if not self.perplexity_key:
            print("  ⚠️  PERPLEXITY_API_KEY не установлен")
            return {"found": False, "citations": []}
        
        print(f"\n  🔍 Перплексити: {topic}")
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-small-online",
            "messages": [
                {
                    "role": "user",
                    "content": f"Please provide information about: {topic}\nAlso list all sources you're using."
                }
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Извлекаем источники
                        citations = data.get("citations", [])
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        # Проверяем, есть ли наш URL
                        found = article_url in str(citations) or article_url in content
                        
                        print(f"    ✓ Ответ получен")
                        print(f"    ✓ Источники: {len(citations)}")
                        print(f"    {'✓' if found else '✗'} Ваш URL найден: {found}")
                        
                        return {
                            "found": found,
                            "citations": citations,
                            "content": content[:200],
                            "source": "perplexity"
                        }
                    else:
                        print(f"    ❌ HTTP {resp.status}")
                        return {"found": False, "citations": []}
        
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
            return {"found": False, "citations": []}
    
    async def track_with_tavily(
        self,
        article_url: str,
        article_title: str,
        topic: str
    ) -> Dict[str, Any]:
        """
        РЕАЛЬНЫЙ способ: Ищет статью среди AI-oriented web sources через Tavily.
        Проверяет, появляется ли URL/заголовок среди релевантных источников.
        """
        if not self.tavily_key:
            print("  ⚠️  TAVILY_API_KEY не установлен")
            return {"mentions": 0, "results": []}
        
        print(f"\n  🔍 Tavily Search: '{topic}'")
        
        url = "https://api.tavily.com/search"
        headers = {
            "Authorization": f"Bearer {self.tavily_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": f'"{article_title}" OR "{article_url}" {topic}',
            "search_depth": "basic",
            "max_results": 10,
            "include_answer": False,
            "include_raw_content": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get("results", [])
                        title_lower = article_title.lower()
                        matched = [
                            result for result in results
                            if (
                                article_url and article_url in result.get("url", "")
                            )
                            or title_lower in result.get("title", "").lower()
                            or title_lower in result.get("content", "").lower()
                        ]
                        
                        print(f"    ✓ Результатов Tavily: {len(results)}")
                        print(f"    ✓ Совпадений статьи: {len(matched)}")
                        
                        return {
                            "mentions": len(matched),
                            "results": [
                                {
                                    "title": r.get("title", ""),
                                    "url": r.get("url", ""),
                                    "snippet": r.get("content", "")[:300],
                                    "score": r.get("score")
                                }
                                for r in results[:5]
                            ],
                            "source": "tavily"
                        }
                    else:
                        print(f"    ❌ HTTP {resp.status}")
                        return {"mentions": 0, "results": []}
        
        except Exception as e:
            print(f"    ❌ Ошибка Tavily: {type(e).__name__}")
            return {"mentions": 0, "results": []}
    
    async def track_with_serpapi(
        self,
        article_url: str,
        topic: str
    ) -> Dict[str, Any]:
        """
        РЕАЛЬНЫЙ способ: Google Search через SerpAPI
        Проверяет позицию вашей статьи в результатах поиска
        """
        if not self.serpapi_key:
            print("  ⚠️  SERPAPI_KEY не установлен")
            return {"position": None, "rank": None}
        
        print(f"\n  🔍 Google Search: '{topic}'")
        
        import requests
        
        try:
            response = requests.get(
                "https://serpapi.com/search",
                params={
                    "q": topic,
                    "api_key": self.serpapi_key,
                    "num": 20
                },
                timeout=20
            )
            response.raise_for_status()
            
            results = response.json().get("organic_results", [])
            
            # Ищем нашу статью
            position = None
            for i, result in enumerate(results, 1):
                if article_url in result.get("link", ""):
                    position = i
                    break
            
            if position:
                print(f"    ✓ Статья найдена в позиции #{position}")
            else:
                print(f"    ✗ Статья не в топ-{len(results)}")
            
            return {
                "position": position,
                "rank": f"Top-{len(results)}" if position else "Not in top-20",
                "total_results": len(results),
                "source": "google"
            }
        
        except Exception as e:
            print(f"    ❌ Ошибка SerpAPI: {type(e).__name__}")
            return {"position": None, "rank": None}
    
    async def track_article_real(
        self,
        article_url: str,
        article_title: str,
        topic: str
    ) -> Dict[str, Any]:
        """
        ПОЛНЫЙ РЕАЛЬНЫЙ МОНИТОРИНГ через все каналы одновременно
        """
        print(f"\n{'='*70}")
        print(f"📊 REAL Citation Tracking")
        print(f"{'='*70}")
        print(f"  Title: {article_title}")
        print(f"  URL: {article_url}")
        print(f"  Topic: {topic}")
        
        timestamp = datetime.now().isoformat()
        
        # Запускаем все проверки параллельно
        tasks = [
            self.track_with_perplexity(article_url, article_title, topic),
            self.track_with_tavily(article_url, article_title, topic),
            self.track_with_serpapi(article_url, topic),
        ]
        
        results = await asyncio.gather(*tasks)
        
        perplexity_result = results[0]
        tavily_result = results[1]
        google_result = results[2]
        
        # Вычисляем общую оценку
        citation_score = 0
        if perplexity_result.get("found"):
            citation_score += 40
        if tavily_result.get("mentions", 0) > 0:
            citation_score += 30
        if google_result.get("position"):
            # Чем выше позиция, тем больше очков
            position = google_result["position"]
            citation_score += max(0, 30 - (position - 1))
        
        report = {
            "timestamp": timestamp,
            "article_url": article_url,
            "article_title": article_title,
            "topic": topic,
            "citation_score": min(100, citation_score),  # 0-100
            "perplexity": perplexity_result,
            "tavily": tavily_result,
            "google": google_result
        }
        
        # Сохраняем в базу
        self.db["citations"].append(report)
        self.save_db()
        
        return report

    async def track_article(
        self,
        article_title: str,
        topic: str,
        article_url: str | None = None
    ) -> Dict[str, Any]:
        """Compatibility wrapper that uses real citation tracking."""
        return await self.track_article_real(
            article_url=article_url or "",
            article_title=article_title,
            topic=topic
        )

    def track_article_citation(
        self,
        article_title: str,
        article_topic: str,
        article_url: str | None = None
    ) -> Dict[str, Any]:
        """Synchronous wrapper for Flask routes."""
        return asyncio.run(
            self.track_article(
                article_title=article_title,
                topic=article_topic,
                article_url=article_url
            )
        )


# Пример использования
async def main():
    tracker = AICitationTrackerAgent()
    
    result = await tracker.track_article_real(
        article_url="https://example.com/lg-gram-laptop",
        article_title="LG Gram Laptop for Students 2026",
        topic="best lightweight laptop for students"
    )
    
    print(f"\n{'='*70}")
    print(f"📈 ИТОГОВАЯ ОЦЕНКА: {result['citation_score']}/100")
    print(f"{'='*70}")
    print(f"\nВ Perplexity: {'✅ Найдено' if result['perplexity']['found'] else '❌ Не найдено'}")
    print(f"В Tavily Search: {result['tavily']['mentions']} совпадений")
    print(f"В Google: Позиция {result['google'].get('position', 'не найдена')}")
    print(f"\n💾 Результаты сохранены в: memory/ai_citations_real.json")


if __name__ == "__main__":
    asyncio.run(main())
