# test.py
import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "llm_seo_system"))

from app.services.llm_service import LLMService
from app.agents.article_agent import ArticleAgent

print("Testing started...")

llm = LLMService()
result = llm.ask("Write short intro about LG laptops")
print(f" LLM Response:\n{result}\n")

agent = ArticleAgent()
article = agent.generate_draft("LG Gram laptop advantages")
print(f"Article Draft:\n{article[:300]}...")

print("All tests passed!")