# 🌐 Price Scraper CLI

A modular CLI for fast, resilient scraping of product data from e-commerce stores. Built for extensibility and polite scraping.

## Status & Metadata

| Field    | Details           |
|--------- |------------------|
| Version  | [![GitHub release (latest by date)](https://img.shields.io/github/v/release/Optane002/Web_Scraper?label=Version&color=blue)](https://github.com/Optane002/Web_Scraper/releases) |
| License  | [![License](https://img.shields.io/github/license/Optane002/Web_Scraper?label=License&color=green)](https://github.com/Optane002/Web_Scraper/blob/main/LICENSE) |
| Language | [![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/) |


## Table of Contents

- [Features & Resilience](#features--resilience)
- [Getting Started](#getting-started)
- [Project Structure & Extensibility](#project-structure--extensibility)
- [License](#license)

## Features & Resilience

- **Multi-Region Support**: Scrapes sites from **Sri Lanka** (Abans, Unity, Nanotek, Singer, Laptop.lk) and **Japan** (TokyoPC).
- **Modular Architecture**: Keeps core logic separate from site-specific scrapers.
- **Auto-Update**: Automatically checks for updates against the GitHub repository on startup.
- **Resilient Scraping**: Automatic retries handle transient errors with polite delays.
- **Brand Extraction**: Guards against messy or incomplete upstream data.
- **Interactive CLI**: Guides dependency checks, region selection, and scraper choice.
- **Excel Export**: Output exports to clean `.xlsx` files for analysis.

## Getting Started

### 1. Prerequisites

Install Python **3.8+**.

### 2. Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/Optane002/Web_Scraper.git
cd Web_Scraper
pip install -r requirements.txt # requests, pandas, openpyxl, urllib3, etc.
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
│   ├── country1/       # Country1 scrapers
│   └── country2/          # Country2 scrapers
├── web_scraper.py      # Main CLI entry point and flow controller.
├── requirements.txt    # Python dependencies.
├── version.txt         # Current version tracking.
└── README.md
```

### Adding a New Website

1. **Create a scraper**: add `scrapers/<country>/<site>.py` with a function that accepts a config dict and returns a list of product dicts.
2. **Wire it up**:
   - Import your scraper inside `scrapers/<country>/__init__.py`.
   - Extend `SUPPORTED_SITES` in `config/sites.py` with the new entry (base URL, category IDs, export filename, etc.).

## License

This project is licensed under the MIT License. See `LICENSE` for details.
