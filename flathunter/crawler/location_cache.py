"""Cache for Rightmove location identifiers resolved via the typeahead API"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional
import requests

from flathunter.core.logging import logger

CACHE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "data", "rightmove_locations.json"
)
TYPEAHEAD_BASE = "https://www.rightmove.co.uk/typeAhead/uknostreet"
VERIFY_INTERVAL_DAYS = 7


class RightmoveLocationCache:
    """Resolves area names to Rightmove locationIdentifier strings, caching results locally."""

    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = os.path.abspath(cache_file)
        self._cache: Optional[dict] = None

    def _load(self) -> dict:
        if self._cache is not None:
            return self._cache
        if os.path.exists(self.cache_file):
            with open(self.cache_file, encoding="utf-8") as f:
                self._cache = json.load(f)
        else:
            self._cache = {}
        return self._cache

    def _save(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, indent=2)

    def _channel_switch(self, search_type: str) -> str:
        return "RENT" if search_type == "rent" else "BUY"

    @staticmethod
    def _tokenize(area_name: str) -> str:
        """Convert an area name to Rightmove's 2-char-chunk path format.

        e.g. "Fitzrovia" → "FI/TZ/RO/VI/A"
        """
        upper = area_name.upper().replace(" ", "")
        return "/".join(upper[i:i+2] for i in range(0, len(upper), 2))

    def _fetch_identifier(self, area_name: str, search_type: str) -> Optional[str]:
        """Call Rightmove typeahead API and return locationIdentifier, or None on failure."""
        try:
            token_path = self._tokenize(area_name)
            url = f"{TYPEAHEAD_BASE}/{token_path}/"
            resp = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            resp.raise_for_status()
            data = resp.json()
            locations = data.get("typeAheadLocations", [])
            if not locations:
                logger.warning("Rightmove typeahead: no results for area '%s'", area_name)
                return None
            identifier = locations[0].get("locationIdentifier")
            return identifier
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Rightmove typeahead API failed for '%s': %s", area_name, exc)
            return None

    def resolve(self, area_name: str, search_type: str = "rent") -> Optional[str]:
        """Return cached locationIdentifier for area_name, fetching from API if not cached."""
        cache = self._load()
        if area_name in cache:
            return cache[area_name]["identifier"]

        identifier = self._fetch_identifier(area_name, search_type)
        if identifier is None:
            return None

        now = datetime.utcnow().isoformat()
        cache[area_name] = {
            "identifier": identifier,
            "cached_at": now,
            "verified_at": now,
        }
        self._cache = cache
        self._save()
        logger.info("Rightmove location cached: '%s' → %s", area_name, identifier)
        return identifier

    def verify_all(self, search_type: str = "rent") -> dict:
        """Re-verify stale cache entries (older than VERIFY_INTERVAL_DAYS).

        Returns a dict mapping area names to 'ok', 'updated', or 'failed'.
        """
        cache = self._load()
        results = {}
        cutoff = datetime.utcnow() - timedelta(days=VERIFY_INTERVAL_DAYS)
        changed = False

        for area_name, entry in cache.items():
            verified_at_str = entry.get("verified_at")
            if verified_at_str:
                verified_at = datetime.fromisoformat(verified_at_str)
                if verified_at > cutoff:
                    results[area_name] = "ok"
                    continue

            identifier = self._fetch_identifier(area_name, search_type)
            if identifier is None:
                results[area_name] = "failed"
                continue

            now = datetime.utcnow().isoformat()
            if identifier != entry["identifier"]:
                logger.warning(
                    "Rightmove location changed: '%s' was %s, now %s",
                    area_name, entry["identifier"], identifier
                )
                entry["identifier"] = identifier
                results[area_name] = "updated"
            else:
                results[area_name] = "ok"
            entry["verified_at"] = now
            changed = True

        if changed:
            self._save()
        return results
