from config import MAIN_DATABASE
from models.Database import Database, Table, Column

# Set up the overall database. Most pipelines export their findings into this
# database.

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
    Column("analyzed_at", "timestamp", nullable=True),
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
    Column("analyzed_at", "timestamp", nullable=True),
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

# Add index on foreign keys
db.execute_sql(
    "CREATE INDEX IF NOT EXISTS organization_domain_id ON organization (domain_id)"
)
db.execute_sql("CREATE INDEX IF NOT EXISTS url_domain_id ON url (domain_id)")
db.execute_sql(
    "CREATE INDEX IF NOT EXISTS keyword_match_url_id ON keyword_match (url_id)"
)

# Add index on timestamps
db.execute_sql("CREATE INDEX IF NOT EXISTS domain_scraped_at ON domain (scraped_at)")
db.execute_sql("CREATE INDEX IF NOT EXISTS domain_analyzed_at ON domain (analyzed_at)")
db.execute_sql("CREATE INDEX IF NOT EXISTS domain_scored_at ON domain (scored_at)")
db.execute_sql("CREATE INDEX IF NOT EXISTS url_scraped_at ON url (scraped_at)")
db.execute_sql("CREATE INDEX IF NOT EXISTS url_analyzed_at ON url (analyzed_at)")

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
