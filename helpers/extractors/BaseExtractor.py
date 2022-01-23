from collections import Counter
import re
from jellyfish import jaro_winkler_similarity


class BaseExtractor:
    def __init__(self, domain, page_count):
        self.domain = domain
        self.page_count = page_count
        self.extractions = []

    @classmethod
    def extract(cls, link):
        raise Exception(f"Method 'extract' is not implemented in {cls}.")

    # Attempt to extract a result from the given link and keep track of the
    # link ID and page ID that the link belongs to.
    def process(self, link, link_id, page_id):
        handle = self.extract(link)
        if handle:
            self.extractions.append(
                dict(handle=handle, link_id=link_id, page_id=page_id)
            )

    # Return a dictionary of handles and the number of pages where the handle
    # was found
    @property
    def counts(self):
        return Counter(
            {result["handle"]: result["page_count"] for result in self.results}
        )

    # Return a list of handles and handle statistics (# of links, # of pages,
    # frequency, etc...), sorted by most frequent handle first
    @property
    def results(self):
        results = []
        handles = set([e["handle"] for e in self.extractions])
        for handle in handles:
            results.append(dict(handle=handle, **self.stats_for(handle)))
        return sorted(results, key=lambda x: x["frequency"], reverse=True)

    def stats_for(self, handle):
        handle_extractions = [e for e in self.extractions if e["handle"] == handle]
        pages_with_handle = set([e["page_id"] for e in handle_extractions])
        total_pages = self.page_count
        return dict(
            link_count=len(handle_extractions),
            page_count=len(pages_with_handle),
            # Frequency is False if total_pages is 0
            frequency=len(pages_with_handle) / total_pages if total_pages else False,
            similarity=self.similarity_with_domain(handle),
        )

    # Calculate the similarity score of the given handle with the domain that
    # this extractor is being used on. For example, handle 'test' will score
    # highly on 'test.com' but poorly on 'example.com'.
    def similarity_with_domain(self, handle):
        plain_handle = re.sub(r"\W", "", handle)
        plain_domain = re.sub(r"\W", "", self.domain)
        plain_domain_no_ending = re.sub(r"\W", "", self.domain.rsplit(".", 1)[0])
        return max(
            jaro_winkler_similarity(plain_handle, plain_domain),
            jaro_winkler_similarity(plain_handle, plain_domain_no_ending),
        )

    @property
    def top_candidate(self):
        results = sorted(self.results, key=lambda x: x["frequency"], reverse=True)

        # No viable candidate
        if len(results) == 0:
            return None

        top_handle = results[0]["handle"]

        # Is the handle used on at least 50% of pages?
        is_used_often = results[0]["frequency"] >= 0.5

        # Is the handle very similar to the domain name?
        # Example: unicef_org and unicef.org are very similar
        is_very_similar = results[0]["similarity"] >= 0.8

        # If we have only one result, and the top candidate is used on at least
        # 50% of pages or is very similar to the domain name (80% score), then
        # we have our top candidate.
        if len(results) == 1:
            return top_handle if is_used_often or is_very_similar else None

        # Is the handle used 5x as much as the second most frequent handle?
        has_frequency_ratio_5 = results[0]["frequency"] >= results[1]["frequency"] * 5

        # Is the handle the most similar to the domain name?
        is_most_similar = results[0]["similarity"] > max(
            [result["similarity"] for result in results[1:]]
        )

        # If we have a handle that is used frequently across the website and
        # used at least 5x as much as the second most frequent handle, we have
        # our top candidate
        if is_used_often and has_frequency_ratio_5:
            return top_handle

        # If we have a handle that is very similar to the domain name and there
        # is no other handle that is more similar, we have our top candidate
        if is_very_similar and is_most_similar:
            return top_handle

        return None