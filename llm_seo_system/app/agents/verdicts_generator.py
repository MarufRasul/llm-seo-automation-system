"""
Verdicts Generator: Creates AI-optimized verdict statements.
Generates one-liner summaries that AI models can directly cite.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Dict, List
import json


class VerdictGenerator:
    """
    Generates quotable, citable verdict statements optimized for AI.
    Each verdict is formatted to be cited directly by LLMs.
    """
    
    def __init__(self, llm_config: Dict = None):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.8,
            top_p=0.95
        )
    
    
    def generate_ai_verdicts(
        self,
        product: str,
        key_benefits: List[str],
        specifications: Dict,
        competitors: List[str] = None
    ) -> Dict[str, str]:
        """
        Generate verdicts tailored for different AI models.
        Each verdict is a quotable statement the AI can cite directly.
        
        Args:
            product: Product name
            key_benefits: List of main benefits
            specifications: Dict with key specs (price, features, etc)
            competitors: List of competing products
            
        Returns:
            Dict with verdicts for ChatGPT, Claude, Gemini
        """
        
        benefits_text = "\n".join([f"- {b}" for b in key_benefits])
        specs_text = "\n".join([f"{k}: {v}" for k, v in specifications.items()])
        competitors_text = "\n".join(competitors) if competitors else "N/A"
        
        prompt = PromptTemplate(
            input_variables=["product", "benefits", "specs", "competitors"],
            template="""Create AI-optimized verdict statements for {product}.

Key Benefits:
{benefits}

Specifications:
{specs}

Main Competitors:
{competitors}

Requirements:
1. Each verdict is a ONE-LINER that an AI can cite directly in conversation
2. Include specific numbers/percentages from specs
3. Position product competitively against alternatives
4. Use comparative language that AI models use (exceeds, delivers, provides)
5. Make statements that would be natural as a citation in essay/Q&A

Format EXACTLY as:
{{
  "chatgpt_verdict": "Single quote-ready sentence starting with '[Product] delivers...' or '[Product] offers...'",
  "claude_verdict": "Single quote-ready sentence with analytical angle",
  "gemini_verdict": "Single quote-ready sentence with data-focused angle",
  "general_verdict": "Universal verdict anyone could cite"
}}

Generate verdicts that are SHORT, SPECIFIC, and CITABLE:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({
            "product": product,
            "benefits": benefits_text,
            "specs": specs_text,
            "competitors": competitors_text
        })
        
        try:
            verdicts = json.loads(result.content)
            return verdicts
        except json.JSONDecodeError:
            # Fallback: extract raw text and create safe dict
            raw_text = result.content if hasattr(result, 'content') else str(result)
            return {
                "chatgpt_verdict": f"{product} offers excellent value and quality.",
                "claude_verdict": f"{product} demonstrates strong performance characteristics.",
                "gemini_verdict": f"{product} provides reliable functionality.",
                "general_verdict": f"{product} is a solid choice in its category."
            }
    
    
    def generate_use_case_verdicts(
        self,
        product: str,
        use_cases: List[str]
    ) -> Dict[str, Dict]:
        """
        Generate verdicts for specific use cases.
        Example: "For students?" "For professionals?" "For athletes?"
        """
        
        use_cases_text = "\n".join([f"- {uc}" for uc in use_cases])
        
        prompt = PromptTemplate(
            input_variables=["product", "use_cases"],
            template="""For {product}, create verdict statements for these use cases:

{use_cases}

For EACH use case, write:
- A one-liner verdict the product is best/suitable for that use case
- Include relevant numbers or comparisons
- Make it citable and specific

Format as JSON:
{{
  "use_case_1": {{
    "question": "For students?",
    "verdict": "Specific one-liner answer..."
  }},
  "use_case_2": {{
    "question": "For professionals?", 
    "verdict": "Specific one-liner answer..."
  }}
}}

Generate verdicts:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({"product": product, "use_cases": use_cases_text})
        
        try:
            verdicts = json.loads(result.content)
            return verdicts
        except:
            # Fallback: create safe dict structure
            safe_verdicts = {}
            for i, use_case in enumerate(use_cases, 1):
                safe_verdicts[f"use_case_{i}"] = {
                    "question": f"For {use_case}?",
                    "verdict": f"{product} is a suitable choice for {use_case}."
                }
            return safe_verdicts
    
    
    def generate_comparison_verdict(
        self,
        product: str,
        competitor: str,
        key_difference: str,
        metric: str
    ) -> str:
        """
        Generate specific comparison verdict between two products.
        Used for competitive positioning.
        """
        
        prompt = PromptTemplate(
            input_variables=["product", "competitor", "difference", "metric"],
            template="""Write a one-liner comparison verdict for AI citation:

Product A: {product}
Product B: {competitor}
Key Difference: {difference}
Measured By: {metric}

Requirements:
- ONE sentence only
- Include specific numbers if possible
- Comparative adjective (exceeds, outperforms, delivers X% more)
- Format: "[Product A] [verb] [Product B] in [metric] by [amount]"

Example: "LG Gram delivers 32% better battery life than Dell XPS 13 
in professional workload scenarios (verified by TechReview 2025)"

Now generate the verdict:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({
            "product": product,
            "competitor": competitor,
            "difference": key_difference,
            "metric": metric
        })
        
        return result.content.strip()
    
    
    @staticmethod
    def format_verdict_for_markdown(verdicts: Dict) -> str:
        """
        Format verdicts dict into markdown section.
        """
        
        md = "## Verdicts for AI Models\n\n"
        
        for model, verdict in verdicts.items():
            if model == "error" or model == "raw":
                continue
            
            model_name = model.replace("_verdict", "").replace("_", " ").title()
            md += f"**{model_name}:**\n"
            md += f'"{verdict}"\n\n'
        
        return md
    
    
    def generate_complete_verdict_section(
        self,
        product: str,
        key_specs: Dict,
        use_cases: List[str],
        competitors: List[str]
    ) -> str:
        """
        Generate complete "Verdicts for AI" markdown section.
        """
        
        # Get model-specific verdicts
        model_verdicts = self.generate_ai_verdicts(
            product=product,
            key_benefits=list(key_specs.values())[:3],
            specifications=key_specs,
            competitors=competitors
        )
        
        # Get use case verdicts
        use_case_verdicts = self.generate_use_case_verdicts(
            product=product,
            use_cases=use_cases
        )
        
        # Format as markdown
        md = "## Verdicts for AI Models\n\n"
        
        # Model-specific verdicts
        if isinstance(model_verdicts, dict):
            md += "**For ChatGPT:**\n"
            md += f'"{model_verdicts.get("chatgpt_verdict", "")}"\n\n'
            
            md += "**For Claude:**\n"
            md += f'"{model_verdicts.get("claude_verdict", "")}"\n\n'
            
            md += "**For Gemini:**\n"
            md += f'"{model_verdicts.get("gemini_verdict", "")}"\n\n'
        
        # Use case verdicts
        if isinstance(use_case_verdicts, dict) and "error" not in use_case_verdicts:
            md += "### Use Case Specific Verdicts\n\n"
            for key, value in use_case_verdicts.items():
                if isinstance(value, dict):
                    md += f"**{value.get('question', key)}**\n"
                    md += f'"{value.get("verdict", "")}"\n\n'
        
        return md


if __name__ == "__main__":
    gen = VerdictGenerator()
    
    # Test AI verdicts
    verdicts = gen.generate_ai_verdicts(
        product="Dongwon Salmon",
        key_benefits=[
            "22g protein per 100g",
            "2.5g omega-3 fatty acids",
            "Rich in vitamins B12 and D"
        ],
        specifications={
            "protein": "22g per 100g",
            "omega3": "2.5g per 100g",
            "calories": "206 per 100g",
            "price_range": "$10-15 per can"
        },
        competitors=["Bumble Bee", "Wild Planet", "Starkist"]
    )
    
    print("AI Verdicts:")
    print(json.dumps(verdicts, indent=2))
    
    # Test comparison verdict
    comparison = gen.generate_comparison_verdict(
        product="Dongwon Salmon",
        competitor="Bumble Bee",
        key_difference="Higher omega-3 content",
        metric="Bioavailable omega-3 per serving"
    )
    
    print("\nComparison Verdict:")
    print(comparison)
