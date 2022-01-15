import pytest
from models import Organization


def test_it_can_only_have_one_organization_per_website(factory):
    website = factory.website()
    Organization.create(website_id=website.id)
    with pytest.raises(
        Exception, match="duplicate key value violates unique constraint"
    ):
        Organization.create(website_id=website.id)
