import pytest
from models import Link


def describe_delete_by_website():
    def test_it_deletes_outgoing_links_of_website(factory):
        website = factory.website()
        factory.link(source_webpage=factory.webpage(website=website))
        factory.link(source_webpage=factory.webpage(website=website))

        assert Link.query.count() == 2
        Link.delete_by_website(website)
        assert Link.query.count() == 0

    def test_it_does_not_delete_incoming_links_of_website(factory):
        website = factory.website()
        factory.link(target_webpage=factory.webpage(website=website))
        factory.link(target_webpage=factory.webpage(website=website))

        Link.delete_by_website(website)
        assert Link.query.count() == 2

    def test_it_does_not_touch_records_belonging_to_other_websites(factory):
        link = factory.link()
        other_link = factory.link()
        assert Link.query.count() == 2

        Link.delete_by_website(link.source_webpage.website)

        assert Link.query.count() == 1
        assert other_link.reload() is not None


def describe_create():
    def it_raises_error_if_both_target_and_target_webpage_are_none(factory):
        with pytest.raises(Exception, match='"link" violates check constraint'):
            Link.create(source_webpage=factory.webpage())

    def it_raises_error_if_both_target_and_target_webpage_are_provided(factory):
        with pytest.raises(Exception, match='"link" violates check constraint'):
            Link.create(
                source_webpage=factory.webpage(),
                target_webpage=factory.webpage(),
                target="mailto:user@example.com",
            )
