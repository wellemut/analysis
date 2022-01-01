import tempfile
import requests
import pytest
from scrapy.http import Response, Request
from scrape.ScrapeSpider import ScrapeSpider


@pytest.mark.vcr
def test_it_does_not_error_on_non_text_response():
    url = "https://17ziele.de/downloads.html?file=files/17ziele/content/downloads/17Ziele-Uebersicht.pdf"

    # Forge a scrapy response to test
    # Request is necessary for the response.meta to work
    scrapy_response = Response(
        body=requests.get(url).content, url=url, request=Request(url=url)
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        results = list(
            ScrapeSpider(asset_path=tmp_dir, allowed_domains=["17ziele.de"]).parse(
                scrapy_response
            )
        )

    # No error raised and no results returned
    assert len(results) == 0