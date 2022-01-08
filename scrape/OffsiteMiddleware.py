import re
from scrapy.spidermiddlewares import offsite

# Unlike the original implementation, this OffsiteMiddleware only allows URLs to
# the root domain and www-subdomain, but no other subdomain
# When allowed_domains = [example.com] allows example.com and www.example.com
# When allowed_domains = [sub.test.com] allows sub.test.com and www.sub.test.com
# Original implementation:
# https://github.com/scrapy/scrapy/blob/master/scrapy/spidermiddlewares/offsite.py
class OffsiteMiddleware(offsite.OffsiteMiddleware):
    def get_host_regex(self, spider):
        regex = super().get_host_regex(spider)
        # Replace optional .* (any subdomains) with optional www-subdomain only
        regex = regex.pattern.replace("(.*\.)?", "(www\.)?", 1)
        return re.compile(regex)