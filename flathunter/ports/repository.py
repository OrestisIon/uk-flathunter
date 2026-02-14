"""Repository port interface"""
from typing import Protocol, List, Dict, Optional

class RepositoryPort(Protocol):
    """Interface for expose persistence"""

    def is_processed(self, expose_id: int | str) -> bool:
        """Check if expose already processed"""
        ...

    def mark_processed(self, expose_id: int | str) -> None:
        """Mark expose as processed"""
        ...

    def save_expose(self, expose: Dict) -> None:
        """Save expose to storage"""
        ...

    def get_recent_exposes(self, count: int) -> List[Dict]:
        """Get recently saved exposes"""
        ...
