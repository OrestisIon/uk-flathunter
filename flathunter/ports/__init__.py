"""Port interfaces for dependency inversion"""
from .crawler import CrawlerPort
from .notifier import NotifierPort
from .repository import RepositoryPort

__all__ = ['CrawlerPort', 'NotifierPort', 'RepositoryPort']
