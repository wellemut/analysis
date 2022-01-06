from models import Keyword, TextBlock, Website


def describe_with_snippet():
    def it_can_get_keyword_with_snippet_of_varying_size():
        website = Website.create(domain="17ziele.de")
        block = TextBlock.create(
            website=website,
            content="The world is changing every day.",
            hash="abc",
            word_count=1,
        )
        Keyword.create(text_block=block, keyword="world", sdg=1, start=4, end=9)
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

    def it_can_get_snippets_for_several_keywords():
        website = Website.create(domain="17ziele.de")
        block = TextBlock.create(
            website=website,
            content="Climate change is a major threat.",
            hash="abc",
            word_count=1,
        )
        Keyword.create(text_block=block, keyword="x", sdg=1, start=0, end=7)
        Keyword.create(text_block=block, keyword="x", sdg=1, start=20, end=25)
        block = TextBlock.create(
            website=website,
            content="We need to strengthen all types of equality.",
            hash="def",
            word_count=1,
        )
        Keyword.create(text_block=block, keyword="x", sdg=1, start=35, end=43)

        keywords = Keyword.query.with_transformation(Keyword.with_snippet(size=0)).all()

        assert keywords[0].snippet == "Climate"
        assert keywords[1].snippet == "major"
        assert keywords[2].snippet == "equality"
