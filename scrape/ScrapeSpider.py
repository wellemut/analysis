from io import BytesIO
from urllib.parse import urlparse
import json
import scrapy
from scrapy.linkextractors import LinkExtractor
import magic
from helpers import get_domain_from_url


class ScrapeSpider(scrapy.Spider):
    REDIRECT_STATUS_CODES = [301, 302, 303, 307, 308]
    name = "ScrapeSpider"

    # Include start URLs in filtering duplicates
    # See: https://hexfox.com/p/how-to-filter-out-duplicate-urls-from-scrapys-start-urls/
    def start_requests(self):
        for url in self.start_urls:
            # If start URL fails, attempt the following fallback URLs in order
            domain = get_domain_from_url(url)
            fallback_urls = [
                f"https://{domain}",
                f"https://www.{domain}",
                f"http://{domain}",
                f"http://www.{domain}",
            ]
            # Remove start URL from fallback URLs
            if url in fallback_urls:
                fallback_urls.remove(url)
            yield scrapy.Request(
                url,
                callback=self.parse,
                errback=self.on_error,
                cb_kwargs=dict(fallback_urls=fallback_urls),
                meta={"playwright": True, "playwright_include_page": True},
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

    async def parse(self, response, depth=0, fallback_urls=None):
        # Get response metadata
        status_code = response.status
        headers = response.headers.to_unicode_dict()

        # Get response content if it's plain text or HTML document
        content = None
        page = response.meta["playwright_page"]
        mime_type = magic.from_buffer(BytesIO(response.body).read(2048))
        if mime_type == "text/plain" or mime_type.startswith("HTML document"):
            content = await page.content()
        await page.close()

        yield self.result(
            url=response.url,
            depth=depth,
            status_code=status_code,
            content=content,
            mime_type=mime_type,
            headers=json.dumps(headers),
        )

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

    # Return the numeric priority for a given URL
    # The more path segments of the url match one of the given start_urls, the
    # higher the priority. This makes sure that the scraper prioritizes URLs
    # the pages that are "subpages" of the start URLs.
    def get_url_priority(self, url):
        # Split a URL into a list of its segments
        get_url_segments = lambda url: urlparse(url).path.strip("/").split("/")

        # Get path segments from given URL and start URLs
        url_segments = get_url_segments(url)
        start_segments = [get_url_segments(url) for url in self.start_urls]

        # Count number of segment matches of given URL with start URLs
        priority = 0
        for segments in start_segments:
            for index, segment in enumerate(segments):
                # Stop as soon as we have a mismatch in the segments
                if index >= len(url_segments) or segment != url_segments[index]:
                    break

                # Increment the priority level by 100 for each matching segment
                priority = max(priority, (index + 1) * 100)

        return priority

    # Follow a link
    def follow(self, response, url, **kwargs):
        return response.follow(
            url,
            priority=self.get_url_priority(url),
            callback=self.parse,
            errback=self.on_error,
            cb_kwargs=kwargs,
            meta={"playwright": True, "playwright_include_page": True},
        )

    # Handle a scraping error
    async def on_error(self, failure):
        print("❌", end="")

        # Close playwright page, if it was opened
        page = failure.request.meta.get("playwright_page", None)
        if page:
            await page.close()

        yield self.result(
            url=failure.request.url,
            depth=failure.request.cb_kwargs.get("depth", 0),
            status_code=999,
            content=repr(failure),
        )

        # Attempt one of the fallback URLs (see start_requests)
        fallback_urls = failure.request.cb_kwargs.get("fallback_urls", [])
        if len(fallback_urls):
            yield scrapy.Request(
                # Use the first fallback URL from the list
                fallback_urls.pop(0),
                callback=self.parse,
                errback=self.on_error,
                cb_kwargs=dict(fallback_urls=fallback_urls),
                meta={"playwright": True, "playwright_include_page": True},
            )

    # Ensure that all results have the same format. Otherwise, the scrapy CSV
    # feed writer will only use the keys present in the first result
    def result(self, url, depth, status_code, content, mime_type=None, headers=None):
        return dict(
            url=url,
            depth=depth,
            status_code=status_code,
            content=content,
            mime_type=mime_type,
            headers=headers,
        )