import os
from operator import itemgetter
import googlemaps
from models.Cache import Cache
from helpers.get_registered_domain import get_registered_domain
from helpers.get_normalized_url import get_normalized_url

# Create an authenticated Google Maps client
class GoogleMapsAPI:
    def __init__(self):
        self.__client = googlemaps.Client(key=os.environ["GOOGLE_MAPS_API_KEY"])

    @property
    def name(self):
        return self.__class__.__name__

    def find_by_url(self, url):
        # Remove protocol
        normalized_url = get_normalized_url(url)
        normalized_target_domain = get_registered_domain(url)

        # Queries to run: url and domain, first in quotes and then without
        QUERIES = [
            # To be exhaustive, we'd need to run all variations of this query
            # with different location biases. But that would be costly.
            f'"{normalized_url}"',
            f'"{normalized_target_domain}"',
            # normalized_url,
            # normalized_target_domain,
        ]

        for query in QUERIES:
            # Identify candidates
            candidates = self.__find_place(
                query,
                "textquery",
                fields=["place_id"],
                language="en",
                # middle of Germany
                location_bias="point:51.1657,10.4515",
                # surrounds Germany
                # location_bias="rectangle:47.3,5.99|54.98,15.02",
            )["candidates"]

            # Analyze each candidate, looking for match between search domain and
            # candidate domain
            for candidate in candidates:
                match, cached_at = itemgetter("result", "cached_at")(
                    self.find_by_id(candidate["place_id"])
                )

                normalized_candidate_domain = get_registered_domain(
                    match.get("website", "")
                )

                if normalized_target_domain == normalized_candidate_domain:
                    return {**match, "cached_at": cached_at}

    def find_by_id(self, place_id):
        return self.__place(
            place_id,
            fields=[
                "place_id",
                "name",
                "website",
                "address_component",
                "formatted_address",
                # Returns address in adr microformat:
                # http://microformats.org/wiki/adr
                # "adr_address",
                "international_phone_number",
                "geometry",
            ],
            language="en",
        )

    def __find_place(self, *args, **kwargs):
        cache = Cache(self.name, "find_place", *args, **kwargs)

        if cache.is_empty:
            cache.update(self.__client.find_place(*args, **kwargs))

        return {**cache.result, "cached_at": cache.cached_at}

    def __place(self, *args, **kwargs):
        cache = Cache(self.name, "place", *args, **kwargs)

        if cache.is_empty:
            cache.update(self.__client.place(*args, **kwargs))

        return {**cache.result, "cached_at": cache.cached_at}
