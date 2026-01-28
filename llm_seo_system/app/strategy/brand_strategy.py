from langchain_openai import ChatOpenAI


class BrandStrategy:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )

    def get_strategy(self, topic: str) -> str:
        prompt = f"""
You are a brand strategy expert.

For the topic: "{topic}"

Define a brand voice and content strategy:

1. Tone (professional, friendly, academic, etc.)
2. Target Audience
3. Key messaging points
4. Words to promote (power words, concepts)
5. Words to avoid (commercial, salesy)

Return in structured format.
"""
        response = self.llm.invoke(prompt)
        return response.content
