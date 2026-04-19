import os
from langchain_openai import ChatOpenAI

class InternalLinkingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    def generate_links(self, topic: str, existing_articles: list) -> str:
        print(f"🔗 InternalLinkingAgent: generating internal links for '{topic}'")
        prompt = f"""
You are an SEO internal linking strategist.

Current article topic:
"{topic}"

Existing article topics on the site:
{existing_articles}

Your task:
Suggest 3–5 related article titles that should be internally linked.

Rules:
- Must be contextually relevant
- Should expand topical authority
- Focus on SEO-friendly titles

Return as a markdown list.
"""
        response = self.llm.invoke(prompt)
        return response.content
