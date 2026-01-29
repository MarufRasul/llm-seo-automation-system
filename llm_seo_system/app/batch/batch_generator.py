"""
Batch Content Generator for Multi-Brand GEO Strategy
Generates multiple articles across brands simultaneously
"""

import json
import os
from datetime import datetime
from app.workflows.article_workflow import ArticleWorkflow
from app.config.brand_configs import BRAND_CONFIGS, get_brand_topics
from app.services.memory_service import MemoryService


class BatchContentGenerator:
    """Generate content for multiple brands and topics"""
    
    def __init__(self):
        self.workflow = ArticleWorkflow()
        self.memory = MemoryService()
        self.results = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def generate_for_brand(self, brand_key, topics_limit=3):
        """
        Generate articles for single brand
        
        Args:
            brand_key: Brand identifier (lg_notebook, dongwon_salmon, doshinji_ceramics)
            topics_limit: How many topics to generate for this brand
        """
        
        config = BRAND_CONFIGS.get(brand_key)
        if not config:
            print(f"❌ Brand not found: {brand_key}")
            return []
        
        print(f"\n{'='*60}")
        print(f"🎯 Generating content for: {config['brand_name']}")
        print(f"{'='*60}")
        
        topics = get_brand_topics(brand_key)[:topics_limit]
        brand_results = []
        
        for idx, topic in enumerate(topics, 1):
            print(f"\n[{idx}/{len(topics)}] Processing: {topic}")
            
            try:
                # Run workflow
                result = self.workflow.run(topic)
                
                # Enrich with brand metadata
                enriched_result = {
                    "brand": brand_key,
                    "brand_name": config["brand_name"],
                    "topic": topic,
                    "timestamp": self.timestamp,
                    **result
                }
                
                brand_results.append(enriched_result)
                self.results.append(enriched_result)
                
                print(f"✅ Generated: {topic}")
                
            except Exception as e:
                print(f"❌ Error generating {topic}: {str(e)}")
                continue
        
        return brand_results
    
    
    def generate_batch(self, brands=None, topics_per_brand=3):
        """
        Generate articles for multiple brands
        
        Args:
            brands: List of brand keys. If None, generates for all brands
            topics_per_brand: Number of topics per brand
        """
        
        if brands is None:
            brands = list(BRAND_CONFIGS.keys())
        
        print(f"\n{'#'*60}")
        print(f"# 🚀 BATCH GEO CONTENT GENERATION")
        print(f"# Brands: {len(brands)} | Topics per brand: {topics_per_brand}")
        print(f"{'#'*60}\n")
        
        for brand_key in brands:
            self.generate_for_brand(brand_key, topics_per_brand)
        
        # Generate report
        self._generate_report()
        
        return self.results
    
    
    def _generate_report(self):
        """Generate summary report"""
        
        report = {
            "timestamp": self.timestamp,
            "total_articles": len(self.results),
            "brands": {},
            "statistics": {}
        }
        
        # Group by brand
        for result in self.results:
            brand = result.get("brand", "unknown")
            if brand not in report["brands"]:
                report["brands"][brand] = []
            report["brands"][brand].append({
                "topic": result.get("topic"),
                "file_path": result.get("file_path", "pending")
            })
        
        # Statistics
        report["statistics"] = {
            "total_brands": len(report["brands"]),
            "articles_per_brand": {
                brand: len(articles) 
                for brand, articles in report["brands"].items()
            }
        }
        
        # Save report
        report_path = f"batch_reports/batch_report_{self.timestamp}.json"
        os.makedirs("batch_reports", exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 GENERATION REPORT")
        print(f"{'='*60}")
        print(f"✅ Total Articles Generated: {report['total_articles']}")
        print(f"📁 Report saved: {report_path}\n")
        
        for brand, articles in report["brands"].items():
            print(f"  {brand}: {len(articles)} articles")
        
        return report
    
    
    def get_results(self):
        """Get all generated results"""
        return self.results
    
    
    def export_results(self, format="json"):
        """Export results to file"""
        
        if format == "json":
            export_path = f"batch_exports/batch_results_{self.timestamp}.json"
            os.makedirs("batch_exports", exist_ok=True)
            
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Results exported to: {export_path}")
            return export_path
        
        return None


# Usage Example:
if __name__ == "__main__":
    # Generate for all brands, 2 topics each
    generator = BatchContentGenerator()
    
    # Option 1: Generate for specific brand
    # results = generator.generate_for_brand("dongwon_salmon", topics_limit=3)
    
    # Option 2: Generate batch for all brands
    results = generator.generate_batch(topics_per_brand=2)
    
    # Export results
    generator.export_results("json")
