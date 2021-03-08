import os
from TwitterAPI import TwitterAPI as TwitterClient
from models.Cache import Cache

# Create an authenticated Twitter client
class TwitterAPI:
    def __init__(self):
        self.__client = TwitterClient(
            os.environ["TWITTER_API_KEY"],
            os.environ["TWITTER_API_SECRET"],
            os.environ["TWITTER_ACCESS_TOKEN_KEY"],
            os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
            api_version="2",
        )

    @property
    def name(self):
        return self.__class__.__name__

    def get_profile(self, handle):
        return self.__request(
            f"users/by/username/:{handle}?user.fields=profile_image_url"
        )

    def __request(self, url):
        cache = Cache(self.name, "request", url)

        if cache.is_empty:
            cache.update(self.__client.request(url).json())

        return {**cache.result, "cached_at": cache.cached_at}
