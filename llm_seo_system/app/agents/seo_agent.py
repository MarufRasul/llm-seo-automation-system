from langchain_openai import ChatOpenAI


class SEOAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )

    def generate_search_queries(self, topic: str) -> str:
        prompt = f"""
You are an AI SEO specialist.

For the topic "{topic}", generate:
- 10 questions people might ask ChatGPT
- 5 long-tail search-style prompts
Focus on natural language queries.
"""
        return self.llm.invoke(prompt).content

    def generate_faq(self, topic: str) -> str:
        prompt = f"""
Create an SEO-optimized FAQ section for an article about "{topic}".
Provide 5 Q&A pairs.
"""
        return self.llm.invoke(prompt).content

    def optimize_article(self, article: str, seo_data: dict) -> str:
        prompt = f"""
You are optimizing an article for LLM SEO (Generative Engine Optimization).

ARTICLE:
{article}

SEARCH QUERIES:
{seo_data['queries']}

FAQ:
{seo_data['faq']}

Improve the article by:
- Adding natural answers to likely AI questions
- Integrating entities
- Making structure LLM-friendly
- Keeping it readable
Return full optimized article.
"""
        return self.llm.invoke(prompt).content
