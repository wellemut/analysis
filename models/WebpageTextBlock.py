from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import models

# Join table beween Webpage and TextBlock
class WebpageTextBlock(models.BaseModel):
    id = Column(Integer, primary_key=True)
    webpage_id = Column(Integer, ForeignKey("webpage.id"), nullable=False, index=True)
    text_block_id = Column(
        Integer, ForeignKey("textblock.id"), nullable=False, index=True
    )
    tag = Column(String, nullable=False)

    webpage = relationship(
        "Webpage", back_populates="webpage_text_blocks", foreign_keys=webpage_id
    )
    text_block = relationship(
        "TextBlock", back_populates="webpage_text_blocks", foreign_keys=text_block_id
    )

    @classmethod
    def delete_by_website(cls, website):
        return cls.delete_by_ids(
            cls.id.query.join(models.Webpage).where(models.Webpage.website == website)
        )