import re
from urllib.parse import urlparse
from helpers.extractors import BaseExtractor


class FacebookExtractor(BaseExtractor):
    name = "facebook"
    top_level_domains = ["facebook.com", "fb.me", "fb.com"]
    NUMERIC_HANDLE_PATTERN = re.compile(r"^.*?\d{5,}$")
    RESERVED_TERMS = [
        "about",
        "ads",
        "business",
        "communitystandards",
        "dialog",
        "donate",
        "e",
        "events",
        "fund",
        "groups",
        "hashtag",
        "help",
        "l",
        "legal",
        "login",
        "permalink",
        "photo",
        "plugins",
        "policies",
        "policy",
        "privacy",
        "profile",
        "setting",
        "share",
        "sharer",
        "terms",
        "watch",
    ]

    @classmethod
    def extract(cls, url):
        handle = None

        # Remove any hash bangs from the URL, because urlparse does not handle
        # them well
        url = url.replace("/#!/", "/")

        # Parse lower-cased URL
        parsed_url = urlparse(url.lower())

        # Ignore any links to facebook developer portal
        if parsed_url.hostname == "developers.facebook.com":
            return None

        # Split url path into its segments
        segments = parsed_url.path.strip("/").split("/")

        # Ignore empty segments (e.g., https://fb.com//news)
        segments = [s for s in segments if s]

        # If the first segment is 'pg', it can be ignored
        if len(segments) and segments[0] == "pg":
            segments.pop(0)

        # If the first segment is 'pages', we are looking for a numeric handle
        # at the end of one of the segments
        if len(segments) and segments[0] == "pages":
            # Find a segment that ends with a long number
            for segment in segments[1:]:
                match = cls.NUMERIC_HANDLE_PATTERN.fullmatch(segment)
                if match:
                    handle = match[0]
                    break

        # If the first segment is not pages, then it's likely the correct handle
        if len(segments) and segments[0] != "pages":
            handle = segments[0]

        # If the handle contains an underscore, it's actually a combination of
        # username ID and post ID. We only keep the user ID
        if handle and "_" in handle:
            handle = handle.split("_")[0]

        # Test handle against reserved pages/terms
        if cls.is_handle_reserved(handle):
            return None

        return handle

    # Check if the handle matches one of the reserved terms
    @classmethod
    def is_handle_reserved(cls, handle):
        for term in cls.RESERVED_TERMS:
            if handle == term or handle == f"{term}.php":
                return True

        return False