import re
import os
import requests
from typing import Dict, List, Any, cast
from langchain_openai import ChatOpenAI


class GapFinderAgent:
    KNOWN_BRANDS = ["LG", "Samsung", "Apple", "Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI", "Sony", "Microsoft"]
    CRITERIA_WORDS = ["weight", "battery", "performance", "price", "display", "specs", "battery life", "ram", "storage", "cpu", "processor", "screen"]
    CATEGORY_WORDS = ["best overall", "best value", "best for", "ultra-lightweight", "category", "budget", "premium"]

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self._serpapi_key = os.getenv("SERPAPI_KEY")

    def analyze(self, queries: list, target_brand: str = "LG", max_queries: int = 10) -> list:
        """Analyze LLM answer gaps for each query. Returns sorted list by gap score (desc)."""
        print(f" GapFinderAgent: analyzing {min(len(queries), max_queries)} queries for brand '{target_brand}'")
        results = []
        for query in queries[:max_queries]:
            llm_answer = self._get_llm_answer(query)
            serp_data = self._get_serp_data(query) if self._serpapi_key else {}
            analysis = self._build_analysis(llm_answer, serp_data, target_brand)
            gaps = self._detect_gaps_from_analysis(analysis)
            score = self._calculate_score(gaps, query=query)
            results.append({
                "query": query,
                "analysis": analysis,
                "gaps": gaps,
                "score": score,
            })
            serp_note = f" | serp_brands={analysis.get('serp_brands', [])}" if serp_data else ""
            print(f"  → '{query[:60]}' | brand_present={analysis['target_brand_present']} | gaps={gaps} | score={score}{serp_note}")
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def _get_llm_answer(self, query: str) -> str:
        response = self.llm.invoke(
            f"You are a helpful search assistant. Answer this query concisely as you would in a real search result: {query}"
        )
        return self._normalize_response_content(response.content)

    @staticmethod
    def _normalize_response_content(content: Any) -> str:
        if isinstance(content, list):
            return " ".join(str(item) for item in content)
        return str(content)

    def _get_serp_data(self, query: str) -> Dict[str, Any]:
        """Fetch top SERP results from SerpAPI for the query."""
        try:
            resp = requests.get(
                "https://serpapi.com/search",
                params={"q": query, "api_key": self._serpapi_key, "num": 5, "gl": "us"},
                timeout=8,
            )
            if resp.status_code != 200:
                return {}
            data = resp.json()
            organic = data.get("organic_results", [])
            featured = data.get("answer_box", {}) or data.get("featured_snippet", {})
            snippets = " ".join(r.get("snippet", "") for r in organic[:5])
            featured_text = featured.get("snippet", "") or featured.get("answer", "")
            combined_text = f"{featured_text} {snippets}"
            serp_brands = [b for b in self.KNOWN_BRANDS if b.lower() in combined_text.lower()]
            return {
                "serp_brands": serp_brands,
                "has_featured_snippet": bool(featured_text),
                "featured_text": featured_text[:200],
                "snippets_preview": snippets[:400],
                "result_count": len(organic),
            }
        except Exception as e:
            print(f"  ⚠️ SerpAPI error: {e}")
            return {}

    def _build_analysis(self, llm_answer: str, serp_data: Dict[str, Any], target_brand: str) -> Dict[str, Any]:
        """Extract structured analysis from both LLM answer and SERP data."""
        brands_found = [b for b in self.KNOWN_BRANDS if b.lower() in llm_answer.lower()]
        serp_brands = serp_data.get("serp_brands", [])
        brand_in_llm = target_brand.lower() in llm_answer.lower()
        brand_in_serp = target_brand.lower() in " ".join(cast(List[str], serp_brands)).lower()
        return {
            "brands_found": brands_found,
            "target_brand_present": brand_in_llm or brand_in_serp,
            "brand_in_llm": brand_in_llm,
            "brand_in_serp": brand_in_serp,
            "serp_brands": serp_brands,
            "has_featured_snippet": serp_data.get("has_featured_snippet", False),
            "has_list": self._has_list(llm_answer),
            "has_criteria": self._has_criteria(llm_answer),
            "has_categories": self._has_categories(llm_answer),
            "answer_length": len(llm_answer.strip()),
            "llm_answer_preview": llm_answer[:280],
        }

    @staticmethod
    def _detect_gaps_from_analysis(analysis: Dict[str, Any]) -> List[str]:
        """Detect gaps from analysis dict."""
        gaps = []
        if not analysis["target_brand_present"]:
            gaps.append("brand_missing")
        if not analysis["has_list"]:
            gaps.append("no_list")
        if not analysis["has_criteria"]:
            gaps.append("weak_criteria")
        if analysis["answer_length"] < 200:
            gaps.append("too_generic")
        if not analysis["has_categories"]:
            gaps.append("no_categories")
        if not analysis.get("brand_in_serp") and analysis.get("serp_brands"):
            gaps.append("brand_missing_from_serp")
        return gaps

    @staticmethod
    def _calculate_score(gaps: List[str], query: str = "") -> float:
        """Calculate gap score based on gaps and query characteristics."""
        weights = {
            "brand_missing": 0.35,
            "brand_missing_from_serp": 0.20,
            "no_list": 0.20,
            "weak_criteria": 0.20,
            "no_categories": 0.15,
            "too_generic": 0.10,
        }
        score = sum(weights.get(g, 0.1) for g in gaps)
        q_lower = query.lower()
        words = q_lower.split()

        if len(words) < 4:
            score -= 0.15
        elif len(words) >= 6:
            score += 0.10

        if "best" in q_lower:
            score += 0.20
        if " for " in q_lower:
            score += 0.15
        if "lightweight" in q_lower or "portable" in q_lower or "thin" in q_lower:
            score += 0.10
        if "under 1kg" in q_lower or "under 1 kg" in q_lower:
            score += 0.15
        audience_keywords = ["students", "college", "travel", "business", "work", "professionals"]
        if any(kw in q_lower for kw in audience_keywords):
            score += 0.20
        if "under" in q_lower and any(c.isdigit() for c in q_lower):
            score += 0.10
        if "budget" in q_lower or "affordable" in q_lower:
            score += 0.10

        if " vs " in q_lower or " versus " in q_lower:
            score -= 0.25
        if q_lower.startswith("how to") or q_lower.startswith("how do"):
            score -= 0.10
        if q_lower.startswith("what is") or q_lower.startswith("why "):
            score -= 0.10
        return round(max(score, 0.0), 2)

    @staticmethod
    def _has_list(text: str) -> bool:
        """Check if text contains a list structure."""
        return bool(re.search(r'(\d+\.|[-•*])\s+\w', text))

    @staticmethod
    def _has_criteria(text: str) -> bool:
        """Check if text contains evaluation criteria."""
        criteria_words = ["weight", "battery", "performance", "price", "display", "specs", "battery life", "ram", "storage", "cpu", "processor", "screen"]
        return any(w in text.lower() for w in criteria_words)

    @staticmethod
    def _has_categories(text: str) -> bool:
        """Check if text contains category labels."""
        category_words = ["best overall", "best value", "best for", "ultra-lightweight", "category", "budget", "premium"]
        return any(w in text.lower() for w in category_words)
