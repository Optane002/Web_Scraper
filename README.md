🌐 Price Scraper CLI (Sri Lanka Focus)

A modular, command-line utility designed for fast, resilient scraping of product data from e-commerce websites in supported regions, currently focused on Sri Lanka.

📊 Status & Metadata

Status

Details

Version

(e.g., v1.0.0)

License



Language

Python 3.8+

🧭 Table of Contents

✨ Features & Resilience

🚀 Getting Started

⚙️ Project Structure & Extensibility

📝 License

✨ Features & Resilience

The tool is built for stability and easy contribution:

Modular Architecture: The core logic is cleanly separated from site-specific code, making it simple to extend the tool.

Initial Coverage: Supports scraping all major product categories from BuyAbans.com.

Resilience: Implements automatic request retries (handling 504 Gateway Timeouts) and polite scraping delays to prevent IP blocking.

Data Integrity: Robust brand extraction logic ensures accurate product attribution, even if the source JSON is messy.

User Interface: Interactive CLI guides users through dependency checks and site selection.

Output: Exports clean, structured data directly to .xlsx (Excel) files.

🚀 Getting Started

1. Prerequisites

You must have Python 3.8+ installed on your system.

2. Installation

Clone the repository and move into the project directory:

git clone [https://github.com/YourUsername/price-scraper-cli.git](https://github.com/YourUsername/price-scraper-cli.git)
cd price-scraper-cli


Install all required Python packages (requests, pandas, openpyxl, urllib3):

pip install -r requirements.txt


3. Running the Scraper

Execute the main script from the root directory of the project:

python web_scraper.py


The application will display a shell-style header, check dependencies, and then prompt you to select the country and target website.

⚙️ Project Structure & Extensibility

The application is split into clear components, allowing simple contribution:

price-scraper-cli/
├── config/
│   └── sites.py        # Maps countries/sites to their scraper functions and configuration settings.
├── scrapers/
│   ├── __init__.py     # Package initializer.
│   └── buyabans.py     # **Contains site-specific scraping logic and helpers.**
├── web_scraper.py      # Main CLI entry point, handling headers, checks, and user flow.
├── requirements.txt    # Lists all mandatory dependencies.
└── README.md


Contributing: Adding a New Website

The core principle of this project is easy extensibility. To add support for a new website (e.g., nanotek.lk):

Create a Scraper Module (scrapers/nanotek.py):

Create a new file in the scrapers/ directory (e.g., nanotek.py).

Implement the main scraping function (it must accept a config dictionary and return a list of product dictionaries).

Integrate Configuration:

Import your new scraper function into scrapers/__init__.py.

Add a new entry to the SUPPORTED_SITES dictionary in config/sites.py, providing the necessary configuration (Base URL, specific IDs, file names, etc.).

📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
