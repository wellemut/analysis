from bs4 import BeautifulSoup
from helpers import squish


def div_without_child_div(tag):
    # Return false if tag is not a div
    if tag.name != "div":
        return False

    # Return false if any child tags are divs
    if tag.find("div", recursive=True):
        return False

    # We found a div without any child divs
    return True


class TextCollection:
    def __init__(self):
        self.texts = []

    # Add a text to the text collection from a given tag, and optionally with
    # a specific tag_name or a custom content getter method.
    def add(self, tag, tag_name=None, getter=lambda x: x.get_text(separator=" ")):
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
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "ol", "ul", "p"]):
        texts.add(tag)

    # Add image descriptions
    for image in soup.find_all("img"):
        texts.add(image, getter=lambda x: x.get("alt"))

    # Add any remaining text inside the body, starting with the deepest div and
    # working upwards
    while tag := soup.body.find(div_without_child_div):
        texts.add(tag)

    # Finally, add any remaining text from the HTML body
    texts.add(soup.body)

    return texts.tolist()