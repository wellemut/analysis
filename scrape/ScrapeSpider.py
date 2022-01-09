from io import BytesIO
import json
import scrapy
from scrapy.linkextractors import LinkExtractor
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

    def parse(self, response, depth=0):
        # Get response metadata
        status_code = response.status
        headers = response.headers.to_unicode_dict()

        # Get response content if it's plain text or HTML document
        content = None
        mime_type = magic.from_buffer(BytesIO(response.body).read(2048))
        if mime_type == "text/plain" or mime_type.startswith("HTML document"):
            content = response.text

        yield {
            "url": response.url,
            "depth": depth,
            "status_code": status_code,
            "content": content,
            "mime_type": mime_type,
            "headers": json.dumps(headers),
        }

        # For redirects, keep depth identical and check location header for new
        # URL
        if status_code in [301, 302, 303, 307, 308]:
            redirect_url = headers.get("Location")
            if redirect_url:
                yield response.follow(
                    redirect_url, callback=self.parse, cb_kwargs=dict(depth=depth)
                )

        # Otherwise, look in entire body for new links
        elif content is not None:
            for link in self.extract_links(response):
                yield response.follow(
                    link.url, callback=self.parse, cb_kwargs=dict(depth=depth + 1)
                )