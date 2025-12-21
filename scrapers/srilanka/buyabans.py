import requests
import re
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# --- Brand and Session Helpers ---

# Known/Expected Brands for name-based lookup
KNOWN_BRANDS = [
    'HP', 'Lenovo', 'Asus', 'Acer', 'Dell', 'MSI', 'Apple', 
    'Samsung', 'LG', 'JVC', 'Haier', 'Toshiba', 'Electrolux', 
    'Whirlpool', 'Oppo', 'Xiaomi', 'JBL', 'Titan', 'Miniso'
]

def extract_brand_from_name(product_name, brand_from_json):
    """
    Tries to find a known brand name in the product title if the dedicated 
    brand_name field is empty. Prioritizes the JSON field if available.
    """
    if brand_from_json and brand_from_json != 'Unknown Brand':
        return brand_from_json
    
    name_lower = product_name.lower()
    
    for brand in KNOWN_BRANDS:
        if brand.lower() in name_lower:
            return brand
            
    return 'Unknown Brand'

def setup_session():
    """Configures a session with retry logic for connection/timeout errors."""
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

def scrape_buyabans(config):
    """
    Scrapes product data from BuyAbans.com API based on the provided configuration.
    Returns a list of dictionaries containing the scraped data.
    """
    all_products_data = []
    session = setup_session()
    
    # Static Headers
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://buyabans.com/'
    }

    print(f"\n[BuyAbans] Starting scrape for {config['country']}...")
    
    for cat_id in config['category_ids']:
        print(f"--- SCRAPING CATEGORY ID: {cat_id} ---")
        
        page = 1
        total_pages = 1
        
        while page <= total_pages:
            PAYLOAD = {
                'category_id': cat_id,
                'stamp_banner_id': '0',
                'sort': 'new_arrivals',
                'is_search_list': 'false',
                'page': page
            }
            
            try:
                print(f"-> Fetching page {page} of category {cat_id}...")
                response = session.get(config['base_url'], params=PAYLOAD, headers=HEADERS)
                response.raise_for_status() 
                
                data = response.json()
                
                if page == 1:
                    last_page_url = data['products'].get('last_page_url')
                    match = re.search(r'page=(\d+)', last_page_url)
                    if match:
                        total_pages = int(match.group(1))
                    else:
                        # Handle case where only one page exists
                        total_pages = 1
                    print(f"  Category has {total_pages} pages.")

                products = data['products']['data']

                for product in products:
                    name = product.get('product_name', product.get('name', 'N/A')).strip()
                    price_value = product.get('final_price', product.get('price')) 
                    
                    price = None 
                    if price_value is not None:
                        try:
                            price_str = str(price_value)
                            cleaned_price = re.sub(r'[^\d]', '', price_str.split('.')[0].replace(',', ''))
                            price = int(cleaned_price)
                        except ValueError:
                            pass 
                    
                    brand_from_json = product.get('brand_name')
                    final_brand_name = extract_brand_from_name(name, brand_from_json)

                    # Filter based ONLY on the wide price range defined in config
                    is_in_price_range = price is not None and config['min_price'] <= price <= config['max_price']

                    if is_in_price_range:
                        all_products_data.append({
                            'Category ID': cat_id,
                            'Brand': final_brand_name,
                            'Model': name,
                            'Price (LKR)': price,
                            'Country': config['country'],
                            'Year (Target)': config['year']
                        })
                
                page += 1
                time.sleep(random.uniform(1, 3)) 

            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [500, 502, 503, 504, 524]:
                    print(f"  Final failure for category {cat_id} after retries: {e}")
                    break
                else:
                    print(f"  HTTP Error {e.response.status_code} in category {cat_id}: {e}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"  Network error/Final timeout in category {cat_id}: {e}")
                break
            except Exception as e:
                print(f"  An unexpected error occurred in category {cat_id}: {e}")
                break 

    print(f"\n[BuyAbans] Scraping finished. Found {len(all_products_data)} products.")
    return all_products_data