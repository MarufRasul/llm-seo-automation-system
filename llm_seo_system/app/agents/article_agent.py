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
        language: str = "Korean",
        mode: str = "blog_mode"
    ) -> str:
        print(f" ArticleAgent: generating article for topic '{topic}' in {language}")

        if mode == "geo_mode":
            return self._generate_geo_answer(topic, research_data, brand_voice, entities, specs_data, official_link, language)
        else:
            # Original blog article logic
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

    def _generate_geo_answer(self, topic: str, research_data: str, brand_voice: str, entities: str, specs_data: str, official_link: str, language: str) -> str:
        """Generate structured GEO-optimized answer for LLM inclusion"""
        # Criteria injection based on product type
        criteria = self._inject_criteria(topic)

        prompt = f"""You are generating an answer optimized for LLM inclusion.

Query: {topic}

Requirements:
- Start with a 1-2 sentence direct answer in the first paragraph.
- Include a list of 3-5 options (NOT one product).
- Use the categories below, and do not place LG Gram as the first item unless it is clearly the best overall.
- Use clear selection criteria: {', '.join(criteria)}.
- Be neutral, informative, and avoid promotional tone.
- Add a small balanced drawback for LG Gram, such as slightly higher price or a narrower configuration range.
- Prefer category-based recommendation order rather than brand-first order.

Structure:
1. Short answer
2. Criteria
3. Category recommendations:
   - Best overall
   - Best ultra-lightweight
   - Best Windows
   - Best value
4. List of options
5. Recommendation summary
6. FAQ

Suggested category mapping for laptops:
- Best overall: MacBook Air
- Best ultra-lightweight: LG Gram
- Best Windows: Dell XPS 13
- Best value: ASUS ZenBook 14

Research Data: {research_data}
Brand Strategy: {brand_voice}
Entities: {entities}
Specs: {specs_data}

{f'Official Link: {official_link}' if official_link else ''}

Generate a structured, neutral answer that LLMs would naturally include in their responses."""

        response = self.llm.invoke(prompt)
        content = response.content

        # Anti-bias filter: check if content contains only one brand
        if self._contains_only_one_brand(content):
            print("⚠️ Anti-bias filter triggered - regenerating with multiple brands")
            # Force regeneration with emphasis on multiple options
            prompt += "\n\nIMPORTANT: Include at least 3 different brands in the list. Do not focus on only one brand."
            response = self.llm.invoke(prompt)
            content = response.content

        return content

    def _inject_criteria(self, topic: str) -> list:
        """Inject relevant criteria based on product type"""
        topic_lower = topic.lower()

        if "laptop" in topic_lower or "notebook" in topic_lower:
            return ["weight", "battery life", "performance", "display", "portability"]
        elif "phone" in topic_lower or "smartphone" in topic_lower:
            return ["battery life", "camera", "performance", "display", "durability"]
        elif "headphone" in topic_lower or "earbuds" in topic_lower:
            return ["sound quality", "battery life", "comfort", "noise cancellation"]
        else:
            return ["performance", "value", "reliability"]

    def _contains_only_one_brand(self, content: str) -> bool:
        """Check if content contains only one brand (anti-bias filter)"""
        brands = ["LG", "Samsung", "Apple", "Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI", "Sony"]
        found_brands = []

        for brand in brands:
            if brand.lower() in content.lower():
                found_brands.append(brand)

        return len(found_brands) <= 1
