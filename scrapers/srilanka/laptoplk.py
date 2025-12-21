import requests
from bs4 import BeautifulSoup
import re
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# --- Brand and Session Helpers ---

KNOWN_BRANDS = [
    'HP', 'Lenovo', 'Asus', 'Acer', 'Dell', 'MSI', 'Apple', 
    'Samsung', 'LG', 'JVC', 'Haier', 'Toshiba', 'Electrolux', 
    'Whirlpool', 'Oppo', 'Xiaomi', 'JBL', 'Titan', 'Miniso'
]

def extract_brand_from_name(product_name):
    """Tries to find a known brand name in the product title."""
    name_lower = product_name.lower()
    for brand in KNOWN_BRANDS:
        if brand.lower() in name_lower:
            return brand
    return 'Other'

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

def scrape_laptop_lk(config):
    """
    Scrapes ALL product data from Laptop.lk shop page using HTML parsing.
    """
    all_products_data = []
    session = setup_session()
    base_url = config['base_url']
    page = 1
    
    # Static Headers
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"\n[Laptop.lk] Starting full shop scrape for {config['country']}...")
    
    # Loop indefinitely until no new page link is found
    while True:
        # Construct the URL for the current page. 
        # Page 1 is just the base URL, Page 2+ follows the /page/N/ pattern
        current_url = f"{base_url}page/{page}/" if page > 1 else base_url
        print(f"-> Fetching page {page}: {current_url}")
        
        try:
            response = session.get(current_url, headers=HEADERS)
            response.raise_for_status() 
            soup = BeautifulSoup(response.content, 'html.parser')

            # 1. Product Container: Standard WooCommerce product list item
            product_containers = soup.find_all('li', class_='product') 

            if not product_containers:
                print("  No more products or pagination found. Stopping scrape.")
                break

            for container in product_containers:
                # 2. Extract Name/Model
                name_elem = container.find('h2', class_='woocommerce-loop-product__title')
                name = name_elem.text.strip() if name_elem else "N/A"
                
                # 3. Extract Price (Handling Sale Items)
                # First, try to find a sale price (<ins>)
                price_elem = container.find('ins')
                
                # If no sale price, get the standard price container
                if not price_elem:
                    price_elem = container.find('span', class_='price')

                # Extract text from the found element
                price_text = price_elem.text if price_elem else "N/A"
                
                price = None 
                if price_text != 'N/A':
                    try:
                        # Clean the price: remove currency symbol (රු/Rs/LKR), commas, and decimals
                        # We split by '.' to drop cents, then remove non-digits
                        cleaned_price = re.sub(r'[^\d]', '', price_text.split('.')[0].replace(',', ''))
                        price = int(cleaned_price)
                    except ValueError:
                        pass 
                
                # 4. Determine Brand (from name/title)
                final_brand_name = extract_brand_from_name(name)

                # 5. Filter based on Price Range
                is_in_price_range = price is not None and config['min_price'] <= price <= config['max_price']

                if is_in_price_range:
                    all_products_data.append({
                        'Category': 'All Products', 
                        'Brand': final_brand_name,
                        'Model': name,
                        'Price (LKR)': price,
                        'Country': config['country'],
                        'Year (Target)': config['year']
                    })

            # Check for next page link/button (Crucial for pagination control)
            # WooCommerce usually has a 'next' class on the next page arrow
            next_link = soup.find('a', class_='next', href=True)
            
            if next_link:
                page += 1
                # Be polite and wait between requests
                time.sleep(random.uniform(1, 3))
            else:
                print("  Reached the last page.")
                break

        except requests.exceptions.HTTPError as e:
            # 404 usually means we went past the last page
            if e.response.status_code == 404:
                print(f"  Page {page} not found (404). Assuming end of list.")
                break
            print(f"  Final failure fetching page {page}: {e}.")
            break 
        except Exception as e:
            print(f"  An unexpected error occurred on page {page}: {e}. Aborting scrape for this site.")
            break 
            
    print(f"\n[Laptop.lk] Scraping finished. Found {len(all_products_data)} products.")
    return all_products_data