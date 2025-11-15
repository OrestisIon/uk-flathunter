"""Expose crawler for Rightmove (UK)"""
import re
from typing import Optional, List, Dict
from bs4 import BeautifulSoup, Tag

from flathunter.core.logging import logger
from flathunter.core.abstract_crawler import Crawler


class Rightmove(Crawler):
    """Implementation of Crawler interface for Rightmove"""

    URL_PATTERN = re.compile(r'https://www\.rightmove\.co\.uk')

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def extract_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extracts all property listings from a provided Soup object"""
        entries = []

        # Rightmove uses class "propertyCard" for individual listings
        findings = soup.find_all('div', class_=re.compile(r'propertyCard', re.I))

        if not findings:
            # Fallback: try to find listings by common patterns
            findings = soup.find_all('div', attrs={'id': re.compile(r'property-\d+', re.I)})

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

        # Extract ID from URL or property card
        property_id = self._extract_id(card, url)
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
        # Look for link with class propertyCard-link or similar
        link = card.find('a', class_=re.compile(r'propertyCard.*link', re.I))
        if isinstance(link, Tag) and link.has_attr('href'):
            href = link['href']
            if isinstance(href, str):
                # Ensure absolute URL
                if href.startswith('http'):
                    return href
                return f'https://www.rightmove.co.uk{href}'

        # Try any link that contains "properties"
        link = card.find('a', href=re.compile(r'/properties/'))
        if isinstance(link, Tag) and link.has_attr('href'):
            href = link['href']
            if isinstance(href, str):
                if href.startswith('http'):
                    return href
                return f'https://www.rightmove.co.uk{href}'

        return None

    def _extract_id(self, card: Tag, url: str) -> Optional[int]:
        """Extract property ID from card or URL"""
        # Try to extract from card's id attribute
        if card.has_attr('id'):
            card_id = card['id']
            if isinstance(card_id, str):
                # Extract digits from id like "property-123456"
                match = re.search(r'\d+', card_id)
                if match:
                    return int(match.group(0))

        # Try to extract from data-test attribute
        if card.has_attr('data-test'):
            data_test = card['data-test']
            if isinstance(data_test, str):
                match = re.search(r'\d+', data_test)
                if match:
                    return int(match.group(0))

        # Extract from URL - Rightmove URLs: /properties/123456789
        match = re.search(r'/properties/(\d+)', url)
        if match:
            return int(match.group(1))

        # Try property-id in URL parameters
        match = re.search(r'propertyId=(\d+)', url)
        if match:
            return int(match.group(1))

        return None

    def _extract_title(self, card: Tag) -> str:
        """Extract property title/description"""
        # Try propertyCard-title class
        title_elem = card.find(class_=re.compile(r'propertyCard.*title', re.I))
        if isinstance(title_elem, Tag):
            return title_elem.get_text(strip=True)

        # Try heading tags
        for tag in ['h2', 'h3', 'h4']:
            heading = card.find(tag)
            if isinstance(heading, Tag):
                text = heading.get_text(strip=True)
                if text and 'bedroom' in text.lower():
                    return text

        return ""

    def _extract_price(self, card: Tag) -> str:
        """Extract rental price"""
        # Try propertyCard-priceValue class
        price_elem = card.find(class_=re.compile(r'propertyCard.*price', re.I))
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
        # Try propertyCard-address class
        address_elem = card.find(class_=re.compile(r'propertyCard.*address', re.I))
        if isinstance(address_elem, Tag):
            return address_elem.get_text(strip=True)

        # Try address tag
        address_elem = card.find('address')
        if isinstance(address_elem, Tag):
            return address_elem.get_text(strip=True)

        # Try meta itemprop="address"
        address_elem = card.find(attrs={'itemprop': 'address'})
        if isinstance(address_elem, Tag):
            return address_elem.get_text(strip=True)

        return ""

    def _extract_rooms(self, card: Tag) -> str:
        """Extract number of bedrooms"""
        # Try propertyCard-details or similar
        details_elem = card.find(class_=re.compile(r'propertyCard.*details', re.I))
        if isinstance(details_elem, Tag):
            text = details_elem.get_text()
            bedroom_match = re.search(r'(\d+)\s*bed', text, re.I)
            if bedroom_match:
                return bedroom_match.group(1)

        # Look in the full card text
        text = card.get_text()
        bedroom_match = re.search(r'(\d+)\s*bed', text, re.I)
        if bedroom_match:
            return bedroom_match.group(1)

        return ""

    def _extract_size(self, card: Tag) -> str:
        """Extract property size in square feet or meters"""
        text = card.get_text()

        # Try to match patterns like "850 sq ft", "79 sq m", etc.
        size_match = re.search(r'(\d+[\d,]*)\s*sq\.?\s*(ft|m|metres|feet)', text, re.I)
        if size_match:
            return f"{size_match.group(1)} {size_match.group(2)}"

        return ""

    def _extract_image(self, card: Tag) -> Optional[str]:
        """Extract main property image URL"""
        # Try to find img tag with propertyCard-img class
        img = card.find('img', class_=re.compile(r'propertyCard.*img', re.I))
        if isinstance(img, Tag):
            # Try src attribute
            if img.has_attr('src'):
                src = img['src']
                if isinstance(src, str) and ('http' in src or src.startswith('//')):
                    if src.startswith('//'):
                        return f'https:{src}'
                    return src

            # Try data-src (lazy loading)
            if img.has_attr('data-src'):
                data_src = img['data-src']
                if isinstance(data_src, str) and ('http' in data_src or data_src.startswith('//')):
                    if data_src.startswith('//'):
                        return f'https:{data_src}'
                    return data_src

        # Try any img tag in the card
        img = card.find('img')
        if isinstance(img, Tag):
            if img.has_attr('src'):
                src = img['src']
                if isinstance(src, str) and ('http' in src or src.startswith('//')):
                    if src.startswith('//'):
                        return f'https:{src}'
                    return src

        return None
