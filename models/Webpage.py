from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from . import BaseModel


class Webpage(BaseModel):
    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey("website.id"), nullable=False, index=True)
    url = Column(String, nullable=False, unique=True)
    depth = Column(Integer, nullable=True)

    website = relationship(
        "Website", back_populates="webpages", foreign_keys=website_id
    )
