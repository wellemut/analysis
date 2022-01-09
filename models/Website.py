from urllib.parse import urlparse
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import models


class Website(models.BaseModel):
    id = Column(Integer, primary_key=True)
    domain = Column(String, nullable=False, index=True, unique=True)

    webpages = relationship("Webpage", back_populates="website")
    text_blocks = relationship("TextBlock", back_populates="website")

    @property
    def homepage(self):
        return models.Webpage.find_by(website=self, depth=0, status_code=200)

    # Get the domain from a given URL
    @classmethod
    def domain_from_url(cls, url):
        domain = urlparse(url).netloc

        # Remove trailing www. (always use root domain)
        if domain.startswith("www."):
            domain = domain.replace("www.", "", 1)

        return domain