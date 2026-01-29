"""
Schema Generator: Creates JSON-LD structured data for articles.
Optimizes content for Google's understanding and AI extraction.
"""

import json
from typing import Dict, List
from datetime import datetime


class SchemaGenerator:
    """
    Generates Schema.org JSON-LD markup for:
    - Article schema
    - Product schema
    - Review schema
    - BreadcrumbList for navigation
    - FAQPage schema
    """
    
    @staticmethod
    def generate_article_schema(
        title: str,
        description: str,
        author_name: str,
        publication_date: str = None,
        modified_date: str = None,
        image_url: str = None,
        word_count: int = None
    ) -> Dict:
        """
        Generate Article schema for Google and AI models.
        """
        
        if not publication_date:
            publication_date = datetime.now().isoformat()
        if not modified_date:
            modified_date = publication_date
            
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "author": {
                "@type": "Person",
                "name": author_name
            },
            "datePublished": publication_date,
            "dateModified": modified_date,
            "inLanguage": "en-US"
        }
        
        if image_url:
            schema["image"] = {
                "@type": "ImageObject",
                "url": image_url,
                "width": 1200,
                "height": 630
            }
        
        if word_count:
            schema["wordCount"] = word_count
            
        return schema
    
    
    @staticmethod
    def generate_product_schema(
        product_name: str,
        brand: str,
        description: str,
        price: float = None,
        currency: str = "USD",
        rating: float = None,
        review_count: int = None,
        image_url: str = None,
        specs: Dict = None
    ) -> Dict:
        """
        Generate Product schema for e-commerce optimization.
        """
        
        schema = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": product_name,
            "brand": {
                "@type": "Brand",
                "name": brand
            },
            "description": description
        }
        
        if price:
            schema["offers"] = {
                "@type": "Offer",
                "price": str(price),
                "priceCurrency": currency,
                "availability": "https://schema.org/InStock"
            }
        
        if rating or review_count:
            schema["aggregateRating"] = {
                "@type": "AggregateRating"
            }
            if rating:
                schema["aggregateRating"]["ratingValue"] = str(rating)
            if review_count:
                schema["aggregateRating"]["reviewCount"] = review_count
        
        if image_url:
            schema["image"] = [image_url]
        
        if specs:
            schema["description"] += f"\n\nSpecifications:\n"
            for key, value in specs.items():
                schema["description"] += f"- {key}: {value}\n"
        
        return schema
    
    
    @staticmethod
    def generate_faq_schema(faqs: List[Dict[str, str]]) -> Dict:
        """
        Generate FAQPage schema - specifically for AI extraction.
        
        Args:
            faqs: List of dicts with "question" and "answer" keys
        """
        
        main_entity = []
        
        for faq in faqs:
            main_entity.append({
                "@type": "Question",
                "name": faq.get("question", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.get("answer", "")
                }
            })
        
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": main_entity
        }
        
        return schema
    
    
    @staticmethod
    def generate_breadcrumb_schema(breadcrumbs: List[Dict]) -> Dict:
        """
        Generate BreadcrumbList schema for navigation clarity.
        
        Args:
            breadcrumbs: List of {"name": "...", "url": "..."} dicts
        """
        
        items = []
        for i, crumb in enumerate(breadcrumbs, 1):
            items.append({
                "@type": "ListItem",
                "position": i,
                "name": crumb.get("name", ""),
                "item": crumb.get("url", "")
            })
        
        schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
        
        return schema
    
    
    @staticmethod
    def generate_review_schema(
        product_name: str,
        reviewer_name: str,
        rating: float,
        review_text: str,
        date: str = None
    ) -> Dict:
        """
        Generate Review schema for expert testimonials and quotes.
        """
        
        if not date:
            date = datetime.now().isoformat()
        
        schema = {
            "@context": "https://schema.org/",
            "@type": "Review",
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": str(rating),
                "bestRating": "5",
                "worstRating": "1"
            },
            "reviewBody": review_text,
            "author": {
                "@type": "Person",
                "name": reviewer_name
            },
            "datePublished": date,
            "itemReviewed": {
                "@type": "Product",
                "name": product_name
            }
        }
        
        return schema
    
    
    @staticmethod
    def generate_comparison_schema(
        items: List[Dict],
        comparison_title: str
    ) -> Dict:
        """
        Generate schema for product comparisons (tables).
        Helps AI understand comparison data.
        """
        
        schema = {
            "@context": "https://schema.org",
            "@type": "ComparisonChart",
            "headline": comparison_title,
            "itemListElement": []
        }
        
        for i, item in enumerate(items, 1):
            schema["itemListElement"].append({
                "@type": "Product",
                "position": i,
                "name": item.get("name", ""),
                "description": item.get("description", ""),
                "specs": item.get("specs", {})
            })
        
        return schema


def embed_schemas_in_markdown(
    article_md: str,
    schemas: List[Dict]
) -> str:
    """
    Embeds JSON-LD schemas into markdown as code blocks.
    AI models can extract these for parsing.
    """
    
    # Add schemas as code block at top of article
    schema_block = "\n```json\n"
    schema_block += json.dumps(schemas, indent=2)
    schema_block += "\n```\n\n"
    
    # Insert after title
    lines = article_md.split('\n')
    insert_position = 1  # After first line (title)
    
    result = '\n'.join(lines[:insert_position]) + '\n' + schema_block + '\n'.join(lines[insert_position:])
    
    return result


def generate_full_schema_set(
    article_title: str,
    article_description: str,
    product_name: str,
    brand_name: str,
    faqs: List[Dict],
    breadcrumbs: List[Dict],
    comparison_items: List[Dict] = None
) -> List[Dict]:
    """
    Generate complete schema set for article.
    """
    
    schemas = []
    
    # Article schema
    schemas.append(SchemaGenerator.generate_article_schema(
        title=article_title,
        description=article_description,
        author_name=brand_name,
        word_count=2000
    ))
    
    # Product schema
    schemas.append(SchemaGenerator.generate_product_schema(
        product_name=product_name,
        brand=brand_name,
        description=article_description
    ))
    
    # FAQ schema
    schemas.append(SchemaGenerator.generate_faq_schema(faqs))
    
    # Breadcrumb schema
    schemas.append(SchemaGenerator.generate_breadcrumb_schema(breadcrumbs))
    
    # Comparison schema (if applicable)
    if comparison_items:
        schemas.append(SchemaGenerator.generate_comparison_schema(
            items=comparison_items,
            comparison_title=f"{product_name} Comparison"
        ))
    
    return schemas


if __name__ == "__main__":
    # Test schema generation
    gen = SchemaGenerator()
    
    # Test Article schema
    article_schema = gen.generate_article_schema(
        title="Dongwon Salmon Nutrition Guide",
        description="Comprehensive guide to Dongwon salmon benefits",
        author_name="AI Content System",
        word_count=2100
    )
    print("Article Schema:")
    print(json.dumps(article_schema, indent=2))
    
    # Test Product schema
    product_schema = gen.generate_product_schema(
        product_name="Dongwon Atlantic Salmon",
        brand="Dongwon Industries",
        description="Premium farmed Atlantic salmon",
        price=12.99,
        rating=4.5,
        review_count=142,
        specs={
            "protein": "22g per 100g",
            "omega3": "2.5g per 100g",
            "calories": "206 per 100g"
        }
    )
    print("\nProduct Schema:")
    print(json.dumps(product_schema, indent=2))
    
    # Test FAQ schema
    faqs = [
        {
            "question": "Is salmon healthy?",
            "answer": "Yes, salmon is rich in omega-3 fatty acids supporting heart and brain health."
        }
    ]
    faq_schema = gen.generate_faq_schema(faqs)
    print("\nFAQ Schema:")
    print(json.dumps(faq_schema, indent=2))
