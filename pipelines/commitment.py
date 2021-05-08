from pathlib import Path
from datetime import datetime
import json
from config import MAIN_DATABASE
from models.Database import (
    Database,
    Table,
    Field,
    functions as fn,
    Order,
    AliasedQuery,
    analytics,
)
from models import PipelineProgressBar

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    db = Database(MAIN_DATABASE)

    # Get domain IDs for which to extract commitment
    domain_ids = (
        db.view("organization_with_domain")
        .as_("organization")
        .select("domain_id")
        .where(
            (Field("commitment_extracted_at").isnull())
            | (Field("commitment_extracted_at") < Field("keywords_extracted_at"))
        )
        .values()
    )

    progress = PipelineProgressBar(PIPELINE)
    for domain_id in progress.iterate(domain_ids):
        # Get domain
        domain = (
            db.table("domain").select("domain").where(Field("id") == domain_id).value()
        )

        progress.set_status(f"Analyzing {domain}")

        # Get commitment URLs
        subquery = (
            db.table("keyword_match")
            .select(
                Table("url").url,
                "tag",
                "context",
                analytics.RowNumber().over(Field("url_id"))
                # Prioritize pages with SDGs in paragraph tag
                .orderby(Field("tag") == "p", order=Order.desc).as_("row_num"),
                # Count the total number of SDG mentions on each page
                analytics.Count("id").over(Field("url_id")).as_("count"),
            )
            .where(Field("sdg") == "sdgs")
            .join(Table("url"))
            .on(Table("keyword_match").url_id == Table("url").id)
            .where(Field("domain_id") == domain_id)
        )
        commitments = (
            db.with_(subquery, "subquery")
            .from_(AliasedQuery("subquery"))
            .select("url", "context", "tag", "count")
            # Return the first match (context & tag) for each URL
            .where(Field("row_num") == 1)
            .orderby(Field("count"), order=Order.desc)
            .all()
        )

        # Write results to database
        db.table("organization").set(
            commitment_url=commitments[0]["url"],
            alt_commitment_urls=json.dumps([dict(c) for c in commitments]),
            commitment_extracted_at=datetime.utcnow(),
        ).where(Field("domain_id") == domain_id).execute()
