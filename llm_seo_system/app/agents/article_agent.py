import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
class ArticleAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7
        )

    def generate_article(self, topic: str) -> str:
        prompt = f"""
Write a detailed, SEO-friendly blog article about "{topic}".

Requirements:
- Clear structure (H1, H2, H3)
- Informative and natural tone
- Include practical use cases
- Around 800–1200 words
"""
        response = self.llm.invoke(prompt)
        return response.content
