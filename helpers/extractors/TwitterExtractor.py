import re
from urllib.parse import urlparse, parse_qs
from helpers.extractors import BaseExtractor


class TwitterExtractor(BaseExtractor):
    name = "twitter"
    top_level_domains = ["twitter.com"]
    # A list of path segments that are valid after a username
    VALID_USER_PATHS = ["status", "lists", "timelines"]
    # A list of domain names used for user accounts
    MAIN_DOMAINS = ["www.twitter.com", "twitter.com", "mobile.twitter.com"]
    # Regex pattern for validating and finding handles
    HANDLE_PATTERN = re.compile(r"^[a-z0-9_]{1,15}$")
    HANDLE_PATTERN_IN_TEXT = re.compile(r"(?:^| )@([a-z0-9_]{1,15})\b")
    # A list of reserved terms that are not valid for a handle
    RESERVED_TERMS = [
        "i",
        "home",
        "search",
        "hashtag",
        "intent",
        "share",
        "account",
        "settings",
        "privacy",
    ]

    @classmethod
    def extract(cls, url):
        handle = None

        # Remove any hash bangs from the URL, because urlparse does not handle
        # them well
        url = url.replace("/#!/", "/")
        url = url.replace("/#/", "/")

        # Parse lower-cased URL
        parsed_url = urlparse(url.lower())

        # Ignore any links to sites other than the main twitter pages
        # Examples: developer portal, help site, legal site, ...
        if parsed_url.hostname not in cls.MAIN_DOMAINS:
            return None

        # Split url path into its segments
        segments = parsed_url.path.strip("/").split("/")

        # Ignore empty segments (e.g., https://twitter.com//home)
        segments = [s for s in segments if s]

        # If there are no segments left, abort
        if not len(segments):
            return None

        # If the first segment indicates an intention, we use a separate set of
        # rules to extract a handle from the query
        if segments[0] in ["intent", "share"]:
            handle = cls.handle_from_query_params(parse_qs(parsed_url.query))
        else:
            # Otherwise, if there is no other segment or the next segment is a
            # valid one, we have our handle
            if len(segments) == 1 or segments[1] in cls.VALID_USER_PATHS:
                handle = segments[0]

        # If the handle starts with an @ symbol, we can remove it
        if handle and handle.startswith("@"):
            handle = handle.replace("@", "", 1)

        # Validate handle
        if handle and not cls.is_handle_valid(handle):
            return None

        # Test handle against reserved pages/terms
        if cls.is_handle_reserved(handle):
            return None

        return handle

    # Check if the handle matches one of the reserved terms
    @classmethod
    def is_handle_reserved(cls, handle):
        return any([handle == term for term in cls.RESERVED_TERMS])

    # Check whether the provided handle matches the Twitter username criteria
    @classmethod
    def is_handle_valid(cls, handle):
        return cls.HANDLE_PATTERN.fullmatch(handle) != None

    # Look for a valid handle in the query params
    @classmethod
    def handle_from_query_params(cls, params):
        # Sometimes present for tweet intent
        if "via" in params:
            return params["via"][0]

        # Present for follow intent
        if "screen_name" in params:
            return params["screen_name"][0]

        # Example: 'twitter:A description,abc:My description,def'
        if "related" in params:
            return params["related"][0].split(",")[0].split(":")[0]

        # Look for a handle in the body text
        if "text" in params:
            match = cls.HANDLE_PATTERN_IN_TEXT.search(params["text"][0])
            if match:
                return match[1]