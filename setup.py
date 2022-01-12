import os
import csv
from models import Website
from helpers import get_domain_from_url

# Initialize the websites to scrape from URLs provided in data/seed.csv
with open(os.path.join("data", "seed.csv")) as file:
    reader = csv.DictReader(file)
    for row in reader:
        Website.create(
            domain=get_domain_from_url(row["url"]),
            # Optionally, set a homepage where the scraping should start from
            homepage=row["url"],
            # Write any kind of data into the meta key (for example, external
            # record IDs)
            meta=dict(external_id=int(row["id"]), name=row["name"]),
        )
