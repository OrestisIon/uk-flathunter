"""Expose crawler for Zoopla (UK)"""
import re
import time
import json
from typing import Optional, List, Dict
from bs4 import BeautifulSoup, Tag

from flathunter.core.logging import logger
from flathunter.crawling.webdriver_crawler import WebdriverCrawler


class Zoopla(WebdriverCrawler):
    """Implementation of Crawler interface for Zoopla"""

    URL_PATTERN = re.compile(r'https://www\.zoopla\.co\.uk')

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def get_page(self, search_url, driver=None, page_no=None) -> BeautifulSoup:
        """Applies a page number to a formatted search URL and fetches the exposes at that page"""
        driver = self.get_driver()
        soup = self.get_soup_from_url(search_url, driver=driver)

        # Wait for JavaScript to render property listings
        # Zoopla uses heavy JavaScript, so we need to give it time
        logger.debug("Waiting for JavaScript to render property listings...")
        time.sleep(3)

        # Refresh the soup with updated page source
        if driver:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'lxml')

        return soup

    def extract_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extracts all property listings from JSON-LD structured data"""
        entries = []

        # Zoopla provides all property data in JSON-LD (Schema.org) structured data
        # Find the JSON-LD script tag with type="application/ld+json"
        json_ld_scripts = soup.find_all('script', type='application/ld+json')

        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)

                # Check if this is the SearchResultsPage with ItemList
                if isinstance(data, dict) and '@graph' in data:
                    # Handle @graph format
                    for item in data['@graph']:
                        if item.get('@type') == 'SearchResultsPage' and 'mainEntity' in item:
                            entries = self._parse_item_list(item['mainEntity'], soup)
                            break
                elif isinstance(data, dict) and data.get('@type') == 'SearchResultsPage':
                    # Handle direct SearchResultsPage format
                    if 'mainEntity' in data:
                        entries = self._parse_item_list(data['mainEntity'], soup)
                        break

                if entries:
                    break

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.debug("Could not parse JSON-LD: %s", e)
                continue

        logger.debug('Number of valid entries found from JSON-LD: %d', len(entries))
        return entries

    def _parse_item_list(self, item_list: Dict, soup: BeautifulSoup) -> List[Dict]:
        """Parse the ItemList from JSON-LD structured data"""
        entries = []

        if not isinstance(item_list, dict) or item_list.get('@type') != 'ItemList':
            return entries

        items = item_list.get('itemListElement', [])
        logger.debug("Found %d items in JSON-LD ItemList", len(items))

        # Extract addresses from HTML (they are in the same order as JSON-LD items)
        addresses = soup.find_all('address')

        for idx, list_item in enumerate(items):
            if not isinstance(list_item, dict):
                continue

            product = list_item.get('item', {})
            if not isinstance(product, dict):
                continue

            # Extract property details
            url = product.get('url', '')
            name = product.get('name', '')
            description = product.get('description', '')
            image = product.get('image', '')

            # Extract price from offers
            offers = product.get('offers', {})
            price = offers.get('price', '')
            currency = offers.get('priceCurrency', 'GBP')

            # Format price with currency
            if price:
                price_formatted = f"£{price} pcm"
            else:
                price_formatted = ""

            # Extract property ID from URL
            property_id = self._extract_id_from_url(url)

            # Extract number of bedrooms from name
            rooms = self._extract_rooms_from_name(name)

            # Get address from HTML if available (addresses are in same order as JSON-LD items)
            address = ""
            if idx < len(addresses):
                address = addresses[idx].get_text(strip=True)

            if url and name and price:
                details = {
                    'id': property_id if property_id else url,
                    'url': url,
                    'title': name,
                    'price': price_formatted,
                    'size': "",  # Not provided in JSON-LD
                    'rooms': rooms,
                    'address': address,
                    'image': image,
                    'crawler': self.get_name()
                }
                entries.append(details)

        return entries

    def _extract_rooms_from_name(self, name: str) -> str:
        """Extract number of bedrooms from property name"""
        # Match patterns like "1 bed", "2 bed", "Studio"
        if 'studio' in name.lower():
            return "0"

        bedroom_match = re.search(r'(\d+)\s*bed', name, re.I)
        if bedroom_match:
            return bedroom_match.group(1)

        return ""

    def _parse_property_card(self, card: Tag) -> Optional[Dict]:
        """Parse a property card element to extract details"""

        # Extract URL and ID
        url = self._extract_url(card)
        if url is None:
            logger.debug("No URL found - skipping")
            return None

        # Extract ID from URL - Zoopla URLs are like /to-rent/details/12345678/
        property_id = self._extract_id_from_url(url)
        if property_id is None:
            logger.debug("No property ID found - skipping")
            return None

        # Extract title
        title = self._extract_title(card)
        if not title:
            logger.debug("No title found - skipping")
            return None

        # Extract price
        price = self._extract_price(card)
        if not price:
            logger.debug("No price found - skipping")
            return None

        # Extract address
        address = self._extract_address(card)
        if not address:
            logger.debug("No address found - skipping")
            return None

        # Extract rooms (bedrooms)
        rooms = self._extract_rooms(card)

        # Extract size (square feet/meters)
        size = self._extract_size(card)

        # Extract image
        image = self._extract_image(card)

        details = {
            'id': property_id,
            'url': url,
            'title': title,
            'price': price,
            'size': size,
            'rooms': rooms,
            'address': address,
            'image': image,
            'crawler': self.get_name()
        }

        return details

    def _extract_url(self, card: Tag) -> Optional[str]:
        """Extract property URL from card"""
        # Look for link element with href
        link = card.find('a', href=re.compile(r'/to-rent/details/'))
        if isinstance(link, Tag) and link.has_attr('href'):
            href = link['href']
            if isinstance(href, str):
                # Ensure absolute URL
                if href.startswith('http'):
                    return href
                return f'https://www.zoopla.co.uk{href}'
        return None

    def _extract_id_from_url(self, url: str) -> Optional[int]:
        """Extract property ID from Zoopla URL"""
        # Zoopla URLs: https://www.zoopla.co.uk/to-rent/details/12345678/
        match = re.search(r'/details/(\d+)', url)
        if match:
            return int(match.group(1))
        return None

    def _extract_title(self, card: Tag) -> str:
        """Extract property title/description"""
        # Try data-testid first
        title_elem = card.find(attrs={'data-testid': 'listing-title'})
        if isinstance(title_elem, Tag):
            return title_elem.get_text(strip=True)

        # Try heading tags
        for tag in ['h2', 'h3', 'h4']:
            heading = card.find(tag)
            if isinstance(heading, Tag):
                text = heading.get_text(strip=True)
                if text:
                    return text

        return ""

    def _extract_price(self, card: Tag) -> str:
        """Extract rental price"""
        # Try data-testid
        price_elem = card.find(attrs={'data-testid': 'listing-price'})
        if isinstance(price_elem, Tag):
            return price_elem.get_text(strip=True)

        # Try common price class patterns
        price_elem = card.find(class_=re.compile(r'price', re.I))
        if isinstance(price_elem, Tag):
            return price_elem.get_text(strip=True)

        # Try finding text with currency symbol
        text = card.get_text()
        price_match = re.search(r'£[\d,]+\s*(pcm|per month|pw)?', text, re.I)
        if price_match:
            return price_match.group(0)

        return ""

    def _extract_address(self, card: Tag) -> str:
        """Extract property address"""
        # Try data-testid
        address_elem = card.find(attrs={'data-testid': 'listing-address'})
        if isinstance(address_elem, Tag):
            return address_elem.get_text(strip=True)

        # Try address tag
        address_elem = card.find('address')
        if isinstance(address_elem, Tag):
            return address_elem.get_text(strip=True)

        # Try common address class patterns
        address_elem = card.find(class_=re.compile(r'address', re.I))
        if isinstance(address_elem, Tag):
            return address_elem.get_text(strip=True)

        return ""

    def _extract_rooms(self, card: Tag) -> str:
        """Extract number of bedrooms"""
        # Look for bedroom information
        text = card.get_text()

        # Try to match patterns like "2 bed", "2 bedroom", etc.
        bedroom_match = re.search(r'(\d+)\s*bed', text, re.I)
        if bedroom_match:
            return bedroom_match.group(1)

        # Try to find in data attributes
        rooms_elem = card.find(attrs={'data-testid': re.compile(r'bed', re.I)})
        if isinstance(rooms_elem, Tag):
            room_text = rooms_elem.get_text(strip=True)
            digit_match = re.search(r'\d+', room_text)
            if digit_match:
                return digit_match.group(0)

        return ""

    def _extract_size(self, card: Tag) -> str:
        """Extract property size in square feet or meters"""
        text = card.get_text()

        # Try to match patterns like "850 sq ft", "79 sq m", etc.
        size_match = re.search(r'(\d+[\d,]*)\s*sq\s*(ft|m)', text, re.I)
        if size_match:
            return f"{size_match.group(1)} {size_match.group(2)}"

        return ""

    def _extract_image(self, card: Tag) -> Optional[str]:
        """Extract main property image URL"""
        # Try to find img tag
        img = card.find('img')
        if isinstance(img, Tag):
            # Try src attribute
            if img.has_attr('src'):
                src = img['src']
                if isinstance(src, str) and src.startswith('http'):
                    return src

            # Try data-src (lazy loading)
            if img.has_attr('data-src'):
                data_src = img['data-src']
                if isinstance(data_src, str) and data_src.startswith('http'):
                    return data_src

        return None
