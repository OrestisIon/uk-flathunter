"""Build Rightmove search URLs from structured search configuration"""
from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import urlencode

from flathunter.core.logging import logger
from flathunter.crawler.location_cache import RightmoveLocationCache

RENT_BASE = "https://www.rightmove.co.uk/property-to-rent/find.html"
BUY_BASE = "https://www.rightmove.co.uk/property-for-sale/find.html"

ADDED_SINCE_MAP = {
    "last_24_hours": "last24Hours",
    "last_3_days": "last3Days",
    "last_7_days": "last7Days",
    "last_14_days": "last14Days",
}

# How often (in days) to run verify_all on the location cache
VERIFY_INTERVAL_DAYS = 7
_last_verified: Optional[datetime] = None


class RightmoveUrlBuilder:
    """Builds Rightmove search URLs from structured filter configs."""

    def __init__(self):
        self.cache = RightmoveLocationCache()

    def _maybe_verify(self, search_type: str):
        global _last_verified  # pylint: disable=global-statement
        now = datetime.utcnow()
        if _last_verified is None or now - _last_verified > timedelta(days=VERIFY_INTERVAL_DAYS):
            logger.info("Running Rightmove location cache verification...")
            results = self.cache.verify_all(search_type)
            logger.info("Location cache verification results: %s", results)
            _last_verified = now

    def build(self, area: str, search_type: str, filters: dict) -> Optional[str]:
        """Build a single Rightmove search URL for the given area and filters.

        Returns None if location resolution fails and no fallback is possible.
        """
        self._maybe_verify(search_type)

        base_url = RENT_BASE if search_type == "rent" else BUY_BASE

        identifier = self.cache.resolve(area, search_type)
        if identifier is None:
            logger.warning(
                "No Rightmove location identifier for '%s'; skipping URL build", area
            )
            return None

        params = {
            "searchLocation": area,
            "useLocationIdentifier": "true",
            "locationIdentifier": identifier,
        }

        if filters.get("price_min") is not None:
            params["minPrice"] = filters["price_min"]
        if filters.get("price_max") is not None:
            params["maxPrice"] = filters["price_max"]
        if filters.get("bedrooms_min") is not None:
            params["minBedrooms"] = filters["bedrooms_min"]
        if filters.get("bedrooms_max") is not None:
            params["maxBedrooms"] = filters["bedrooms_max"]
        if filters.get("radius") is not None:
            params["radius"] = filters["radius"]

        added_since = filters.get("added_since")
        if added_since and added_since in ADDED_SINCE_MAP:
            params["added_to_site"] = ADDED_SINCE_MAP[added_since]

        dont_show = []
        if filters.get("exclude_shared"):
            dont_show.append("sharedOwnership")
        if filters.get("exclude_retirement"):
            dont_show.append("retirement")
        if filters.get("exclude_student"):
            dont_show.append("student")
        if dont_show:
            params["dontShow"] = ",".join(dont_show)

        url = f"{base_url}?{urlencode(params)}"
        logger.info("Generated Rightmove URL for '%s': %s", area, url)
        return url

    def build_all(self, search: dict) -> List[str]:
        """Build URLs for all areas in a search config entry."""
        search_type = search.get("type", "rent")
        filters = search.get("filters", {})
        urls = []
        for area in search.get("areas", []):
            url = self.build(area, search_type, filters)
            if url:
                urls.append(url)
        return urls
