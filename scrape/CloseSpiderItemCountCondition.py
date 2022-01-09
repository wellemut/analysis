"""CloseSpiderItemCountCondition is an extension that forces spiders to be
closed after a certain number of items that match a given condition have been
scraped.

Based on the default CloseSpider extensenion.
Docs: https://docs.scrapy.org/en/latest/topics/extensions.html#module-scrapy.extensions.closespider
Code: https://docs.scrapy.org/en/latest/_modules/scrapy/extensions/closespider.html#CloseSpider
"""

from scrapy import signals
from scrapy.exceptions import NotConfigured

# Add a custom CloseSpider extension that can auto-close a spider after a
# maximum number of items have been scraped that match a particular condition.
# We use this to close the spider after the pipeline's MAX_PAGES with status
# code 200 and having content have been scraped. The default CloseSpider
# extension does not allow to differentiate between different items but we do
# not want to count redirects or 404s towards our max page limit.
class CloseSpiderItemCountCondition:
    def __init__(self, crawler):
        self.crawler = crawler

        setting = crawler.settings.get("CLOSESPIDER_ITEMCOUNT_CONDITION", {})

        if not setting:
            raise NotConfigured

        self.counter = 0
        self.close_on_count = setting.get("count")
        self.meets_condition = setting.get("condition")

        crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    # Count items received and close spider after collecting X items matching
    # the user-provided condition
    def item_scraped(self, item, spider):
        if not self.meets_condition(item):
            return

        self.counter += 1
        if self.counter >= self.close_on_count:
            self.crawler.engine.close_spider(spider, "closespider_itemcount_condition")
