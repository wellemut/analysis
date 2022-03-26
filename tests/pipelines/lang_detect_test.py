from pipelines.LangDetectPipeline import LangDetectPipeline
from models import TextBlock, WebpageTextBlock


def test_it_identifies_language_of_text_blocks(factory):
    website = factory.website()
    block1 = factory.text_block(
        website=website,
        content="Die 17 Ziele sind von allen Ländern verabschiedet worden.",
    )
    block2 = factory.text_block(
        website=website,
        content="By 2030, all countries need to work to eliminate extreme poverty.",
    )

    LangDetectPipeline.process(website.domain)

    assert block1.reload().language == "de"
    assert block2.reload().language == "en"


def test_it_identifies_language_of_texts():
    LangDetectPipeline.detect_language("Der Hund geht durch den Wald") == "de"
    LangDetectPipeline.detect_language("The stars shine brightly in the night") == "en"
    LangDetectPipeline.detect_language("© Peter") == "unclear"


def test_it_identifies_language_of_short_texts():
    LangDetectPipeline.detect_language("Circular economy") == "en"
