"""Factory for creating crawler instances"""
import re
from typing import Dict, List, Type, Optional
from flathunter.core.abstract_crawler import Crawler
from flathunter.core.logging import logger

class CrawlerFactory:
    """Factory for managing and creating crawler instances"""

    def __init__(self):
        self._registry: Dict[re.Pattern, Type[Crawler]] = {}

    def register(self, pattern: re.Pattern, crawler_class: Type[Crawler]):
        """Register a crawler class with URL pattern"""
        self._registry[pattern] = crawler_class
        logger.debug("Registered crawler: %s for pattern %s",
                     crawler_class.__name__, pattern.pattern)

    def create_all(self, config) -> List[Crawler]:
        """Create all registered crawler instances"""
        return [crawler_cls(config) for crawler_cls in self._registry.values()]

    def get_crawler_for_url(self, url: str, config) -> Optional[Crawler]:
        """Get appropriate crawler instance for URL"""
        for pattern, crawler_cls in self._registry.items():
            if pattern.search(url):
                return crawler_cls(config)
        return None

def get_default_crawler_factory() -> CrawlerFactory:
    """Create factory with all built-in crawlers registered"""
    from flathunter.crawler.germany.immobilienscout import Immobilienscout
    from flathunter.crawler.germany.wggesucht import WgGesucht
    from flathunter.crawler.germany.kleinanzeigen import Kleinanzeigen
    from flathunter.crawler.germany.immowelt import Immowelt
    from flathunter.crawler.germany.vrmimmo import VrmImmo
    from flathunter.crawler.uk.zoopla import Zoopla
    from flathunter.crawler.uk.rightmove import Rightmove
    from flathunter.crawler.italy.immobiliare import Immobiliare
    from flathunter.crawler.italy.subito import Subito
    from flathunter.crawler.spain.idealista import Idealista

    factory = CrawlerFactory()

    # Register all crawlers with their patterns
    factory.register(re.compile(r'https://www\.immobilienscout24\.de'), Immobilienscout)
    factory.register(re.compile(r'https://www\.wg-gesucht\.de'), WgGesucht)
    factory.register(re.compile(r'https://www\.kleinanzeigen\.de'), Kleinanzeigen)
    factory.register(re.compile(r'https://www\.immowelt\.de'), Immowelt)
    factory.register(re.compile(r'https://www\.vrm-immo\.de'), VrmImmo)
    factory.register(re.compile(r'https://www\.zoopla\.co\.uk'), Zoopla)
    factory.register(re.compile(r'https://www\.rightmove\.co\.uk'), Rightmove)
    factory.register(re.compile(r'https://www\.immobiliare\.it'), Immobiliare)
    factory.register(re.compile(r'https://www\.subito\.it'), Subito)
    factory.register(re.compile(r'https://www\.idealista\.(it|com|es)'), Idealista)

    return factory
