from helpers.extractors import BaseExtractor


class EmailExtractor(BaseExtractor):
    name = "email"
    top_level_domains = [None]

    @classmethod
    def extract(cls, target):
        target = target.lower()

        # Only parse targets starting with mailto
        if not target.startswith("mailto:"):
            return None

        # Remove leading mailto
        target = target.replace("mailto:", "", 1)

        # Separate any query params (?subject=XYZ)
        target = target.split("?")[0]

        # Make sure @ symbol is present in email address
        if "@" not in target:
            return None

        return target