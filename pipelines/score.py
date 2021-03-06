from pathlib import Path
from datetime import datetime
from config import MAIN_DATABASE
from models.Database import Database, Table, Field, functions as fn
from models import PipelineProgressBar

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    db = Database(MAIN_DATABASE)

    # Get domain IDs to score
    domain_ids = (
        db.table("domain")
        .select("id")
        .where(
            (Table("domain").analyzed_at.notnull() & Table("domain").scored_at.isnull())
            | (Table("domain").scored_at < Table("domain").analyzed_at)
        )
        .values()
    )

    progress = PipelineProgressBar(PIPELINE)
    for domain_id in progress.iterate(domain_ids):
        # Get domain
        domain = (
            db.table("domain").select("domain").where(Field("id") == domain_id).value()
        )

        progress.set_status(f"Scoring {domain}")

        # Get word count
        word_count = (
            db.table("url")
            .select(fn.Sum(Field("word_count")))
            .where(Field("domain_id") == domain_id)
            .value()
        )

        # Get keyword match count per SDG
        df = (
            db.table("keyword_match")
            .select("sdg", fn.Count("id").as_("count"))
            .join(Table("url"))
            .on(Table("keyword_match").url_id == Table("url").id)
            .where(Field("domain_id") == domain_id)
            .groupby(Field("sdg"))
            .to_dataframe()
        )

        # Calculate percentages
        df["percent"] = round(df["count"] / word_count * 100, 2)

        # Calculate scores
        df["target"] = df["sdg"].apply(lambda x: 2.5 if x == "sdgs" else 10.0)
        df["score"] = round(df["percent"] / df["target"] * 100, 2).clip(upper=100)

        # Remove scores below minimum score threshold
        df = df[df["score"] >= 4]

        # Pivot
        df = df[["sdg", "score"]].set_index("sdg").T

        # Calculate total score
        df["total"] = round(df.sum(axis=1) / 500 * 100, 2).clip(upper=100)

        # Rename all columns to end with _score
        df = df.rename(columns=lambda x: x + "_score")

        # Write results to database
        db.table("domain").set(
            **df.to_dict(orient="records")[0], scored_at=datetime.utcnow()
        ).where(Field("id") == domain_id).execute()
