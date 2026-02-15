"""Core domain models"""
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

@dataclass
class Expose:
    """Property listing domain model"""
    id: int | str
    url: str
    title: str
    price: str
    crawler: str
    size: str = ""
    rooms: str = ""
    address: str = ""
    image: Optional[str] = None
    images: Optional[List[str]] = None
    durations: Optional[str] = None
    created_at: Optional[str] = None

    # AI/LLM enrichment fields
    ai_score: Optional[float] = None
    ai_reasoning: Optional[str] = None
    ai_highlights: Optional[List[str]] = None
    ai_warnings: Optional[List[str]] = None
    ai_confidence: Optional[str] = None
    ai_red_flags: Optional[List[str]] = None
    extracted_features: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for backward compatibility"""
        result = asdict(self)
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expose':
        """Create from dict - filters unknown fields"""
        known_fields = {k: v for k, v in data.items()
                       if k in cls.__dataclass_fields__}
        return cls(**known_fields)
