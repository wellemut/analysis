from models import WebpageTextBlock


def describe_delete_by_website():
    def test_it_deletes_webpage_text_blocks_associated_with_website(factory):
        website = factory.website()
        factory.webpage_text_block(webpage=factory.webpage(website=website))
        factory.webpage_text_block(webpage=factory.webpage(website=website))

        assert WebpageTextBlock.query.count() == 2
        WebpageTextBlock.delete_by_website(website)
        assert WebpageTextBlock.query.count() == 0

    def test_it_does_not_touch_unassociated_webpage_text_blocks(factory):
        webpage_text_block = factory.webpage_text_block()
        other_webpage_text_block = factory.webpage_text_block()
        assert WebpageTextBlock.query.count() == 2

        WebpageTextBlock.delete_by_website(webpage_text_block.webpage.website)

        assert WebpageTextBlock.query.count() == 1
        assert other_webpage_text_block.reload() is not None