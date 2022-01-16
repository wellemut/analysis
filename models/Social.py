from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import models


class Social(models.BaseModel):
    id = Column(Integer, primary_key=True)
    organization_id = Column(
        Integer, ForeignKey("organization.id"), nullable=False, index=True
    )
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    page_count = Column(Integer, nullable=False)

    organization = relationship(
        "Organization", back_populates="socials", foreign_keys=organization_id
    )

    @classmethod
    def delete_by_website(cls, website):
        return cls.delete_by_ids(
            cls.id.query.join(cls.organization).where(
                models.Organization.website == website
            )
        )