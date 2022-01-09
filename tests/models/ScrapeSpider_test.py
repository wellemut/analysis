import requests
import pytest
from scrapy.http import TextResponse, Request
from scrape.ScrapeSpider import ScrapeSpider


@pytest.mark.vcr
def test_it_does_not_error_on_non_text_response():
    url = "https://17ziele.de/downloads.html?file=files/17ziele/content/downloads/17Ziele-Uebersicht.pdf"

    # Forge a scrapy response to test
    # Request is necessary for the response.meta to work
    scrapy_response = TextResponse(
        body=requests.get(url).content, url=url, request=Request(url=url)
    )

    results = list(ScrapeSpider(allowed_domains=["17ziele.de"]).parse(scrapy_response))

    # No error raised
    assert len(results) == 1
    assert results[0]["status_code"] == 200
    assert results[0]["mime_type"] == "PDF document, version 1.3"
    assert results[0]["content"] == None


@pytest.mark.vcr
def test_it_collects_redirects():
    url = "http://github.com"
    request = requests.get(url, allow_redirects=False)

    # Forge a scrapy response to test
    # Request is necessary for the response.meta to work
    scrapy_response = TextResponse(
        status=request.status_code,
        headers=request.headers,
        body=request.content,
        url=url,
        request=Request(url=url),
    )

    results = list(ScrapeSpider(allowed_domains=["github.com"]).parse(scrapy_response))

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
    body = """
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

    def it_follows_links_on_the_same_naked_and_www_domain_only():
        url = "https://www.example.com/"
        scrapy_response = TextResponse(
            body=body,
            url=url,
            request=Request(url=url),
        )

        results = list(
            ScrapeSpider(allowed_domains=["example.com"]).parse(scrapy_response)
        )

        # Results do not include links to subdomain.example.com nor other-domain.com
        assert len(results) == 4
        assert results[0]["depth"] == 0
        assert results[1].url == "https://www.example.com/subpage"
        assert results[2].url == "https://www.example.com/home"
        assert results[3].url == "https://example.com/blog"

    def it_supports_subdomains_as_allowed_domain():
        url = "https://subdomain.example.com/"
        scrapy_response = TextResponse(
            body=body,
            url=url,
            request=Request(url=url),
        )

        results = list(
            ScrapeSpider(allowed_domains=["subdomain.example.com"]).parse(
                scrapy_response
            )
        )

        # Results do not include links to subdomain.example.com nor other-domain.com
        assert len(results) == 4
        assert results[0]["depth"] == 0
        assert results[1].url == "https://subdomain.example.com/subpage"
        assert results[2].url == "https://subdomain.example.com/about"
        assert results[3].url == "https://www.subdomain.example.com/more"