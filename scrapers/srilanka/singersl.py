import requests
from bs4 import BeautifulSoup
import re
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# --- Brand Helpers ---

KNOWN_BRANDS = [
    'HP', 'Lenovo', 'Asus', 'Acer', 'Dell', 'MSI', 'Apple', 
    'Samsung', 'LG', 'JVC', 'Haier', 'Toshiba', 'Electrolux', 
    'Whirlpool', 'Oppo', 'Xiaomi', 'JBL', 'Titan', 'Miniso',
    'Singer', 'Sony', 'Panasonic', 'Hitachi', 'Beko', 'Huawei',
    'TCL', 'Sharp', 'Kenwood', 'Sisil', 'Unic'
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
    return http

# --- Main Scraper Function ---

def scrape_singer_sl(config):
    """
    Scrapes product data from SingerSL.com /filter page.
    """
    all_products_data = []
    session = setup_session()
    base_url = config['base_url']
    page = 1
    
    # Headers to mimic a real browser
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"\n[Singer SL] Starting scrape for {config['country']}...")
    
    while True:
        # Construct URL: Singer uses ?page=1 parameter
        current_url = f"{base_url}?page={page}"
        print(f"-> Fetching page {page}...")
        
        try:
            response = session.get(current_url, headers=HEADERS)
            response.raise_for_status() 
            soup = BeautifulSoup(response.content, 'html.parser')

            # 1. Product Container
            # Matches: <div class="p-2 ... product ...">
            product_cards = soup.find_all('div', class_='product')

            if not product_cards:
                print("  No products found on this page. Stopping scrape.")
                break

            items_found_on_page = 0

            for card in product_cards:
                # 2. Extract Name
                # Matches: <h5 class="card-title product__name mb-1">
                name_elem = card.find('h5', class_='product__name')
                name = name_elem.text.strip() if name_elem else "N/A"
                
                # 3. Extract Price
                # Matches: <div class="product__price ..."> <span class="price"> Rs 29,969 </span>
                price_elem = card.find('span', class_='price')
                
                price = None 
                if price_elem:
                    raw_price_text = price_elem.get_text(strip=True)
                    try:
                        # Clean: Remove 'Rs', commas, spaces, and take integer part
                        cleaned_price = re.sub(r'[^\d]', '', raw_price_text.split('.')[0])
                        price = int(cleaned_price)
                    except ValueError:
                        pass 
                
                # 4. Determine Brand
                final_brand_name = extract_brand_from_name(name)

                # 5. Filter based on Price Range
                is_in_price_range = price is not None and config['min_price'] <= price <= config['max_price']

                if is_in_price_range:
                    all_products_data.append({
                        'Category': 'General', 
                        'Brand': final_brand_name,
                        'Model': name,
                        'Price (LKR)': price,
                        'Country': config['country'],
                        'Year (Target)': config['year']
                    })
                    items_found_on_page += 1

            # Check for Next Page
            # The HTML might use a generic class for pagination
            # We check if we found items. If items were found, we assume there might be a next page.
            # (Since Singer's pagination structure varies, we'll rely on item count + explicit next link if available)
            
            # Try finding the explicit next button (common in pagination)
            # Look for any link with 'page=' + next_page_number
            next_page_param = f"page={page+1}"
            next_link = soup.find('a', href=re.compile(next_page_param))
            
            # Fallback: If 16+ items found (full page), try next page anyway (Singer listing is large)
            if next_link or items_found_on_page >= 12:
                page += 1
                time.sleep(random.uniform(1, 3))
            else:
                print("  Reached the last page (No next link or partial page).")
                break

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print("  Page not found (404). Stopping.")
                break
            print(f"  Error fetching page {page}: {e}.")
            break 
        except Exception as e:
            print(f"  An unexpected error occurred on page {page}: {e}.")
            break 
            
    print(f"\n[Singer SL] Scraping finished. Found {len(all_products_data)} products.")
    return all_products_data