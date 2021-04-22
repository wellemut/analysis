from urllib.parse import urlparse
import re

FILE_EXTENSION_REGEX = re.compile(r"\.(html|php|htm)$")
IGNORE_LIST = [
    "privacy",
    "privacypolicy",
    "privacypolicyen",
    "privacypolicy2",
    "privacynotice",
    "privacystatement",
    "privacydatenschutz",
    "dataprivacystatement",
    "appprivacy",
    "dataprivacy",
    "dataprotection",
    "dataprotectionstatement",
    "datasecurity",
    "imprintprivacy",
    "datenschutz",
    "datenschutzhinweis",
    "datenschutzerklaerung",
    "datenschutzimpressum",
    "gdpr",
    "gpdr",
    "agb",
    "agben",
    "agbs",
    "allgemeinegeschaeftsbedingungen",
    "eula",
    "terms",
    "termsofuse",
    "generaltermsandconditions",
    "termsconditions",
    "termsandconditions",
    "termsofservice",
    "legal",
    "imprint",
    "imprintandprivacyprotection",
    "nutzungsbedingungen",
    "rss",
    "feed",
    "press",
    "presspage",
    "pressreleases",
    "presse",
    "pressemitteilungen",
    "archive",
    "nachrichtenarchiv",
    "archiv",
    "blog",
    "posts",
    "post",
    "news",
    "aktuelles",
    "aktuellemeldungen",
    "sitemap",
    "impressum",
    "contact",
    "kontakt",
    "jobs",
]

# Return True if the URL should NOT be analyzed
# This is the case for privacy policy pages or terms and conditions pages
def should_ignore_url(url):
    # Get URL path
    path = urlparse(url).path

    # Convert path to lowercase
    path = path.lower()

    # Remove file extension, if any
    path = FILE_EXTENSION_REGEX.sub("", path, count=1)

    # Remove trailing slash, if any
    path = path.rstrip("/")

    # Removing any separators
    path = path.translate(str.maketrans("", "", "-_"))

    # Check if any path segments match
    for segment in path.split("/"):
        if segment in IGNORE_LIST:
            return True

    return False
