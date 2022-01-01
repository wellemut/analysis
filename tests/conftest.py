import os
import shutil
import pytest
from sqlalchemy.orm import close_all_sessions
from vcr import use_cassette
import tldextract
from config import APPLICATION_DATA_PATH
from models import BaseModel

# Truncate all tables
@pytest.fixture(autouse=True)
def reset_database():
    close_all_sessions()
    with BaseModel.session.begin():
        for table in BaseModel.metadata.tables:
            BaseModel.session.execute("TRUNCATE TABLE {} CASCADE".format(table))


# Clear application data directory
@pytest.fixture(autouse=True)
def reset_application_data():
    for filename in os.listdir(APPLICATION_DATA_PATH):
        file_path = os.path.join(APPLICATION_DATA_PATH, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


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