from pathlib import Path
from datetime import datetime
from operator import itemgetter
import re
from bs4 import BeautifulSoup
from config import MAIN_DATABASE
from models.Database import Database, Table, Column, Field, Order
from models import PipelineProgressBar
from helpers.is_binary_string import is_binary_string
from helpers.get_registered_domain import get_registered_domain

PIPELINE = Path(__file__).stem

# This ignores links to javascript functions, internal links, etc...
URL_REGEX = re.compile(r"^(?:https?|mailto|tel):", flags=re.IGNORECASE)


def run_pipeline(domain, url, reset):
    # Create database
    db = Database(MAIN_DATABASE)

    # TODO: Support for select analysis + resetting
    # # Clear records for domain/url
    # if reset:
    #     with db.start_transaction() as transaction:
    #         db.table("links").delete().where(
    #             Table("links").url_id.isin(
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
        db.view("organization_with_domain")
        .as_("organization")
        .select("domain_id")
        .where(
            (Field("links_extracted_at").isnull())
            | (Field("links_extracted_at") < Field("scraped_at"))
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
                (Field("links_extracted_at") < Field("scraped_at"))
                | (Field("scraped_at").notnull() & Field("links_extracted_at").isnull())
            )
            .values()
        )

        url_progress = progress.add_bar(domain)
        for url_id in url_progress.iterate(url_ids):
            url, html = itemgetter("url", "html")(
                db.table("url")
                .select("url", "html")
                .where(Field("id") == url_id)
                .first()
            )

            url_progress.set_status(f"Analyzing {url}")

            # If this URL contains binary text, let's skip it
            if is_binary_string(html):
                progress.print("Skipping", url, "...", "Binary file detected")
                db.table("url").set(links_extracted_at=datetime.utcnow()).execute()
                continue

            # Prepare text extraction from HTML
            soup = BeautifulSoup(html, "lxml")

            # Search for links to Twitter, Facebook, or LinkedIn
            links = []

            # Find all anchor tags and extract hrefs
            anchors = soup.find_all("a")
            hrefs = list(filter(None, [anchor.get("href", "") for anchor in anchors]))

            # Keep only url matching our pattern
            hrefs = list(filter(lambda href: URL_REGEX.match(href), hrefs))

            # Identify link domain
            for href in hrefs:
                links.append({"url": href, "domain": get_registered_domain(href)})

            # Ignore links to the same domain
            registered_domain = get_registered_domain(url)
            links = list(
                filter(lambda link: link["domain"] != registered_domain, links)
            )

            # Write links to database
            with db.start_transaction() as transaction:
                # Delete existing links
                db.table("link").delete().where(Field("url_id") == url_id).execute(
                    transaction=transaction
                )
                # Write new matches
                for link in links:
                    db.table("link").insert(
                        url_id=url_id,
                        target_domain=link["domain"],
                        target_url=link["url"],
                    ).execute(transaction=transaction)
                # Update timestamp
                db.table("url").set(links_extracted_at=datetime.utcnow()).where(
                    Field("id") == url_id
                ).execute(transaction=transaction)

        db.table("organization").set(links_extracted_at=datetime.utcnow()).where(
            Field("domain_id") == domain_id
        ).execute()
