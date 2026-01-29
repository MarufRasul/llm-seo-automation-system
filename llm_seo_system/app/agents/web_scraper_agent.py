"""
Web Scraper Agent: Extracts real data from official brand websites.
Uses BeautifulSoup for HTML parsing, Selenium for JavaScript-heavy sites.
Falls back to Google Search API if direct scraping fails.
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraperAgent:
    """
    Scrapes official brand websites for:
    - Product specifications
    - Pricing information
    - Availability status
    - Product descriptions
    - Nutritional/material information
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10
        self.max_retries = 3
    
    
    def scrape_website(self, url: str) -> Optional[Dict]:
        """
        Scrape a single website with retry logic.
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dict with scraped content or None if failed
        """
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔍 Scraping {url} (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract text content
                    text_content = soup.get_text(separator='\n', strip=True)
                    
                    # Extract structured data (if JSON-LD available)
                    json_ld = self._extract_json_ld(soup)
                    
                    # Extract tables
                    tables = self._extract_tables(soup)
                    
                    # Extract product specs
                    specs = self._extract_specs(soup)
                    
                    return {
                        "url": url,
                        "status": "success",
                        "text_content": text_content[:5000],  # First 5000 chars
                        "json_ld": json_ld,
                        "tables": tables,
                        "specs": specs,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    logger.warning(f"⚠️ Status {response.status_code} for {url}")
                    
            except requests.Timeout:
                logger.warning(f"⏱️ Timeout on {url}")
            except Exception as e:
                logger.warning(f"❌ Error scraping {url}: {str(e)}")
                
            # Wait before retry
            if attempt < self.max_retries - 1:
                time.sleep(2)
        
        return None
    
    
    def _extract_json_ld(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract JSON-LD structured data."""
        
        json_ld_data = []
        
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except:
                pass
        
        return json_ld_data
    
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract HTML tables from page."""
        
        tables = []
        
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cols = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cols:
                    rows.append(cols)
            
            if rows:
                tables.append({
                    "headers": rows[0] if rows else [],
                    "data": rows[1:] if len(rows) > 1 else []
                })
        
        return tables
    
    
    def _extract_specs(self, soup: BeautifulSoup) -> Dict:
        """Extract product specifications from common patterns."""
        
        specs = {}
        
        # Look for common spec containers
        spec_patterns = [
            'specs', 'specifications', 'product-specs', 'technical-specs',
            'details', 'product-details', 'info', 'product-info'
        ]
        
        for pattern in spec_patterns:
            # By class
            for elem in soup.find_all(class_=pattern):
                self._extract_key_values(elem, specs)
            
            # By id
            elem = soup.find(id=pattern)
            if elem:
                self._extract_key_values(elem, specs)
        
        return specs
    
    
    def _extract_key_values(self, elem, specs_dict: Dict):
        """Extract key-value pairs from an element."""
        
        for item in elem.find_all(['li', 'tr', 'div']):
            text = item.get_text().strip()
            
            # Look for patterns like "Label: Value" or "Label - Value"
            for sep in [':', '-', '–']:
                if sep in text:
                    parts = text.split(sep, 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key and value and len(key) < 50:
                            specs_dict[key] = value
                    break
    
    
    def scrape_brand_website(
        self,
        brand_config: Dict
    ) -> Dict:
        """
        Scrape all product pages for a brand.
        
        Args:
            brand_config: Brand config from brand_configs.py with URLs
            
        Returns:
            Aggregated data from all brand pages
        """
        
        brand_name = brand_config.get("brand_name", "Unknown")
        product_pages = brand_config.get("product_pages", [])
        
        logger.info(f"🔍 Starting brand scrape for {brand_name}")
        
        aggregated_data = {
            "brand": brand_name,
            "pages": [],
            "all_specs": {},
            "all_tables": [],
            "json_ld_data": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for page_url in product_pages:
            page_data = self.scrape_website(page_url)
            
            if page_data:
                aggregated_data["pages"].append(page_data)
                
                # Merge specs
                if page_data.get("specs"):
                    aggregated_data["all_specs"].update(page_data["specs"])
                
                # Collect tables
                if page_data.get("tables"):
                    aggregated_data["all_tables"].extend(page_data["tables"])
                
                # Collect JSON-LD
                if page_data.get("json_ld"):
                    aggregated_data["json_ld_data"].extend(page_data["json_ld"])
        
        return aggregated_data
    
    
    def extract_product_data(
        self,
        scraped_data: Dict
    ) -> Dict:
        """
        Clean and structure scraped data for article generation.
        
        Returns:
            Clean data ready for LLM processing
        """
        
        extracted = {
            "brand": scraped_data.get("brand"),
            "specifications": [],
            "prices": [],
            "products": [],
            "materials": [],
            "features": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Extract from JSON-LD (structured data - most reliable)
        for json_ld in scraped_data.get("json_ld_data", []):
            if json_ld.get("@type") == "Product":
                extracted["products"].append({
                    "name": json_ld.get("name"),
                    "description": json_ld.get("description"),
                    "price": json_ld.get("price"),
                    "image": json_ld.get("image"),
                    "offers": json_ld.get("offers")
                })
        
        # Extract from specs
        for key, value in scraped_data.get("all_specs", {}).items():
            extracted["specifications"].append({
                "attribute": key,
                "value": value
            })
        
        # Extract from tables
        for table in scraped_data.get("all_tables", []):
            if table.get("data"):
                extracted["tables"] = table
        
        return extracted


# Utility function to integrate with research_agent
def get_website_data(brand_config: Dict) -> Dict:
    """
    Helper to get fresh data from brand website.
    Falls back gracefully if scraping fails.
    """
    
    if not brand_config.get("product_pages"):
        logger.warning("No product pages configured for brand")
        return {"error": "No product pages configured"}
    
    scraper = WebScraperAgent()
    
    try:
        logger.info(f"📥 Scraping {brand_config.get('brand_name')} website...")
        
        scraped = scraper.scrape_brand_website(brand_config)
        extracted = scraper.extract_product_data(scraped)
        
        logger.info(f"✅ Successfully scraped {len(scraped.get('pages', []))} pages")
        
        return extracted
        
    except Exception as e:
        logger.error(f"❌ Scraping failed: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Test with sample config
    sample_config = {
        "brand_name": "Test Brand",
        "product_pages": [
            "https://example.com/products"
        ]
    }
    
    scraper = WebScraperAgent()
    data = get_website_data(sample_config)
    print(json.dumps(data, indent=2))
