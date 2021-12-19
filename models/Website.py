from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from . import BaseModel


class Website(BaseModel):
    id = Column(Integer, primary_key=True)
    domain = Column(String, nullable=False, index=True, unique=True)

    webpages = relationship("Webpage", back_populates="website")
