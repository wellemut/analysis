from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import tldextract
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