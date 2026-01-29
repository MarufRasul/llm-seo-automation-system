"""
Flask API Server for AI SEO Blog Generator
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from app.workflows.article_workflow import ArticleWorkflow
from app.outputs.storage_service import StorageService
from app.config.brand_configs import BRAND_CONFIGS, get_brand_topics
from app.batch.batch_generator import BatchContentGenerator

app = Flask(__name__)
CORS(app)

# Initialize services
workflow = ArticleWorkflow()
storage = StorageService("outputs")
batch_generator = BatchContentGenerator()
storage = StorageService("outputs")


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "AI SEO Blog Generator API is running"})


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

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        print(f"\n📝 Generating article for: {topic}")

        # Run the workflow
        result = workflow.run(topic)

        # Save article to file
        article_path = storage.save_article(topic, result["article"])

        return jsonify({
            "success": True,
            "data": {
                "topic": result["topic"],
                "raw_article": result["raw_article"][:500] + "...",  # Preview
                "seo_queries": result["seo_queries"],
                "faq": result["faq"],
                "optimized_article": result["optimized_article"][:500] + "...",
                "seo_score": result["seo_score"][:500] + "...",
                "file_path": article_path
            }
        }), 200

    except Exception as e:
        print(f"❌ Error: {str(e)}")
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
            return jsonify({"articles": []})

        files = os.listdir(output_dir)
        articles = [f.replace(".md", "") for f in files if f.endswith(".md")]

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
                with open(os.path.join(output_dir, file), "r", encoding="utf-8") as f:
                    content = f.read()

                return jsonify({
                    "success": True,
                    "topic": topic,
                    "content": content,
                    "file": file
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


if __name__ == "__main__":
    print("🚀 Starting AI SEO Blog Generator API...")
    print("📍 Running on http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
