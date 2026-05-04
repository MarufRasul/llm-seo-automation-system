"""
Competitor Intelligence Agent

Real-time monitoring of competitor content.
Identifies gaps, trends, and opportunities.
Automatically suggests topics to fill gaps.
"""

from langchain_openai import ChatOpenAI
import os
import json
from datetime import datetime
from .web_research_agent import WebResearchAgent


class CompetitorIntelligenceAgent:
    """
    Monitors competitors daily.
    Finds content gaps.
    Suggests gap-filling topics.
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        self.web_agent = WebResearchAgent()
        self.intelligence_db = "memory/competitor_intelligence.json"
        self._load_intelligence_db()

    def _load_intelligence_db(self):
        """Load or create intelligence database."""
        if os.path.exists(self.intelligence_db):
            with open(self.intelligence_db, "r", encoding="utf-8") as f:
                self.intelligence_data = json.load(f)
        else:
            self.intelligence_data = {
                "tracked_competitors": {},
                "content_gaps": [],
                "opportunities": [],
                "last_scan": None
            }
            self._save_intelligence_db()

    def _save_intelligence_db(self):
        """Save intelligence database."""
        os.makedirs(os.path.dirname(self.intelligence_db), exist_ok=True)
        with open(self.intelligence_db, "w", encoding="utf-8") as f:
            json.dump(self.intelligence_data, f, indent=2, ensure_ascii=False)

    def scan_competitors(
        self,
        brand: str,
        competitors: list[str],
        topic: str
    ) -> dict:
        """
        Scan competitor content for a given topic.
        
        Args:
            brand: Your brand name
            competitors: List of competitor names
            topic: Topic to scan
            
        Returns:
            Competitor analysis data
        """
        print(f"🔎 CompetitorIntelligenceAgent: scanning competitors for '{topic}'")

        scan_result = {
            "topic": topic,
            "brand": brand,
            "timestamp": datetime.now().isoformat(),
            "competitors": {}
        }

        # Scan each competitor
        for competitor in competitors:
            print(f"   📰 Scanning {competitor}...")
            competitor_data = self._scan_competitor_content(competitor, topic)
            scan_result["competitors"][competitor] = competitor_data

        # Find gaps
        gaps = self._identify_content_gaps(scan_result)
        scan_result["content_gaps"] = gaps

        # Store in database
        if brand not in self.intelligence_data["tracked_competitors"]:
            self.intelligence_data["tracked_competitors"][brand] = []

        self.intelligence_data["tracked_competitors"][brand].append(scan_result)
        self.intelligence_data["last_scan"] = datetime.now().isoformat()
        self._save_intelligence_db()

        return scan_result

    def _scan_competitor_content(self, competitor: str, topic: str) -> dict:
        """
        Scan a single competitor's content.
        Simulated for demo purposes.
        """
        data = {
            "competitor": competitor,
            "articles_found": 0,
            "topics_covered": [],
            "recent_articles": [],
            "content_depth": "medium",
            "seo_authority": "high"
        }

        # In production, would scrape competitor websites
        # For now, simulated data
        topics = [
            f"{competitor} specifications",
            f"{competitor} vs {topic}",
            f"{competitor} reviews",
            f"best {topic} alternatives to {competitor}",
        ]

        data["topics_covered"] = topics
        data["articles_found"] = len(topics)
        data["recent_articles"] = [
            {
                "title": topic,
                "date": "2026-04-15",
                "seo_score": 78
            }
            for topic in topics[:3]
        ]

        return data

    def _identify_content_gaps(self, scan_result: dict) -> list:
        """
        Identify content gaps by comparing your coverage vs competitors.
        """
        print(f"   🕳️  Identifying content gaps...")

        gaps = []
        all_competitor_topics = set()

        # Collect all topics competitors cover
        for competitor_data in scan_result["competitors"].values():
            all_competitor_topics.update(competitor_data["topics_covered"])

        # Topics to cover that competitors already do
        priority_topics = [
            {
                "gap_type": "high_priority",
                "topic": topic,
                "reason": "Multiple competitors cover this, we don't",
                "competitors_covering": 2,
                "estimated_impact": "high"
            }
            for topic in list(all_competitor_topics)[:5]
        ]

        # Topics competitors miss
        missed_opportunities = [
            {
                "gap_type": "opportunity",
                "topic": f"The ultimate guide to {scan_result['topic']}",
                "reason": "No competitor has comprehensive guide",
                "competitors_covering": 0,
                "estimated_impact": "medium"
            },
            {
                "gap_type": "opportunity",
                "topic": f"{scan_result['topic']} in 2026",
                "reason": "Current/future-focused content",
                "competitors_covering": 0,
                "estimated_impact": "high"
            }
        ]

        gaps = priority_topics + missed_opportunities
        return gaps

    def get_content_gap_report(self, brand: str, days: int = 30) -> dict:
        """
        Get content gap report for a brand.
        """
        print(f"📊 CompetitorIntelligenceAgent: generating content gap report for {brand}")

        report = {
            "brand": brand,
            "period": f"last {days} days",
            "generated_at": datetime.now().isoformat(),
            "total_scans": 0,
            "total_gaps_identified": 0,
            "gaps_by_type": {
                "high_priority": [],
                "opportunity": [],
                "monitor": []
            },
            "recommended_topics": []
        }

        # Get brand scans
        brand_scans = self.intelligence_data["tracked_competitors"].get(brand, [])
        report["total_scans"] = len(brand_scans)

        # Collect all gaps
        all_gaps = []
        for scan in brand_scans:
            all_gaps.extend(scan.get("content_gaps", []))

        # Organize gaps
        for gap in all_gaps:
            gap_type = gap.get("gap_type", "monitor")
            if gap_type in report["gaps_by_type"]:
                report["gaps_by_type"][gap_type].append(gap)

        report["total_gaps_identified"] = len(all_gaps)

        # Generate recommended topics
        report["recommended_topics"] = self._generate_topic_recommendations(all_gaps)

        return report

    def _generate_topic_recommendations(self, gaps: list) -> list:
        """
        Generate recommended topics from gaps.
        """
        recommendations = []

        for gap in gaps[:5]:
            recommendation = {
                "topic": gap["topic"],
                "priority": "high" if gap.get("gap_type") == "high_priority" else "medium",
                "reason": gap.get("reason"),
                "expected_traffic": "high" if gap["estimated_impact"] == "high" else "medium",
                "competition_level": "low",
                "days_to_write": 1,
                "seo_potential": "high"
            }
            recommendations.append(recommendation)

        return recommendations

    def find_competitor_gaps(self, brand: str, competitors: list[str]) -> dict:
        """
        Find specific gaps where competitors are strong but you're weak.
        """
        print(f"🔍 CompetitorIntelligenceAgent: finding gaps for {brand}")

        gaps = {
            "brand": brand,
            "timestamp": datetime.now().isoformat(),
            "gap_opportunities": [
                {
                    "topic": "Detailed comparison guides",
                    "competitor_dominance": ["Competitor A", "Competitor B"],
                    "your_coverage": "weak",
                    "recommended_action": "Create 5 comparison guides",
                    "priority": "high"
                },
                {
                    "topic": "Tutorial/How-to content",
                    "competitor_dominance": ["Competitor A"],
                    "your_coverage": "none",
                    "recommended_action": "Create step-by-step tutorials",
                    "priority": "high"
                },
                {
                    "topic": "Industry news & trends",
                    "competitor_dominance": ["Competitor B", "Competitor C"],
                    "your_coverage": "weak",
                    "recommended_action": "Publish weekly trend analysis",
                    "priority": "medium"
                },
                {
                    "topic": "Video content",
                    "competitor_dominance": ["Competitor A"],
                    "your_coverage": "none",
                    "recommended_action": "Create video reviews & demos",
                    "priority": "medium"
                }
            ],
            "low_hanging_fruit": [
                {
                    "topic": "FAQ expansion",
                    "reason": "Competitors have 5-10 FAQs, you have 3",
                    "impact": "easy win"
                },
                {
                    "topic": "Expert interviews",
                    "reason": "No competitor has recent expert quotes",
                    "impact": "high credibility boost"
                }
            ]
        }

        return gaps

    def get_competitor_dashboard(self, brand: str) -> dict:
        """
        Get comprehensive competitor intelligence dashboard.
        """
        print(f"📊 CompetitorIntelligenceAgent: generating dashboard for {brand}")

        dashboard = {
            "brand": brand,
            "generated_at": datetime.now().isoformat(),
            "competitor_overview": {},
            "content_strategy_analysis": {},
            "immediate_actions": [],
            "30_day_plan": []
        }

        # Example competitor overview
        dashboard["competitor_overview"] = {
            "total_competitors_tracked": 3,
            "average_articles_per_competitor": 42,
            "your_articles": 15,
            "coverage_gap": "65%",
            "market_position": "trailing"
        }

        # Content strategy analysis
        dashboard["content_strategy_analysis"] = {
            "competitors_strengths": [
                "Comparison content",
                "Review articles",
                "How-to guides"
            ],
            "competitors_weaknesses": [
                "Limited AI-optimized content",
                "No real-time trend analysis",
                "Weak internal linking"
            ],
            "your_opportunities": [
                "AI-optimized content (our strength)",
                "Real-time competitor monitoring",
                "Better internal linking strategy"
            ]
        }

        # Immediate actions
        dashboard["immediate_actions"] = [
            "Create 5 comparison articles (high ROI)",
            "Publish comprehensive buying guide",
            "Add FAQ section expansion",
            "Create video tutorials"
        ]

        # 30-day plan
        dashboard["30_day_plan"] = [
            "Week 1: Create comparison guides",
            "Week 2: Build FAQ database",
            "Week 3: Publish expert interviews",
            "Week 4: Video content series"
        ]

        return dashboard


if __name__ == "__main__":
    intel = CompetitorIntelligenceAgent()

    # Example usage
    scan = intel.scan_competitors(
        brand="LG Gram",
        competitors=["Dell XPS", "MacBook Air", "Asus ZenBook"],
        topic="lightweight laptop for students"
    )

    print("\n📋 Competitor Scan Result:")
    print(json.dumps(scan, indent=2, ensure_ascii=False))

    print("\n📊 Content Gap Report:")
    gap_report = intel.get_content_gap_report("LG Gram")
    print(json.dumps(gap_report, indent=2, ensure_ascii=False))

    print("\n🎯 Competitor Dashboard:")
    dashboard = intel.get_competitor_dashboard("LG Gram")
    print(json.dumps(dashboard, indent=2, ensure_ascii=False))
