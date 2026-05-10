import os
import re
from typing import Any, Dict, List

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None  # type: ignore

from app.agents.presence_measurement import compute_serp_metrics


class GapFinderAgent:
    KNOWN_BRANDS = [
        "LG",
        "Samsung",
        "Apple",
        "Dell",
        "HP",
        "Lenovo",
        "ASUS",
        "Acer",
        "MSI",
        "Sony",
        "Microsoft",
    ]
    CRITERIA_WORDS = [
        "weight",
        "battery",
        "performance",
        "price",
        "display",
        "specs",
        "battery life",
        "ram",
        "storage",
        "cpu",
        "processor",
        "screen",
    ]
    CATEGORY_WORDS = [
        "best overall",
        "best value",
        "best for",
        "ultra-lightweight",
        "category",
        "budget",
        "premium",
    ]

    def __init__(self):
        self._serpapi_key = os.getenv("SERPAPI_KEY")

    def analyze(self, queries: list, target_brand: str = "LG", max_queries: int = 10) -> list:
        """
        Query → Google (via SerpAPI) → SERP → gap heuristics.
        No LLM answers for gap detection (avoids “guessing”).
        """
        print(
            f" GapFinderAgent: analyzing {min(len(queries), max_queries)} queries for brand '{target_brand}' (SERP-driven)",
        )
        results = []
        for query in queries[:max_queries]:
            serp_bundle = self._fetch_serp_bundle(query)
            organic = serp_bundle.get("organic_results") or []
            serp_metrics = compute_serp_metrics(organic, target_brand)
            analysis = self._build_analysis(serp_bundle, target_brand)
            analysis["serp_metrics"] = serp_metrics
            gaps = self._detect_gaps_from_analysis(analysis)
            score = self._calculate_score(gaps, query=query)
            results.append(
                {
                    "query": query,
                    "analysis": analysis,
                    "gaps": gaps,
                    "score": score,
                    "organic_results": organic,
                    "serp_metrics": serp_metrics,
                },
            )
            serp_note = (
                f" | serp_brands={analysis.get('serp_brands', [])}"
                if serp_bundle.get("organic_results")
                else ""
            )
            print(
                f"  → '{query[:60]}' | brand_present={analysis['target_brand_present']} | gaps={gaps} | score={score}{serp_note}",
            )
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def get_serp(self, query: str, num: int = 10) -> List[Dict[str, Any]]:
        """Return organic_results only (wrapper for tests/tools)."""
        bundle = self._serp_api_call(query, num)
        return list(bundle.get("organic_results") or [])

    def _serp_api_call(self, query: str, num: int = 10) -> Dict[str, Any]:
        """Single SerpAPI GoogleSearch request; returns full JSON dict."""
        if not self._serpapi_key:
            print("  ⚠️ SERPAPI_KEY is not set — cannot fetch Google SERP.")
            return {}
        if GoogleSearch is None:
            print(
                "  ⚠️ Install SerpAPI client: pip install google-search-results",
            )
            return {}

        params = {
            "q": query,
            "api_key": self._serpapi_key,
            "num": num,
            "gl": "us",
            "hl": "en",
        }
        search = GoogleSearch(params)
        return search.get_dict() or {}

    @staticmethod
    def extract_brands_from_organic(organic: List[Dict[str, Any]]) -> List[str]:
        brands: List[str] = []
        for r in organic:
            title = r.get("title") or ""
            snippet = r.get("snippet") or ""
            text = f"{title} {snippet}".lower()
            for b in GapFinderAgent.KNOWN_BRANDS:
                if b.lower() in text:
                    brands.append(b)
        return list(dict.fromkeys(brands))

    def _fetch_serp_bundle(self, query: str) -> Dict[str, Any]:
        try:
            full_data = self._serp_api_call(query, num=10)
        except Exception as e:
            print(f"  ⚠️ SerpAPI error: {e}")
            full_data = {}

        organic = list(full_data.get("organic_results") or [])

        print("\n=== REAL SERP ===")
        if not organic:
            print("  (no organic results — check SERPAPI_KEY or quota)")
        for i, r in enumerate(organic):
            print(f"{i + 1}. {r.get('title')}")
            print(f"   {r.get('link')}")
        print("=== END SERP ===\n")

        featured = (
            full_data.get("answer_box")
            or full_data.get("featured_snippet")
            or {}
        )

        serp_brands = self.extract_brands_from_organic(organic)
        snippets = " ".join((r.get("snippet") or "") for r in organic[:10])
        titles_joined = " ".join((r.get("title") or "") for r in organic[:10])
        featured_text = ""
        if isinstance(featured, dict):
            featured_text = featured.get("snippet") or featured.get("answer") or ""

        combined_serp_text = f"{featured_text}\n{titles_joined}\n{snippets}".strip()

        return {
            "organic_results": organic,
            "serp_brands": serp_brands,
            "combined_serp_text": combined_serp_text,
            "has_featured_snippet": bool(featured_text),
            "featured_text": featured_text[:300],
            "result_count": len(organic),
            "raw_answer_box": featured if isinstance(featured, dict) else {},
        }

    def _build_analysis(
        self,
        serp_bundle: Dict[str, Any],
        target_brand: str,
    ) -> Dict[str, Any]:
        text = serp_bundle.get("combined_serp_text") or ""
        serp_brands = serp_bundle.get("serp_brands") or []

        brands_found = [b for b in self.KNOWN_BRANDS if b.lower() in text.lower()]
        tb = target_brand.strip()
        brand_in_serp_list = any(
            tb.lower() == b.lower() or tb.lower() in b.lower() for b in serp_brands
        )
        brand_in_serp_text = tb.lower() in text.lower()
        target_present = brand_in_serp_list or brand_in_serp_text

        return {
            "gap_source": "google_serp",
            "brands_found": brands_found,
            "target_brand_present": target_present,
            "brand_in_serp": brand_in_serp_list or brand_in_serp_text,
            "brand_in_llm": False,
            "serp_brands": serp_brands,
            "has_featured_snippet": serp_bundle.get("has_featured_snippet", False),
            "has_list": self._has_list(text) or self._organic_titles_list_like(
                serp_bundle.get("organic_results") or [],
            ),
            "has_criteria": self._has_criteria(text),
            "has_categories": self._has_categories(text),
            "answer_length": len(text.strip()),
            "llm_answer_preview": "",
            "serp_text_preview": text[:400],
            "organic_count": serp_bundle.get("result_count", 0),
        }

    @staticmethod
    def _organic_titles_list_like(organic: List[Dict[str, Any]]) -> bool:
        """Titles like '10 best …' imply list intent in SERP."""
        for r in organic[:5]:
            t = (r.get("title") or "").lower()
            if re.search(r"\b\d+\s+(best|top)\b", t):
                return True
        return False

    @staticmethod
    def _detect_gaps_from_analysis(analysis: Dict[str, Any]) -> List[str]:
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
        serp_brands = analysis.get("serp_brands") or []
        tb_ok = analysis.get("brand_in_serp")
        if serp_brands and not tb_ok:
            gaps.append("brand_missing_from_serp")
        if analysis.get("organic_count", 0) == 0:
            gaps.append("no_serp_results")
        return gaps

    @staticmethod
    def _calculate_score(gaps: List[str], query: str = "") -> float:
        weights = {
            "brand_missing": 0.35,
            "brand_missing_from_serp": 0.20,
            "no_list": 0.20,
            "weak_criteria": 0.20,
            "no_categories": 0.15,
            "too_generic": 0.10,
            "no_serp_results": 0.40,
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
        audience_keywords = [
            "students",
            "college",
            "travel",
            "business",
            "work",
            "professionals",
        ]
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
        return bool(re.search(r"(\d+\.|[-•*])\s+\w", text))

    @staticmethod
    def _has_criteria(text: str) -> bool:
        tl = text.lower()
        return any(w in tl for w in GapFinderAgent.CRITERIA_WORDS)

    @staticmethod
    def _has_categories(text: str) -> bool:
        tl = text.lower()
        return any(w in tl for w in GapFinderAgent.CATEGORY_WORDS)
