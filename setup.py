from config import MAIN_DATABASE
from models.Database import Database, Table, Column

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
    Column("total_score", "integer", nullable=True),
    *sdgs_score_columns,
    Column("first_scraped_at", "timestamp", nullable=True),
    Column("scraped_at", "timestamp", nullable=True),
    Column("keywords_extracted_at", "timestamp", nullable=True),
    Column("scored_at", "timestamp", nullable=True),
).primary_key("id").unique("domain").if_not_exists().execute()

db.table("organization").create(
    Column("id", "integer", nullable=False),
    Column("domain_id", "integer", nullable=False),
    Column("name", "text", nullable=True),
    Column("logo", "text", nullable=True),
    Column("twitter_handle", "text", nullable=True),
    Column("facebook_handle", "text", nullable=True),
    Column("linkedin_handle", "text", nullable=True),
    Column("summary", "text", nullable=True),
    Column("address", "text", nullable=True),
    Column("latitude", "text", nullable=True),
    Column("longitude", "text", nullable=True),
    Column("links_extracted_at", "timestamp", nullable=True),
).foreign_key("domain_id", references="domain (id)").primary_key("id").unique(
    "domain_id"
).if_not_exists().execute()

db.table("url").create(
    Column("id", "integer", nullable=False),
    Column("domain_id", "integer", nullable=False),
    Column("url", "text", nullable=False),
    Column("level", "int", nullable=False),
    Column("html", "text", nullable=True),
    Column("error", "text", nullable=True),
    Column("word_count", "integer", nullable=True),
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
    Column("target_domain", "text", nullable=False),
    Column("target_url", "text", nullable=False),
).foreign_key("url_id", references="url (id)").primary_key(
    "id"
).if_not_exists().execute()

# Add index on foreign keys
add_index(db, table="organization", column="domain_id")
add_index(db, table="url", column="domain_id")
add_index(db, table="keyword_match", column="url_id")
add_index(db, table="link", column="url_id")

# Add index on timestamps
add_index(db, table="organization", column="links_extracted_at")
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

# Seed the database
db.table("domain").insert(domain="dgvn.de", homepage="https://dgvn.de/").execute()
db.table("domain").insert(
    domain="die-gdi.de", homepage="https://www.die-gdi.de"
).execute()

print("Database", f"{db.name}.sqlite", "was successfully set up ✅")
# TODO: Insert initial domains
# print("Added", (count_after - count_before), "new domains")
# print("Total domains in database:", count_after)
