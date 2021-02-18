from models.Database import Database


def get_urls_table_from_scraped_database():
    return Database("scraped").table("urls")
