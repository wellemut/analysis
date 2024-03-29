import requests
import pytest
from scrapy.http import TextResponse, Request
from scrape.ScrapeSpider import ScrapeSpider

# Mock PlaywrightPage
class PlaywrightPage:
    _content = None

    def __init__(self, content=None):
        self._content = content

    async def close(self):
        pass

    async def content(self):
        return self._content


@pytest.mark.vcr
async def test_it_does_not_error_on_non_text_response():
    spider = ScrapeSpider(allowed_domains=["17ziele.de"])
    url = "https://17ziele.de/downloads.html?file=files/17ziele/content/downloads/17Ziele-Uebersicht.pdf"
    content = requests.get(url).content

    # Forge a scrapy response to test
    # Request is necessary for the response.meta to work
    scrapy_response = TextResponse(
        body=content,
        url=url,
        request=Request(
            url=url,
            meta=dict(playwright_page=PlaywrightPage(content=content)),
        ),
    )

    results = []
    async for result in spider.parse(scrapy_response):
        results.append(result)

    # No error raised
    assert len(results) == 1
    assert results[0]["status_code"] == 200
    assert results[0]["mime_type"] == "PDF document, version 1.3"
    assert results[0]["content"] == None


@pytest.mark.vcr
async def test_it_collects_redirects():
    spider = ScrapeSpider(allowed_domains=["github.com"])
    url = "http://github.com"
    request = requests.get(url, allow_redirects=False)

    # Forge a scrapy response to test
    # Request is necessary for the response.meta to work
    scrapy_response = TextResponse(
        status=request.status_code,
        headers=request.headers,
        body=request.content,
        url=url,
        request=Request(
            url=url, meta=dict(playwright_page=PlaywrightPage(content=request.content))
        ),
    )

    results = []
    async for result in spider.parse(scrapy_response):
        results.append(result)

    assert len(results) == 2
    assert {
        "url": url,
        "depth": 0,
        "content": None,
        "status_code": 301,
        "mime_type": "empty",
        "headers": '{"content-length": "0", "location": "https://github.com/"}',
    } == results[0]
    assert results[1].url == "https://github.com/"
    assert results[1].cb_kwargs["depth"] == 0


def describe_link_extraction():
    body_with_external_links = """
    <html>
        <body>
            <a href='/subpage'>subpage</a>
            <a href='https://subdomain.example.com/about'>subdomain</a>
            <a href='https://www.subdomain.example.com/more'>www subdomain</a>
            <a href='https://other-domain.com/'>other domain</a>
            <a href='https://www.example.com/home'>www</a>
            <a href='https://example.com/blog'>root</a>
        </body>    
    </html>""".encode(
        "utf-8"
    )

    async def it_follows_links_on_the_same_naked_and_www_domain_only():
        spider = ScrapeSpider(allowed_domains=["example.com"])
        url = "https://www.example.com/"
        scrapy_response = TextResponse(
            body=body_with_external_links,
            url=url,
            request=Request(
                url=url,
                meta=dict(
                    playwright_page=PlaywrightPage(content=body_with_external_links)
                ),
            ),
        )

        results = []
        async for result in spider.parse(scrapy_response):
            results.append(result)

        # Results do not include links to subdomain.example.com nor other-domain.com
        assert len(results) == 4
        assert results[0]["depth"] == 0
        assert results[1].url == "https://www.example.com/subpage"
        assert results[2].url == "https://www.example.com/home"
        assert results[3].url == "https://example.com/blog"

    async def it_supports_subdomains_as_allowed_domain():
        spider = ScrapeSpider(allowed_domains=["subdomain.example.com"])
        url = "https://subdomain.example.com/"
        scrapy_response = TextResponse(
            body=body_with_external_links,
            url=url,
            request=Request(
                url=url,
                meta=dict(
                    playwright_page=PlaywrightPage(content=body_with_external_links)
                ),
            ),
        )

        results = []
        async for result in spider.parse(scrapy_response):
            results.append(result)

        # Results do not include links to subdomain.example.com nor other-domain.com
        assert len(results) == 4
        assert results[0]["depth"] == 0
        assert results[1].url == "https://subdomain.example.com/subpage"
        assert results[2].url == "https://subdomain.example.com/about"
        assert results[3].url == "https://www.subdomain.example.com/more"

    body_with_internal_links = """
        <html>
            <body>
                <a href='/'>HOME</a>
                <a href='/jrc'>JRC HOME</a>
                <a href='/jrc/en'>JRC EN</a>
                <a href='https://www.example.com/jrc/en/news'>JRC EN NEWS</a>
            </body>    
        </html>""".encode(
        "utf-8"
    )

    async def it_prioritizes_urls_matching_the_start_url():
        url = "https://example.com/jrc/en/"
        spider = ScrapeSpider(allowed_domains=["example.com"], start_urls=[url])
        scrapy_response = TextResponse(
            body=body_with_internal_links,
            url=url,
            request=Request(
                url=url,
                cb_kwargs=dict(start_url=url),
                meta=dict(
                    playwright_page=PlaywrightPage(content=body_with_internal_links)
                ),
            ),
        )

        results = []
        async for result in spider.parse(scrapy_response):
            results.append(result)

        # Results do not include links to subdomain.example.com nor other-domain.com
        assert len(results) == 5
        assert results[0]["depth"] == 0
        assert results[1].url == "https://example.com/"
        assert results[1].priority == 0
        assert results[2].url == "https://example.com/jrc"
        assert results[2].priority == 100
        assert results[3].url == "https://example.com/jrc/en"
        assert results[3].priority == 200
        assert results[4].url == "https://www.example.com/jrc/en/news"
        assert results[4].priority == 200


def describe_get_url_priority():
    def it_gives_highest_priority_to_urls_matching_start_url():
        start_url = "https://www.example.com/en/home"
        spider = ScrapeSpider(start_urls=[start_url])
        assert spider.get_url_priority("https://example.com/en") == 100
        assert spider.get_url_priority("https://example.com/en/") == 100
        assert spider.get_url_priority("https://example.com/") == 0
        assert spider.get_url_priority("https://example.com/") == 0
        assert spider.get_url_priority("https://example.com/en/home") == 200
        assert spider.get_url_priority("https://example.com/en/home/") == 200
        assert spider.get_url_priority("https://example.com/en/home/news") == 200
