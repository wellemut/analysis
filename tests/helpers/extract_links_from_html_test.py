from helpers import extract_links_from_html


def test_it_extracts_all_hrefs_from_anchor_tags():
    links = extract_links_from_html(
        """<body>
        <div>
        <a href="https://test.com/abc">test.com</a>
        <a href="/example/website">test.com</a>
        <p><a href="https://www.example.com">test.com</a></p>
        </div>
        </body>"""
    )
    assert len(links) == 3
    assert links[0] == "https://test.com/abc"
    assert links[1] == "/example/website"
    assert links[2] == "https://www.example.com"


def test_it_extracts_mailto_and_tel_links():
    links = extract_links_from_html(
        """
    <html>
        <body>
            <p>
                <a href="mailto:hello@example.com" target="_blank">email</a>
                <a href="tel:+1234">tel</a>
            </p>
        </body>
    </html>"""
    )
    assert len(links) == 2
    assert links[0] == "mailto:hello@example.com"
    assert links[1] == "tel:+1234"


def test_it_ignores_links_without_href():
    links = extract_links_from_html(
        '<html><body><a target="_blank">no href</a></body></html>'
    )
    assert len(links) == 0


def test_it_handles_child_elements_in_anchor_tags():
    links = extract_links_from_html(
        """<body>
            <a href="https://test.com/">
                ok test <img src="img.png" />
            </a>
        </body>"""
    )
    assert links == ["https://test.com/"]


def test_it_handles_doctype_correctly():
    links = extract_links_from_html(
        """<!DOCTYPE html>
        <html>
            <body>
                <a href="https://test.com/">test</a>
            </body>
        </html>"""
    )
    assert links == ["https://test.com/"]