from pipelines import KeywordPipeline
from models import Keyword, TextBlock, Website
from helpers import matches_dict


def test_it_supports_english():
    assert KeywordPipeline.supported_languages == ["en"]


def test_it_finds_keywords_in_text_blocks():
    website = Website.create(domain="17ziele.de")
    TextBlock.create(
        website=website,
        content="Poverty continues to be a major issue.",
        hash="abc",
        word_count=1,
        language="en",
    )

    KeywordPipeline.process("17ziele.de")

    assert Keyword.query.count() == 1
    keyword = Keyword.first()
    assert keyword.keyword == "poverty"
    assert keyword.sdg == 1
    assert keyword.start == 0
    assert keyword.end == 7


def test_it_ignores_non_english_texts():
    website = Website.create(domain="17ziele.de")
    for index, language in enumerate(["de", "fr", "unclear", None]):
        TextBlock.create(
            website=website,
            content="Poverty continues to be a major issue.",
            hash=f"abc{index}",
            word_count=1,
            language=language,
        )

    KeywordPipeline.process("17ziele.de")

    assert Keyword.query.count() == 0


def test_it_deletes_existing_keywords_for_the_domain():
    website = Website.create(domain="17ziele.de")
    block = TextBlock.create(
        website=website,
        content="Lorem ipsum dolorem...",
        hash="abc",
        word_count=1,
        language="en",
    )
    Keyword.create(text_block=block, keyword="a", sdg=1, start=0, end=1)
    Keyword.create(text_block=block, keyword="b", sdg=1, start=1, end=2)

    KeywordPipeline.process("17ziele.de")

    assert Keyword.query.count() == 0


def describe_find_keywords():
    def it_matches_poverty():
        nlp = KeywordPipeline.get_nlp("en")
        doc = nlp("We need to reduce poverty globally.")
        matches = KeywordPipeline.find_keywords(doc)
        assert len(matches) == 1
        assert {"keyword": "poverty", "sdg": 1} == matches_dict(matches[0])

    def it_matches_based_on_lemma():
        nlp = KeywordPipeline.get_nlp("en")
        doc = nlp("The country teams called to action.")
        matches = KeywordPipeline.find_keywords(doc)
        assert len(matches) == 1
        assert {"keyword": "call to action"} == matches_dict(matches[0])