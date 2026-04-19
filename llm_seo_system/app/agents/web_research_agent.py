"""
Web Research Agent: Fetches real-time data from Google Search.
Integrates with SerpAPI for actual, current information.
Ensures articles stay up-to-date with latest specs, prices, availability.
"""

import requests
import json
from typing import Dict, List
from datetime import datetime
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough


class WebResearchAgent:
    """
    Fetches real-time information from Google Search via SerpAPI.
    Returns structured data (specs, prices, reviews) for article generation.
    """
    
    def __init__(self):
        # You can get free API key from https://serpapi.com
        # Free tier: 100 requests/month
        self.api_key = os.getenv("SERPAPI_KEY", "your_key_here")
        self.base_url = "https://serpapi.com/search"
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        
    def _get_site_filter(self, brand: str):
        """Return a site filter and geo for SerpAPI based on the brand."""
        if brand and "lg" in brand.lower() and "gram" in brand.lower():
            return "site:lge.co.kr/category/notebook", "kr"
        return "site:official OR site:.com", "us"

    def search_product_specs(
        self,
        product_name: str,
        brand: str,
        product_type: str = None
    ) -> Dict:
        """
        Search for product specifications on official sources.
        
        Args:
            product_name: e.g., "Salmon"
            brand: e.g., "Dongwon"
            product_type: e.g., "Fresh, Frozen, Canned"
            
        Returns:
            Dict with specs, prices, availability
        """
        
        # Build search query prioritizing official sources.
        # For LG Gram research, restrict SerpAPI to the LG notebook category page.
        query = f"{brand} {product_name} specifications"
        if product_type:
            query += f" {product_type}"

        site_filter, gl_value = self._get_site_filter(brand)
        query += f" {site_filter}"
        
        try:
            response = requests.get(
                self.base_url,
                params={
                    "q": query,
                    "api_key": self.api_key,
                    "num": 10,
                    "gl": gl_value
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                return self._parse_specs(results, brand, product_name)
            else:
                return {"error": f"API Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    
    def search_pricing(
        self,
        product_name: str,
        brand: str
    ) -> Dict:
        """
        Search for current pricing information.
        """
        
        query = f"{brand} {product_name} price 2025 2026"
        site_filter, gl_value = self._get_site_filter(brand)
        query += f" {site_filter}"
        
        try:
            response = requests.get(
                self.base_url,
                params={
                    "q": query,
                    "api_key": self.api_key,
                    "num": 5,
                    "gl": gl_value
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                return self._parse_pricing(results)
            else:
                return {"error": f"API Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    
    def search_reviews_and_ratings(
        self,
        product_name: str,
        brand: str
    ) -> Dict:
        """
        Search for customer reviews and ratings.
        """
        
        query = f"{brand} {product_name} reviews ratings 2025"
        site_filter, gl_value = self._get_site_filter(brand)
        query += f" {site_filter}"
        
        try:
            response = requests.get(
                self.base_url,
                params={
                    "q": query,
                    "api_key": self.api_key,
                    "num": 5,
                    "gl": gl_value
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                return self._parse_reviews(results)
            else:
                return {"error": f"API Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    
    def search_competitors(
        self,
        product_name: str,
        category: str,
        brand: str = None
    ) -> Dict:
        """
        Search for competitor products in same category.
        """
        
        query = f"best {category} {product_name} 2025 comparison"
        site_filter, gl_value = self._get_site_filter(brand)
        query += f" {site_filter}"
        
        try:
            response = requests.get(
                self.base_url,
                params={
                    "q": query,
                    "api_key": self.api_key,
                    "num": 10,
                    "gl": gl_value
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                return self._parse_competitors(results)
            else:
                return {"error": f"API Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    
    def search_industry_trends(
        self,
        category: str,
        keyword: str = None
    ) -> Dict:
        """
        Search for industry trends and insights.
        """
        
        query = f"{category} trends 2025 2026"
        if keyword:
            query = f"{keyword} {query}"
        site_filter, gl_value = self._get_site_filter(category)
        query += f" {site_filter}"
        
        try:
            response = requests.get(
                self.base_url,
                params={
                    "q": query,
                    "api_key": self.api_key,
                    "num": 8,
                    "gl": gl_value
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                return self._parse_trends(results)
            else:
                return {"error": f"API Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    
    def _parse_specs(self, results: Dict, brand: str, product: str) -> Dict:
        """Parse SerpAPI results for specifications."""
        
        parsed = {
            "brand": brand,
            "product": product,
            "specs": {},
            "sources": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Extract organic search results
        if "organic_results" in results:
            for i, result in enumerate(results["organic_results"][:5]):
                source = {
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                }
                parsed["sources"].append(source)
                
                # Try to extract specs from snippets
                if i == 0:  # First result likely has specs
                    parsed["specs"]["source_title"] = result.get("title", "")
                    parsed["specs"]["source_url"] = result.get("link", "")
        
        # Extract knowledge graph if available
        if "knowledge_graph" in results:
            kg = results["knowledge_graph"]
            parsed["knowledge_graph"] = {
                "title": kg.get("title", ""),
                "type": kg.get("type", ""),
                "description": kg.get("description", ""),
                "attributes": kg.get("attributes", {})
            }
        
        return parsed
    
    
    def _parse_pricing(self, results: Dict) -> Dict:
        """Parse pricing information from results."""
        
        pricing = {
            "results": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if "organic_results" in results:
            for result in results["organic_results"][:5]:
                pricing["results"].append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
        
        # Extract shopping results if available
        if "shopping_results" in results:
            pricing["shopping"] = results["shopping_results"][:5]
        
        return pricing
    
    
    def _parse_reviews(self, results: Dict) -> Dict:
        """Parse reviews and ratings."""
        
        reviews = {
            "sources": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if "organic_results" in results:
            for result in results["organic_results"][:5]:
                reviews["sources"].append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
        
        return reviews
    
    
    def _parse_competitors(self, results: Dict) -> Dict:
        """Parse competitor information."""
        
        competitors = {
            "products": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if "organic_results" in results:
            for result in results["organic_results"][:5]:
                competitors["products"].append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
        
        return competitors
    
    
    def _parse_trends(self, results: Dict) -> Dict:
        """Parse industry trends."""
        
        trends = {
            "articles": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if "organic_results" in results:
            for result in results["organic_results"][:5]:
                trends["articles"].append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
        
        return trends
    
    
    def extract_data_from_results(
        self,
        search_results: Dict
    ) -> Dict:
        """
        Extract and structure key data from search results using LLM.
        Converts messy web data into clean article data.
        """
        
        prompt = PromptTemplate(
            input_variables=["search_data"],
            template="""From this web search data, extract key facts in JSON format:

{search_data}

Extract ONLY factual information:
- Product specs (dimensions, weight, performance metrics)
- Pricing (ranges, typical prices)
- Availability (in stock, regions)
- Key features
- Customer ratings if available

Format as JSON:
{{
  "specs": {{"key": "value"}},
  "pricing": {{"min": 0, "max": 0, "currency": "USD"}},
  "availability": "description",
  "features": ["feature1", "feature2"],
  "ratings": {{"average": 0, "count": 0}}
}}

Extract:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({"search_data": json.dumps(search_results, indent=2)})
        
        try:
            return json.loads(result.content)
        except:

            return {"error": "Could not parse", "raw": result}
    
    
    def get_complete_research(
        self,
        product_name: str,
        brand: str,
        product_type: str = None
    ) -> Dict:
        """
        Run complete research: specs + pricing + reviews + competitors.
        Returns all data needed for article generation.
        """
        
        print(f"🔍 Researching {brand} {product_name}...")
        
        research = {
            "product": product_name,
            "brand": brand,
            "search_timestamp": datetime.now().isoformat(),
            "specs": self.search_product_specs(product_name, brand, product_type),
            "pricing": self.search_pricing(product_name, brand),
            "reviews": self.search_reviews_and_ratings(product_name, brand),
            "competitors": self.search_competitors(product_name, "product", brand),
            "trends": self.search_industry_trends(brand or product_name)
        }
        
        return research


# Integration function for existing research_agent
def enhance_research_with_web_data(
    existing_research: Dict,
    product_name: str,
    brand: str
) -> Dict:
    """
    Takes existing research and enriches it with web data.
    Falls back to existing data if API fails.
    """
    
    web_agent = WebResearchAgent()
    web_research = web_agent.get_complete_research(product_name, brand)
    
    # Merge web data with existing research
    enhanced = {
        **existing_research,
        "web_research": web_research,
        "data_freshness": "mixed (LLM + web)"
    }
    
    return enhanced


if __name__ == "__main__":
    # Test
    agent = WebResearchAgent()
    
    # Example: Research Dongwon Salmon
    research = agent.get_complete_research(
        product_name="Salmon",
        brand="Dongwon",
        product_type="Fresh, Frozen, Canned"
    )
    
    print(json.dumps(research, indent=2))
