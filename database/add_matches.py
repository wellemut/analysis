# Add matches to a URL
import sqlite3
import datetime
import json
from .config import DATABASE_PATH
from .find_url import find_url

def add_matches(url, matches, word_count):
    # Connect to the database
    connection = sqlite3.connect(DATABASE_PATH)
    query = connection.cursor()

    # Find URL
    url_object = find_url(url)

    # Add scraped HTML to the URL
    query.execute('''UPDATE urls
                    SET matches=:matches,
                        word_count=:word_count,
                        analyzed_at=:analyzed_at
                    WHERE id=:id''',
                    {
                        "matches": json.dumps(matches),
                        "word_count": word_count,
                        "id": url_object["id"],
                        "analyzed_at": datetime.datetime.utcnow()
                    })

    # Save (commit) the changes
    connection.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    connection.close()
