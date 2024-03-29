import random
import string
from models import (
    Keyword,
    Link,
    Organization,
    Social,
    TextBlock,
    Webpage,
    WebpageTextBlock,
    Website,
)


class FixtureFactory:
    @classmethod
    def with_defaults(cls, kwargs, defaults):
        for key, value in defaults.items():
            if key not in kwargs:
                kwargs[key] = value(kwargs) if callable(value) else value
        return kwargs

    @classmethod
    def letters(cls, count=10):
        return "".join(random.choice(string.ascii_letters) for i in range(count))

    @classmethod
    def domain(cls):
        return f"{cls.letters(10)}.com"

    @classmethod
    def link(cls, **kwargs):
        return Link.create(
            **cls.with_defaults(
                kwargs,
                dict(
                    source_webpage=lambda _: cls.webpage(),
                    target_webpage=lambda x: None if "target" in x else cls.webpage(),
                    target=lambda x: None if "target_webpage" in x else cls.letters(5),
                ),
            )
        )

    @classmethod
    def organization(cls, **kwargs):
        return Organization.create(
            **cls.with_defaults(kwargs, dict(website=lambda _: cls.website()))
        )

    @classmethod
    def webpage(cls, **kwargs):
        return Webpage.create(
            **cls.with_defaults(
                kwargs,
                dict(
                    website=lambda _: cls.website(),
                    url=lambda x: f'https://www.{x["website"].domain}/{cls.letters(5)}',
                ),
            )
        )

    @classmethod
    def webpage_text_block(cls, **kwargs):
        return WebpageTextBlock.create(
            **cls.with_defaults(
                kwargs,
                dict(
                    webpage=lambda _: cls.webpage(),
                    text_block=lambda _: cls.text_block(),
                    tag="p",
                ),
            )
        )

    @classmethod
    def website(cls, **kwargs):
        return Website.create(
            **cls.with_defaults(
                kwargs,
                dict(
                    domain=lambda _: cls.domain(),
                    top_level_domain=lambda x: x["domain"],
                ),
            )
        )

    @classmethod
    def social(cls, **kwargs):
        return Social.create(
            **cls.with_defaults(
                kwargs,
                dict(
                    organization=lambda _: cls.organization(),
                    type="twitter",
                    value=lambda _: cls.letters(10),
                    page_count=lambda _: random.randint(1, 100),
                ),
            )
        )

    @classmethod
    def text_block(cls, **kwargs):
        return TextBlock.create(
            **cls.with_defaults(
                kwargs,
                dict(
                    website=lambda _: cls.website(),
                    content=lambda _: cls.letters(15),
                    hash=lambda x: TextBlock.text_to_hash(x["content"]),
                    word_count=lambda x: TextBlock.count_words(x["content"]),
                ),
            )
        )

    @classmethod
    def keyword(cls, **kwargs):
        return Keyword.create(
            **cls.with_defaults(
                kwargs,
                dict(
                    text_block=lambda _: cls.text_block(),
                    keyword="abc",
                    start=1,
                    end=1,
                    sdg=1,
                ),
            )
        )
