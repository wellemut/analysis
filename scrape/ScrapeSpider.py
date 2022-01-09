from io import BytesIO
import json
import scrapy
from scrapy.linkextractors import LinkExtractor
import magic


class ScrapeSpider(scrapy.Spider):
    REDIRECT_STATUS_CODES = [301, 302, 303, 307, 308]
    name = "ScrapeSpider"

    # Include start URLs in filtering duplicates
    # See: https://hexfox.com/p/how-to-filter-out-duplicate-urls-from-scrapys-start-urls/
    def start_requests(self):
        for url in self.start_urls:
            # If start URL fails, attempt the following fallback URLs in order
            fallback_urls = [
                url.replace("https://", "https://www.", 1),
                url.replace("https://", "http://", 1),
                url.replace("https://", "http://www.", 1),
            ]
            yield scrapy.Request(
                url,
                callback=self.parse,
                errback=self.on_error,
                cb_kwargs=dict(fallback_urls=fallback_urls),
            )

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

    def parse(self, response, depth=0, fallback_urls=None):
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

        # Default message, indicating an error response
        message = "❌"
        if status_code == 200:
            message = "✅"
        elif status_code in self.REDIRECT_STATUS_CODES:
            message = "⏩"
        print(message, end="")

        # For redirects, keep depth identical and check location header for new
        # URL
        if status_code in self.REDIRECT_STATUS_CODES:
            redirect_url = headers.get("Location")
            if redirect_url:
                yield self.follow(response, redirect_url, depth=depth)

        # Otherwise, look in entire body for new links
        elif content is not None:
            for link in self.extract_links(response):
                yield self.follow(response, link.url, depth=depth + 1)

    # Follow a link
    def follow(self, response, url, **kwargs):
        return response.follow(
            url, callback=self.parse, errback=self.on_error, cb_kwargs=kwargs
        )

    # Handle a scraping error
    def on_error(self, failure):
        depth = failure.request.cb_kwargs.get("depth", 0)
        yield {
            "url": failure.request.url,
            "depth": depth,
            "status_code": 999,
            "content": repr(failure),
        }

        # Attempt one of the fallback URLs (see start_requests)
        fallback_urls = failure.request.cb_kwargs.get("fallback_urls", [])
        if len(fallback_urls):
            yield scrapy.Request(
                # Use the first fallback URL from the list
                fallback_urls.pop(0),
                callback=self.parse,
                errback=self.on_error,
                cb_kwargs=dict(fallback_urls=fallback_urls),
            )
