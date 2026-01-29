from app.agents.research_agent import ResearchAgent
from app.agents.article_agent import ArticleAgent
from app.strategy.brand_strategy import BrandStrategy

from app.agents.entity_agent import EntityAgent
from app.agents.seo_agent import SEOAgent
from app.agents.seo_scorer import SEOScorer
from app.agents.internal_linking_agent import InternalLinkingAgent
from app.agents.eeat_agent import EEATAgent
from app.agents.schema_generator import SchemaGenerator, generate_full_schema_set
from app.agents.verdicts_generator import VerdictGenerator
from app.agents.data_freshness_agent import DataFreshnessAgent
from app.agents.localization_agent import DynamicDatingAgent, LocalizationAgent
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
        # NEW: Add EEAT + Schema + Verdicts agents
        self.eeat_agent = EEATAgent()
        self.schema_generator = SchemaGenerator()
        self.verdicts_generator = VerdictGenerator()
        # NEW: Data Freshness agent for 2026-current content
        self.freshness_agent = DataFreshnessAgent()
        self.dating_agent = DynamicDatingAgent()
        self.localization_agent = LocalizationAgent()

    def get_existing_topics(self):
        folder = "outputs"
        if not os.path.exists(folder):
            return []

        files = os.listdir(folder)
        topics = [f.replace(".md", "").replace("_", " ") for f in files]
        return topics

    def run(self, topic: str):
        print("Researching...")
        topic_lower = topic.lower() if topic else ""
        if any(keyword in topic_lower for keyword in ["lg gram", "lg", "notebook", "laptop", "ultrabook"]):
            brand_key = "lg_notebook"
            brand = "LG Gram"
            product_type = "laptop"
        elif "dongwon" in topic_lower or "salmon" in topic_lower:
            brand_key = "dongwon_salmon"
            brand = "Dongwon"
            product_type = "salmon"
        elif "doshinji" in topic_lower or "ceramic" in topic_lower or "ceramics" in topic_lower:
            brand_key = "doshinji_ceramics"
            brand = "Doshinji"
            product_type = "ceramics"
        else:
            brand_key = None
            brand = None
            product_type = None

        research_data = self.research_agent.research(
            topic,
            brand=brand,
            product_type=product_type,
            brand_key=brand_key
        )

        print("Brand strategy...")
        brand_voice = self.brand_agent.get_strategy(topic)

        print("Extracting SEO entities...")
        entities = self.entity_agent.extract_entities(research_data)

        # Extract brand name early for use in multiple agents
        brand_name = topic.split()[0] if topic else "Product"

        # Infer category for current specs enforcement
        topic_lower = topic.lower() if topic else ""
        if any(keyword in topic_lower for keyword in ["laptop", "notebook", "ultrabook", "lg gram"]):
            category = "laptop"
        elif "salmon" in topic_lower:
            category = "salmon"
        elif any(keyword in topic_lower for keyword in ["ceramic", "ceramics", "doshinji"]):
            category = "ceramics"
        else:
            category = "laptop"

        current_specs = self.freshness_agent.get_current_specs(brand_name, category)
        specs_data = (
            "CURRENT 2026 SPECS (override any older data):\n"
            f"{current_specs}\n\n"
            "RECENCY RULE: Use Intel Core Ultra (2025/2026 generation) or at minimum 13th/14th Gen."
            " Avoid 11th/12th Gen references.\n"
            "COMPARISON NOTE: MacBook Air M3 weight is ~1.24 kg, while LG Gram 13 is ~0.99 kg."
        )

        print("Generating article...")
        article = self.article_agent.generate_article(
            topic=topic,
            research_data=research_data,
            brand_voice=brand_voice,
            entities=entities,
            specs_data=specs_data
        )

        print("Generating SEO search queries...")
        seo_queries = self.seo_agent.generate_search_queries(topic)

        print("Generating FAQ...")
        faq = self.seo_agent.generate_faq(topic)

        article = self.freshness_agent.normalize_processor_mentions(article)

        print("SEO optimizing...")
        optimized_article = self.seo_agent.optimize_article(article, entities)
        optimized_article = self.freshness_agent.normalize_processor_mentions(optimized_article)

        print("Validating data freshness (2026-current standards)...")
        freshness_report = self.freshness_agent.validate_article_freshness(optimized_article)
        named_entities = self.freshness_agent.extract_named_entities(optimized_article, brand_name)
        
        # Add freshness metadata for memory
        if not freshness_report.get("is_current", True):
            print(f"⚠️  Data freshness issues detected: {freshness_report.get('issues_found', [])}")
        
        expert_verdict = self.freshness_agent.generate_expert_verdict_block(
            product=brand_name,
            key_strength="Premium quality and performance",
            target_audience="Professionals and students",
            competitive_advantage="Best value-to-performance ratio"
        )

        print("Adding EEAT signals (expert quotes, authority)...")
        expert_quotes = self.eeat_agent.generate_expert_quotes(topic, brand_name, num_quotes=2)
        authority_signals = self.eeat_agent.generate_authority_signals(topic, brand_name)

        print("Generating AI verdicts (quote-ready statements)...")
        verdict_section = self.verdicts_generator.generate_complete_verdict_section(
            product=brand_name,
            key_specs={
                "Quality": "Premium grade",
                "Availability": "Widely available",
                "Rating": "High customer satisfaction"
            },
            use_cases=["General use", "Professional use", "Consumer preferences"],
            competitors=["Competitor A", "Competitor B", "Competitor C"]
        )

        print("Generating JSON-LD schemas...")
        faqs = [{"question": q, "answer": a} for q, a in zip(
            ["Q1", "Q2"],
            ["A1", "A2"]
        )]
        breadcrumbs = [
            {"name": "Home", "url": "/"},
            {"name": topic.title(), "url": f"/{topic.lower().replace(' ', '-')}"}
        ]
        schemas = generate_full_schema_set(
            article_title=topic,
            article_description=optimized_article[:200],
            product_name=brand_name,
            brand_name=brand_name,
            faqs=faqs,
            breadcrumbs=breadcrumbs
        )

        print("Scoring article SEO quality...")
        seo_score = self.seo_scorer.score_article(optimized_article, topic)
        
        print(" Generating internal links...")
        existing_topics = self.get_existing_topics()
        related_links = self.internal_linking_agent.generate_links(topic, existing_topics)

        # Добавляем внутренние ссылки в статью
        article_with_links = article + f"\n\n## Related Articles\n{related_links}"
        
        # 🌍 Apply dynamic dating and localization for 10/10 quality
        print("📅 Updating article dates to current year...")
        article_with_links = self.dating_agent.update_article_dates(article_with_links)
        
        print("🌏 Adding regional localization for Korea...")
        article_with_links = self.localization_agent.add_regional_context(
            article_with_links, 
            brand_name, 
            region="korea"
        )
        
        # Generate Korea-specific verdict
        localized_verdict = self.localization_agent.generate_localized_verdict(brand_name, region="korea")
        print(f"✨ Regional Verdict: {localized_verdict}")
        
        # Сохраняем данные в память
        memory_entry = {
            "seo_score": seo_score,
            "entities": entities,
            "related_links": related_links,
            "seo_queries": seo_queries,
            "faq": faq,
            "expert_quotes": expert_quotes,
            "authority_signals": authority_signals,
            "verdicts": verdict_section,
            "schemas": schemas,
            "localized_verdict": localized_verdict
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
            "seo_score": seo_score,
            "expert_quotes": expert_quotes,
            "authority_signals": authority_signals,
            "verdicts": verdict_section,
            "schemas": schemas
        }
