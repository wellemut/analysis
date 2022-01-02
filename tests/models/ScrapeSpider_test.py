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

    # No error raised and no results returned
    assert len(results) == 0