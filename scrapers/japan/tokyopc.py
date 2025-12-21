import requests
from bs4 import BeautifulSoup
import re
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# --- Brand and Session Helpers ---

KNOWN_BRANDS = [
    'Apple', 'Samsung', 'Sony', 'Microsoft', 'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'MSI',
    'Huawei', 'Oppo', 'Xiaomi', 'Google', 'Motorola', 'Sharp', 'Toshiba', 'Fujitsu', 'Panasonic'
]

def extract_brand_from_name(product_name):
    """Tries to find a known brand name in the product title."""
    name_lower = product_name.lower()
    for brand in KNOWN_BRANDS:
        if brand.lower() in name_lower:
            return brand
    return 'Other'

def setup_session():
    """Configures a session with retry logic."""
    retry_strategy = Retry(
        total=3, 
        backoff_factor=1, 
        status_forcelist=[500, 502, 503, 504, 524], 
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return http

def get_categories(session, base_url):
    """Fetches the home page to extract category URLs."""
    print(f"Fetching categories from {base_url}...")
    try:
        response = session.get(base_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        categories = []
        
        cat_links = soup.select('a.ty-menu__submenu-link')
        
        for link in cat_links:
            href = link.get('href')
            
            name_span = link.select_one('span.v-center')
            if name_span:
                
                text_parts = [t for t in name_span.contents if isinstance(t, str)]
                name = "".join(text_parts).strip()
                if not name: 
                     name = name_span.get_text(strip=True)
            else:
                name = link.get_text(strip=True)
                
            if href and href.startswith('http'):
                
                if not any(c['url'] == href for c in categories):
                    categories.append({'name': name, 'url': href})
                
        print(f"Found {len(categories)} categories.")
        return categories
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

def scrape_tokyopc(config):
    """
    Scrapes product data from TokyoPC.jp by iterating through categories.
    """
    all_products_data = []
    session = setup_session()
    base_url = config['base_url']

    categories = get_categories(session, base_url)
    
    if not categories:
        print("No categories found. Exiting.")
        return []

    for category in categories:
        cat_name = category['name']
        cat_url = category['url']
        print(f"\n--- Scraping Category: {cat_name} ---")
        
        page = 1
        while True:
            
            if '?' in cat_url:
                page_url = f"{cat_url}&page={page}"
            else:
                page_url = f"{cat_url}?page={page}"
                
            print(f"  Fetching page {page}: {page_url}")
            
            try:
                response = session.get(page_url, timeout=20)
                if response.status_code == 404:
                    print("  Page not found. Stopping category.")
                    break
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                products = soup.select('div.ut2-gl__content')
                
                if not products:
                    print("  No products found on this page. Stopping category.")
                    break
                
                print(f"  Found {len(products)} products.")
                
                for product in products:
                    try:
                        
                        title_tag = product.select_one('a.product-title')
                        if not title_tag:
                            continue
                        title = title_tag.get_text(strip=True)
                        product_url = title_tag.get('href')
                        
                        price_tag = product.select_one('span.ty-price')
                        
                        price_text = "0"
                        if price_tag:
                            price_text = price_tag.get_text(strip=True)
                        
                        price_clean = re.sub(r'[^\d]', '', price_text)
                        price = float(price_clean) if price_clean else 0.0
                        
                        brand = extract_brand_from_name(title)
                        
                        all_products_data.append({
                            'Brand': brand,
                            'Model': title,
                            'Price (JPY)': price,
                            'Category': cat_name,
                            'Store': 'TokyoPC',
                            'URL': product_url
                        })
                        
                    except Exception as e:
                        print(f"  Error parsing product: {e}")
                        continue
                
                pagination = soup.select_one('div.ty-pagination')
                if pagination:
                    
                    next_link = pagination.select_one('a[class*="next"]')
                    if not next_link:
                        
                        print("  No next page link found. Stopping category.")
                        break
                else:
                    
                    if page > 50: 
                        break
                
                page += 1
                time.sleep(1)
                
            except Exception as e:
                print(f"  Error scraping page {page}: {e}")
                break
                
    return all_products_data
