import pytest
from sqlalchemy.orm import close_all_sessions
from vcr import use_cassette
from models import BaseModel, Website, Webpage

# Truncate all tables
@pytest.fixture(autouse=True)
def reset_database():
    close_all_sessions()
    with BaseModel.session.begin():
        for table in BaseModel.metadata.tables:
            BaseModel.session.execute("TRUNCATE TABLE {} CASCADE".format(table))


@pytest.fixture(scope="session")
def vcr_config():
    # Change record_mode to "once" to temporarily record new casettes/requests
    return {"record_mode": "none"}


# Factory for generating a Webpage from a URL
@pytest.fixture
def create_webpage_from_url():
    def _webpage_factory(url, **kwargs):
        domain = Website.domain_from_url(url)
        website = Website.find_by_or_create(domain=domain)
        return Webpage.create(website=website, url=url, **kwargs)

    return _webpage_factory