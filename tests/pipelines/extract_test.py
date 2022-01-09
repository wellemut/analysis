from models.WebpageTextBlock import WebpageTextBlock
from pipelines import ExtractPipeline
from models import TextBlock, Keyword


def test_it_extracts_text_blocks_from_webpages(create_webpage_from_url):
    page1 = create_webpage_from_url(
        "https://www.17ziele.de",
        content="""
        <html>
            <head><title>my title</title>
            <body>
                <h1>hello <span>world!</span></h1>
            </body>
        </html>""",
    )
    create_webpage_from_url(
        "https://www.17ziele.de/abc",
        content="""
        <html>
            <body>
                <p>hello world!</p>
            </body>
        </html>""",
    )

    ExtractPipeline.process("17ziele.de")

    assert TextBlock.query.count() == 2
    assert len(page1.webpage_text_blocks) == 2
    assert page1.webpage_text_blocks[0].tag == "title"
    assert page1.webpage_text_blocks[0].text_block.content == "my title"


def test_it_ignores_pages_without_content(create_webpage_from_url):
    create_webpage_from_url("https://www.17ziele.de", content="<body>abc</body>")
    create_webpage_from_url("https://www.17ziele.de/home")

    ExtractPipeline.process("17ziele.de")

    assert TextBlock.query.count() == 1


def test_it_ignores_blocklisted_urls(create_webpage_from_url):
    create_webpage_from_url(
        "https://www.17ziele.de/privacy.html",
        content="<body><p>ignore content</p></body>",
    )

    ExtractPipeline.process("17ziele.de")

    assert TextBlock.query.count() == 0


def test_it_removes_associated_records_for_the_website(create_webpage_from_url):
    webpage = create_webpage_from_url(
        "https://www.17ziele.de", content="<body>hello world</body>"
    )
    block = TextBlock.create(
        website=webpage.website, content="xyz", hash="abc", word_count=1
    )
    WebpageTextBlock.create(webpage=webpage, text_block=block, tag="p")
    Keyword.create(text_block=block, keyword="a", sdg=1, start=0, end=1)

    other_webpage = create_webpage_from_url("https://example.com")
    other_block = TextBlock.create(
        website=other_webpage.website, content="xyz", hash="abc", word_count=1
    )
    WebpageTextBlock.create(webpage=other_webpage, text_block=other_block, tag="p")

    ExtractPipeline.process("17ziele.de")

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

    def test_that_misc_pages_are_ignored():
        for url in misc:
            assert ExtractPipeline.is_url_blocklisted(url) == True