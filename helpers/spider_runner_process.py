from billiard import Process
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scrapy.signalmanager import dispatcher
from twisted.python import log

# Runs a spider inside a sub process and reports results back to main thread
class SpiderRunnerProcess(Process):
    def __init__(self, name, queue, settings=None, **arguments):
        Process.__init__(self)
        self.name = name
        self.queue = queue
        self.settings = settings
        self.arguments = arguments
        self.results = []
        self.errors = []

    # Collect crawler results
    def crawler_results(self, signal, sender, item, response, spider):
        self.results.append(item)

    def raise_error(self, signal, sender, failure, response, spider):
        self.errors.append(failure)

    def run(self):
        dispatcher.connect(self.crawler_results, signal=signals.item_scraped)
        dispatcher.connect(self.raise_error, signal=signals.item_error)
        dispatcher.connect(self.raise_error, signal=signals.spider_error)

        # Get project settings and merge custom settings, if passed
        settings = get_project_settings()
        if self.settings:
            settings.update(self.settings, priority="cmdline")

        # Begin crawl
        process = CrawlerProcess(settings)
        process.crawl(self.name, **self.arguments)
        process.start()  # the script will block here until the crawling is finished

        # report results and errors back to main thread
        isFailed = len(self.errors) > 0
        self.queue.put({"results": self.results, "isFailed": isFailed})
