from langchain_openai import ChatOpenAI

class QuerySimulatorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def generate_queries(self, topic: str) -> list:
        """
        Generates AI-style user questions for the topic
        """
        prompt = f"""
You are modeling how real users ask AI systems questions.

Generate 10 natural language questions users might ask ChatGPT about:

TOPIC: {topic}

Focus on:
- Buying decisions
- Comparisons
- Suitability
- Use cases
- Recommendations
"""
        response = self.llm.invoke(prompt)
        queries = response.content.split("\n")
        return [q.strip("- ").strip() for q in queries if len(q) > 5]

    def simulate_ai_extraction(self, article: str, queries: list) -> dict:
        """
        Tests whether the article can answer each query
        """
        results = {}

        for q in queries:
            prompt = f"""
You are an AI assistant answering a user.

USER QUESTION:
{q}

ARTICLE:
{article}

If the article contains enough info to answer, extract the answer.
If not, say: NOT FOUND
"""
            response = self.llm.invoke(prompt).content

            if "NOT FOUND" in response:
                results[q] = "❌ Not covered"
            else:
                results[q] = "✅ Covered"

        coverage_score = int(
            (list(results.values()).count("✅ Covered") / len(results)) * 100
        )

        return {
            "coverage_score": coverage_score,
            "query_results": results
        }
