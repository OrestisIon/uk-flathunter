#!/usr/bin/env python3
"""Debug script to check Zoopla HTML structure"""
import time
from bs4 import BeautifulSoup
from flathunter.core.config import Config
from flathunter.crawling.chrome_wrapper import get_chrome_driver

# Load config
config = Config('config.yaml')

# Get the URL
url = "https://www.zoopla.co.uk/to-rent/property/wc1x/?added=24_hours&beds_min=0&is_retirement_home=false&is_shared_accommodation=false&is_student_accommodation=false&price_frequency=per_month&price_max=2500&q=WC1X&radius=1&search_source=to-rent"

# Initialize driver
driver = get_chrome_driver([])

try:
    print("Loading URL...")
    driver.get(url)

    # Wait for JavaScript to render
    print("Waiting for page to load...")
    time.sleep(5)

    # Get page source
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    # Save to file for inspection
    with open('zoopla_debug.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    print("\nHTML saved to zoopla_debug.html")

    # Try to find property cards using various selectors
    print("\n=== Checking for property cards ===")

    # Method 1: data-testid
    cards_testid = soup.find_all('div', attrs={'data-testid': lambda x: x and 'search-result' in x})
    print(f"Found {len(cards_testid)} cards with data-testid containing 'search-result'")

    # Method 2: class patterns
    cards_class = soup.find_all('div', class_=lambda x: x and ('listing' in str(x).lower() or 'result' in str(x).lower() or 'card' in str(x).lower()))
    print(f"Found {len(cards_class)} divs with 'listing', 'result', or 'card' in class")

    # Method 3: Look for links to property details
    links = soup.find_all('a', href=lambda x: x and '/to-rent/details/' in x)
    print(f"Found {len(links)} links to /to-rent/details/")

    if links:
        print("\nFirst few property links found:")
        for i, link in enumerate(links[:5]):
            href = link.get('href', '')
            text = link.get_text(strip=True)[:50]
            print(f"  {i+1}. {href} - {text}")

    # Look for article tags (common for listings)
    articles = soup.find_all('article')
    print(f"\nFound {len(articles)} <article> tags")

    # Look for li tags (if listings are in a list)
    lis = soup.find_all('li', class_=lambda x: x and ('listing' in str(x).lower() or 'result' in str(x).lower()))
    print(f"Found {len(lis)} <li> tags with 'listing' or 'result' in class")

finally:
    print("\nClosing driver...")
    driver.quit()
