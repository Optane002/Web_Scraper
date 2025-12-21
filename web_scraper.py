import os
import sys
import pandas as pd
from config.sites import SUPPORTED_SITES

REQUIRED_PACKAGES = ['requests', 'pandas', 'openpyxl', 'urllib3', 'bs4']
VERSION_FILE = "version.txt"
REPO_VERSION_URL = "https://raw.githubusercontent.com/Optane002/Web_Scraper/main/version.txt"

def get_current_version():
    """Reads the current version from the local version file."""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return "Unknown"

def display_header():
    """Prints a styled header for the CLI application using a raw string."""
    version = get_current_version()
    header = rf"""
    _______________________________________________________________
    
        ██╗    ██╗███████╗██████╗                               
        ██║    ██║██╔════╝██╔══██╗                              
        ██║ █╗ ██║█████╗  ██████╔╝                              
        ██║███╗██║██╔══╝  ██╔══██╗                              
        ╚███╔███╔╝███████╗██████╔╝                              
         ╚══╝╚══╝ ╚══════╝╚═════╝                               
                                                        
            ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
            ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
            ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
            ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
            ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
            ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝    
                       ><>< Developed by Chamicara De Silva ><><
                                   Version: {version}
    _______________________________________________________________
    """
    print(header)

def check_dependencies():
    """Checks if all packages listed in requirements.txt are installed."""
    print("--- 1. Checking Dependencies ---")
    all_installed = True
    
    sys.stdout.flush()

    for package in REQUIRED_PACKAGES:
        try:
            import_name = "bs4" if package == "bs4" else package
            __import__(import_name)
            print(f"  [ OK ] {package}")
        except ImportError:
            print(f"  [FAIL] {package}. Please run 'pip install -r requirements.txt'")
            all_installed = False
            
    if not all_installed:
        print("\nDependencies missing. Please install required packages before proceeding.")
        sys.exit(1)
    
    print("\n✅ Dependencies check passed.")


def check_for_updates():
    """Checks a remote GitHub file for the latest version."""
    print("\n--- 2. Checking for Updates ---")
    current_version = get_current_version()
    
    if "YOUR_USERNAME" in REPO_VERSION_URL:
        print("  ℹ️  Update check skipped (Repo URL not configured).")
        return

    try:
        import requests
        response = requests.get(REPO_VERSION_URL, timeout=3)
        
        if response.status_code == 200:
            latest_version = response.text.strip()
            if latest_version != current_version:
                print(f"  ⚠️  NEW VERSION AVAILABLE: {latest_version}")
                print(f"  Current version: {current_version}")
                print(f"  Please pull the latest changes from the repository.")
                
                choice = input("  Continue with current version? (y/n): ").lower()
                if choice != 'y':
                    print("Exiting to allow update.")
                    sys.exit(0)
            else:
                print("  ✅ You are using the latest version.")
        else:
            print(f"  ⚠️  Could not check for updates (Status: {response.status_code})")
            
    except Exception as e:
        print(f"  ⚠️  Could not check for updates: {e}")


def get_user_choice():
    """Prompts the user to select a country and a website."""
    
    countries = list(SUPPORTED_SITES.keys())
    if not countries:
        print("\nError: No supported countries defined in config/sites.py. Exiting.")
        sys.exit(1)
        
    print("\n--- 3. Select Country ---")
    
    for i, country_name in enumerate(countries, 1):
        print(f"  {i}. {country_name}")
        
    try:
        if len(countries) > 1:
            country_choice = int(input("Enter country number: "))
            selected_country = countries[country_choice - 1]
        else:
            print(f"  (Defaulting to: {countries[0]})")
            selected_country = countries[0]
            
    except (ValueError, IndexError):
        print("Invalid choice. Exiting.")
        sys.exit(1)
        
    sites_in_country = SUPPORTED_SITES[selected_country]
    
    print(f"\n--- 4. Select Website (Country: {selected_country}) ---")
    
    site_names = list(sites_in_country.keys())
    for i, name in enumerate(site_names, 1):
        print(f"  {i}. {name}")
        
    try:
        site_choice = int(input("Enter website number: "))
        if 1 <= site_choice <= len(site_names):
            site_name = site_names[site_choice - 1]
            return sites_in_country[site_name]
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)
    except ValueError:
        print("Invalid input. Please enter a number. Exiting.")
        sys.exit(1)


def save_data(data, config):
    """Saves the scraped data to an Excel file using pandas, removing duplicates."""
    filename = config['output_filename']
    if not data:
        print("No data was scraped to save.")
        return

    print(f"\n--- 6. Saving Data to {filename} ---")
    try:
        df = pd.DataFrame(data)
        
        initial_count = len(df)
        df.drop_duplicates(subset=['Model', 'Price (LKR)'], keep='first', inplace=True)
        final_count = len(df)
        
        if initial_count > final_count:
            print(f"  ℹ️ Removed {initial_count - final_count} duplicate entries.")
        
        df.to_excel(filename, index=False, engine='openpyxl') 
        print(f"✅ SUCCESS: Data saved to {filename}")
        print(f"Total unique records saved: {final_count}")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to save to Excel. Details: {e}")


if __name__ == "__main__":
    
    display_header()
    check_dependencies()
    check_for_updates()
    
    chosen_site = get_user_choice()
    
    scraper_function = chosen_site['scraper']
    scraper_config = chosen_site['config']
    
    print("\n--- 5. Running Scraper ---")
    scraped_data = scraper_function(scraper_config)
    
    save_data(scraped_data, scraper_config)
    
    print("\n--------------------------------------------------------------")
    print("✨ Bye now ! Have a great day.")
    print("--------------------------------------------------------------")