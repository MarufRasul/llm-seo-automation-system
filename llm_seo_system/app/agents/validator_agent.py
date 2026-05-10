import re


class ValidatorAgent:
    KNOWN_BRANDS = ["LG", "Samsung", "Apple", "Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI", "Sony", "Microsoft"]
    CATEGORY_WORDS = ["best overall", "best value", "best for", "ultra-lightweight", "best budget", "best windows", "best battery"]

    def validate(self, article: str) -> dict:
        """Validate GEO article quality. Returns dict with valid flag and issues list."""
        issues = []

        has_list = self._has_list(article)
        brand_count = self._count_brands(article)
        has_cats = self._has_categories(article)
        has_qa = self._has_quick_answer(article)

        if not has_list:
            issues.append("no_list")
        if brand_count < 3:
            issues.append(f"insufficient_brands (found {brand_count}, need 3+)")
        if not has_cats:
            issues.append("no_categories")
        if not has_qa:
            issues.append("no_quick_answer")

        valid = len(issues) == 0
        print(f"{'✅' if valid else '⚠️'} ValidatorAgent: valid={valid}, brands={brand_count}, issues={issues}")
        return {
            "valid": valid,
            "issues": issues,
            "brand_count": brand_count,
            "has_list": has_list,
            "has_categories": has_cats,
            "has_quick_answer": has_qa,
        }

    def _has_list(self, text: str) -> bool:
        return bool(re.search(r'(\d+\.|[-•*])\s+\w', text))

    def _count_brands(self, text: str) -> int:
        text_lower = text.lower()
        return sum(1 for brand in self.KNOWN_BRANDS if brand.lower() in text_lower)

    def _has_categories(self, text: str) -> bool:
        text_lower = text.lower()
        return any(word in text_lower for word in self.CATEGORY_WORDS)

    def _has_quick_answer(self, text: str) -> bool:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        first_content = next((l for l in lines if not l.startswith("#")), "")
        return 20 < len(first_content) < 600
