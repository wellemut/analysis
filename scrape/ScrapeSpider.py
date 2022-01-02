import os
from io import BytesIO
from uuid import uuid4
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http.response.text import TextResponse
import magic


class ScrapeSpider(scrapy.Spider):
    name = "ScrapeSpider"

    # Include start URLs in filtering duplicates
    # See: https://hexfox.com/p/how-to-filter-out-duplicate-urls-from-scrapys-start-urls/
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url)

    # Extract all links on the page
    # Docs: https://docs.scrapy.org/en/latest/topics/link-extractors.html
    def extract_links(self, response):
        return LinkExtractor(
            allow_domains=self.allowed_domains, canonicalize=True
        ).extract_links(response)

    # Write HTML response to file (compressed/gzipped)
    def write_to_file(self, response):
        asset_path = os.path.join(self.asset_path, f"{uuid4()}.txt")
        with open(asset_path, "w") as file:
            file.write(response.text)
        return asset_path

    def parse(self, response):
        # Skip if response is not text (e.g., binary, such as image)
        # See: https://stackoverflow.com/a/57475077/6451879
        if not isinstance(response, TextResponse):
            return

        # Skip if response is not plain text or HTML (e.g., PDF)
        type = magic.from_buffer(BytesIO(response.body).read(2048))
        if not type == "text/plain" and not type.startswith("HTML document"):
            return

        depth = response.meta.get("depth", 0)

        asset_path = self.write_to_file(response)
        yield {"url": response.url, "depth": depth, "asset_path": asset_path}

        for link in self.extract_links(response):
            yield response.follow(
                link.url, callback=self.parse, meta={"depth": depth + 1}
            )
