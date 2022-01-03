from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import tldextract
import models


class Webpage(models.BaseModel):
    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey("website.id"), nullable=False, index=True)
    url = Column(String, nullable=False, unique=True)
    depth = Column(Integer, nullable=True)
    content = Column(String, nullable=True)

    website = relationship(
        "Website", back_populates="webpages", foreign_keys=website_id
    )
    webpage_text_blocks = relationship("WebpageTextBlock", back_populates="webpage")

    # Create a webpage from the provided URL, automatically finding the
    # associated website (or creating it, if it does not exist)
    @classmethod
    def create_from_url(cls, url):
        ext = tldextract.extract(url)
        website = models.Website.find_by_or_create(domain=f"{ext.domain}.{ext.suffix}")
        return cls.create(website=website, url=url)
