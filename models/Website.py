from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import models


class Website(models.BaseModel):
    id = Column(Integer, primary_key=True)
    domain = Column(String, nullable=False, index=True, unique=True)

    organization = relationship("Organization", back_populates="website", uselist=False)
    webpages = relationship("Webpage", back_populates="website")
    text_blocks = relationship("TextBlock", back_populates="website")

    # Return the suggested homepage based on webpages that have been scraped
    @property
    def suggested_homepage(self):
        return models.Webpage.find_by(website=self, depth=0, status_code=200)