import itertools
import logging
import tempfile
from multiprocessing import Process
import csv
from scrapy.crawler import CrawlerProcess as CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrape.ScrapeSpider import ScrapeSpider
from models import Website, Webpage


class ScrapePipeline:
    # Limit scraping to first 100 pages
    MAX_PAGES = 100
    # Do not scrape pages bigger than 10MB
    MAX_PAGE_SIZE = int(10 * 1e6)

    @classmethod
    def process(cls, domain):
        # Store scraped URLs in a temporary file
        # We do this so that we can avoid writing the URLs to the database until
        # the very end. This allows us to wrap the database insert/updates into
        # a single transaction and ensure that our database remains in a good
        # state, even if this pipeline crashes at some point.
        with tempfile.NamedTemporaryFile(mode="r") as csv_file:
            # Run crawler inside a multiprocess. Otherwise, scrapy will complain
            # about not being restartable
            p = Process(
                target=ScrapePipeline.scrape,
                kwargs={
                    "domain": domain,
                    "csv_path": csv_file.name,
                },
            )
            p.start()
            p.join()

            # Wrap database actions in a transaction
            with Website.session.begin():
                website = Website.find_by_or_create(domain=domain)

                # Reset attributes for all pages of this website
                Webpage.query.filter(Webpage.website_id == website.id).update(
                    {"depth": None, "content": None}
                )

                # Increase the CSV field size limit to the allowed maximum
                # page size to avoid field size error.
                # See: https://stackoverflow.com/a/15063941/6451879
                csv.field_size_limit(ScrapePipeline.MAX_PAGE_SIZE)
                reader = csv.DictReader(csv_file)

                # Scrapy will not exactly observe the MAX_PAGES limit
                # because it will finish any pending requests that it
                # has already started. To get the desired maximum, we
                # stop processing pages after the maximum is reached.
                for row in itertools.islice(reader, cls.MAX_PAGES):
                    # Write each webpage into the database
                    webpage = Webpage.find_by_or_create(website=website, url=row["url"])
                    webpage.update(depth=row["depth"], content=row["content"])

    @staticmethod
    def scrape(domain, csv_path):
        process = CrawlerProcess(
            settings={
                **get_project_settings().copy_to_dict(),
                "CLOSESPIDER_ITEMCOUNT": ScrapePipeline.MAX_PAGES,
                "DOWNLOAD_MAXSIZE": ScrapePipeline.MAX_PAGE_SIZE,
                "FEEDS": {f"{csv_path}": {"format": "csv"}},
                # Disable warnings related to page size
                "DOWNLOAD_WARNSIZE": 0,
            }
        )
        # Filter out error messages related to max download size being exceeded
        for log in ["scrapy.core.scraper", "scrapy.core.downloader.handlers.http11"]:
            logging.getLogger(log).addFilter(DownloadSizeFilter())

        process.crawl(
            ScrapeSpider,
            start_urls=[f"http://{domain}"],
            allowed_domains=[domain],
        )
        process.start()
        process.join()


class DownloadSizeFilter(logging.Filter):
    def filter(self, record):
        # Filter out errors related to max download size being exceeded
        msg = record.getMessage()
        if msg.startswith("Error downloading") or msg.startswith("Cancelling download"):
            return False

        return True
