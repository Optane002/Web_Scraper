from scrapers import buyabans, laptoplk, singersl

SUPPORTED_SITES = {
    "Sri Lanka": {
        "BuyAbans.com (All Products)": {
            "scraper": buyabans.scrape_buyabans,
            "config": {
                "base_url": "https://buyabans.com/product-list",
                "category_ids": [
                    '67', '567', '9', '568', '569', '570', '572', 
                    '573', '27', '19', '26', '17', '33'
                ],
                "output_filename": "BuyAbans_All_Products.xlsx",
                "country": "Sri Lanka",
                "year": 2025,
                "min_price": 1000,
                "max_price": 99999999
            }
        },
        "Laptop.lk (All Products)": {
            "scraper": laptoplk.scrape_laptop_lk,
            "config": {
                "base_url": "https://www.laptop.lk/index.php/shop/",
                "output_filename": "Laptop_lk_All_Products.xlsx",
                "country": "Sri Lanka",
                "year": 2025,
                "min_price": 1000,
                "max_price": 99999999
            }
        },
        "Singer.lk (All Products)": {
            "scraper": singersl.scrape_singer_sl,
            "config": {
                "base_url": "https://www.singersl.com/products",
                "output_filename": "SingerSL_All_Products.xlsx",
                "country": "Sri Lanka",
                "year": 2025,
                "min_price": 1000,
                "max_price": 99999999
            }
        }
    }
}
