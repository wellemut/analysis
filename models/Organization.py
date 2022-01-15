from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import models


class Organization(models.BaseModel):
    id = Column(Integer, primary_key=True)
    website_id = Column(
        Integer, ForeignKey("website.id"), nullable=False, index=True, unique=True
    )
    homepage = Column(String, nullable=True)
    meta = Column(JSONB, nullable=True)

    website = relationship(
        "Website", back_populates="organization", foreign_keys=website_id
    )
    # relationship outbound_connections defined in models.Connection
    # relationship inbound_connections defined in models.Connection