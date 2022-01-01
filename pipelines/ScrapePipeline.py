import os
import logging
import tempfile
from multiprocessing import Process
import csv
from scrapy.crawler import CrawlerProcess as CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrape.ScrapeSpider import ScrapeSpider
from models import Website, Webpage


class ScrapePipeline:
    MAX_PAGES = 100

    @classmethod
    def process(cls, domain):
        # Store scraped URLs in a temporary file
        # We do this so that we can avoid writing the URLs to the database until
        # the very end. This allows us to wrap the database insert/updates into
        # a single transaction and ensure that our database remains in a good
        # state, even if this pipeline crashes at some point.
        with tempfile.TemporaryDirectory() as tmp_dir:
            # URLs are exported to the following CSV files and later transferred
            # to the database
            csv_path = os.path.join(tmp_dir, "pages.csv")

            # Run crawler inside a multiprocess. Otherwise, scrapy will complain
            # about not being restartable
            p = Process(
                target=ScrapePipeline.scrape,
                kwargs={
                    "domain": domain,
                    "csv_path": csv_path,
                    "asset_path": tmp_dir,
                },
            )
            p.start()
            p.join()

            # Wrap database actions in a transaction
            with Website.session.begin():
                website = Website.find_by_or_create(domain=domain)

                # Reset attributes for all pages of this website
                Webpage.query.filter(Webpage.website_id == website.id).update(
                    {"depth": None, "file_name": None}
                )

                # Read scraped URLs and update the database
                with open(csv_path, "r") as file:
                    reader = csv.DictReader(file)

                    # Write each webpage into the database
                    page_count = 0
                    for row in reader:
                        webpage = Webpage.find_by_or_create(
                            website=website, url=row["url"]
                        )
                        with open(row["asset_path"], "r") as f:
                            webpage.update(depth=row["depth"], content=f.read())

                        # Scrapy will not exactly observe the MAX_PAGES limit
                        # because it will finish any pending requests that it
                        # has already started. To get the desired maximum, we
                        # stop processing pages after the maximum is reached.
                        page_count += 1
                        if page_count >= cls.MAX_PAGES:
                            break

    @staticmethod
    def scrape(domain, csv_path, asset_path):
        process = CrawlerProcess(
            settings={
                **get_project_settings().copy_to_dict(),
                "CLOSESPIDER_ITEMCOUNT": ScrapePipeline.MAX_PAGES,
                "FEEDS": {f"{csv_path}": {"format": "csv"}},
            }
        )
        # Filter out error messages related to max download size being exceeded
        for log in ["scrapy.core.scraper", "scrapy.core.downloader.handlers.http11"]:
            logging.getLogger(log).addFilter(DownloadSizeFilter())

        process.crawl(
            ScrapeSpider,
            start_urls=[f"http://{domain}"],
            allowed_domains=[domain],
            asset_path=asset_path,
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
