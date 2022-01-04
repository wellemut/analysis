import pytest
from models import TextBlock, Website


def describe_content_to_hash():
    def it_converts_rabbit_to_HASH():
        assert (
            TextBlock.text_to_hash("rabbit")
            == "d37d96b42ad43384915e4513505c30c0b1c4e7c765b5577eda25b5dbd7f26d89"
        )


def describe_count_words():
    def it_returns_number_of_words():
        assert TextBlock.count_words("hello world,  this is a sentence") == 6

    def it_returns_zero_if_only_spaces():
        assert TextBlock.count_words("    ") == 0


def describe_create():
    def it_cannot_create_two_identical_text_blocks_for_the_same_website():
        website = Website.create(domain="example.com")
        TextBlock.create(
            website=website, hash="abc", word_count=2, content="hello world!"
        )
        with pytest.raises(
            Exception, match="duplicate key value violates unique constraint"
        ):
            TextBlock.create(
                website=website, hash="abc", word_count=2, content="hello world!"
            )

    def it_can_create_identical_text_blocks_for_different_websites():
        TextBlock.create(
            website=Website.create(domain="example.com"),
            hash="abc",
            word_count=2,
            content="hello world!",
        )
        TextBlock.create(
            website=Website.create(domain="test.com"),
            hash="abc",
            word_count=2,
            content="hello world!",
        )
        assert TextBlock.query.count() == 2

    def it_cannot_be_created_without_content_or_hash_or_word_count():
        with pytest.raises(Exception, match='null value in column "word_count"'):
            TextBlock.create(content="abc", hash="abc")
        with pytest.raises(Exception, match='null value in column "hash"'):
            TextBlock.create(content="abc", word_count=1)
        with pytest.raises(Exception, match='null value in column "content"'):
            TextBlock.create(hash="abc", word_count=1)

    def it_cannot_be_created_with_empty_content():
        with pytest.raises(Exception, match="Text block content cannot be empty"):
            TextBlock.create(content="", hash="abc", word_count=1)

    def it_cannot_be_created_with_word_count_zero():
        with pytest.raises(Exception, match="Text block word count cannot be zero"):
            TextBlock.create(content="     ", hash="abc", word_count=0)
