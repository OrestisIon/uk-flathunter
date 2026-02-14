"""Notifier port interface"""
from typing import Protocol

class NotifierPort(Protocol):
    """Interface for notification services"""

    def notify(self, message: str) -> None:
        """Send a text notification"""
        ...
