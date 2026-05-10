class StrategyBuilderAgent:
    LAPTOP_CATEGORIES_DEFAULT = ["best overall", "best ultra-lightweight", "best value", "best Windows"]
    LAPTOP_CATEGORIES_STUDENT = ["best overall", "best ultra-lightweight", "best value", "best battery life"]
    LAPTOP_CATEGORIES_LIGHT = ["best overall", "best ultra-lightweight", "best battery", "best value"]
    GENERIC_CATEGORIES = ["best overall", "best value", "best for professionals", "best budget"]

    # Maps brand_position → reasoning sentence shown in UI / passed to article
    INSERTION_REASONS = {
        "best ultra-lightweight": "LG Gram weighs under 1 kg — lighter than most Windows competitors",
        "best value": "LG Gram offers premium build quality at a competitive price point",
        "best overall": "LG Gram balances weight, battery life, and performance for most users",
        "best battery life": "LG Gram delivers 20+ hours battery — best in class for Windows laptops",
        "best Windows": "LG Gram runs full Windows on the lightest chassis in the category",
    }

    def build(self, query: str, gaps: list) -> dict:
        """Build content strategy from query and detected gaps."""
        query_lower = query.lower()

        fmt = self._determine_format(query_lower)
        categories = self._determine_categories(query_lower)
        brand_position = self._determine_brand_position(query_lower)
        reason = self.INSERTION_REASONS.get(brand_position, "LG is a competitive choice in this category")

        print(f" StrategyBuilder: format={fmt}, position='{brand_position}', reason='{reason}'")
        return {
            "query": query,
            "strategy": {
                "format": fmt,
                "categories": categories,
                "brand_position": brand_position,
                "brand_insertion": {
                    "position": brand_position,
                    "reason": reason,
                },
                "gaps_addressed": gaps,
            }
        }

    def _determine_format(self, query_lower: str) -> str:
        if any(w in query_lower for w in ["best", "top", "recommend", "alternatives"]):
            return "list"
        if any(w in query_lower for w in ["how to", "how do", "guide", "tips"]):
            return "guide"
        if "vs" in query_lower or "versus" in query_lower or "compare" in query_lower:
            return "comparison"
        return "list"

    def _determine_categories(self, query_lower: str) -> list:
        if "laptop" in query_lower or "notebook" in query_lower:
            if "student" in query_lower or "school" in query_lower or "college" in query_lower:
                return self.LAPTOP_CATEGORIES_STUDENT
            if "lightweight" in query_lower or "light" in query_lower or "ultra" in query_lower:
                return self.LAPTOP_CATEGORIES_LIGHT
            return self.LAPTOP_CATEGORIES_DEFAULT
        return self.GENERIC_CATEGORIES

    def _determine_brand_position(self, query_lower: str) -> str:
        if any(w in query_lower for w in ["lightweight", "light", "ultra", "portable", "thin"]):
            return "best ultra-lightweight"
        if any(w in query_lower for w in ["student", "college", "school"]):
            return "best ultra-lightweight"
        if any(w in query_lower for w in ["battery"]):
            return "best battery life"
        if any(w in query_lower for w in ["value", "cheap", "affordable", "budget"]):
            return "best value"
        return "best ultra-lightweight"
