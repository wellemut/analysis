import os
import shutil
from helpers.get_scraped_database import get_scraped_database

database_path = get_scraped_database().file_path

# Copy database from scrape/
if os.path.exists(database_path):
    raise Exception("Destination file exists!")
else:
    shutil.copy(
        os.path.join("..", "scrape", "database", "database.sqlite"), database_path
    )
