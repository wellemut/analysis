def describe_suggested_homepage():
    def it_returns_homepage(factory):
        site = factory.website()
        factory.webpage(website=site, depth=0, status_code=301)
        root_page = factory.webpage(website=site, depth=0, status_code=200)
        factory.webpage(website=site, depth=1, status_code=200)
        factory.webpage(website=site, depth=1, status_code=200)

        assert site.suggested_homepage == root_page

    def it_returns_none_if_no_homepage(factory):
        site = factory.website()
        factory.webpage(website=site)
        factory.webpage(website=site, depth=0)
        factory.webpage(website=site, status_code=200)
        factory.webpage(website=site, depth=1)
        factory.webpage(website=site, depth=1)

        assert site.suggested_homepage == None