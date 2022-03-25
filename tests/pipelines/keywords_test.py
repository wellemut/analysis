from pipelines.KeywordsPipeline import KeywordsPipeline
from models import Keyword
from helpers import matches_dict


def test_it_supports_english():
    assert KeywordsPipeline.supported_languages == ["en"]


def test_it_finds_keywords_in_text_blocks(factory):
    block = factory.text_block(
        content="Poverty continues to be a major issue.", language="en"
    )

    KeywordsPipeline.process(block.website.domain)

    assert Keyword.query.count() == 1
    keyword = Keyword.first()
    assert keyword.keyword == "poverty"
    assert keyword.sdg == 1
    assert keyword.start == 0
    assert keyword.end == 7


def test_it_ignores_non_english_texts(factory):
    website = factory.website()
    content = "Poverty continues to be a major issue."
    factory.text_block(website=website, content=content, hash="a", language="de")
    factory.text_block(website=website, content=content, hash="b", language="fr")
    factory.text_block(website=website, content=content, hash="c", language="unclear")
    factory.text_block(website=website, content=content, hash="d", language=None)

    KeywordsPipeline.process(website.domain)

    assert Keyword.query.count() == 0


def test_it_deletes_existing_keywords_for_the_domain(factory):
    block = factory.text_block()
    factory.keyword(text_block=block)
    factory.keyword(text_block=block)

    KeywordsPipeline.process(block.website.domain)

    assert Keyword.query.count() == 0


def describe_get_nlp():
    def it_normalizes_lemmas_from_british_to_american_english():
        nlp = KeywordsPipeline.get_nlp("en")
        doc = nlp("I optimise five metres of programmes in ten instalments")
        lemmas = [token.lemma_ for token in doc]
        assert lemmas == "i optimize five meter of program in ten installment".split()

    def it_expands_contractions_of_will():
        # There is a bug in Spacy where contractions of will (e.g., he'll) are
        # not correctly expanded to 'will' and instead remain as "'ll". This
        # will be fixed in Spacy 3.3 according to
        # https://github.com/explosion/spaCy/issues/9899
        # For now, we manually replace 'll lemmas with will
        nlp = KeywordsPipeline.get_nlp("en")
        doc = nlp("I'll he'll she'll we'll")
        lemmas = [token.lemma_ for token in doc]
        assert lemmas == "i will he will she will we will".split()


def describe_find_keywords():
    def it_matches_poverty():
        nlp = KeywordsPipeline.get_nlp("en")
        doc = nlp("We need to reduce poverty globally.")
        matches = KeywordsPipeline.find_keywords(doc)
        assert len(matches) == 1
        assert {"keyword": "reduce poverty", "sdg": 1} == matches_dict(matches[0])

    def it_matches_based_on_lemma():
        nlp = KeywordsPipeline.get_nlp("en")
        doc = nlp("It is time for safer cities")
        matches = KeywordsPipeline.find_keywords(doc)
        assert len(matches) == 1
        assert {"keyword": "safe city"} == matches_dict(matches[0])

    def it_matches_both_british_and_american_english():
        nlp = KeywordsPipeline.get_nlp("en")
        british = nlp("Organised crime poses a problem for the locals.")
        american = nlp("Organized crime poses a problem for the locals.")

        matches_british = KeywordsPipeline.find_keywords(british)
        assert len(matches_british) == 1
        assert {"keyword": "organized crime"} == matches_dict(matches_british[0])

        matches_american = KeywordsPipeline.find_keywords(american)
        assert len(matches_american) == 1
        assert {"keyword": "organized crime"} == matches_dict(matches_american[0])

    def it_does_not_double_count_contained_keywords():
        nlp = KeywordsPipeline.get_nlp("en")
        doc = nlp("We fight for the climate and climate change mitigation.")
        matches = KeywordsPipeline.find_keywords(doc)
        assert len(matches) == 2
        assert {"keyword": "climate"} == matches_dict(matches[0])
        assert {"keyword": "climate change mitigation"} == matches_dict(matches[1])

    def it_does_not_count_keywords_if_they_are_all_generic():
        nlp = KeywordsPipeline.get_nlp("en")
        doc = nlp("There are academic students in the classroom of the university.")
        matches = KeywordsPipeline.find_keywords(doc)
        assert len(matches) == 0
        doc = nlp(
            "There are academic students working on education reform in the classroom of the university."
        )
        matches = KeywordsPipeline.find_keywords(doc)
        assert len(matches) == 5