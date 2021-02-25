import sys
from twisted.internet import reactor
import scrapy
from scrapy import signals
from scrapy.utils.project import get_project_settings

from multiprocessing import Queue

from helpers.spider_runner_process import SpiderRunnerProcess

# Helper class for running spiders as a process
class SpiderRunner:

    # Run the spider with the given name as a process
    @staticmethod
    def run(name, **arguments):
        queue = Queue()
        process = SpiderRunnerProcess(name  = name,
                                      queue = queue,
                                      **arguments)
        process.start()
        process.join()

        # Get queue contents
        queue_contents = queue.get()
        isFailed = queue_contents["isFailed"]
        results = queue_contents["results"]

        if isFailed:
            sys.exit(1)

        return results
