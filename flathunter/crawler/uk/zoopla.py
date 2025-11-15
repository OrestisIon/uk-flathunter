"""Expose crawler for Zoopla (UK)"""
import re
from typing import Optional, List, Dict
from bs4 import BeautifulSoup, Tag

from flathunter.core.logging import logger
from flathunter.core.abstract_crawler import Crawler


class Zoopla(Crawler):
    """Implementation of Crawler interface for Zoopla"""

    URL_PATTERN = re.compile(r'https://www\.zoopla\.co\.uk')

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def extract_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extracts all property listings from a provided Soup object"""
        entries = []

        # Zoopla uses a data-testid attribute for property cards
        # The structure is: <div data-testid="search-result">
        findings = soup.find_all('div', attrs={'data-testid': lambda x: x and 'search-result' in x})

        if not findings:
            # Fallback: try to find listing cards by common class patterns
            findings = soup.find_all('div', class_=re.compile(r'listing|search-result|property-card', re.I))

        logger.debug('Found %d potential property cards', len(findings))

        for card in findings:
            if not isinstance(card, Tag):
                continue

            details = self._parse_property_card(card)
            if details is not None:
                entries.append(details)

        logger.debug('Number of valid entries found: %d', len(entries))
        return entries

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
