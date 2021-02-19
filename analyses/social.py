from pathlib import Path
import re
from pymaybe import maybe
from bs4 import BeautifulSoup
import pandas as pd
from models.Database import Database, Table, Column, Field, Order
from models import PipelineProgressBar
from helpers.get_urls_table_from_scraped_database import (
    get_urls_table_from_scraped_database,
)
from helpers.is_binary_string import is_binary_string
from helpers.update_analysis_database import update_analysis_database
from helpers.save_result import save_result

PIPELINE = Path(__file__).stem

TWITTER_REGEX = re.compile(
    r"^(?:https?:)?\/\/(?:www\.)?twitter.com\/(?:#!\/)?(?!(?:intent|(?:[a-z]{2}\/)?privacy|hashtag|home|search|share|account|personalization)\b)(?P<handle>[A-Za-z0-9_]+)\/?",
    flags=re.IGNORECASE,
)
FACEBOOK_REGEX = re.compile(
    r"^(?:https?:)?\/\/(?:(?:www|m|mobile|touch|mbasic)\.)?(?:facebook|fb)\.(?:com|me)\/(?!(?:sharer|share|login|ads|policy|policies|settings|about|hashtag|help|events|groups|(?:v[0-9]+\.[0-9]+\/dialog))\b)(?:pg\/|pages\/(?:[^\/]+\/)*)?(?P<handle>[^\/_\?#@]+)\/?",
    flags=re.IGNORECASE,
)
LINKEDIN_REGEX = re.compile(
    r"(?:https?:)?\/\/(?:[a-z]{2,3}\.)?linkedin.com\/company/(?P<handle>[^\/\?#]+)\/?"
)
REGEXES = {
    "twitter": TWITTER_REGEX,
    "facebook": FACEBOOK_REGEX,
    "linkedin": LINKEDIN_REGEX,
}


def run_pipeline(domain, url, reset):
    # Create database
    db = Database("socials")

    db.table("urls").create(
        Column("id", "integer", nullable=False),
        Column("domain", "text", nullable=False),
        Column("url", "text", nullable=False),
    ).primary_key("id").unique("url").if_not_exists().execute()

    db.table("socials").create(
        Column("id", "integer", nullable=False),
        Column("url_id", "text", nullable=False),
        Column("type", "text", nullable=False),
        Column("handle", "text", nullable=False),
        Column("href", "text", nullable=False),
    ).foreign_key("url_id", references="urls (id)").primary_key(
        "id"
    ).if_not_exists().execute()

    # Add index on foreign key matches.url_id
    db.execute_sql(
        "CREATE INDEX IF NOT EXISTS socials_url_id_index ON socials (url_id)"
    )

    # Create view: combination of urls and socials
    db.execute_sql(
        "CREATE VIEW IF NOT EXISTS results AS {query}".format(
            query=db.table("urls")
            .select(
                "domain",
                "url",
                Table("socials").type,
                Table("socials").href,
                Table("socials").handle,
            )
            .join(Table("socials"))
            .on(Table("urls").id == Table("socials").url_id)
            .get_sql()
        )
    )

    # Clear records for domain/url
    if reset:
        with db.start_transaction() as transaction:
            db.table("socials").delete().where(
                Table("socials").url_id.isin(
                    db.table("urls")
                    .select("id")
                    .where(
                        Field("domain").glob_unless_none(domain)
                        & Field("url").glob_unless_none(url)
                    )
                )
            ).execute(transaction=transaction)
            db.table("urls").delete().where(
                Field("domain").glob_unless_none(domain)
                & Field("url").glob_unless_none(url)
            ).execute(transaction=transaction)

    # Fetch IDs for first 10 URLs for each domain, ignoring URLs already
    # scraped
    print(
        "Skipping",
        db.table("urls").count("id").value(),
        "URLs already analyzed...",
    )

    scraped_urls = get_urls_table_from_scraped_database()
    with scraped_urls.database.start_transaction() as transaction:
        scraped_urls.database.attach(db, name="analysis", transaction=transaction)

        ids_of_scraped_records = (
            scraped_urls.as_("a")
            .select("id")
            .where(
                Field("domain").glob_unless_none(domain)
                & Field("url").glob_unless_none(url)
                & Field("html").notnull()
                & Field("id").isin(
                    scraped_urls.as_("b")
                    .select("id")
                    .where(Field("domain") == Table("a").domain)
                    .orderby("id")
                    .limit(10)
                )
                & Field("url").notin(db.table("urls").schema("analysis").select("url"))
            )
            .orderby("domain", order=Order.desc)
            .orderby("id")
            .values(transaction=transaction)
        )

    # Analyze each HTML snippet in database
    progress = PipelineProgressBar(PIPELINE)
    for scraped_record_id in progress.iterate(ids_of_scraped_records):
        scraped_record = (
            scraped_urls.select("id", "domain", "url", "html")
            .where(Field("id") == scraped_record_id)
            .first()
        )
        id = scraped_record["id"]
        domain = scraped_record["domain"]
        url = scraped_record["url"]
        html = scraped_record["html"]

        progress.set_current_url(url)

        # If this URL contains binary text, let's skip it
        if is_binary_string(html):
            progress.print("Skipping", url, "...", "Binary file detected")
            continue

        # Prepare text extraction from HTML
        soup = BeautifulSoup(html, "lxml")

        # Search for links to Twitter, Facebook, or LinkedIn
        socials = []

        # Find all anchor tags and extract hrefs
        links = soup.find_all("a")
        hrefs = [link.get("href", "") for link in links]

        # Search each href
        for href in hrefs:
            for type, regex in REGEXES.items():
                match = regex.match(href)
                if match:
                    socials.append(
                        {
                            "type": type,
                            "href": href,
                            "handle": match.group("handle").lower(),
                        }
                    )

        # Write socials to database
        with db.start_transaction() as transaction:
            new_url_id = (
                db.table("urls")
                .insert(domain=domain, url=url)
                .execute(
                    transaction=transaction, callback=lambda cursor: cursor.lastrowid
                )
            )
            for social in socials:
                db.table("socials").insert(
                    url_id=new_url_id,
                    type=social["type"],
                    href=social["href"],
                    handle=social["handle"],
                ).execute(transaction=transaction)

    print("Analyzing results...")

    # Get data
    handles = (
        db.view("results").select("domain", "url", "type", "handle").to_dataframe()
    )

    # Count number of hrefs for each type and domain
    handles = (
        handles.groupby(["domain", "type", "handle"])
        .size()
        .reset_index()
        .rename(columns={0: "count"})
    )

    # Sort dataset
    handles = handles.sort_values(by=["domain", "type", "count"], ascending=False)

    # Keep top 1-row for each hit
    handles = handles.groupby(["domain", "type"]).head(1)

    # Ignore count
    # handles = handles.drop(columns=["count"])

    # Unstack type into columns, so that we have one row per domain
    handles = handles.set_index(["domain", "type"]).unstack(level=-1).reset_index()

    # Rename columns
    handles.columns = ["_".join(reversed(col)).strip("_") for col in handles.columns]

    # Count number of analyzed URLs for each type and domain
    urls = db.table("urls").select("domain", "url").to_dataframe()
    url_count = (
        urls.groupby(["domain"]).size().reset_index().rename(columns={0: "url_count"})
    )

    # Merge handles and url counts
    df = handles.merge(url_count, left_on="domain", right_on="domain")

    # Write to analysis database
    update_analysis_database(
        df[["domain", "twitter_handle", "facebook_handle", "linkedin_handle"]]
    )

    # Save as JSON
    save_result(PIPELINE, df)
