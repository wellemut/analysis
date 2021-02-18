import os
from pathlib import Path
import urllib.request
from models.Database import Database, Table, Column, Field, Order
from models import PipelineProgressBar
from models import TwitterClient
from helpers.get_domains_table_from_analysis_database import (
    get_domains_table_from_analysis_database,
)
from helpers.update_analysis_database import update_analysis_database
from helpers.save_result import save_result

PIPELINE = Path(__file__).stem
LOGOS_DIR = Path(os.path.join(__file__, "..", "..", "files", "logos")).resolve()


def run_pipeline(domain, url, reset):
    # Create database
    db = Database("logos")

    db.table("domains").create(
        Column("id", "integer", nullable=False),
        Column("domain", "text", nullable=False),
        Column("logo", "text", nullable=True),
    ).primary_key("id").unique("domain").if_not_exists().execute()

    # Clear records for domain/url
    if reset:
        db.table("domains").delete().where(
            Field("domain").glob_unless_none(domain)
        ).execute()

    # Fetch IDs for level-0 domain from analysis database, ignoring URLs already
    # scraped
    print(
        "Skipping",
        db.table("domains").count("id").value(),
        "domains already analyzed...",
    )

    analyzed_domains = get_domains_table_from_analysis_database()
    with analyzed_domains.database.start_transaction() as transaction:
        analyzed_domains.database.attach(db, name="analysis", transaction=transaction)

        ids_of_domains_to_analyze = (
            analyzed_domains.select("id")
            .where(
                Field("domain").glob_unless_none(domain)
                & Field("domain").notin(
                    db.table("domains").schema("analysis").select("domain")
                )
                & (Field("twitter_handle").notnull())
            )
            .orderby("domain", order=Order.desc)
            .orderby("id")
            .values(transaction=transaction)
        )

    # Twitter API
    twitter = TwitterClient()

    # Set up logos folder
    os.makedirs(LOGOS_DIR, exist_ok=True)

    # Analyze each HTML snippet in database
    progress = PipelineProgressBar(PIPELINE)
    for domain_id in progress.iterate(ids_of_domains_to_analyze):
        scraped_record = (
            analyzed_domains.select("id", "domain", "twitter_handle")
            .where(Field("id") == domain_id)
            .first()
        )
        id = scraped_record["id"]
        domain = scraped_record["domain"]
        twitter_handle = scraped_record["twitter_handle"]

        progress.set_current_url(domain)

        # Request profile image from Twitter
        response = twitter.request(
            f"users/by/username/:{twitter_handle}?user.fields=profile_image_url"
        )
        data = response.json()

        if "error" in data:
            progress.print(data["error"]["detail"])
            db.table("domains").insert(domain=domain).execute()
            continue

        # Download image
        image_url = data["data"]["profile_image_url"].replace("_normal", "_200x200")
        file_name = f"{twitter_handle}.{image_url.split('.')[-1]}"
        file_path = os.path.join(LOGOS_DIR, file_name)
        urllib.request.urlretrieve(image_url, file_path)

        # Write summary to database
        db.table("domains").insert(domain=domain, logo=file_name).execute()

    # Get data
    df = (
        db.table("domains")
        .select(
            "domain",
            "logo",
        )
        .to_dataframe()
    )

    # Sort
    df = df.sort_values(by=["domain"])

    print("Downloaded", df["logo"].count(), "/", len(df.index), "logos")

    # Write to analysis database
    update_analysis_database(df[["domain", "logo"]])

    # Save as JSON
    save_result(PIPELINE, df)
