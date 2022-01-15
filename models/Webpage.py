from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import aliased, relationship
from sqlalchemy.ext.hybrid import hybrid_property
import models


class Webpage(models.BaseModel):
    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey("website.id"), nullable=False, index=True)
    url = Column(String, nullable=False, unique=True)
    depth = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=True)
    headers = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    content = Column(String, nullable=True)

    website = relationship(
        "Website", back_populates="webpages", foreign_keys=website_id
    )
    webpage_text_blocks = relationship("WebpageTextBlock", back_populates="webpage")
    outbound_links = relationship(
        "Link", back_populates="source_webpage", foreign_keys="Link.source_webpage_id"
    )
    inbound_links = relationship(
        "Link", back_populates="target_webpage", foreign_keys="Link.target_webpage_id"
    )

    @hybrid_property
    def is_ok_and_has_content(self):
        return self.is_ok & self.has_content

    # Return true if the page has status code 200
    @hybrid_property
    def is_ok(self):
        return self.status_code == 200

    # Return true if the page has content
    @hybrid_property
    def has_content(self):
        return self.content != None

    # Delete any webpages for the given website ID that are not being referenced
    # by any (Webpage)TextBlocks, any outbound links, or any inbound links.
    # These webpages are unused and can be removed.
    @classmethod
    def delete_unused_by_website(cls, website):
        outbound_links = aliased(models.Link)
        inbound_links = aliased(models.Link)
        cls.delete_by_ids(
            cls.id.query.join(cls.webpage_text_blocks, isouter=True)
            .join(outbound_links, cls.outbound_links, isouter=True)
            .join(inbound_links, cls.inbound_links, isouter=True)
            .where(cls.website == website)
            .where(models.WebpageTextBlock.id == None)
            .where(outbound_links.id == None)
            .where(inbound_links.id == None)
        )