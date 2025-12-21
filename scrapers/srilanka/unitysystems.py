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
    'Whirlpool', 'Oppo', 'Xiaomi', 'JBL', 'Titan', 'Miniso',
    'Logitech', 'Fantech', 'Razer', 'Corsair', 'HyperX', 'SteelSeries',
    'Gigabyte', 'Zotac', 'Palit', 'Galax', 'PNY', 'Intel', 'AMD',
    'Kingston', 'Transcend', 'Adata', 'Western Digital', 'Seagate',
    'Hikvision', 'Dahua', 'Ezviz', 'Imou', 'Tp-Link', 'D-Link',
    'Ubiquiti', 'Mikrotik', 'Cisco', 'Epson', 'Canon', 'Brother',
    'Pantum', 'Ricoh', 'Kyocera', 'Konica Minolta', 'Sharp', 'Toshiba'
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

def scrape_unitysystems(config):
    """
    Scrapes ALL product data from Unity Systems shop page using HTML parsing.
    """
    all_products_data = []
    session = setup_session()
    base_url = config['base_url']
    page = 1
    
    # Static Headers
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    print(f"--- Starting Scrape for Unity Systems ---")

    while True:
        # Construct URL for pagination
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}page/{page}/"
            
        print(f"Scraping Page {page}...")
        
        try:
            response = session.get(url, headers=HEADERS, timeout=20)
            
            # Check if we've reached a non-existent page (some sites redirect to home or 404)
            if response.status_code == 404:
                print("Reached 404. Ending scrape.")
                break
            
            # Some sites redirect to the first page if the page number is too high
            if page > 1 and response.url == base_url:
                print("Redirected to home/first page. Ending scrape.")
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product containers
            # Based on analysis: div.product-grid-item or div.wd-product
            products = soup.select('div.product-grid-item')
            
            if not products:
                print("No products found on this page. Ending scrape.")
                break
                
            print(f"Found {len(products)} products on page {page}.")
            
            for product in products:
                try:
                    # Extract Name
                    name_elem = product.select_one('h3.wd-entities-title a')
                    if not name_elem:
                        continue
                    product_name = name_elem.text.strip()
                    product_url = name_elem.get('href')
                    
                    # Extract Price
                    # Try multiple selectors for price
                    price_elem = product.select_one('span.price span.woocommerce-Price-amount bdi')
                    if not price_elem:
                        # Check for sale price
                        price_elem = product.select_one('span.price ins span.woocommerce-Price-amount bdi')
                    
                    price_text = "0"
                    if price_elem:
                        # Remove currency symbol and commas
                        price_text = re.sub(r'[^\d.]', '', price_elem.text)
                    
                    try:
                        price = float(price_text)
                    except ValueError:
                        price = 0.0
                        
                    # Filter by price range
                    if not (config['min_price'] <= price <= config['max_price']):
                        continue

                    # Extract Brand
                    brand = extract_brand_from_name(product_name)
                    
                    # Extract Image
                    image_url = "N/A"
                    img_elem = product.select_one('div.product-element-top a.product-image-link img')
                    if img_elem:
                        image_url = img_elem.get('data-src') or img_elem.get('src')

                    # Add to list
                    all_products_data.append({
                        'Category': 'All Products',
                        'Brand': brand,
                        'Model': product_name,
                        'Price (LKR)': price,
                        'Product URL': product_url,
                        'Image URL': image_url,
                        'Country': config['country'],
                        'Year (Target)': config['year']
                    })
                    
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue
            
            # Check for next page button to decide whether to continue
            # Look for standard WooCommerce pagination
            next_button = soup.select_one('a.next.page-numbers')
            if not next_button:
                print("No 'Next' button found. Ending scrape.")
                break
                
            page += 1
            # Be polite
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            break

    return all_products_data
