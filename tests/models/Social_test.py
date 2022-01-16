from models import Social


def describe_delete_by_website():
    def test_it_deletes_socials_associated_with_website(factory):
        org = factory.organization()
        factory.social(organization=org)
        factory.social(organization=org)

        assert Social.query.count() == 2
        Social.delete_by_website(org.website)
        assert Social.query.count() == 0

    def test_it_does_not_touch_unassociated_socials(factory):
        social = factory.social()
        other_social = factory.social()
        assert Social.query.count() == 2

        Social.delete_by_website(social.organization.website)

        assert Social.query.count() == 1
        assert Social.find(social.id) is None
        assert Social.find(other_social.id) is not None