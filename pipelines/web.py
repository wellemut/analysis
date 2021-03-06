from pathlib import Path
from datetime import datetime
from operator import itemgetter
from config import MAIN_DATABASE
from models.Database import Database, Column, Field, Order, Table, functions as fn
from models import PipelineProgressBar
from helpers.spider_runner import SpiderRunner

# Set the maximum scrape level:
# level 1 = one click away from root
# level 2 = two clicks away
# etc...
MAX_LEVEL = 1

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    db = Database(MAIN_DATABASE)

    # Fetch IDs for domain/url from scrape database, ignoring URLs already
    # scraped
    print(
        "Skipping",
        db.table("domain").count("id").where(Field("scraped_at").notnull()).value(),
        "domains already analyzed...",
    )

    # Get last scraped domain, so we can continue where we left of
    last_domain_scraped = (
        db.table("url")
        .select(Table("domain").id)
        .join(Table("domain"))
        .on(Table("url").domain_id == Table("domain").id)
        .orderby("scraped_at", order=Order.desc)
        .limit(1)
        .value()
    )

    # Get domains to scrape
    domain_ids_to_scrape = (
        db.table("domain")
        .select("id")
        .where(Field("scraped_at").isnull())
        .orderby(Field("id") == last_domain_scraped, order=Order.desc)
        .values()
    )

    progress = PipelineProgressBar(f"{PIPELINE}: DOMAINS")
    for domain_id in progress.iterate(domain_ids_to_scrape):
        domain, homepage = itemgetter("domain", "homepage")(
            db.table("domain")
            .select("domain", "homepage")
            .where(Field("id") == domain_id)
            .first()
        )

        # Create the homepage, unless it exists
        table = db.table("url")
        table.insert(url=homepage, domain_id=domain_id, level=0).on_conflict(
            table.url
        ).do_nothing().execute()

        url_progress = progress.add_bar(domain, max_value=0)

        while True:
            # Fetch the URLs to scrape for this domain
            criteria = (Field("domain_id") == domain_id) & (
                Field("scraped_at").isnull()
            )
            if MAX_LEVEL is not None:
                criteria = criteria & (Field("level") <= MAX_LEVEL)

            urls_to_scrape = (
                db.table("url").select("id", "url", "level").where(criteria).all()
            )

            # If no URLs are left, mark domain as done
            if len(urls_to_scrape) == 0:
                url_progress.finish()
                table = db.table("url")
                first_scraped_at = (
                    table.select(fn.Min(table.scraped_at))
                    .where(Field("domain_id") == domain_id)
                    .value()
                )
                db.table("domain").set(
                    first_scraped_at=first_scraped_at, scraped_at=datetime.now()
                ).where(Field("id") == domain_id).execute()
                break

            url_progress.max_value += len(urls_to_scrape)

            # Scrape each URL
            for url_object in urls_to_scrape:
                id = url_object["id"]
                url = url_object["url"]
                level = url_object["level"]

                url_progress.set_status(f"Scraping {url}")

                SpiderRunner.run(
                    "Website Spider",
                    start_urls=[url],
                    allowed_domains=[domain],
                    # Manually pass the url, because redirects and other effects
                    # may lead to a different URL being scraped
                    database_name=MAIN_DATABASE,
                    url_id=id,
                    domain_id=domain_id,
                    url=url,
                    domain=domain,
                    level=level,
                    settings={
                        "ITEM_PIPELINES": {
                            "scraper_web.pipelines.WriteWebsitePipeline": 100
                        }
                    },
                )

                url_progress.item_complete()
