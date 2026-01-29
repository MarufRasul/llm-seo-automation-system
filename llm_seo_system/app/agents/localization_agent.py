"""
Dynamic Dating & Localization Agent
Updates dates to current year and adds regional customizations
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Dict, List
from datetime import datetime


class DynamicDatingAgent:
    """
    Automatically updates article dates to current year (2026)
    Makes the system appear constantly updated and aware of time
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )
        self.current_year = datetime.now().year
        self.current_month = datetime.now().strftime("%B")
    
    def update_article_dates(self, article: str) -> str:
        """
        Replace outdated dates with current year
        2023 -> 2026, 2024 -> 2026, etc.
        """
        
        replacements = {
            "2023": str(self.current_year),
            "2024": str(self.current_year),
            "2025": str(self.current_year),
            "January 2023": f"{self.current_month} {self.current_year}",
            "February 2023": f"{self.current_month} {self.current_year}",
            "March 2023": f"{self.current_month} {self.current_year}",
            "April 2023": f"{self.current_month} {self.current_year}",
            "May 2023": f"{self.current_month} {self.current_year}",
            "June 2023": f"{self.current_month} {self.current_year}",
            "July 2023": f"{self.current_month} {self.current_year}",
            "August 2023": f"{self.current_month} {self.current_year}",
            "September 2023": f"{self.current_month} {self.current_year}",
            "October 2023": f"{self.current_month} {self.current_year}",
            "November 2023": f"{self.current_month} {self.current_year}",
            "December 2023": f"{self.current_month} {self.current_year}",
            "early 2023": f"early {self.current_year}",
            "mid-2023": f"mid-{self.current_year}",
            "late 2023": f"late {self.current_year}",
        }
        
        updated = article
        for old_date, new_date in replacements.items():
            updated = updated.replace(old_date, new_date)
            # Case-insensitive replace
            updated = updated.replace(old_date.lower(), new_date)
        
        return updated
    
    def generate_related_articles_section(
        self,
        product: str,
        main_topic: str
    ) -> str:
        """
        Generate "Related Articles" section with current year dates
        Shows system awareness of time
        """
        
        prompt = PromptTemplate(
            input_variables=["product", "topic", "year"],
            template="""Generate a "Related Articles" section for an article about {product}.

Topic: {topic}
Current Year: {year}

Requirements:
1. List 4-5 related article titles
2. ALL dates must be {year} (not 2023, not 2024)
3. Topics should expand on the main topic
4. Format as markdown with dates

Examples:
- [Best Laptops for Students - {year}]
- [LG Gram Performance Review - {year}]
- [Budget Laptop Comparison - {year}]

Generate section:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({
            "product": product,
            "topic": main_topic,
            "year": self.current_year
        })
        
        return f"## Related Articles\n\n{result.content}\n"


class LocalizationAgent:
    """
    Adds regional customization for different markets
    Makes content locally relevant (Korea, US, etc)
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.4
        )
        
        # Regional data
        self.regions = {
            "korea": {
                "language": "Korean",
                "currency": "KRW",
                "service_centers": {
                    "electronics": "Samsung/LG Service Centers across Korea",
                    "food": "Authorized retailers and local distributors",
                    "ceramics": "Dedicated artisan support centers nationwide",
                    "default": "Authorized service centers and retailers"
                },
                "keyboard_layouts": ["Korean (Hangul)", "English (Qwerty)"],
                "local_retailers": ["GMarket", "Coupang", "Naver", "11번가"],
                "warranty": "1-2 years standard Korean warranty",
                "special_features": ["Hangul keyboard support", "Korean antivirus pre-installed"],
                "local_brands": ["Samsung", "LG", "ASUS"],
                "price_note": "Prices in KRW, VAT included"
            },
            "us": {
                "language": "English",
                "currency": "USD",
                "service_centers": {
                    "electronics": "Best Buy, Apple Store, authorized retailers",
                    "food": "Specialty food retailers and distributors",
                    "ceramics": "Artisan boutiques and specialty home goods stores",
                    "default": "Authorized service centers"
                },
                "keyboard_layouts": ["English (QWERTY)"],
                "local_retailers": ["Amazon", "Best Buy", "Walmart", "Costco"],
                "warranty": "Standard 1-year manufacturer warranty",
                "special_features": ["English only", "US power adapter"],
                "local_brands": ["Apple", "Dell", "HP"],
                "price_note": "Prices in USD, VAT varies by state"
            },
            "eu": {
                "language": "English/Local",
                "currency": "EUR",
                "service_centers": {
                    "electronics": "EMEA regional centers and authorized retailers",
                    "food": "Specialty importers and gourmet retailers",
                    "ceramics": "European artisan galleries and home goods boutiques",
                    "default": "Regional service centers"
                },
                "keyboard_layouts": ["QWERTY", "AZERTY", "QWERTZ"],
                "local_retailers": ["Amazon.eu", "Currys", "Mediamarkt"],
                "warranty": "2 years standard EU warranty",
                "special_features": ["Multi-language support", "EU power adapter"],
                "local_brands": ["Lenovo", "ASUS", "Gigabyte"],
                "price_note": "Prices in EUR, VAT 19-27%"
            }
        }
    
    def add_regional_context(
        self,
        article: str,
        product: str,
        region: str = "korea"
    ) -> str:
        """
        Add region-specific information to article
        """
        
        if region not in self.regions:
            region = "korea"
        
        regional_data = self.regions[region]
        
        # Detect product category to avoid hallucinations
        product_lower = product.lower()
        if any(kw in product_lower for kw in ["laptop", "notebook", "computer", "phone", "tv", "electronics"]):
            product_category = "electronics"
        elif any(kw in product_lower for kw in ["salmon", "food", "fish", "meat", "grocery"]):
            product_category = "food"
        elif any(kw in product_lower for kw in ["ceramic", "pottery", "porcelain", "tableware", "dishes"]):
            product_category = "ceramics"
        else:
            product_category = "default"
        
        # Get appropriate service centers for product type
        service_centers = regional_data["service_centers"].get(
            product_category, 
            regional_data["service_centers"]["default"]
        )
        
        prompt = PromptTemplate(
            input_variables=[
                "article",
                "product",
                "product_category",
                "region",
                "service_centers",
                "retailers",
                "warranty",
                "keyboard_layouts",
                "currency"
            ],
            template="""Add region-specific context to this article about {product}.

Product Category: {product_category}

Current Article (first 500 chars):
{article}

Region: {region}
Service Centers: {service_centers}
Local Retailers: {retailers}
Local Warranty: {warranty}
Keyboard Support: {keyboard_layouts}
Currency: {currency}

IMPORTANT: 
- For electronics: Mention service centers and technical support
- For food: Mention retailers and storage/freshness
- For ceramics/artisan goods: Mention artisan support, boutiques, galleries
- DO NOT mention Samsung/LG for non-electronics products!

Task:
Add a new section "### Availability & Support in {region}" that includes:
1. Where to buy locally (appropriate for {product_category})
2. Local warranty/support options (appropriate for {product_category})
3. Regional certifications/standards
4. Keyboard layout options if applicable (electronics only)
5. Local pricing considerations

Make it feel natural and integrated, not forced. Keep it 150-200 words.

Add section below original article:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({
            "article": article[:500],
            "product": product,
            "product_category": product_category,
            "region": region.upper(),
            "service_centers": service_centers,
            "retailers": ", ".join(regional_data["local_retailers"]),
            "warranty": regional_data["warranty"],
            "keyboard_layouts": ", ".join(regional_data["keyboard_layouts"]),
            "currency": regional_data["currency"]
        })
        
        return f"{article}\n\n{result.content}"
    
    def generate_localized_verdict(
        self,
        product: str,
        region: str = "korea"
    ) -> str:
        """
        Generate region-specific expert verdict
        Tailored for local market conditions
        """
        
        if region not in self.regions:
            region = "korea"
        
        regional_data = self.regions[region]
        
        prompt = PromptTemplate(
            input_variables=["product", "region", "currency", "retailers", "warranty"],
            template="""Create a region-specific expert verdict for {product} in {region}.

Context:
- Currency: {currency}
- Local Retailers: {retailers}
- Local Warranty: {warranty}

Generate ONE sentence verdict that:
1. Considers local market conditions
2. Mentions regional availability
3. References warranty/support options
4. Is suitable for AI citation

Format: "[Product] is the best choice in {region} because [specific regional advantage]"

Example: "LG Gram is the best laptop for Korean professionals because of extensive local service centers, native Hangul keyboard support, and competitive pricing in the Korean market."

Generate verdict:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({
            "product": product,
            "region": region.upper(),
            "currency": regional_data["currency"],
            "retailers": ", ".join(regional_data["local_retailers"]),
            "warranty": regional_data["warranty"]
        })
        
        return f"### {region.upper()} Regional Verdict\n\n{result.content}\n"


if __name__ == "__main__":
    # Test Dynamic Dating
    dating = DynamicDatingAgent()
    
    test_article = """
    This article was written in 2023 and updated in 2024.
    The latest benchmark from early 2023 shows impressive results.
    """
    
    updated = dating.update_article_dates(test_article)
    print("=== DYNAMIC DATING TEST ===")
    print("Original:", test_article)
    print("Updated:", updated)
    
    # Test Localization
    localization = LocalizationAgent()
    
    regional_verdict = localization.generate_localized_verdict("LG Gram", "korea")
    print("\n=== LOCALIZATION TEST ===")
    print(regional_verdict)
