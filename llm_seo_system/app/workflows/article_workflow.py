from app.agents.research_agent import ResearchAgent
from app.agents.article_agent import ArticleAgent
from app.strategy.brand_strategy import BrandStrategy

from app.agents.entity_agent import EntityAgent
from app.agents.seo_agent import SEOAgent
from app.agents.seo_scorer import SEOScorer
from app.agents.internal_linking_agent import InternalLinkingAgent
import os
from app.services.memory_service import MemoryService
from app.agents.site_brain_agent import SiteBrainAgent
from app.agents.citation_optimizer_agent import CitationOptimizerAgent
from app.agents.query_simulator_agent import QuerySimulatorAgent
from app.agents.site_brain_agent import SiteBrainAgent







class ArticleWorkflow:
    def __init__(self):
        self.query_agent = QuerySimulatorAgent()
        self.citation_agent = CitationOptimizerAgent()
        self.site_brain = SiteBrainAgent()
        self.memory = MemoryService()
        self.internal_linking_agent = InternalLinkingAgent()
        self.research_agent = ResearchAgent()
        self.brand_agent = BrandStrategy()
        self.entity_agent = EntityAgent()
        self.article_agent = ArticleAgent()
        self.seo_agent = SEOAgent()
        self.seo_scorer = SEOScorer()

    def get_existing_topics(self):
        folder = "outputs"
        if not os.path.exists(folder):
            return []

        files = os.listdir(folder)
        topics = [f.replace(".md", "").replace("_", " ") for f in files]
        return topics

    def run(self, topic: str):
        print("Researching...")
        research_data = self.research_agent.research(topic)

        print("Brand strategy...")
        brand_voice = self.brand_agent.get_strategy(topic)

        print("Extracting SEO entities...")
        entities = self.entity_agent.extract_entities(research_data)

        print("Generating article...")
        article = self.article_agent.generate_article(
            topic=topic,
            research_data=research_data,
            brand_voice=brand_voice,
            entities=entities
        )

        print("Generating SEO search queries...")
        seo_queries = self.seo_agent.generate_search_queries(topic)

        print("Generating FAQ...")
        faq = self.seo_agent.generate_faq(topic)

        print("SEO optimizing...")
        optimized_article = self.seo_agent.optimize_article(article, entities)

        print("Scoring article SEO quality...")
        seo_score = self.seo_scorer.score_article(optimized_article, topic)
        
        print(" Generating internal links...")
        existing_topics = self.get_existing_topics()
        related_links = self.internal_linking_agent.generate_links(topic, existing_topics)

        # Добавляем внутренние ссылки в статью
        article_with_links = article + f"\n\n## Related Articles\n{related_links}"
        
        # Сохраняем данные в память
        memory_entry = {
            "seo_score": seo_score,
            "entities": entities,
            "related_links": related_links,
            "seo_queries": seo_queries,
            "faq": faq
        }
        self.memory.save_article_record(topic, memory_entry)

        print(" Planning next articles...")
        next_plan = self.site_brain.plan_next_articles(topic, memory_entry)

        print("\n=== NEXT CONTENT STRATEGY ===")
        print(next_plan)

        return {
            "topic": topic,
            "raw_article": article,
            "seo_queries": seo_queries,
            "faq": faq,
            "article": article_with_links,
            "optimized_article": optimized_article,
            "seo_score": seo_score
        }
