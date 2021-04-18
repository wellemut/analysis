import os
from pathlib import Path
from datetime import datetime
from operator import itemgetter
import urllib.request
from config import MAIN_DATABASE
from models.Database import Database, Field
from models import PipelineProgressBar
from models.TwitterAPI import TwitterAPI
from models.GoogleMapsAPI import GoogleMapsAPI

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    # Create database
    db = Database(MAIN_DATABASE)

    # Get domain IDs to name
    domain_ids = (
        db.table("organization")
        .select("domain_id")
        .where(
            Field("socials_extracted_at").notnull()
            & Field("address_extracted_at").notnull()
        )
        .where(
            (Field("name_extracted_at").isnull())
            | (Field("name_extracted_at") < Field("socials_extracted_at"))
            | (Field("name_extracted_at") < Field("address_extracted_at"))
        )
        .values()
    )

    gmaps = GoogleMapsAPI()
    twitter = TwitterAPI()
    progress = PipelineProgressBar(PIPELINE)
    for domain_id in progress.iterate(domain_ids):
        # Get domain
        domain, twitter_handle, googlemaps_id = itemgetter(
            "domain", "twitter_handle", "googlemaps_id"
        )(
            db.view("organization_with_domain")
            .select("domain", "twitter_handle", "googlemaps_id")
            .where(Field("domain_id") == domain_id)
            .first()
        )
        progress.set_status(f"Naming {domain}")

        name = None
        name_cached_at = None

        # Check Google maps for name
        if googlemaps_id is not None:
            place = gmaps.find_by_id(googlemaps_id)
            name = place["result"]["name"]
            name_cached_at = place["cached_at"]

        # Check Twitter for name
        if name is None and twitter_handle is not None:
            profile = twitter.get_profile(twitter_handle)

            if "error" in profile:
                progress.print(profile["error"]["detail"])
            else:
                name = profile["data"]["name"]
                name_cached_at = profile["cached_at"]

        # Write name to database
        db.table("organization").set(
            name=name,
            name_extracted_at=datetime.utcnow(),
            name_cached_at=name_cached_at,
        ).where(Field("domain_id") == domain_id).execute()
