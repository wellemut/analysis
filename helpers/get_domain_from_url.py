from urllib.parse import urlparse


def get_domain_from_url(url):
    domain = urlparse(url).netloc

    # Remove trailing www. (always use root domain)
    if domain.startswith("www."):
        domain = domain.replace("www.", "", 1)

    return domain