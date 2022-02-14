from helpers import extract_texts_from_html


def test_it_extracts_contained_tags():
    texts = extract_texts_from_html(
        """<body>
        <h1>Hello <span>world</span>!</h1>
        <span>outer <span>inner</span></span>
        </body>"""
    )
    assert len(texts) == 2
    assert texts[0]["tag"] == "h1"
    assert texts[0]["content"] == "Hello world !"
    assert texts[1]["tag"] == "body"
    assert texts[1]["content"] == "outer inner"


def test_it_extracts_title_and_meta_description():
    texts = extract_texts_from_html(
        """
    <html>
        <head>
            <title>my page title</title>
            <meta name="description" content="my description" />
        </head>
        <body></body>
    </html>"""
    )

    assert len(texts) == 2
    assert texts[0]["tag"] == "title"
    assert texts[0]["content"] == "my page title"
    assert texts[1]["tag"] == "meta description"
    assert texts[1]["content"] == "my description"


def test_it_extracts_body_text_last():
    texts = extract_texts_from_html(
        """
        <body>
            toast
            <p>hello</p>
            bread
        </body>
    """
    )

    assert len(texts) == 2
    assert texts[0]["tag"] == "p"
    assert texts[0]["content"] == "hello"
    assert texts[1]["tag"] == "body"
    assert texts[1]["content"] == "toast bread"


def test_it_includes_deeply_nested_tags():
    texts = extract_texts_from_html(
        """
        <body>
            <div>
                <span>
                    <b>hello</b>
                </span>
            </div>
        </body>"""
    )

    assert len(texts) == 1
    assert texts[0]["tag"] == "div"
    assert texts[0]["content"] == "hello"


def test_it_extracts_child_tags_before_parents():
    texts = extract_texts_from_html(
        """
        <body>
            <main>
                <div>
                    <info>
                        all my content
                        <div>ok <b>hello!</b></div>
                    </info>
                </div>
            </main>
        </body>"""
    )
    assert len(texts) == 2
    assert texts[0]["tag"] == "div"
    assert texts[0]["content"] == "ok hello!"
    assert texts[1]["tag"] == "div"
    assert texts[1]["content"] == "all my content"


def test_it_includes_image_alt_tags():
    texts = extract_texts_from_html(
        """
        <body>
            <img src="lorem" alt="image description" />
        </body>"""
    )

    assert len(texts) == 1
    assert texts[0]["tag"] == "img"
    assert texts[0]["content"] == "image description"


def test_it_extracts_list_items():
    texts = extract_texts_from_html(
        """
        <body>
            <ol>
                <li>hello world!</li><li>test</li>
            </ol>
        </body>
        """
    )
    assert len(texts) == 1
    assert texts[0]["tag"] == "ol"
    assert texts[0]["content"] == "hello world! test"


def test_it_splits_content_at_br_tags():
    texts = extract_texts_from_html(
        """<body>
        <p>mission:<br/>improve life</p>
        <p>vision<br>- item 1<br>- item 2</p>
        </body>"""
    )
    assert texts[0]["tag"] == "p"
    assert texts[0]["content"] == "mission: . improve life"
    assert texts[1]["tag"] == "p"
    assert texts[1]["content"] == "vision . - item 1 . - item 2"


def test_it_ignores_html_comments():
    texts = extract_texts_from_html(
        """
        <body>
            <!--<p>hello</p>-->
            <!--<span>ok</span>-->
            <span>include</span>
        </body>"""
    )

    assert len(texts) == 1
    assert texts[0]["content"] == "include"


def test_it_ignores_script_tags():
    texts = extract_texts_from_html(
        """
        <body>
            <script>
                <h1>inside script</h1>
            </script>
        </body>"""
    )

    assert len(texts) == 0


def test_it_does_not_fail_when_tag_content_is_none():
    texts = extract_texts_from_html("<body><img /></body>")
    assert len(texts) == 0