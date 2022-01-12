from models import Website, Webpage


def test_it_returns_ok_on_status_code_200(factory):
    page_a = factory.webpage(status_code=200)
    assert page_a.is_ok

    page_b = factory.webpage(status_code=301)
    assert not page_b.is_ok