from sqlalchemy.orm import load_only
from helpers.extract_texts_from_html import extract_texts_from_html
from models import Website, Webpage, TextBlock, WebpageTextBlock


class ExtractPipeline:
    @classmethod
    def process(cls, domain):
        # Store new webpage text blocks (associations between webpages and
        # text blocks)
        webpage_text_blocks = []

        # Get IDs for all webpages that belong to this domain and that have some
        # content
        website = Website.find_by(domain=domain)
        webpages = (
            Webpage.query.where(Webpage.website_id == website.id)
            .where(Webpage.content != None)
            .options(load_only("id"))
            .all()
        )
        webpage_ids = [page.id for page in webpages]

        # For each page, ...
        for id in webpage_ids:
            # ... extract text blocks from HTML content
            for text in extract_texts_from_html(Webpage.find(id).content):

                # ... find or create associated text block
                block = TextBlock.find_by_content_or_create(content=text["content"])

                # ... and set up text block association
                webpage_text_blocks.append(
                    WebpageTextBlock().fill(
                        webpage_id=id, text_block_id=block.id, tag=text["tag"]
                    )
                )

        with website.session.begin():
            # Clear existing text block associations
            WebpageTextBlock.query.where(
                WebpageTextBlock.webpage_id.in_(webpage_ids)
            ).delete()

            # Save new text block associations
            for webpage_text_block in webpage_text_blocks:
                webpage_text_block.save()
