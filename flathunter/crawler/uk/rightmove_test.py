import pytest

from flathunter.crawler.uk.rightmove import Rightmove
from flathunter.testing.config import StringConfig

DUMMY_CONFIG = """
urls:
  - https://www.rightmove.co.uk/property-to-rent/find.html
    """

TEST_URL = 'https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION%5E93917&minBedrooms=2&maxPrice=2000&propertyTypes=&includeLetAgreed=false&mustHave=&dontShow=&furnishTypes=&keywords='

@pytest.fixture
def crawler():
    return Rightmove(StringConfig(string=DUMMY_CONFIG))

def test_url_pattern_matches():
    """Test that the Rightmove URL pattern correctly identifies Rightmove URLs"""
    pattern = Rightmove.URL_PATTERN
    assert pattern.search('https://www.rightmove.co.uk/property-to-rent/find.html') is not None
    assert pattern.search('https://www.rightmove.co.uk/properties/12345') is not None
    assert pattern.search('https://www.rightmove.co.uk/property-for-sale/') is not None
    assert pattern.search('https://www.zoopla.co.uk/to-rent/') is None
    assert pattern.search('https://www.immobilienscout24.de/') is None

def test_crawler_initialization(crawler):
    """Test that the crawler can be instantiated"""
    assert crawler is not None
    assert crawler.get_name() == 'Rightmove'

def test_get_page(crawler):
    """Test that we can fetch a page from Rightmove"""
    soup = crawler.get_page(TEST_URL)
    assert soup is not None

def test_extract_data(crawler):
    """Test that we can extract listing data from a Rightmove search page"""
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
    assert entry['url'].startswith("https://www.rightmove.co.uk"), "URL should be a Rightmove link"

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
    assert entry['crawler'] == 'Rightmove', "Crawler should be 'Rightmove'"

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

def test_property_type_in_title(crawler):
    """Test that property types are captured in title"""
    soup = crawler.get_page(TEST_URL)
    entries = crawler.extract_data(soup)
    assert len(entries) > 0

    # Rightmove typically includes property type in title
    # e.g., "2 bedroom flat to rent" or "3 bedroom house"
    entry = entries[0]
    title_lower = entry['title'].lower()
    assert any(word in title_lower for word in ['flat', 'house', 'apartment', 'bedroom']), \
        "Title should contain property type or bedroom information"
