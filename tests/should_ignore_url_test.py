# Test should_ignore_url
from helpers.should_ignore_url import should_ignore_url

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
        assert should_ignore_url(url) == True


def test_that_terms_and_conditions_are_ignored():
    for url in terms_and_conditions:
        assert should_ignore_url(url) == True


def test_that_feeds_are_ignored():
    for url in feeds:
        assert should_ignore_url(url) == True


def test_that_misc_pages_are_ignored():
    for url in misc:
        assert should_ignore_url(url) == True
