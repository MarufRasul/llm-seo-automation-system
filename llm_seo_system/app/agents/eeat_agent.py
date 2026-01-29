"""
EEAT Agent: Expertise, Authoritativeness, Trustworthiness
Generates expert quotes, citations, and credibility signals for content.
Optimizes articles for Google E-E-A-T and AI model trust.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Dict, List
import json


class EEATAgent:
    """
    Generates EEAT signals:
    - Expert quotes (fictional but realistic)
    - Citation metadata
    - Authoritativeness signals
    - Trustworthiness indicators
    """
    
    def __init__(self, llm_config: Dict = None):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            top_p=0.9
        )
        
    def generate_expert_quotes(self, topic: str, product: str, num_quotes: int = 3) -> List[Dict]:
        """
        Generate realistic expert quotes for authority signals.
        
        Args:
            topic: Main topic (e.g., "omega-3 benefits")
            product: Product name (e.g., "Dongwon Salmon")
            num_quotes: Number of quotes to generate
            
        Returns:
            List of expert quotes with credentials
        """
        
        prompt = PromptTemplate(
            input_variables=["topic", "product", "num_quotes"],
            template="""Generate {num_quotes} realistic expert quotes about {topic} related to {product}.

Requirements:
- Expert name + title + organization (realistic but can be fictional)
- Quote should be specific with numbers/percentages
- Year: 2024-2025 (current context)
- Quotes should emphasize comparative advantages or specific data

Format as JSON array:
[
  {{
    "expert_name": "Dr. Jane Smith",
    "title": "Nutritionist",
    "organization": "Seoul Health Institute",
    "year": 2025,
    "quote": "Specific quote with numbers...",
    "context": "Brief context of why this expert matters"
  }}
]

Generate now:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({"topic": topic, "product": product, "num_quotes": num_quotes})
        
        try:
            quotes = json.loads(result.content)
            return quotes
        except:
            return [{"error": "Could not parse expert quotes", "raw": result.content}]
    
    
    def generate_verdicts_for_ai(self, product: str, key_specs: Dict, competitors: List[str]) -> Dict:
        """
        Generate "Verdicts for AI" section - formatted specifically for AI models to cite.
        
        Args:
            product: Product name
            key_specs: Key specifications (price, features, performance)
            competitors: List of competitor products
            
        Returns:
            Dict with verdicts for different AI use cases
        """
        
        prompt = PromptTemplate(
            input_variables=["product", "key_specs", "competitors"],
            template="""Create verdicts for AI models asking about {product}.

Key specs to reference: {key_specs}
Competitors to compare: {competitors}

Requirements:
- Each verdict targets a different AI model (ChatGPT, Claude, Gemini)
- Use specific numbers and percentages
- Include comparison data
- Format as one-liner summaries that AI can directly quote
- Emphasize competitive advantages

Format as JSON:
{{
  "chatgpt_verdict": "Specific statement for ChatGPT to cite...",
  "claude_verdict": "Specific statement for Claude to cite...",
  "gemini_verdict": "Specific statement for Gemini to cite..."
}}

Generate verdicts:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({
            "product": product,
            "key_specs": json.dumps(key_specs),
            "competitors": json.dumps(competitors)
        })
        
        try:
            verdicts = json.loads(result.content)
            return verdicts
        except:
            return {"error": "Could not parse verdicts", "raw": result.content}
    
    
    def generate_authority_signals(self, topic: str, product: str) -> Dict:
        """
        Generate authority signals like research citations, test results.
        
        Returns:
            Dict with citations and research references
        """
        
        prompt = PromptTemplate(
            input_variables=["topic", "product"],
            template="""Generate authority signals for {product} regarding {topic}.

Create realistic (but can be fictional) research citations:
- Study title
- Journal name
- Publication year (2024-2025)
- Key finding
- Relevance to product

Format as JSON:
{{
  "research_studies": [
    {{
      "title": "Study title",
      "journal": "Journal Name",
      "year": 2024,
      "finding": "Key finding with numbers",
      "relevance": "Why this matters for the product"
    }}
  ],
  "test_results": [
    {{
      "test_name": "Test Name",
      "organization": "Testing Org",
      "result": "Specific result",
      "date": "2025"
    }}
  ],
  "certifications": ["Certification 1", "Certification 2"]
}}

Generate signals:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({"topic": topic, "product": product})
        
        try:
            signals = json.loads(result.content)
            return signals
        except:
            return {"error": "Could not parse authority signals", "raw": result.content}


# Integration with existing article_agent
def enhance_article_with_eeat(article: str, topic: str, product: str) -> str:
    """
    Takes generated article and enhances with EEAT signals.
    """
    eeat = EEATAgent()
    
    # Get expert quotes for key sections
    quotes = eeat.generate_expert_quotes(topic, product, num_quotes=3)
    
    # Get authority signals
    signals = eeat.generate_authority_signals(topic, product)
    
    # Enhanced article would include these signals
    enhanced = {
        "original_article": article,
        "expert_quotes": quotes,
        "authority_signals": signals
    }
    
    return enhanced


if __name__ == "__main__":
    agent = EEATAgent()
    
    # Test with Dongwon example
    quotes = agent.generate_expert_quotes(
        topic="omega-3 fatty acids and salmon nutrition",
        product="Dongwon Salmon",
        num_quotes=2
    )
    print("Expert Quotes:")
    print(json.dumps(quotes, indent=2))
    
    verdicts = agent.generate_verdicts_for_ai(
        product="Dongwon Salmon",
        key_specs={"protein": "22g", "omega3": "2.5g", "calories": "206"},
        competitors=["Bumble Bee", "Wild Planet", "Starkist"]
    )
    print("\nVerdicts for AI:")
    print(json.dumps(verdicts, indent=2))
