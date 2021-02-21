import os
from pathlib import Path
import urllib.request
from urllib.parse import urlparse
import googlemaps
from models.Database import Database, Table, Column, Field, Order
from models import PipelineProgressBar
from helpers.get_urls_table_from_scraped_database import (
    get_urls_table_from_scraped_database,
)
from helpers.get_registered_domain import get_registered_domain
from helpers.update_analysis_database import update_analysis_database
from helpers.save_result import save_result

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    # Create database
    db = Database("gmaps")

    db.table("domains").create(
        Column("id", "integer", nullable=False),
        Column("domain", "text", nullable=False),
        Column("name", "text", nullable=True),
        Column("address", "text", nullable=True),
        Column("phone", "text", nullable=True),
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

    scraped_urls = get_urls_table_from_scraped_database()
    with scraped_urls.database.start_transaction() as transaction:
        scraped_urls.database.attach(db, name="analysis", transaction=transaction)

        domains_to_analyze = (
            scraped_urls.select("domain")
            .distinct()  # NOTE: Temporary use of distinct due to duplicate domains
            .where(
                Field("domain").glob_unless_none(domain)
                & (Field("level") == 0)
                & (Field("html").notnull())
                & Field("domain").notin(
                    db.table("domains").schema("analysis").select("domain")
                )
            )
            .orderby("domain", order=Order.desc)
            .orderby("id")
            .values(transaction=transaction)
        )

    # GoogleMaps API
    gmaps = googlemaps.Client(key=os.environ["GOOGLE_MAPS_API_KEY"])

    # Analyze each HTML snippet in database
    progress = PipelineProgressBar(PIPELINE)
    for domain in progress.iterate(domains_to_analyze):

        progress.set_current_url(domain)

        # Normalized domain
        normalized_domain = get_registered_domain(domain)
        result = {}

        # Find place
        result = gmaps.find_place(
            domain,
            "textquery",
            fields=["name", "formatted_address", "place_id"],
            language="en",
            location_bias="point:51.1657,10.4515",
        )
        candidates = result["candidates"]

        # Analyze each candidate, looking for match between search domain and
        # candidate domain
        for candidate in candidates:
            match = gmaps.place(
                candidate["place_id"],
                fields=[
                    "name",
                    "website",
                    "formatted_address",
                    # Returns address in adr microformat:
                    # http://microformats.org/wiki/adr
                    # "adr_address",
                    "international_phone_number",
                ],
                language="en",
            )["result"]

            normalized_candidate_domain = get_registered_domain(
                match.get("website", "")
            )

            if normalized_domain == normalized_candidate_domain:
                result = match
                break

        db.table("domains").insert(
            domain=domain,
            address=result.get("formatted_address", None),
            name=result.get("name", None),
            phone=result.get("international_phone_number", None),
        ).execute()

    # Get data
    df = (
        db.table("domains")
        .select(
            "domain",
            "name",
            "address",
            "phone",
        )
        .to_dataframe()
    )

    print("Scraped", df["address"].count(), "/", len(df.index), "addresses")

    # Remove completely empty rows
    df = df[df.filter(regex="^(?!domain).+$").notnull().any(axis=1)]

    # Sort
    df = df.sort_values(by=["domain"])

    # Save as JSON
    save_result(PIPELINE, df)
