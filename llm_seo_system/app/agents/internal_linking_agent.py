import os
from langchain_openai import ChatOpenAI

class InternalLinkingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    def generate_links(self, topic: str, existing_articles: list) -> str:
        print(f"🔗 InternalLinkingAgent: generating internal links for '{topic}'")
        prompt = f"""
당신은 한국어 SEO 내부 링크 전략가입니다.

현재 글 주제:
"{topic}"

사이트에 이미 있는 글 주제:
{existing_articles}

작업:
내부 링크로 연결하면 좋은 관련 글 제목 3~5개를 제안하세요.

규칙:
- 반드시 한국어로만 작성
- 현재 글과 문맥상 관련 있어야 함
- 토픽 권위를 확장하는 방향이어야 함
- SEO 친화적인 제목이어야 함
- 설명 문장 없이 markdown bullet list만 반환

반환 형식:
- 관련 글 제목
- 관련 글 제목
"""
        response = self.llm.invoke(prompt)
        return response.content
