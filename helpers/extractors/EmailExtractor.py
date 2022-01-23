from functools import cache
from helpers import get_top_level_domain_from_url
from helpers.extractors import BaseExtractor


class EmailExtractor(BaseExtractor):
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

    # Return true if the email address starts with a common prefix for contact
    # email addresses, like info@company.org
    @staticmethod
    def has_common_prefix(email):
        return email.split("@")[0] in ["info", "contact", "secretariat", "director"]

    # Return true if the given email address belongs to the domain of this
    # extractor
    def belongs_to_domain(self, email):
        return email.split("@", 1)[1] == self.domain

    # Return true if the given email address belongs to the top level domain of
    # this extractor
    def belongs_to_top_level_domain(self, email):
        return email.split("@", 1)[1] == self.top_level_domain

    # Get the top level domain for this extractor
    @property
    @cache
    def top_level_domain(self):
        return get_top_level_domain_from_url(f"https://{self.domain}")

    @property
    def top_candidate(self):
        results = self.results

        if len(results) == 0:
            return None

        # Is the email used on at least 50% of pages?
        is_used_often = results[0]["frequency"] >= 0.5

        # Is the email address used 5 times as much as the next one
        has_frequency_ratio_5 = False
        if len(results) == 1 or results[0]["frequency"] >= results[1]["frequency"] * 5:
            has_frequency_ratio_5 = True

        # If the most used email address is used on at least 50% of pages and at
        # least 5 times as much as the second most frequent email address,
        # return it
        if is_used_often and has_frequency_ratio_5:
            return results[0]["handle"]

        # If there is an email address with one of the following prefixes often
        # used for contact email addresses, then return if it matches the
        # given domain or top level domain
        contact_results = [
            result for result in results if self.has_common_prefix(result["handle"])
        ]

        # See if a contact email matches the given domain
        for result in contact_results:
            if self.belongs_to_domain(result["handle"]):
                return result["handle"]

        # See if a contact email matches the given top level domain
        # top_level_domain =
        for result in contact_results:
            if self.belongs_to_top_level_domain(result["handle"]):
                return result["handle"]

        return None