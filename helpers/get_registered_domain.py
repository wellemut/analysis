import tldextract

# Return the registered domain for a given URL
def get_registered_domain(url):
    return tldextract.extract(url).registered_domain
