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

app = Flask(__name__)
CORS(app)

# Initialize services
workflow = ArticleWorkflow()
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


if __name__ == "__main__":
    print("🚀 Starting AI SEO Blog Generator API...")
    print("📍 Running on http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
