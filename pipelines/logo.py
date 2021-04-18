from pathlib import Path
from datetime import datetime
from operator import itemgetter
import urllib.request
import hashlib
from config import MAIN_DATABASE
from models.Database import Database, Field
from models import PipelineProgressBar
from models.TwitterAPI import TwitterAPI
from models.CloudinaryApi import CloudinaryApi

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

    twitter = TwitterAPI()
    progress = PipelineProgressBar(PIPELINE)
    for domain_id in progress.iterate(domain_ids):
        # Get domain
        domain, twitter_handle, current_logo_url, current_logo_hash = itemgetter(
            "domain", "twitter_handle", "logo", "logo_hash"
        )(
            db.view("organization_with_domain")
            .select("domain", "twitter_handle", "logo", "logo_hash")
            .where(Field("domain_id") == domain_id)
            .first()
        )
        progress.set_status(f"Analyzing {domain}")

        # Get logo url
        logo = None
        logo_url = None
        logo_hash = None
        logo_cached_at = None

        if twitter_handle is not None:
            profile = twitter.get_profile(twitter_handle)

            if "errors" in profile:
                for error in profile["errors"]:
                    progress.print(error["detail"])
            else:
                profile_image_url = profile["data"]["profile_image_url"].replace(
                    "_normal", "_200x200"
                )
                logo = urllib.request.urlopen(profile_image_url).read()
                logo_cached_at = profile["cached_at"]

        if logo:
            logo_hash = hashlib.sha256(logo).hexdigest()

            # Upload new image
            if logo_hash != current_logo_hash:
                logo_url = CloudinaryApi.upload(logo)
            else:
                logo_url = current_logo_url

        # Write logo to database
        db.table("organization").set(
            logo=logo_url,
            logo_hash=logo_hash,
            logo_extracted_at=datetime.utcnow(),
            logo_cached_at=logo_cached_at,
        ).where(Field("domain_id") == domain_id).execute()
