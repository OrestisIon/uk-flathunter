# pylint: disable=missing-docstring
import unittest

from flathunter.crawler.url_builders.london_zones import expand_zones, TFL_ZONES
from flathunter.crawler.url_builders import _resolve_areas


class ExpandZonesTest(unittest.TestCase):

    def test_zone_1_returns_known_districts(self):
        areas = expand_zones([1])
        self.assertIn("EC1", areas)
        self.assertIn("WC1", areas)
        self.assertIn("W1", areas)
        self.assertIn("SW1", areas)

    def test_zone_2_returns_known_districts(self):
        areas = expand_zones([2])
        self.assertIn("NW1", areas)   # Camden
        self.assertIn("W11", areas)   # Notting Hill
        self.assertIn("SW11", areas)  # Battersea
        self.assertIn("E14", areas)   # Canary Wharf

    def test_multiple_zones_merged(self):
        z1 = set(expand_zones([1]))
        z2 = set(expand_zones([2]))
        both = expand_zones([1, 2])
        self.assertEqual(set(both), z1 | z2)

    def test_no_duplicates_across_zones(self):
        areas = expand_zones([1, 2, 3, 4, 5])
        self.assertEqual(len(areas), len(set(areas)))

    def test_unknown_zone_returns_empty(self):
        self.assertEqual(expand_zones([99]), [])

    def test_empty_input_returns_empty(self):
        self.assertEqual(expand_zones([]), [])

    def test_all_zones_have_entries(self):
        for zone in [1, 2, 3, 4, 5]:
            self.assertGreater(len(TFL_ZONES[zone]), 0, f"Zone {zone} has no districts")

    def test_no_district_appears_in_two_zones(self):
        seen = {}
        for zone, districts in TFL_ZONES.items():
            for d in districts:
                self.assertNotIn(d, seen, f"{d} appears in both zone {seen.get(d)} and zone {zone}")
                seen[d] = zone


class ResolveAreasTest(unittest.TestCase):

    def test_no_zones_returns_search_unchanged(self):
        search = {"areas": ["Fitzrovia", "Marylebone"], "name": "test"}
        result = _resolve_areas(search)
        self.assertEqual(result["areas"], ["Fitzrovia", "Marylebone"])

    def test_zones_expanded_to_postcode_districts(self):
        search = {"zones": [1], "name": "test"}
        result = _resolve_areas(search)
        self.assertIn("EC1", result["areas"])
        self.assertIn("W1", result["areas"])

    def test_explicit_areas_appended_after_zone_areas(self):
        search = {"zones": [1], "areas": ["Canary Wharf"], "name": "test"}
        result = _resolve_areas(search)
        # Canary Wharf is not a postcode district, so it should be appended
        self.assertIn("Canary Wharf", result["areas"])
        # Zone 1 districts should come first
        self.assertIn("EC1", result["areas"])
        self.assertLess(result["areas"].index("EC1"), result["areas"].index("Canary Wharf"))

    def test_no_duplicates_when_area_already_in_zone(self):
        # EC1 is in Zone 1; adding it explicitly should not produce a duplicate
        search = {"zones": [1], "areas": ["EC1"], "name": "test"}
        result = _resolve_areas(search)
        self.assertEqual(result["areas"].count("EC1"), 1)

    def test_original_search_dict_not_mutated(self):
        search = {"zones": [1], "areas": ["Fitzrovia"], "name": "test"}
        _resolve_areas(search)
        self.assertEqual(search["areas"], ["Fitzrovia"])  # original unchanged

    def test_zones_key_preserved_in_result(self):
        search = {"zones": [2], "name": "test"}
        result = _resolve_areas(search)
        self.assertEqual(result["zones"], [2])
