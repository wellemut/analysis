from models.Database import Database, Column, Field, Order
from helpers.spider_runner import SpiderRunner

# Set the maximum scrape level:
# level 1 = one click away from root
# level 2 = two clicks away
# etc...
MAX_LEVEL = 1


def run_pipeline(domain, url, reset):
    # Create database
    db = Database("scraped")

    # Setup database
    db.table("urls").create(
        Column("id", "integer", nullable=False),
        Column("domain", "text", nullable=False),
        Column("url", "text", nullable=False),
        Column("level", "int", nullable=False),
        Column("html", "text", nullable=True),
        Column("error", "text", nullable=True),
        Column("created_at", "timestamp", nullable=True),
        Column("scraped_at", "timestamp", nullable=True),
    ).primary_key("id").unique("url").if_not_exists().execute()

    # Get last scraped domain, so we can continue where we left of
    last_domain_scraped = (
        db.table("urls")
        .select("domain")
        .where(Field("scraped_at").notnull())
        .orderby("scraped_at", order=Order.desc)
        .limit(1)
        .value()
    )

    # Scrape each URL in database
    search_conditions = Field("scraped_at").isnull()
    if MAX_LEVEL:
        search_conditions = search_conditions & Field("level") <= MAX_LEVEL

    while domain := (
        db.table("urls")
        .select("domain")
        .where(search_conditions)
        .orderby(f"domain = '{last_domain_scraped}'", order=Order.desc)
        .limit(1)
        .value()
    ):
        domains_done = (
            db.table("urls")
            .count("domain")
            .where((Field("scraped_at").notnull()) & (Field("level") == 0))
            .value()
        )
        total_domains = (
            db.table("urls").count("domain").where(Field("level") == 0).value()
        )
        urls = (
            db.table("urls")
            .select("id", "url", "level")
            .where((Field("domain") == domain) & (Field("scraped_at").isnull()))
            .all()
        )
        for url_object in urls:
            id = url_object["id"]
            url = url_object["url"]
            level = url_object["level"]

            # Print progress:
            # - Domain (x out of all)
            # - Item (out of all URLs for this domain)
            # - Level
            items_done = (
                db.table("urls")
                .count("url")
                .where(Field("scraped_at").notnull() & Field("domain") == domain)
                .value()
            )
            total_items = (
                db.table("urls")
                .count("url")
                .where((Field("domain") == domain) & (Field("level") <= MAX_LEVEL))
                .value()
            )

            # If we are not scraping level 0, then we are still working on the last
            # domain
            if level == 0:
                domains_done += 1

            print(
                "Scraping",
                "D",
                str(domains_done) + "/" + str(total_domains),
                "I",
                str(items_done + 1) + "/" + str(total_items),
                "L",
                str(level),
                ":",
                url,
                end=" ... ",
                flush=True,
            )

            SpiderRunner.run(
                "Website Spider",
                start_urls=[url],
                allowed_domains=[domain],
                # Manually pass the url, because redirects and other effects
                # may lead to a different URL being scraped
                url=url,
                domain=domain,
                level=level,
                settings={
                    "ITEM_PIPELINES": {
                        "scraper_web.pipelines.WriteWebsitePipeline": 100
                    }
                },
            )

            print("Done!")

        last_domain_scraped = domain
