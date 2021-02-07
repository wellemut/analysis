from pathlib import Path
from pymaybe import maybe
from bs4 import BeautifulSoup
import pandas as pd
from database import Database, Table, Column, Field, Order
from helpers.get_urls_table_from_scraped_database import (
    get_urls_table_from_scraped_database,
)
from helpers.save_result import save_result

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    # Create database
    db = Database("summaries")

    db.table("domains").create(
        Column("id", "integer", nullable=False),
        Column("domain", "text", nullable=False),
        Column("summary", "text", nullable=True),
    ).primary_key("id").unique("domain").if_not_exists().execute()

    # Clear records for domain/url
    if reset:
        db.table("domains").delete().where(
            Field("domain").glob_unless_none(domain)
        ).execute()

    # Fetch IDs for level-0 domain from scrape database
    scraped_urls = get_urls_table_from_scraped_database()
    ids_of_scraped_records = (
        scraped_urls.select("id")
        .where(
            Field("domain").glob_unless_none(domain)
            & (Field("level") == 0)
            & (Field("html").notnull())
        )
        .orderby("domain", order=Order.desc)
        .orderby("id")
        .values()
    )

    # Fetch analyzed URLs
    analyzed_domains = db.table("domains").select("domain").values()

    # Analyze each HTML snippet in database
    for index, scraped_record_id in enumerate(ids_of_scraped_records, start=1):
        scraped_record = (
            scraped_urls.select("id", "domain", "url", "html")
            .where(Field("id") == scraped_record_id)
            .first()
        )
        id = scraped_record["id"]
        domain = scraped_record["domain"]
        url = scraped_record["url"]
        html = scraped_record["html"]

        # If this domain has already been analyzed, let's skip it.
        if analyzed_domains.count(domain) >= 1:
            print("Skipping", domain, "...", "Already done")
            continue

        print(
            "({current}/{total})".format(
                current=index, total=len(ids_of_scraped_records)
            ),
            "Searching for meta description in scraped HTML for",
            domain,
            end=" ... ",
            flush=True,
        )

        # Prepare text extraction from HTML
        soup = BeautifulSoup(html, "lxml")

        # Search for meta description in HTML
        # NOTE: In the future, we may use NPL algorithms to extract a summary
        # based on word frequency across all URLs of each domain

        # Search page meta description
        description = (
            maybe(soup.head)
            .select_one('meta[name="description"]')["content"]
            .strip()
            .or_else(None)
        )

        # Search meta og:description
        if not description:
            description = (
                maybe(soup.head)
                .select_one('meta[property="og:description"]')["content"]
                .strip()
                .or_else(None)
            )

        # Search meta og:description
        if not description:
            description = (
                maybe(soup.head)
                .select_one('meta[name="twitter:description"]')["content"]
                .strip()
                .or_else(None)
            )

        # Write summary to database
        db.table("domains").insert(
            domain=domain, summary=(description or None)
        ).execute()

        print("Done")
        # NOTE: We currently have duplicate domains in our scraped dataset, so
        # we need to add finished domains here, so we skip them on the second
        # round (otherwise, we get a non-unique domain error).
        analyzed_domains.append(domain)

    print("Exporting to dataframe...")

    # Get data
    df = (
        db.table("domains")
        .select(
            "domain",
            "summary",
        )
        .to_dataframe()
    )

    # Sort
    df = df.sort_values(by=["domain"])

    print("Found", df["summary"].count(), "/", len(df.index), "summaries")

    # Save as JSON
    save_result(PIPELINE, df)
