import re

class CitationOptimizerAgent:
    def __init__(self):
        pass

    def analyze(self, article: str) -> dict:
        """
        Analyzes how well the article is optimized for LLM citation behavior
        """
        print("📑 CitationOptimizerAgent: analyzing article citation optimization")

        score = 0
        report = {}

        # Definition detection
        definitions = re.findall(r"\b(is|refers to|defined as)\b", article.lower())
        definition_score = min(len(definitions) * 2, 10)
        score += definition_score
        report["definitions"] = definition_score

        # Structured lists
        list_items = re.findall(r"^\s*[-*•]\s+", article, re.MULTILINE)
        list_score = min(len(list_items) * 1.5, 10)
        score += list_score
        report["structured_lists"] = list_score

        # FAQ presence
        faq_questions = re.findall(r"\?\n", article)
        faq_score = min(len(faq_questions) * 2, 10)
        score += faq_score
        report["faq_density"] = faq_score

        # Comparisons
        comparisons = re.findall(r"\b(vs|versus|compared to|better than)\b", article.lower())
        comparison_score = min(len(comparisons) * 2, 10)
        score += comparison_score
        report["comparisons"] = comparison_score

        # Step-by-step instructions
        steps = re.findall(r"\b(step \d+|first,|second,|third,)\b", article.lower())
        step_score = min(len(steps) * 2, 10)
        score += step_score
        report["step_guides"] = step_score

        # Clear claims
        claims = re.findall(r"\b(best|ideal|designed for|optimized for|perfect for)\b", article.lower())
        claim_score = min(len(claims) * 1.5, 10)
        score += claim_score
        report["clear_claims"] = claim_score

        # Normalize to 0–100
        total_score = min(score, 100)
        report["total_citation_score"] = total_score

        return report
