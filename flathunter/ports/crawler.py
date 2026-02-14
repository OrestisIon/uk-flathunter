"""Crawler port interface"""
import re
from typing import Protocol, List, Dict, Optional

class CrawlerPort(Protocol):
    """Interface that all crawlers must implement"""
    URL_PATTERN: re.Pattern

    def crawl(self, url: str, max_pages: Optional[int] = None) -> List[Dict]:
        """Crawl a URL and return expose dicts"""
        ...

    def get_name(self) -> str:
        """Return crawler name"""
        ...

    def get_expose_details(self, expose: Dict) -> Dict:
        """Optionally fetch additional details"""
        ...

    def load_address(self, url: str) -> str:
        """Extract address from expose URL"""
        ...
