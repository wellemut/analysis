import pytest
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


def describe_top_candidate():
    # Simplify the extract method, so that it returns the same value as we put
    # into it. This is fine for these tests, as we already test the real extract
    # method above.
    @pytest.fixture(autouse=True)
    def mock_extract(mocker):
        mocker.patch.object(EmailExtractor, "extract", lambda cls, x: x)

    # Test helper to mock the processing/extraction of many handles
    def _process_many(extractor, handle, times):
        for num in range(times):
            extractor.process(handle, link_id=num, page_id=num)

    def it_returns_email_used_on_more_than_half_of_pages():
        e = EmailExtractor(domain="test.com", page_count=20)
        _process_many(e, "hi@test.com", 16)
        _process_many(e, "mary@test.com", 3)
        _process_many(e, "info@test.com", 1)
        assert e.top_candidate == "hi@test.com"

    def it_does_not_return_top_email_if_second_top_is_used_one_fifth_of_top():
        e = EmailExtractor(domain="test.com", page_count=20)
        _process_many(e, "hi@test.com", 16)
        _process_many(e, "mary@test.com", 4)
        assert e.top_candidate == None

    def it_returns_none_when_no_emails_were_processed():
        e = EmailExtractor(domain="test.com", page_count=20)
        assert e.top_candidate == None

    def it_returns_email_used_on_more_than_half_pages_if_no_other_email_exists():
        e = EmailExtractor(domain="test.com", page_count=20)
        _process_many(e, "hi@gmail.com", 10)
        assert e.top_candidate == "hi@gmail.com"

    def describe_when_having_email_with_common_contact_prefix():
        def it_returns_email_on_same_domain():
            e = EmailExtractor(domain="sub.test.com", page_count=20)
            _process_many(e, "jon@test.com", 9)
            _process_many(e, "info@test.com", 3)
            _process_many(e, "secretariat@sub.test.com", 1)
            assert e.top_candidate == "secretariat@sub.test.com"

        def it_returns_email_on_top_level_domain_if_no_domain_match_found():
            e = EmailExtractor(domain="sub.test.com", page_count=20)
            _process_many(e, "jon@test.com", 9)
            _process_many(e, "info@test.com", 1)
            assert e.top_candidate == "info@test.com"
