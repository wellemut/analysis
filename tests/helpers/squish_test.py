from helpers import squish


def test_it_removes_leading_and_trailing_whitespace():
    assert squish("   hello world!  ") == "hello world!"


def test_it_squishes_whitespaces_inside_text():
    assert squish(" \n\thello  \n  \t world!  ") == "hello world!"