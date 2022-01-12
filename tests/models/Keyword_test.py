from models import Keyword, TextBlock, Website


def describe_with_snippet():
    def it_can_get_keyword_with_snippet_of_varying_size(factory):
        block = factory.text_block(content="The world is changing every day.")
        factory.keyword(text_block=block, keyword="world", start=4, end=9)
        keyword = Keyword.query.with_transformation(
            Keyword.with_snippet(size=0)
        ).first()

        assert keyword.snippet == "world"

        keyword = Keyword.query.with_transformation(
            Keyword.with_snippet(size=3)
        ).first()

        assert keyword.snippet == "he world is"

        keyword = Keyword.query.with_transformation(
            Keyword.with_snippet(size=10)
        ).first()

        assert keyword.snippet == "The world is changi"

    def it_can_get_snippets_for_several_keywords(factory):
        block = factory.text_block(content="Climate change is a major threat.")
        factory.keyword(text_block=block, start=0, end=7)
        factory.keyword(text_block=block, start=20, end=25)
        block = factory.text_block(
            content="We need to strengthen all types of equality."
        )
        factory.keyword(text_block=block, start=35, end=43)

        keywords = Keyword.query.with_transformation(Keyword.with_snippet(size=0)).all()

        assert keywords[0].snippet == "Climate"
        assert keywords[1].snippet == "major"
        assert keywords[2].snippet == "equality"
