import tldextract


def get_domain_from_url(url):
    # Ignore URLs without valid protocol
    if not url.startswith("http://") and not url.startswith("https://"):
        return None

    # Extract segments from url
    segments = tldextract.extract(url)

    # If suffix is missing, do not consider valid
    if not segments.suffix:
        return None

    # Combine into domain
    domain = ".".join(part for part in segments if part)

    # Domain must be shorter than 255 according to specifications
    if len(domain) > 255:
        return None

    # Domain may not contain any of the following invalid characters
    for invalid_char in " %@!,'&$":
        if invalid_char in domain:
            return None

    # Remove leading www. (always use root domain)
    if domain.startswith("www."):
        domain = domain.replace("www.", "", 1)

    # Lowercase domain
    domain = domain.lower()

    return domain