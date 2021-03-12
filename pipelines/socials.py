from pathlib import Path
from datetime import datetime
import re
import pandas as pd
from config import MAIN_DATABASE
from models.Database import Database, Table, Column, Field, functions as fn
from models import PipelineProgressBar

PIPELINE = Path(__file__).stem

TWITTER_REGEX = re.compile(
    r"^(?:https?:)?\/\/(?:www\.)?twitter.com\/(?:#!\/)?(?!(?:intent|(?:[a-z]{2}\/)?privacy|hashtag|home|search|share|account|personalization)\b)(?P<handle>[A-Za-z0-9_]+)\/?",
    flags=re.IGNORECASE,
)
FACEBOOK_REGEX = re.compile(
    r"^(?:https?:)?\/\/(?:(?:www|m|mobile|touch|mbasic)\.)?(?:facebook|fb)\.(?:com|me)\/(?!(?:sharer|share|login|ads|policy|policies|settings|about|hashtag|help|events|groups|(?:v[0-9]+\.[0-9]+\/dialog))\b)(?:pg\/|pages\/(?:[^\/]+\/)*)?(?P<handle>[^\/_\?#@]+)\/?",
    flags=re.IGNORECASE,
)
LINKEDIN_REGEX = re.compile(
    r"(?:https?:)?\/\/(?:[a-z]{2,3}\.)?linkedin.com\/company/(?P<handle>[^\/\?#]+)\/?"
)
SOCIALS = [
    {"social": "twitter", "regex": TWITTER_REGEX, "domains": ["twitter.com"]},
    {
        "social": "facebook",
        "regex": FACEBOOK_REGEX,
        "domains": ["facebook.com", "fb.com", "fb.me"],
    },
    {"social": "linkedin", "regex": LINKEDIN_REGEX, "domains": ["linkedin.com"]},
]
DOMAIN_TO_SOCIAL_MAP = pd.DataFrame(
    data=[
        [domain, social["social"]] for social in SOCIALS for domain in social["domains"]
    ],
    columns=["domain", "social"],
)
SOCIAL_DOMAINS = DOMAIN_TO_SOCIAL_MAP["domain"].tolist()


def run_pipeline(domain, url, reset):
    # Create database
    db = Database(MAIN_DATABASE)

    # Get domain IDs to extract socials for
    domain_ids = (
        db.view("organization")
        .select("domain_id")
        .where(
            (
                Field("socials_extracted_at").isnull()
                & Field("links_extracted_at").notnull()
            )
            | (Field("socials_extracted_at") < Field("links_extracted_at"))
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

        # Get links
        links = (
            db.table("link")
            .select("target_url", "target_domain", fn.Count("id").as_("count"))
            .join(Table("url"))
            .on(Table("link").url_id == Table("url").id)
            .where(Field("domain_id") == domain_id)
            .where(Field("target_domain").isin(SOCIAL_DOMAINS))
            .groupby(Field("target_url"))
            .to_dataframe()
        )

        # Identify the social by joining with DOMAIN_TO_SOCIAL_MAP
        df = pd.merge(
            links,
            DOMAIN_TO_SOCIAL_MAP,
            how="left",
            left_on="target_domain",
            right_on="domain",
        )

        # No socials found, skip this domain
        if len(df.index) == 0:
            db.table("organization").set(
                socials_extracted_at=datetime.utcnow(),
            ).where(Field("domain_id") == domain_id).execute()
            continue

        # Apply the appropriate regex to each row
        def get_handle(row):
            regex = next(
                item["regex"] for item in SOCIALS if item["social"] == row["social"]
            )
            match = regex.match(row["target_url"])

            return match.group("handle").lower() if match else None

        df["handle"] = df.apply(get_handle, axis=1)

        # Count number of handles
        df = df.groupby(["social", "handle"])[["count"]].agg("sum").reset_index()

        # Sort dataset
        df = df.sort_values(by=["social", "count"], ascending=False)

        # Keep top 1-row for each hit
        df = df.groupby(["social"]).head(1)

        # Pivot frame
        df = df[["social", "handle"]].set_index("social").T

        # Rename all columns to end with _handle
        df = df.rename(columns=lambda x: x + "_handle")

        # Write results to database
        db.table("organization").set(
            socials_extracted_at=datetime.utcnow(),
            **next(iter(df.to_dict(orient="records")), {}),
        ).where(Field("domain_id") == domain_id).execute()
