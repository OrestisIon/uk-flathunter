"""Build Zoopla search URLs from structured search configuration"""
from typing import List
from urllib.parse import urlencode, quote

from flathunter.core.logging import logger

RENT_BASE = "https://www.zoopla.co.uk/to-rent/property"
BUY_BASE = "https://www.zoopla.co.uk/for-sale/property"

ADDED_SINCE_MAP = {
    "last_24_hours": "today",
    "last_3_days": "last_3_days",
    "last_7_days": "last_week",
    "last_14_days": "last_2_weeks",
}


class ZooplaUrlBuilder:
    """Builds Zoopla search URLs from structured filter configs."""

    def build(self, area: str, search_type: str, filters: dict) -> str:
        """Build a single Zoopla search URL for the given area and filters."""
        base_url = RENT_BASE if search_type == "rent" else BUY_BASE
        area_slug = quote(area, safe="")

        params = {"q": area, "search_source": "to-rent" if search_type == "rent" else "for-sale"}

        if filters.get("price_min") is not None:
            params["price_min"] = filters["price_min"]
        if filters.get("price_max") is not None:
            params["price_max"] = filters["price_max"]
        if search_type == "rent":
            params["price_frequency"] = "per_month"

        if filters.get("bedrooms_min") is not None:
            params["beds_min"] = filters["bedrooms_min"]
        if filters.get("bedrooms_max") is not None:
            params["beds_max"] = filters["bedrooms_max"]

        if filters.get("radius") is not None:
            params["radius"] = filters["radius"]

        added_since = filters.get("added_since")
        if added_since and added_since in ADDED_SINCE_MAP:
            params["added"] = ADDED_SINCE_MAP[added_since]

        if filters.get("exclude_shared") is True:
            params["is_shared_accommodation"] = "false"
        if filters.get("exclude_retirement") is True:
            params["is_retirement_home"] = "false"
        if filters.get("exclude_student") is True:
            params["is_student_accommodation"] = "false"

        url = f"{base_url}/{area_slug}/?{urlencode(params)}"
        logger.info("Generated Zoopla URL for '%s': %s", area, url)
        return url

    def build_all(self, search: dict) -> List[str]:
        """Build URLs for all areas in a search config entry."""
        search_type = search.get("type", "rent")
        filters = search.get("filters", {})
        urls = []
        for area in search.get("areas", []):
            urls.append(self.build(area, search_type, filters))
        return urls
