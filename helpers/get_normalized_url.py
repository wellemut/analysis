import tldextract

# Normalize the URL by removing the protocol
def get_normalized_url(url):
    return ".".join(tldextract.extract(url)).strip(".")
