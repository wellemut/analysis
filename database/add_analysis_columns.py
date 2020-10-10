# Add match columns to the database
import sqlite3
from .config import DATABASE_PATH

def add_analysis_columns():
    # Connect to the database
    connection = sqlite3.connect(DATABASE_PATH)
    query = connection.cursor()

    # Add matches column
    query.execute('''ALTER TABLE urls ADD matches json''')
    query.execute('''ALTER TABLE urls ADD word_count int''')
    query.execute('''ALTER TABLE urls ADD analyzed_at timestamp''')

    # Save (commit) the changes
    connection.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    connection.close()
