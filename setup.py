import os
import sys
from pathlib import Path
import pandas as pd
from config import MAIN_DATABASE, ASSETS_DIR, EXPORT_DIR, EXPORT_GRAPHS_DIR
from models.Database import Database, Table, Column, Field, functions as fn
from helpers.get_registered_domain import get_registered_domain

# Set up export folders
Path(EXPORT_DIR).mkdir(parents=True, exist_ok=True)
Path(EXPORT_GRAPHS_DIR).mkdir(parents=True, exist_ok=True)

# Set up the overall database. Most pipelines export their findings into this
# database.

# Helper method for adding an INDEX to a table on a given column
def add_index(database, table, column):
    database.execute_sql(
        "CREATE INDEX IF NOT EXISTS {table}_{column} ON {table} ({column})".format(
            table=table, column=column
        )
    )


# Create database
db = Database(MAIN_DATABASE)

# Setup database
sdgs_score_columns = [Column("sdgs_score", "integer", nullable=True)]
for i in range(1, 18):
    sdgs_score_columns.append(Column(f"sdg{i}_score", "integer", nullable=True))

db.table("domain").create(
    Column("id", "integer", nullable=False),
    Column("domain", "text", nullable=False),
    Column("homepage", "text", nullable=False),
    Column("selected", "boolean", nullable=True),
    Column("sdg_champion", "boolean", nullable=True),
    Column("total_score", "integer", nullable=True),
    *sdgs_score_columns,
    Column("first_scraped_at", "timestamp", nullable=True),
    Column("selected_at", "timestamp", nullable=True),
    Column("scraped_at", "timestamp", nullable=True),
    Column("keywords_extracted_at", "timestamp", nullable=True),
    Column("scored_at", "timestamp", nullable=True),
).primary_key("id").unique("domain").if_not_exists().execute()

db.table("organization").create(
    Column("id", "integer", nullable=False),
    Column("domain_id", "integer", nullable=False),
    Column("name", "text", nullable=True),
    Column("commitment_url", "text", nullable=True),
    Column("alt_commitment_urls", "text", nullable=True),
    Column("logo", "text", nullable=True),
    Column("logo_hash", "text", nullable=True),
    Column("twitter_handle", "text", nullable=True),
    Column("facebook_handle", "text", nullable=True),
    Column("linkedin_handle", "text", nullable=True),
    Column("about", "text", nullable=True),
    Column("address", "text", nullable=True),
    Column("state", "text", nullable=True),
    Column("country", "text", nullable=True),
    Column("latitude", "text", nullable=True),
    Column("longitude", "text", nullable=True),
    Column("googlemaps_id", "text", nullable=True),
    Column("commitment_extracted_at", "timestamp", nullable=True),
    Column("links_extracted_at", "timestamp", nullable=True),
    Column("socials_extracted_at", "timestamp", nullable=True),
    Column("address_extracted_at", "timestamp", nullable=True),
    Column("address_cached_at", "timestamp", nullable=True),
    Column("name_extracted_at", "timestamp", nullable=True),
    Column("name_cached_at", "timestamp", nullable=True),
    Column("logo_extracted_at", "timestamp", nullable=True),
    Column("logo_cached_at", "timestamp", nullable=True),
    Column("about_extracted_at", "timestamp", nullable=True),
).foreign_key("domain_id", references="domain (id)").primary_key("id").unique(
    "domain_id"
).if_not_exists().execute()

db.table("url").create(
    Column("id", "integer", nullable=False),
    Column("domain_id", "integer", nullable=False),
    Column("url", "text", nullable=False),
    Column("level", "int", nullable=False),
    Column("html_file", "text", nullable=True),
    Column("error", "text", nullable=True),
    Column("word_count", "integer", nullable=True),
    Column("ignored", "boolean", nullable=True),
    Column("scraped_at", "timestamp", nullable=True),
    Column("keywords_extracted_at", "timestamp", nullable=True),
    Column("links_extracted_at", "timestamp", nullable=True),
).foreign_key("domain_id", references="domain (id)").primary_key("id").unique(
    "url"
).if_not_exists().execute()

db.table("keyword_match").create(
    Column("id", "integer", nullable=False),
    Column("url_id", "integer", nullable=False),
    Column("sdg", "text", nullable=False),
    Column("keyword", "text", nullable=False),
    Column("context", "text", nullable=False),
    Column("tag", "text", nullable=False),
).foreign_key("url_id", references="url (id)").primary_key(
    "id"
).if_not_exists().execute()

db.table("link").create(
    Column("id", "integer", nullable=False),
    Column("url_id", "integer", nullable=False),
    Column("target_domain_id", "integer", nullable=True),
    Column("target_url", "text", nullable=False),
).foreign_key("url_id", references="url (id)").foreign_key(
    "target_domain_id", references="domain (id)"
).primary_key(
    "id"
).if_not_exists().execute()

# Add index on foreign keys
add_index(db, table="organization", column="domain_id")
add_index(db, table="url", column="domain_id")
add_index(db, table="keyword_match", column="url_id")
add_index(db, table="link", column="url_id")
add_index(db, table="link", column="target_domain_id")

# Add index on timestamps
add_index(db, table="organization", column="commitment_extracted_at")
add_index(db, table="organization", column="links_extracted_at")
add_index(db, table="organization", column="socials_extracted_at")
add_index(db, table="organization", column="address_extracted_at")
add_index(db, table="organization", column="address_cached_at")
add_index(db, table="organization", column="name_extracted_at")
add_index(db, table="organization", column="name_cached_at")
add_index(db, table="organization", column="logo_extracted_at")
add_index(db, table="organization", column="logo_cached_at")
add_index(db, table="organization", column="about_extracted_at")
add_index(db, table="domain", column="selected_at")
add_index(db, table="domain", column="scraped_at")
add_index(db, table="domain", column="keywords_extracted_at")
add_index(db, table="domain", column="scored_at")
add_index(db, table="url", column="scraped_at")
add_index(db, table="url", column="keywords_extracted_at")
add_index(db, table="url", column="links_extracted_at")

# Create views
db.execute_sql(
    "CREATE VIEW IF NOT EXISTS organization_with_domain AS {query}".format(
        query=db.table("organization")
        .select("*")
        .join(Table("domain"))
        .on(Table("organization").domain_id == Table("domain").id)
        .get_sql()
    )
)
db.execute_sql(
    "CREATE VIEW IF NOT EXISTS domain_with_keyword_matches AS {query}".format(
        query=db.table("keyword_match")
        .select(
            "id",
            Table("domain").domain,
            Table("url").url,
            "sdg",
            "keyword",
            "context",
            "tag",
        )
        .join(Table("url"))
        .on(Table("keyword_match").url_id == Table("url").id)
        .join(Table("domain"))
        .on(Table("url").domain_id == Table("domain").id)
        .get_sql()
    )
)
db.execute_sql(
    "CREATE VIEW IF NOT EXISTS link_with_target_domain AS {query}".format(
        query=db.table("link")
        .select(
            "id",
            "url_id",
            "target_url",
            Table("domain").domain.as_("target_domain"),
        )
        .join(Table("domain"))
        .on(Table("link").target_domain_id == Table("domain").id)
        .get_sql()
    )
)
source_url = Table("url").as_("source_url").table
source_domain = Table("domain").as_("source_domain").table
target_domain = Table("domain").as_("target_domain").table
db.execute_sql(
    "CREATE VIEW IF NOT EXISTS link_with_source_and_target AS {query}".format(
        query=db.table("link")
        .select(
            "id",
            source_domain.id.as_("source_domain_id"),
            source_domain.domain.as_("source_domain"),
            source_url.url.as_("source_url"),
            target_domain.id.as_("target_domain_id"),
            target_domain.domain.as_("target_domain"),
            "target_url",
        )
        .join(source_url)
        .on(Table("link").url_id == source_url.id)
        .join(source_domain)
        .on(source_url.domain_id == source_domain.id)
        .join(target_domain)
        .on(Table("link").target_domain_id == target_domain.id)
        .get_sql()
    )
)
db.execute_sql(
    "CREATE VIEW IF NOT EXISTS referral AS {query}".format(
        query=db.view("link_with_source_and_target")
        .select(
            "source_domain_id", "source_domain", "target_domain_id", "target_domain"
        )
        .distinct()
        .join(Table("organization"))
        .on(
            Table("link_with_source_and_target").source_domain_id
            == Table("organization").domain_id
        )
        .orderby("source_domain")
        .orderby("target_domain")
        .get_sql()
    )
)
db.execute_sql(
    "CREATE VIEW IF NOT EXISTS domain_with_inbound_referrals AS {query}".format(
        query=db.table("domain")
        .select(
            Table("domain").star,
            fn.Count(Field("source_domain_id")).as_("inbound_referral_count"),
            fn.GroupConcat(Field("source_domain")).as_("inbound_referrals"),
        )
        .left_join(Table("referral"))
        .on(Table("domain").id == Table("referral").target_domain_id)
        .groupby("id")
        .get_sql()
    )
)
# View for listing connections between organizations
db.execute_sql(
    "CREATE VIEW IF NOT EXISTS connection AS {query}".format(
        query=db.view("referral")
        .select(
            "source_domain_id", "source_domain", "target_domain_id", "target_domain"
        )
        .join(Table("organization"))
        .on(Table("referral").target_domain_id == Table("organization").domain_id)
        .orderby("source_domain")
        .orderby("target_domain")
        .get_sql()
    )
)

# Seed the database from CSV file
seed = pd.read_csv(os.path.join(ASSETS_DIR, "seed-urls.csv"))
seed["url"] = seed["url"].apply(
    lambda url: f"http://{url}"
    if (not url.startswith("http://") and not url.startswith("https://"))
    else url
)
seed["domain"] = seed["url"].apply(lambda url: get_registered_domain(url))

# Insert domains into the database
with db.start_transaction() as transaction:
    for index, row in seed.iterrows():
        sys.stdout.write("Seeding " + row["url"] + " ... ")
        db.table("domain").insert(domain=row["domain"], homepage=row["url"]).execute(
            transaction=transaction
        )
        print("✅")

print("Database", f"{db.name}.sqlite", "was successfully set up ✅")
