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
        entities: str,
        specs_data: str = ""
    ) -> str:

        prompt = f"""
Write a detailed, SEO-optimized article about "{topic}" with a focus on factual accuracy and LLM-friendly structure.

BRAND STRATEGY:
{brand_voice}

RESEARCH DATA:
{research_data}

SPECIFICATIONS / FACTUAL DATA:
{specs_data if specs_data else research_data}

IMPORTANT SEO ENTITIES TO INCLUDE NATURALLY:
{entities}

Requirements:
- Clear article structure (H1, H2, H3)
- Authoritative, factual tone (no marketing fluff)
- Include real-world use cases or applications
- Semantic SEO with natural integration of entities
- Target word count: ~1000 words

Add the following sections:

1. Key Facts
- Bullet-point factual statements
- Include numeric ranges, specs, and comparisons (e.g., vs other models or products)
- Short declarative sentences AI systems can quote

2. AI-Friendly Summary
- 5–7 short, factual sentences
- Each sentence must express one clear fact about the product or topic
- Use numbers, measurements, ratings, or other concrete data when possible

3. Optional Comparison Section
- Compare with similar products or brands (if applicable)
- Include specs, performance, or usage differences

Instructions for AI:
- Ensure all numbers and specifications are accurate based on the research data
- Maintain factual and neutral tone
- Avoid marketing exaggerations
- Make the content useful for both human readers and LLM systems

"""
        response = self.llm.invoke(prompt)
        return response.content
