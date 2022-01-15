import logging
import tempfile
from multiprocessing import Process
import csv
from scrapy.crawler import CrawlerProcess as CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrape.ScrapeSpider import ScrapeSpider
from models import Website, Webpage
from helpers import get_top_level_domain_from_url


class ScrapePipeline:
    # Limit scraping to first 100 pages
    MAX_PAGES = 100
    # Do not scrape pages bigger than 10MB
    MAX_PAGE_SIZE = int(10 * 1e6)

    @classmethod
    def process(cls, domain):
        print(f"Scraping {domain}:", end=" ")

        # Determine the homepage / first page to scrape
        homepage = f"https://{domain}"
        website = Website.find_by(domain=domain) or Website().fill(
            domain=domain, top_level_domain=get_top_level_domain_from_url(homepage)
        )
        if website.organization and website.organization.homepage:
            homepage = website.organization.homepage

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
                    "homepage": homepage,
                    "csv_path": csv_file.name,
                },
            )
            p.start()
            p.join()
            # Start a new line (Scrapy prints messages on a single line)
            print("")

            # Wrap database actions in a transaction
            with Website.session.begin():
                website.save()

                # Delete all webpages that are no longer needed (ID is not
                # being referenced in any other table)
                Webpage.delete_unused_by_website(website)

                # Reset attributes for all remaining pages of this website
                Webpage.query.filter_by(website=website).update(
                    dict(
                        depth=None,
                        status_code=None,
                        headers=None,
                        mime_type=None,
                        content=None,
                    )
                )

                # Increase the CSV field size limit to the allowed maximum
                # page size to avoid field size error.
                # See: https://stackoverflow.com/a/15063941/6451879
                csv.field_size_limit(ScrapePipeline.MAX_PAGE_SIZE)
                reader = csv.DictReader(csv_file)

                pages_count_ok = 0
                for row in reader:
                    # Replace any empty strings in fields with None, since CSV
                    # cannot handle None natively
                    for key, value in row.items():
                        if isinstance(value, str) and value == "":
                            row[key] = None

                    # Convert status code to int
                    row["status_code"] = int(row["status_code"])

                    # Write each webpage into the database
                    webpage = Webpage.find_by_or_create(
                        website=website, url=row.pop("url")
                    )
                    webpage.update(**row)

                    # Scrapy will not exactly observe the MAX_PAGES limit
                    # because it will finish any pending requests that it has
                    # already started. To get the desired maximum, we stop
                    # processing pages after the maximum is reached.
                    if cls.is_ok_and_has_content(row):
                        pages_count_ok += 1

                    if pages_count_ok >= cls.MAX_PAGES:
                        break

        print("Scraped", pages_count_ok, "pages for", domain)

    @staticmethod
    def is_ok_and_has_content(page):
        return page["status_code"] == 200 and page["content"] is not None

    @classmethod
    def get_scrape_settings(cls):
        settings = get_project_settings().copy()
        # Close spider after max number of pages meeting the condition (status
        # code 200 and having content) have been scraped
        settings.set(
            "CLOSESPIDER_ITEMCOUNT_CONDITION",
            dict(count=cls.MAX_PAGES, condition=cls.is_ok_and_has_content),
        )
        settings.set("DOWNLOAD_MAXSIZE", cls.MAX_PAGE_SIZE)
        # Disable warnings related to page size
        settings.set("DOWNLOAD_WARNSIZE", 0)
        return settings

    @classmethod
    def scrape(cls, domain, homepage, csv_path):
        process = CrawlerProcess(
            settings={
                **cls.get_scrape_settings().copy_to_dict(),
                "FEEDS": {f"{csv_path}": {"format": "csv"}},
            }
        )
        # Filter out error messages related to max download size being exceeded
        for log in ["scrapy.core.scraper", "scrapy.core.downloader.handlers.http11"]:
            logging.getLogger(log).addFilter(DownloadSizeFilter())

        process.crawl(
            ScrapeSpider,
            start_urls=[homepage],
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
