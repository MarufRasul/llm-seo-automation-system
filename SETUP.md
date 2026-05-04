# AI SEO Blog Generator - Frontend & Backend Setup

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Backend Server

```bash
cd llm_seo_system
python api_server.py
```

Output:

```
Starting AI SEO Blog Generator API...
📍 Running on http://localhost:5000
```

### Open Frontend

Open your browser and go to:

```
file:///C:/Users/MarufRasul/Desktop/AI%20SEO%20Blog%20Generator%20Agent/frontend/index.html
```

Or use a simple HTTP server:

```bash
# From project root
python -m http.server 8000
```

Then visit: `http://localhost:8000/frontend/`

---

## Frontend Features

### Content Generator

- Enter any topic (e.g., "LG Gram laptop for students")
- Click "Generate AI-Optimized Article"
- System will:
  - Research the topic
  - Extract SEO entities
  - Generate article
  - Create FAQ blocks
  - Optimize for AI systems
  - Score SEO quality

### System Status

- View total articles generated
- View topics in memory
- Click any article to reload it

### Generated Content Tabs

- **Raw Article** - Initial generated content
- **SEO Queries** - Search questions & long-tail queries
- **FAQ Block** - Structured Q&A
- **Optimized Version** - SEO-optimized version
- **SEO Score** - Detailed scoring analysis

---

## API Endpoints

### Health Check

```
GET /api/health
```

Response:

```json
{
  "status": "ok",
  "message": "AI SEO Blog Generator API is running"
}
```

### Generate Article

```
POST /api/generate
Content-Type: application/json

{
  "topic": "LG Gram laptop for students"
}
```

Response:

```json
{
  "success": true,
  "data": {
    "topic": "LG Gram laptop for students",
    "raw_article": "...",
    "seo_queries": "...",
    "faq": "...",
    "optimized_article": "...",
    "seo_score": "...",
    "file_path": "/path/to/article.md"
  }
}
```

### Get Articles List

```
GET /api/articles
```

### Get Article Detail

```
GET /api/article/<topic>
```

### Get Memory Data

```
GET /api/memory
```

---

## UI/UX Features

✅ Modern gradient design
✅ Responsive layout (mobile-friendly)
✅ Real-time loading indicators
✅ Tab-based content viewing
✅ Error & success notifications
✅ Article quick-load
✅ System statistics

---

## Troubleshooting

### "Connection refused" Error

- Make sure backend is running: `python api_server.py`
- Check if port 5000 is available
- Try: `lsof -i :5000` to see what's using the port

### CORS Error

- Backend has CORS enabled (flask-cors)
- If still failing, check browser console for details

### Slow Generation

- First generation takes 2-3 minutes (LLM calls)
- Subsequent calls should be faster if using smaller models

---

## Project Structure

```
AI SEO Blog Generator Agent/
├── frontend/
│   └── index.html          #  Beautiful web interface
├── llm_seo_system/
│   ├── api_server.py       # Flask API
│   ├── app/
│   │   ├── main.py         # CLI entry point
│   │   ├── workflows/
│   │   │   └── article_workflow.py
│   │   ├── agents/         # AI agents
│   │   ├── services/       # Core services
│   │   └── strategy/
│   └── outputs/            # Generated articles
├── requirements.txt        # Dependencies
└── README.md
```

---

## Next Steps

1. **Customize Agents** - Modify prompts in `app/agents/`
2. **Add Database** - Store articles in PostgreSQL/MongoDB
3. **Deploy** - Use Docker + AWS/Heroku
4. **Add Authentication** - JWT tokens for multi-user
5. **Advanced UI** - Build React version for better UX

---

## Support

For issues:

1. Check `.env` file has `OPENAI_API_KEY`
2. Verify all dependencies installed
3. Check browser console for errors
4. Review backend logs for API issues

Happy content generation!
