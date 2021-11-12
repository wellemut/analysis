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
            (
                Table("domain").keywords_extracted_at.notnull()
                & Table("domain").scored_at.isnull()
            )
            | (Table("domain").scored_at < Table("domain").keywords_extracted_at)
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

        # Is SDG champion? (aka at least one mention of SDGs)
        sdgs_count = df.set_index("sdg")["count"].to_dict().get("sdgs", 0)
        is_sdg_champion = sdgs_count >= 1

        # Calculate percentages
        df["percent"] = round(df["count"] / word_count * 100, 2)

        # Calculate scores
        df["target"] = df["sdg"].apply(lambda x: 2.5 if x == "sdgs" else 10.0)
        df["minimum"] = df["sdg"].apply(lambda x: 0.1 if x == "sdgs" else 0.4)
        df["score"] = round(
            (df["percent"] - df["minimum"]) / (df["target"] - df["minimum"]) * 100, 2
        ).clip(upper=100, lower=0)

        # Pivot
        df = df[["sdg", "score"]].set_index("sdg").T

        # Calculate total score
        total_score = round(df.sum(axis=1) / 500 * 100, 2).clip(upper=100)[0]

        # Add missing SDGs (set to none)
        for goal in range(1, 18):
            if f"sdg{goal}" not in df.columns:
                df[f"sdg{goal}"] = None

        # Rename all columns to end with _score
        df = df.rename(columns=lambda x: x + "_score")

        # Write results to database
        with db.start_transaction() as transaction:
            db.table("domain").set(
                sdg_champion=is_sdg_champion,
                total_score=total_score,
                scored_at=datetime.utcnow(),
                **next(iter(df.to_dict(orient="records")), {}),
            ).where(Field("id") == domain_id).execute(transaction=transaction)

            # Add or remove from organization table
            organization = db.table("organization")
            if is_sdg_champion:
                organization.insert(domain_id=domain_id,).on_conflict(
                    organization.domain_id
                ).do_nothing().execute(transaction=transaction)
            else:
                organization.delete().where(Field("domain_id") == domain_id).execute(
                    transaction=transaction
                )
