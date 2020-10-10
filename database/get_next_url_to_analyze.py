# Return the next URL that needs analyzing
import sqlite3
from .config import DATABASE_PATH

def get_next_url_to_analyze():
    # Connect to the database
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    query = connection.cursor()

    # Find URL
    query.execute('''SELECT *
                     FROM urls
                     WHERE html IS NOT NULL
                     AND matches IS NULL
                     LIMIT 1''')
    result = query.fetchone()

    # Save (commit) the changes
    connection.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    connection.close()

    return result
