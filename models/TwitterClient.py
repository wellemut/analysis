import os
from TwitterAPI import TwitterAPI

# Create an authenticated Twitter client
class TwitterClient(TwitterAPI):
    def __init__(self, *args, api_version="2", **kwargs):
        super().__init__(
            os.environ["TWITTER_API_KEY"],
            os.environ["TWITTER_API_SECRET"],
            os.environ["TWITTER_ACCESS_TOKEN_KEY"],
            os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
            *args,
            api_version=api_version,
            **kwargs
        )
