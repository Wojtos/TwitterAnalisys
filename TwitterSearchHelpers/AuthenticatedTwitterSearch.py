from TwitterSearch import TwitterSearch
import os


class AuthenticatedTwitterSearch(TwitterSearch):
    def __init__(self, **attr):
        super().__init__(
            consumer_key=os.getenv("CONSUMER_KEY"),
            consumer_secret=os.getenv("CONSUMER_SECRET"),
            access_token=os.getenv("ACCESS_TOKEN"),
            access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
            **attr
        )
