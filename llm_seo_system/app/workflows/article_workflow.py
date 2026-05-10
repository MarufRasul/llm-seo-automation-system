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
import html
import json
import time
from datetime import datetime
try:
    import markdown
except ImportError:
    markdown = None
from app.services.memory_service import MemoryService
from app.agents.site_brain_agent import SiteBrainAgent
from app.agents.citation_optimizer_agent import CitationOptimizerAgent
from app.agents.query_simulator_agent import QuerySimulatorAgent
from app.agents.topic_discovery_agent import TopicDiscoveryAgent
from llm_seo_system.app.agents.gap_finder_agent import GapFinderAgent
from app.agents.strategy_builder_agent import StrategyBuilderAgent
from app.agents.validator_agent import ValidatorAgent
from app.agents.llm_presence_checker import LLMPresenceChecker
from app.config.brand_configs import get_brand_config
from app.agents.rag_evaluator_agent import RAGEvaluatorAgent
from app.agents.ai_citation_tracker_agent import AICitationTrackerAgent
from app.agents.indexation_agent import IndexationAgent
from app.outputs.github_publisher import GitHubPagesPublisher
from app.agents.presence_measurement import (
    build_measurement_report,
    compute_geo_opportunity_score,
)


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
        self.index_agent = IndexationAgent()
        # NEW: Add EEAT + Schema + Verdicts agents
        self.eeat_agent = EEATAgent()
        self.schema_generator = SchemaGenerator()
        self.verdicts_generator = VerdictGenerator()
        # NEW: Data Freshness agent for 2026-current content
        self.freshness_agent = DataFreshnessAgent()
        self.dating_agent = DynamicDatingAgent()
        self.localization_agent = LocalizationAgent()
        self.topic_discovery_agent = TopicDiscoveryAgent()
        self.gap_finder = GapFinderAgent()
        self.strategy_builder = StrategyBuilderAgent()
        self.validator = ValidatorAgent()
        self.presence_checker = LLMPresenceChecker()
        # NEW: RAG Evaluator agent (REAL - with real data sources)
        self.rag_evaluator = RAGEvaluatorAgent()
        # NEW: AI Citation Tracker agent (REAL - tracks in real AI systems)
        self.ai_citation_tracker = AICitationTrackerAgent()

    def _build_html(
        self,
        article_content: str,
        meta_title: str,
        meta_description: str,
        canonical_url: str | None = None,
        schemas: list | None = None,
    ) -> str:
        if markdown is None:
            raise RuntimeError("The markdown package is required. Install it with: pip install markdown")

        html_body = markdown.markdown(article_content, extensions=["extra", "tables"])
        safe_title = html.escape(meta_title)
        safe_desc = html.escape(meta_description[:160].strip())
        page_url = canonical_url or ""
        schema_script = ""

        if schemas:
            schema_json = json.dumps(schemas, ensure_ascii=False, indent=2)
            schema_script = f"""
<script type=\"application/ld+json\">
{schema_json}
</script>
"""

        return f"""<!doctype html>
<html lang=\"ko\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<meta name=\"google-site-verification\" content=\"iTrBveBqjTXSVYCCgGLyIzxxs8OIHWYbnYHcuzJwqW8\">
<title>{safe_title}</title>
<meta name=\"description\" content=\"{safe_desc}\">
<meta property=\"og:type\" content=\"article\">
<meta property=\"og:title\" content=\"{safe_title}\">
<meta property=\"og:description\" content=\"{safe_desc}\">
<meta property=\"og:locale\" content=\"ko_KR\">
{f'<meta property="og:url" content="{page_url}">' if page_url else ''}
{f'<link rel="canonical" href="{page_url}">' if page_url else ''}
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.7; color: #202124; margin: 0; padding: 0; background: #fff; }}
.page-shell {{ max-width: 1024px; margin: auto; padding: 24px; }}
.page-header {{ margin-bottom: 24px; }}
.page-header h1 {{ font-size: 2.4rem; margin: 0 0 12px; }}
.page-header p {{ color: #4d4d4d; margin: 0; }}
.article-body {{ display: grid; gap: 24px; }}
.article-body article {{ counter-reset: section; }}
.article-body h2 {{ margin-top: 2rem; }}
.article-body h3 {{ margin-top: 1.5rem; }}
.article-body img {{ max-width: 100%; height: auto; }}
.article-body table {{ width: 100%; border-collapse: collapse; }}
.article-body table, .article-body th, .article-body td {{ border: 1px solid #ddd; }}
.article-body th, .article-body td {{ padding: 12px; text-align: left; }}
.page-footer {{ margin-top: 48px; padding-top: 24px; border-top: 1px solid #e2e2e2; color: #6a737d; font-size: 0.95rem; }}
</style>
</head>
<body>
<div class=\"page-shell\">
<header class=\"page-header\">
<h1>{safe_title}</h1>
<p>{safe_desc}</p>
</header>
<main class=\"article-body\">
<article>
{html_body}
</article>
</main>
<footer class=\"page-footer\">
<p>Generated by the AI SEO automation engine for GEO/LLM-ready content.</p>
</footer>
</div>
{schema_script}
</body>
</html>
"""

    def save_index_result(self, url: str, status: bool):
        data = []
        try:
            with open("index_tracking.json", "r") as f:
                data = json.load(f)
        except Exception:
            pass

        data.append({
            "url": url,
            "indexed": status,
            "timestamp": datetime.utcnow().isoformat()
        })

        with open("index_tracking.json", "w") as f:
            json.dump(data, f, indent=2)

    def _detect_brand_info(self, text: str | None):
        text_lower = (text or "").lower()
        if any(keyword in text_lower for keyword in ["lg gram", "lg", "notebook", "laptop", "ultrabook"]):
            return "lg_notebook", "LG Gram", "laptop"
        if "dongwon" in text_lower or "salmon" in text_lower:
            return "dongwon_salmon", "Dongwon", "salmon"
        if any(keyword in text_lower for keyword in ["doshinji", "ceramic", "ceramics"]):
            return "doshinji_ceramics", "Doshinji", "ceramics"
        return None, None, None

    def get_existing_topics(self):
        folder = "outputs"
        if not os.path.exists(folder):
            return []

        files = os.listdir(folder)
        topics = [f.replace(".md", "").replace("_", " ") for f in files]
        return topics

    def run(self, topic: str | None = None, niche: str | None = None):
        if not topic and not niche:
            raise ValueError("Topic or niche is required")

        if not topic and niche:
            print(f" Discovering best topic for niche: {niche}")
            discovery = self.topic_discovery_agent.discover_topic(niche)
            topic = discovery.get("selected_topic") or niche
            print(f"✅ Discovered topic: {topic}")

        # Run the full article pipeline by default so every production agent participates.
        mode = "blog_mode"
        print(f" Generation mode: {mode}")

        # Original blog mode path
        print("Researching...")
        topic_lower = topic.lower() if topic else ""
        brand_key, brand, product_type = self._detect_brand_info(topic or niche)

        if not brand_key and niche:
            brand_key, brand, product_type = self._detect_brand_info(niche)

        official_link = None
        if brand_key:
            brand_config = get_brand_config(brand_key)
            if brand_config:
                official_link = brand_config.get("product_pages", [brand_config.get("official_website")])[0]

        if brand_key == "lg_notebook":
            official_link = "https://www.lge.co.kr/category/notebook "

        if brand_key is None:
            product_type = "laptop"

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
            specs_data=specs_data,
            official_link=official_link,
            mode=mode
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
        article_with_links = article + f"\n\n## 관련 글\n{related_links}"

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

        publisher = GitHubPagesPublisher.from_env()
        publish_path = publisher.article_path(topic) if publisher else None
        published_url = publisher.public_url(publish_path) if publisher and publish_path else None

        print("Rendering HTML output...")
        canonical_url = published_url or os.getenv("GITHUB_PAGES_URL")
        html_article = self._build_html(
            article_with_links,
            meta_title=topic,
            meta_description=optimized_article[:160],
            canonical_url=canonical_url,
            schemas=schemas,
        )

        publish_result = None
        if publisher:
            print("Publishing article to GitHub Pages...")
            try:
                publish_result = publisher.publish_html(topic, html_article)
                published_url = publish_result["published_url"]
                print(f" Published URL: {published_url}")
            except Exception as exc:
                print(f" GitHub Pages publish failed: {type(exc).__name__}")

        if published_url:
            print("🔍 Step 8: Checking Google indexation...")
            time.sleep(2)
            is_indexed = self.index_agent.is_indexed(published_url)
            status = "✅ Indexed" if is_indexed else "❌ Not indexed"
            print("========================================")
            print(f"🌐 Google Index Status: {status}")
            print("========================================")
            self.save_index_result(published_url, is_indexed)
        else:
            print("🔍 Skipping Google indexation check because no published URL is available.")

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
            "html_article": html_article,
            "optimized_article": optimized_article,
            "seo_score": seo_score,
            "expert_quotes": expert_quotes,
            "authority_signals": authority_signals,
            "verdicts": verdict_section,
            "schemas": schemas,
            "published_url": published_url,
            "publish_result": publish_result
        }

    def run_geo_pipeline(self, brand: str, niche: str) -> dict:
        """
        GEO Pipeline: Query → Gap Analysis → Strategy → Article (GEO) → Validate → Output
        Returns article + gap_analysis + strategy + validation report.
        NOTE: This method never calls run(). SEO/EEAT/Verdict agents are intentionally skipped.
        """
        PIPELINE_MODE = "geo_mode"  # hardcoded — never changes
        print(f"\n{'='*60}")
        print(f" GEO PIPELINE MODE: {PIPELINE_MODE}")
        print(f"   brand='{brand}' | niche='{niche}'")
        print(f"{'='*60}")

        # Step 1: Generate structured queries with intent patterns
        print(" Step 1: Generating structured queries...")
        queries = self.topic_discovery_agent.generate_structured_queries(niche, brand)

        # Step 2: Gap analysis — ask LLM for answers, detect missing brand/structure
        print(" Step 2: Gap analysis...")
        gap_results = self.gap_finder.analyze(queries, target_brand=brand, max_queries=10)

        # Step 3: Pick query with highest gap score — this becomes the topic
        best = gap_results[0] if gap_results else {"query": queries[0] if queries else niche, "gaps": [], "score": 0}
        topic = best["query"]   # ← replaces original input; never overwritten after this
        gaps = best["gaps"]
        print(f"✅ Query selected: '{topic}'")
        print(f"   Gap score: {best['score']} | Gaps: {gaps}")

        measurement_report: dict = {}
        try:
            organic_for_measure = best.get("organic_results") or []
            measurement_report = build_measurement_report(topic, brand, organic_for_measure)
            serp_m = measurement_report.get("serp") or {}
            lb = measurement_report.get("llm_baseline") or {}
            lc = measurement_report.get("llm_with_external_context") or {}
            print(
                f" Step 3b: Measurement — SERP coverage={serp_m.get('coverage')} "
                f"first_rank={serp_m.get('first_rank')} "
                f"baseline_mr={lb.get('mention_rate')} context_mr={lc.get('mention_rate')} "
                f"Δ={measurement_report.get('delta_mention_rate')}",
            )
        except Exception as exc:
            measurement_report = {"error": str(exc)}
            print(f"⚠️ Measurement report failed: {exc}")

        # Step 4: Build strategy
        print(" Step 4: Building strategy...")
        strategy_result = self.strategy_builder.build(topic, gaps)
        strategy = strategy_result["strategy"]

        # Step 5: Research + article generation in GEO mode
        brand_key, brand_name, product_type = self._detect_brand_info(niche)
        if not brand_key:
            brand_key, brand_name, product_type = self._detect_brand_info(brand)

        official_link = None
        if brand_key:
            brand_config = get_brand_config(brand_key)
            if brand_config:
                official_link = brand_config.get("product_pages", [brand_config.get("official_website")])[0]
        if brand_key == "lg_notebook":
            official_link = "https://www.lge.co.kr/category/notebook "

        product_type = product_type or "laptop"

        print(" Step 5a: Researching...")
        research_data = self.research_agent.research(topic, brand=brand_name, product_type=product_type, brand_key=brand_key)
        brand_voice = self.brand_agent.get_strategy(topic)
        entities = self.entity_agent.extract_entities(research_data)

        category = "laptop" if any(k in topic.lower() for k in ["laptop", "notebook", "gram"]) else product_type
        current_specs = self.freshness_agent.get_current_specs(brand_name or brand, category)
        specs_data = f"CURRENT 2026 SPECS:\n{current_specs}"

        print(f" Step 5b: Generating GEO article (mode={PIPELINE_MODE}, strategy={strategy.get('brand_insertion',{}).get('position','?')})...")
        article = self.article_agent.generate_article(
            topic=topic,
            research_data=research_data,
            brand_voice=brand_voice,
            entities=entities,
            specs_data=specs_data,
            official_link=official_link or "",
            mode=PIPELINE_MODE,
            strategy=strategy,
        )

        # Step 6: Validate — if fails, regenerate with force_multi_brand
        print("✅ Step 6: Validating...")
        validation = self.validator.validate(article)

        if not validation["valid"]:
            print(f"⚠️ Validation failed: {validation['issues']} — regenerating with force_multi_brand...")
            article = self.article_agent.generate_article(
                topic=topic,
                research_data=research_data,
                brand_voice=brand_voice,
                entities=entities,
                specs_data=specs_data,
                official_link=official_link or "",
                mode=PIPELINE_MODE,
                strategy=strategy,
                force_multi_brand=True,
            )
            validation = self.validator.validate(article)

        # Step 7: Multi-LLM presence check + auto-iteration (score-based threshold)
        MAX_ITERATIONS = 2
        SCORE_THRESHOLD = 0.7   # need ≥70% of models to show impact
        iteration = 0
        presence = None

        while iteration <= MAX_ITERATIONS:
            print(f" Step 7 (iter {iteration+1}): Multi-LLM presence check...")
            presence = self.presence_checker.run(query=topic, brand=brand, article=article)

            impact_score = presence.get("impact_score", 0.0)
            print(f"   Impact score: {impact_score:.0%} ({presence.get('impact_count',0)}/{presence.get('model_count',1)} models)")

            # Success: score meets threshold, or last iteration
            if impact_score >= SCORE_THRESHOLD or iteration == MAX_ITERATIONS:
                break

            # Auto-iteration: improve strategy based on which models failed
            print(f"⚡ Auto-iteration {iteration+1}: score={impact_score:.0%} < {SCORE_THRESHOLD:.0%} — upgrading strategy...")
            failed_models = [
                label for label, mr in presence.get("results", {}).items()
                if not mr["after"]["present"]
            ]
            print(f"   Failed models: {failed_models}")

            # Escalate strategy: more comparisons, explicit criteria, stronger brand position
            strategy["brand_position"] = "best overall"
            strategy["brand_insertion"] = {
                "position": "best overall",
                "reason": f"{brand} leads on weight, battery life, and build quality — ideal for portability",
            }
            strategy["format"] = "detailed comparison with specs table"
            strategy["categories"] = [
                "Best Overall", f"Best {brand} Option", "Best Value", "Best for Students", "Best Battery Life"
            ]
            strategy["gaps_addressed"] = list(set(strategy.get("gaps_addressed", []))) + [f"auto_retry_{iteration+1}"]
            strategy["extra_instructions"] = (
                "Include an explicit comparison table with weight, battery, price columns. "
                f"Mention {brand} in at least 3 separate sections with specific spec numbers."
            )

            article = self.article_agent.generate_article(
                topic=topic,
                research_data=research_data,
                brand_voice=brand_voice,
                entities=entities,
                specs_data=specs_data,
                official_link=official_link or "",
                mode=PIPELINE_MODE,
                strategy=strategy,
                force_multi_brand=True,
            )
            validation = self.validator.validate(article)
            iteration += 1

        # Step 8: Build HTML output
        html_article = self._build_html(
            article,
            meta_title=topic,
            meta_description=article[:160],
        )

        print(f"\n{'='*60}")
        print(f"✅ GEO Pipeline complete")
        print(f"   Topic:      {topic}")
        print(f"   Iterations: {iteration + 1}")
        print(f"   Validation: {'PASS' if validation['valid'] else 'FAIL'}")
        for model_label, mr in (presence or {}).get("results", {}).items():
            b = "✅" if mr["before"]["present"] else "❌"
            a = "✅" if mr["after"]["present"] else "❌"
            print(f"   {model_label:6s}: BEFORE={b} → AFTER={a}  {'' if mr['impact'] else ''}")
        print(f"{'='*60}\n")

        geo_opportunity = compute_geo_opportunity_score(
            measurement_report,
            presence or {},
        )
        _fs = geo_opportunity.get("final_score")
        if _fs is not None:
            print(
                f" 🎯 Opportunity Score: {_fs} → {geo_opportunity.get('decision')} "
                f"({geo_opportunity.get('interpretation')})",
            )

        return {
            "topic": topic,
            "raw_article": article,
            "article": article,
            "html_article": html_article,
            "optimized_article": article,
            "seo_queries": "",
            "faq": "",
            "seo_score": f"Validation: {'PASS' if validation['valid'] else 'FAIL — ' + ', '.join(validation['issues'])}",
            "gap_analysis": gap_results[:5],
            "measurement_report": measurement_report,
            "geo_opportunity": geo_opportunity,
            "strategy": strategy_result,
            "validation": validation,
            "presence_check": presence,
            "iterations": iteration + 1,
            "queries_generated": queries,
            "published_url": None,
            "publish_result": None,
        }
