import os
from pathlib import Path
from datetime import datetime
from operator import itemgetter
import urllib.request
from config import MAIN_DATABASE, LOGOS_DIR
from models.Database import Database, Field
from models import PipelineProgressBar
from models.TwitterAPI import TwitterAPI

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    # Create database
    db = Database(MAIN_DATABASE)

    # Get domain IDs to download logo for
    domain_ids = (
        db.table("organization")
        .select("domain_id")
        .where(
            (
                Field("logo_extracted_at").isnull()
                & Field("socials_extracted_at").notnull()
            )
            | (Field("logo_extracted_at") < Field("socials_extracted_at"))
        )
        .values()
    )

    # Create logos directory
    Path(LOGOS_DIR).mkdir(parents=True, exist_ok=True)

    twitter = TwitterAPI()
    progress = PipelineProgressBar(PIPELINE)
    for domain_id in progress.iterate(domain_ids):
        # Get domain
        domain, twitter_handle = itemgetter("domain", "twitter_handle")(
            db.view("organization_with_domain")
            .select("domain", "twitter_handle")
            .where(Field("domain_id") == domain_id)
            .first()
        )
        progress.set_status(f"Analyzing {domain}")

        # Get logo url
        file_name = None
        logo_extracted_at = datetime.utcnow()
        if twitter_handle is not None:
            profile = twitter.get_profile(twitter_handle)

            if "error" in profile:
                progress.print(profile["error"]["detail"])
            else:
                # Download image
                image_url = profile["data"]["profile_image_url"].replace(
                    "_normal", "_200x200"
                )
                file_name = f"{twitter_handle}.{image_url.split('.')[-1]}"
                file_path = os.path.join(LOGOS_DIR, file_name)
                urllib.request.urlretrieve(image_url, file_path)
                logo_extracted_at = profile["cached_at"]

        # Write logo to database
        db.table("organization").set(
            logo=file_name, logo_extracted_at=logo_extracted_at
        ).where(Field("domain_id") == domain_id).execute()
