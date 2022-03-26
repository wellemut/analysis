import re
from functools import cache
from urllib.parse import urlparse
import spacy
from helpers import extract_texts_from_html, squish
from models import Website, Webpage, TextBlock, WebpageTextBlock, Keyword


class ExtractPipeline:
    FILE_EXTENSION_REGEX = re.compile(r"\.(html|php|htm)$")
    # URLs that contain one of the following terms are ignored
    URL_BLOCKLIST = [
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
        "sitemap",
        "impressum",
        "contact",
        "kontakt",
        "jobs",
        "team",
        "teams",
        "ourteam",
        "author",
        "authors",
        "career",
        "careers",
        "staff",
        "boardofdirectors",
        "advisoryboard",
        "people",
        "person",
        "bio",
        "bios",
        "funders",
        "partners",
        "copyright",
        "glossary",
    ]

    @classmethod
    def process(cls, domain):
        print(f"Extracting {domain}:", end=" ")

        # Get IDs for all webpages that belong to this domain and that have
        # content and status code 200
        website = Website.find_by(domain=domain)
        webpage_ids = Webpage.query.filter_by(
            website=website, is_ok_and_has_content=True
        ).ids()

        # Cache block hashes and associated block IDs in a hash map. This is
        # faster than querying the database for hash IDs.
        hash_to_id_map = dict()

        with website.session.begin():
            # Clear existing text blocks and text block associations
            WebpageTextBlock.delete_by_website(website)
            Keyword.delete_by_website(website)
            TextBlock.delete_by_website(website)

            # For each page, ...
            for id in webpage_ids:
                webpage = Webpage.find(id)

                # ... skip if the URL is blocklisted (e.g., privacy policy or news)
                if cls.is_url_blocklisted(webpage.url):
                    continue

                # ... skip if the URL is for a person (e.g., team member)
                if cls.is_url_for_person(webpage.url):
                    continue

                # ... otherwise, extract text blocks from HTML content
                for text in extract_texts_from_html(webpage.content):
                    content = text["content"]
                    hash = TextBlock.text_to_hash(content)

                    # If block with this hash does not yet exist, create it
                    if not hash in hash_to_id_map:
                        block = TextBlock.create(
                            website_id=website.id,
                            hash=hash,
                            content=content,
                            word_count=TextBlock.count_words(content),
                        )
                        hash_to_id_map[hash] = block.id

                    # Set up text block association
                    WebpageTextBlock.create(
                        webpage_id=id,
                        text_block_id=hash_to_id_map.get(hash),
                        tag=text["tag"],
                    )

                # Print progress indicator
                print(".", end="")

        # Print summary stats
        print("")
        print(
            "Extracted",
            TextBlock.query.filter_by(website=website).count(),
            "text blocks",
        )

    # Get the NLP pipeline for the given language (cached)
    @classmethod
    @cache
    def get_nlp(cls):
        return spacy.load("en_core_web_lg")

    @classmethod
    def is_url_for_person(cls, url):
        # Initialize NLP pipeline
        nlp = cls.get_nlp()

        # Remove file extension, if any
        path = cls.FILE_EXTENSION_REGEX.sub("", url.lower(), count=1)

        # Split url path into its segments
        segments = urlparse(path).path.strip("/").split("/")

        # Pretty-format each segment, keeping only alphanumeric characters and
        # using titlecase (which makes name recognition perform better)
        non_alpha = re.compile(r"[^a-zA-Z0-9]")
        segments = [squish(non_alpha.sub(" ", s)) for s in segments]

        # Parse each segment
        docs = nlp.pipe(segments)

        # Check if any URL segment consists of just a person
        for doc in docs:
            ent = next(iter(doc.ents), None)
            is_person = ent and ent.label_ == "PERSON"
            is_full_length = ent and ent.start == 0 and ent.end == len(doc)
            if is_person and is_full_length:
                return True

        return False

    @classmethod
    def is_url_blocklisted(cls, url):
        # Get URL path
        path = urlparse(url).path

        # Convert path to lowercase
        path = path.lower()

        # Remove file extension, if any
        path = cls.FILE_EXTENSION_REGEX.sub("", path, count=1)

        # Remove trailing slash, if any
        path = path.rstrip("/")

        # Removing any separators
        path = path.translate(str.maketrans("", "", "-_"))

        # Check if any path segments match
        for segment in path.split("/"):
            if segment in cls.URL_BLOCKLIST:
                return True

        return False