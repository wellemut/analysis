import pytest
from models import TextBlock


def describe_find_by_content_or_create():
    def it_creates_new_text_block_with_hash_and_word_count():
        block = TextBlock.find_by_content_or_create("hello world!")
        assert block.id != None
        assert (
            block.hash
            == "7509e5bda0c762d2bac7f90d758b5b2263fa01ccbc542ab5e3df163be08e6ca9"
        )
        assert block.word_count == 2
        assert TextBlock.query.count() == 1

    def it_returns_existing_text_block_if_block_with_same_hash_exists():
        block = TextBlock.find_by_content_or_create("hello world!")
        block2 = TextBlock.find_by_content_or_create("hello world!")
        assert block.id == block2.id
        assert TextBlock.query.count() == 1


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
