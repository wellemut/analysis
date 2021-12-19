import os
from models import Website, Webpage


def describe_create_from_url():
    def it_finds_website_if_it_exists():
        website = Website.create(domain="example.com")
        webpage = Webpage.create_from_url("https://www.example.com/my-page")
        assert webpage.website == website

    def it_creates_website_if_it_does_not_exists():
        webpage = Webpage.create_from_url("https://www.example.com/my-page")
        assert webpage.website.domain == "example.com"


def test_it_can_set_and_get_content():
    webpage = Webpage.create_from_url("https://www.example.com/")
    webpage.content = "<h1>hello world!</h1>"
    assert os.path.isfile(webpage.asset_path) == True
    assert webpage.content == "<h1>hello world!</h1>"