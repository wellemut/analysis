import os
from uuid import uuid4
import scrapy
from scrapy.linkextractors import LinkExtractor


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
        depth = response.meta.get("depth", 0)

        asset_path = self.write_to_file(response)
        yield {"url": response.url, "depth": depth, "asset_path": asset_path}

        for link in self.extract_links(response):
            yield response.follow(
                link.url, callback=self.parse, meta={"depth": depth + 1}
            )
