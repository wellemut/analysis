from models import Website, Webpage


def test_it_returns_ok_on_status_code_200():
    site = Website.create(domain="example.com")
    page_a = Webpage.create(website=site, url="https://example.com/a", status_code=200)
    assert page_a.is_ok

    page_b = Webpage.create(website=site, url="https://example.com/b", status_code=301)
    assert not page_b.is_ok