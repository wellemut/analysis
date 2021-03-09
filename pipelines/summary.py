from pathlib import Path
from datetime import datetime
from operator import itemgetter
from pymaybe import maybe
from bs4 import BeautifulSoup
from config import MAIN_DATABASE
from models.Database import Database, Field
from models import PipelineProgressBar

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    # Create database
    db = Database(MAIN_DATABASE)

    # Get domain IDs to summarize
    domain_ids = (
        db.view("organization_with_domain")
        .as_("organization")
        .select("domain_id")
        .where(
            (Field("summary_extracted_at").isnull())
            | (Field("summary_extracted_at") < Field("scraped_at"))
        )
        .values()
    )

    progress = PipelineProgressBar(PIPELINE)
    for domain_id in progress.iterate(domain_ids):
        # Get root-level HTML
        url, html = itemgetter("url", "html")(
            db.table("url")
            .select("url", "html")
            .where(Field("domain_id") == domain_id)
            .where(Field("level") == 0)
            .limit(1)
            .first()
        )
        progress.set_status(f"Summarizing {url}")

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

        # Write to table
        db.table("organization").set(
            summary=description,
            summary_extracted_at=datetime.utcnow(),
        ).where(Field("domain_id") == domain_id).execute()
