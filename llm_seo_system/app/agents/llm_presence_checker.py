import os
import anthropic
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMPresenceChecker:
    """
    Multi-LLM before/after presence check.

    BEFORE: ask each LLM the query without context  → does brand appear?
    AFTER:  ask each LLM the query + article context → does brand appear?

    Proves the pipeline works across models, not just GPT.
    """

    def __init__(self):
        self.gpt = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        self._anthropic = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
        self.models = ["gpt-4o-mini", "claude-haiku-4-5"]

    # ──────────────────────────────────────────────────────────────────────
    # Single-model helpers
    # ──────────────────────────────────────────────────────────────────────

    def _ask_gpt(self, prompt: str) -> str:
        return self.gpt.invoke(prompt).content

    def _ask_claude(self, prompt: str) -> str:
        try:
            msg = self._anthropic.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            print(f"  ⚠️ Claude error: {e}")
            return ""

    def _check_one(self, model: str, prompt: str, brand: str) -> dict:
        answer = self._ask_gpt(prompt) if "gpt" in model else self._ask_claude(prompt)
        present = brand.lower() in answer.lower()
        return {"model": model, "present": present, "answer_preview": answer[:200]}

    # ──────────────────────────────────────────────────────────────────────
    # Before / After per model
    # ──────────────────────────────────────────────────────────────────────

    def _before_prompt(self, query: str) -> str:
        return f"You are a helpful search assistant. Answer this query concisely: {query}"

    def _after_prompt(self, query: str, article: str) -> str:
        return (
            f"Use the following article as your primary source.\n\n"
            f"Article:\n{article[:2000]}\n\n"
            f"Answer this query based on the article: {query}"
        )

    def run(self, query: str, brand: str, article: str) -> dict:
        """Run before/after check on all models. Returns structured result."""
        print(f" Step 7: Multi-LLM presence check (brand='{brand}')...")
        before_prompt = self._before_prompt(query)
        after_prompt = self._after_prompt(query, article)

        results = {}
        for model in self.models:
            label = "GPT" if "gpt" in model else "Claude"
            b = self._check_one(model, before_prompt, brand)
            a = self._check_one(model, after_prompt, brand)
            results[label] = {"before": b, "after": a, "impact": (not b["present"]) and a["present"]}
            flag_b = "✅" if b["present"] else "❌"
            flag_a = "✅" if a["present"] else "❌"
            print(f"   {label:6s} BEFORE={flag_b}  AFTER={flag_a}  impact={'' if results[label]['impact'] else '—'}")

        any_impact = any(v["impact"] for v in results.values())
        all_after  = all(v["after"]["present"] for v in results.values())
        impact_count = sum(1 for v in results.values() if v["impact"])
        impact_score = round(impact_count / len(results), 2) if results else 0.0

        # Per-model failure reasons (derived without extra LLM calls)
        for label, mr in results.items():
            mr["failure_reason"] = self._failure_reason(mr) if not mr["after"]["present"] else None

        print(f"   → impact_score={impact_score} ({impact_count}/{len(results)}) | all_after={all_after}")
        return {
            "brand": brand,
            "query": query,
            "results": results,
            "any_impact": any_impact,
            "all_after_present": all_after,
            "impact_score": impact_score,
            "impact_count": impact_count,
            "model_count": len(results),
            # keep flat before/after for backward compat with frontend
            "before": results.get("GPT", {}).get("before", {}),
            "after":  results.get("GPT", {}).get("after",  {}),
            "impact": any_impact,
        }

    def _failure_reason(self, model_result: dict) -> str:
        """Infer why a model didn't cite the brand after seeing the article."""
        after_preview = (model_result.get("after") or {}).get("answer_preview", "")
        if len(after_preview) < 80:
            return "Response too short — model gave a generic answer"
        if "vs" in after_preview.lower() or "compare" in after_preview.lower():
            return "Model focused on comparisons, brand didn't stand out"
        return "Needs stronger comparison signals and explicit criteria"
