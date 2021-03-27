from pathlib import Path
from datetime import datetime
from operator import itemgetter
import pycountry
from config import MAIN_DATABASE
from models.GoogleMapsAPI import GoogleMapsAPI
from models.Database import Database, Table, Field, functions as fn, Order
from models import PipelineProgressBar

PIPELINE = Path(__file__).stem

# Reject a domain
def reject(domain_id):
    Database(MAIN_DATABASE).table("domain").set(
        selected=False, selected_at=datetime.utcnow()
    ).where(Field("id") == domain_id).execute()


def run_pipeline(domain, url, reset):
    db = Database(MAIN_DATABASE)

    # Get domain IDs to select or reject
    domain_ids = (
        db.view("domain_with_inbound_referrals")
        .select("id")
        .where(Field("selected_at").isnull())
        .orderby(Field("inbound_referral_count"), order=Order.desc)
        .values()
    )

    CC_TLDS = [country.alpha_2 for country in pycountry.countries]
    gmaps = GoogleMapsAPI()
    progress = PipelineProgressBar(PIPELINE)
    for domain_id in progress.iterate(domain_ids):
        # Get domain and homepage
        domain, homepage = itemgetter("domain", "homepage")(
            db.table("domain")
            .select("domain", "homepage")
            .where(Field("id") == domain_id)
            .first()
        )

        progress.set_status(f"Analyzing {domain}")

        # Get domain suffix
        suffix = domain.lower().split(".")[-1]

        # Reject domain if suffix is a country code TLD, other than Germany or EU
        if suffix not in ["de", "eu"] and suffix in CC_TLDS:
            reject(domain_id)
            continue

        # Get country for domain, based on address in GMaps
        # In future iterations, we may keep domains even when no address is
        # found. And/or scrape their address from Facebook or LinkedIn.
        components = (gmaps.find_by_url(homepage) or {}).get("address_components", [])
        country = next(
            (x["short_name"] for x in components if "country" in x["types"]), None
        )

        if country is None or country.upper() != "DE":
            reject(domain_id)
            continue

        # Accept domain
        db.table("domain").set(selected=True, selected_at=datetime.utcnow()).where(
            Field("id") == domain_id
        ).execute()
