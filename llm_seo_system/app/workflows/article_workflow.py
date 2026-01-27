from app.agents.article_agent import ArticleAgent
from app.agents.seo_agent import SEOAgent



class ArticleWorkflow:
    def __init__(self):
        self.article_agent = ArticleAgent()
        self.seo_agent = SEOAgent()

    def run(self, topic: str):
        print(" Workflow started...")
        print(f" Topic: {topic}")

        # Генерация статьи
        print(" Generating article...")
        article = self.article_agent.generate_article(topic)

        #  SEO анализ
        print(" Generating SEO data...")
        search_queries = self.seo_agent.generate_search_queries(topic)
        faq_block = self.seo_agent.generate_faq(topic)

        seo_data = {
            "queries": search_queries,
            "faq": faq_block
        }

        #  SEO оптимизация статьи
        print(" Optimizing article...")
        optimized_article = self.seo_agent.optimize_article(article, seo_data)

        print(" Workflow finished!")

        return {
            "topic": topic,
            "raw_article": article,
            "seo_queries": search_queries,
            "faq": faq_block,
            "optimized_article": optimized_article
        }
