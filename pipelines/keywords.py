from pathlib import Path
from datetime import datetime
from operator import itemgetter
from pymaybe import maybe
from bs4 import BeautifulSoup
from config import MAIN_DATABASE
from models.Database import Database, Table, Field
from models import PipelineProgressBar
from helpers.is_binary_string import is_binary_string
from helpers.find_sdg_keywords_in_text import find_sdg_keywords_in_text
from helpers.should_ignore_url import should_ignore_url
from helpers.read_gzipped_asset import read_gzipped_asset

PIPELINE = Path(__file__).stem


# Write matches to database
def commit_to_database(database, url_id, word_count, matches, ignored):
    with database.start_transaction() as transaction:
        # Delete existing matches
        database.table("keyword_match").delete().where(
            Field("url_id") == url_id
        ).execute(transaction=transaction)
        # Write new matches
        for match in matches:
            database.table("keyword_match").insert(
                url_id=url_id,
                sdg=match["sdg"],
                keyword=match["keyword"],
                context=match["context"],
                tag=match["tag"],
            ).execute(transaction=transaction)
        # Update word count
        database.table("url").set(
            word_count=word_count,
            ignored=ignored,
            keywords_extracted_at=datetime.utcnow(),
        ).where(Field("id") == url_id).execute(transaction=transaction)


def run_pipeline(domain, url, reset):
    db = Database(MAIN_DATABASE)

    # Create view: combination of urls and matches
    # db.execute_sql(
    #     "CREATE VIEW IF NOT EXISTS results AS {query}".format(
    #         query=db.table("urls")
    #         .select(
    #             "domain",
    #             "url",
    #             "word_count",
    #             Table("matches").sdg,
    #             Table("matches").keyword,
    #             Table("matches").context,
    #         )
    #         .join(Table("matches"))
    #         .on(Table("urls").id == Table("matches").url_id)
    #         .get_sql()
    #     )
    # )

    # Create view: URLs without any matches
    # db.execute_sql(
    #     "CREATE VIEW IF NOT EXISTS urls_without_matches AS {query}".format(
    #         query=db.table("urls")
    #         .select(
    #             "domain",
    #             "url",
    #         )
    #         .where(
    #             Table("urls").id.notin(db.table("matches").select("url_id").distinct())
    #         )
    #         .get_sql()
    #     )
    # )

    # Clear records for domain/url
    # TODO: Enable support for reset
    # if reset:
    #     with db.start_transaction() as transaction:
    #         db.table("matches").delete().where(
    #             Table("matches").url_id.isin(
    #                 db.table("urls")
    #                 .select("id")
    #                 .where(
    #                     Field("domain").glob_unless_none(domain)
    #                     & Field("url").glob_unless_none(url)
    #                 )
    #             )
    #         ).execute(transaction=transaction)
    #         db.table("urls").delete().where(
    #             Field("domain").glob_unless_none(domain)
    #             & Field("url").glob_unless_none(url)
    #         ).execute(transaction=transaction)

    # Get domain IDs to analyze
    domain_ids = (
        db.table("domain")
        .select("id")
        .where(
            (Field("scraped_at").notnull() & Field("keywords_extracted_at").isnull())
            | (Field("keywords_extracted_at") < Field("scraped_at"))
        )
        .values()
    )

    progress = PipelineProgressBar(f"{PIPELINE}: DOMAINS")
    for domain_id in progress.iterate(domain_ids):
        # Get domain
        domain = (
            db.table("domain").select("domain").where(Field("id") == domain_id).value()
        )

        # Get url IDs to analyze
        url_ids = (
            db.table("url")
            .select("id")
            .where(Field("domain_id") == domain_id)
            .where(
                (Field("keywords_extracted_at") < Field("scraped_at"))
                | (
                    Field("scraped_at").notnull()
                    & Field("keywords_extracted_at").isnull()
                )
            )
            .where(Field("html_file").notnull())
            .values()
        )

        url_progress = progress.add_bar(domain)
        for url_id in url_progress.iterate(url_ids):
            url, html_file = itemgetter("url", "html_file")(
                db.table("url")
                .select("url", "html_file")
                .where(Field("id") == url_id)
                .first()
            )

            url_progress.set_status(f"Analyzing {url}")

            # If this is a non-content URL, let's ignore it
            if should_ignore_url(url):
                commit_to_database(
                    database=db,
                    url_id=url_id,
                    word_count=None,
                    matches=[],
                    ignored=True,
                )
                continue

            # Load html
            html = read_gzipped_asset(html_file)

            # If this URL contains binary text, let's skip it
            if is_binary_string(html):
                progress.print("Skipping", url, "...", "Binary file detected")
                commit_to_database(
                    database=db,
                    url_id=url_id,
                    word_count=0,
                    matches=[],
                    ignored=False,
                )
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
                        find_sdg_keywords_in_text(
                            item.get_text(separator=" ").strip(), tag
                        )
                    )
                    item.decompose()

            matches.extend(
                find_sdg_keywords_in_text(
                    soup.get_text(separator=" ").strip(), tag="other"
                )
            )

            commit_to_database(
                database=db,
                url_id=url_id,
                word_count=word_count,
                matches=matches,
                ignored=False,
            )

        db.table("domain").set(keywords_extracted_at=datetime.utcnow()).where(
            Field("id") == domain_id
        ).execute()
