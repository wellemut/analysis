from urllib.parse import urlparse
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
import models


class Website(models.BaseModel):
    id = Column(Integer, primary_key=True)
    domain = Column(String, nullable=False, index=True, unique=True)
    homepage = Column(String, nullable=True)
    meta = Column(JSON, nullable=True)

    webpages = relationship("Webpage", back_populates="website")
    text_blocks = relationship("TextBlock", back_populates="website")

    # Return the suggested homepage based on webpages that have been scraped
    @property
    def suggested_homepage(self):
        return models.Webpage.find_by(website=self, depth=0, status_code=200)