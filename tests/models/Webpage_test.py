from models import Website, Webpage


def describe_create_from_url():
    def it_finds_website_if_it_exists():
        website = Website.create(domain="example.com")
        webpage = Webpage.create_from_url("https://www.example.com/my-page")
        assert webpage.website == website

    def it_creates_website_if_it_does_not_exists():
        webpage = Webpage.create_from_url("https://www.example.com/my-page")
        assert webpage.website.domain == "example.com"


def test_it_returns_ok_on_status_code_200():
    site = Website.create(domain="example.com")
    page_a = Webpage.create(website=site, url="https://example.com/a", status_code=200)
    assert page_a.is_ok

    page_b = Webpage.create(website=site, url="https://example.com/b", status_code=301)
    assert not page_b.is_ok