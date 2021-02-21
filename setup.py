from models.Database import Database, Table, Column, Field
from helpers.get_urls_table_from_scraped_database import (
    get_urls_table_from_scraped_database,
)

# Set up the overall analysis database. Each pipeline exports their findings
# into this database.

# Create database
db = Database("analysis")

sdgs_score_columns = [Column("sdgs_score", "integer", nullable=True)]
for i in range(1, 18):
    sdgs_score_columns.append(Column(f"sdg{i}_score", "integer", nullable=True))

sdgs_count_columns = [Column("sdgs_count", "integer", nullable=True)]
for i in range(1, 18):
    sdgs_count_columns.append(Column(f"sdg{i}_count", "integer", nullable=True))

db.table("domains").create(
    Column("id", "integer", nullable=False),
    Column("domain", "text", nullable=False),
    Column("url", "text", nullable=False),
    Column("name", "text", nullable=True),
    Column("total_score", "integer", nullable=True),
    *sdgs_score_columns,
    Column("logo", "text", nullable=True),
    Column("twitter_handle", "text", nullable=True),
    Column("facebook_handle", "text", nullable=True),
    Column("linkedin_handle", "text", nullable=True),
    Column("summary", "text", nullable=True),
    Column("address", "text", nullable=True),
    Column("latitude", "text", nullable=True),
    Column("longitude", "text", nullable=True),
    Column("word_count", "integer", nullable=True),
    *sdgs_count_columns,
).primary_key("id").unique("domain").unique("url").if_not_exists().execute()

count_before = db.table("domains").count("domain").value()

# Write domains to database
scraped_urls = get_urls_table_from_scraped_database()
with db.start_transaction() as transaction:
    db.attach(scraped_urls.database, name="scraped", transaction=transaction)

    # NOTE: We currently use .groupby() due to duplicate domains in scraped.sqlite
    db.table("domains").insert_in_columns("domain", "url").from_(
        scraped_urls.schema("scraped").table
    ).select("domain", "url").where(
        (Field("level") == 0)
        & Field("domain").notin(db.table("domains").select("domain"))
    ).groupby(
        "domain"
    ).execute(
        transaction=transaction
    )

count_after = db.table("domains").count("domain").value()

print("Database", f"{db.name}.sqlite", "was successfully set up ✅")
print("Added", (count_after - count_before), "new domains")
print("Total domains in database:", count_after)
