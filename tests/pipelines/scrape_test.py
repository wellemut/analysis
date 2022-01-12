import os
import pytest
from pipelines.ScrapePipeline import ScrapePipeline
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


def test_it_falls_back_to_www_and_non_https_when_it_cannot_find_start_url(factory):
    website = factory.website(domain="example.com")
    ScrapePipeline.process(website.domain)

    # It makes four scraping attemps that result in errors
    assert len(website.webpages) == 4
    assert [page.status_code for page in website.webpages] == [999, 999, 999, 999]

    # It starts with the https version as the start URL
    assert website.webpages[0].url == "https://example.com"

    # It tries the following three fallback URLs before giving up
    assert website.webpages[1].url == "https://www.example.com"
    assert website.webpages[2].url == "http://example.com"
    assert website.webpages[3].url == "http://www.example.com"


def test_it_retains_existing_referenced_pages_in_the_database(factory):
    website = factory.website()
    unreferenced_webpage = factory.webpage(website=website)
    referenced_webpage = factory.webpage(
        website=website, depth=5, status_code=200, content="abcdef"
    )
    factory.webpage_text_block(webpage=referenced_webpage)

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