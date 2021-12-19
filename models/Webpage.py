import os
import math
import gzip
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import tldextract
from config import ASSETS_PATH
import models


class Webpage(models.BaseModel):
    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey("website.id"), nullable=False, index=True)
    url = Column(String, nullable=False, unique=True)
    depth = Column(Integer, nullable=True)

    website = relationship(
        "Website", back_populates="webpages", foreign_keys=website_id
    )

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
        # We create subdirectories for every 10k files
        group = str(math.floor(self.id / 10000))
        return os.path.join(ASSETS_PATH, "webpages", group, f"{self.id}.gz")

    # Get the HTML content associated with this webpage
    @property
    def content(self):
        with gzip.open(self.asset_path, "rt") as f:
            return f.read()

    # Set the HTML content associated with this webpage
    @content.setter
    def content(self, value):
        # Create directory unless exists
        os.makedirs(os.path.dirname(self.asset_path), exist_ok=True)
        # Write new content to file
        with gzip.open(self.asset_path, "wt") as file:
            file.write(value)