import os
import shutil
from database.config import DATABASE_PATH
from database.add_analysis_columns import add_analysis_columns

# Copy database from scrape/
if os.path.exists(DATABASE_PATH):
    raise Exception("Destination file exists!")
else:
    shutil.copy(
        os.path.join("..", "scrape", "database", "database.sqlite"),
        DATABASE_PATH
    )

# Add columns
add_analysis_columns()
