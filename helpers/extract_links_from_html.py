from bs4 import BeautifulSoup, SoupStrainer

# Returns all links from an HTML document
def extract_links_from_html(html):
    # Use soup strainer to ignore all parts of the HTML document that are not
    # links. This improves performance. We only collect anchor tags that have an
    # href attribute.
    # See: https://beautiful-soup-4.readthedocs.io/en/latest/#parsing-only-part-of-a-document

    anchor_tags = SoupStrainer("a", href=True)
    soup = BeautifulSoup(html, "lxml", parse_only=anchor_tags)

    # Extract each link
    # Note: Must use #find_all instead of #contents
    # See: https://stackoverflow.com/a/17944089/6451879
    return [a.attrs["href"] for a in soup.find_all(anchor_tags)]