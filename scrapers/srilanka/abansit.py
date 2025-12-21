import requests
from bs4 import BeautifulSoup
import re
import time
import random
import json
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
    'Pantum', 'Ricoh', 'Kyocera', 'Konica Minolta', 'Sharp', 'Toshiba',
    'Huawei'
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

def scrape_abansit(config):
    """
    Scrapes product data from Abans IT using their AJAX pagination endpoint.
    """
    all_products_data = []
    session = setup_session()
    base_url = config['base_url']
    
    categories = config.get('categories', [])
    
    page = 1
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://abansit.lk/products',
    }

    print(f"--- Starting Scrape for Abans IT ---")

    while True:
        url = f"{base_url}{page}"
        
        params = {
            'brands': '[]',
            'min_price': config.get('min_price', 0),
            'max_price': config.get('max_price', 1000000),
            'page_name': 'all_products',
            'categories': json.dumps(categories),
            'ram': '[]',
            'storage': '[]',
            'processor': '[]'
        }
        
        print(f"Scraping Page {page}...")
        
        try:
            response = session.get(url, headers=HEADERS, params=params, timeout=20)
            
            if response.status_code != 200:
                print(f"Failed to fetch page {page}. Status code: {response.status_code}")
                break
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"Failed to decode JSON on page {page}. Response might not be JSON.")
                break
            
            product_html = data.get('product_table', '')
            if not product_html.strip():
                print("No products found in response (empty HTML). Ending scrape.")
                break
                
            soup = BeautifulSoup(product_html, 'html.parser')
            
            products = soup.select('.product-shortcode.style-1')
            
            if not products:
                print(f"No product cards found in HTML on page {page}. Ending scrape.")
                break
                
            print(f"Found {len(products)} products on page {page}.")
            
            for product in products:
                try:
                    title_elem = product.select_one('.title')
                    if not title_elem:
                        continue
                    
                    if title_elem.name != 'a':
                        name_anchor = title_elem.select_one('a')
                        if name_anchor:
                            product_name = name_anchor.text.strip()
                        else:
                            product_name = title_elem.text.strip()
                    else:
                        product_name = title_elem.text.strip()
                    
                    product_name = " ".join(product_name.split())

                    product_url = "N/A"
                    if title_elem.name == 'a':
                        product_url = title_elem.get('href')
                    else:
                        link_elem = product.select_one('a.preview') or product.select_one('a.image')
                        if link_elem:
                            product_url = link_elem.get('href')
                            
                    price_elem = product.select_one('.price')
                    price_text = "0"
                    if price_elem:
                        
                        new_price = price_elem.select_one('.new-price')
                        if new_price:
                            price_text = new_price.text
                        else:
                            price_text = price_elem.text
                            
                    
                    price_text = re.sub(r'[^\d.]', '', price_text)
                    try:
                        price = float(price_text)
                    except ValueError:
                        price = 0.0
                        
                    
                    if not (config['min_price'] <= price <= config['max_price']):
                        continue

                    
                    brand = extract_brand_from_name(product_name)
                    
                    
                    image_url = "N/A"
                    img_elem = product.select_one('img')
                    if img_elem:
                        image_url = img_elem.get('src')

                    
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
            
            page += 1
            
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            break

    return all_products_data
