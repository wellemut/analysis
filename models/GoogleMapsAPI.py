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

        # Identify candidates
        candidates = self.__find_place(
            normalized_url,
            "textquery",
            fields=["name", "formatted_address", "place_id"],
            language="en",
            # middle of Germany
            location_bias="point:51.1657,10.4515",
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

        # If we still have no candidate, let's attempt search with the registered
        # domain only
        if normalized_target_domain != normalized_url:
            return self.find_by_url(normalized_target_domain)

    def find_by_id(self, place_id):
        return self.__place(
            place_id,
            fields=[
                "place_id",
                "name",
                "website",
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
