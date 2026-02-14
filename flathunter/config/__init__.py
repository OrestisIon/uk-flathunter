"""Configuration module"""

# Import with graceful fallbacks for optional dependencies
__all__ = []

try:
    from .settings import Settings
    __all__.append('Settings')
except ImportError:
    Settings = None

try:
    from .crawler_factory import CrawlerFactory, get_default_crawler_factory
    __all__.extend(['CrawlerFactory', 'get_default_crawler_factory'])
except ImportError:
    CrawlerFactory = None
    get_default_crawler_factory = None

try:
    from .notifier_factory import NotifierFactory, get_default_notifier_factory
    __all__.extend(['NotifierFactory', 'get_default_notifier_factory'])
except ImportError:
    NotifierFactory = None
    get_default_notifier_factory = None

# Backward compatibility - allow importing legacy Config from here
try:
    from flathunter.core.config import Config as LegacyConfig
    __all__.append('LegacyConfig')
except ImportError:
    LegacyConfig = None
