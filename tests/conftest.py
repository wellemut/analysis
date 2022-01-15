import os
import pytest
from sqlalchemy.orm import close_all_sessions
from vcr import use_cassette
import tldextract
from models import BaseModel
from .FixtureFactory import FixtureFactory

# Truncate all tables
@pytest.fixture(autouse=True)
def reset_database():
    close_all_sessions()
    with BaseModel.session.begin():
        for table in BaseModel.metadata.tables:
            BaseModel.session.execute("TRUNCATE TABLE {} CASCADE".format(table))


# Make a request with TLD extract to cache the Public Suffix List (PLS)
# See: https://github.com/john-kurkowski/tldextract#note-about-caching
@pytest.fixture(autouse=True, scope="session")
def cache_tld_extract():
    with use_cassette(
        os.path.join(
            os.path.dirname(__file__),
            "casettes",
            "conftest",
            "cache_tld_extract.yaml",
        ),
        record_mode="once",
    ):
        tldextract.extract("example.com")


@pytest.fixture(scope="session")
def vcr_config():
    # Change record_mode to "once" to temporarily record new casettes/requests
    return {"record_mode": "none"}


# A factory for generating models
@pytest.fixture
def factory():
    return FixtureFactory