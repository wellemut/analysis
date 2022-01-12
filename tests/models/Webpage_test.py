from models import Website, Webpage


def test_it_returns_ok_on_status_code_200(factory):
    page_a = factory.webpage(status_code=200)
    assert page_a.is_ok

    page_b = factory.webpage(status_code=301)
    assert not page_b.is_ok


def describe_delete_unused_by_website():
    def test_it_deletes_only_unused_webpages_associated_with_website(factory):
        website = factory.website()
        used_webpage = factory.webpage(website=website)
        factory.webpage_text_block(webpage=used_webpage)
        unused_webpage = factory.webpage(website=website)

        assert Webpage.query.count() == 2
        Webpage.delete_unused_by_website(website)
        assert Webpage.query.count() == 1
        assert used_webpage.reload() is not None

    def test_it_does_not_touch_unused_webpages_of_other_websites(factory):
        website = factory.website()
        factory.webpage(website=website)
        other_unused_webpage = factory.webpage()

        Webpage.delete_unused_by_website(website)

        assert Webpage.query.count() == 1
        assert other_unused_webpage.reload() is not None