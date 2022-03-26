from models.WebpageTextBlock import WebpageTextBlock
from pipelines.ExtractPipeline import ExtractPipeline
from models import TextBlock


def test_it_extracts_text_blocks_from_webpages(factory):
    website = factory.website()
    page1 = factory.webpage(
        website=website,
        status_code=200,
        content="""
        <html>
            <head><title>my title</title>
            <body>
                <h1>hello <span>world!</span></h1>
            </body>
        </html>""",
    )
    factory.webpage(
        website=website,
        status_code=200,
        content="""
        <html>
            <body>
                <p>hello world!</p>
            </body>
        </html>""",
    )

    ExtractPipeline.process(website.domain)

    assert TextBlock.query.count() == 2
    assert len(page1.webpage_text_blocks) == 2
    assert page1.webpage_text_blocks[0].tag == "title"
    assert page1.webpage_text_blocks[0].text_block.content == "my title"


def test_it_ignores_pages_without_content_and_status_200(factory):
    site = factory.website()
    page = factory.webpage(website=site, content="<body>abc</body>", status_code=200)
    factory.webpage(website=site, content="<body>abc</body>", status_code=301)
    factory.webpage(website=site, content="<body>abc</body>", status_code=404)
    factory.webpage(website=site, content=None, status_code=200)

    ExtractPipeline.process(site.domain)

    assert TextBlock.query.count() == 1
    assert len(page.webpage_text_blocks) == 1


def test_it_ignores_blocklisted_urls(factory):
    page = factory.webpage(
        url="https://www.example.com/privacy",
        content="<body><p>ignore content</p></body>",
        status_code=200,
    )

    ExtractPipeline.process(page.website.domain)

    assert TextBlock.query.count() == 0


def test_it_removes_associated_records_for_the_website(factory):
    webpage = factory.webpage(
        url="https://www.example.com/my-page",
        content="<body>hello world</body>",
        status_code=200,
    )
    block = factory.text_block(website=webpage.website)
    factory.webpage_text_block(webpage=webpage, text_block=block)
    factory.keyword(text_block=block)

    other_webpage = factory.webpage()
    other_block = factory.text_block(website=other_webpage.website)
    factory.webpage_text_block(webpage=other_webpage, text_block=other_block)

    ExtractPipeline.process(webpage.website.domain)

    assert TextBlock.query.count() == 2
    assert WebpageTextBlock.query.count() == 2
    assert len(webpage.webpage_text_blocks) == 1
    assert webpage.webpage_text_blocks[0].tag == "body"
    assert webpage.webpage_text_blocks[0].text_block.content == "hello world"

    # Does not touch other webpage's text blocks
    assert len(other_webpage.reload().webpage_text_blocks) == 1


def describe_is_url_blocklisted():
    privacy_policies = [
        "https://www.tier.app/privacy.html",
        "https://www.strayz.de/Privacy",
        "https://www.tier.app/de/privacy-notice/",
        "https://www.tier.app/privacy-policy/",
        "https://pi.pe/privacy_policy/index.html",
        "https://www.zolar.de/datenschutz",
        "https://niyok.de/pages/datenschutz-impressum",
        "https://www.silfir.com/privacy-datenschutz",
        "https://www.ecf-farmsystems.com/datenschutzerklaerung/",
        "https://www.solarkiosk.eu/data-protection/",
        "https://humanoo.com/en/data-security/",
        "https://www.12tree.de/privacy-statement",
        "https://cogniscent.io/privacy-policy-en",
        "https://mitte.co/privacy-policy-2/",
        "https://smarterials.berlin/en/gpdr/",
        "https://sanitygroup.com/data-privacy/",
        "https://www.milkthesun.com/en/data-privacy-statement",
        "https://www.epigenomics.com/imprint/data-protection-statement/",
        "https://www.noerr.com/de/meta/datenschutz",
        "https://www.alnatura.de/de-de/ueber-uns/datenschutzhinweis/",
    ]

    terms_and_conditions = [
        "https://www.tier.app/agb.html",
        "https://www.tier.app/de/terms-and-conditions/",
        "https://www.ansmann.de/no/general-terms-and-conditions",
        "http://www.ea.com/terms-of-service",
        "https://klima.com/terms-of-service/",
        "https://chatterbug.com/en/legal/terms",
        "https://greenfashiontours.com/imprint-and-privacy-protection/",
        "https://marleyspoon.com/terms",
        "https://www.fixfirst.de/nutzungsbedingungen",
        "https://plantix.net/imprint",
        "https://www.lindera.de/agbs",
        "https://plana.earth/terms-conditions",
        "https://www.zolar.de/allgemeine-geschaeftsbedingungen",
        "https://careloop.io/en/agb-en/",
        "https://www.xayn.com/terms-of-use",
        "https://www.teamviewer.com/eula/",
    ]

    feeds = [
        "https://merics.org/en/rss",
        "https://www.brot-fuer-die-welt.de/presse/",
        "https://www.baumev.de/Presse.html",
        "https://sanitygroup.com/press/",
        "https://www.pro-bahn-berlin.de/blog.html",
        "https://de.squarespace.com/blog/category/makers",
        "https://door2door.io/de/news/mediathek/",
        "https://einhorn.my/press-page/",
        "https://www.hcu-hamburg.de/presse/news/news/",
        "https://www.koblenz.de/coronavirus/aktuelle-meldungen/",
        "https://www.lateinamerikaverein.de/de/aktuelles/corona-news",
        "https://www.nakos.de/aktuelles/nachrichten/",
        "https://power-shift.de/feed/",
        "https://www.osnabrueck.de/start/archiv/nachrichtenarchiv.html",
        "https://www.ge.com/power/about/press-releases",
    ]

    team = [
        "https://www.example.com/team",
        "https://www.example.com/author/john",
        "https://www.example.com/authors/frank",
        "https://www.example.com/about/staff",
        "https://www.example.com/careers",
        "https://www.example.com/about/sarah/bio",
    ]

    misc = [
        "https://www.muelheim-ruhr.de/cms/shared/sitemap.php",
        "https://cenior.de/Impressum",
        "https://medexo.com/service-bereich/kontakt/",
        "https://www.milkthesun.com/en/jobs",
        "https://www.gfk.com/contact",
    ]

    def test_that_privacy_policies_are_ignored():
        for url in privacy_policies:
            assert ExtractPipeline.is_url_blocklisted(url) == True

    def test_that_terms_and_conditions_are_ignored():
        for url in terms_and_conditions:
            assert ExtractPipeline.is_url_blocklisted(url) == True

    def test_that_feeds_are_ignored():
        for url in feeds:
            assert ExtractPipeline.is_url_blocklisted(url) == True

    def test_that_team_pages_are_ignored():
        for url in team:
            assert ExtractPipeline.is_url_blocklisted(url) == True

    def test_that_misc_pages_are_ignored():
        for url in misc:
            assert ExtractPipeline.is_url_blocklisted(url) == True