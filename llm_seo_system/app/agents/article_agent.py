# app/agents/article_agent.py

from app.services.llm_service import LLMService


class ArticleAgent:
    def __init__(self):
        self.llm = LLMService()

    def generate_draft(self, topic: str) -> str:
        """
        Generate an article draft based on the specified topic
        """

        prompt = f"""
        You are an expert content writer.

        Write a detailed, informative article about: {topic}

        The article should include:
        - Introduction
        - Explanation of the topic
        - Key features or characteristics
        - Benefits or advantages
        - Comparison if relevant
        - Practical use cases
        - Conclusion

        Write in a clear, structured, SEO-friendly way.
        """

        response = self.llm.ask(prompt)

        return response
