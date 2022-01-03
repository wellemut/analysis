import os
import pytest
from pipelines import ScrapePipeline
from models import Website, Webpage

# Scrape max 5 pages per domain to speed up the testing
@pytest.fixture(autouse=True)
def limit_to_5_pages(mocker):
    mocker.patch.object(ScrapePipeline, "MAX_PAGES", 5)
    yield


@pytest.fixture(autouse=True)
def cache_scrapy_requests(mocker):
    # Custom scrapy settings to inject
    # These cache all scrapy requests and are an alternative to pytest VCR,
    # which does not work with twisted
    # See: https://github.com/kiwicom/pytest-recording/issues/50
    cache_settings = {
        "HTTPCACHE_ENABLED": True,
        # Never expire the cache
        "HTTPCACHE_EXPIRATION_SECS": 0,
        "HTTPCACHE_DIR": os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "scrapy-cache"
        ),
        "HTTPCACHE_IGNORE_RESPONSE_CACHE_CONTROLS": ["no-cache", "no-store"],
        "HTTPCACHE_IGNORE_MISSING": True,
    }
    # Combine default and custom settings into a new test_settings dict
    scrapy_settings = ScrapePipeline().get_scrape_settings().copy()
    for key, value in cache_settings.items():
        scrapy_settings.set(key, value)
    mocker.patch.object(
        ScrapePipeline,
        "get_scrape_settings",
        return_value=scrapy_settings,
    )
    yield


def test_it_scrapes_pages_of_domain():
    ScrapePipeline.process("17ziele.de")
    website = Website.find_by(domain="17ziele.de")
    assert len(website.webpages) == 5
    assert website.homepage.content.find("©2021 ENGAGEMENT GLOBAL") > 0


def test_it_retains_existing_pages_in_the_database():
    website = Website.create(domain="17ziele.de")
    webpage = Webpage.create(
        website=website,
        url="https://17ziele.de/my-page.html",
        depth=5,
        content="abcdef",
    )
    ScrapePipeline.process("17ziele.de")
    assert len(website.webpages) == 6
    assert webpage.reload().depth == None
    assert webpage.content == None