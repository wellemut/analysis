import os
import csv
from models import Website

# Initialize the websites to scrape from URLs provided in data/seed.csv
with open(os.path.join("data", "seed.csv")) as file:
    reader = csv.DictReader(file)
    for row in reader:
        domain = Website.domain_from_url(row["url"])
        Website.create(
            domain=domain,
            # Write any kind of data into the meta key (for example, external
            # record IDs)
            meta=dict(external_id=int(row["id"]), name=row["name"]),
        )
