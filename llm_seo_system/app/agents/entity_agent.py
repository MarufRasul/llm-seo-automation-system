from langchain_openai import ChatOpenAI

class EntityAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2
        )

    def extract_entities(self, research_data: str) -> str:
        print("📌 EntityAgent: extracting SEO entities from research data")
        prompt = f"""
You are an SEO entity extraction system.

From the research data below, extract important SEO entities.

Return in this format:

BRANDS:
-

PRODUCTS:
-

TECHNOLOGIES:
-

FEATURES:
-

TARGET AUDIENCE:
-

RELATED CONCEPTS:
-

Research Data:
{research_data}
"""
        response = self.llm.invoke(prompt)
        return response.content
