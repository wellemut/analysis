from pipelines.LinksPipeline import LinksPipeline
from models import Link


def test_it_identifies_links_in_content(factory):
    website = factory.website()
    webpage = factory.webpage(
        website=website,
        status_code=200,
        content="""
        <body>
            <a href="https://test.com/">test</a>
            <a href="http://test.com/abc">http</a>
            <a href="mailto:user@gmail.com">mailto</a>
            <a href="tel:+9999">tel</a>
            <a href="/internal">internal</a>
            <a>no href</a>
            <a href="ftp://example.com/">ftp</a>
        </body>""",
    )

    LinksPipeline.process(website.domain)

    assert Link.query.count() == 4
    links = webpage.outbound_links
    assert links[0].target_webpage.url == "https://test.com/"
    assert links[0].target_webpage.website.domain == "test.com"
    assert links[1].target_webpage.url == "http://test.com/abc"
    assert links[1].target_webpage.website.domain == "test.com"
    assert links[2].target_webpage == None
    assert links[2].target == "mailto:user@gmail.com"
    assert links[3].target_webpage == None
    assert links[3].target == "tel:+9999"


def test_it_deletes_existing_links(factory):
    webpage = factory.webpage()
    factory.link(source_webpage=webpage)
    factory.link(source_webpage=webpage)

    assert len(webpage.outbound_links) == 2

    LinksPipeline.process(webpage.website.domain)

    assert len(webpage.outbound_links) == 0


def test_it_ignores_pages_without_content_and_status_200(factory):
    site = factory.website()
    content_with_link = "<body><a href='https://example.com'>test</a></body>"
    page = factory.webpage(website=site, content=content_with_link, status_code=200)
    factory.webpage(website=site, content=content_with_link, status_code=301)
    factory.webpage(website=site, content=content_with_link, status_code=404)
    factory.webpage(website=site, content=None, status_code=200)

    LinksPipeline.process(site.domain)

    assert Link.query.count() == 1
    assert len(page.outbound_links) == 1


def describe_is_email():
    def it_returns_true_for_valid_emails():
        assert LinksPipeline.is_email("mailto:user@example.com") == True
        assert LinksPipeline.is_email("mailto:user@example.com?subject=hello") == True
        assert LinksPipeline.is_email("MAiLto:user@example.com") == True

    def it_returns_false_for_non_mailto_links():
        assert LinksPipeline.is_email("mail:user@example.com") == False
        assert LinksPipeline.is_email("user@example.com") == False
        assert LinksPipeline.is_email("https://user@example.com") == False
        assert LinksPipeline.is_email("tel:user@example.com") == False

    def it_returns_false_if_link_has_no_at_symbol():
        assert LinksPipeline.is_email("mailto:?subject=email") == False


def describe_is_phone():
    def it_returns_true_for_url_starting_with_tel():
        assert LinksPipeline.is_phone("tel:123") == True
        assert LinksPipeline.is_phone("tel:+04537175") == True
        assert LinksPipeline.is_phone("TEl:AbCDEfgh") == True

    def it_returns_false_for_non_tel_links():
        assert LinksPipeline.is_phone("mailto:12344756") == False
        assert LinksPipeline.is_phone("https://4475321473") == False