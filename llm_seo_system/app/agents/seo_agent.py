from langchain_openai import ChatOpenAI


class SEOAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )

    def _ask(self, prompt: str):
        print(f"🔧 SEOAgent: sending prompt to SEO model")
        return self.llm.invoke(prompt).content

    # 🔹 SEO анализ темы
    def analyze_topic(self, topic: str):
        print(f"🔍 SEOAgent: analyzing topic '{topic}'")
        prompt = f"""
You are an advanced SEO strategist.

For the topic: "{topic}"

Provide:

1. Meta Title (SEO optimized)
2. Meta Description (max 160 characters)
3. URL Slug
4. Main Keywords
5. LSI Keywords
6. Important Entities related to the topic
"""
        return self._ask(prompt)

    # 🔹 Поисковые вопросы
    def generate_search_queries(self, topic: str):
        print(f"🔎 SEOAgent: generating search queries for '{topic}'")
        prompt = f"""
Generate 10 search questions and 5 long-tail search queries for: "{topic}"
"""
        return self._ask(prompt)

    # 🔹 FAQ блок
    def generate_faq(self, topic: str):
        print(f"❓ SEOAgent: generating FAQ section for '{topic}'")
        prompt = f"""
Create an SEO-friendly FAQ section (5 Q&A) for: "{topic}"
"""
        return self._ask(prompt)

    # 🔹 SEO оптимизация статьи
    def optimize_article(self, article: str, seo_data: dict):
        print(f"🛠️ SEOAgent: optimizing article using SEO data")
        prompt = f"""
You are an SEO editor.

Improve the article using this SEO data:

SEO DATA:
{seo_data}

ARTICLE:
{article}

Tasks:
- naturally insert keywords
- improve headings
- increase semantic relevance
- keep it human and readable
"""
        return self._ask(prompt)
