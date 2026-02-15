# pylint: disable=missing-docstring
import unittest
import tempfile
import os.path
import os
from flathunter.core.config import Config
from flathunter.testing.config import StringConfig

class ConfigTest(unittest.TestCase):

    DUMMY_CONFIG = """
urls:
  - https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc
    """

    EMPTY_FILTERS_CONFIG = """
urls:
  - https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc

filters:

"""

    LEGACY_FILTERS_CONFIG = """
urls:
  - https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc

excluded_titles:
  - Title
  - Another
"""

    FILTERS_CONFIG = """
urls:
  - https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc

filters:
    excluded_titles:
        - fish
    min_size: 30
    max_size: 100
    min_price: 500
    max_price: 1500
    min_rooms: 2
    max_rooms: 5
"""

    def test_loads_config(self):
        created = False
        if not os.path.isfile("config.yaml"):
            config_file = open("config.yaml", "w")
            config_file.write(self.DUMMY_CONFIG)
            config_file.flush()
            config_file.close()
            created = True
        config = Config("config.yaml")
        self.assertTrue(len(config.get('urls') or []) > 0, "Expected URLs in config file")
        if created:
            os.remove("config.yaml")

    def test_loads_config_at_file(self):
        with tempfile.NamedTemporaryFile(mode='w+') as temp:
            temp.write(self.DUMMY_CONFIG)
            temp.flush()
            config = Config(temp.name)
        self.assertTrue(len(config.get('urls') or []) > 0, "Expected URLs in config file")

    def test_loads_config_from_string(self):
        config = StringConfig(string=self.EMPTY_FILTERS_CONFIG)
        self.assertIsNotNone(config)
        my_filter = config.get_filter()
        self.assertIsNotNone(my_filter)

    def test_loads_legacy_config_from_string(self):
        config = StringConfig(string=self.LEGACY_FILTERS_CONFIG)
        self.assertIsNotNone(config)
        my_filter = config.get_filter()
        self.assertIsNotNone(my_filter)
        self.assertTrue(len(my_filter.filters) > 0)

    def test_loads_filters_config_from_string(self):
        config = StringConfig(string=self.FILTERS_CONFIG)
        self.assertIsNotNone(config)
        my_filter = config.get_filter()
        self.assertIsNotNone(my_filter)

    def test_defaults_fields(self):
        config = StringConfig(string=self.FILTERS_CONFIG)
        self.assertIsNotNone(config)
        self.assertEqual(config.database_location(),
                         os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/.."))

    def test_init_searchers_includes_uk_crawlers(self):
        """Test that UK crawlers (Zoopla, Rightmove) are initialized"""
        config = StringConfig(string=self.DUMMY_CONFIG)
        config.init_searchers()

        searchers = config.searchers()
        searcher_names = [searcher.get_name() for searcher in searchers]

        # Check UK crawlers are present
        self.assertIn('Zoopla', searcher_names, "Zoopla crawler should be initialized")
        self.assertIn('Rightmove', searcher_names, "Rightmove crawler should be initialized")

        # Check existing German/Italian crawlers are still there
        self.assertIn('Immobilienscout', searcher_names)
        self.assertIn('WgGesucht', searcher_names)
        self.assertIn('Kleinanzeigen', searcher_names)

    def test_searchers_route_to_correct_crawler(self):
        """Test that URLs are routed to the correct crawler based on URL pattern"""
        config = StringConfig(string=self.DUMMY_CONFIG)
        config.init_searchers()

        test_cases = [
            ('https://www.zoopla.co.uk/to-rent/property/london/', 'Zoopla'),
            ('https://www.rightmove.co.uk/property-to-rent/find.html', 'Rightmove'),
            ('https://www.immobilienscout24.de/', 'Immobilienscout'),
            ('https://www.wg-gesucht.de/', 'WgGesucht'),
        ]

        for url, expected_crawler in test_cases:
            matching_crawlers = [
                searcher.get_name()
                for searcher in config.searchers()
                if searcher.URL_PATTERN.search(url)
            ]
            self.assertIn(expected_crawler, matching_crawlers,
                f"URL {url} should be handled by {expected_crawler} crawler")

    def test_uk_config_with_zoopla_urls(self):
        """Test configuration with UK Zoopla URLs"""
        uk_config = """
urls:
  - https://www.zoopla.co.uk/to-rent/property/london/?beds_min=2&price_max=2000
notifiers:
  - telegram
telegram:
  bot_token: dummy_token
  receiver_ids:
    - 12345
        """

        config = StringConfig(string=uk_config)
        config.init_searchers()

        self.assertEqual(len(config.target_urls()), 1)
        self.assertIn('zoopla.co.uk', config.target_urls()[0])

        searcher_names = [s.get_name() for s in config.searchers()]
        self.assertIn('Zoopla', searcher_names)

    def test_uk_config_with_rightmove_urls(self):
        """Test configuration with UK Rightmove URLs"""
        uk_config = """
urls:
  - https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION%5E93917
notifiers:
  - telegram
telegram:
  bot_token: dummy_token
  receiver_ids:
    - 12345
        """

        config = StringConfig(string=uk_config)
        config.init_searchers()

        self.assertEqual(len(config.target_urls()), 1)
        self.assertIn('rightmove.co.uk', config.target_urls()[0])

        searcher_names = [s.get_name() for s in config.searchers()]
        self.assertIn('Rightmove', searcher_names)

    def test_mixed_country_config(self):
        """Test configuration with both German and UK URLs"""
        mixed_config = """
urls:
  - https://www.immobilienscout24.de/Suche/
  - https://www.zoopla.co.uk/to-rent/property/london/
  - https://www.rightmove.co.uk/property-to-rent/find.html
notifiers:
  - telegram
telegram:
  bot_token: dummy_token
  receiver_ids:
    - 12345
        """

        config = StringConfig(string=mixed_config)
        config.init_searchers()

        self.assertEqual(len(config.target_urls()), 3)

        # All crawlers should be initialized
        searcher_names = [s.get_name() for s in config.searchers()]
        self.assertIn('Immobilienscout', searcher_names)
        self.assertIn('Zoopla', searcher_names)
        self.assertIn('Rightmove', searcher_names)
