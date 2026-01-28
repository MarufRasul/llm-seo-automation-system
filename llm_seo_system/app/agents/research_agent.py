from langchain_openai import ChatOpenAI

class ResearchAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2  # меньше креатива, больше фактов
        )

    def research(self, topic: str) -> str:
        prompt = f"""
You are an AI research assistant.

Collect factual, structured information about: "{topic}"

Return:

1. Key facts
2. Important specifications (if product/tech)
3. Real-world use cases
4. Comparisons or alternatives
5. Target audience
6. Trends or recent developments

Write in bullet points. No fluff.
"""
        response = self.llm.invoke(prompt)
        return response.content
