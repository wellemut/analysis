import os
from itertools import groupby
from functools import cache
import csv
import json
from sqlalchemy.orm import load_only
from sqlalchemy_mixins.utils import classproperty
import spacy
from spacy.matcher import PhraseMatcher
from spacy.language import Language
from spacy.lang.en import English
from models import Keyword, Website, TextBlock
from helpers import batches


class KeywordPipeline:
    # Mapping of languages to the Spacy models to use for the NLP pipeline
    NLP_MODELS = {"en": "en_core_web_sm"}

    @classmethod
    def process(cls, domain):
        website = Website.find_by(domain=domain)

        # Keep track of identified keywords
        keywords = []

        # Get IDs for all text blocks that belong to this domain and that have
        # content in one of the supported languages
        blocks = (
            TextBlock.query.where(TextBlock.website_id == website.id)
            .where(TextBlock.language.in_(cls.supported_languages))
            .options(load_only("id"))
            .all()
        )
        block_ids = [block.id for block in blocks]

        for ids in batches(block_ids, 100):
            # Load the blocks in this batch
            blocks = TextBlock.query.where(TextBlock.id.in_(ids)).all()

            # Group blocks by language
            by_lang = lambda x: x.language
            for language, group in groupby(sorted(blocks, key=by_lang), key=by_lang):
                nlp = cls.get_nlp(language)

                # Create tuples of content and block ID to pass into the pipeline
                tuples = [(block.content, block.id) for block in group]
                docs = nlp.pipe(tuples, as_tuples=True)

                for doc, block_id in docs:
                    for match in cls.find_keywords(doc):
                        keywords.append(
                            Keyword().fill(
                                text_block_id=block_id,
                                keyword=match["keyword"],
                                sdg=match["sdg"],
                                start=match["start"],
                                end=match["end"],
                            )
                        )

        with Keyword.session.begin():
            # Clear existing keywords from database
            Keyword.query.where(Keyword.text_block_id.in_(block_ids)).delete()

            # Write new keywords to database
            for keyword in keywords:
                keyword.save()

    # Find SDG keywords in the provided Spacy NLP document
    # Return a list of dicts with the following keys:
    # - keyword: The keyword that was found
    # - sdg: The SDG that the keyword is grouped under
    # - start: The position of the character where the keyword match starts
    # - end: The position of the character where the keyword match ends
    @classmethod
    def find_keywords(cls, doc):
        matcher = cls.get_matcher(doc.lang_)

        matches = []
        for match_id, start, end in matcher(doc):
            keyword_id = int(matcher.vocab.strings[match_id])
            matches.append(
                {
                    **cls.get_keyword_list(doc.lang_)[keyword_id],
                    # Get the position of the first character
                    "start": doc[start].idx,
                    # Get the position of the last character
                    "end": doc[end - 1].idx + len(doc[end - 1]),
                }
            )

        return matches

    @classproperty
    def supported_languages(cls):
        return list(cls.NLP_MODELS.keys())

    # Get a list of dicts with keyword and sdg, in the form of:
    # [{ "keyword": "poverty", "sdg": 1 }, { ... }, { ... }]
    @classmethod
    @cache
    def get_keyword_list(cls, language):
        with open(os.path.join("data", f"keywords_{language}.csv")) as file:
            keywords = []
            for row in csv.DictReader(file):
                keywords.append({"keyword": row["keyword"], "sdg": int(row["sdg"])})
            return keywords

    # Get the PhraseMatcher for the given language, with keyword matching
    # patterns from the relevant keywords list (in the data/keywords_{lang}.csv
    # file) (cached)
    @classmethod
    @cache
    def get_matcher(cls, language):
        nlp = cls.get_nlp(language)
        # We match on lemmas, so that we do not need to worry about plurals,
        # tenses, etc...
        matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")

        # Set up matcher
        keywords = [keyword["keyword"] for keyword in cls.get_keyword_list(language)]
        for index, pattern in enumerate(nlp.pipe(keywords)):
            matcher.add(str(index), [pattern])

        return matcher

    # Get the NLP pipeline for the given language (cached)
    @classmethod
    @cache
    def get_nlp(cls, language):
        nlp = spacy.load(
            cls.NLP_MODELS[language],
            # Disable all pipelines except for lemmatizer.
            # Lemmatizer requires tagger and attribute_ruler, so these are
            # included, too. PhraseMatcher appears to require tok2vec, so this
            # is included, too.
            # See: https://spacy.io/api/lemmatizer
            exclude=["parser", "senter", "ner"],
        )
        nlp.add_pipe("lemma_normalizer")

        return nlp


# Do nothing by default
@Language.component("lemma_normalizer")
def default_normalizer(doc):
    return doc


@English.factory("lemma_normalizer")
def create_en_normalizer(nlp, name):
    # Standardize all lemmas from british to american spelling using the
    # British-to-American dictionary available here:
    # https://raw.githubusercontent.com/hyperreality/American-British-English-Translator/master/data/british_spellings.json
    british_to_american_english = {}
    with open(os.path.join("data", "british_to_american_spellings.json")) as file:
        british_to_american_english = json.load(file)
    return TokenNormalizer(british_to_american_english)


class TokenNormalizer:
    def __init__(self, norm_table):
        self.norm_table = norm_table

    def __call__(self, doc):
        for token in doc:
            token.lemma_ = self.norm_table.get(token.lemma_, token.lemma_)
        return doc