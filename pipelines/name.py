import os
from pathlib import Path
import pandas as pd
from models.Database import Field, Order
from models import PipelineProgressBar
from helpers.get_urls_table_from_scraped_database import (
    get_urls_table_from_scraped_database,
)
from helpers.update_analysis_database import update_analysis_database
from helpers.save_result import save_result

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    # Load the CSV file of names, by domain
    names = pd.read_csv(
        Path(os.path.join(__file__, "..", "..", "files", "names.csv")).resolve()
    )

    # Load all domains
    # NOTE: We need to load distinct domains only, because we have a few
    # duplicates at the moment.
    scraped_urls = get_urls_table_from_scraped_database()
    domains = (
        scraped_urls.select("domain")
        .distinct()
        .where(Field("level") == 0)
        .orderby("domain", order=Order.desc)
        .orderby("id")
        .to_dataframe()
    )

    # Merge pandas
    df = domains.merge(names, how="outer", on="domain", indicator=True, validate="1:1")

    # Count names without domain
    unused_names = df[df["_merge"] == "right_only"]
    if len(unused_names.index) != 0:
        print(
            "Found",
            len(unused_names.index),
            "unused domain names:",
            ", ".join(unused_names["name"].values),
        )

    # Count names
    df = df[df["_merge"] != "right_only"]
    df = df.drop(columns=["_merge"])
    print("Found", df["name"].count(), "/", len(df.index), "names")

    # Count missing names
    missing = df[df["name"].isnull()]
    if len(missing.index) != 0:
        print("Missing:", ", ".join(missing["domain"].values))

    # Write to analysis database
    update_analysis_database(df[["domain", "name"]])

    # Save as JSON
    save_result(PIPELINE, df)
