from langchain_openai import ChatOpenAI

class SiteBrainAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    def plan_next_articles(self, topic: str, article_memory: dict) -> str:
        """
        Analyzes previous article performance and suggests next content strategy
        """

        prompt = f"""
You are an AI Content Strategist.

We are building an AI-optimized knowledge site.

Here is existing article performance data:

{article_memory}

Main Topic Cluster:
{topic}

Your job:
Identify content gaps and suggest 5 HIGH-IMPACT next articles that:

- Increase AI answer coverage
- Cover missing user questions
- Expand semantic entity graph
- Strengthen topical authority
- Improve chances of being cited by LLMs

For each article provide:
1. Title
2. Target AI query it answers
3. Why AI systems would use it
"""
        response = self.llm.invoke(prompt)
        return response.content
