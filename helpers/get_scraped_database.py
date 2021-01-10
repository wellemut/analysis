from database import Database


def get_scraped_database():
    return Database("scraped", table="urls")
