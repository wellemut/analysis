from models import Website, Webpage


def test_it_returns_ok_on_status_code_200(factory):
    page_a = factory.webpage(status_code=200)
    assert page_a.is_ok

    page_b = factory.webpage(status_code=301)
    assert not page_b.is_ok


def describe_delete_unused_by_website():
    def test_it_deletes_only_unused_webpages_associated_with_website(factory):
        website = factory.website()
        factory.webpage(website=website)
        page_with_text = factory.webpage(website=website)
        factory.webpage_text_block(webpage=page_with_text)
        page_with_outbound_link = factory.webpage(website=website)
        factory.link(source_webpage=page_with_outbound_link)
        page_with_inbound_link = factory.webpage(website=website)
        factory.link(target_webpage=page_with_inbound_link)

        assert Webpage.query.filter_by(website=website).count() == 4
        Webpage.delete_unused_by_website(website)
        assert Webpage.query.filter_by(website=website).count() == 3

        assert page_with_text.reload() is not None
        assert page_with_outbound_link.reload() is not None
        assert page_with_inbound_link.reload() is not None

    def test_it_does_not_touch_unused_webpages_of_other_websites(factory):
        website = factory.website()
        factory.webpage(website=website)
        other_unused_webpage = factory.webpage()

        Webpage.delete_unused_by_website(website)

        assert Webpage.query.count() == 1
        assert other_unused_webpage.reload() is not None