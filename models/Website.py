from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import models


class Website(models.BaseModel):
    id = Column(Integer, primary_key=True)
    domain = Column(String, nullable=False, index=True, unique=True)

    webpages = relationship("Webpage", back_populates="website")

    @property
    def homepage(self):
        return models.Webpage.find_by(website=self, depth=0)