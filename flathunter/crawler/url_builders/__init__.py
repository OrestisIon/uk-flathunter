"""URL builder package for structured search configuration"""
from typing import List

from flathunter.core.logging import logger


def _resolve_areas(search: dict) -> dict:
    """Return a copy of *search* with zones expanded and merged into areas.

    If a search specifies ``zones: [1, 2]``, those TfL zones are expanded to
    postcode districts and prepended to any explicit ``areas:`` entries.
    Duplicates are removed while preserving order.
    """
    zones = search.get("zones", [])
    explicit_areas = search.get("areas", [])

    if not zones:
        return search

    from flathunter.crawler.url_builders.london_zones import expand_zones  # pylint: disable=import-outside-toplevel
    zone_areas = expand_zones(zones)

    # Merge: zone-derived areas first, then any explicit areas not already present
    seen = set(zone_areas)
    merged = list(zone_areas)
    for area in explicit_areas:
        if area not in seen:
            seen.add(area)
            merged.append(area)

    logger.info(
        "Search '%s': zones %s expanded to %d area(s)",
        search.get("name", "<unnamed>"), zones, len(merged)
    )
    return {**search, "areas": merged}


def build_urls_from_searches(searches: list) -> List[str]:
    """Build a flat list of crawlable URLs from a structured searches config block.

    Each search entry may target multiple sites and areas; this produces one URL
    per (site, area) combination. If ``zones:`` is present, TfL zones are
    expanded to London postcode districts and merged with any explicit ``areas:``.
    """
    from flathunter.crawler.url_builders.rightmove import RightmoveUrlBuilder  # pylint: disable=import-outside-toplevel
    from flathunter.crawler.url_builders.zoopla import ZooplaUrlBuilder  # pylint: disable=import-outside-toplevel

    builders = {
        "rightmove": RightmoveUrlBuilder(),
        "zoopla": ZooplaUrlBuilder(),
    }

    all_urls: List[str] = []
    for search in searches:
        name = search.get("name", "<unnamed>")
        resolved = _resolve_areas(search)
        sites = resolved.get("sites", [])
        for site in sites:
            builder = builders.get(site)
            if builder is None:
                logger.warning("Unknown site '%s' in search '%s'; skipping", site, name)
                continue
            urls = builder.build_all(resolved)
            logger.info("Search '%s' / %s → %d URL(s)", name, site, len(urls))
            all_urls.extend(urls)

    return all_urls
