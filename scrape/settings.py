# Scrapy settings for scrape project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "scrape"

SPIDER_MODULES = ["scrape"]
NEWSPIDER_MODULE = "scrape"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'scrape (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

LOG_LEVEL = "WARN"

# Disable the referrer header to avoid warning on following links:
# WARNING: RuntimeWarning: Could not load referrer policy
#          'no-referrer-when-downgrade, strict-origin-when-cross-origin'
REFERER_ENABLED = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Crawl in breadth-first order rather than depth-first order because we want to
# give priority to pages that are reachable with fewer clicks
# See: https://docs.scrapy.org/en/latest/faq.html#faq-bfo-dfo
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"

# Abort page load after 15 seconds, if not complete (defaults to 3 minutes)
# See: https://docs.scrapy.org/en/latest/topics/broad-crawls.html#reduce-download-timeout
DOWNLOAD_TIMEOUT = 15

# Retry page load one time after failure, for two attemps in total (original
# attempt plus one retry).
# See: https://docs.scrapy.org/en/latest/topics/broad-crawls.html#disable-retries
RETRY_TIMES = 1

# Disable cookies, as recommended by Scrapy (enabled by default)
# See: https://docs.scrapy.org/en/latest/topics/broad-crawls.html#disable-cookies
COOKIES_ENABLED = False

# Overwrite the OffsiteMiddleware to only follow links that are on the same root
# or www domain (e.g., example.com and www.example.com), but no links to
# subdomains (e.g., subdomain.example.com)
# See: https://github.com/scrapy/scrapy/issues/3412
SPIDER_MIDDLEWARES = {
    "scrapy.spidermiddlewares.offsite.OffsiteMiddleware": None,
    "scrape.OffsiteMiddleware.OffsiteMiddleware": 500,
}

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'scrape.middlewares.ScrapeSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'scrape.middlewares.ScrapeDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'scrape.pipelines.ScrapePipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
