# Find a URL in the database
import sqlite3
from .config import DATABASE_PATH

def find_url(url):
    # Connect to the database
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    query = connection.cursor()

    # Find URL
    query.execute('''SELECT * FROM urls WHERE url=:url LIMIT 1''',
                    {
                        "url": url,
                    })
    result = query.fetchone()

    # Save (commit) the changes
    connection.commit()


    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    connection.close()

    return result
