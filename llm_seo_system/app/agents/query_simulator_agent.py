from langchain_openai import ChatOpenAI
import requests
import os
import json
from typing import List

class QuerySimulatorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.serpapi_key = os.getenv("SERPAPI_KEY", "")
        self.base_url = "https://serpapi.com/search"

    def _fetch_google_people_also_ask(self, topic: str) -> List[str]:
        """
        Fetch REAL questions from Google 'People Also Ask' section.
        These are actual questions people search for.
        """
        if not self.serpapi_key:
            print("⚠️  SERPAPI_KEY not set - skipping real Google data")
            return []
        
        try:
            print(f"🔍 Fetching REAL questions from Google 'People Also Ask' for '{topic}'...")
            response = requests.get(
                self.base_url,
                params={
                    "q": topic,
                    "api_key": self.serpapi_key,
                    "engine": "google"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                questions = []
                
                # Extract "People Also Ask" section
                if "people_also_ask" in results:
                    for item in results["people_also_ask"]:
                        question = item.get("question", "").strip()
                        if question and len(question) > 5:
                            questions.append(question)
                            print(f"   ✓ {question}")
                
                # Fallback: extract from organic results titles (real search results)
                if len(questions) < 5 and "organic_results" in results:
                    for item in results["organic_results"][:5]:
                        title = item.get("title", "").strip()
                        if title and len(title) > 10 and "?" in title:
                            questions.append(title)
                
                return questions[:8]
            else:
                print(f"❌ Google API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"⚠️  Could not fetch Google data: {e}")
            return []

    def _fetch_reddit_questions(self, topic: str) -> List[str]:
        """
        Fetch real questions from Reddit threads about the topic.
        Reddit has authentic user questions.
        """
        if not self.serpapi_key:
            return []
        
        try:
            print(f"👥 Searching Reddit for real user questions about '{topic}'...")
            response = requests.get(
                self.base_url,
                params={
                    "q": f"site:reddit.com {topic} question",
                    "api_key": self.serpapi_key,
                    "engine": "google",
                    "num": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                questions = []
                
                if "organic_results" in results:
                    for result in results["organic_results"][:3]:
                        title = result.get("title", "").strip()
                        if title and "?" in title:
                            questions.append(title)
                            print(f"   ✓ {title}")
                
                return questions
            return []
            
        except Exception as e:
            print(f"⚠️  Reddit search failed: {e}")
            return []

    def _fetch_youtube_video_titles(self, topic: str) -> List[str]:
        """
        Extract questions from YouTube video titles.
        YouTube creators make videos about what people want to know.
        """
        if not self.serpapi_key:
            return []
        
        try:
            print(f"🎥 Searching YouTube for video titles about '{topic}'...")
            response = requests.get(
                self.base_url,
                params={
                    "q": topic,
                    "api_key": self.serpapi_key,
                    "engine": "youtube",
                    "num": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                questions = []
                
                if "video_results" in results:
                    for video in results["video_results"][:3]:
                        title = video.get("title", "").strip()
                        if title and len(title) > 10:
                            questions.append(title)
                            print(f"   ✓ {title}")
                
                return questions
            return []
            
        except Exception as e:
            print(f"⚠️  YouTube search failed: {e}")
            return []

    def generate_queries(self, topic: str) -> list:
        """
        Collect REAL user questions from multiple sources:
        1. Google "People Also Ask" - real search questions
        2. Reddit - authentic user questions
        3. YouTube - creator-curated questions
        4. GPT simulation - fallback if no real data
        """
        print(f"\n🎯 QuerySimulatorAgent: Collecting REAL user questions for '{topic}'")
        all_queries = []
        
        # Priority 1: Real Google data
        google_queries = self._fetch_google_people_also_ask(topic)
        all_queries.extend(google_queries)
        
        # Priority 2: Real Reddit questions
        reddit_queries = self._fetch_reddit_questions(topic)
        all_queries.extend(reddit_queries)
        
        # Priority 3: Real YouTube topics
        youtube_queries = self._fetch_youtube_video_titles(topic)
        all_queries.extend(youtube_queries)
        
        # Fallback: Simulate if we don't have enough real data
        if len(all_queries) < 5:
            print(f"📊 Not enough real data, generating simulated questions...")
            simulated = self._simulate_queries(topic)
            all_queries.extend(simulated)
        
        # Deduplicate and clean
        unique_queries = []
        seen = set()
        for q in all_queries:
            q_lower = q.lower().strip()
            if q_lower not in seen and len(q) > 5:
                unique_queries.append(q)
                seen.add(q_lower)
        
        print(f"✅ Collected {len(unique_queries)} real user questions\n")
        return unique_queries[:10]

    def _simulate_queries(self, topic: str) -> List[str]:
        """
        Fallback: Simulate questions if real data not available.
        """
        prompt = f"""
Generate 10 natural language questions that real users ask about:

TOPIC: {topic}

Focus on:
- Buying decisions
- Comparisons
- Suitability
- Use cases
- Recommendations

Return only questions, one per line.
"""
        response = self.llm.invoke(prompt)
        queries = response.content.split("\n")
        return [q.strip("- ").strip() for q in queries if len(q.strip()) > 5]

    def simulate_ai_extraction(self, article: str, queries: list) -> dict:
        """
        Tests whether the article can answer each query
        """
        print("🧠 QuerySimulatorAgent: simulating AI query coverage")
        results = {}

        for q in queries:
            prompt = f"""
You are an AI assistant answering a user.

USER QUESTION:
{q}

ARTICLE:
{article}

If the article contains enough info to answer, extract the answer.
If not, say: NOT FOUND
"""
            response = self.llm.invoke(prompt).content

            if "NOT FOUND" in response:
                results[q] = "❌ Not covered"
            else:
                results[q] = "✅ Covered"

        coverage_score = int(
            (list(results.values()).count("✅ Covered") / len(results)) * 100
        )

        return {
            "coverage_score": coverage_score,
            "query_results": results
        }
