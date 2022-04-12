import pytest
from pipelines.ScrapePipeline import ScrapePipeline
from models import Website, Webpage
import socket

# Scrape max 5 pages per domain to speed up the testing
@pytest.fixture(autouse=True)
def a_limit_to_5_pages(mocker):
    mocker.patch.object(ScrapePipeline, "MAX_PAGES", 5)


@pytest.fixture(autouse=True)
def b_speed_up_scrapy_requests(mocker):
    # Custom scrapy settings to inject
    settings_overwrites = {
        # Disable throttling
        "AUTOTHROTTLE_ENABLED": False,
        # Disable robots.txt check
        "ROBOTSTXT_OBEY": False,
    }
    # Combine default and custom settings into a new test_settings dict
    scrapy_settings = ScrapePipeline().get_scrape_settings().copy()
    for key, value in settings_overwrites.items():
        scrapy_settings.set(key, value)
    mocker.patch.object(
        ScrapePipeline,
        "get_scrape_settings",
        return_value=scrapy_settings,
    )


@pytest.mark.block_network(
    # Get IP address of our mock local test server
    allowed_hosts=socket.gethostbyname_ex("test.local.com")[2]
)
def test_it_scrapes_pages_of_domain():
    ScrapePipeline.process("test.local.com")
    website = Website.find_by(domain="test.local.com")

    # It stores pages with status 200
    assert (
        Webpage.query.filter_by(is_ok_and_has_content=True, website=website).count()
        == 3
    )
    root_page = website.root_page
    assert root_page.depth == 0
    assert root_page.status_code == 200
    assert root_page.headers != None
    assert root_page.mime_type == "HTML document, ASCII text"
    assert root_page.content.find("Hello World!") > 0


@pytest.mark.block_network(
    # Get IP address of our mock local server without response
    allowed_hosts=socket.gethostbyname_ex("undefined.local.com")[2]
)
def describe_when_start_url_cannot_be_found():
    def it_falls_back_to_www_and_non_https_versions_of_the_url(factory):
        website = factory.website(domain="undefined.local.com")
        factory.organization(
            website=website, homepage="https://www.undefined.local.com/home"
        )
        ScrapePipeline.process(website.domain)

        # It makes four scraping attemps that result in errors
        assert len(website.webpages) == 5
        assert all([page.status_code == 999 for page in website.webpages])

        # It starts with homepage as the start URL
        assert website.webpages[0].url == "https://www.undefined.local.com/home"

        # It tries the following four fallback URLs before giving up
        assert website.webpages[1].url == "https://undefined.local.com"
        assert website.webpages[2].url == "https://www.undefined.local.com"
        assert website.webpages[3].url == "http://undefined.local.com"
        assert website.webpages[4].url == "http://www.undefined.local.com"

        # Has no suggested homepage
        assert website.root_page == None

    def describe_when_start_url_is_one_of_the_fallback_urls():
        def it_attempts_the_remaining_fallback_urls(factory):
            website = factory.website(domain="undefined.local.com")
            ScrapePipeline.process(website.domain)

            # It makes four scraping attemps that result in errors
            assert len(website.webpages) == 4
            assert all([page.status_code == 999 for page in website.webpages])

            # It starts with homepage as the start URL
            assert website.webpages[0].url == "https://undefined.local.com"

            # It tries the following three fallback URLs before giving up
            assert website.webpages[1].url == "https://www.undefined.local.com"
            assert website.webpages[2].url == "http://undefined.local.com"
            assert website.webpages[3].url == "http://www.undefined.local.com"

            # Has no suggested homepage
            assert website.root_page == None


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