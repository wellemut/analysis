from hashlib import sha256
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
import models


class TextBlock(models.BaseModel):
    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey("website.id"), nullable=False)
    hash = Column(String, nullable=False)
    word_count = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    language = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("website_id", "hash"),)

    website = relationship(
        "Website", back_populates="text_blocks", foreign_keys=website_id
    )
    webpage_text_blocks = relationship("WebpageTextBlock", back_populates="text_block")
    keywords = relationship("Keyword", back_populates="text_block")

    @classmethod
    def find_by_content_or_create(cls, content):
        hash = cls.text_to_hash(content)
        return cls.find_by(hash=hash) or cls.create(
            content=content,
            hash=hash,
            word_count=cls.count_words(content),
        )

    @classmethod
    def text_to_hash(cls, text):
        return sha256(text.encode()).hexdigest()

    @classmethod
    def count_words(cls, text):
        return len(text.split())

    # Make sure content and word count are valid
    def on_create(self):
        if self.content == "":
            raise Exception("Text block content cannot be empty.")
        if self.word_count == 0:
            raise Exception("Text block word count cannot be zero.")

    # Make sure content and word count are valid
    def on_update(self):
        if self.content == "":
            raise Exception("Text block content cannot be empty.")
        if self.word_count == 0:
            raise Exception("Text block word count cannot be zero.")
