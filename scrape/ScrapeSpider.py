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

    def parse(self, response):
        depth = response.meta.get("depth", 0)
        yield {"url": response.url, "depth": depth}

        for link in self.extract_links(response):
            yield response.follow(
                link.url, callback=self.parse, meta={"depth": depth + 1}
            )
