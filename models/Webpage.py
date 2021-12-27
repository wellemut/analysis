import os
import gzip
from uuid import uuid4
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_mixins.utils import classproperty
import tldextract
from config import ASSETS_PATH
import models


class Webpage(models.BaseModel):
    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey("website.id"), nullable=False, index=True)
    url = Column(String, nullable=False, unique=True)
    depth = Column(Integer, nullable=True)
    file_name = Column(String, nullable=True)

    website = relationship(
        "Website", back_populates="webpages", foreign_keys=website_id
    )

    @classproperty
    def settable_attributes(cls):
        return super().settable_attributes + ["content"]

    # Create a webpage from the provided URL, automatically finding the
    # associated website (or creating it, if it does not exist)
    @classmethod
    def create_from_url(cls, url):
        ext = tldextract.extract(url)
        website = models.Website.find_by_or_create(domain=f"{ext.domain}.{ext.suffix}")
        return cls.create(website=website, url=url)

    # Path to where this page's HTML content is stored
    @property
    def asset_path(self):
        if self.file_name is None:
            return None
        group = self.file_name[:2]
        return os.path.join(ASSETS_PATH, "webpages", group, f"{self.file_name}.gz")

    # Get the HTML content associated with this webpage
    @property
    def content(self):
        with gzip.open(self.asset_path, "rt") as f:
            return f.read()

    # Set the HTML content associated with this webpage
    @content.setter
    def content(self, value):
        if value is None:
            self.file_name = None
            return

        # Set file name
        self.file_name = str(uuid4())

        # Create directory unless exists
        os.makedirs(os.path.dirname(self.asset_path), exist_ok=True)

        # Write new content to file
        with gzip.open(self.asset_path, "wt") as file:
            file.write(value)