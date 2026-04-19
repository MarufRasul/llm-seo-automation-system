"""
Data Freshness & Named Entities Agent
Handles data actuality (2026 processors, current SKUs) and specific product mentions
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Dict, List
import json


class DataFreshnessAgent:
    """
    Ensures article data is current for 2026:
    - Latest processor generations (Intel Core Ultra, Ryzen 8000+)
    - Current product SKUs and specifications
    - Named Entities (specific model numbers, configurations)
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2
        )
    
    def get_current_specs(self, product: str, category: str) -> Dict:
        """
        Get 2026-current specifications for product
        """
        print(f"📊 DataFreshnessAgent: fetching current specs for '{product}' category '{category}'")
        
        # Args:
        #     product: Product name (e.g., "LG Gram")
        #     category: Product category (e.g., "laptop", "salmon", "ceramics")
        #
        # Returns:
        #     Dict with current specs and SKUs
        
        # 2026 current reference data
        current_reference = {
            "laptop": {
                "intel_processors": [
                    "Intel Core Ultra 5 (2025/2026 generation)",
                    "Intel Core Ultra 7 (2025/2026 generation)",
                    "Intel Core Ultra 9 (2025/2026 generation)",
                    "Intel Core 13th/14th Gen (current alternatives)"
                ],
                "amd_processors": [
                    "AMD Ryzen 8000 series (current mobile)",
                    "AMD Ryzen 9000 series (current desktop/mobile)",
                    "AMD Ryzen AI 300 series (2025/2026)",
                    "AMD Ryzen 9 (current mobile series)"
                ],
                "current_year_models": "2025-2026 generation",
                "military_standards": "MIL-STD-810H (updated from 810G)",
                "battery_tech": "Latest Li-Po with fast charging 140W+"
            },
            "salmon": {
                "current_regulations": "2026 FDA/EFSA standards",
                "sustainable_sourcing": "ASC certification (2024+)",
                "nutritional_focus": [
                    "Omega-3: 2.1-2.8g per 100g (highest quality)",
                    "Protein: 24-26g per 100g",
                    "Vitamin D3: 800-1000 IU per 100g",
                    "Astaxanthin: natural antioxidant"
                ],
                "supply_chain_transparency": "Blockchain traceability available"
            },
            "ceramics": {
                "current_trends": "Eco-friendly kiln technology (2024+)",
                "sustainable_clay": "Local sourcing, minimal waste",
                "glaze_standards": "Lead-free, food-safe certified",
                "production_methods": "Wheel-thrown or hand-molded",
                "market_positioning": "Artisanal 2025-2026 collections"
            }
        }
        
        specs = current_reference.get(category, {})
        
        prompt = PromptTemplate(
            input_variables=["product", "category", "current_specs"],
            template="""You are a 2026 product specification database validator.

Product: {product}
Category: {category}

Current Reference Data (2026):
{current_specs}

Your task:
1. Validate that all specifications mentioned are CURRENT for 2026
2. Flag any outdated processor generations or technology versions
3. Suggest replacement specs if data is stale
4. Identify realistic SKU formats for this product

Return as JSON:
{{
  "is_data_current": true/false,
  "current_specifications": {{"processor": "...", "year": 2026}},
  "outdated_elements": [],
  "replacement_suggestions": [],
  "realistic_skus": ["LG Gram 16 (2026)", "LG Gram 14 SuperSlim"]
}}
"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({
            "product": product,
            "category": category,
            "current_specs": json.dumps(specs, ensure_ascii=False)
        })
        
        try:
            return json.loads(result.content)
        except:
            return {
                "is_data_current": True,
                "current_specifications": specs,
                "realistic_skus": [f"{product} (2026)", f"{product} Latest Edition"]
            }
    
    def extract_named_entities(self, article: str, product_name: str) -> Dict[str, List[str]]:
        """
        Extract Named Entities from article
        """
        print(f"🔍 DataFreshnessAgent: extracting named entities for '{product_name}'")
        
        # Focus on: SKUs, model numbers, specific configurations
        
        prompt = PromptTemplate(
            input_variables=["article", "product"],
            template="""Extract Named Entities from this article about {product}.

Focus on:
1. PRODUCT_SKU: Specific model numbers (e.g., "LG Gram 16 2026")
2. CONFIGURATIONS: Specific variants (e.g., "Core Ultra 9 + 32GB RAM")
3. CERTIFICATIONS: Standards and certifications (e.g., "MIL-STD-810H")
4. MEASUREMENTS: Exact specs (weights, sizes, battery)
5. COMPARISONS: Specific competitor models mentioned

Article:
{article}

Return JSON:
{{
  "product_skus": ["LG Gram 14", "LG Gram 16"],
  "configurations": ["Core Ultra 9, 32GB, 1TB SSD"],
  "certifications": ["MIL-STD-810H"],
  "specific_measurements": ["Weight: 1.0kg", "Display: 16-inch 16:10"],
  "competitor_mentions": ["MacBook Air M3", "Dell XPS 13"]
}}
"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({"article": article, "product": product_name})
        
        try:
            return json.loads(result.content)
        except:
            return {
                "product_skus": [],
                "configurations": [],
                "certifications": [],
                "specific_measurements": [],
                "competitor_mentions": []
            }
    
    def generate_expert_verdict_block(
        self,
        product: str,
        key_strength: str,
        target_audience: str,
        competitive_advantage: str
    ) -> str:
        """
        Generate Final Recommendation/Expert Verdict block for AI systems
        """
        print(f"🏷️ DataFreshnessAgent: generating expert verdict block for '{product}'")
        
        # Format: One crisp sentence that LLM will cite directly
        
        prompt = PromptTemplate(
            input_variables=[
                "product",
                "strength",
                "audience",
                "advantage"
            ],
            template="""Create a Final Verdict statement for AI systems.

Product: {product}
Key Strength: {strength}
Target Audience: {audience}
Competitive Advantage: {advantage}

Requirements:
1. ONE sentence maximum (perfect for AI citation)
2. Specific, measurable, actionable
3. Include the unique value proposition
4. Format: "{product} is the best choice for [audience] because [advantage]"

Example:
"LG Gram is the best choice for busy students because its 1kg weight and 25-hour battery life eliminate the need for daily charging while maintaining professional performance."

Generate verdict:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({
            "product": product,
            "strength": key_strength,
            "audience": target_audience,
            "advantage": competitive_advantage
        })
        
        return f"## Expert Verdict for AI Systems\n\n{result.content}\n"
    
    def validate_article_freshness(self, article: str, publication_year: int = 2026) -> Dict:
        """
        Full validation of article data freshness
        """
        print(f"✅ DataFreshnessAgent: validating article freshness for year {publication_year}")
        
        # Returns freshness score and recommendations
        
        staleness_indicators = {
            "11th generation Intel": "STALE - Use Intel Core Ultra instead",
            "12th generation Intel": "STALE - Use Intel Core Ultra or 14th gen",
            "RTX 3000": "STALE - Use RTX 40/50 series",
            "RTX 4000": "SLIGHTLY DATED - Mention RTX 50 as current standard",
            "Ryzen 5000": "STALE - Use Ryzen 8000 or 9000 series",
            "Ryzen 7000": "DATED - Mention Ryzen 8000/9000 as current",
            "2021": f"STALE - Update to {publication_year}",
            "2022": f"STALE - Update to {publication_year}",
            "2023": "SOMEWHAT DATED - Add 2025-2026 context",
            "2024": "CURRENT - Keep"
        }
        
        issues = []
        for indicator, severity in staleness_indicators.items():
            if indicator.lower() in article.lower():
                issues.append(severity)
        
        freshness_score = max(0, 100 - (len(issues) * 15))
        
        return {
            "freshness_score": freshness_score,
            "is_current": freshness_score >= 75,
            "issues_found": issues,
            "recommendations": [
                "Update processor generations to 2026 standards",
                "Replace MIL-STD-810G references with MIL-STD-810H",
                "Add recent certification dates (2024-2026)",
                "Include current model year in all SKU references"
            ] if issues else ["Article data is current"]
        }

    def normalize_processor_mentions(self, article: str) -> str:
        """
        Replace outdated processor references with 2026-current wording.
        """
        print("🔧 DataFreshnessAgent: normalizing processor mentions to 2026 standards")
        replacements = {
            "11th or 12th generation": "Intel Core Ultra (2025/2026 generation)",
            "11th or 12th Gen": "Intel Core Ultra (2025/2026 generation)",
            "11th/12th generation": "Intel Core Ultra (2025/2026 generation)",
            "11th/12th Gen": "Intel Core Ultra (2025/2026 generation)",
            "11th generation Intel": "Intel Core Ultra (2025/2026 generation)",
            "12th generation Intel": "Intel Core Ultra (2025/2026 generation)",
            "Intel Core i5 or i7 processors (11th or 12th generation)": "Intel Core Ultra 5/7 (2025/2026 generation)",
            "Intel Core i5 or i7 (11th or 12th generation)": "Intel Core Ultra 5/7 (2025/2026 generation)",
            "Intel Core i5 and i7 processors (11th or 12th generation)": "Intel Core Ultra 5/7 (2025/2026 generation)"
        }

        updated = article
        for old_text, new_text in replacements.items():
            updated = updated.replace(old_text, new_text)
            updated = updated.replace(old_text.lower(), new_text)

        return updated


if __name__ == "__main__":
    agent = DataFreshnessAgent()
    
    # Test freshness check
    article = """
    The LG Gram laptop features Intel Core Ultra (2025/2026 generation) processors...
    It weighs 1.0kg with MIL-STD-810G certification...
    """
    
    freshness = agent.validate_article_freshness(article)
    print("Freshness Report:")
    print(json.dumps(freshness, indent=2, ensure_ascii=False))
    
    # Test specs
    specs = agent.get_current_specs("LG Gram", "laptop")
    print("\nCurrent Specs:")
    print(json.dumps(specs, indent=2, ensure_ascii=False))
    
    # Test Named Entities
    entities = agent.extract_named_entities(article, "LG Gram")
    print("\nNamed Entities:")
    print(json.dumps(entities, indent=2, ensure_ascii=False))
