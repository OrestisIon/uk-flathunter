"""Factory for creating notifier instances"""
from typing import Dict, List, Type
from flathunter.core.abstract_notifier import Notifier
from flathunter.core.logging import logger

class NotifierFactory:
    """Factory for managing notifier instances"""

    def __init__(self):
        self._registry: Dict[str, Type[Notifier]] = {}

    def register(self, name: str, notifier_class: Type[Notifier]):
        """Register a notifier class"""
        self._registry[name] = notifier_class
        logger.debug(f"Registered notifier: {name}")

    def create_enabled(self, enabled_names: List[str], config) -> List[Notifier]:
        """Create instances of enabled notifiers"""
        notifiers = []
        for name in enabled_names:
            if name in self._registry:
                notifiers.append(self._registry[name](config))
            else:
                logger.warning(f"Unknown notifier: {name}")
        return notifiers

def get_default_notifier_factory() -> NotifierFactory:
    """Create factory with all built-in notifiers registered"""
    from flathunter.notifiers import (
        SenderTelegram,
        SenderSlack,
        SenderMattermost,
        SenderApprise,
        SenderFile
    )

    factory = NotifierFactory()
    factory.register('telegram', SenderTelegram)
    factory.register('slack', SenderSlack)
    factory.register('mattermost', SenderMattermost)
    factory.register('apprise', SenderApprise)
    factory.register('file', SenderFile)

    return factory
