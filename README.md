
# 🌐 Price Scraper CLI (Sri Lanka Only)

A modular CLI for fast, resilient scraping of product data from Sri Lankan e-commerce stores. Built for extensibility and polite scraping.

## Status & Metadata

| Field    | Details           |
|--------- |------------------|
| Version  | v1.0.0 |
| License  | MIT               |
| Language | Python 3.8+       |

## Table of Contents

- [Features & Resilience](#features--resilience)
- [Getting Started](#getting-started)
- [Project Structure & Extensibility](#project-structure--extensibility)
- [License](#license)

## Features & Resilience

- Modular architecture keeps core logic separate from site-specific scrapers.
- Initial coverage targets BuyAbans.com across major product categories.
- Automatic retries handle transient 504 errors with polite delays to avoid IP blocks.
- Brand extraction guards against messy or incomplete upstream JSON.
- Interactive CLI guides dependency checks, region selection, and scraper choice.
- Output exports to clean `.xlsx` files for analysis and sharing.

## Getting Started

### 1. Prerequisites

Install Python **3.8+**.

### 2. Installation

Clone the repo and install dependencies:

```
git clone https://github.com/Optane002/web_scraper.git
cd web_scraper
pip install -r requirements.txt  # requests, pandas, openpyxl, urllib3, etc.
```

### 3. Run the Scraper

```
python web_scraper.py
```

The CLI presents a shell-style header, performs dependency checks, then prompts for region and target site.

## Project Structure & Extensibility

```
price-scraper-cli/
├── config/
│   └── sites.py        # Maps countries/sites to their scrapers and config.
├── scrapers/
│   ├── __init__.py     # Package initializer.
│   └── mysite.py       # Site-specific scraping logic & helpers.
├── web_scraper.py      # Main CLI entry point and flow controller.
├── requirements.txt    # Python dependencies.
└── README.md
```

### Adding a New Website

1. **Create a scraper**: add `scrapers/<site>.py` with a function that accepts a config dict and returns a list of product dicts.
2. **Wire it up**:
   - Import your scraper inside `scrapers/__init__.py`.
   - Extend `SUPPORTED_SITES` in `config/sites.py` with the new entry (base URL, category IDs, export filename, etc.).

## License

This project is licensed under the MIT License. See `LICENSE` for details.
