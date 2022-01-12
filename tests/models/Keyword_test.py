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


def describe_delete_by_website():
    def test_it_deletes_keywords_associated_with_website(factory):
        website = factory.website()
        block1 = factory.text_block(website=website)
        block2 = factory.text_block(website=website)
        factory.keyword(text_block=block1)
        factory.keyword(text_block=block1)
        factory.keyword(text_block=block2)

        assert Keyword.query.count() == 3
        Keyword.delete_by_website(website)
        assert Keyword.query.count() == 0

    def test_it_does_not_touch_unassociated_keywords(factory):
        keyword = factory.keyword()
        other_keyword = factory.keyword()
        assert Keyword.query.count() == 2

        Keyword.delete_by_website(keyword.text_block.website)

        assert Keyword.query.count() == 1
        assert Keyword.find(keyword.id) is None
        assert Keyword.find(other_keyword.id) is not None