import re
from urllib.parse import urlparse
from sqlalchemy.orm import load_only
from helpers.extract_texts_from_html import extract_texts_from_html
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

    @classmethod
    def process(cls, domain):
        # Get IDs for all webpages that belong to this domain and that have some
        # content
        website = Website.find_by(domain=domain)
        webpage_ids = (
            Webpage.query.filter_by(website=website)
            .where(Webpage.content != None)
            .ids()
        )

        with website.session.begin():
            # Clear existing text blocks and text block associations
            all_webpages = (
                Webpage.query.where(Webpage.website_id == website.id)
                .options(load_only("id"))
                .all()
            )
            WebpageTextBlock.query.where(
                WebpageTextBlock.webpage_id.in_([page.id for page in all_webpages])
            ).delete()
            all_blocks = (
                TextBlock.query.where(TextBlock.website_id == website.id)
                .options(load_only("id"))
                .all()
            )
            Keyword.query.where(
                Keyword.text_block_id.in_([block.id for block in all_blocks])
            ).delete()
            TextBlock.query.where(TextBlock.website_id == website.id).delete()

            # For each page, ...
            for id in webpage_ids:
                webpage = Webpage.find(id)

                # ... skip if the URL is blocklisted (e.g., privacy policy or news)
                if cls.is_url_blocklisted(webpage.url):
                    continue

                # ... eotherwise, extract text blocks from HTML content
                for text in extract_texts_from_html(webpage.content):

                    # Find or create associated text block
                    content = text["content"]
                    hash = TextBlock.text_to_hash(content)
                    block = TextBlock.find_by(website_id=website.id, hash=hash)
                    if not block:
                        block = TextBlock.create(
                            website=website,
                            hash=hash,
                            content=content,
                            word_count=TextBlock.count_words(content),
                        )

                    # Set up text block association
                    WebpageTextBlock.create(
                        webpage_id=id, text_block_id=block.id, tag=text["tag"]
                    )

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