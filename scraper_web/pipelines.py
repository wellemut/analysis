import os
import datetime
from models.Database import Database, Field

# from database.add_scraped_html import add_scraped_html
# from database.create_url import create_url
# from database.add_scrape_error import add_scrape_error

db = Database("scraped")


class WriteWebsitePipeline(object):
    def process_item(self, item, spider):
        item_class = type(item).__name__

        url = spider.url
        domain = spider.domain
        level = spider.level

        if item_class == "Website":
            with db.start_transaction() as transaction:
                # Add scraped HTML to the database
                db.table("urls").set(
                    html=item["html"].decode("UTF-8"),
                    scraped_at=datetime.datetime.utcnow(),
                ).where(Field("url") == url).execute(transaction=transaction)

                # Add collected links to the database
                table = db.table("urls")
                for link in item["links"]:
                    table.insert(
                        url=link,
                        domain=domain,
                        level=level + 1,
                        created_at=datetime.datetime.utcnow(),
                    ).on_conflict(table.url).do_nothing().execute(
                        transaction=transaction
                    )

        # Add error to the database
        elif item_class == "Error":
            print(item["message"])
            db.table("urls").set(
                error=item["message"], scraped_at=datetime.datetime.utcnow()
            ).where(Field("url") == url).execute()

        # Return nothing
        # With large arrays, we run into an issue when trying to pass it from
        # one process to another.
        return None
