import pytest
from sqlalchemy.orm import close_all_sessions
from models import BaseModel
from .FixtureFactory import FixtureFactory

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


# A factory for generating models
@pytest.fixture
def factory():
    return FixtureFactory