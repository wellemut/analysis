from pipelines.SocialsPipeline import SocialsPipeline
from models import Social


def test_it_identifies_socials_in_links(factory):
    organization = factory.organization()
    website = organization.website
    fb = factory.website(domain="facebook.com", top_level_domain="facebook.com")
    fb_profile = factory.webpage(website=fb, url="https://facebook.com/MYUSERPROFILE")
    factory.link(
        source_webpage=factory.webpage(website=website), target_webpage=fb_profile
    )
    factory.link(
        source_webpage=factory.webpage(website=website), target_webpage=fb_profile
    )
    factory.link(
        source_webpage=factory.webpage(website=website), target="mailto:hello@me.com"
    )

    SocialsPipeline.process(website.domain)

    assert Social.query.count() == 2
    socials = Social.query.order_by(Social.page_count.desc()).all()

    assert socials[0].organization == organization
    assert socials[0].type == "facebook"
    assert socials[0].value == "myuserprofile"
    assert socials[0].page_count == 2

    assert socials[1].organization == organization
    assert socials[1].type == "email"
    assert socials[1].value == "hello@me.com"
    assert socials[1].page_count == 1


def test_it_deletes_existing_socials(factory):
    org = factory.organization()
    factory.social(organization=org)
    factory.social(organization=org)

    assert len(org.socials) == 2

    SocialsPipeline.process(org.website.domain)

    assert len(org.socials) == 0


def test_it_counts_handles_per_unique_webpage(factory):
    organization = factory.organization()
    page = factory.webpage(website=organization.website)
    tw = factory.website(domain="twitter.com", top_level_domain="twitter.com")
    tw_profile = factory.webpage(
        website=tw, url="https://twitter.com/example/status/1234"
    )
    factory.link(source_webpage=page, target_webpage=tw_profile)
    factory.link(source_webpage=page, target_webpage=tw_profile)

    assert len(page.outbound_links) == 2

    SocialsPipeline.process(organization.website.domain)

    assert len(organization.socials) == 1
    assert organization.socials[0].type == "twitter"
    assert organization.socials[0].value == "example"
    assert organization.socials[0].page_count == 1