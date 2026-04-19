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
        specs_data: str = "",
        official_link: str = "",
        language: str = "Korean"
    ) -> str:
        print(f"📝 ArticleAgent: generating article for topic '{topic}' in {language}")

        prompt = f"""
Answer only in Korean. The entire article must be written in Korean. Do not use any English text in the article body, headings, or section labels, except for URLs and necessary product model names.

LG 그램 노트북 관련 주제로, 한국 독자를 대상으로 한 상세한 SEO 최적화 글을 작성하세요.

BRAND STRATEGY:
{brand_voice}

RESEARCH DATA:
{research_data}

SPECIFICATIONS / FACTUAL DATA:
{specs_data if specs_data else research_data}

IMPORTANT SEO ENTITIES TO INCLUDE NATURALLY:
{entities}

요구사항:
- 명확한 문단 구조(H1, H2, H3)
- 사실 중심의 권위 있는 어조
- 과도한 마케팅 문구는 피할 것
- 실제 사용 사례 또는 응용 사례 포함
- 자연스러운 의미론적 SEO 반영
- 목표 분량: 약 1000자
- 한국 검색 사용자에게 자연스럽게 읽히는 한국어 사용

제품이나 매장 관련 주제인 경우, 공식 URL을 "공식 출처" 또는 "구매처" 섹션에 명확히 포함하세요.
- 공식 URL을 그대로 사용
- 공식 매장 페이지를 신뢰할 수 있는 출처로 명시
- 다른 쇼핑몰이나 서드파티 링크로 대체하지 않을 것
- 공식 링크가 주어진 경우, 기사 본문에 반드시 포함

다음 섹션을 포함하세요:

1. 주요 정보
- 핵심 사실을 문장형으로 정리
- 숫자, 사양, 비교 정보 포함
- AI가 인용할 수 있는 간결한 진술

2. AI 친화 요약
- 5~7개의 짧은 사실 문장
- 각 문장은 명확한 하나의 사실 표현
- 숫자, 측정값, 등급, 구체적 데이터를 포함

3. 비교 섹션
- 유사 제품 또는 브랜드와 비교
- 사양, 성능, 사용 측면 차이 점 포함

Instructions for AI:
- Ensure all numbers and specifications are accurate based on the research data
- Maintain factual and neutral tone
- Avoid marketing exaggerations
- Make the content useful for both human readers and LLM systems
- Use only Korean in the article body, headings, and section titles
- Write the article entirely in {language} for the Korean market

{f'OFFICIAL_LINK: {official_link}\n공식 출처 섹션 또는 구매처 섹션에 해당 URL을 명확히 포함하세요.\n' if official_link else ''}
"""
        response = self.llm.invoke(prompt)
        return response.content
