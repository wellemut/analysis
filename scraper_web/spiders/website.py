# -*- coding: utf-8 -*-
import traceback
import scrapy
import twisted
from pprint import pprint
from ..items import Website, Link, Error
from scrapy.linkextractors import LinkExtractor
from helpers.extract_text_from import extract_text_from

# Alternatively, consider using a CrawlSpider:
# https://stackoverflow.com/a/36838995/6451879

# Scrape an entire website
class WebsiteSpider(scrapy.Spider):
    name = "Website Spider"

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, errback=self.errback, dont_filter=True)

    def parse(self, response):
        try:
            # Extract page HTML
            yield Website(html=response.body)

            # Extract links to other pages of this domain
            for link in self.extract_links(response):
                link_url = response.urljoin(link.url)
                yield Link(url=link_url)

        except Exception as error:
            traceback_str = "".join(traceback.format_tb(error.__traceback__))
            yield Error(message=str(error) + "\n" + traceback_str)

    # Extract all links on the page
    # Docs: https://docs.scrapy.org/en/latest/topics/link-extractors.html
    def extract_links(self, response):
        return LinkExtractor(
            allow_domains=self.allowed_domains, canonicalize=True
        ).extract_links(response)

    # Catch errors
    def errback(self, failure):
        yield Error(message=repr(failure))
