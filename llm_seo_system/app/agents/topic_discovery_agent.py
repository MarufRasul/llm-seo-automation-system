from langchain_openai import ChatOpenAI
import json
from .research_agent import ResearchAgent
from .query_simulator_agent import QuerySimulatorAgent
from ..config.brand_configs import get_brand_config
from .web_scraper_agent import get_website_data


class TopicDiscoveryAgent:
    BAD_PATTERNS = [
        "잃어버렸",
        "도난",
        "문제",
        "고장",
        "사고",
        "분실",
        "잃어버림",
        "모르겠",
        "어떻게",
        "어디",
        "언제",
        "왜",
        "사례",
        "이야기",
    ]

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.research_agent = ResearchAgent()
        self.query_agent = QuerySimulatorAgent()

    def is_relevant_topic(self, topic: str, brand_keywords: list[str]) -> bool:
        topic_lower = topic.lower()
        return any(keyword in topic_lower for keyword in brand_keywords)

    def is_bad_intent(self, topic: str) -> bool:
        topic_lower = topic.lower()
        return any(pattern in topic_lower for pattern in self.BAD_PATTERNS)

    def score_topic(self, topic: str) -> int:
        topic_lower = topic.lower()
        score = 0
        if "lg" in topic_lower or "그램" in topic_lower:
            score += 3
        if "노트북" in topic_lower or "laptop" in topic_lower or "gram" in topic_lower:
            score += 3
        if "추천" in topic_lower or "best" in topic_lower or "best" in topic_lower:
            score += 5
        if "vs" in topic_lower or "대" in topic_lower or "vs." in topic_lower:
            score += 4
        if "배터리" in topic_lower or "performance" in topic_lower or "specs" in topic_lower:
            score += 2
        return score

    def discover_topic(self, niche: str) -> dict:
        """Discover a high-potential article topic for the given niche."""
        print(f"🧠 TopicDiscoveryAgent: discovering topic for niche '{niche}'")
        niche = niche.strip()
        if not niche:
            return {
                "selected_topic": "",
                "candidate_topics": [],
                "reason": "No niche provided.",
                "signals": {}
            }

        print(f"🔎 Discovering topics for niche: {niche}")

        candidate_questions = self.query_agent.generate_queries(niche)

        brand_keywords = []
        niche_lower = niche.lower()
        if any(keyword in niche_lower for keyword in ["lge", "lg전자", "notebook", "노트북", "laptop"]):
            brand_keywords = ["lg", "그램", "gram", "노트북", "laptop"]
        elif any(keyword in niche_lower for keyword in ["동원", "연어", "salmon"]):
            brand_keywords = ["동원", "연어", "salmon"]
        elif any(keyword in niche_lower for keyword in ["도슨티", "도자기", "ceramic", "ceramics"]):
            brand_keywords = ["도자기", "도슨티", "ceramic", "ceramics"]

        filtered_questions = [
            q for q in candidate_questions
            if (not brand_keywords or self.is_relevant_topic(q, brand_keywords))
            and not self.is_bad_intent(q)
        ]

        if filtered_questions:
            print(f"✅ Filtered questions: {len(filtered_questions)} of {len(candidate_questions)} remain after relevance/intent filtering")
        else:
            print("⚠️ No filtered questions found; using all candidate questions as fallback")
            filtered_questions = candidate_questions

        filtered_questions = sorted(
            filtered_questions,
            key=self.score_topic,
            reverse=True
        )

        signals = {
            "ai_questions": filtered_questions,
            "trends": {},
            "competitor_context": {},
            "site_data": {}
        }

        brand_config = None
        niche_lower = niche.lower()
        if any(keyword in niche_lower for keyword in ["lge", "lg전자", "notebook", "노트북", "laptop"]):
            brand_config = get_brand_config("lg_notebook")
        elif any(keyword in niche_lower for keyword in ["동원", "연어", "salmon"]):
            brand_config = get_brand_config("dongwon_salmon")
        elif any(keyword in niche_lower for keyword in ["도슨티", "도자기", "ceramic", "ceramics"]):
            brand_config = get_brand_config("doshinji_ceramics")

        if brand_config:
            try:
                site_data = get_website_data(brand_config)
                signals["site_data"] = site_data
            except Exception as e:
                print(f"⚠️ Brand site scraping failed: {e}")

        if self.research_agent.use_web_search:
            try:
                trends = self.research_agent.web_agent.search_industry_trends(niche)
                competitor_context = self.research_agent.web_agent.search_competitors(niche, "cosmetics", brand=None)
                signals["trends"] = trends
                signals["competitor_context"] = competitor_context
            except Exception as e:
                print(f"⚠️ Trend/competitor discovery failed: {e}")

        prompt = f"""
You are an AI topic selection expert for SEO content.

Niche: {niche}

Use these signals:
- What users ask AI systems like ChatGPT/Perplexity
- Trending search signals from Google
- Competitor coverage gaps

Filter topic candidates by relevance to the niche and product.
Do not choose personal stories, travel accidents, theft, loss, or non-commercial questions.
Focus on:
- product recommendations
- comparisons
- specifications
- use cases
- buying guidance
- search intent with strong SEO potential

Based on this niche, suggest 3 candidate article topics with the highest potential to be cited by AI and searched by users.
Choose the one topic that has the strongest citation potential and content gap.

Format the result as JSON with keys:
- selected_topic
- candidate_topics
- recommendation_reason
"""

        context_snippet = ""
        if filtered_questions:
            context_snippet += "\nAI user questions:\n" + "\n".join(filtered_questions[:8])
        if signals["trends"]:
            context_snippet += "\n\nGoogle trends snippets:\n"
            if isinstance(signals["trends"], dict):
                trends_text = json.dumps(signals["trends"], ensure_ascii=False, indent=2)
                context_snippet += trends_text[:1500]
        if signals["competitor_context"]:
            context_snippet += "\n\nCompetitor snippets:\n"
            if isinstance(signals["competitor_context"], dict):
                competitor_text = json.dumps(signals["competitor_context"], ensure_ascii=False, indent=2)
                context_snippet += competitor_text[:1500]

        if signals["site_data"]:
            context_snippet += "\n\nOfficial site data:\n"
            try:
                site_data_text = json.dumps(signals["site_data"], ensure_ascii=False, indent=2)
                context_snippet += site_data_text[:1800]
            except Exception:
                context_snippet += str(signals["site_data"])

        prompt += f"\n\nContext:\n{context_snippet}\n"

        response = self.llm.invoke(prompt)
        selected_topic = ""
        candidate_topics = []
        recommendation_reason = ""
        try:
            parsed = json.loads(response.content)
            selected_topic = parsed.get("selected_topic", "")
            candidate_topics = parsed.get("candidate_topics", [])
            recommendation_reason = parsed.get("recommendation_reason", "")
        except Exception:
            # Fallback: parse manually if the model returns text
            lines = [line.strip() for line in response.content.splitlines() if line.strip()]
            for line in lines:
                if line.lower().startswith("selected_topic"):
                    selected_topic = line.split(":", 1)[-1].strip(' "')
                elif line.lower().startswith("candidate_topics"):
                    raw = line.split(":", 1)[-1].strip()
                    if raw.startswith("["):
                        try:
                            candidate_topics = json.loads(raw)
                        except Exception:
                            candidate_topics = [t.strip(' "') for t in raw.strip('[]').split(",") if t.strip()]
                elif line.lower().startswith("recommendation_reason"):
                    recommendation_reason = line.split(":", 1)[-1].strip(' "')

        def normalize_topic(topic: str) -> str:
            return topic.strip()

        selected_topic = normalize_topic(selected_topic)
        candidate_topics = [normalize_topic(t) for t in candidate_topics if t]

        valid_candidates = [
            t for t in candidate_topics
            if (not brand_keywords or self.is_relevant_topic(t, brand_keywords))
            and not self.is_bad_intent(t)
        ]

        if self.is_bad_intent(selected_topic) or (brand_keywords and not self.is_relevant_topic(selected_topic, brand_keywords)):
            if valid_candidates:
                print("⚠️ Selected topic failed relevance/intent validation, choosing best filtered candidate")
                selected_topic = valid_candidates[0]
            elif filtered_questions:
                selected_topic = filtered_questions[0]

        if not selected_topic and filtered_questions:
            selected_topic = filtered_questions[0]

        return {
            "selected_topic": selected_topic,
            "candidate_topics": candidate_topics,
            "recommendation_reason": recommendation_reason,
            "signals": signals,
            "raw_output": response.content
        }
