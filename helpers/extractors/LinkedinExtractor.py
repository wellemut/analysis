from urllib.parse import urlparse
from helpers.extractors import BaseExtractor


class LinkedinExtractor(BaseExtractor):
    top_level_domains = ["linkedin.com"]
    # A list of path segments that will precede a handle
    VALID_ENTITIES = ["company", "school", "showcase"]

    @classmethod
    def extract(cls, url):
        handle = None

        # Parse lower-cased URL
        parsed_url = urlparse(url.lower())

        # Split url path into its segments
        segments = parsed_url.path.strip("/").split("/")

        # Ignore empty segments (e.g., https://linkedin.com//home)
        segments = [s for s in segments if s]

        # Check if we have at least two segments, where the first segment is of
        # a valid entity (company, school, showcase, ...). If so, our handle is
        # the second segment.
        if len(segments) >= 2 and segments[0] in cls.VALID_ENTITIES:
            handle = segments[1]

        return handle