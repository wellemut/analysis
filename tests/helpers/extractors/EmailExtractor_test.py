from helpers.extractors import BaseExtractor, EmailExtractor


def test_it_is_an_extractor():
    assert issubclass(EmailExtractor, BaseExtractor)


def test_it_extracts_valid_emails():
    links = {
        "mailto:user@example.com": "user@example.com",
        "mailto:a@b.com?subject=abc": "a@b.com",
        "MAILto:CAP@lower.com": "cap@lower.com",
    }
    for link, email in links.items():
        assert (link, EmailExtractor.extract(link)) == (link, email)


def test_it_ignores_links_without_mailto():
    links = ["user@example.com", "https://a@b.com?subject=abc", "tel:CAP@lower.com"]
    for link in links:
        assert (link, EmailExtractor.extract(link)) == (link, None)