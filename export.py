# Export database to CSV file
import pandas as pd
import sqlite3
import json
from pathlib import Path
from database.config import DATABASE_PATH

def aggregate(x):
    d = {}
    d['page_count'] = x['url'].count()
    d['scrape_error_count'] = x['scrape_error'].count()

    for column in x.columns:
        if column.endswith("_match_count") or column == "word_count":
            d[column] = x[column].sum()

    d['scraped_at'] = x['scraped_at'].max()
    d['analyzed_at'] = x['analyzed_at'].max()

    return pd.Series(d, index=list(d.keys()))


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
                        FROM urls
                        WHERE level <= 1''', conn)

# Count number of matches for each row
df['sdgs_match_count'] = df.apply(lambda row: get_match_count(row, "sdgs"), axis=1)
for i in range(1, 18):
    sdg = "sdg" + str(i)
    df[sdg + "_match_count"] = df.apply(lambda row: get_match_count(row, sdg), axis=1)

# Rearrange columns
last_cols = ['matches', 'scraped_at', 'analyzed_at']
first_cols = [col for col in df.columns if col not in last_cols]
df = df[first_cols + last_cols]

# Timestamps to date
df[['scraped_at','analyzed_at']] = df[['scraped_at','analyzed_at']].apply(pd.to_datetime, format='%Y-%m-%d %H:%M:%S.%f')

df = df.sort_values(by=['domain', 'scraped_at'])
Path("export").mkdir(parents=True, exist_ok=True)
df.to_csv('export/by-url.csv', index=False)

# Combine by domain
df = df.groupby(by=['domain']).apply(aggregate)

df = df.sort_values(by=['domain'])
Path("export").mkdir(parents=True, exist_ok=True)
df.to_csv('export/by-domain.csv', index=True)
