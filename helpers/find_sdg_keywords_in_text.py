from helpers.get_sdg_regex_patterns import get_sdg_regex_patterns
from helpers.get_context import get_context

# Load regex patterns
regex_patterns = get_sdg_regex_patterns()


def find_sdg_keywords_in_text(text, matches, tag):
    # Search for keywords in string
    for goal, pattern in regex_patterns.items():
        for match in pattern.finditer(text):
            matches[goal] = matches.get(goal, [])
            matches[goal].append(
                {
                    "keyword": match.group(),
                    "context": get_context(
                        text, start=match.start(), end=match.end(), context=50
                    ),
                    "tag": tag,
                }
            )
