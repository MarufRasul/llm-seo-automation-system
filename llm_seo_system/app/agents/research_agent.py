from langchain_openai import ChatOpenAI
from .web_research_agent import WebResearchAgent
from .web_scraper_agent import get_website_data
from ..config.brand_configs import get_brand_config
import json
import os

class ResearchAgent:
    def __init__(self, use_web_search: bool = True, use_web_scraper: bool = True):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2  # меньше креатива, больше фактов
        )
        self.use_web_search = use_web_search and os.getenv("SERPAPI_KEY")
        self.use_web_scraper = use_web_scraper
        if self.use_web_search:
            self.web_agent = WebResearchAgent()

    def research(self, topic: str, brand: str = None, product_type: str = None, brand_key: str = None) -> str:
        """
        Enhanced research with multiple data sources:
        1. Direct website scraping (from brand_configs)
        2. Google Search API (fallback)
        3. LLM knowledge base (fallback)
        """
        
        data_sources = []
        
        # PRIORITY 1: Scrape official website if configured
        if self.use_web_scraper and brand_key:
            print(f"📥 Scraping official website for {brand}...")
            try:
                brand_config = get_brand_config(brand_key)
                if brand_config:
                    website_data = get_website_data(brand_config)
                    if website_data.get("products") or website_data.get("specifications"):
                        data_sources.append(f"\n\n## OFFICIAL WEBSITE DATA (Real-time from {brand_config.get('official_website')}):\n{json.dumps(website_data, indent=2)}")
                        print(f"✅ Website data fetched successfully")
            except Exception as e:
                print(f"⚠️ Website scraping failed: {e}, falling back to other sources")
        
        # PRIORITY 2: Google Search API if website scraping unavailable/failed
        if self.use_web_search and brand and not (data_sources):
            print(f"📡 Fetching real-time data via Google Search for {brand}...")
            try:
                web_research = self.web_agent.get_complete_research(
                    product_name=topic,
                    brand=brand,
                    product_type=product_type
                )
                data_sources.append(f"\n\n## GOOGLE SEARCH DATA (Real-time from Google):\n{json.dumps(web_research, indent=2)}")
                print(f"✅ Google Search data fetched successfully")
            except Exception as e:
                print(f"⚠️ Google Search failed: {e}")
        
        data_section = "".join(data_sources) if data_sources else ""
        
        prompt = f"""
You are an AI research assistant.

Collect factual, structured information about: "{topic}"
Brand: {brand or "Not specified"}

{data_section if data_section else "No real-time data available - use knowledge base"}

Return:

1. Key facts (prioritize real-time data if available)
2. Important specifications (if product/tech)
3. Real-world use cases
4. Comparisons or alternatives
5. Target audience
6. Trends or recent developments
7. Pricing (if available)
8. Availability and sourcing
9. Certifications and quality standards

Write in bullet points. No fluff. Prefer specific numbers and current year data (2025/2026).
"""
        response = self.llm.invoke(prompt)
        return response.content
