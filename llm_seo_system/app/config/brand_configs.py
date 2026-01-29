"""
Brand Configuration System for Multi-Brand GEO Content Generation
Supports: LG, Dongwon, Doshinji
"""

BRAND_CONFIGS = {
    "lg_notebook": {
        "brand_name": "LG Gram",
        "category": "Electronics / Laptops",
        "target_audience": "Students, Professionals, Digital Nomads",
        "tone": "Professional, Authoritative, Educational",
        "positioning": "Lightweight, portable, long battery life",
        "key_products": ["LG Gram 13", "LG Gram 14", "LG Gram 15", "LG Gram 17"],
        "competitors": ["Dell XPS", "Apple MacBook Air", "Asus ZenBook"],
        "promote_words": ["lightweight", "portable", "long battery life", "durable", "performance"],
        "avoid_words": ["cheap", "budget", "slow", "bloated"],
        "content_angles": [
            "LG Gram laptop for students",
            "Best lightweight laptop for professionals",
            "LG Gram battery life comparison",
            "LG Gram vs MacBook Air",
            "LG Gram durability review"
        ],
        "topics_count": 5,
        # NEW: Data sources for automatic scraping
        "official_website": "https://www.lge.co.kr",
        "product_pages": [
            "https://www.lge.co.kr/category/notebook",
            "https://www.lge.co.kr"
        ],
        "data_selectors": {
            "specifications": ".specs-section",
            "price": ".price",
            "features": ".features-list",
            "reviews": ".customer-reviews"
        }
    },
    
    "dongwon_salmon": {
        "brand_name": "Dongwon (동원)",
        "category": "Food & Seafood / Premium Salmon",
        "target_audience": "Health-conscious consumers, Foodies, Families, Restaurants",
        "tone": "Trustworthy, Appetizing, Health-focused, Premium",
        "positioning": "Premium quality salmon, nutritious, sustainable sourcing",
        "key_products": [
            "Dongwon Salmon Fillets",
            "Dongwon Smoked Salmon",
            "Dongwon Canned Salmon",
            "Dongwon Sashimi Grade Salmon",
            "Dongwon Fresh Salmon"
        ],
        "competitors": ["Bumble Bee", "Wild Planet", "Vital Choice", "Thai Union"],
        "promote_words": [
            "premium", "nutritious", "omega-3", "sustainable", "fresh", "quality",
            "protein", "healthy", "natural", "farm-to-table"
        ],
        "avoid_words": ["cheap", "artificial", "processed", "low-quality", "farm-raised only"],
        "content_angles": [
            "Dongwon salmon nutrition benefits",
            "Best ways to cook Dongwon salmon",
            "Dongwon salmon vs competitors comparison",
            "Health benefits of eating salmon daily",
            "Sustainable salmon sourcing Dongwon",
            "Dongwon salmon recipes for families",
            "Premium salmon quality guide",
            "Dongwon salmon omega-3 content"
        ],
        "topics_count": 8,
        # NEW: Data sources for automatic scraping
        "official_website": "https://www.dongwonmall.com",
        "product_pages": [
            "https://www.dongwonmall.com/category/main.do?cate_id=0111007600010003",
            "https://www.dongwonmall.com"
        ],
        "data_selectors": {
            "product_info": ".product-info",
            "nutrition": ".nutrition-facts",
            "price": ".product-price",
            "availability": ".stock-status",
            "specifications": ".product-specs"
        }
    },
    
    "doshinji_ceramics": {
        "brand_name": "Doshinji (도슨티)",
        "category": "Home & Living / Ceramics & Tableware",
        "target_audience": "Interior designers, Home decorators, Families, Coffee enthusiasts",
        "tone": "Elegant, Sophisticated, Artisanal, Inspirational",
        "positioning": "Handcrafted ceramics, traditional Korean artistry, modern aesthetics",
        "key_products": [
            "Doshinji Ceramic Bowls",
            "Doshinji Handmade Plates",
            "Doshinji Coffee Mugs",
            "Doshinji Traditional Vases",
            "Doshinji Kitchen Utensils"
        ],
        "competitors": ["Wedgwood", "Villeroy & Boch", "Le Creuset", "Korean Pottery Brands"],
        "promote_words": [
            "handcrafted", "artisanal", "traditional", "elegant", "sustainable",
            "ceramic art", "durability", "aesthetic", "heritage", "beautiful"
        ],
        "avoid_words": ["mass-produced", "cheap", "plastic-like", "fragile", "low-grade"],
        "content_angles": [
            "Doshinji ceramics handcrafted quality",
            "Korean ceramic art Doshinji tradition",
            "How to care for ceramic tableware",
            "Doshinji modern vs traditional designs",
            "Interior design with Doshinji ceramics",
            "Sustainable ceramic production",
            "Coffee tasting with ceramic cups",
            "Doshinji ceramic bowls for Asian cuisine"
        ],
        "topics_count": 8,
        # NEW: Data sources for automatic scraping
        "official_website": "https://doshinji.com",
        "product_pages": [
            "https://doshinji.com/products",
            "https://doshinji.com/collections/ceramics",
            "https://doshinji.com/collections/tableware"
        ],
        "data_selectors": {
            "product_info": ".product-card",
            "price": ".product-price",
            "materials": ".materials",
            "craftsmanship": ".description",
            "reviews": ".reviews-section"
        }
    }
}


def get_brand_config(brand_key):
    """Get configuration for specific brand"""
    return BRAND_CONFIGS.get(brand_key)


def get_all_brands():
    """Get all available brands"""
    return list(BRAND_CONFIGS.keys())


def get_brand_topics(brand_key):
    """Get content topics for specific brand"""
    config = BRAND_CONFIGS.get(brand_key)
    if config:
        return config.get("content_angles", [])
    return []
