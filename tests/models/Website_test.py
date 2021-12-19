from models import Website, Webpage


def describe_homepage():
    def it_returns_homepage():
        website = Website.create(domain="example.com")
        Webpage.create(website=website, url="https://www.example.com/")
        Webpage.create(website=website, url="https://www.example.com/home", depth=0)
        Webpage.create(website=website, url="https://www.example.com/a", depth=1)
        Webpage.create(website=website, url="https://www.example.com/b", depth=1)

        assert website.homepage.url == "https://www.example.com/home"

    def it_returns_none_if_no_homepage():
        website = Website.create(domain="example.com")
        Webpage.create(website=website, url="https://www.example.com/")
        Webpage.create(website=website, url="https://www.example.com/a", depth=1)
        Webpage.create(website=website, url="https://www.example.com/b", depth=1)

        assert website.homepage == None