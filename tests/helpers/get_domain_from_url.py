from helpers import get_domain_from_url


def test_it_returns_root_domain():
    assert get_domain_from_url("http://www.example.com") == "example.com"
    assert get_domain_from_url("http://example.com/abc/def") == "example.com"
    assert get_domain_from_url("http://sub.test.com") == "sub.test.com"
    assert get_domain_from_url("http://www.sub.test.com") == "sub.test.com"
