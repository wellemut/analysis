import re

WHITESPACE_PATTERN = re.compile(r"\s+", re.MULTILINE)


def squish(text):
    return WHITESPACE_PATTERN.sub(" ", text).strip()
