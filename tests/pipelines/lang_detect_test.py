from pipelines import LangDetectPipeline
from models import Webpage, TextBlock, WebpageTextBlock


def test_it_identifies_language_of_text_blocks():
    page = Webpage.create_from_url("https://www.17ziele.de")
    block1 = TextBlock.create(
        website=page.website,
        hash="abc",
        word_count=1,
        content="Die 17 Ziele sind von allen Ländern verabschiedet worden.",
    )
    block2 = TextBlock.create(
        website=page.website,
        hash="def",
        word_count=1,
        content="By 2030, all countries need to work to eliminate extreme poverty.",
    )
    WebpageTextBlock.create(webpage=page, text_block=block1, tag="p")
    WebpageTextBlock.create(webpage=page, text_block=block2, tag="p")

    LangDetectPipeline.process("17ziele.de")

    assert block1.reload().language == "de"
    assert block2.reload().language == "en"


def test_it_identifies_language_of_texts():
    LangDetectPipeline.detect_language("Der Hund geht durch den Wald") == "de"
    LangDetectPipeline.detect_language("The stars shine brightly in the night") == "en"
    LangDetectPipeline.detect_language("© Peter") == "unclear"
