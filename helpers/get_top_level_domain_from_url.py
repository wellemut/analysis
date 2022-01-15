import tldextract
import helpers


def get_top_level_domain_from_url(url):
    domain = helpers.get_domain_from_url(url)

    # If domain could not be extracted, the URL might be malformed or otherwise
    # invalid
    if domain is None:
        return None

    # Extract segments from url
    top_level_domain = tldextract.extract(url).registered_domain

    return top_level_domain if top_level_domain else None