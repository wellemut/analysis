from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CheckConstraint
import models


class Link(models.BaseModel):
    id = Column(Integer, primary_key=True)
    source_webpage_id = Column(
        Integer, ForeignKey("webpage.id"), nullable=False, index=True
    )
    # Each link must point to a target webpage or target (mailto:, tel:, ...)
    target_webpage_id = Column(
        Integer, ForeignKey("webpage.id"), nullable=True, index=True
    )
    target = Column(String, nullable=True)

    source_webpage = relationship(
        "Webpage", back_populates="outbound_links", foreign_keys=source_webpage_id
    )
    target_webpage = relationship(
        "Webpage", back_populates="inbound_links", foreign_keys=target_webpage_id
    )

    __table_args__ = (
        (
            # Require either webpage or target on each link record, otherwise
            # raise error
            CheckConstraint(
                "(target_webpage_id IS NULL) <> (target IS NULL)",
                name="target_webpage_id_xor_target",
            )
        ),
    )

    @classmethod
    def delete_by_website(cls, website):
        return cls.delete_by_ids(
            cls.id.query.join(cls.source_webpage).where(
                models.Webpage.website == website
            )
        )