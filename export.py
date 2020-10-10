# Export database to CSV file
import pandas as pd
import sqlite3
import json
from pathlib import Path
from database.config import DATABASE_PATH

def get_match_count(row, key):
    if row["scrape_error"]:
        return None

    return len(json.loads(row["matches"]).get(key, []))

# Read database into pandas
conn = sqlite3.connect(
    DATABASE_PATH, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES
)
df = pd.read_sql('''SELECT
                        id, domain, url, error as scrape_error, word_count,
                        matches, scraped_at, analyzed_at
                        FROM urls''', conn)

# Count number of matches for each row
df['sdgs_word_count'] = df.apply(lambda row: get_match_count(row, "sdgs"), axis=1)
for i in range(1, 18):
    sdg = "sdg" + str(i)
    df[sdg + "_word_count"] = df.apply(lambda row: get_match_count(row, sdg), axis=1)

# Rearrange columns
last_cols = ['matches', 'scraped_at', 'analyzed_at']
first_cols = [col for col in df.columns if col not in last_cols]
df = df[first_cols + last_cols]

Path("export").mkdir(parents=True, exist_ok=True)
df.to_csv('export/database.csv', index=False)
