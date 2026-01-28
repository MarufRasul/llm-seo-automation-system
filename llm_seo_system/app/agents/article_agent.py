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

    def generate_article(
        self,
        topic: str,
        research_data: str,
        brand_voice: str,
        entities: str
    ) -> str:

        prompt = f"""
Write a detailed, SEO-optimized article about "{topic}".

BRAND STRATEGY:
{brand_voice}

RESEARCH DATA:
{research_data}

IMPORTANT SEO ENTITIES TO NATURALLY INCLUDE:
{entities}

Requirements:
- Naturally integrate entities into headings and text
- Use semantic SEO
- Clear structure (H1, H2, H3)
- Authoritative tone
- Real-world use cases
- ~1000 words
"""
        response = self.llm.invoke(prompt)
        return response.content
