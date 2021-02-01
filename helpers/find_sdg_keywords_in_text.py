from helpers.get_sdg_regex_patterns import get_sdg_regex_patterns
from helpers.get_context import get_context

# Load regex patterns
regex_patterns = get_sdg_regex_patterns()
main_pattern = regex_patterns["main"]
pattern_items = regex_patterns["items"]


def find_sdg_keywords_in_text(text, tag):
    matches = []

    # Search for keywords in string
    for match in main_pattern.finditer(text):
        matched_string = match.group()

        match_found = False
        for item in pattern_items:
            # Add one match for each matching pattern
            if item["pattern"].match(matched_string):
                match_found = True
                matches.append(
                    {
                        "sdg": item["sdg"],
                        "keyword": item["keyword"],
                        "context": get_context(
                            text, start=match.start(), end=match.end(), context=50
                        ),
                        "tag": tag,
                    }
                )

        if not match_found:
            raise Exception(f"Could not find match for {matched_string}")

    return matches
