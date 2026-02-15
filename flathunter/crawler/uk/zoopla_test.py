# pylint: disable=missing-docstring
import pytest

from flathunter.crawler.uk.zoopla import Zoopla
from flathunter.testing.config import StringConfig

DUMMY_CONFIG = """
urls:
  - https://www.zoopla.co.uk/to-rent/property/london/
    """

TEST_URL = 'https://www.zoopla.co.uk/to-rent/property/london/?beds_min=2&price_frequency=per_month&price_max=2000&q=London&results_sort=newest_listings&search_source=to-rent'

@pytest.fixture
def crawler():
    return Zoopla(StringConfig(string=DUMMY_CONFIG))

def test_url_pattern_matches():
    """Test that the Zoopla URL pattern correctly identifies Zoopla URLs"""
    pattern = Zoopla.URL_PATTERN
    assert pattern.search('https://www.zoopla.co.uk/to-rent/property/london/') is not None
    assert pattern.search('https://www.zoopla.co.uk/to-rent/details/12345/') is not None
    assert pattern.search('https://www.rightmove.co.uk/property-to-rent/') is None
    assert pattern.search('https://www.immobilienscout24.de/') is None

def test_crawler_initialization(crawler):
    """Test that the crawler can be instantiated"""
    assert crawler is not None
    assert crawler.get_name() == 'Zoopla'

def test_get_page(crawler):
    """Test that we can fetch a page from Zoopla"""
    soup = crawler.get_page(TEST_URL)
    assert soup is not None

def test_extract_data(crawler):
    """Test that we can extract listing data from a Zoopla search page"""
    soup = crawler.get_page(TEST_URL)
    assert soup is not None
    entries = crawler.extract_data(soup)
    assert entries is not None
    assert len(entries) > 0, "Should have at least one entry"

def test_entry_has_required_fields(crawler):
    """Test that extracted entries have all required fields"""
    soup = crawler.get_page(TEST_URL)
    entries = crawler.extract_data(soup)
    assert len(entries) > 0

    entry = entries[0]
    # Required fields
    assert 'id' in entry
    assert entry['id'] > 0, "Id should be parsed as positive integer"

    assert 'url' in entry
    assert entry['url'].startswith("https://www.zoopla.co.uk"), "URL should be a Zoopla link"

    assert 'title' in entry
    assert entry['title'], "Title should not be empty"

    assert 'price' in entry
    assert entry['price'], "Price should not be empty"

    assert 'size' in entry
    # Size might be optional on some listings

    assert 'rooms' in entry
    assert entry['rooms'], "Rooms should not be empty"

    assert 'address' in entry
    assert entry['address'], "Address should not be empty"

    assert 'crawler' in entry
    assert entry['crawler'] == 'Zoopla', "Crawler should be 'Zoopla'"

def test_entry_image_field(crawler):
    """Test that entries have image field (even if it might be None)"""
    soup = crawler.get_page(TEST_URL)
    entries = crawler.extract_data(soup)
    assert len(entries) > 0

    entry = entries[0]
    assert 'image' in entry
    # Image might be None or a URL string

def test_multiple_entries(crawler):
    """Test that we get multiple entries from a search page"""
    soup = crawler.get_page(TEST_URL)
    entries = crawler.extract_data(soup)
    assert len(entries) > 5, "Should have multiple entries from search page"

    # Check that entries have unique IDs
    ids = [entry['id'] for entry in entries]
    assert len(ids) == len(set(ids)), "Entry IDs should be unique"

def test_price_format(crawler):
    """Test that prices are in expected format"""
    soup = crawler.get_page(TEST_URL)
    entries = crawler.extract_data(soup)
    assert len(entries) > 0

    # UK rental prices typically shown as "£1,500 pcm" or similar
    entry = entries[0]
    assert '£' in entry['price'] or 'pcm' in entry['price'].lower(), \
        "Price should contain UK currency symbol or rental period"
