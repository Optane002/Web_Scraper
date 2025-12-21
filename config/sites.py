from scrapers.srilanka import buyabans, laptoplk, singersl, unitysystems, abansit, nanotek
from scrapers.japan import tokyopc

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
                "base_url": "https://www.singersl.com/filter",
                "output_filename": "SingerSL_All_Products.xlsx",
                "country": "Sri Lanka",
                "year": 2025,
                "min_price": 1000,
                "max_price": 99999999
            }
        },
        "UnitySystems.lk (All Products)": {
            "scraper": unitysystems.scrape_unitysystems,
            "config": {
                "base_url": "https://www.unitysystems.lk/shop/",
                "output_filename": "UnitySystems_All_Products.xlsx",
                "country": "Sri Lanka",
                "year": 2025,
                "min_price": 1000,
                "max_price": 99999999
            }
        },
        "AbansIT.lk (All Products)": {
            "scraper": abansit.scrape_abansit,
            "config": {
                "base_url": "https://abansit.lk/welcome/productsPagination/",
                "output_filename": "AbansIT_All_Products.xlsx",
                "country": "Sri Lanka",
                "year": 2025,
                "min_price": 1000,
                "max_price": 99999999,
                "categories": [
                    "laptops", "desktops", "monitors", "accessories", 
                    "gaming", "tablets", "printers", "all-in-one",
                    "education", "professional", "smartboards", "signages"
                ]
            }
        },
        "Nanotek.lk (All Products)": {
            "scraper": nanotek.scrape_nanotek,
            "config": {
                "base_url": "https://www.nanotek.lk",
                "output_filename": "Nanotek_All_Products.xlsx",
                "country": "Sri Lanka",
                "year": 2025,
                "min_price": 1000,
                "max_price": 99999999
            }
        }
    },
    "Japan": {
        "TokyoPC.jp (All Products)": {
            "scraper": tokyopc.scrape_tokyopc,
            "config": {
                "base_url": "https://www.tokyopc.jp/",
                "output_filename": "TokyoPC_All_Products.xlsx",
                "country": "Japan",
                "year": 2025,
                "min_price": 1000,
                "max_price": 99999999
            }
        }
    }
}