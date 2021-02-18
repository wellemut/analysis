from pathlib import Path
import json
from pymaybe import maybe
from bs4 import BeautifulSoup
import pandas as pd
from models.Database import Database, Table, Column, Field, Order
from models import PipelineProgressBar
from helpers.get_urls_table_from_scraped_database import (
    get_urls_table_from_scraped_database,
)
from helpers.is_binary_string import is_binary_string
from helpers.find_sdg_keywords_in_text import find_sdg_keywords_in_text
from helpers.update_analysis_database import update_analysis_database
from helpers.save_result import save_result

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    # Create database
    db = Database("sdgs")

    db.table("urls").create(
        Column("id", "integer", nullable=False),
        Column("domain", "text", nullable=False),
        Column("url", "text", nullable=False),
        Column("word_count", "integer", nullable=False),
    ).primary_key("id").unique("url").if_not_exists().execute()

    db.table("matches").create(
        Column("id", "integer", nullable=False),
        Column("url_id", "text", nullable=False),
        Column("sdg", "text", nullable=False),
        Column("keyword", "text", nullable=False),
        Column("context", "text", nullable=False),
        Column("tag", "text", nullable=False),
        Column("CHECK(sdg <> '')"),
        Column("CHECK(keyword <> '')"),
        Column("CHECK(context <> '')"),
    ).foreign_key("url_id", references="urls (id)").primary_key(
        "id"
    ).if_not_exists().execute()

    # Add index on foreign key matches.url_id
    db.execute_sql(
        "CREATE INDEX IF NOT EXISTS matches_url_id_index ON matches (url_id)"
    )

    # Create view: combination of urls and matches
    db.execute_sql(
        "CREATE VIEW IF NOT EXISTS results AS {query}".format(
            query=db.table("urls")
            .select(
                "domain",
                "url",
                "word_count",
                Table("matches").sdg,
                Table("matches").keyword,
                Table("matches").context,
            )
            .join(Table("matches"))
            .on(Table("urls").id == Table("matches").url_id)
            .get_sql()
        )
    )

    # Create view: URLs without any matches
    db.execute_sql(
        "CREATE VIEW IF NOT EXISTS urls_without_matches AS {query}".format(
            query=db.table("urls")
            .select(
                "domain",
                "url",
            )
            .where(
                Table("urls").id.notin(db.table("matches").select("url_id").distinct())
            )
            .get_sql()
        )
    )

    # Clear records for domain/url
    if reset:
        with db.start_transaction() as transaction:
            db.table("matches").delete().where(
                Table("matches").url_id.isin(
                    db.table("urls")
                    .select("id")
                    .where(
                        Field("domain").glob_unless_none(domain)
                        & Field("url").glob_unless_none(url)
                    )
                )
            ).execute(transaction=transaction)
            db.table("urls").delete().where(
                Field("domain").glob_unless_none(domain)
                & Field("url").glob_unless_none(url)
            ).execute(transaction=transaction)

    # Fetch IDs for domain/url from scrape database, ignoring URLs already
    # scraped
    print(
        "Skipping",
        db.table("urls").count("id").value(),
        "URLs already analyzed...",
    )

    scraped_urls = get_urls_table_from_scraped_database()
    with scraped_urls.database.start_transaction() as transaction:
        scraped_urls.database.attach(db, name="analysis", transaction=transaction)

        ids_of_scraped_records = (
            scraped_urls.select("id")
            .where(
                Field("domain").glob_unless_none(domain)
                & Field("url").glob_unless_none(url)
                & Field("html").notnull()
                & Field("url").notin(db.table("urls").schema("analysis").select("url"))
            )
            .orderby("domain", order=Order.desc)
            .orderby("id")
            .values(transaction=transaction)
        )

    # Analyze each HTML snippet in database
    progress = PipelineProgressBar(PIPELINE)
    for scraped_record_id in progress.iterate(ids_of_scraped_records):
        scraped_record = (
            scraped_urls.select("id", "domain", "url", "html")
            .where(Field("id") == scraped_record_id)
            .first()
        )
        id = scraped_record["id"]
        domain = scraped_record["domain"]
        url = scraped_record["url"]
        html = scraped_record["html"]

        progress.set_current_url(url)

        # If this URL contains binary text, let's skip it
        if is_binary_string(html):
            progress.print("Skipping", url, "...", "Binary file detected")
            db.table("urls").insert(domain=domain, url=url, word_count=0).execute()
            continue

        # Prepare text extraction from HTML
        soup = BeautifulSoup(html, "lxml")
        word_count = len(soup.get_text(separator=" ", strip=True).split())

        # Search for matches in the HTML
        # After an item is parsed/searced, we remove the item with decompose(),
        # so that we avoid duplicates (if one tag is nested inside another, for
        # example)
        matches = []

        # Search page title
        title = maybe(soup.head).find("title").or_else(None)
        if title:
            matches.extend(
                find_sdg_keywords_in_text(
                    title.get_text(separator=" ").strip(), tag="title"
                )
            )
            title.decompose()

        # Search page meta description
        description = (
            maybe(soup.head).select_one('meta[name="description"]').or_else(None)
        )
        if description:
            matches.extend(
                find_sdg_keywords_in_text(
                    description.get("content", "").strip(),
                    tag="meta description",
                )
            )
            description.decompose()

        # Search body
        SEARCH_TAGS = [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
        ]
        for tag in SEARCH_TAGS:
            for item in maybe(soup.body).find_all(tag).or_else([]):
                matches.extend(
                    find_sdg_keywords_in_text(item.get_text(separator=" ").strip(), tag)
                )
                item.decompose()

        matches.extend(
            find_sdg_keywords_in_text(soup.get_text(separator=" ").strip(), tag="other")
        )

        # Write matches to database
        with db.start_transaction() as transaction:
            new_url_id = (
                db.table("urls")
                .insert(domain=domain, url=url, word_count=word_count)
                .execute(
                    transaction=transaction, callback=lambda cursor: cursor.lastrowid
                )
            )
            for match in matches:
                db.table("matches").insert(
                    url_id=new_url_id,
                    sdg=match["sdg"],
                    keyword=match["keyword"],
                    context=match["context"],
                    tag=match["tag"],
                ).execute(transaction=transaction)

    print("Analyzing results...")

    # Get data
    df = db.view("results").select("domain", "url", "word_count", "sdg").to_dataframe()

    # Count sdgs
    sdgs_counts = (
        df.groupby(["domain", "sdg"])
        .size()
        .reset_index()
        .rename(columns={0: "count"})
        .pivot(index="domain", columns="sdg", values="count")
        .reset_index()
    )

    # Order sdg columns from 1 to 17
    sdgs_counts = sdgs_counts[["domain", "sdgs", *[f"sdg{i}" for i in range(1, 18)]]]

    # Count words
    word_counts = (
        df.groupby(["domain", "url"])
        .head(1)
        .groupby(["domain"])
        .sum()
        .reset_index()[["domain", "word_count"]]
    )

    # Merge sdg counts and word counts
    del df
    df = word_counts.merge(sdgs_counts, left_on="domain", right_on="domain")

    # Rename sdg columns: sdg9 -> sdg9_matches_count
    old_names = df.filter(regex="sdg").columns.tolist()
    new_names = []
    for name in old_names:
        new_names.append(name + "_count")
    df = df.rename(columns=dict(zip(old_names, new_names)))

    # Calculate %
    for column in df.filter(regex="sdg").columns:
        df[column.replace("count", "percent")] = round(
            df[column] / df["word_count"] * 100, 2
        )

    # Calculate scores
    for column in df.filter(regex="_percent").columns:
        bound = None
        if column == "sdgs_percent":
            bound = 2.5
        elif column.endswith("_percent"):
            bound = 10.0

        df[column.replace("percent", "score")] = round(
            df[column] / bound * 100, 2
        ).clip(upper=100)

    # Remove scores below 4
    for column in df.filter(regex="_score").columns:
        df[column] = df[column].mask(df[column] < 4)

    # Calculate total score
    df["total_score"] = round(
        df.filter(regex="_score").sum(axis=1) / 500 * 100, 2
    ).clip(upper=100)

    # Sort by total score, descending
    df = df.sort_values(by=["total_score"], ascending=False)

    # Write to analysis database
    update_analysis_database(
        df[
            [
                "domain",
                "total_score",
                "word_count",
                *df.filter(regex="sdg.+_score").columns,
                *df.filter(regex="sdg.+_count").columns,
            ]
        ]
    )

    # Save as JSON
    save_result(PIPELINE, df)
