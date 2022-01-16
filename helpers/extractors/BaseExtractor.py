from collections import defaultdict, Counter


class BaseExtractor:
    def __init__(self):
        self.handles = defaultdict(set)

    @classmethod
    def extract(cls, link):
        raise Exception(f"Method 'extract' is not implemented in {cls}.")

    # Attempt to extract a result from the given link and keep track of the
    # pages where the link has been seen
    def process(self, link, page):
        item = self.extract(link)
        if item:
            self.handles[item].add(page)

    @property
    def counts(self):
        return Counter({value: len(pages) for value, pages in self.handles.items()})