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
    'Pantum', 'Ricoh', 'Kyocera', 'Konica Minolta', 'Sharp', 'Toshiba',
    'Huawei', 'Sony', 'Microsoft', 'Google', 'OnePlus', 'Nokia'
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

def get_categories(session, base_url):
    """Fetches the home page to extract category URLs."""
    print(f"Fetching categories from {base_url}...")
    try:
        response = session.get(base_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        categories = []
        # Select category links from the sidebar/menu
        # Based on nanotek.html: ul.ty-cat-list li.ty-catListItem a
        cat_links = soup.select('ul.ty-cat-list li.ty-catListItem a')
        
        for link in cat_links:
            href = link.get('href')
            name = link.select_one('.ty-catTitle span')
            if name:
                name = name.text.strip()
            else:
                name = "Unknown Category"
                
            if href and href.startswith('http'):
                categories.append({'name': name, 'url': href})
                
        print(f"Found {len(categories)} categories.")
        return categories
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

# --- Main Scraper Function ---

def scrape_nanotek(config):
    """
    Scrapes product data from Nanotek.lk by iterating through categories.
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
            # Assuming ?page=N pattern for Nanotek
            if page == 1:
                url = cat_url
            else:
                url = f"{cat_url}?page={page}"
            
            print(f"  Fetching page {page}...")
            
            try:
                response = session.get(url, timeout=20)
                
                if response.status_code == 404:
                    print("  Page not found. Moving to next category.")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Select product items
                # Based on nanotek.html: li.ty-catPage-productListItem
                products = soup.select('li.ty-catPage-productListItem')
                
                if not products:
                    print("  No products found on this page. Moving to next category.")
                    break
                
                print(f"  Found {len(products)} products.")
                
                items_added = 0
                for product in products:
                    try:
                        # Extract Link & Container
                        # The <a> tag wraps the .ty-productBlock-wrap
                        link_elem = product.find('a', href=True)
                        if not link_elem:
                            continue
                        product_url = link_elem['href']
                        
                        # Extract Title
                        title_elem = product.select_one('.ty-productBlock-title')
                        if title_elem:
                            product_name = title_elem.text.strip()
                            # Clean up whitespace
                            product_name = " ".join(product_name.split())
                        else:
                            continue
                            
                        # Extract Price
                        price_elem = product.select_one('.ty-productBlock-price-retail')
                        price_text = "0"
                        if price_elem:
                            price_text = re.sub(r'[^\d.]', '', price_elem.text)
                        
                        try:
                            price = float(price_text)
                        except ValueError:
                            price = 0.0
                            
                        # Filter by price
                        if not (config['min_price'] <= price <= config['max_price']):
                            continue
                            
                        # Extract Image
                        img_elem = product.select_one('.ty-productBlock-imgHolder img')
                        image_url = "N/A"
                        if img_elem:
                            image_url = img_elem.get('src')
                            
                        # Extract Brand
                        brand = extract_brand_from_name(product_name)
                        
                        all_products_data.append({
                            'Category': cat_name,
                            'Brand': brand,
                            'Model': product_name,
                            'Price (LKR)': price,
                            'Product URL': product_url,
                            'Image URL': image_url,
                            'Country': config['country'],
                            'Year (Target)': config['year']
                        })
                        items_added += 1
                        
                    except Exception as e:
                        continue
                
                if items_added == 0 and len(products) > 0:
                     # If we found products but filtered them all out, we should still check next page
                     pass

                # Check for Next Page
                # Nanotek uses a "View More Results" button which might just be a link or JS.
                # If we are using ?page=N, we need to know when to stop.
                # If the number of products is small (e.g. < 10), it might be the last page.
                # Or we can check if the "View More" button exists.
                # In nanotek.html: <div class="ty-more-wrap js-more-results">
                
                next_button = soup.select_one('.js-more-results')
                if not next_button:
                    print("  No 'View More' button found. End of category.")
                    break
                
                page += 1
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"  Error scraping page {page}: {e}")
                break
        
        # Small pause between categories
        time.sleep(1)

    return all_products_data
