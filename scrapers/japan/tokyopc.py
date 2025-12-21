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
        # Select category links from the menu
        # Based on tokyopc.html: a.ty-menu__submenu-link
        cat_links = soup.select('a.ty-menu__submenu-link')
        
        for link in cat_links:
            href = link.get('href')
            # Get text from span.v-center or direct text
            name_span = link.select_one('span.v-center')
            if name_span:
                # Remove labels like "Hit", "Popular" if present (clone to avoid modifying soup in place if needed, but here it's fine)
                # We use get_text but exclude children with class m-label?
                # Easier to just decompose them in a copy or just ignore.
                # Let's just take the text and clean it up if it ends with Hit/Popular/New
                # Or better:
                text_parts = [t for t in name_span.contents if isinstance(t, str)]
                name = "".join(text_parts).strip()
                if not name: # Fallback if text is inside a tag we missed
                     name = name_span.get_text(strip=True)
            else:
                name = link.get_text(strip=True)
                
            if href and href.startswith('http'):
                # Avoid duplicate categories if possible, or just add all
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
    
    # 1. Get Categories
    categories = get_categories(session, base_url)
    
    if not categories:
        print("No categories found. Exiting.")
        return []

    # 2. Iterate Categories
    for category in categories:
        cat_name = category['name']
        cat_url = category['url']
        print(f"\n--- Scraping Category: {cat_name} ---")
        
        page = 1
        while True:
            # Construct URL for pagination
            # CS-Cart often uses page-N suffix or ?page=N
            # We'll try ?page=N as it's safer if we don't know the rewrite rules
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
                
                # Find product grid
                # Based on tokyopc.html: div.ut2-gl__content
                products = soup.select('div.ut2-gl__content')
                
                if not products:
                    print("  No products found on this page. Stopping category.")
                    break
                
                print(f"  Found {len(products)} products.")
                
                for product in products:
                    try:
                        # Title
                        title_tag = product.select_one('a.product-title')
                        if not title_tag:
                            continue
                        title = title_tag.get_text(strip=True)
                        product_url = title_tag.get('href')
                        
                        # Price
                        # Look for discounted price first, then regular price
                        # Structure: span.ty-price contains <bdi><span class="ty-price-num">¥</span><span class="ty-price-num">81,500</span></bdi>
                        # We select the parent .ty-price to get the full text "¥81,500"
                        price_tag = product.select_one('span.ty-price')
                        
                        price_text = "0"
                        if price_tag:
                            price_text = price_tag.get_text(strip=True)
                        
                        # Clean price (remove currency symbol, commas)
                        price_clean = re.sub(r'[^\d]', '', price_text)
                        price = float(price_clean) if price_clean else 0.0
                        
                        brand = extract_brand_from_name(title)
                        
                        all_products_data.append({
                            'Brand': brand,
                            'Model': title,
                            'Price (JPY)': price, # Assuming JPY based on site
                            'Category': cat_name,
                            'Store': 'TokyoPC',
                            'URL': product_url
                        })
                        
                    except Exception as e:
                        print(f"  Error parsing product: {e}")
                        continue
                
                # Check for next page
                # If we found products, we try the next page. 
                # Ideally we check for a "Next" button, but if we can't find it, 
                # we rely on the "No products found" check above.
                # However, to be safe, let's look for pagination controls.
                pagination = soup.select_one('div.ty-pagination')
                if pagination:
                    # Check if there is a "next" link
                    next_link = pagination.select_one('a[class*="next"]')
                    if not next_link:
                        # If pagination exists but no next link, we are at the end
                        print("  No next page link found. Stopping category.")
                        break
                else:
                    # If no pagination controls at all, it might be a single page category
                    # But since we are forcing ?page=N, we might get the same page or empty.
                    # If the site ignores ?page=N and returns the same content, we'll loop forever.
                    # So we should check if the current page content is identical to the previous one?
                    # Or just assume if we found products, we try next.
                    # A safer bet without known pagination is to stop if we suspect it's a single page.
                    # But let's try to detect if "page 2" is actually different.
                    # For now, let's assume if we found products, we continue, but limit to reasonable max pages to prevent infinite loops if it ignores param.
                    if page > 50: 
                        break
                
                page += 1
                time.sleep(1) # Be polite
                
            except Exception as e:
                print(f"  Error scraping page {page}: {e}")
                break
                
    return all_products_data
