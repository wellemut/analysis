from pathlib import Path
from datetime import datetime
from operator import itemgetter
from config import MAIN_DATABASE
from models.Database import Database, Table, Field, functions as fn
from models import PipelineProgressBar
from models.GoogleMapsAPI import GoogleMapsAPI

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    # Create database
    db = Database(MAIN_DATABASE)

    # Get domain IDs to extract address for
    domain_ids = (
        db.view("organization_with_domain")
        .as_("organization")
        .select("domain_id")
        .where(
            (Field("address_extracted_at").isnull())
            | (Field("address_extracted_at") < Field("scraped_at"))
        )
        .values()
    )

    gmaps = GoogleMapsAPI()
    progress = PipelineProgressBar(PIPELINE)
    for domain_id in progress.iterate(domain_ids):
        # Get domain
        domain, homepage = itemgetter("domain", "homepage")(
            db.table("domain")
            .select("domain", "homepage")
            .where(Field("id") == domain_id)
            .first()
        )
        progress.set_status(f"Analyzing {domain}")

        # Get address
        result = gmaps.find_by_url(homepage) or {}

        # Write to table
        db.table("organization").set(
            address=result.get("formatted_address", None),
            latitude=result.get("geometry", {}).get("location", {}).get("lat", None),
            longitude=result.get("geometry", {}).get("location", {}).get("lng", None),
            address_extracted_at=result.get("cached_at", datetime.utcnow()),
        ).where(Field("domain_id") == domain_id).execute()
