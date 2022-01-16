from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import aliased, relationship
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

    # Return keyword with a snippet of the text block content where the keyword
    # was found:
    # Keyword.query.with_transformation(Keyword.with_snippet(size=10)).all()
    @classmethod
    def with_filter_by_source_website(cls, website):
        def _transformer(query):
            source_webpage = aliased(models.Webpage)
            return query.join(source_webpage, cls.source_webpage).where(
                source_webpage.website == website
            )

        return _transformer

    @classmethod
    def delete_by_website(cls, website):
        return cls.delete_by_ids(
            cls.id.query.with_transformation(
                Link.with_filter_by_source_website(website)
            )
        )