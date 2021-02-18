from models.Database import Database


def get_domains_table_from_analysis_database():
    return Database("analysis").table("domains")
