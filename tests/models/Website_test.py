import pytest
from models import Website, Webpage


def describe_homepage():
    @pytest.fixture
    def website():
        return Website.create(domain="example.com")

    @pytest.fixture
    def create_webpage(website):
        def _create_webpage(url, depth=None, status_code=None):
            Webpage.create(
                website=website, url=url, depth=depth, status_code=status_code
            )

        return _create_webpage

    def it_returns_homepage(create_webpage, website):
        create_webpage("http://www.example.com/")
        create_webpage("https://www.example.com/", depth=0, status_code=301)
        create_webpage("https://www.example.com/home", depth=0, status_code=200)
        create_webpage("https://www.example.com/a", depth=1, status_code=200)
        create_webpage("https://www.example.com/b", depth=1, status_code=200)

        assert website.homepage.url == "https://www.example.com/home"

    def it_returns_none_if_no_homepage(create_webpage, website):
        create_webpage("https://www.example.com/")
        create_webpage("https://www.example.com/a", depth=0)
        create_webpage("https://www.example.com/b", status_code=200)
        create_webpage("https://www.example.com/c", depth=1)
        create_webpage("https://www.example.com/d", depth=1)

        assert website.homepage == None