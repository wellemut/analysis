from pathlib import Path
from datetime import datetime
from operator import itemgetter
from config import MAIN_DATABASE
from models.Database import Database, Field
from models import PipelineProgressBar
from models.GoogleMapsAPI import GoogleMapsAPI

PIPELINE = Path(__file__).stem

# German to English
GERMAN_STATES = {
    "Baden-Württemberg": "Baden-Württemberg",
    "Bayern": "Bavaria",
    "Berlin": "Berlin",
    "Brandenburg": "Brandenburg",
    "Bremen": "Bremen",
    "Hamburg": "Hamburg",
    "Hessen": "Hesse",
    "Niedersachsen": "Lower Saxony",
    "Mecklenburg-Vorpommern": "Mecklenburg-Vorpommern",
    "Nordrhein-Westfalen": "North Rhine-Westphalia",
    "Rheinland-Pfalz": "Rhineland-Palatinate",
    "Saarland": "Saarland",
    "Sachsen": "Saxony",
    "Sachsen-Anhalt": "Saxony-Anhalt",
    "Schleswig-Holstein": "Schleswig-Holstein",
    "Thüringen": "Thuringia",
}


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

        # Extract country & state
        components = result.get("address_components", [])
        country = next(
            (c["long_name"] for c in components if "country" in c["types"]), None
        )
        state = next(
            (
                c["long_name"]
                for c in components
                if "administrative_area_level_1" in c["types"]
            ),
            None,
        )

        # If country is not Germany, do not store address and geocoordinates
        if country is not None and country != "Germany":
            result = {"place_id": result["place_id"]}

        # For German states, convert names to English
        if state is not None and country == "Germany":
            state = GERMAN_STATES.get(state, state)
            if state not in GERMAN_STATES.values():
                raise Exception(
                    f"{state} must be in English and one of the 16 German states"
                )

        # Write to table
        db.table("organization").set(
            googlemaps_id=result.get("place_id", None),
            address=result.get("formatted_address", None),
            state=state,
            country=country,
            latitude=result.get("geometry", {}).get("location", {}).get("lat", None),
            longitude=result.get("geometry", {}).get("location", {}).get("lng", None),
            address_extracted_at=datetime.utcnow(),
            address_cached_at=result.get("cached_at", None),
        ).where(Field("domain_id") == domain_id).execute()
