from helpers import get_domain_from_url


def test_it_returns_root_domain():
    assert get_domain_from_url("http://www.example.com") == "example.com"
    assert get_domain_from_url("http://example.com/abc/def") == "example.com"
    assert get_domain_from_url("http://sub.test.com") == "sub.test.com"
    assert get_domain_from_url("http://www.sub.test.com") == "sub.test.com"


def test_it_removes_ports():
    assert get_domain_from_url("https://example.com:80") == "example.com"


def test_it_lowercases_domain():
    assert get_domain_from_url("https://Example.COM") == "example.com"


def test_it_returns_none_for_invalid_domains():
    invalid = [
        "https://www.example",
        "email@gmail.com",
        "/internal-link",
        "/internal.com",
        "test.me",
        "https://user:password:ok",
        "https://the%20news%now.com",
        "http://hello world",
        "https://" + "abc" * 100 + ".com",
    ]

    for domain in invalid:
        assert get_domain_from_url(domain) == None