from bs4 import BeautifulSoup, NavigableString
from helpers import squish


def contains_text(tag):
    # Ignore non tags (text instances)
    if isinstance(tag, NavigableString):
        return False

    # Return true if any immediate child of this tag is a string
    for content in tag.contents:
        if isinstance(content, NavigableString) and len(squish(content)) > 0:
            return True


class TextCollection:
    def __init__(self):
        self.texts = []

    # Add a text to the text collection from a given tag, and optionally with
    # a specific tag_name or a custom content getter method.
    def add(self, tag, tag_name=None, getter=lambda x: x.get_text()):
        if tag is None:
            return

        name = tag_name or tag.name
        content = squish(getter(tag) or "")
        tag.decompose()

        if len(content) > 0:
            self.texts.append({"tag": name, "content": content})

    def tolist(self):
        return self.texts


# Returns texts from an HTML document
def extract_texts_from_html(html):
    soup = BeautifulSoup(html, "lxml")
    texts = TextCollection()

    # Ignore all content in script tags
    for script in soup.find_all("script"):
        script.decompose()

    # Add title and meta data
    texts.add(soup.title)
    texts.add(
        soup.select_one('head meta[name="description"]'),
        tag_name="meta description",
        getter=lambda x: x.get("content"),
    )

    # Add any text nodes
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"]):
        texts.add(tag)

    # Add image descriptions
    for image in soup.find_all("img"):
        texts.add(image, getter=lambda x: x.get("alt"))

    # Add any remaining text inside the body (e.g., from divs or spans)
    while tag := soup.body.find(contains_text):
        texts.add(tag)

    # Finally, add any remaining text from the HTML body
    texts.add(soup.body)

    return texts.tolist()