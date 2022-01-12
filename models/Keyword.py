from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import models


class Keyword(models.BaseModel):
    id = Column(Integer, primary_key=True)
    text_block_id = Column(
        Integer, ForeignKey("textblock.id"), nullable=False, index=True
    )
    keyword = Column(String, nullable=False)
    sdg = Column(Integer, nullable=False)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)

    text_block = relationship(
        "TextBlock", back_populates="keywords", foreign_keys=text_block_id
    )

    # Return keyword with a snippet of the text block content where the keyword
    # was found:
    # Keyword.query.with_transformation(Keyword.with_snippet(size=10)).all()
    @classmethod
    def with_snippet(cls, size=50):
        def _transformer(query):
            return query.join(models.TextBlock).add_columns(
                func.substr(
                    models.TextBlock.content,
                    # Starting point is not 0-based in SQL (but 1 based), so we
                    # add one at the end
                    func.greatest(Keyword.start - size, 0) + 1,
                    # Second parameter is the length of the substring (not the
                    # end)
                    Keyword.end + size - func.greatest(Keyword.start - size, 0),
                ).label("snippet")
            )

        return _transformer

    @classmethod
    def delete_by_website(cls, website):
        return cls.delete_by_ids(
            cls.id.query.join(models.TextBlock).where(
                models.TextBlock.website == website
            )
        )