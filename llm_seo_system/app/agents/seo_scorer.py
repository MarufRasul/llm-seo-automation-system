from langchain_openai import ChatOpenAI


class SEOScorer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2  # аналитика, не креатив
        )

    def score_article(self, article: str, topic: str) -> str:
        print(f"📊 SEOScorer: scoring article for topic '{topic}'")
        prompt = f"""
You are an advanced AI SEO auditor.

Analyze the following article written for the topic: "{topic}"

Evaluate and score from 0 to 10:

1. Content Depth — how well the topic is covered
2. Semantic SEO — use of related entities and subtopics
3. Structure — headings, hierarchy, readability
4. EEAT — expertise, authority, trust
5. Keyword Optimization — natural keyword usage
6. AI Visibility — how understandable it is for AI systems

Then provide:
- Total score out of 100
- Strengths
- Weaknesses
- Specific improvement suggestions

ARTICLE:
{article}
"""

        response = self.llm.invoke(prompt)
        return response.content
