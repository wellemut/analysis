from io import BytesIO
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
            # Only extract links matching root domain or www-domain, but not
            # any other subdomains
            allow=fr'^.+\:\/\/(www.)?({"|".join(self.allowed_domains)})',
            allow_domains=self.allowed_domains,
            canonicalize=True,
        ).extract_links(response)

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

        yield {"url": response.url, "depth": depth, "content": response.text}

        for link in self.extract_links(response):
            yield response.follow(
                link.url, callback=self.parse, meta={"depth": depth + 1}
            )
