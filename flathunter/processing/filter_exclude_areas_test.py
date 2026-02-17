# pylint: disable=missing-docstring
import unittest

from flathunter.processing.filter import ExcludeAreasFilter, Filter
from flathunter.testing.config import StringConfig


def _expose(address):
    return {"address": address, "title": "Test", "price": "£1500", "id": "1"}


class ExcludeAreasFilterTest(unittest.TestCase):
    """Unit tests for ExcludeAreasFilter"""

    # --- name matching ---

    def test_excludes_matching_name(self):
        f = ExcludeAreasFilter(["Peckham"], [])
        self.assertFalse(f.is_interesting(_expose("10 Peckham High Street, SE15 5AB")))

    def test_name_match_is_case_insensitive(self):
        f = ExcludeAreasFilter(["peckham"], [])
        self.assertFalse(f.is_interesting(_expose("10 PECKHAM High Street")))

    def test_name_match_is_substring(self):
        f = ExcludeAreasFilter(["elephant and castle"], [])
        self.assertFalse(f.is_interesting(_expose("Flat 3, Elephant and Castle, SE1")))

    def test_allows_non_matching_name(self):
        f = ExcludeAreasFilter(["Peckham"], [])
        self.assertTrue(f.is_interesting(_expose("5 Baker Street, W1U 6XE")))

    def test_empty_name_list_excludes_nothing(self):
        f = ExcludeAreasFilter([], [])
        self.assertTrue(f.is_interesting(_expose("10 Peckham Road")))

    # --- postcode matching ---

    def test_excludes_matching_postcode(self):
        f = ExcludeAreasFilter([], ["SE1"])
        self.assertFalse(f.is_interesting(_expose("1 London Road, SE1 7PB")))

    def test_postcode_match_is_case_insensitive(self):
        f = ExcludeAreasFilter([], ["se1"])
        self.assertFalse(f.is_interesting(_expose("1 London Road, SE1 7PB")))

    def test_postcode_match_uses_word_boundary(self):
        # SE1 should not match SE15
        f = ExcludeAreasFilter([], ["SE1"])
        self.assertTrue(f.is_interesting(_expose("10 Peckham High Street, SE15 5AB")))

    def test_postcode_sw8_excluded(self):
        f = ExcludeAreasFilter([], ["SW8"])
        self.assertFalse(f.is_interesting(_expose("Flat 2, Vauxhall, SW8 1RG")))

    def test_allows_non_matching_postcode(self):
        f = ExcludeAreasFilter([], ["SE1"])
        self.assertTrue(f.is_interesting(_expose("5 Baker Street, W1U 6XE")))

    # --- combined name + postcode ---

    def test_excludes_when_name_matches_but_postcode_does_not(self):
        f = ExcludeAreasFilter(["Peckham"], ["SE1"])
        self.assertFalse(f.is_interesting(_expose("20 Peckham Rye, SE22 9ET")))

    def test_excludes_when_postcode_matches_but_name_does_not(self):
        f = ExcludeAreasFilter(["Peckham"], ["SE1"])
        self.assertFalse(f.is_interesting(_expose("Waterloo Road, SE1 8SW")))

    def test_allows_when_neither_name_nor_postcode_match(self):
        f = ExcludeAreasFilter(["Peckham"], ["SE1"])
        self.assertTrue(f.is_interesting(_expose("5 Baker Street, W1U 6XE")))

    def test_missing_address_key_does_not_raise(self):
        f = ExcludeAreasFilter(["Peckham"], ["SE1"])
        self.assertTrue(f.is_interesting({"title": "No address", "price": "£1000", "id": "2"}))

    def test_none_address_does_not_raise(self):
        f = ExcludeAreasFilter(["Peckham"], ["SE1"])
        self.assertTrue(f.is_interesting({"address": None, "title": "Test", "price": "£1000", "id": "3"}))

    # --- Filter.filter() integration ---

    def test_filters_list_of_exposes(self):
        f = Filter([ExcludeAreasFilter(["Peckham"], ["SE1"])])
        exposes = [
            _expose("10 Peckham Road, SE15"),          # excluded by name
            _expose("Waterloo Road, SE1 8SW"),         # excluded by postcode
            _expose("5 Baker Street, W1U 6XE"),        # allowed
            _expose("Oxford Street, W1D 2HG"),         # allowed
        ]
        results = list(f.filter(exposes))
        self.assertEqual(len(results), 2)
        self.assertIn(_expose("5 Baker Street, W1U 6XE"), results)
        self.assertIn(_expose("Oxford Street, W1D 2HG"), results)


class ExcludeAreasConfigTest(unittest.TestCase):
    """Integration tests: exclude_areas in config flows through to FilterBuilder"""

    EXCLUDE_AREAS_CONFIG = """
urls:
  - https://www.zoopla.co.uk/to-rent/property/london/

exclude_areas:
  names:
    - "Elephant and Castle"
    - "Peckham"
  postcodes:
    - "SE1"
    - "SW8"
"""

    NO_EXCLUDE_CONFIG = """
urls:
  - https://www.zoopla.co.uk/to-rent/property/london/
"""

    def test_config_reads_exclude_names(self):
        config = StringConfig(string=self.EXCLUDE_AREAS_CONFIG)
        self.assertEqual(config.exclude_area_names(), ["Elephant and Castle", "Peckham"])

    def test_config_reads_exclude_postcodes(self):
        config = StringConfig(string=self.EXCLUDE_AREAS_CONFIG)
        self.assertEqual(config.exclude_area_postcodes(), ["SE1", "SW8"])

    def test_config_returns_empty_when_not_set(self):
        config = StringConfig(string=self.NO_EXCLUDE_CONFIG)
        self.assertEqual(config.exclude_area_names(), [])
        self.assertEqual(config.exclude_area_postcodes(), [])

    def test_filter_builder_adds_exclude_areas_filter(self):
        config = StringConfig(string=self.EXCLUDE_AREAS_CONFIG)
        built_filter = config.get_filter()
        filter_types = [type(f).__name__ for f in built_filter.filters]
        self.assertIn("ExcludeAreasFilter", filter_types)

    def test_filter_builder_skips_exclude_areas_filter_when_not_configured(self):
        config = StringConfig(string=self.NO_EXCLUDE_CONFIG)
        built_filter = config.get_filter()
        filter_types = [type(f).__name__ for f in built_filter.filters]
        self.assertNotIn("ExcludeAreasFilter", filter_types)

    def test_end_to_end_excludes_forbidden_address(self):
        config = StringConfig(string=self.EXCLUDE_AREAS_CONFIG)
        built_filter = config.get_filter()
        self.assertFalse(built_filter.is_interesting_expose(
            _expose("Flat 1, Elephant and Castle, SE1 6TE")
        ))

    def test_end_to_end_allows_permitted_address(self):
        config = StringConfig(string=self.EXCLUDE_AREAS_CONFIG)
        built_filter = config.get_filter()
        self.assertTrue(built_filter.is_interesting_expose(
            _expose("5 Baker Street, W1U 6XE")
        ))
