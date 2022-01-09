import os
import pytest
from pipelines import ScrapePipeline
from models import Website, Webpage, TextBlock, WebpageTextBlock

# Scrape max 5 pages per domain to speed up the testing
@pytest.fixture(autouse=True)
def a_limit_to_5_pages(mocker):
    mocker.patch.object(ScrapePipeline, "MAX_PAGES", 5)


@pytest.fixture(autouse=True)
def b_cache_scrapy_requests(mocker):
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
        # Disable throttling
        "AUTOTHROTTLE_ENABLED": False,
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


def test_it_scrapes_pages_of_domain():
    ScrapePipeline.process("17ziele.de")
    website = Website.find_by(domain="17ziele.de")

    # It stores pages with status 200
    assert (
        Webpage.query.filter_by(is_ok_and_has_content=True, website=website).count()
        == 5
    )
    assert website.homepage.url == "https://17ziele.de/"
    assert website.homepage.depth == 0
    assert website.homepage.status_code == 200
    assert website.homepage.headers != None
    assert website.homepage.mime_type == "HTML document, UTF-8 Unicode text"
    assert website.homepage.content.find("©2021 ENGAGEMENT GLOBAL") > 0

    # It stores redirect
    redirect = Webpage.find_by(url="http://17ziele.de")
    assert redirect.status_code == 301


def test_it_retains_existing_referenced_pages_in_the_database():
    website = Website.create(domain="example.com")
    unreferenced_webpage = Webpage.create(
        website=website,
        url="https://example.com/my-page.html",
    )
    referenced_webpage = Webpage.create(
        website=website,
        url="https://example.com/about",
        depth=5,
        status_code=200,
        headers='{"key": "value"}',
        mime_type="HTML Doc",
        content="abcdef",
    )
    block = TextBlock.create(website=website, content="abc", hash="abc", word_count=1)
    WebpageTextBlock.create(webpage=referenced_webpage, text_block=block, tag="p")

    # Before pipeline, both pages exist
    assert len(website.webpages) == 2
    assert Webpage.find_by(url=unreferenced_webpage.url) != None

    ScrapePipeline.process(website.domain)

    # After pipeline, unreferenced webpage is deleted...
    assert Webpage.find_by(url=unreferenced_webpage.url) == None

    # and referenced webpage is reset
    assert referenced_webpage.reload().depth == None
    assert referenced_webpage.status_code == None
    assert referenced_webpage.headers == None
    assert referenced_webpage.mime_type == None
    assert referenced_webpage.content == None