import os
import datetime
from models.Database import Database, Field


class WriteWebsitePipeline(object):
    def process_item(self, item, spider):
        item_class = type(item).__name__

        db = Database(spider.database_name)
        id = spider.url_id
        url = spider.url
        domain_id = spider.domain_id
        domain = spider.domain
        level = spider.level

        if item_class == "Website":
            with db.start_transaction() as transaction:
                # Add scraped HTML to the database
                db.table("url").set(
                    html=item["html"].decode("UTF-8"),
                    scraped_at=datetime.datetime.utcnow(),
                ).where(Field("id") == id).execute(transaction=transaction)

                # Add collected links to the database
                table = db.table("url")
                for link in item["links"]:
                    table.insert(
                        url=link,
                        domain_id=domain_id,
                        level=level + 1,
                    ).on_conflict(table.url).do_nothing().execute(
                        transaction=transaction
                    )

        # Add error to the database
        elif item_class == "Error":
            print(item["message"])
            db.table("url").set(
                error=item["message"], scraped_at=datetime.datetime.utcnow()
            ).where(Field("id") == id).execute()

        # Return nothing
        # With large arrays, we run into an issue when trying to pass it from
        # one process to another.
        return None
