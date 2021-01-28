from pathlib import Path
import json
from pymaybe import maybe
from bs4 import BeautifulSoup
import pandas as pd
from database import Database, Column, Field, Order
from helpers.get_scraped_database import get_scraped_database
from helpers.is_binary_string import is_binary_string
from helpers.find_sdg_keywords_in_text import find_sdg_keywords_in_text
from helpers.save_result import save_result

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    # Create database
    db = Database("sdgs")
    db.create(
        Column("id", "integer", nullable=False),
        Column("domain", "text", nullable=False),
        Column("url", "text", nullable=False),
        Column("sdg", "text", nullable=False),
        Column("keyword", "text", nullable=False),
        Column("context", "text", nullable=False),
        Column("tag", "text", nullable=False),
        Column("url_word_count", "integer", nullable=False),
        Column("CHECK(domain <> '')"),
        Column("CHECK(url <> '')"),
        Column("CHECK(sdg <> '')"),
        Column("CHECK(keyword <> '')"),
        Column("CHECK(context <> '')"),
    ).if_not_exists().primary_key("id").execute()

    # Clear records for domain/url
    if reset:
        db.delete().where(
            Field("domain").glob_unless_none(domain)
            & Field("url").glob_unless_none(url)
        ).execute()

    # Fetch IDs for domain/url from scrape database
    scraped_db = get_scraped_database()
    ids_of_scraped_records = (
        scraped_db.select("id")
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
    analyzed_urls = db.select("url").distinct().fetch_values()

    # Analyze each HTML snippet in database
    for scraped_record_id in ids_of_scraped_records:
        scraped_record = (
            scraped_db.select("id", "domain", "url", "html")
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
            "Searching for keywords in scraped HTML for", url, end=" ... ", flush=True
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
            for match in matches:
                db.insert(
                    domain=domain,
                    url=url,
                    sdg=match["sdg"],
                    keyword=match["keyword"],
                    context=match["context"],
                    tag=match["tag"],
                    url_word_count=word_count,
                ).execute_in_transaction(transaction)

            transaction.commit()

        print("Done")

    print("Exporting to dataframe...")

    # Get data
    df = db.to_pandas_dataframe("domain", "url", "sdg", "url_word_count")

    # Prepare aggregating by URL
    def aggregate_rows_by_url(row):
        d = {}

        d["word_count"] = row["url_word_count"].max()

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
