from models.WebpageTextBlock import WebpageTextBlock
from pipelines import ExtractPipeline
from models import Webpage, TextBlock


def test_it_extracts_text_blocks_from_webpages():
    page1 = Webpage.create_from_url("https://www.17ziele.de")
    page1.update(
        content="""
        <html>
            <head><title>my title</title>
            <body>
                <h1>hello <span>world!</span></h1>
            </body>
        </html>""",
    )
    page2 = Webpage.create_from_url("https://www.17ziele.de/abc")
    page2.update(
        content="""
        <html>
            <body>
                <p>hello world!</p>
            </body>
        </html>""",
    )

    ExtractPipeline.process("17ziele.de")

    assert TextBlock.query.count() == 2
    assert len(page1.webpage_text_blocks) == 2
    assert page1.webpage_text_blocks[0].tag == "title"
    assert page1.webpage_text_blocks[0].text_block.content == "my title"


def test_it_ignores_pages_without_content():
    page = Webpage.create_from_url("https://www.17ziele.de")
    page.update(content="<body>abc</body>")
    Webpage.create_from_url("https://www.17ziele.de/home")

    ExtractPipeline.process("17ziele.de")

    assert TextBlock.query.count() == 1


def test_it_removes_existing_text_block_associations_for_the_website():
    webpage = Webpage.create_from_url("https://www.17ziele.de")
    webpage.update(content="<body>hello world</body>")
    block = TextBlock.find_by_content_or_create("xyz")
    WebpageTextBlock.create(webpage=webpage, text_block=block, tag="p")

    other_webpage = Webpage.create_from_url("https://example.com")
    WebpageTextBlock.create(webpage=other_webpage, text_block=block, tag="p")

    ExtractPipeline.process("17ziele.de")

    assert TextBlock.query.count() == 2
    assert WebpageTextBlock.query.count() == 2
    assert len(webpage.webpage_text_blocks) == 1
    assert webpage.webpage_text_blocks[0].tag == "body"
    assert webpage.webpage_text_blocks[0].text_block.content == "hello world"

    # Does not touch other webpage's text blocks
    assert len(other_webpage.reload().webpage_text_blocks) == 1
