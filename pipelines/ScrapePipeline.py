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
        with tempfile.NamedTemporaryFile(suffix=".csv") as file:

            # Run crawler inside a multiprocess. Otherwise, scrapy will complain
            # about not being restartable
            p = Process(target=ScrapePipeline.scrape, args=(domain, file.name))
            p.start()
            p.join()

            # Read scraped URLs and update the database
            with open(file.name, "r") as file:
                reader = csv.DictReader(file)

                # Wrap database actions in a transaction
                with Website.session.begin():
                    website = Website.find_by_or_create(domain=domain)

                    # Reset attributes for all pages of this websites
                    Webpage.query.filter(Webpage.website_id == website.id).update(
                        {"depth": None}
                    )

                    # Write each webpage into the database
                    page_count = 0
                    for row in reader:
                        Webpage.find_by_or_create(
                            website_id=website.id, url=row["url"]
                        ).update(depth=row["depth"])
                        page_count += 1

                        # Scrapy will not exactly observe the MAX_PAGES limit
                        # because it will finish any pending requests that it
                        # has already started. To get the desired maximum, we
                        # stop processing pages after the maximum is reached.
                        if page_count >= cls.MAX_PAGES:
                            break

    @staticmethod
    def scrape(domain, file_path):
        process = CrawlerProcess(
            settings={
                **get_project_settings().copy_to_dict(),
                "CLOSESPIDER_ITEMCOUNT": ScrapePipeline.MAX_PAGES,
                "FEEDS": {f"{file_path}": {"format": "csv"}},
            }
        )
        process.crawl(
            ScrapeSpider, start_urls=[f"http://{domain}"], allowed_domains=[domain]
        )
        process.start()
        process.join()
