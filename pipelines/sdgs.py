from pathlib import Path
import json
from pymaybe import maybe
from bs4 import BeautifulSoup
import pandas as pd
from database import Database, Table, Column, Field, Order
from helpers.get_urls_table_from_scraped_database import (
    get_urls_table_from_scraped_database,
)
from helpers.is_binary_string import is_binary_string
from helpers.find_sdg_keywords_in_text import find_sdg_keywords_in_text
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
    ).foreign_key("url_id", references="urls (id)", on_delete="CASCADE").primary_key(
        "id"
    ).if_not_exists().execute()

    # Add index on foreign key matches.url_id
    db.execute_sql(
        "CREATE INDEX IF NOT EXISTS matches_url_id_index ON matches (url_id)"
    )

    # Clear records for domain/url
    if reset:
        db.table("urls").delete().where(
            Field("domain").glob_unless_none(domain)
            & Field("url").glob_unless_none(url)
        ).execute()

    # Fetch IDs for domain/url from scrape database
    scraped_urls = get_urls_table_from_scraped_database()
    ids_of_scraped_records = (
        scraped_urls.select("id")
        .where(
            Field("domain").glob_unless_none(domain)
            & Field("url").glob_unless_none(url)
            & Field("html").notnull()
        )
        .orderby("domain", order=Order.desc)
        .orderby("id")
        .fetch_values()
    )

    # Fetch analyzed URLs
    analyzed_urls = db.table("urls").select("url").fetch_values()

    # Analyze each HTML snippet in database
    for index, scraped_record_id in enumerate(ids_of_scraped_records):
        scraped_record = (
            scraped_urls.select("id", "domain", "url", "html")
            .where(Field("id") == scraped_record_id)
            .fetch()
        )
        id = scraped_record["id"]
        domain = scraped_record["domain"]
        url = scraped_record["url"]
        html = scraped_record["html"]

        # If this URL has already been analyzed, let's skip it.
        if analyzed_urls.count(url) >= 1:
            print("Skipping", url, "...", "Already done")
            continue

        # If this URL contains binary text, let's skip it
        if is_binary_string(html):
            print("Skipping", url, "...", "Binary file detected")
            continue

        print(
            "({current}/{total})".format(
                current=index, total=len(ids_of_scraped_records)
            ),
            "Searching for keywords in scraped HTML for",
            url,
            end=" ... ",
            flush=True,
        )

        # Prepare text extraction from HTML
        soup = BeautifulSoup(html, "html.parser")
        word_count = len(soup.get_text(separator=" ", strip=True).split())

        # Search for matches in the HTML
        # After an item is parsed/searced, we remove the item with decompose(),
        # so that we avoid duplicates (if one tag is nested inside another, for
        # example)
        matches = []

        # Search page title
        title = maybe(soup.head).find("title").or_none()
        if title:
            matches.extend(
                find_sdg_keywords_in_text(
                    title.get_text(separator=" ").strip(), tag="title"
                )
            )
            title.decompose()

        # Search page meta description
        description = maybe(soup.head).select_one('meta[name="description"]').or_none()
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
            new_url = (
                db.table("urls")
                .insert(domain=domain, url=url, word_count=word_count)
                .execute_in_transaction(transaction)
            )
            for match in matches:
                db.table("matches").insert(
                    url_id=new_url["lastrowid"],
                    sdg=match["sdg"],
                    keyword=match["keyword"],
                    context=match["context"],
                    tag=match["tag"],
                ).execute_in_transaction(transaction)

            transaction.commit()

        print("Done")

    print("Exporting to dataframe...")

    # Get data
    df = (
        db.table("urls")
        .join(Table("matches"))
        .on(Table("urls").id == Table("matches").url_id)
        .select("domain", "url", "word_count", Table("matches").sdg)
        .to_dataframe()
    )

    # Prepare aggregating by URL
    def aggregate_rows_by_url(row):
        d = {}

        d["word_count"] = row["word_count"].max()

        # Count SDG matches
        sdg_keys = list("sdg" + str(i) for i in range(1, 18))
        for key in ["sdgs", *sdg_keys]:
            d[key + "_matches_count"] = (row["sdg"] == key).sum()

        return pd.Series(d)

    # Aggregate by URL
    df = df.groupby(by=["domain", "url"]).apply(aggregate_rows_by_url)
    df = df.reset_index()

    # Prepare aggregating by domain
    def aggregate_rows_by_domain(row):
        d = {}

        for column in row.columns:
            if column.endswith("_matches_count") or column == "word_count":
                d[column] = row[column].sum()

        return pd.Series(d)

    # Aggregate by domain
    df = df.groupby(by=["domain"]).apply(aggregate_rows_by_domain)
    df = df.reset_index()

    # Sort
    df = df.sort_values(by=["domain"])

    # Save as JSON
    save_result(PIPELINE, df)
