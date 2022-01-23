from pipelines.SocialsPipeline import SocialsPipeline
from models import Social


def test_it_identifies_socials_in_links(factory):
    organization = factory.organization()
    website = organization.website
    fb = factory.website(domain="facebook.com", top_level_domain="facebook.com")
    fb_profile = factory.webpage(website=fb, url="https://facebook.com/MYUSERPROFILE")
    factory.link(
        source_webpage=factory.webpage(website=website, content="a", status_code=200),
        target_webpage=fb_profile,
    )
    factory.link(
        source_webpage=factory.webpage(website=website, content="a", status_code=200),
        target_webpage=fb_profile,
    )
    factory.link(
        source_webpage=factory.webpage(website=website, content="a", status_code=200),
        target="mailto:hello@me.com",
    )

    SocialsPipeline.process(website.domain)

    assert Social.query.count() == 2
    socials = Social.query.order_by(Social.page_count.desc()).all()

    assert socials[0].organization == organization
    assert socials[0].type == "facebook_handle"
    assert socials[0].value == "myuserprofile"
    assert socials[0].page_count == 2

    assert socials[1].organization == organization
    assert socials[1].type == "email_address"
    assert socials[1].value == "hello@me.com"
    assert socials[1].page_count == 1

    organization.reload()
    assert organization.facebook_handle == "myuserprofile"
    assert organization.email_address == None


def test_it_deletes_existing_socials(factory):
    org = factory.organization(
        facebook_handle="a", twitter_handle="b", linkedin_handle="c", email_address="d"
    )
    factory.social(organization=org)
    factory.social(organization=org)

    assert len(org.socials) == 2
    assert org.facebook_handle == "a"
    assert org.twitter_handle == "b"
    assert org.linkedin_handle == "c"
    assert org.email_address == "d"

    SocialsPipeline.process(org.website.domain)

    assert len(org.socials) == 0
    assert org.facebook_handle == None
    assert org.twitter_handle == None
    assert org.linkedin_handle == None
    assert org.email_address == None


def test_it_counts_handles_per_unique_webpage(factory):
    organization = factory.organization()
    page = factory.webpage(website=organization.website, content="a", status_code=200)
    tw = factory.website(domain="twitter.com", top_level_domain="twitter.com")
    tw_profile = factory.webpage(
        website=tw,
        url="https://twitter.com/example/status/1234",
    )
    factory.link(source_webpage=page, target_webpage=tw_profile)
    factory.link(source_webpage=page, target_webpage=tw_profile)

    assert len(page.outbound_links) == 2

    SocialsPipeline.process(organization.website.domain)

    assert len(organization.socials) == 1
    assert organization.socials[0].type == "twitter_handle"
    assert organization.socials[0].value == "example"
    assert organization.socials[0].page_count == 1
    assert organization.twitter_handle == "example"