# Extract the text from the given CSS object and the
# provided query string.
def extract_text_from(css_object, query):
    if not query:
        return None

    full_query = format_query(query, ' *::text')

    # Get string contents
    contents    = css_object.css(full_query).getall()

    # Strip, combine, encode
    stripped    = list(map(str.strip, contents))
    joint       = u'\n'.join(stripped)
    text        = joint.strip()

    return text

# Appends default_selector (such as ' *::text') to the query, unless
# the query already has a selector set
def format_query(query, default_selector):
    is_exact_query = '::' in query

    if is_exact_query:
        return query
    else:
        return query + default_selector
