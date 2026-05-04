"""
Flask API Server for AI SEO Blog Generator
"""
import sys
import os
import re
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from app.workflows.article_workflow import ArticleWorkflow
from app.outputs.storage_service import StorageService
from app.services.memory_service import MemoryService
from app.config.brand_configs import BRAND_CONFIGS, get_brand_topics
from app.batch.batch_generator import BatchContentGenerator
from app.agents.data_freshness_agent import DataFreshnessAgent
from app.agents.ai_citation_tracker_agent import AICitationTrackerAgent
from app.agents.competitor_intelligence_agent import CompetitorIntelligenceAgent

app = Flask(__name__)
CORS(app)

# Initialize services
workflow = ArticleWorkflow()
storage = StorageService("outputs")
memory_service = MemoryService()
batch_generator = BatchContentGenerator()
freshness_agent = DataFreshnessAgent()
citation_tracker = AICitationTrackerAgent()
competitor_intel = CompetitorIntelligenceAgent()


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "AI SEO Blog Generator API is running"})


@app.route("/api/test", methods=["GET"])
def test():
    """Test endpoint - returns sample data without LLM calls"""
    return jsonify({
        "success": True,
        "data": {
            "topic": "Test Article - LG Gram Laptop",
            "raw_article": "This is a test article about LG Gram laptops. The LG Gram series is known for its lightweight design and portability...",
            "seo_queries": "- LG Gram laptop review\n- Best lightweight laptop\n- LG Gram for students",
            "faq": "Q: Is LG Gram good? A: Yes, LG Gram is excellent for portability.\nQ: Price? A: Starting from $899",
            "optimized_article": "Optimized version: The LG Gram laptop combines lightweight design with powerful performance...",
            "seo_score": "SEO Score: 85/100\nReadability: 90%\nKeyword density: 8.5%"
        }
    })


@app.route("/api/generate", methods=["POST"])
def generate_article():
    """
    Generate SEO-optimized article for given topic
    POST /api/generate
    {
        "topic": "LG Gram laptop for students"
    }
    """
    try:
        data = request.json
        topic = data.get("topic", "").strip()
        niche = data.get("niche", "").strip()

        if not topic and not niche:
            return jsonify({"error": "Topic or niche is required"}), 400

        if niche and not topic:
            print(f"\n📝 Discovering best topic for niche: {niche}")
            result = workflow.run(topic=None, niche=niche)
        else:
            print(f"\n📝 Generating article for: {topic}")
            result = workflow.run(topic)

        # Save article to file using the generated or discovered topic
        article_topic = result.get("topic") or topic

        if result.get("mode") == "geo_mode":
            # Handle GEO mode response
            article_path = storage.save_article(article_topic, result["structured_answer"])
            response_payload = {
                "topic": result["topic"],
                "mode": "geo_mode",
                "structured_answer": result["structured_answer"],
                "html_answer": result["html_answer"],
                "file_path": article_path,
            }
        else:
            # Handle traditional blog mode response
            if result.get("html_article"):
                article_path = storage.save_article_html(article_topic, result["html_article"])
            else:
                article_path = storage.save_article(article_topic, result["article"])

            response_payload = {
                "topic": result["topic"],
                "raw_article": result["raw_article"][:500] + "...",  # Preview
                "seo_queries": result["seo_queries"],
                "faq": result["faq"],
                "optimized_article": result["optimized_article"][:500] + "...",
                "seo_score": result["seo_score"][:500] + "...",
                "file_path": article_path,
            }
        if result.get("published_url"):
            response_payload["published_url"] = result["published_url"]

        return jsonify({
            "success": True,
            "data": response_payload
        }), 200

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/discover-topic", methods=["POST"])
def discover_topic():
    """Discover a high-potential topic from a niche."""
    try:
        data = request.json
        niche = data.get("niche", "").strip()

        if not niche:
            return jsonify({"error": "Niche is required"}), 400

        print(f"\n🔎 Discovering topic for niche: {niche}")
        discovery = workflow.topic_discovery_agent.discover_topic(niche)

        return jsonify({
            "success": True,
            "data": discovery
        }), 200

    except Exception as e:
        print(f"❌ Topic discovery error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/articles", methods=["GET"])
def get_articles():
    """Get list of generated articles"""
    try:
        output_dir = "outputs"
        if not os.path.exists(output_dir):
            return jsonify({"articles": [], "count": 0})

        files = os.listdir(output_dir)
        article_names = set()
        for f in files:
            if f.endswith(".md") or f.endswith(".html"):
                article_names.add(os.path.splitext(f)[0])

        articles = sorted(article_names)

        return jsonify({
            "success": True,
            "articles": articles,
            "count": len(articles)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/article/<topic>", methods=["GET"])
def get_article_detail(topic):
    """Get detailed article content"""
    try:
        output_dir = "outputs"
        # Find file matching topic
        files = os.listdir(output_dir)

        for file in files:
            if topic.lower().replace(" ", "_") in file.lower():
                file_path = os.path.join(output_dir, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Get file stats
                file_stat = os.stat(file_path)
                created_time = datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                return jsonify({
                    "success": True,
                    "topic": topic,
                    "content": content,
                    "file_path": file_path,
                    "file_name": file,
                    "size": file_stat.st_size,
                    "created": created_time
                }), 200

        return jsonify({
            "success": False,
            "error": "Article not found"
        }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/article/<topic>", methods=["DELETE"])
def delete_article(topic):
    """Delete a generated article file and clean memory if possible."""
    try:
        output_dir = "outputs"
        files = os.listdir(output_dir)
        removed_files = []

        search_key = topic.lower()
        for file_name in files:
            base_name = os.path.splitext(file_name)[0].lower()
            if base_name == search_key:
                file_path = os.path.join(output_dir, file_name)
                os.remove(file_path)
                removed_files.append(file_name)

        if not removed_files:
            return jsonify({
                "success": False,
                "error": "Article not found"
            }), 404

        # Try to remove the memory entry associated with this article.
        base_topic = topic
        match = re.match(r"^(.*)_(\d{8}_\d{6})$", topic)
        if match:
            base_topic = match.group(1).replace("_", " ")
        else:
            base_topic = topic.replace("_", " ")

        memory_service.delete_article_record(base_topic)

        return jsonify({
            "success": True,
            "message": f"Deleted article(s): {', '.join(removed_files)}"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/memory", methods=["GET"])
def get_memory():
    """Get memory data for all topics"""
    try:
        memory_file = "memory/topics.json"
        if os.path.exists(memory_file):
            with open(memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify({
                "success": True,
                "topics": list(data.keys()),
                "count": len(data)
            }), 200

        return jsonify({
            "success": True,
            "topics": [],
            "count": 0
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= DATA FRESHNESS & VALIDATION ENDPOINTS =============

@app.route("/api/validate/freshness", methods=["POST"])
def validate_freshness():
    """
    Validate article data freshness (2026-current standards)
    POST /api/validate/freshness
    {
        "article": "Article text here...",
        "product": "LG Gram"
    }
    """
    try:
        data = request.json
        article = data.get("article", "").strip()
        product = data.get("product", "Unknown").strip()

        if not article:
            return jsonify({"error": "Article content is required"}), 400

        # Validate freshness
        freshness_report = freshness_agent.validate_article_freshness(article)

        # Extract named entities
        entities = freshness_agent.extract_named_entities(article, product)

        return jsonify({
            "success": True,
            "product": product,
            "freshness": freshness_report,
            "named_entities": entities
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/validate/article/<topic>", methods=["GET"])
def validate_article(topic):
    """
    Validate existing saved article for data freshness
    GET /api/validate/article/{topic}
    """
    try:
        output_dir = "outputs"
        files = os.listdir(output_dir)

        for file in files:
            if topic.lower().replace(" ", "_") in file.lower():
                file_path = os.path.join(output_dir, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Validate freshness
                freshness_report = freshness_agent.validate_article_freshness(content)
                entities = freshness_agent.extract_named_entities(content, topic)

                return jsonify({
                    "success": True,
                    "topic": topic,
                    "file": file,
                    "freshness": freshness_report,
                    "named_entities": entities,
                    "freshness_score": freshness_report.get("freshness_score", 0)
                }), 200

        return jsonify({
            "success": False,
            "error": "Article not found"
        }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= BATCH GENERATION ENDPOINTS =============

@app.route("/api/brands", methods=["GET"])
def get_brands():
    """Get list of available brands"""
    return jsonify({
        "success": True,
        "brands": list(BRAND_CONFIGS.keys()),
        "count": len(BRAND_CONFIGS),
        "details": {
            key: {
                "name": config["brand_name"],
                "category": config["category"],
                "topics_count": config["topics_count"]
            }
            for key, config in BRAND_CONFIGS.items()
        }
    }), 200


@app.route("/api/brand/<brand_key>/topics", methods=["GET"])
def get_brand_topics_api(brand_key):
    """Get content topics for specific brand"""
    topics = get_brand_topics(brand_key)

    if not topics:
        return jsonify({
            "success": False,
            "error": "Brand not found"
        }), 404

    return jsonify({
        "success": True,
        "brand": brand_key,
        "topics": topics,
        "count": len(topics)
    }), 200


@app.route("/api/batch/generate", methods=["POST"])
def batch_generate():
    """
    Generate batch content for multiple brands
    POST /api/batch/generate
    {
        "brands": ["dongwon_salmon", "doshinji_ceramics"],
        "topics_per_brand": 2
    }
    """
    try:
        data = request.json
        brands = data.get("brands", list(BRAND_CONFIGS.keys()))
        topics_per_brand = data.get("topics_per_brand", 2)

        print(f"\n📦 Batch generation started: {len(brands)} brands, {topics_per_brand} topics each")

        # Create new generator for this batch
        generator = BatchContentGenerator()
        results = generator.generate_batch(brands=brands, topics_per_brand=topics_per_brand)

        return jsonify({
            "success": True,
            "batch_id": generator.timestamp,
            "total_articles": len(results),
            "brands_processed": len(brands),
            "articles_per_brand": topics_per_brand,
            "status": "completed"
        }), 200

    except Exception as e:
        print(f"❌ Batch generation error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/batch/<batch_id>/status", methods=["GET"])
def batch_status(batch_id):
    """Get batch generation status"""
    # Check if batch report exists
    report_path = f"batch_reports/batch_report_{batch_id}.json"

    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        return jsonify({
            "success": True,
            "batch_id": batch_id,
            "status": "completed",
            "report": report
        }), 200

    return jsonify({
        "success": False,
        "error": "Batch not found"
    }), 404


@app.route("/api/batch/dongwon", methods=["POST"])
def batch_dongwon():
    """
    Generate Dongwon (salmon) content
    POST /api/batch/dongwon
    {
        "topics_limit": 3
    }
    """
    try:
        data = request.json or {}
        topics_limit = data.get("topics_limit", 3)

        print(f"\n🐟 Dongwon salmon content generation: {topics_limit} topics")

        generator = BatchContentGenerator()
        results = generator.generate_for_brand("dongwon_salmon", topics_limit=topics_limit)

        return jsonify({
            "success": True,
            "brand": "Dongwon (동원)",
            "articles_generated": len(results),
            "batch_id": generator.timestamp,
            "timestamp": generator.timestamp
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/batch/doshinji", methods=["POST"])
def batch_doshinji():
    """
    Generate Doshinji (ceramics) content
    POST /api/batch/doshinji
    {
        "topics_limit": 3
    }
    """
    try:
        data = request.json or {}
        topics_limit = data.get("topics_limit", 3)

        print(f"\n🍶 Doshinji ceramics content generation: {topics_limit} topics")

        generator = BatchContentGenerator()
        results = generator.generate_for_brand("doshinji_ceramics", topics_limit=topics_limit)

        return jsonify({
            "success": True,
            "brand": "Doshinji (도슨티)",
            "articles_generated": len(results),
            "batch_id": generator.timestamp,
            "timestamp": generator.timestamp
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= AI CITATION & COMPETITOR INTELLIGENCE ENDPOINTS =============

@app.route("/api/metrics/ai-citations", methods=["GET"])
def get_ai_citations():
    """Get AI citation metrics and performance."""
    try:
        report = citation_tracker.get_citation_report()
        comparison = citation_tracker.get_llm_comparison()

        return jsonify({
            "success": True,
            "data": {
                "report": report,
                "llm_comparison": comparison,
                "summary": {
                    "total_articles_tracked": report["summary"]["total_tracked"],
                    "total_citations": report["summary"]["total_citations"],
                    "citation_rate": f"{report['summary']['citation_rate']:.1f}%",
                    "top_performing_llm": max(
                        comparison["llms"].items(),
                        key=lambda x: x[1]["citation_rate"]
                    )[0] if comparison["llms"] else "N/A"
                }
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/metrics/track-citation", methods=["POST"])
def track_article_citation():
    """Track a specific article for AI citations."""
    try:
        data = request.json
        article_title = data.get("article_title", "").strip()
        article_topic = data.get("article_topic", "").strip()
        article_url = data.get("article_url")

        if not article_title or not article_topic:
            return jsonify({
                "success": False,
                "error": "article_title and article_topic are required"
            }), 400

        result = citation_tracker.track_article_citation(
            article_title=article_title,
            article_topic=article_topic,
            article_url=article_url
        )

        return jsonify({
            "success": True,
            "data": result
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/metrics/competitor-intelligence", methods=["POST"])
def get_competitor_intelligence():
    """Get competitor intelligence and content gaps."""
    try:
        data = request.json
        brand = data.get("brand", "").strip()
        competitors = data.get("competitors", [])

        if not brand:
            return jsonify({
                "success": False,
                "error": "brand is required"
            }), 400

        gap_report = competitor_intel.get_content_gap_report(brand)
        gaps = competitor_intel.find_competitor_gaps(brand, competitors)
        dashboard = competitor_intel.get_competitor_dashboard(brand)

        return jsonify({
            "success": True,
            "data": {
                "gap_report": gap_report,
                "gap_opportunities": gaps,
                "dashboard": dashboard
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/metrics/dashboard", methods=["GET"])
def get_metrics_dashboard():
    """Get comprehensive metrics dashboard."""
    try:
        # Get all metrics
        citations = citation_tracker.get_citation_report()
        citation_summary = citations["summary"]

        # Get article count from output directory
        output_dir = "outputs"
        article_count = 0
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            article_names = set()
            for f in files:
                if f.endswith(".md") or f.endswith(".html"):
                    article_names.add(os.path.splitext(f)[0])
            article_count = len(article_names)

        dashboard_data = {
            "generated_at": datetime.now().isoformat(),
            "ai_visibility": {
                "total_articles": article_count,
                "articles_cited_by_llms": citation_summary.get("total_citations", 0),
                "citation_rate": f"{citation_summary.get('citation_rate', 0):.1f}%",
                "status": "✅ Active" if citation_summary.get("citation_rate", 0) > 10 else "⏳ Building"
            },
            "content_gaps": {
                "high_priority_gaps": 8,
                "quick_win_opportunities": 3,
                "recommended_topics_this_week": 5
            },
            "llm_performance": {
                "chatgpt": "📈 Strong",
                "claude": "📊 Stable",
                "perplexity": "📈 Growing"
            },
            "next_actions": [
                "Track 5 new articles for citations",
                "Fill 3 high-priority content gaps",
                "Optimize top articles for better AI readability"
            ]
        }

        return jsonify({
            "success": True,
            "data": dashboard_data
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("🚀 Starting AI SEO Blog Generator API...")
    print(f"📍 Running on http://localhost:{port}")
    app.run(debug=True, host="0.0.0.0", port=port)
